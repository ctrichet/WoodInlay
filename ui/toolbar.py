#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/toolbar.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 19:50:24 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize


class CollapsibleToolbar(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("CollapsibleToolbar")

        self.content_widget = QWidget()
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(2)

        capture_icon = QIcon("./icons/camera.svg")
        self.capture_btn = QPushButton()
        self.capture_btn.setIcon(capture_icon)
        self.capture_btn.setIconSize(QSize(24, 24))
        self.capture_btn.setFlat(True)
        layout.addWidget(self.capture_btn)

        export_icon = QIcon("./icons/export.svg")
        self.export_btn = QPushButton()
        self.export_btn.setIcon(export_icon)
        self.export_btn.setIconSize(QSize(24, 24))
        self.export_btn.setFlat(True)
        layout.addWidget(self.export_btn)

        duplicate_icon = QIcon("./icons/duplicate.svg")
        self.duplicate_btn = QPushButton()
        self.duplicate_btn.setIcon(duplicate_icon)
        self.duplicate_btn.setIconSize(QSize(24, 24))
        self.duplicate_btn.setFlat(True)
        layout.addWidget(self.duplicate_btn)

        nest_icon = QIcon("./icons/nest.svg")
        self.nest_btn = QPushButton()
        self.nest_btn.setIcon(nest_icon)
        self.nest_btn.setIconSize(QSize(24, 24))
        self.nest_btn.setFlat(True)
        layout.addWidget(self.nest_btn)

        zoom_in_icon = QIcon("./icons/zoom_in.svg")
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(zoom_in_icon)
        self.zoom_in_btn.setIconSize(QSize(24, 24))
        self.zoom_in_btn.setFlat(True)
        layout.addWidget(self.zoom_in_btn)

        zoom_out_icon = QIcon("./icons/zoom_out.svg")
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(zoom_out_icon)
        self.zoom_out_btn.setIconSize(QSize(24, 24))
        self.zoom_out_btn.setFlat(True)
        layout.addWidget(self.zoom_out_btn)

        handle_icon = QIcon("./icons/handle.svg")
        self.toggle_btn = QToolButton()
        self.toggle_btn.setIcon(handle_icon)
        self.toggle_btn.setFixedWidth(10)
        self.toggle_btn.setStyleSheet("padding: 0; margin: 0;")
        self.toggle_btn.clicked.connect(self.toggle_collapsed)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.content_widget)
        main_layout.addWidget(self.toggle_btn)
        self.setLayout(main_layout)

        self.collapsed = True
        self.update_ui()

    def toggle_collapsed(self):
        self.collapsed = not self.collapsed
        self.update_ui()

    def update_ui(self):
        self.content_widget.setVisible(not self.collapsed)
        self.toggle_btn.setText("⯇" if not self.collapsed else "⯈")
