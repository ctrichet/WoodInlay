#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/delegates.py                                            !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from PyQt5.QtWidgets import (
    QStyledItemDelegate, QStyleOptionViewItem, QStyle
)
from PyQt5.QtCore import Qt

class ColorBackgroundDelegate(QStyledItemDelegate):
    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors  # liste de QColor, indexées comme les items du QComboBox

    def paint(self, painter, option, index):
        color = self.colors[index.row()]
        if option.state & QStyle.State_Selected:
            # Appliquer une bordure blanche sans masquer la couleur
            painter.save()
            painter.fillRect(option.rect, color)
            pen = painter.pen()
            pen.setWidth(2)
            pen.setColor(Qt.white)
            painter.setPen(pen)
            painter.drawRect(option.rect.adjusted(1, 1, -2, -2))
            painter.restore()
        else:
            painter.fillRect(option.rect, color)
        # Afficher le texte par-dessus
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        return super().sizeHint(option, index)


class TreeItemHighlightDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Copie de l'option mais sans l'état "Selected" pour empêcher le fond bleu
        custom_option = QStyleOptionViewItem(option)
        custom_option.state &= ~QStyle.State_Selected

        # Dessine le fond de l’item sans le surlignage de Qt
        super().paint(painter, custom_option, index)