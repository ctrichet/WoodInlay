#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/views.py                                                !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRectF
from core.model_items import GroupItem, DuplicataGroupItem
from utils.debug import debug_log

class ZoomableView(QGraphicsView):
    def __init__(self, layer):
        super().__init__(layer.scene)
        self.layer = layer
        self.setRenderHint(QPainter.Antialiasing)
        self.zoom_factor = 1.25
        self.newly_selected = {}
        self._last_pan_point = None
        self.setDragMode(QGraphicsView.NoDrag)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._rubber_band_rect = None

    ################################- ZOOM -####################################

    def wheelEvent(self, event):
        factor = self.zoom_factor if event.angleDelta().y() > 0 else 1 / self.zoom_factor
        self.scale(factor, factor)

    def zoom_in(self):
        self.scale(self.zoom_factor, self.zoom_factor)

    def zoom_out(self):
        self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)

    ############################################################################

class SvgView(ZoomableView):
    def __init__(self, layer):
        super().__init__(layer)

    def mousePressEvent(self, event):
        self._last_pan_point = event.pos()
        ctrl_pressed = QApplication.keyboardModifiers() & Qt.ControlModifier
        if not ctrl_pressed:
            self.layer.scene.clearSelection()
            self.layer.tree.clearSelection()
        item = self.itemAt(self._last_pan_point)
        if item:
            item = item.parentItem()
            item.closed_item.setPen(QColor(0, 120, 215))
            self.newly_selected[item.element_id] = item

    def mouseMoveEvent(self, event):
        if self._last_pan_point != None:
            ####################- Rubber Band Rectangle -###################
            if self._rubber_band_rect:
                self.layer.scene.removeItem(self._rubber_band_rect)
                self._rubber_band_rect = None
            rect = QRectF(self.mapToScene(self._last_pan_point), self.mapToScene(event.pos())).normalized()
            pen = QPen(QColor(0, 120, 215), 1, Qt.DashLine)  # couleur bleue, style tireté
            self._rubber_band_rect = self.layer.scene.addRect(rect, pen)
            ################################################################
            for item in self.newly_selected.values():
                item.closed_item.setPen()
            self.newly_selected = {}
            items_in_rect = [item for item in self.layer.scene.items(rect, Qt.IntersectsItemShape) if isinstance(item, GroupItem)]
            for item in items_in_rect:
                item.closed_item.setPen(QColor(0, 120, 215))
                self.newly_selected[item.element_id] = item

    def mouseReleaseEvent(self, event):
        if self._rubber_band_rect:
            self.layer.scene.removeItem(self._rubber_band_rect)
            self._rubber_band_rect = None
        if event.button() == Qt.LeftButton:
            for item_id, item in self.newly_selected.items():
                item.closed_item.setPen()
                if not item.isSelected():
                    item.setSelected(True)
                    tree_item = self.layer.tree_items_by_id[item_id]
                    tree_item.setSelected(True)
                    self.layer.set_parent_selection(tree_item)
        elif event.button() == Qt.RightButton:
            for item_id, item in self.newly_selected.items():
                item.closed_item.setPen()
                if item.isSelected():
                    item.setSelected(False)
                    tree_item = self.layer.tree_items_by_id[item_id]
                    tree_item.setSelected(False)
                    parent = tree_item.parent()
                    while parent:
                        if parent.isSelected():
                            parent.setSelected(True)
                            parent = parent.parent()
                        else:
                            break
        self.newly_selected = {}
        self._last_pan_point = None

################################################################################

class ImageView(ZoomableView):
    def __init__(self, layer):
        super().__init__(layer)

    def mousePressEvent(self, event):
        self._last_pan_point = event.pos()
        ctrl_pressed = QApplication.keyboardModifiers() & Qt.ControlModifier
        item = self.itemAt(self._last_pan_point)
        if item:
            item = item.parentItem()
        if ctrl_pressed:
            if item:
                item.closed_item.setPen(QColor(0, 120, 215))
                self.newly_selected[item.element_id] = item
        elif item:
            if item.isSelected():
                self.move = True
                super().mousePressEvent(event)
            else:
                item.closed_item.setPen(QColor(0, 120, 215))
                self.newly_selected[item.element_id] = item
        else:
            self.layer.scene.clearSelection()
            self.layer.tree.clearSelection()

    def mouseMoveEvent(self, event):
        if self._last_pan_point:
            if self.move:
                super().mousePressEvent(event)
            else:
                ####################- Rubber Band Rectangle -###################
                if self._rubber_band_rect:
                    self.layer.scene.removeItem(self._rubber_band_rect)
                    self._rubber_band_rect = None
                rect = QRectF(self.mapToScene(self._last_pan_point), self.mapToScene(event.pos())).normalized()
                pen = QPen(QColor(0, 120, 215), 1, Qt.DashLine)  # couleur bleue, style tireté
                self._rubber_band_rect = self.layer.scene.addRect(rect, pen)
                ################################################################

                for item in self.newly_selected.values():
                    item.closed_item.setPen()
                self.newly_selected = {}
                items_in_rect = [item for item in self.layer.scene.items(rect, Qt.IntersectsItemShape) if isinstance(item, DuplicataGroupItem)]
                for item in items_in_rect:
                    item.closed_item.setPen(QColor(0, 120, 215))
                    self.newly_selected[item.element_id] = item

    def mouseReleaseEvent(self, event):
        if self._rubber_band_rect:
            self.layer.scene.removeItem(self._rubber_band_rect)
            self._rubber_band_rect = None
        if self.move:
            super().mouseReleaseEvent(event)
        elif event.button() == Qt.LeftButton:
            for item_id, item in self.newly_selected.items():
                item.closed_item.setPen()
                if not item.isSelected():
                    item.setSelected(True)
                    tree_item = self.layer.tree_items_by_id[item_id]
                    tree_item.setSelected(True)
                    self.layer.set_parent_selection(tree_item)
        elif event.button() == Qt.RightButton:
            for item_id, item in self.newly_selected.items():
                item.closed_item.setPen()
                if item.isSelected():
                    item.setSelected(False)
                    tree_item = self.layer.tree_items_by_id[item_id]
                    tree_item.setSelected(False)
                    parent = tree_item.parent()
                    while parent:
                        if parent.isSelected():
                            parent.setSelected(True)
                            parent = parent.parent()
                        else:
                            break
        self.newly_selected = {}
        self._last_pan_point = None
        self.move = False
