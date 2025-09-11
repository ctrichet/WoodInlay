#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/svg_layer.py                                            !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import os
from PyQt5.QtWidgets import(
    QWidget, QVBoxLayout, QGraphicsScene, QTreeWidget,
)
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
from PyQt5.QtGui import QPainter
from utils.debug import debug_log
from ui.layer import LayerWidget
from ui.delegates import TreeItemHighlightDelegate

class SvgLayerWidget(LayerWidget):
    _instance = None

    @staticmethod
    def add_to_scene(item):
        if SvgLayerWidget._instance:
            scene = SvgLayerWidget._instance.scene
            scene.addItem(item)
            view = SvgLayerWidget._instance.view
            if view is not None:
                view.ensureVisible(scene.itemsBoundingRect(), 50, 50)
        else:
            print("Pas d’instance SvgLayerWidget initialisée")

    @staticmethod
    def get_instance(file_path):
        if not SvgLayerWidget._instance:
            SvgLayerWidget._instance = SvgLayerWidget(file_path)
        return SvgLayerWidget._instance

    def __init__(self, file_path):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.load_svg(file_path)
        tree = QTreeWidget()
        tree.setHeaderLabels(["Éléments SVG"])
        tree.setMinimumWidth(200)
        tree.setItemDelegate(TreeItemHighlightDelegate())
        tree.setStyleSheet("""
            QTreeWidget {
                background-color: #232323;
                color: white;
                border: none;
            }
            QTreeWidget::item {
                background-color: #232323;
                color: white;
            }
            QTreeWidget::item:selected {
                background-color: #353535;
                color: white;
            }
            QHeaderView::section {
                background-color: #353535;   /* fond de l'en-tête */
                color: white;                /* texte en blanc */
                border: none;
                padding: 4px;
            }
        """)
        self.tree = tree

    def load_svg(self, file_path):
        renderer = QSvgRenderer(file_path)
        item = QGraphicsSvgItem()
        item.setSharedRenderer(renderer)
        item.id = os.path.basename(file_path)
        self.add_to_scene(item)
