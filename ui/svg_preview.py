#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/svg_preview.py                                          !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 17:24:08 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
from PyQt5.QtWidgets import QDockWidget, QWidget, QToolButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from ui.svg_layer import SvgLayerWidget


class PreviewDock(QDockWidget):
    def __init__(self, title: str, parent=None, layer_getter=None):
        super().__init__(title, parent)
        self.layer_getter = layer_getter
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
        )

        # Crée une titlebar custom
        titlebar = QWidget()
        layout = QHBoxLayout(titlebar)
        layout.setContentsMargins(2, 2, 2, 2)

        self.title_label = QLabel(title)
        layout.addWidget(self.title_label)

        layout.addStretch()  # <-- pousse les widgets suivants à droite

        self.float_button = QToolButton()
        self.float_button.setText("⇱")  # icône ou symbole pour float
        self.float_button.clicked.connect(self.on_float_button_clicked)
        layout.addWidget(self.float_button)

        titlebar.setLayout(layout)
        self.setTitleBarWidget(titlebar)

        # Connecter le signal topLevelChanged
        self.topLevelChanged.connect(self.on_top_level_changed)
        self.update_fit()

    def on_float_button_clicked(self):
        self.setFloating(not self.isFloating())

    def on_top_level_changed(self, floating: bool):
        """Dock détaché ou rattaché"""
        if not floating:
            # Rattaché
            if self.layer_getter and isinstance(self.layer_getter(), SvgLayerWidget):
                self.hide()
        self.update_fit()

    def resizeEvent(self, event):
        """Redimensionnement du dock"""
        self.update_fit()
        super().resizeEvent(event)

    def update_fit(self):
        view = self.widget()
        if view and view.scene():
            view.fitInView(view.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
