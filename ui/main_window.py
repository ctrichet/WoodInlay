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
    QGraphicsView, QWidget, QHBoxLayout, QVBoxLayout, QShortcut, QTabBar,
    QStyle, QToolButton, QDockWidget,
)
from PyQt5.QtGui import (
    QColor, QKeySequence, QPixmap, QImage, QPalette, QBrush,
)
from PyQt5.QtCore import (
    Qt, QPointF, QEvent, QTimer,
)
from core.model_items import DuplicataGroupItem
from core.duplication_manager import perform_unique_duplication
from core.nesting_manager import NestingManager, NestingWorker
from ui.svg_layer import SvgLayerWidget
from ui.toolbar import CollapsibleToolbar
from ui.layer import LayerWidget
from ui.image_layer import ImageLayerWidget
from ui.svg_preview import PreviewDock
from ui.dialogs import (
    NestingConfigDialog, BackgroundSelectionDialog, DarkFileDialog,
    DarkMessageBox,
)
from ui.tab_bar import CustomTabBar
from utils.debug import debug_log


from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsRectItem

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

        # SVG Layer (doit exister avant on_tab_changed)
        self.svg_layer = SvgLayerWidget(choose_svg_file())
        self.layer = self.svg_layer
        self.tree = self.layer.tree

        # Tabs
        self.init_tabs()

        self.init_connections()
        self.init_preview_dock()
        self.init_tree_dock()
        self.init_main_layout()

        # Central widget
        container = QWidget()
        container.setAutoFillBackground(True)
        container.setPalette(self.init_palette())
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Toolbar
        self.toolbar = CollapsibleToolbar(
            zoom_in_func=self.zoom_in_current_view,
            zoom_out_func=self.zoom_out_current_view
        )
        self.toolbar.duplicate_btn.clicked.connect(self.duplicate_via_toolbar_or_shortcut)
        self.layout.insertWidget(0, self.toolbar, 0)

        # 🟢 Appel maintenant que tout est prêt
        self.on_tab_changed(0)

    def init_tabs(self):
        self.tabs = QTabWidget()
        self.colored_tabbar = CustomTabBar()
        self.tabs.setTabBar(self.colored_tabbar)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.tabs.addTab(self.layer, "SVG")
        self.colored_tabbar.set_tab_color(0, QColor(45, 45, 45))
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)

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
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        return palette

    def get_active_layer(self):
        return self.layer

    def init_main_layout(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tabs, 4)
        self.layout = main_layout

    def init_preview_dock(self):
        svg_preview = QGraphicsView()
        svg_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        svg_preview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Désactive interaction utilisateur
        svg_preview.setInteractive(False)
        svg_preview.setDragMode(QGraphicsView.NoDrag)
        svg_preview.setFocusPolicy(Qt.NoFocus)
        svg_preview.setScene(self.layer.scene)
        svg_preview.setStyleSheet("""
            QGraphicsView {
                background-color: #232323;   /* fond du QGraphicsView */
                border: none;
            }
        """)
        svg_preview.viewport().setStyleSheet("background-color: #232323;")
        svg_preview.fitInView(svg_preview.scene().sceneRect(), Qt.KeepAspectRatio)

        self.preview_dock = PreviewDock("SVG Preview", self, layer_getter=lambda: self.layer)
        self.preview_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.preview_dock.setWidget(svg_preview)
        self.addDockWidget(Qt.RightDockWidgetArea, self.preview_dock)
        self.preview_dock.hide()

    def init_tree_dock(self):
        # Dans __init__ ou init_layout
        self.tree_dock = QDockWidget(None, self)
        self.tree_dock.setTitleBarWidget(QWidget())  # en remplaçant la titlebar par un widget vide
        self.tree_dock.setAllowedAreas(Qt.RightDockWidgetArea)  # seulement à droite
        self.tree_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)  # non détachable
        self.tree_dock.setWidget(self.tree)
        self.tree_dock.setStyleSheet("""
            QDockWidget {
                background-color: #232323;      /* gris foncé pour le dock */
                titlebar-close-icon: url(none); /* optionnel: masquer le bouton fermer */
                titlebar-normal-icon: url(none);
            }
            QDockWidget::title {
                background-color: #353535;      /* barre de titre un peu plus claire */
                text-align: center;
                color: white;
                padding: 2px;
            }
        """)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tree_dock)

        # Optionnel : fixer la largeur du tree
        self.tree_dock.setFixedWidth(250)


    def init_connections(self):

        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.duplicate_via_toolbar_or_shortcut)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_active_layer_to_svg)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.open_nesting_dialog)
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self.stop_nesting)

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
        color = layer_widget.margin_color
        debug_log(f"[OK] ✅ Couleur de bordure : {color.name()}")

        # ⚙️ Construction du widget de l'onglet
        outer_frame = QWidget()
        outer_frame.setStyleSheet(f"background-color: {color.name()}; border-radius: 0px;")

        inner_layout = QHBoxLayout(outer_frame)
        inner_layout.setContentsMargins(8, 8, 8, 8)

        inner_container = QWidget()
        inner_container.setStyleSheet("background-color: none;")
        content_layout = QHBoxLayout(inner_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(layer_widget)
        inner_layout.addWidget(inner_container)

        # ⚠️ Fond gris foncé dans la vue
        layer_widget.view.setBackgroundBrush(QBrush(QColor(53, 53, 53)))

        tab_name = os.path.basename(image_path)

        # 📌 Insertion dans le QTabWidget juste avant le "+"
        index = self.tabs.count() - 1
        self.tabs.insertTab(index, outer_frame, tab_name)

        # 🔹 Configurer le bouton de fermeture et la couleur via la TabBar
        self.tabs.tabBar().add_image_tab(index, color)

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
        self.layer.tree.hide()
        layer = self.get_layer_widget_from_tab(self.tabs.widget(index))
        self.layer = layer
        layer.tree.show()
        self.tree_dock.setWidget(layer.tree)
        if isinstance(layer, SvgLayerWidget):
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
        debug_log(f"Nombre d’éléments sélectionnés dans la scène : {len(selected_items)}")

        if not selected_items:
            DarkMessageBox.information(self, "Info", "Aucun élément sélectionné à dupliquer.")
            debug_log("END")
            return

        # Cas 1 : l'utilisateur est sur le calque SVG
        if isinstance(self.layer, SvgLayerWidget):
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

            debug_log(f"✅ Duplication vers calque sélectionné $ {target_path}")

        # Cas 2 : l'utilisateur est sur un calque image
        elif isinstance(self.layer, ImageLayerWidget):
            target_layer_widget = self.layer
            debug_log(f"✅ Duplication directe sur le calque actif $ {self.layer}")

        else:
            debug_log("❌ Onglet actif non reconnu (ni SVG, ni calque image)")
            DarkMessageBox.warning(self, "Erreur", "L'onglet actif ne permet pas la duplication.")
            debug_log("END")
            return

        # Exécution de la duplication
        perform_unique_duplication(selected_items, target_layer_widget, self.svg_layer)
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

        if target_path in self.image_layer_widgets:
            return target_path

        DarkMessageBox.warning(self, "Erreur", "Calque image introuvable.")
        return None

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
        dialog = NestingConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            print("[DEBUG] Nesting config:", config)
            layer = self.active_image_layer()
            layer.worker = NestingWorker(config, layer)
            layer.worker.nm.placement_signal.connect(layer.on_placement)
            layer.worker.start()
        return None

    def stop_nesting(self):
        if hasattr(self.layer, 'worker'):
            self.layer.worker.nm.stop()
            DarkMessageBox.information(self, "Nesting", "Nesting interrompu par l'utilisateur.")
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
