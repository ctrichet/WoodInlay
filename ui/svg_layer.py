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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
from PyQt5.QtGui import QPainter
from utils.debug import debug_log
from .views import ZoomableView
from woodinlay import WoodInlayManager

class SvgLayerWidget(QWidget):
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
        self.items_map = {}
        self.scene = QGraphicsScene()
        self.view = ZoomableView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.load_svg(file_path)

    def load_svg(self, file_path):
        renderer = QSvgRenderer(file_path)
        item = QGraphicsSvgItem()
        item.setSharedRenderer(renderer)
        item.id = os.path.basename(file_path)
        self.add_to_scene(item)
