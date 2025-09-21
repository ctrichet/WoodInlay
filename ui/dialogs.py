#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/dialogs.py                                              !!!!!!||| 
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/21 13:23:55 ctrichet             \|||/.::::::::::::::'
#|   Updated: 2025/09/21 13:23:55 ctrichet                  :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#


#############################################################   .=<|||>=.   ####
# |                                                              |(0)|||||      #
# |   ui/dialogs.py                                              !!!!!!|||
# |                                                         /||||||||||||/.:::::,
# |   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
# |                                                        ||||||/.::::::::::::::
# |   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
# |   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
# |                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import os
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QListView,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QTreeView,
    QLineEdit,
    QMessageBox,
    QCheckBox,
)
from PyQt5.QtGui import QPalette
from .delegates import ColorBackgroundDelegate


class NestingConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nesting Configuration")

        layout = QVBoxLayout()

        # Espacement entre pièces
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0, 100)
        self.spacing_spin.setValue(2.0)
        self.spacing_spin.setSuffix(" mm")
        layout.addWidget(QLabel("Espacement entre pièces :"))
        layout.addWidget(self.spacing_spin)

        # Marges (bin border)
        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setRange(0, 100)
        self.margin_spin.setValue(5.0)
        self.margin_spin.setSuffix(" mm")
        layout.addWidget(QLabel("Marge avec le bord du bin :"))
        layout.addWidget(self.margin_spin)

        # Rotations autorisées
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(
            ["Pas de rotation", "90°", "180°", "Libre (15° pas)", "Libre (5° pas)"]
        )
        layout.addWidget(QLabel("Rotations autorisées :"))
        layout.addWidget(self.rotation_combo)

        # Population size
        self.population_spin = QSpinBox()
        self.population_spin.setRange(1, 1000)
        self.population_spin.setValue(20)
        layout.addWidget(QLabel("Taille de la population :"))
        layout.addWidget(self.population_spin)

        # Mutation rate
        self.mutation_spin = QDoubleSpinBox()
        self.mutation_spin.setRange(0.0, 1.0)
        self.mutation_spin.setSingleStep(0.05)
        self.mutation_spin.setValue(0.1)
        layout.addWidget(QLabel("Taux de mutation :"))
        layout.addWidget(self.mutation_spin)

        # Type d’optimisation
        self.optimization_combo = QComboBox()
        self.optimization_combo.addItems(["Gravity (compact)", "Bounding box"])
        layout.addWidget(QLabel("Type d’optimisation :"))
        layout.addWidget(self.optimization_combo)

        # Approximation des formes
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(0, 10)
        self.tolerance_spin.setValue(0.5)
        self.tolerance_spin.setSuffix(" px")
        layout.addWidget(QLabel("Tolérance d’approximation des formes :"))
        layout.addWidget(self.tolerance_spin)

        # Autoriser le miroir
        self.mirror_check = QCheckBox("Autoriser les symétries (flip/mirror)")
        layout.addWidget(self.mirror_check)

        # Boutons OK / Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_config(self):
        return {
            "spacing": self.spacing_spin.value(),
            "margin": self.margin_spin.value(),
            "rotation": self.rotation_combo.currentText(),
            "population": self.population_spin.value(),
            "mutation": self.mutation_spin.value(),
            "optimization": self.optimization_combo.currentText(),
            "tolerance": self.tolerance_spin.value(),
            "allow_mirror": self.mirror_check.isChecked(),
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
        palette.setColor(QPalette.Button, current_color)
        self.combo.setPalette(palette)

        # Appliquer le délégué personnalisé pour la coloration de fond
        delegate = ColorBackgroundDelegate(self.layer_colors, self.combo)
        self.combo.setItemDelegate(delegate)

        layout.addWidget(QLabel("Calque :", self))
        layout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.update_combo_color)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
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
