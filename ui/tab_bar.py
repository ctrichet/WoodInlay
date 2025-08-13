#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/tab_bar.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from PyQt5.QtWidgets import (
    QTabBar, QStyleOptionTab, QStyle, QFileDialog, QDialog
)
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import QSize

from ui.dialogs import DarkFileDialog

from utils.debug import debug_log

class CustomTabBar(QTabBar):
    _window = None
    _min_width = 35
    _max_width = 150

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tab_colors = {}
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
        tab_width = max(CustomTabBar._min_width, min(CustomTabBar._max_width, tab_width))

        if index == count - 1:  # onglet "+"
            tab_width = CustomTabBar._min_width

        return QSize(int(tab_width), size.height())

    def add_plus_tab(self):
        """Ajoute l'onglet spécial + à la fin."""
        self.addTab("+")
        self.set_tab_color(self.count() - 1, QColor("#CCCCCC"))

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
        dialog = DarkFileDialog(self, "Charger un ou plusieurs calques de fond")
        dialog.setFileMode(QFileDialog.ExistingFiles)  # Permet de sélectionner plusieurs fichiers
        dialog.setNameFilter("Images (*.png *.jpg *.bmp *.pdf)")

        if dialog.exec_() == QDialog.Accepted:
            files = dialog.selectedFiles()
            for f in files:
                CustomTabBar._window.load_image_layer(f)

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            rect = self.tabRect(index)
            color = self._tab_colors.get(index, QColor("gray"))

            # 🔹 Fond de l’onglet
            painter.save()
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 2))
            painter.drawRoundedRect(rect, 6, 6)
            painter.restore()

            # 🔹 Label
            self.style().drawControl(QStyle.CE_TabBarTabLabel, option, painter, self)
