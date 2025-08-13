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

    def parse_svg_or_group(self):
        """Parse le fichier SVG et envoie les données à la fenêtre."""
        debug_log("parse_svg_or_group: START")

        try:
            tree = ET.parse(self._svg_file)
        except Exception as e:
            debug_log(f"[ERROR] Impossible de parser {self._svg_file} : {e}")
            return

        root = tree.getroot()

        # imports locaux pour éviter les cycles
        from core.model_items import GroupItem, PathItem

        def ensure_id(elem):
            if "id" not in elem.attrib:
                elem.set("id", f"auto_{uuid.uuid4().hex[:8]}")
            return elem.attrib["id"]

        def is_closed(d):
            if not d:
                return False
            d_cleaned = re.sub(r'[\s,]+', ' ', d.strip()).upper()
            return bool(re.search(r'M[^MZ]*Z', d_cleaned))

        def process_group_or_svg(group_elem, parent_tree_item=None):
            group_id = ensure_id(group_elem)
            tree_item = self.window.add_group_to_tree(group_id, parent_tree_item)

            closed = []
            open_ = []

            for child in group_elem:
                tag = child.tag.lower().split("}")[-1]

                if tag == "g":
                    process_group_or_svg(child, tree_item)
                    continue

                if tag in {"text", "image", "use", "style", "title", "desc", "defs", "clippath", "marker"}:
                    debug_log(f"[IGNORE] Élement ignoré : {tag}")
                    continue

                element_id = ensure_id(child)
                path_d = ""

                if tag == "path":
                    path_d = child.attrib.get("d", "")

                elif tag == "rect":
                    x = float(child.attrib.get("x", "0"))
                    y = float(child.attrib.get("y", "0"))
                    w = float(child.attrib.get("width", "0"))
                    h = float(child.attrib.get("height", "0"))
                    path_d = f"M{x},{y} h{w} v{h} h{-w} Z"

                elif tag == "circle":
                    cx = float(child.attrib.get("cx", "0"))
                    cy = float(child.attrib.get("cy", "0"))
                    r = float(child.attrib.get("r", "0"))
                    path_d = (
                        f"M{cx - r},{cy} "
                        f"a{r},{r} 0 1,0 {2*r},0 "
                        f"a{r},{r} 0 1,0 {-2*r},0 Z"
                    )

                elif tag == "ellipse":
                    cx = float(child.attrib.get("cx", "0"))
                    cy = float(child.attrib.get("cy", "0"))
                    rx = float(child.attrib.get("rx", "0"))
                    ry = float(child.attrib.get("ry", "0"))
                    path_d = (
                        f"M{cx - rx},{cy} "
                        f"a{rx},{ry} 0 1,0 {2*rx},0 "
                        f"a{rx},{ry} 0 1,0 {-2*rx},0 Z"
                    )

                elif tag == "polygon":
                    points = child.attrib.get("points", "").strip()
                    path_d = f"M{points} Z"

                elif tag == "polyline":
                    points = child.attrib.get("points", "").strip()
                    path_d = f"M{points}"

                elif tag == "line":
                    x1 = float(child.attrib.get("x1", "0"))
                    y1 = float(child.attrib.get("y1", "0"))
                    x2 = float(child.attrib.get("x2", "0"))
                    y2 = float(child.attrib.get("y2", "0"))
                    path_d = f"M{x1},{y1} L{x2},{y2}"

                else:
                    debug_log(f"[SKIP] ⛔ Balise non supportée : {tag}")
                    continue

                if not path_d:
                    continue

                item = PathItem(path_d)
                if is_closed(path_d):
                    closed.append((element_id, item))
                else:
                    open_.append(item)

            if len(closed) == 0:
                return

            elif len(closed) > 1:
                for element_id, closed_item in closed:
                    group_item = GroupItem(element_id, closed_item)
                    self.window.add_svg_item(group_item, tree_item)

            elif len(closed) == 1:
                element_id, closed_item = closed[0]
                group_item = GroupItem(element_id, closed_item, open_)
                self.window.add_svg_item(group_item, tree_item)

        if root.tag.lower().endswith("svg"):
            process_group_or_svg(root, parent_tree_item=None)
        else:
            debug_log("[WARN] Le fichier racine n'est pas un <svg>.")

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
