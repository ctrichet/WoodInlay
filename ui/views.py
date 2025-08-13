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

from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QPointF

class ZoomableView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.zoom_factor = 1.25
        self._panning = False
        self._last_pan_point = QPointF()
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        factor = self.zoom_factor if event.angleDelta().y() > 0 else 1 / self.zoom_factor
        self.scale(factor, factor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.setCursor(Qt.OpenHandCursor)
            self._panning = True
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.setCursor(Qt.ArrowCursor)
            self._panning = False
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if self._panning and event.button() == Qt.LeftButton:
            self._last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and not self._last_pan_point.isNull():
            delta = self.mapToScene(event.pos()) - self.mapToScene(self._last_pan_point)
            self.translate(-delta.x(), -delta.y())
            self._last_pan_point = event.pos()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._panning and event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self._last_pan_point = QPointF()
        else:
            super().mouseReleaseEvent(event)

    def zoom_in(self):
        self.scale(self.zoom_factor, self.zoom_factor)

    def zoom_out(self):
        self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
