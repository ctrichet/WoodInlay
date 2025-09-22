#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/svg_layer.py                                            !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 19:50:24 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
import re
import uuid
import xml.etree.ElementTree as ET

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QTreeWidgetItem, QFileDialog

from core.model_items import PathItem, GroupItem
from ui.layer import LayerWidget
from ui.views import SvgView

from utils.debug import debug_log


class SvgLayerWidget(LayerWidget):

    def __init__(self, file_path):
        super().__init__()
        self.init_view(SvgView(self))
        self.parse_svg(file_path)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.update_padding()

    def parse_svg(self, svg_file):
        try:
            tree = ET.parse(svg_file)
        except Exception as e:
            debug_log(f"[ERROR] Impossible de parser {svg_file} : {e}")
            return

        root = tree.getroot()
        if root.tag.lower().endswith("svg"):
            self.process_svg_element(root, [])
        else:
            debug_log("[WARN] Le fichier racine n'est pas un <svg>.")

    def process_svg_element(self, element, ancestors_tree_items):
        def ensure_id(elem):
            if "id" not in elem.attrib:
                elem.set("id", f"auto_{uuid.uuid4().hex[:8]}")
            return elem.attrib["id"]

        def is_closed(d):
            if not d:
                return False
            d_cleaned = re.sub(r"[\s,]+", " ", d.strip()).upper()
            return bool(re.search(r"M[^MZ]*Z", d_cleaned))

        element_id = ensure_id(element)
        tree_item = QTreeWidgetItem()
        tree_item.setText(0, element_id)
        tree_item.setData(0, Qt.UserRole, element_id)
        # Dans le cas de la racine
        if not len(ancestors_tree_items):
            self.tree.addTopLevelItem(tree_item)
            self.tree_items_by_id[element_id] = tree_item
        ancestors_tree_items.append(tree_item)

        closed = []
        open_ = []
        for child in element:
            tag = child.tag.lower().split("}")[-1]

            if tag == "g":
                self.process_svg_element(child, ancestors_tree_items.copy())
                continue

            if tag in {
                "text",
                "image",
                "use",
                "style",
                "title",
                "desc",
                "defs",
                "clippath",
                "marker",
            }:
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

        else:
            # On ajoute les tree_items de leurs ancetres
            tree_item_idx = len(ancestors_tree_items) - 1
            while tree_item_idx > 0:
                tree_item = ancestors_tree_items[tree_item_idx]
                if tree_item.parent():
                    break
                else:
                    tree_item_id = tree_item.data(0, Qt.UserRole)
                    self.tree_items_by_id[tree_item_id] = tree_item
                    ancestors_tree_items[tree_item_idx - 1].addChild(tree_item)
                    tree_item_idx -= 1

            if len(closed) != 1:
                open_ = []

            for element_id, closed_item in closed:
                group_item = GroupItem(element_id, closed_item, open_)
                self.scene.addItem(group_item)
                self.items_by_id[element_id] = group_item

                tree_item = QTreeWidgetItem(ancestors_tree_items[-1])
                tree_item.setText(0, element_id)
                tree_item.setData(0, Qt.UserRole, element_id)
                self.tree_items_by_id[element_id] = tree_item

    def capture_png(self):

        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PNG", "", "Images PNG (*.png)"
        )
        if not filename:
            return  # Annulé par l'utilisateur

        # Forcer l'extension .png si absente
        if not filename.lower().endswith(".png"):
            filename += ".png"

        # Créer une image de la taille du widget
        image = QImage(self.size(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        # Peindre le contenu du widget sur l'image
        painter = QPainter(image)
        self.render(painter)
        painter.end()

        # Sauvegarder en PNG
        if not image.save(filename, "PNG"):
            print(f"[ERREUR] Impossible de sauvegarder {filename}")
        else:
            print(f"[OK] Capture exportée : {filename}")
