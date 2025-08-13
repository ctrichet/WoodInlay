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
from core.model_items import GroupItem

def perform_unique_duplication(selected_items, target_view, window):
    """Effectue une duplication spécifique d'items."""
    for item in selected_items:
        if isinstance(item, GroupItem):
            if item.duplicate(target_view):
                element_id = item.element_id
                bg_filename = os.path.basename(target_view.scene().name)

                tree_item = window.tree_items_by_id.get(element_id)
                if tree_item:
                    window.apply_tree_item_color(tree_item, bg_filename)