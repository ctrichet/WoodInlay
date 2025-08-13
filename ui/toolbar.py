#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/toolbar.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class CollapsibleToolbar(QWidget):
    def __init__(self, zoom_in_func, zoom_out_func):
        super().__init__()
        self.zoom_in_func = zoom_in_func
        self.zoom_out_func = zoom_out_func

        self.content_widget = QWidget()
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        duplicate_icon = QIcon("../../icons/duplicate.svg")
        self.duplicate_btn = QPushButton()
        self.duplicate_btn.setIcon(duplicate_icon)
        self.duplicate_btn.setIconSize(QSize(24, 24))
        self.duplicate_btn.setFlat(True)
        layout.addWidget(self.duplicate_btn)

        zoom_in_icon = QIcon("../../icons/zoom_in.svg")
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(zoom_in_icon)
        self.zoom_in_btn.setIconSize(QSize(24, 24))
        self.zoom_in_btn.setFlat(True)
        layout.addWidget(self.zoom_in_btn)

        zoom_out_icon = QIcon("../../icons/zoom_out.svg")
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(zoom_out_icon)
        self.zoom_out_btn.setIconSize(QSize(24, 24))
        self.zoom_out_btn.setFlat(True)
        layout.addWidget(self.zoom_out_btn)

        self.toggle_btn = QPushButton("⯈")
        self.toggle_btn.setFixedWidth(20)
        self.toggle_btn.clicked.connect(self.toggle_collapsed)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.content_widget)
        main_layout.addWidget(self.toggle_btn)
        self.setLayout(main_layout)

        self.collapsed = True
        self.update_ui()

        self.zoom_in_btn.clicked.connect(self.zoom_in_func)
        self.zoom_out_btn.clicked.connect(self.zoom_out_func)

    def toggle_collapsed(self):
        self.collapsed = not self.collapsed
        self.update_ui()

    def update_ui(self):
        self.content_widget.setVisible(not self.collapsed)
        self.toggle_btn.setText("⯇" if not self.collapsed else "⯈")
