#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/layer.py                                                !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from PyQt5.QtWidgets import (
    QWidget, QGraphicsScene, QTreeWidget, QVBoxLayout, QApplication, QAbstractItemView,
)
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from ui.views import ZoomableView
from utils.debug import debug_log

class LayerWidget(QWidget):
    """Classe mère pour SvgLayerWidget et ImageLayerWidget."""
    def __init__(self, tree_header="Éléments"):
        super().__init__()
        self.tree_items_by_id = {}
        self.items_by_id = {}

        # TreeWidget associé au layer
        tree = QTreeWidget()
        tree.setHeaderLabels([tree_header])
        tree.setMinimumWidth(200)
        tree.setSelectionMode(QAbstractItemView.NoSelection)
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
        # Scene et vue
        self.scene = QGraphicsScene()

        self.tree.itemClicked.connect(self.on_tree_item_clicked)

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



