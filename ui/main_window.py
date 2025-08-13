#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/main_window.py                                          !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import os, fitz, sys
from typing import Optional
from math import radians, cos, sin

from PyQt5.QtWidgets import (
    QMainWindow, QTreeWidget, QTreeWidgetItem, QTabWidget, QDialog, QFileDialog,
    QGraphicsView, QWidget, QHBoxLayout, QVBoxLayout, QShortcut,
)
from PyQt5.QtGui import (
    QColor, QKeySequence, QPixmap, QImage, QPalette, QBrush
)
from PyQt5.QtCore import (
    Qt, QPointF,
)
from core.svg_parser import parse_svg_or_group
from core.duplication_manager import perform_unique_duplication
from ui.svg_layer import SvgLayerWidget
from ui.toolbar import CollapsibleToolbar
from ui.image_layer import ImageLayerWidget
from ui.dialogs import (
    NestingConfigDialog, BackgroundSelectionDialog, DarkFileDialog,
    DarkMessageBox,
)
from ui.delegates import TreeItemHighlightDelegate
from ui.tab_bar import CustomTabBar
from utils.debug import debug_log


class MainWindow(QMainWindow):
    _instance = None

    def __init__(self):
        def choose_svg_file():
            """Ouvre une boîte de dialogue pour choisir un fichier SVG au démarrage avec thème sombre."""

            dialog = DarkFileDialog(
                None,
                "Choisir un fichier SVG",
                "",
                "Fichiers SVG (*.svg)"
            )
            dialog.setFileMode(QFileDialog.ExistingFile)

            if dialog.exec_() == QDialog.Accepted:
                file_path = dialog.selectedFiles()[0]
                return file_path
            else:
                DarkMessageBox.warning(self, "Aucun fichier", "Aucun fichier SVG sélectionné. L'application va se fermer.")
                sys.exit(0)

        super().__init__()
        MainWindow._instance = self
        self.setWindowTitle("Wood Inlay Tool - Qt SVG")
        self.resize(1200, 800)

        # Dictionnaires
        self.image_layers = {}
        self.image_layer_widgets = {}
        self.tree_items_by_id = {}
        self.group_items_by_id = {}

        # Widgets
        self.init_tree_widget()
        self.init_svg_preview()

        # Tabs
        self.tabs = QTabWidget()
        self.colored_tabbar = CustomTabBar()
        self.tabs.setTabBar(self.colored_tabbar)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.init_layout()

        # Central widget
        container = QWidget()
        container.setAutoFillBackground(True)
        container.setPalette(self.init_palette())
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # SVG Layer (doit exister avant on_tab_changed)
        svg_file = choose_svg_file()
        self.load_svg_layer(svg_file)
        parse_svg_or_group(svg_file, self)
        self.svg_preview.setScene(self.svg_layer.scene)
        self.init_connections()

        # Toolbar
        self.toolbar = CollapsibleToolbar(
            zoom_in_func=self.zoom_in_current_view,
            zoom_out_func=self.zoom_out_current_view
        )
        self.toolbar.duplicate_btn.clicked.connect(self.duplicate_via_toolbar_or_shortcut)
        self.layout.insertWidget(0, self.toolbar, 0)

        # 🟢 Appel maintenant que tout est prêt
        self.on_tab_changed(0)

    def init_palette(self):
        """Renvoie une palette sombre pour l'UI."""
        palette = QPalette()
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(53, 53, 53))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(35, 35, 35))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        palette.setColor(QPalette.Window, QColor(35, 35, 35))
        return palette

    def init_layout(self):
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.svg_preview)
        right_layout.addWidget(self.tree)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tabs, 4)
        main_layout.addWidget(right_widget, 1)
        self.layout = main_layout

    def init_connections(self):
        self.tree.itemSelectionChanged.connect(self.sync_tree_to_scene)
        self.svg_layer.scene.selectionChanged.connect(self.sync_scene_to_tree)

        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.duplicate_via_toolbar_or_shortcut)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_active_layer_to_svg)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.open_nesting_dialog)

    def init_svg_preview(self):
        # Vue miniature non interactive pour l'aperçu
        svg_preview = QGraphicsView()
        svg_preview.setFixedHeight(150)  # hauteur de l'aperçu
        svg_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        svg_preview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Désactive interaction utilisateur
        svg_preview.setInteractive(False)
        svg_preview.setDragMode(QGraphicsView.NoDrag)
        svg_preview.setFocusPolicy(Qt.NoFocus)
        svg_preview.setStyleSheet("background: transparent; border: none;")
        svg_preview.hide()  # masquée par défaut
        self.svg_preview = svg_preview

    def init_tree_widget(self):
        tree = QTreeWidget()
        tree.setHeaderLabels(["Éléments SVG"])
        tree.setMinimumWidth(200)
        tree.setItemDelegate(TreeItemHighlightDelegate())
        self.tree = tree

    def active_scene(self):
        current_tab = self.tabs.currentWidget()
        if current_tab is None:
            return None

        image_layer_widget = self.image_layers.get(current_tab)
        if image_layer_widget:
            return image_layer_widget.scene
        return None

    def export_active_layer_to_svg(self):
        current_tab = self.tabs.currentWidget()
        scene = self.active_scene()

        if scene is None:
            debug_log("Export ignoré : aucun calque actif")
            return

        # Retrouve le widget correspondant à la scène active
        for widget, image_layer in self.image_layers.items():
            if image_layer.scene is scene:
                debug_log(f"Export SVG pour le calque : {image_layer.image_path}")
                image_layer.export_svg()
                return

        # Sinon, il s'agit probablement du svg_layer
        if current_tab is self.svg_layer:
            debug_log("Export ignoré : calque actif = SVG layer")
        else:
            debug_log("Export ignoré : calque actif inconnu")

    def load_image_layer(self, image_path):
        debug_log(f"[LOAD] ➜ Traitement de : {image_path}")
        supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")

        if not image_path.lower().endswith(supported_formats):
            DarkMessageBox.critical(self, "Erreur", f"❌ Format non supporté : {image_path}")
            return

        # 📄 Conversion ou chargement direct selon l'extension
        if image_path.lower().endswith(".pdf"):
            pixmap = self.render_pdf_to_pixmap(image_path)
        else:
            pixmap = QPixmap(image_path)

        if pixmap is None or pixmap.isNull():
            debug_log(f"[ERROR] ❌ Impossible de charger le fichier : {image_path}")
            DarkMessageBox.critical(self, "Erreur", f"❌ Impossible de charger le fichier : {image_path}")
            return

        # 🎯 Création du widget calque image
        layer_widget = ImageLayerWidget(image_path=image_path, pixmap=pixmap)

        # 🔶 Cadre extérieur coloré (bordure)
        color = layer_widget.margin_color.name()
        debug_log(f"[OK] ✅ Couleur de bordure : {color}")

        outer_frame = QWidget()
        outer_frame.setStyleSheet(f"background-color: {color}; border-radius: 0px;")

        inner_layout = QHBoxLayout(outer_frame)
        inner_layout.setContentsMargins(8, 8, 8, 8)

        inner_container = QWidget()
        inner_container.setStyleSheet("background-color: none;")

        content_layout = QHBoxLayout(inner_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(layer_widget)

        inner_layout.addWidget(inner_container)

        # ⚠️ Fond gris foncé
        layer_widget.view.setBackgroundBrush(QBrush(QColor(53, 53, 53)))

        tab_name = os.path.basename(image_path)

        # 📌 Insertion avant l’onglet "+"
        plus_index = self.tabs.count() - 1
        index = self.tabs.insertTab(plus_index, outer_frame, tab_name)

        self.image_layer_widgets[image_path] = layer_widget
        self.image_layers[outer_frame] = layer_widget

        self.tabs.tabBar().set_tab_color(index, layer_widget.margin_color)

        print(f"[INFO] 🟢 Onglet ajouté : {tab_name} (image_path {image_path})")

    def load_svg_layer(self, file_path):
        # Créer l'objet SvgLayerWidget
        self.svg_layer = SvgLayerWidget.get_instance(file_path)

        # Ajouter un onglet dans les tabs pour la couche SVG
        self.tabs.addTab(self.svg_layer, "SVG Layer")

        # Couleur grise personnalisée
        self.colored_tabbar.set_tab_color(0, QColor(45, 45, 45))


    def render_pdf_to_pixmap(self, pdf_path, page_number=0, dpi=300):
        try:
            doc = fitz.open(pdf_path)

            debug_log(f"Nombre de pages dans le PDF : {doc.page_count}")
            if doc.page_count == 0:
                print("[ERROR] PDF vide")
                return None

            page = doc.load_page(page_number)
            debug_log(f"Dimensions de la page : {page.rect}")

            # DPI plus élevé pour un rendu correct (par défaut c’est 72dpi = très petit)
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=True)
            debug_log(f"Rendu : {pix.width}x{pix.height}")

            # === ÉTAPE 3 : Conversion QImage → QPixmap ===
            mode = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, mode).copy()
            pixmap = QPixmap.fromImage(image)

            if pixmap.isNull():
                print("[ERROR] QPixmap vide après conversion")
                return None

            return pixmap

        except Exception as e:
            print(f"[ERROR] PDF rendering failed: {e}")
            return None


    def add_group_to_tree(self, group_id, parent_tree_item=None):
        parent = parent_tree_item or self.tree.invisibleRootItem()
        group_item = QTreeWidgetItem(parent)
        group_item.setText(0, group_id)
        group_item.setData(0, Qt.UserRole, group_id)

        self.tree_items_by_id[group_id] = group_item
        return group_item

    def add_svg_item(self, item, parent_tree_item=None):
        # Ajout à la scène via SvgLayerWidget
        self.svg_layer.items_map[item.element_id] = item
        self.svg_layer.add_to_scene(item)

        # Création du nœud dans l'arborescence
        tree_parent = parent_tree_item or self.tree.invisibleRootItem()
        tree_item = QTreeWidgetItem(tree_parent)
        tree_item.setText(0, item.element_id)
        tree_item.setData(0, Qt.UserRole, item.element_id)
        self.tree_items_by_id[item.element_id]  = tree_item
        self.group_items_by_id[item.element_id] = item

    def get_current_view(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, SvgLayerWidget):
            return current_widget.view
        elif isinstance(current_widget, QWidget):
            # Peut contenir ImageLayerWidget dans layout
            for child in current_widget.children():
                if isinstance(child, ImageLayerWidget):
                    return child.view
        return None

    def zoom_in_current_view(self):
        view = self.get_current_view()
        if view:
            view.zoom_in()

    def zoom_out_current_view(self):
        view = self.get_current_view()
        if view:
            view.zoom_out()

    def update_svg_preview(self):
        if not self.svg_layer or not self.svg_layer.scene:
            return

        scene_rect = self.svg_layer.scene.sceneRect()
        self.svg_preview.fitInView(scene_rect, Qt.KeepAspectRatio)

    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if widget == self.svg_layer:
            self.svg_preview.hide()
        else:
            self.update_svg_preview()
            self.svg_preview.show()

    def sync_scene_to_tree(self):
        """Synchronise la sélection dans la scène vers l’arbre."""
        self.tree.blockSignals(True)
        self.tree.clearSelection()

        for item in self.svg_layer.scene.selectedItems():
            tree_item = self.tree_items_by_id.get(item.element_id)
            if tree_item:
                tree_item.setSelected(True)

        self.tree.blockSignals(False)

    def sync_tree_to_scene(self):
        selected_tree_items = self.tree.selectedItems()
        scene = self.svg_layer.scene

        # ⏸️ Bloque temporairement les signaux
        scene.blockSignals(True)

        # Étape 1 – collecter les feuilles liées à chaque item sélectionné
        def collect_leaf_ids(tree_item):
            ids = []
            if tree_item.childCount() == 0:
                element_id = tree_item.data(0, Qt.UserRole)
                if element_id in self.group_items_by_id:
                    ids.append(element_id)
            else:
                for i in range(tree_item.childCount()):
                    ids.extend(collect_leaf_ids(tree_item.child(i)))
            return ids

        # Étape 2 – Détecter si les feuilles sont toutes sélectionnées
        for tree_item in selected_tree_items:
            leaf_ids = collect_leaf_ids(tree_item)
            all_selected = all(
                self.group_items_by_id.get(id_).isSelected()
                for id_ in leaf_ids if id_ in self.group_items_by_id
            )

            # Étape 3 – toggle sélection dans la scène
            for id_ in leaf_ids:
                group_item = self.group_items_by_id.get(id_)
                if not group_item:
                    continue
                group_item.setSelected(not all_selected)  # toggle selon état global

        scene.blockSignals(False)


    def duplicate_via_toolbar_or_shortcut(self):
        debug_log("START")

        current_widget = self.tabs.currentWidget()
        debug_log(f"Widget actif : {current_widget}")

        selected_items = self.svg_layer.scene.selectedItems()
        debug_log(f"Nombre d’éléments sélectionnés dans la scène : {len(selected_items)}")
        debug_log(f"Items sélectionnés : {[getattr(it, 'element_id', '??') for it in selected_items]}")

        if not selected_items:
            DarkMessageBox.information(self, "Info", "Aucun élément sélectionné à dupliquer.")
            debug_log("END")
            return

        # Cas 1 : l'utilisateur est sur le calque SVG
        if isinstance(current_widget, SvgLayerWidget):
            target_path = self.open_background_selection_dialog()
            if target_path is None:
                debug_log("Aucun calque cible sélectionné pour la duplication.")
                debug_log("END")
                return

            target_layer_widget = self.image_layer_widgets.get(target_path)
            if not target_layer_widget:
                DarkMessageBox.warning(self, "Erreur", "Le calque cible sélectionné est invalide.")
                debug_log("Erreur : Le calque cible sélectionné est invalide.")
                debug_log("END")
                return

            target_view = target_layer_widget.view
            debug_log(f"✅ Duplication vers calque sélectionné $ {target_path}")

        # Cas 2 : l'utilisateur est sur un calque image
        elif current_widget in self.image_layers:
            target_layer_widget = self.image_layers[current_widget]
            target_path = next((p for p,w in self.image_layer_widgets.items() if w == target_layer_widget), None)
            if not target_path:
                debug_log("❌ Calque actif non trouvé dans image_layer_widgets.")
                DarkMessageBox.warning(self, "Erreur", "Calque actif introuvable.")
                debug_log("END")
                return

            target_view = target_layer_widget.view
            debug_log(f"✅ Duplication directe sur le calque actif $ {target_path}")

        else:
            debug_log("❌ Onglet actif non reconnu (ni SVG, ni calque image)")
            DarkMessageBox.warning(self, "Erreur", "L'onglet actif ne permet pas la duplication.")
            debug_log("END")
            return

        # Exécution de la duplication
        perform_unique_duplication(selected_items, target_view, self)
        debug_log("END")

    def open_background_selection_dialog(self):
        selected = self.svg_layer.scene.selectedItems()
        if not selected:
            DarkMessageBox.information(self, "Info", "Sélectionnez un élément SVG à dupliquer.")
            return None

        if not self.image_layer_widgets:
            DarkMessageBox.warning(self, "Aucun calque", "Aucun calque image n'est chargé.")
            return None

        dialog = BackgroundSelectionDialog(self.image_layer_widgets, self)
        target_path = dialog.get_selected_layer_path()

        if not target_path:
            return None  # Annulé

        # Plus besoin de boucle ! ✅
        if target_path in self.image_layer_widgets:
            return target_path

        DarkMessageBox.warning(self, "Erreur", "Calque image introuvable.")
        return None

    def apply_tree_item_color(self, tree_item, bg_filename):
        # Trouve le calque image correspondant à ce nom de fichier
        image_path = next(
            (path for path in self.image_layer_widgets if os.path.basename(path) == bg_filename),
            None
        )

        if image_path is None:
            print(f"[WARNING] Aucun calque image trouvé pour {bg_filename}")
            return

        layer_widget = self.image_layer_widgets[image_path]
        color = layer_widget.margin_color

        for col in range(tree_item.columnCount()):
            tree_item.setBackground(col, color)

        # Si parent, essaye aussi de colorer le groupe
        parent = tree_item.parent()
        if parent:
            self.apply_group_item_color(parent)

    def apply_group_item_color(self, group_item) -> Optional[QColor]:
        """Colorie le groupe si tous ses enfants directs ont une couleur (identique ou non).
        Retourne la couleur appliquée ou None si aucune."""
        if group_item.childCount() == 0:
            return None  # Ce n'est pas un groupe

        child_colors = set()

        for i in range(group_item.childCount()):
            child = group_item.child(i)

            # Récupérer la couleur de l'enfant
            if child.childCount() > 0:
                # Enfant est un groupe → on suppose qu’il est déjà coloré
                brush = child.background(0)
                if brush.style() != Qt.NoBrush:
                    child_colors.add(brush.color().name())
                else:
                    return None  # Enfant groupe non encore coloré → on arrête ici
            else:
                # Enfant normal
                brush = child.background(0)
                if brush.style() != Qt.NoBrush:
                    child_colors.add(brush.color().name())
                else:
                    return None  # Un enfant non coloré → le groupe ne l’est pas

        # Si tous les enfants sont colorés
        if len(child_colors) == 1:
            final_color = QColor(list(child_colors)[0])
        else:
            final_color = QColor("#888888")  # Couleur pour duplication multiple

        for col in range(group_item.columnCount()):
            group_item.setBackground(col, final_color)

        return final_color

    def color_tree_selection(self):
        def apply_color_recursive(tree_item, color):
            for col in range(tree_item.columnCount()):
                tree_item.setBackground(col, color)
            for i in range(tree_item.childCount()):
                apply_color_recursive(tree_item.child(i), color)

        selected_items = self.tree.selectedItems()
        default_color = self.tree.palette().base().color()
        selection_color = QColor("#a8d5ff")  # Exemple couleur sélection personnalisée

        # D’abord, réinitialiser les couleurs de TOUS les items
        def mask_all_colors(item):
            for col in range(item.columnCount()):
                item.setBackground(col, default_color)
            for i in range(item.childCount()):
                mask_all_colors(item.child(i))

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            mask_all_colors(root.child(i))

        # Puis colorer récursivement les items sélectionnés et leurs enfants
        for item in selected_items:
            apply_color_recursive(item, selection_color)

    def rotate_group(self, items, angle_degrees):
        if not items:
            return

        # 1. Centre de rotation global
        bounding_rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        center = bounding_rect.center()

        # 2. Préparation rotation
        angle_radians = radians(angle_degrees)
        cos_a = cos(angle_radians)
        sin_a = sin(angle_radians)

        for item in items:
            # 3. Position courante dans la scène
            pos = item.scenePos()

            # 4. Calcul du vecteur relatif au centre global
            dx = pos.x() - center.x()
            dy = pos.y() - center.y()

            # 5. Appliquer rotation à ce vecteur
            new_dx = dx * cos_a - dy * sin_a
            new_dy = dx * sin_a + dy * cos_a

            # 6. Nouvelle position
            new_pos = QPointF(center.x() + new_dx, center.y() + new_dy)

            # 7. Déplacement + rotation locale (autour de son propre centre)
            item.setPos(new_pos)
            item.setRotation(item.rotation() + angle_degrees)

    def open_nesting_dialog(self):
        if self.tabs.currentWidget() == self.svg_layer:
            DarkMessageBox.information(self, "Info", "Le calepinage ne peut s’effectuer que sur un calque image.")

        dialog = NestingConfigDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return  # annulé

        config = dialog.get_values()
        selected = self.active_scene().selectedItems()

        if not selected:
            DarkMessageBox.information(self, "Info", "Aucun duplicata sélectionné pour le nesting.")
            return

        debug_log(f"[NESTING] Configuration : {config}")
        self.perform_nesting(config, selected)

