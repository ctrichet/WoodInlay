#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   ui/dialogs.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QFileDialog, QListView,
    QDoubleSpinBox, QComboBox, QPushButton, QDialogButtonBox,QTreeView,
    QLineEdit, QMessageBox,
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from .delegates import ColorBackgroundDelegate

class NestingConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration du Nesting")
        layout = QVBoxLayout(self)

        # Espacement
        h_spacing = QHBoxLayout()
        h_spacing.addWidget(QLabel("Espacement (mm):"))
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0, 100)
        self.spacing_spin.setValue(2.0)
        h_spacing.addWidget(self.spacing_spin)
        layout.addLayout(h_spacing)

        # Marges
        h_margin = QHBoxLayout()
        h_margin.addWidget(QLabel("Marge (mm):"))
        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setRange(0, 100)
        self.margin_spin.setValue(10.0)
        h_margin.addWidget(self.margin_spin)
        layout.addLayout(h_margin)

        # Optimisation
        h_opt = QHBoxLayout()
        h_opt.addWidget(QLabel("Optimisation:"))
        self.optimization_combo = QComboBox()
        self.optimization_combo.addItems(["gravity", "bounding box"])
        h_opt.addWidget(self.optimization_combo)
        layout.addLayout(h_opt)

        # Rotation
        h_rot = QHBoxLayout()
        h_rot.addWidget(QLabel("Pas de rotation:"))
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(1, 360)
        self.rotation_spin.setValue(90)
        h_rot.addWidget(self.rotation_spin)
        layout.addLayout(h_rot)

        # Approximation
        h_approx = QHBoxLayout()
        h_approx.addWidget(QLabel("Approximation:"))
        self.approx_spin = QSpinBox()
        self.approx_spin.setRange(1, 100)
        self.approx_spin.setValue(10)
        h_approx.addWidget(self.approx_spin)
        layout.addLayout(h_approx)

        # Population
        h_pop = QHBoxLayout()
        h_pop.addWidget(QLabel("Population:"))
        self.population_spin = QSpinBox()
        self.population_spin.setRange(1, 1000)
        self.population_spin.setValue(100)
        h_pop.addWidget(self.population_spin)
        layout.addLayout(h_pop)

        # Mutation
        h_mut = QHBoxLayout()
        h_mut.addWidget(QLabel("Taux de mutation:"))
        self.mutation_spin = QDoubleSpinBox()
        self.mutation_spin.setRange(0, 1)
        self.mutation_spin.setSingleStep(0.05)
        self.mutation_spin.setValue(0.8)
        h_mut.addWidget(self.mutation_spin)
        layout.addLayout(h_mut)

        # Boutons
        btns = QHBoxLayout()
        ok_btn = QPushButton("Lancer")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def get_config(self):
        return {
            "spacing_mm": self.spacing_spin.value(),
            "margin_mm": self.margin_spin.value(),
            "optimization": self.optimization_combo.currentText(),
            "rotation_step": self.rotation_spin.value(),
            "rotations": list(range(0, 360, self.rotation_spin.value())),
            "approximation": self.approx_spin.value(),
            "population": self.population_spin.value(),
            "mutation_rate": self.mutation_spin.value()
        }


class BackgroundSelectionDialog(QDialog):
    def __init__(self, image_layer_widgets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choisir le calque cible")
        self.setMinimumWidth(300)
        self.selected_name = None

        layout = QVBoxLayout(self)

        self.combo = QComboBox(self)

        self.layer_colors = []

        for path, layer in image_layer_widgets.items():
            basename = os.path.basename(path)
            color = layer.margin_color
            self.combo.addItem(basename, userData=path)
            self.layer_colors.append(color)

        # Appliquer la couleur de fond à l'élément affiché dans la QComboBox
        current_color = self.layer_colors[0]  # ← correspond à la première couleur
        palette = self.combo.palette()
        palette.setColor(QPalette.Base, current_color)
        palette.setColor(QPalette.Button, current_color)  # parfois nécessaire selon le style Qt
        self.combo.setPalette(palette)

        # Appliquer le délégué personnalisé pour la coloration de fond
        delegate = ColorBackgroundDelegate(self.layer_colors, self.combo)
        self.combo.setItemDelegate(delegate)

        layout.addWidget(QLabel("Calque :", self))
        layout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.update_combo_color)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_layer_path(self):
        if self.exec_() == QDialog.Accepted:
            index = self.combo.currentIndex()
            return self.combo.itemData(index)
        return None


    def update_combo_color(self, index):
        color = self.layer_colors[index]
        palette = self.combo.palette()
        palette.setColor(QPalette.Base, color)
        palette.setColor(QPalette.Button, color)
        self.combo.setPalette(palette)

class DarkFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setOption(QFileDialog.DontUseNativeDialog, True)

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

        self.setStyleSheet("""
            QFileDialog {
                background-color: #353535;
                color: white;
            }
            QLineEdit, QComboBox {
                background-color: #232323;
                color: white;
            }
            QListView, QTreeView {
                background-color: #232323;
                color: white;
            }
            QPushButton {
                background-color: #454545;
                color: white;
                border: 1px solid #5A5A5A;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #3c3c3c;
                border: none;
                margin: 0px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #5A5A5A;
                border: none;
                min-height: 20px;
                min-width: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                border: none;
            }
        """)


        for view in self.findChildren((QTreeView, QListView)):
            view.setPalette(dark_palette)
            if isinstance(view, QTreeView):
                header = view.header()
                if header:
                    header.setStyleSheet("background-color: #353535; color: white;")
                    header.setPalette(dark_palette)

        # Appliquer aussi la palette aux QLineEdit et QComboBox (path + filter)
        for widget_type in (QLineEdit, QComboBox):
            for widget in self.findChildren(widget_type):
                widget.setPalette(dark_palette)

class DarkMessageBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Palette sombre
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

        # Style sombre optionnel pour affiner les boutons et textes
        self.setStyleSheet("""
            QMessageBox {
                background-color: #353535;
                color: white;
            }
            QPushButton {
                background-color: #454545;
                color: white;
                border: 1px solid #5A5A5A;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
        """)

    @classmethod
    def warning(cls, parent, title, text, buttons=QMessageBox.Ok):
        box = cls(QMessageBox.Warning, title, text, buttons, parent)
        return box.exec_()

    @classmethod
    def information(cls, parent, title, text, buttons=QMessageBox.Ok):
        box = cls(QMessageBox.Information, title, text, buttons, parent)
        return box.exec_()

    @classmethod
    def critical(cls, parent, title, text, buttons=QMessageBox.Ok):
        box = cls(QMessageBox.Critical, title, text, buttons, parent)
        return box.exec_()
