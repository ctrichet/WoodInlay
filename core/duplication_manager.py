#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   core/duplication_manager.py                                !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/21 14:32:45 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/21 14:32:45 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#

from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt

from core.model_items import DuplicataGroupItem
from utils.debug import debug_log


def perform_unique_duplication(selected_items, layer, svg_layer):
    """Effectue une duplication spécifique d'items."""
    parent_items = {}
    for tree_item in selected_items:
        item_id = tree_item.data(0, Qt.UserRole)
        tree_item_id = item_id
        if not tree_item_id in layer.tree_items_by_id.keys():
            tree_item_copy = QTreeWidgetItem([tree_item.text(0)])
            tree_item_copy.setData(0, Qt.UserRole, tree_item.data(0, Qt.UserRole))
            layer.tree_items_by_id[tree_item_id] = tree_item_copy
            parent_item = tree_item.parent()
            while True:
                if parent_item:
                    parent_tree_id = parent_item.data(0, Qt.UserRole)
                    if parent_tree_id in layer.tree_items_by_id.keys():
                        layer.tree_items_by_id[parent_tree_id].addChild(tree_item_copy)
                        break
                    else:
                        parent_item_copy = QTreeWidgetItem([parent_item.text(0)])
                        tree_item_copy.setData(
                            0, Qt.UserRole, parent_item.data(0, Qt.UserRole)
                        )
                        layer.tree_items_by_id[parent_tree_id] = parent_item_copy
                        parent_item_copy.addChild(tree_item_copy)
                        parent_item = parent_item.parent()
                        tree_item_copy = parent_item_copy
                else:
                    layer.tree.addTopLevelItem(tree_item_copy)
                    break

        if item_id in svg_layer.items_by_id.keys():
            group_item = svg_layer.items_by_id[item_id]

            if group_item.duplicata:
                previous_layer = group_item.duplicata.layer
                if previous_layer == layer:
                    continue
                previous_layer.scene.removeItem(group_item.duplicata)
                previous_layer.items_by_id.pop(item_id)
                tree_item = previous_layer.tree_items_by_id[item_id]
                parent = tree_item.parent()
                if parent:
                    parent.takeChild(parent.indexOfChild(tree_item))
                previous_layer.tree_items_by_id.pop(item_id)
            group_item.duplicata = DuplicataGroupItem(group_item, layer)
            layer.items_by_id[item_id] = group_item.duplicata
            layer.scene.addItem(group_item.duplicata)
            debug_log(f"Adding duplicata {item_id} to layer {layer.scene.name}")
            tree_item = svg_layer.tree_items_by_id[item_id]
            debug_log(
                f"Nombre de colonnes dans le treeWidget : {tree_item.columnCount()}"
            )
            tree_item.setBackground(0, QBrush(layer.margin_color))

            for col in range(tree_item.columnCount()):
                tree_item.setBackground(col, QBrush(layer.margin_color))

            debug_log(
                f"Coloring item {item_id} with color {layer.margin_color} of layer {layer.scene.name}"
            )
            parent_tree_item = tree_item.parent()
            if parent_tree_item:
                parent_items[parent_tree_item.data(0, Qt.UserRole)] = parent_tree_item
            group_item.duplicata.mask()

    # Coloration des parents dans l'arbre SVG
    for tree_item in parent_items.values():
        while tree_item:
            all_children = True
            for idx in range(tree_item.childCount()):
                if tree_item.child(idx).background(0).color() != layer.margin_color:
                    all_children = False
                    break
            if all_children:
                tree_item.setBackground(0, QBrush(layer.margin_color))
            else:
                break
            tree_item = tree_item.parent()
