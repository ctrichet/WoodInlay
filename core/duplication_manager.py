#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   core/duplication_manager.py                                !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import os
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import Qt

from core.model_items import GroupItem, DuplicataGroupItem
from utils.debug import debug_log

def perform_unique_duplication(selected_items, layer, svg_layer):
    """Effectue une duplication spécifique d'items."""
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
                        tree_item_copy.setData(0, Qt.UserRole, parent_item.data(0, Qt.UserRole))
                        layer.tree_items_by_id[parent_tree_id] = parent_item_copy
                        parent_item_copy.addChild(tree_item_copy)
                        parent_item = parent_item.parent()
                        tree_item_copy = parent_item_copy
                else:
                    layer.tree.addTopLevelItem(tree_item_copy)
                    break

        if item_id in svg_layer.items_by_id.keys():
            svg_layer.items_by_id[item_id].duplicate(layer)
