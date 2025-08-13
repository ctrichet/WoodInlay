#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   core/model_items.py                                        !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####
from PyQt5.QtWidgets import (
    QGraphicsPathItem, QGraphicsItemGroup, QGraphicsPixmapItem,
    QGraphicsSceneMouseEvent,
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import (
    QPainterPath, QImage, QPixmap, QPainter, QTransform
)
from math import radians, cos, sin, atan2, degrees
from svg.path import parse_path

from utils.debug import debug_log

class PathItem(QGraphicsPathItem):
    def __init__(self, d_string, parent=None):
        def parse_svg_path_d(d_string):
            path = QPainterPath()
            if not d_string:
                return path
            try:
                svg_path = parse_path(d_string)
                for e in svg_path:
                    start = e.start
                    if path.isEmpty():
                        path.moveTo(start.real, start.imag)
                    if e.__class__.__name__ == "Line":
                        path.lineTo(e.end.real, e.end.imag)
                    elif e.__class__.__name__ == "CubicBezier":
                        path.cubicTo(
                            e.control1.real, e.control1.imag,
                            e.control2.real, e.control2.imag,
                            e.end.real, e.end.imag
                        )
                    elif e.__class__.__name__ == "QuadraticBezier":
                        path.quadTo(
                            e.control.real, e.control.imag,
                            e.end.real, e.end.imag
                        )
                    elif e.__class__.__name__ == "Arc":
                        path.lineTo(e.end.real, e.end.imag)
                    else:
                        path.lineTo(e.end.real, e.end.imag)
            except Exception as e:
                print(f"[ERREUR] Parsing du path SVG échoué : {e}")
            return path

        painter_path = parse_svg_path_d(d_string)
        super().__init__(painter_path, parent)
        self.d_string = d_string


class CompositeGroupItem(QGraphicsItemGroup):
    def __init__(self, element_id, closed_item, open_items, parent=None):
        super().__init__(parent)
        self.element_id = element_id
        self.closed_item = closed_item
        self.addToGroup(closed_item)
        if open_items:
            for item in open_items:
                self.addToGroup(item)
        self.setFlags(
            self.ItemIsSelectable |
            self.ItemIsMovable |
            self.ItemSendsGeometryChanges
        )

    def shape(self):
        return self.closed_item.path()


class GroupItem(CompositeGroupItem):
    def __init__(self, element_id, closed_item, open_items=None, parent=None):
        super().__init__(element_id, closed_item, open_items, parent)
        self.duplicata = None
        self.setFlags(self.ItemIsSelectable)

    def duplicate(self, target_view):
        scene = target_view.scene()
        background_id = scene.name
        if self.duplicata:
            if self.duplicata.background_id == background_id:
                return False
            self.duplicata.scene().removeItem(self.duplicata)
        self.duplicata = DuplicataGroupItem(self, background_id)
        self.add_duplicata_to_background(scene)
        return True

    def add_duplicata_to_background(self, scene):
        scene.addItem(self.duplicata)
        self.duplicata.mask()


class DuplicataGroupItem(CompositeGroupItem):
    @staticmethod
    def estimate_rotation(item):
        p1 = item.mapToScene(item.boundingRect().topLeft())
        p2 = item.mapToScene(item.boundingRect().topRight())
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        return degrees(atan2(dy, dx))

    def __init__(self, groupItem, background_id, parent=None):
        element_id = f"{groupItem.element_id}_dup"
        closed_dup = PathItem(d_string=groupItem.closed_item.d_string)
        open_items = []
        for item in groupItem.childItems():
            if item is groupItem.closed_item:
                continue
            open_dup = PathItem(d_string=item.d_string)
            open_items.append(open_dup)

        super().__init__(element_id, closed_dup, open_items, parent)
        self.background_id = background_id
        self.mask_item_pos = groupItem.pos()
        debug_log(f"groupItem.closed_item.boundingRect().topLeft() = {groupItem.closed_item.boundingRect().topLeft()}")
        debug_log(f"groupItem.closed_item.sceneBoundingRect().topLeft() = {groupItem.closed_item.sceneBoundingRect().topLeft()}")
        self.mask_item = None
        self.setFlags(
            self.ItemIsSelectable |
            self.ItemIsMovable |
            self.ItemSendsGeometryChanges
        )
        self._right_dragging = False
        self._last_mouse_pos = None
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.OpenHandCursor)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self._right_dragging and self._last_mouse_pos is not None:
            # Calculer la rotation en fonction du déplacement horizontal de la souris
            delta_x = event.scenePos().x() - self._last_mouse_pos.x()
            rotation_angle = delta_x  # ou delta_x * un facteur de sensibilité

            # Rotation groupée
            from ui.main_window import MainWindow
            selected_items = [item for item in MainWindow._instance.active_scene().selectedItems() if isinstance(item, DuplicataGroupItem)]
            MainWindow._instance.rotate_group(selected_items, rotation_angle)

            self._last_mouse_pos = event.scenePos()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)

        elif event.button() == Qt.RightButton:
            self._right_dragging = True
            self._last_mouse_pos = event.scenePos()
            self.setCursor(Qt.SizeAllCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.RightButton and self._right_dragging:
            self._right_dragging = False
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
            self.mask()
            return

        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)
        debug_log(f"[DuplicataGroupItem] 🖱️ Mouse released — actualisation du masque pour {self.element_id}")
        self.mask()

    def mask(self):
        def rotate_vector(vec: QPointF, angle_degrees: float) -> QPointF:
            angle_rad = radians(angle_degrees)
            x = vec.x() * cos(angle_rad) - vec.y() * sin(angle_rad)
            y = vec.x() * sin(angle_rad) + vec.y() * cos(angle_rad)
            return QPointF(x, y)

        from ui.main_window import MainWindow
        main_window = MainWindow._instance
        if self.mask_item:
            main_window.svg_layer.scene.removeItem(self.mask_item)

        image_layer_widget = main_window.image_layer_widgets.get(self.background_id)
        pixmap = image_layer_widget.background_pixmap

        original_path = self.closed_item.path()
        transformed_path = self.sceneTransform().map(original_path)
        bounding_rect = transformed_path.boundingRect().toRect().adjusted(-1, -1, 1, 1)

        output_image = QImage(bounding_rect.size(), QImage.Format_ARGB32_Premultiplied)
        output_image.fill(Qt.transparent)

        painter = QPainter(output_image)
        painter.setRenderHint(QPainter.Antialiasing)
        clip_offset = -bounding_rect.topLeft()
        painter.setClipPath(transformed_path.translated(clip_offset))
        painter.drawPixmap(clip_offset, pixmap)
        painter.end()

        masked_pixmap = QPixmap.fromImage(output_image)
        masked_item = QGraphicsPixmapItem(masked_pixmap)
        masked_item.setOpacity(0.85)
        masked_item.setPos(bounding_rect.topLeft())

        main_window.svg_layer.scene.addItem(masked_item)
        masked_origin_scene = masked_item.mapToScene(masked_item.transformOriginPoint())
        duplicata_origin_scene = self.mapToScene(self.transformOriginPoint())
        offset = masked_origin_scene - duplicata_origin_scene
        offset = rotate_vector(offset, -self.rotation())
        masked_item.setRotation(-self.rotation())
        masked_item.setPos(self.mask_item_pos + offset)
        self.mask_item = masked_item
