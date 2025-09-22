#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/layer.py                                                !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 16:07:05 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPainter
from PyQt5.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QTreeWidget,
    QHBoxLayout,
    QApplication,
    QGraphicsView,
    QAbstractItemView,
    QVBoxLayout,
)

from styles.colors import Colors

from utils.debug import debug_log


class LayerWidget(QWidget):
    """Classe mère pour SvgLayerWidget et ImageLayerWidget."""

    def __init__(self, tree_header="Éléments"):
        super().__init__()
        self.tree_items_by_id = {}
        self.items_by_id = {}
        self.margin_color = QColor(
            Colors.svg_frame
        )  # couleur par défaut si non redéfinie

        # TreeWidget associé au layer
        tree = QTreeWidget()
        tree.setHeaderLabels([tree_header])
        tree.setMinimumWidth(200)
        tree.setSelectionMode(QAbstractItemView.NoSelection)
        tree.setAutoFillBackground(True)
        self.tree = tree

        # Scene et vue
        self.scene = QGraphicsScene()
        self.tree.itemClicked.connect(self.on_tree_item_clicked)

    def init_view(self, view: QGraphicsView):
        """Initialise la view du layer avec le background brush et layout."""
        self.view = view
        self.view.setRenderHint(QPainter.Antialiasing)
        # Fond de la view identique à la couleur du layer
        self.view.setBackgroundBrush(QBrush(QColor(Colors.alternate_base)))

        # Layout vertical avec marges pour voir le cadre
        layout = QVBoxLayout()
        layout.setContentsMargins(13, 13, 0, 0)  # laisse apparaître le "cadre"
        layout.addWidget(self.view)
        self.setLayout(layout)

    def build_tab_container(self, tab_color=None):
        if tab_color is None:
            tab_color = self.margin_color

        # cadre extérieur (wrapper) — on garde le background existant pour l'effet "cadre"
        outer_frame = QWidget()
        # Attache une référence au LayerWidget pour pouvoir le retrouver depuis l'onglet
        outer_frame.layer_widget = self
        outer_frame.setStyleSheet(
            f"background-color: {tab_color.name()}; border-radius: 6px;"
        )

        inner_layout = QHBoxLayout(outer_frame)

        inner_container = QWidget()
        content_layout = QHBoxLayout(inner_container)
        # on ajoute le LayerWidget lui-même dans le container interne
        content_layout.addWidget(self)
        inner_layout.addWidget(inner_container)

        return outer_frame

    def on_tree_item_clicked(self, item, column):
        debug_log()

        def update_item_and_children_selection(item, selected):
            item.setSelected(selected)
            if item.childCount():
                for idx in range(item.childCount()):
                    update_item_and_children_selection(item.child(idx), selected)
            item_id = item.data(0, Qt.UserRole)
            if item_id in self.items_by_id:
                self.items_by_id[item_id].setSelected(selected)

        ctrl_pressed = QApplication.keyboardModifiers() & Qt.ControlModifier
        self.tree.blockSignals(True)
        self.scene.blockSignals(True)

        if ctrl_pressed:
            previously_selected = item.isSelected()
            debug_log(f"previously_selected = {previously_selected}")
            update_item_and_children_selection(item, not previously_selected)
            if previously_selected:
                parent = item.parent()
                while parent and parent.isSelected():
                    parent.setSelected(False)
                    parent = parent.parent()
            else:
                self.set_parent_selection(item)
        else:
            self.tree.clearSelection()
            self.scene.clearSelection()
            update_item_and_children_selection(item, True)
            self.set_parent_selection(item)

        self.tree.blockSignals(False)
        self.scene.blockSignals(False)

    def set_parent_selection(self, item):
        parent = item.parent()
        if not parent:
            return
        for idx in range(parent.childCount()):
            if not parent.child(idx).isSelected():
                return
        parent.setSelected(True)
        self.set_parent_selection(parent)
