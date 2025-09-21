#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   core/nesting_manager.py                                    !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/21 14:32:45 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/21 14:32:45 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#

import random
import numpy as np
from shapely.geometry import Polygon, Point
from shapely import affinity
from shapely.ops import unary_union

from PyQt5.QtCore import (
    QPointF,
    QThread,
    QSemaphore,
    pyqtSignal,
    QObject,
)

from PyQt5.QtGui import (
    QImage,
    qAlpha,
)

from core.model_items import DuplicataGroupItem

from utils.debug import debug_log
from PyQt5.QtCore import QPointF

from shapely.geometry import Polygon


class NestingWorker(QThread):
    placement_signal = pyqtSignal(int, float, float, float)  # idx, rot, dx, dy

    def __init__(self, config, layer):
        super().__init__()
        self.layer = layer
        self.nm = NestingManager(None, self.layer)

    def run(self):
        self.nm.nest()


class NestingManager(QObject):
    placement_signal = pyqtSignal(int, float, float, float)
    max_repulsion_iters = 50
    max_attempts_per_ind = 30

    def transformed_polygons_indiv(self, rotations, positions):
        """
        Transforme tous les polygones selon les rotations et positions de l'individu.
        Retourne une liste de polygones shapely.
        """
        result = []
        for poly, rot, (dx, dy) in zip(self.polygons_nested, rotations, positions):
            p = affinity.rotate(poly, rot, origin="centroid", use_radians=False)
            p = affinity.translate(p, xoff=dx, yoff=dy)
            result.append(p)
        return result

    def _random_individual(self):
        """
        Crée un individu aléatoire :
        - rotation choisie dans self.allowed_rotations
        - position initiale (dx, dy) aléatoire dans le bin
        Retourne : (rotations, positions)
        """
        n = len(self.polygons_nested)
        rotations = [random.choice(self.allowed_rotations) for _ in range(n)]
        positions = []

        minx, miny, maxx, maxy = self.bin_polygon_with_margins.bounds

        for poly in self.polygons_nested:
            # taille du polygone pour éviter qu'il sorte du bin
            p_minx, p_miny, p_maxx, p_maxy = poly.bounds
            width = p_maxx - p_minx
            height = p_maxy - p_miny

            # choisir dx, dy aléatoire pour placer le polygone dans le bin
            dx = random.uniform(minx - p_minx, maxx - p_maxx)
            dy = random.uniform(miny - p_miny, maxy - p_maxy)
            positions.append((dx, dy))

        return rotations, positions

    def genetic_nesting(self):
        # génération initiale
        population = [self._random_individual() for _ in range(self.population_size)]
        population = [ind for ind in population if self.is_valid_individual(*ind)]
        if not population:
            debug_log("Aucun individu valide généré")
            return

        self.best_score = None

        generation = 0
        while self.run:
            debug_log(f"generation : {generation}")
            generation += 1
            scored_pop = []
            for rotations, positions in population:
                polygons_transformed = self.transformed_polygons_indiv(
                    rotations, positions
                )
                score = self.fitness(polygons_transformed)
                scored_pop.append((score, (rotations, positions)))

            # tri décroissant
            scored_pop.sort(key=lambda x: x[0])  # plus petit score = meilleur
            best_score_gen, best_indiv = scored_pop[0]

            # émettre signal si meilleur score
            if self.best_score is None or best_score_gen < self.best_score:
                self.best_score = best_score_gen
                debug_log(f"Best score = {self.best_score}")
                rotations, positions = best_indiv
                for i, (rot, (dx, dy)) in enumerate(zip(rotations, positions)):
                    self.emit_placement(i, rot, dx, dy)

            elites = [ind for _, ind in scored_pop[: self.elite_size]]

            # nouvelle population
            new_population = elites.copy()
            while len(new_population) < self.population_size:
                p1, p2 = random.sample(elites, 2)
                child = self._crossover(p1, p2)
                child = self._mutate(*child)
                if self.is_valid_individual(*child):
                    new_population.append(child)
            population = new_population

    def __init__(self, config, layer):
        super().__init__()
        self.bin_margin: float = 2
        self.spacing: float = 2
        self.mutation_rotation: int = 10
        self.mutation_translation: float = 5
        self.population_size = 30
        self.elite_size: int = 5
        self.lp_refine_top: int = 3
        self.lp_delta: float = 5.0
        self.fitness_method = (
            "areaTopLeft"  # gravity/area/area_top/quadratic/quadratic_top
        )
        self.quadratic_fitness_coeff: float = 0.5
        self.allowed_rotations = [rot for rot in range(0, 360, self.mutation_rotation)]

        self.layer = layer
        self.bin_polygon_with_margins = self.get_layer_bin_polygon()
        self.run = True
        self.polygons_fixed_with_spacing = []
        self.polygons_nested_with_spacing = []
        self.polygons_nested = []
        self.polygons_nested_semaphores = {}
        self.polygon_idx_to_item = {}
        self.initial_rotations = []
        self.placements = {}
        self.best_score = None

    def stop(self):
        self.run = False

    def emit_placement(self, idx, rot, dx, dy):
        self.placement_signal.emit(idx, rot, dx, dy)

    def _crossover(self, parent1, parent2):
        """
        Croisement simple d'individus :
        - parent1 et parent2 : tuples (rotations, positions)
        Retourne un enfant : (rotations, positions)
        """
        rotations1, positions1 = parent1
        rotations2, positions2 = parent2

        n = len(rotations1)
        # point de croisement aléatoire
        cp = random.randint(1, n - 1)

        # combiner rotations et positions
        child_rotations = rotations1[:cp] + rotations2[cp:]
        child_positions = positions1[:cp] + positions2[cp:]

        return (child_rotations, child_positions)

    def _mutate(self, rotations, positions):
        """
        Mutation aléatoire :
        - rotation changée aléatoirement avec probabilité
        - translation modifiée légèrement
        """
        new_rotations = []
        new_positions = []

        for rot, (dx, dy), poly in zip(rotations, positions, self.polygons_nested):
            # mutation rotation
            if random.random() < 0.2:  # 20% chance de muter
                rot = random.choice(self.allowed_rotations)

            # mutation translation
            if random.random() < 0.5:  # 50% chance de muter
                # ajustement aléatoire limité
                dx += random.uniform(
                    -self.mutation_translation, self.mutation_translation
                )
                dy += random.uniform(
                    -self.mutation_translation, self.mutation_translation
                )

                # garder polygone à l'intérieur du bin
                minx, miny, maxx, maxy = self.bin_polygon_with_margins.bounds
                p_minx, p_miny, p_maxx, p_maxy = poly.bounds
                dx = max(minx - p_minx, min(dx, maxx - p_maxx))
                dy = max(miny - p_miny, min(dy, maxy - p_maxy))

            new_rotations.append(rot)
            new_positions.append((dx, dy))

        return (new_rotations, new_positions)

    def collect(self):
        scene = self.layer.scene
        if len(scene.selectedItems()) == 0:
            debug_log("Aucun polygone pour GA")
            return
        for item in scene.items():
            if not isinstance(item, DuplicataGroupItem):
                debug_log(f"type item : {type(item)}")
                continue

            poly_shapely = item.to_shapely_polygon()
            if item in scene.selectedItems():
                idx = len(self.polygons_nested)
                self.initial_rotations.append(item.rotation())
                self.polygons_nested.append(poly_shapely)
                self.polygon_idx_to_item[idx] = item
                poly_shapely_with_margin = poly_shapely.buffer(self.spacing / 2)
                self.polygons_nested_with_spacing.append(poly_shapely_with_margin)
            elif poly_shapely.within(self.bin_polygon_with_margins):
                self.polygons_fixed_with_spacing.append(
                    poly_shapely.buffer(self.spacing / 2)
                )

        if not self.check_bin_capacity:
            debug_log("Aire de la bin insuffisante")
            return

        self._separate_by_repulsion()

    def is_valid_individual(self, rotations, positions):
        """
        Vérifie si l'individu est valide :
        - polygone dans le bin
        - pas de chevauchement entre eux ou avec fixes
        """
        n = len(self.polygons_nested)
        placed_polys = []
        for idx in range(n):
            poly = affinity.rotate(
                self.polygons_nested_with_spacing[idx],
                rotations[idx],
                origin="centroid",
                use_radians=False,
            )
            dx, dy = positions[idx]
            poly = affinity.translate(poly, xoff=dx, yoff=dy)

            # Collision avec bin
            if not poly.within(self.bin_polygon_with_margins):
                return False

            # Collision avec fixes
            for fixed in self.polygons_fixed_with_spacing:
                if poly.intersects(fixed):
                    return False

            # Collision avec polygones déjà placés
            for p in placed_polys:
                if poly.intersects(p):
                    return False

            placed_polys.append(poly)
        return True

    def nest(self):
        self.collect()
        self.genetic_nesting()
        return

    def _separate_by_repulsion(self) -> bool:
        """
        Applique une séparation par répulsion vectorielle pour corriger les chevauchements.
        Met à jour self.polygons_nested et self.polygons_nested_with_spacing.
        Retourne True si la séparation a convergé, False sinon.
        """
        debug_log("_separate_by_repulsion start")
        n = len(self.polygons_nested_with_spacing)
        if n == 0:
            return True

        placed_polys = self.polygons_nested_with_spacing.copy()
        final_transforms = [(0, 0.0, 0.0) for _ in range(n)]  # (rot, dx, dy)

        max_disp_per_iter = self.spacing * 2  # limite pour éviter saut trop grand

        for it in range(NestingManager.max_repulsion_iters):
            debug_log(f"iteration : {it}")
            overlap_found = False
            displacements = [np.array([0.0, 0.0]) for _ in range(n)]

            for i in range(n):
                poly_i = placed_polys[i]

                # Collision avec polygones fixes
                for fixed in self.polygons_fixed_with_spacing:
                    if poly_i.intersects(fixed):
                        overlap_found = True
                        inter = poly_i.intersection(fixed)
                        if not inter.is_empty:
                            # vecteur du centre vers poly_i
                            c_i = np.array(poly_i.centroid.coords[0])
                            c_fixed = np.array(fixed.centroid.coords[0])
                            v = c_i - c_fixed
                            dist = np.linalg.norm(v)
                            if dist < 1e-3:
                                v = np.random.rand(2) - 0.5
                                dist = np.linalg.norm(v)
                            v_unit = v / dist
                            scale = np.sqrt(inter.area)
                            dx, dy = v_unit * scale
                            # limiter le déplacement
                            dx, dy = np.clip(
                                [dx, dy], -max_disp_per_iter, max_disp_per_iter
                            )
                            displacements[i] += np.array([dx, dy])

                # Collision avec autres polygones
                for j in range(i + 1, n):
                    poly_j = placed_polys[j]
                    if poly_i.intersects(poly_j):
                        overlap_found = True
                        inter = poly_i.intersection(poly_j)
                        if not inter.is_empty:
                            c_i = np.array(poly_i.centroid.coords[0])
                            c_j = np.array(poly_j.centroid.coords[0])
                            v = c_i - c_j
                            dist = np.linalg.norm(v)
                            if dist < 1e-3:
                                v = np.random.rand(2) - 0.5
                                dist = np.linalg.norm(v)
                            v_unit = v / dist
                            scale = np.sqrt(inter.area) / 2
                            dx_i, dy_i = v_unit * scale
                            dx_j, dy_j = -v_unit * scale
                            # limiter
                            dx_i, dy_i = np.clip(
                                [dx_i, dy_i], -max_disp_per_iter, max_disp_per_iter
                            )
                            dx_j, dy_j = np.clip(
                                [dx_j, dy_j], -max_disp_per_iter, max_disp_per_iter
                            )
                            displacements[i] += np.array([dx_i, dy_i])
                            displacements[j] += np.array([dx_j, dy_j])

                # Collision avec les bords du bin
                if not poly_i.within(self.bin_polygon_with_margins):
                    overlap_found = True
                    minx, miny, maxx, maxy = poly_i.bounds
                    bminx, bminy, bmaxx, bmaxy = self.bin_polygon_with_margins.bounds
                    dx = dy = 0.0
                    if minx < bminx:
                        dx = bminx - minx
                    elif maxx > bmaxx:
                        dx = bmaxx - maxx
                    if miny < bminy:
                        dy = bminy - miny
                    elif maxy > bmaxy:
                        dy = bmaxy - maxy
                    # limiter
                    dx, dy = np.clip([dx, dy], -max_disp_per_iter, max_disp_per_iter)
                    displacements[i] += np.array([dx, dy])

            # Appliquer les déplacements
            for i in range(n):
                dx, dy = displacements[i]
                if dx != 0.0 or dy != 0.0:
                    placed_polys[i] = affinity.translate(
                        placed_polys[i], xoff=dx, yoff=dy
                    )
                    rot, old_dx, old_dy = final_transforms[i]
                    final_transforms[i] = (rot, old_dx + dx, old_dy + dy)

            if not overlap_found:
                debug_log("Separation converged, updating polygons")
                for i in range(n):
                    rot, dx, dy = final_transforms[i]
                    item = self.polygon_idx_to_item[i]
                    self.polygons_nested_semaphores[i] = QSemaphore(0)
                    self.emit_placement(i, rot, dx, dy)
                    self.polygons_nested_semaphores[i].acquire()
                    poly = item.to_shapely_polygon()
                    self.polygons_nested[i] = poly
                    self.polygons_nested_with_spacing[i] = poly.buffer(self.spacing / 2)
                    self.initial_rotations[i] = item.rotation()
                self.polygons_nested_semaphores = None
                debug_log("End")
                return True

        debug_log("Initial separation failed after max iterations.")
        return False

    def _repulsion_vector(self, poly, fixed):
        """
        Calcule un vecteur minimal pour éloigner `poly` de `fixed`.
        Retourne dx, dy.
        """
        # centroides
        c_poly = np.array(poly.centroid.coords[0])
        c_fixed = np.array(fixed.centroid.coords[0])
        # vecteur direction de répulsion
        v = c_poly - c_fixed
        dist = np.linalg.norm(v)
        if dist < 1e-3:
            # éviter division par zéro : déplacement aléatoire
            v = np.random.rand(2) - 0.5
            dist = np.linalg.norm(v)
        v_unit = v / dist
        # amplitude : overlap minimal = buffer + 1.0
        dx, dy = v_unit * self.spacing
        return dx, dy

    def _mutual_repulsion_vectors(self, poly_i, poly_j):
        """
        Calcule vecteurs de répulsion pour deux polygones qui se chevauchent.
        Retourne dx_i, dy_i, dx_j, dy_j
        """
        c_i = np.array(poly_i.centroid.coords[0])
        c_j = np.array(poly_j.centroid.coords[0])
        v = c_i - c_j
        dist = np.linalg.norm(v)
        if dist < 1e-3:
            # déplacement aléatoire si centroids très proches
            v = np.random.rand(2) - 0.5
            dist = np.linalg.norm(v)
        v_unit = v / dist
        # on sépare équitablement les deux polygones
        dx_i, dy_i = v_unit * self.spacing * 0.5
        dx_j, dy_j = -v_unit * self.spacing * 0.5
        return dx_i, dy_i, dx_j, dy_j

    def _repulsion_vector_to_bin(self, poly, bin_poly):
        """
        Déplace le polygone à l'intérieur du bin s'il sort.
        Retourne dx, dy
        """
        minx, miny, maxx, maxy = poly.bounds
        bminx, bminy, bmaxx, bmaxy = bin_poly.bounds
        dx = dy = 0.0
        if minx < bminx:
            dx = bminx - minx + self.spacing
        elif maxx > bmaxx:
            dx = bmaxx - maxx - self.spacing
        if miny < bminy:
            dy = bminy - miny + self.spacing
        elif maxy > bmaxy:
            dy = bmaxy - maxy - self.spacing
        return dx, dy

    def fitness(self, polygons):

        if self.fitness_method == "gravity":
            max_right_bound = 0
            for poly in polygons:
                right_bound = poly.bounds[2]
                if right_bound > max_right_bound:
                    max_right_bound = right_bound
            return max_right_bound

        elif self.fitness_method == "area":
            max_right_bound = 0
            min_left_bound = polygons[0].bounds[0]
            max_bottom_bound = 0
            min_top_bound = polygons[0].bounds[1]
            for poly in polygons + self.polygons_fixed_with_spacing:
                left_bound, top_bound, right_bound, bottom_bound = poly.bounds
                if left_bound < min_left_bound:
                    min_left_bound = left_bound
                if right_bound > max_right_bound:
                    max_right_bound = right_bound
                if top_bound < min_top_bound:
                    min_top_bound = top_bound
                if bottom_bound > max_bottom_bound:
                    max_bottom_bound = bottom_bound
            return (right_bound - left_bound) * (bottom_bound - top_bound)

        elif self.fitness_method == "areaTopLeft":
            max_right_bound = 0
            max_bottom_bound = 0
            for poly in polygons + self.polygons_fixed_with_spacing:
                right_bound = poly.bounds[2]
                bottom_bound = poly.bounds[3]
                if right_bound > max_right_bound:
                    max_right_bound = right_bound
                if bottom_bound > max_bottom_bound:
                    max_bottom_bound = bottom_bound
            return max_right_bound * max_bottom_bound

        elif self.fitness_method == "quadratic":
            max_right_bound = 0
            min_left_bound = polygons[0].bounds[0]
            max_bottom_bound = 0
            min_top_bound = polygons[0].bounds[1]

            for poly in polygons + self.polygons_fixed_with_spacing:
                left_bound, top_bound, right_bound, bottom_bound = poly.bounds
                if left_bound < min_left_bound:
                    min_left_bound = left_bound
                if right_bound > max_right_bound:
                    max_right_bound = right_bound
                if top_bound < min_top_bound:
                    min_top_bound = top_bound
                if bottom_bound > max_bottom_bound:
                    max_bottom_bound = bottom_bound

            width = max_right_bound - min_left_bound
            height = max_bottom_bound - min_top_bound

            # Malus quadratique pour l'écart par rapport au carré
            ratio = max(width / height, height / width)
            malus = 1 + self.quadratic_fitness_coeff * (ratio - 1) ** 2
            return width * height * malus

        elif self.fitness_method == "quadraticTopLeft":
            max_right_bound = 0
            max_bottom_bound = 0
            for poly in polygons + self.polygons_fixed_with_spacing:
                right_bound = poly.bounds[2]
                bottom_bound = poly.bounds[3]
                if right_bound > max_right_bound:
                    max_right_bound = right_bound
                if bottom_bound > max_bottom_bound:
                    max_bottom_bound = bottom_bound
            ratio = max(
                max_right_bound / max_bottom_bound, max_bottom_bound / max_right_bound
            )
            malus = 1 + self.quadratic_fitness_coeff * (ratio - 1) ** 2
            return max_right_bound * max_bottom_bound * malus

        else:
            print(f"[ERREUR] Fitness methode inconnue : {self.fitness_method}")
            return

    def check_bin_capacity(self):
        total_area = sum(poly.area for poly in self.polygons_nested_with_spacing)
        total_area += sum(poly.area for poly in self.polygons_fixed_with_spacing)
        return total_area < self.bin_polygon_with_margins.area

    def get_layer_bin_polygon(self):
        pixmap = getattr(self.layer, "background_pixmap", None)
        if pixmap is None:
            debug_log("[get_layer_polygon] Aucun pixmap de fond trouvé")
            return Polygon()

        # Convertir le QPixmap en QImage pour accéder aux pixels
        img = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)

        polygons = []
        visited = set()

        width = img.width()
        height = img.height()

        # Parcourir tous les pixels pour trouver les zones opaques
        for y in range(height):
            for x in range(width):
                if (x, y) in visited:
                    continue
                alpha = qAlpha(img.pixel(x, y))
                if alpha > 0:  # pixel non transparent
                    # créer un petit rectangle 1x1 pour chaque pixel opaque
                    poly = Polygon(
                        [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1), (x, y)]
                    )
                    polygons.append(poly)
                    visited.add((x, y))

        if not polygons:
            return Polygon()

        return unary_union(polygons).buffer(-self.bin_margin + self.spacing / 2)

    def apply_placement(self, idx, rotation, dx, dy):
        debug_log(f"rot = {rotation}, dx  = {dx}, dy = {dy}")
        item = self.polygon_idx_to_item[idx]
        item.setRotation(self.initial_rotations[idx] + rotation)
        poly = self.polygons_nested[idx]
        if self.polygons_nested_semaphores:
            self.polygons_nested_semaphores[idx].release()
        poly_transformed = affinity.rotate(
            poly, rotation, origin="centroid", use_radians=False
        )
        poly_transformed = affinity.translate(poly_transformed, xoff=dx, yoff=dy)

        element = item.closed_item.path().elementAt(0)
        local_source_point = QPointF(element.x, element.y)
        source_scene_pos = item.mapToScene(local_source_point)
        target_scene_pos = QPointF(*poly_transformed.exterior.coords[0])
        if item.parentItem():
            parent = item.parentItem()
            source_parent = parent.mapFromScene(source_scene_pos)
            target_parent = parent.mapFromScene(target_scene_pos)
            delta = target_parent - source_parent
        else:
            delta = target_scene_pos - source_scene_pos

        item.setPos(item.pos() + delta)
        item.mask()
