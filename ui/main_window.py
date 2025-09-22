#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/main_window.py                                          !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 17:17:05 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
import os, fitz, sys
from math import radians, cos, sin

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QKeySequence, QPixmap, QImage, QBrush, QColor
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QDialog,
    QFileDialog,
    QMessageBox,
    QWidget,
    QGraphicsView,
    QHBoxLayout,
    QShortcut,
    QTabBar,
    QDockWidget,
)

from core.duplication_manager import perform_unique_duplication
from core.nesting_manager import NestingWorker
from ui.svg_layer import SvgLayerWidget
from ui.toolbar import CollapsibleToolbar
from ui.layer import LayerWidget
from ui.image_layer import ImageLayerWidget
from ui.svg_preview import PreviewDock
from ui.dialogs import NestingConfigDialog, BackgroundSelectionDialog
from ui.tab_bar import CustomTabBar
from styles.colors import Colors

from utils.debug import debug_log


class MainWindow(QMainWindow):
    _instance = None

    def __init__(self):
        super().__init__()
        MainWindow._instance = self
        self.setWindowTitle("Wood Inlay Tool - Qt SVG")
        self.resize(1200, 800)

        # ===================== Choix du fichier SVG =====================
        file_path = self.choose_svg_file()

        # ===================== Attributs =====================
        self.image_layers = {}
        self.image_layer_widgets = {}

        # SVG Layer (doit exister avant l'initialisation des docks et onglets)
        self.svg_layer = SvgLayerWidget(file_path)
        self.layer = self.svg_layer
        self.tree = self.layer.tree

        # ===================== Layout principal =====================
        self.layout = QHBoxLayout()
        # ===================== UI Components =====================
        self.init_tabs()
        self.init_toolbar()
        self.init_preview_dock()
        self.init_tree_dock()

        # ===================== Raccourcis =====================
        self.init_connections()

        # Central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # 🟢 Définir l’onglet actif une fois tout prêt
        self.on_tab_changed(0)

    # ----------------- Fichier SVG -----------------
    def choose_svg_file(self):
        """Ouvre une boîte de dialogue pour choisir un fichier SVG au démarrage avec thème sombre."""
        dialog = QFileDialog(None, "Select SVG model", "", "SVG Files (*.svg)")
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_() == QDialog.Accepted:
            return dialog.selectedFiles()[0]
        else:
            QMessageBox.warning(
                self,
                "Aucun fichier",
                "Aucun fichier SVG sélectionné. L'application va se fermer.",
            )
            sys.exit(0)

    # ----------------- Onglets -----------------
    def init_tabs(self):
        self.tabs = QTabWidget()
        self.colored_tabbar = CustomTabBar()
        self.tabs.setTabBar(self.colored_tabbar)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Encapsule le SVG layer dans le même wrapper que les images
        svg_outer = self.layer.build_tab_container()
        self.tabs.addTab(svg_outer, "SVG")
        self.colored_tabbar.set_tab_color(0, Colors.svg_frame)
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.layout.addWidget(self.tabs, 4)
        # si tu as un onglet "+" ou autre, ajoute-le après

    # ----------------- Toolbar -----------------
    def init_toolbar(self):
        self.toolbar = CollapsibleToolbar(
            zoom_in_func=self.zoom_in_current_view,
            zoom_out_func=self.zoom_out_current_view,
        )
        self.toolbar.duplicate_btn.clicked.connect(
            self.duplicate_via_toolbar_or_shortcut
        )
        self.layout.insertWidget(0, self.toolbar, 0)

    # ----------------- Dock Preview -----------------
    def init_preview_dock(self):
        svg_preview = QGraphicsView()
        svg_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        svg_preview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        svg_preview.setInteractive(False)
        svg_preview.setDragMode(QGraphicsView.NoDrag)
        svg_preview.setFocusPolicy(Qt.NoFocus)
        svg_preview.setScene(self.layer.scene)

        self.preview_dock = PreviewDock(
            "SVG Preview", self, layer_getter=lambda: self.layer
        )
        self.preview_dock.setAllowedAreas(
            Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea
        )
        self.preview_dock.setWidget(svg_preview)
        self.addDockWidget(Qt.RightDockWidgetArea, self.preview_dock)
        self.preview_dock.update_fit()
        self.preview_dock.hide()

    # ----------------- Dock Tree -----------------
    def init_tree_dock(self):
        self.tree_dock = QDockWidget(None, self)
        self.tree_dock.setTitleBarWidget(QWidget())  # supprime la titlebar
        self.tree_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.tree_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)  # pas détachable
        self.tree_dock.setWidget(self.tree)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tree_dock)
        self.tree_dock.setFixedWidth(250)

    # ----------------- Raccourcis -----------------
    def init_connections(self):
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(
            self.duplicate_via_toolbar_or_shortcut
        )
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(
            self.export_active_layer_to_svg
        )
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(
            self.open_nesting_dialog
        )
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self.stop_nesting)

    # ----------------- Utilitaires -----------------
    def get_active_layer(self):
        return self.layer

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

    def load_svg_layer(self, file_path):
        layer_widget = SvgLayerWidget(file_path)

        outer_frame = layer_widget.build_tab_container()

        tab_name = os.path.basename(file_path)
        index = self.tabs.count() - 1
        self.tabs.insertTab(index, outer_frame, tab_name)

        self.svg_layer_widgets[file_path] = layer_widget

    def load_image_layer(self, image_path):
        debug_log(f"[LOAD] ➜ Traitement de : {image_path}")
        supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")

        if not image_path.lower().endswith(supported_formats):
            QMessageBox.critical(
                self, "Erreur", f"❌ Format non supporté : {image_path}"
            )
            return

        if image_path.lower().endswith(".pdf"):
            pixmap = self.render_pdf_to_pixmap(image_path)
        else:
            pixmap = QPixmap(image_path)

        if pixmap is None or pixmap.isNull():
            debug_log(f"[ERROR] ❌ Impossible de charger le fichier : {image_path}")
            QMessageBox.critical(
                self, "Erreur", f"❌ Impossible de charger le fichier : {image_path}"
            )
            return

        # 🎯 Création du widget calque image
        layer_widget = ImageLayerWidget(image_path=image_path, pixmap=pixmap)

        # Encapsulation dans outer_frame via LayerWidget
        outer_frame = layer_widget.build_tab_container()

        tab_name = os.path.basename(image_path)

        # 📌 Insertion dans le QTabWidget juste avant le "+"
        index = self.tabs.count() - 1
        self.tabs.insertTab(index, outer_frame, tab_name)

        # 🔹 Configurer le bouton de fermeture et la couleur via la TabBar
        self.tabs.tabBar().add_image_tab(index, layer_widget.margin_color)

        # 🔹 Enregistrer la référence
        self.image_layer_widgets[image_path] = layer_widget

        debug_log(f"[OK] Onglet ajouté : {tab_name} à l'indice {index}")

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

    def on_tab_changed(self, index):
        debug_log(f"tab  index : {index}")
        # Récupère le widget d'onglet (wrapper ou layer direct)
        widget = self.tabs.widget(index)
        layer = getattr(widget, "layer_widget", widget)

        # Masquer l'ancien arbre
        self.layer.tree.hide()

        # Mettre à jour le layer courant
        self.layer = layer
        self.layer.tree.show()
        self.tree_dock.setWidget(self.layer.tree)

        # Gestion du dock de preview
        if isinstance(self.layer, SvgLayerWidget):
            if not self.preview_dock.isFloating():
                self.preview_dock.hide()
        else:
            if not self.preview_dock.isFloating():
                self.preview_dock.show()
                self.preview_dock.update_fit()

    def get_layer_widget_from_tab(self, tab_widget):
        """Renvoie l'ImageLayerWidget contenu dans l'onglet, ou None si introuvable."""
        if isinstance(tab_widget, LayerWidget):
            return tab_widget
        # Cherche parmi les enfants
        for child in tab_widget.findChildren(LayerWidget):
            return child
        return None

    def duplicate_via_toolbar_or_shortcut(self):

        selected_items = self.svg_layer.tree.selectedItems()
        debug_log(
            f"Nombre d’éléments sélectionnés dans la scène : {len(selected_items)}"
        )

        if not selected_items:
            QMessageBox.information(self, "Info", "No selected shape to duplicate")
            debug_log("END")
            return
        elif len(self.image_layer_widgets) == 0:
            QMessageBox.warning(self, "Info", "No background layer loaded")
            return None

        elif isinstance(self.layer, SvgLayerWidget):
            if len(self.image_layer_widgets) == 1:
                target_layer_widget = next(iter(self.image_layer_widgets.values()))
            else:
                dialog = BackgroundSelectionDialog(self.image_layer_widgets, self)
                target_path = dialog.get_selected_layer_path()

                target_layer_widget = self.image_layer_widgets.get(target_path)

        elif isinstance(self.layer, ImageLayerWidget):
            target_layer_widget = self.layer
            debug_log(f"✅ Duplication directe sur le calque actif $ {self.layer}")

        else:
            debug_log("❌ Onglet actif non reconnu (ni SVG, ni calque image)")
            return

        # Exécution de la duplication
        perform_unique_duplication(selected_items, target_layer_widget, self.svg_layer)
        debug_log("END")

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
        layer = self.layer
        if isinstance(layer, SvgLayerWidget):
            return
        dialog = NestingConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            layer.worker = NestingWorker(self.layer)
            dialog.set_config(layer.worker.nm)
            layer.worker.nm.placement_signal.connect(layer.on_placement)
            layer.worker.start()
        return None

    def stop_nesting(self):
        if hasattr(self.layer, "worker"):
            self.layer.worker.nm.stop()
            QMessageBox.information(
                self, "Nesting", "Nesting interrompu par l'utilisateur."
            )
        else:
            debug_log("Aucun Nesting en cours sur le layer")

    def active_image_layer(self):
        """Retourne l’ImageLayerWidget actif si l’onglet courant est une image, None sinon."""
        current_tab = self.tabs.currentWidget()
        if current_tab is None:
            return None

        # Vérifie si current_tab est directement un ImageLayerWidget
        if isinstance(current_tab, ImageLayerWidget):
            return current_tab

        # Sinon, cherche parmi ses enfants
        for child in current_tab.findChildren(ImageLayerWidget):
            return child

        return None
