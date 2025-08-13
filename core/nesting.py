#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   core/nesting.py                                            !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import random
from shapely.geometry import Polygon
from shapely.affinity import rotate, translate
from PyQt5.QtCore import (
    QTimer,
)
from .model_items import DuplicataGroupItem


def approximate_polygon(item: DuplicataGroupItem, simplify_tolerance=0.5) -> Polygon:
    path = item.closed_item.path()
    qt_polygon = path.toFillPolygon()
    if qt_polygon.isEmpty() or qt_polygon.size() < 3:
        print(f"[WARN] approximation vide pour {item.element_id}")
        return None
    points = [(pt.x(), pt.y()) for pt in qt_polygon]
    poly = Polygon(points)
    if not poly.is_valid or poly.area == 0:
        return None
    return poly


class Individual:
    def __init__(self, duplicatas, placements=None):
        self.duplicatas = duplicatas
        self.placements = placements or []
        self.polygons = []
        self.fitness = None

    def clone(self):
        clone = Individual(self.duplicatas)
        clone.placements = list(self.placements)
        clone.polygons = list(self.polygons)
        clone.fitness = self.fitness
        return clone

    def randomize(self, surface_rect, spacing_mm, allowed_rotations):
        self.placements = []
        self.polygons = []
        for dup in self.duplicatas:
            poly = approximate_polygon(dup)
            if not poly:
                self.placements.append(None)
                self.polygons.append(None)
                continue
            rot = random.choice(allowed_rotations)
            rotated = rotate(poly, rot, origin=(0, 0), use_radians=False)
            minx, miny, maxx, maxy = rotated.bounds
            width, height = maxx - minx, maxy - miny
            x = random.uniform(surface_rect.left(), surface_rect.right() - width)
            y = random.uniform(surface_rect.top(), surface_rect.bottom() - height)
            placed_poly = translate(rotated, xoff=x - minx, yoff=y - miny)
            self.placements.append((x - minx, y - miny, rot))
            self.polygons.append(placed_poly)


class NestingEngine:

    _instance  = None

    def __init__(self, scene, duplicatas, config, surface_rect, on_update):
        if self._instance:
            return self._intance
        self.scene = scene
        self.duplicatas = duplicatas
        self.config = config
        self.surface_rect = surface_rect
        self.on_update = on_update
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_generation)
        self.population = []
        self.best_individual = None
        self.generation = 0
        self._instance  =  self

    def start(self):
        self.timer.start(100)

    def stop(self):
        self.timer.stop()
