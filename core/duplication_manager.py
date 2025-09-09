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
from core.model_items import GroupItem, DuplicataGroupItem

def perform_unique_duplication(selected_items, target_view, window):
    """Effectue une duplication spécifique d'items."""
    for item in selected_items:
        item.duplicate(target_view)
        # mettre à jour le mapping TreeWidget si nécessaire
        element_id = item.element_id
        tree_item = window.tree_items_by_id.get(element_id)
        if tree_item:
            window.apply_tree_item_color(tree_item, item.duplicata.background_id)
