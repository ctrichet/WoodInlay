#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/tab_bar.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 19:55:37 githubactions                 :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtWidgets import (
    QTabBar,
    QStyleOptionTab,
    QStyle,
    QFileDialog,
    QDialog,
    QToolButton,
    QMessageBox,
)

from core.model_items import DuplicataGroupItem
from ui.image_layer import ImageLayerWidget
from styles.colors import Colors

from utils.debug import debug_log


class CustomTabBar(QTabBar):
    _window = None
    _min_width = 35
    _max_width = 150

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tab_colors = {}
        self.close_buttons = {}
        self.setUsesScrollButtons(False)
        self.add_plus_tab()  # Ajoute le "+" au démarrage

    def tabSizeHint(self, index):
        count = self.count()
        total_width = self.parent().width()
        debug_log(f"total_width = {total_width}, count = {count}")
        size = super().tabSizeHint(index)

        if count == 0:
            return size

        tab_width = total_width / count
        tab_width = max(
            CustomTabBar._min_width, min(CustomTabBar._max_width, tab_width)
        )

        if index == count - 1:  # onglet "+"
            tab_width = CustomTabBar._min_width

        return QSize(int(tab_width), size.height())

    def add_plus_tab(self):
        """Ajoute l'onglet spécial + à la fin."""
        self.addTab("+")
        self.set_tab_color(self.count() - 1, QColor(Colors.plus_tab))

    def add_image_tab(self, index: int, color: QColor):
        """Ajoute seulement le bouton de fermeture et la couleur de l'onglet."""
        self.set_tab_color(index, color)

        close_btn = QToolButton(self)
        close_btn.setObjectName("close_btn")
        close_btn.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        close_btn.setAutoRaise(True)
        close_btn.clicked.connect(lambda _, i=index: self.close_tab(i))
        self.setTabButton(index, QTabBar.RightSide, close_btn)
        self.close_buttons[index] = close_btn

    def close_tab(self, index: int):

        self._window.tabs.blockSignals(True)
        frame = self.parent().widget(index)
        image_layer_widget = frame.findChildren(ImageLayerWidget)[0]

        for item in image_layer_widget.scene.items():
            if isinstance(item, DuplicataGroupItem):
                tree_item = self._window.svg_layer.tree_items_by_id[item.element_id]
                tree_item.setBackground(0, QBrush(QColor(Colors.alternate_base)))
                # Supprimer le masque associé
                if item.mask_item and item.mask_item.scene():
                    item.mask_item.scene().removeItem(item.mask_item)
                    item.mask_item = None
                # Supprimer le duplicata de la scène
                if item.scene():
                    item.scene().removeItem(item)

        # 2️⃣ Nettoyer les références dans les dictionnaires
        image_path = next(
            (
                p
                for p, w in self._window.image_layer_widgets.items()
                if w == image_layer_widget
            ),
            None,
        )
        if image_path:
            self._window.image_layer_widgets.pop(image_path, None)
        current_index = self.parent().currentIndex()
        # 3️⃣ Supprimer l’onglet et le widget
        self._window.tabs.removeTab(index)
        frame.deleteLater()
        self.close_buttons.pop(index, None)
        self._window.tabs.blockSignals(False)

        if index == current_index:
            self._window.on_tab_changed(0)

    def set_tab_color(self, index, color):
        self._tab_colors[index] = color
        self.update()

    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index == self.count() - 1:
            # 📌 Clic sur l'onglet +
            self.on_plus_tab_clicked()
            return  # Empêche la sélection classique
        super().mousePressEvent(event)

    def on_plus_tab_clicked(self):
        """Action quand on clique sur le +"""
        dialog = QFileDialog(self, "Select image to use as cutting layer")
        dialog.setFileMode(
            QFileDialog.ExistingFiles
        )  # Permet de sélectionner plusieurs fichiers
        dialog.setNameFilter("Images (*.png *.jpg *.bmp *.pdf)")

        if dialog.exec_() == QDialog.Accepted:
            files = dialog.selectedFiles()

            # ⚡ Filtrer les fichiers déjà ouverts
            files_to_open = [
                f for f in files if f not in CustomTabBar._window.image_layer_widgets
            ]

            if not files_to_open:
                QMessageBox.information(self, "Info", "File already open")
                return

            for f in files_to_open:
                CustomTabBar._window.load_image_layer(f)

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            rect = self.tabRect(index)
            color = QColor(self._tab_colors.get(index, Colors.plus_tab))

            # 🔹 Fond de l’onglet
            painter.save()
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 2))
            painter.drawRoundedRect(rect, 6, 6)
            painter.restore()

            # 🔹 Label
            self.style().drawControl(QStyle.CE_TabBarTabLabel, option, painter, self)
