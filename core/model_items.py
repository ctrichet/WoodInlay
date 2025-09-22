#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   core/model_items.py                                        !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 17:46:14 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
from math import hypot
from PyQt5.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsItemGroup,
    QGraphicsPixmapItem,
    QStyle,
    QGraphicsSceneMouseEvent,
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import (
    QPainterPath,
    QImage,
    QPixmap,
    QPainter,
    QPen,
    QPolygonF,
    QColor,
)
from styles.colors import Colors
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
                            e.control1.real,
                            e.control1.imag,
                            e.control2.real,
                            e.control2.imag,
                            e.end.real,
                            e.end.imag,
                        )
                    elif e.__class__.__name__ == "QuadraticBezier":
                        path.quadTo(
                            e.control.real, e.control.imag, e.end.real, e.end.imag
                        )
                    elif e.__class__.__name__ == "Arc":
                        path.lineTo(e.end.real, e.end.imag)
                    else:
                        path.lineTo(e.end.real, e.end.imag)
            except Exception as e:
                print(f"[ERREUR] Parsing du path SVG échoué : {e}")
            path.setFillRule(Qt.OddEvenFill)
            return path

        painter_path = parse_svg_path_d(d_string)
        super().__init__(painter_path, parent)
        self.d_string = d_string

    def setPen(self, color=QColor(Colors.outline)):
        pen = QPen(color)
        super().setPen(pen)


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
            self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsGeometryChanges
        )

    def shape(self):
        return self.closed_item.path()

    def paint(self, painter, option, widget=None):
        if option.state & QStyle.State_Selected:
            painter.setPen(
                QPen(QColor(Colors.highlight))
            )  # couleur sélection personnalisée
        else:
            painter.setPen((QPen(QColor(Colors.outline))))
        super().paint(painter, option, widget)


class GroupItem(CompositeGroupItem):
    def __init__(self, element_id, closed_item, open_items=None, parent=None):
        super().__init__(element_id, closed_item, open_items, parent)
        self.duplicata = None
        self.setFlags(self.ItemIsSelectable)


class DuplicataGroupItem(CompositeGroupItem):
    @staticmethod
    def estimate_rotation(item):
        p1 = item.mapToScene(item.boundingRect().topLeft())
        p2 = item.mapToScene(item.boundingRect().topRight())
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        return degrees(atan2(dy, dx))

    def __init__(self, groupItem, layer, parent=None):
        closed_dup = PathItem(d_string=groupItem.closed_item.d_string)
        open_items = []
        for item in groupItem.childItems():
            if item is groupItem.closed_item:
                continue
            open_dup = PathItem(d_string=item.d_string)
            open_items.append(open_dup)

        super().__init__(groupItem.element_id, closed_dup, open_items, parent)
        self.layer = layer
        self.mask_item_pos = groupItem.pos()
        debug_log(
            f"groupItem.closed_item.boundingRect().topLeft() = {groupItem.closed_item.boundingRect().topLeft()}"
        )
        debug_log(
            f"groupItem.closed_item.sceneBoundingRect().topLeft() = {groupItem.closed_item.sceneBoundingRect().topLeft()}"
        )
        self.mask_item = None
        self.setFlags(
            self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsGeometryChanges
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

            selected_items = [
                item
                for item in MainWindow._instance.get_layer_widget_from_tab(
                    MainWindow._instance.tabs.currentWidget()
                ).scene.selectedItems()
                if isinstance(item, DuplicataGroupItem)
            ]
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
        debug_log(
            f"[DuplicataGroupItem] 🖱️ Mouse released — actualisation du masque pour {self.element_id}"
        )

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

        image_layer_widget = self.layer
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

    def to_polygon(self, tolerance: float = 0.002) -> QPolygonF:
        """
        Retourne un QPolygonF approximant le tracé fermé du duplicata,
        transformé dans les coordonnées de la scène, prêt pour le nesting.
        La simplification conserve le premier point exact pour un offset fiable.
        :param tolerance: tolérance de simplification en pixels
        """
        path = self.closed_item.path()
        polygon = path.toFillPolygon()  # QPolygonF

        if polygon.isEmpty():
            return QPolygonF()

        # Appliquer transformation globale
        transformed_polygon = self.sceneTransform().map(polygon)

        # Simplification avec conservation du premier point
        if tolerance > 0 and len(transformed_polygon) > 2:
            simplified = QPolygonF()
            first_point = transformed_polygon[0]
            simplified.append(first_point)  # garder le premier point exact
            prev_point = first_point

            for pt in transformed_polygon[1:]:
                if hypot(pt.x() - prev_point.x(), pt.y() - prev_point.y()) >= tolerance:
                    simplified.append(pt)
                    prev_point = pt

            # Pas besoin de fermer arbitrairement : polygone déjà fermé
            transformed_polygon = simplified

        return transformed_polygon

    def to_shapely_polygon(self, tolerance):
        """
        Convertit le QPolygonF en shapely.geometry.Polygon.
        Garantit que le premier point reste le même pour calculer un offset précis.
        """
        from shapely.geometry import Polygon

        qpoly = self.to_polygon(tolerance)
        if qpoly.isEmpty():
            return Polygon()

        coords = [(pt.x(), pt.y()) for pt in qpoly]
        return Polygon(coords)
