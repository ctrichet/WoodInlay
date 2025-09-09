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

def perform_unique_duplication(selected_items, target_layer, window):
    """Effectue une duplication spécifique d'items."""
    for item in selected_items:
        item.duplicate(target_layer.view)
        # mettre à jour le mapping TreeWidget si nécessaire
        element_id = item.element_id
        tree_item = window.svg_layer.tree_items_by_id.get(element_id)
        if tree_item:
            window.apply_tree_item_color(tree_item, item.duplicata.background_id)

         # 3️⃣ Créer le QTreeWidgetItem dans le tree du calque cible
        parent_tree_item = target_layer.tree.invisibleRootItem()
        tree_item = QTreeWidgetItem(parent_tree_item)
        tree_item.setText(0, element_id)
        tree_item.setData(0, Qt.UserRole, element_id)

        # 4️⃣ Mettre à jour le mapping tree_items_by_id du calque cible
        target_layer.tree_items_by_id[element_id] = tree_item