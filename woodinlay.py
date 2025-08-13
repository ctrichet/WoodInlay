#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   woodinlay.py                                               !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import os
import uuid
import re
import xml.etree.ElementTree as ET

from PyQt5.QtCore import Qt
from utils.debug import debug_log


class WoodInlayManager:
    """
    Gère les données et la logique métier de l'application.
    Ne dérive plus de QApplication (c'est géré par app.py).
    """
    _svg_file = "../design.svg"
    _supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")

    def __init__(self):
        # État global
        self.background_files = {}
        self.items_by_id = {}
        self.groups_by_id = {}
        self.window = None

    def perform_unique_duplication(self, selected_items, target_view):
        """Effectue une duplication spécifique d'items."""
        from core.model_items import GroupItem

        for item in selected_items:
            if isinstance(item, GroupItem):
                if item.duplicate(target_view):
                    element_id = item.element_id
                    bg_filename = os.path.basename(target_view.scene().name)

                    tree_item = self.window.tree_items_by_id.get(element_id)
                    if tree_item:
                        self.window.apply_tree_item_color(tree_item, bg_filename)
