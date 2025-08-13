#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/image_layer.py                                          !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 15:43:01 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 15:43:01 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import os
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsScene, QFileDialog, QDialog
)
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import QRectF, Qt

from .views import ZoomableView
from core.model_items import DuplicataGroupItem
from ui.dialogs import DarkFileDialog, DarkMessageBox

from utils.debug import debug_log


class ImageLayerWidget(QWidget):
    _color_step = 0

    @staticmethod
    def next_margin_color():
        ImageLayerWidget._color_step += 1
        base_index = (ImageLayerWidget._color_step - 1) % 7 + 1
        r_on = bool(base_index & 0b100)
        g_on = bool(base_index & 0b010)
        b_on = bool(base_index & 0b001)
        cycle_pos = ((ImageLayerWidget._color_step - 1) // 7) % 8
        intensity = 0.5 - (cycle_pos * 0.05)
        intensity = max(intensity, 0.3)

        def channel_value(on):
            return int(255 * intensity) if on else 0

        return QColor(channel_value(r_on), channel_value(g_on), channel_value(b_on))

    def __init__(self, image_path=None, pixmap=None):
        super().__init__()
        self.margin_color = ImageLayerWidget.next_margin_color()
        self.image_path = image_path
        self.scene = QGraphicsScene()
        self.scene.name = image_path
        original_addItem = self.scene.addItem
        self.scene.addItem = lambda item: (
            debug_log(f"[Scene: {self.scene.name}] addItem: id={id(item)}, type={type(item)}"),
            original_addItem(item)
        )[1]

        self.view = ZoomableView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.background_pixmap = None

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        if pixmap:
            self.load_pixmap(pixmap)
        elif image_path:
                self.load_image(image_path)

    def load_image(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            DarkMessageBox.critical(self, "Erreur", f"Impossible de charger l’image : {path}")
            return
        self.load_pixmap(pixmap)


    def load_pixmap(self, pixmap):
        if pixmap.isNull():
            print("[ERROR] Pixmap vide, rien à afficher.")
            return
        debug_log(f"Pixmap size: {pixmap.width()}x{pixmap.height()}")
        self.background_pixmap = pixmap.copy()
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def export_svg(self):
        if not self.image_path:
            DarkMessageBox.warning(self, "Export SVG", "Aucune image de fond chargée.")
            return


        svg_root = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "version": "1.1"
        })

        for item in self.scene.items():
            if isinstance(item, DuplicataGroupItem):
                d_string = item.closed_item.d_string.strip()
                if not d_string:
                    continue

                ET.SubElement(svg_root, "path", {
                    "id": item.element_id,
                    "d": d_string,
                    "fill": "none",
                    "stroke": "black",
                    "stroke-width": "1"
                })

        image_name = os.path.basename(self.image_path)
        base_name, _ = os.path.splitext(image_name)
        default_filename = base_name + ".svg"

        dialog = DarkFileDialog(self, "Exporter en SVG")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter("Fichiers SVG (*.svg)")
        dialog.selectFile(default_filename)

        if dialog.exec_() != QDialog.Accepted:
            return  # annulation

        output_path = dialog.selectedFiles()[0]

        tree = ET.ElementTree(svg_root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

        DarkMessageBox.information(self, "Export SVG", f"Fichier exporté :\n{output_path}")
