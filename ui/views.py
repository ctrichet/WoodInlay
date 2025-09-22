from PyQt5.QtWidgets import (
    QGraphicsView,
    QApplication,
)
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRectF

from core.model_items import GroupItem, DuplicataGroupItem
from styles.colors import Colors

from utils.debug import debug_log


class ZoomableView(QGraphicsView):

    zoom_factor = 1.25

    def __init__(self, layer):
        super().__init__(layer.scene)
        self.layer = layer
        self.setRenderHint(QPainter.Antialiasing)
        self.setObjectName("view")
        self.newly_selected = {}
        self._last_pan_point = None
        self.setDragMode(QGraphicsView.NoDrag)
        self.setMouseTracking(True)
        self._rubber_band_rect = None

    def _can_zoom(self, factor: float) -> bool:
        view_size = self.viewport().size()
        bounds = self.scene().itemsBoundingRect()
        scale = self.transform().m11()
        width = bounds.width() * scale
        height = bounds.height() * scale
        factor_x = view_size.width() / width
        factor_y = view_size.height() / height
        factor = min(factor_x, factor_y)

        return factor < self.zoom_factor

    def wheelEvent(self, event):
        delta_y = event.angleDelta().y() if hasattr(event, "angleDelta") else 0
        if delta_y == 0:
            return

        zoom_in = delta_y > 0
        factor = self.zoom_factor if zoom_in else 1 / self.zoom_factor

        # Empêcher dézoom excessif
        if not zoom_in and not self._can_zoom(factor):
            return

        # Position du curseur dans la scène AVANT le zoom
        old_scene_pos = self.mapToScene(event.pos())

        # Appliquer le zoom
        self.scale(factor, factor)

        # Position du curseur dans la scène APRÈS le zoom
        new_scene_pos = self.mapToScene(event.pos())

        # Offset pour garder le curseur fixe
        offset = new_scene_pos - old_scene_pos
        current_center = self.mapToScene(self.viewport().rect().center())
        self.centerOn(current_center - offset)

        self.update_padding()

    def zoom_in(self):
        self.scale(self.zoom_factor, self.zoom_factor)
        self.update_padding()

    def zoom_out(self):
        factor = 1 / self.zoom_factor
        if self._can_zoom(factor):
            self.scale(factor, factor)
            self.update_padding()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_padding()

    def update_padding(self):
        if self.layer.scene.items():
            bounds = self.scene().itemsBoundingRect()
            scale = self.transform().m11()
            # debug_log(f"Bounding_Rect : width = {bounds.width()}, height = {bounds.height()}")
            horizontal_padding = self.viewport().width() - scale * bounds.width() * 0.5
            vertical_padding = self.viewport().height() - scale * bounds.height() * 0.5
            if horizontal_padding < 0:
                horizontal_padding = 0
            if vertical_padding < 0:
                vertical_padding = 0
            padded_rect = bounds.adjusted(
                -horizontal_padding,
                -vertical_padding,
                horizontal_padding,
                vertical_padding,
            )
            self.layer.scene.setSceneRect(padded_rect)

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
            item.closed_item.setPen(QColor(Colors.preselection))
            self.newly_selected[item.element_id] = item

    def mouseMoveEvent(self, event):
        if self._last_pan_point != None:
            ####################- Rubber Band Rectangle -###################
            if self._rubber_band_rect:
                self.layer.scene.removeItem(self._rubber_band_rect)
                self._rubber_band_rect = None
            rect = QRectF(
                self.mapToScene(self._last_pan_point), self.mapToScene(event.pos())
            ).normalized()
            pen = QPen(
                QColor(Colors.preselection), 1, Qt.DashLine
            )  # couleur bleue, style tireté
            self._rubber_band_rect = self.layer.scene.addRect(rect, pen)
            ################################################################
            for item in self.newly_selected.values():
                item.closed_item.setPen()
            self.newly_selected = {}
            items_in_rect = [
                item
                for item in self.layer.scene.items(rect, Qt.IntersectsItemShape)
                if isinstance(item, GroupItem)
            ]
            for item in items_in_rect:
                item.closed_item.setPen(QColor(Colors.preselection))
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
        self.move = False

    def mousePressEvent(self, event):
        self._last_pan_point = event.pos()
        ctrl_pressed = QApplication.keyboardModifiers() & Qt.ControlModifier
        item = self.itemAt(self._last_pan_point)
        if item:
            item = item.parentItem()
        if ctrl_pressed:
            if item:
                item.closed_item.setPen(QColor(Colors.preselection))
                self.newly_selected[item.element_id] = item
        elif item:
            if item.isSelected():
                self.move = True
                super().mousePressEvent(event)
            else:
                item.closed_item.setPen(QColor(Colors.preselection))
                self.newly_selected[item.element_id] = item
        else:
            self.layer.scene.clearSelection()
            self.layer.tree.clearSelection()

    def mouseMoveEvent(self, event):
        if self._last_pan_point:
            if self.move:
                super().mouseMoveEvent(event)
            else:
                ####################- Rubber Band Rectangle -###################
                if self._rubber_band_rect:
                    self.layer.scene.removeItem(self._rubber_band_rect)
                    self._rubber_band_rect = None
                rect = QRectF(
                    self.mapToScene(self._last_pan_point), self.mapToScene(event.pos())
                ).normalized()
                pen = QPen(QColor(Colors.preselection), 1, Qt.DashLine)
                self._rubber_band_rect = self.layer.scene.addRect(rect, pen)
                ################################################################

                for item in self.newly_selected.values():
                    item.closed_item.setPen()
                self.newly_selected = {}
                items_in_rect = [
                    item
                    for item in self.layer.scene.items(rect, Qt.IntersectsItemShape)
                    if isinstance(item, DuplicataGroupItem)
                ]
                for item in items_in_rect:
                    item.closed_item.setPen(QColor(Colors.preselection))
                    self.newly_selected[item.element_id] = item

    def mouseReleaseEvent(self, event):
        if self._rubber_band_rect:
            self.layer.scene.removeItem(self._rubber_band_rect)
            self._rubber_band_rect = None
        if self.move:
            super().mouseReleaseEvent(event)
            for item in self.layer.scene.selectedItems():
                if isinstance(item, DuplicataGroupItem):
                    item.mask()
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
