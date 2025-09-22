#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/dialogs.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 18:38:20 githubactions                 :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/dialogs.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 16:34:59 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/dialogs.py                                              !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 16:29:06 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#

import os
from pathlib import Path
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QDialogButtonBox,
    QCheckBox,
)

from core.nesting_manager import NestingManager
from .delegates import ColorBackgroundDelegate
from styles.colors import Colors

from utils.debug import debug_log


import json
import os
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QDialogButtonBox,
)


class NestingConfigDialog(QDialog):
    _CONFIG_FILE = (
        Path(__file__).resolve().parent.parent / "config" / "nesting_config.json"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nesting Configuration")
        layout = QVBoxLayout()

        # Charger la config existante
        self.config = self.load_config()

        # Espacement entre pièces
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0, 100)
        self.spacing_spin.setValue(self.config.get("spacing", 2.0))
        self.spacing_spin.setSuffix(" mm")
        layout.addWidget(QLabel("Spacing between shapes :"))
        layout.addWidget(self.spacing_spin)

        # Marges (bin border)
        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setRange(0, 100)
        self.margin_spin.setValue(self.config.get("margin", 5.0))
        self.margin_spin.setSuffix(" mm")
        layout.addWidget(QLabel("Bin margins :"))
        layout.addWidget(self.margin_spin)

        # Rotation step
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 180)
        self.rotation_spin.setValue(self.config.get("rotation_step", 15))
        self.rotation_spin.setSuffix(" °")
        layout.addWidget(QLabel("Rotation step :"))
        layout.addWidget(self.rotation_spin)

        # Translation maximum
        self.translation_spin = QSpinBox()
        self.translation_spin.setRange(1, 10)
        self.translation_spin.setValue(self.config.get("max_translation_step", 3))
        layout.addWidget(QLabel("Maximum translation step :"))
        layout.addWidget(self.translation_spin)

        # Population size
        self.population_spin = QSpinBox()
        self.population_spin.setRange(1, 1000)
        self.population_spin.setValue(self.config.get("population_size", 30))
        layout.addWidget(QLabel("Population size :"))
        layout.addWidget(self.population_spin)

        # Type d’optimisation
        self.optimization_combo = QComboBox()
        self.optimization_combo.addItems(NestingManager._fitness_methods)
        layout.addWidget(QLabel("Optimization method :"))
        layout.addWidget(self.optimization_combo)

        # Coefficient pour fitness (affiché seulement si quadratic)
        self.fitness_coeff_spin = QDoubleSpinBox()
        self.fitness_coeff_spin.setRange(0, 1)
        self.fitness_coeff_spin.setValue(
            self.config.get("quadratic_fitness_coeff", 0.5)
        )
        self.fitness_coeff_label = QLabel("Quadratic fitness coefficient :")
        layout.addWidget(self.fitness_coeff_label)
        layout.addWidget(self.fitness_coeff_spin)

        # Approximation des formes
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(0, 2)
        self.tolerance_spin.setValue(self.config.get("tolerance", 0.5))
        self.tolerance_spin.setSuffix(" px, mm TODO")
        layout.addWidget(QLabel("Shape approximation tolerance :"))
        layout.addWidget(self.tolerance_spin)

        # Autoriser le miroir
        self.mirror_check = QCheckBox("Allow mirroring")
        self.mirror_check.setChecked(self.config.get("allow_mirror", False))
        layout.addWidget(self.mirror_check)

        # Checkbox pour sauvegarder les valeurs
        self.save_check = QCheckBox("Save these values as defaults")
        self.save_check.setChecked(True)
        layout.addWidget(self.save_check)

        # Boutons OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # Gestion de la visibilité du coefficient
        self.optimization_combo.currentTextChanged.connect(
            self.update_fitness_coeff_visibility
        )
        self.update_fitness_coeff_visibility(self.optimization_combo.currentText())

    def update_fitness_coeff_visibility(self, text: str):
        """Affiche ou masque la spinbox en fonction de la méthode choisie."""
        if text.lower().startswith("quadratic"):
            self.fitness_coeff_label.show()
            self.fitness_coeff_spin.show()
        else:
            self.fitness_coeff_label.hide()
            self.fitness_coeff_spin.hide()

    def load_config(self):
        if os.path.exists(self._CONFIG_FILE):
            with open(self._CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_and_accept(self):
        if self.save_check.isChecked():
            config = {
                "spacing": self.spacing_spin.value(),
                "margin": self.margin_spin.value(),
                "rotation_step": self.rotation_spin.value(),
                "max_translation_step": self.translation_spin.value(),
                "population_size": self.population_spin.value(),
                "optimization_method": self.optimization_combo.currentText(),
                "quadratic_fitness_coeff": self.fitness_coeff_spin.value(),
                "tolerance": self.tolerance_spin.value(),
                "allow_mirror": self.mirror_check.isChecked(),
            }
            with open(self._CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        self.accept()

    def set_config(self, nesting_manager):
        nesting_manager.spacing = self.spacing_spin.value()
        nesting_manager.bin_margin = self.margin_spin.value()
        nesting_manager.mutation_rotation = self.rotation_spin.value()
        nesting_manager.population_size = self.population_spin.value()
        nesting_manager.mutation_translation = self.translation_spin.value()
        fitness_method = self.optimization_combo.currentText()
        nesting_manager.fitness_method = fitness_method
        if "quadratic" in fitness_method:
            nesting_manager.quadratic_fitness_coeff = self.fitness_coeff_spin.value()
        nesting_manager.tolerance = self.tolerance_spin.value()
        nesting_manager.allow_mirror = self.mirror_check.isChecked()


class BackgroundSelectionDialog(QDialog):
    def __init__(self, image_layer_widgets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select target layer")
        self.setMinimumWidth(300)
        self.selected_name = None

        layout = QVBoxLayout(self)

        self.combo = QComboBox(self)
        self.combo.setStyleSheet(
            """
            QComboBox QAbstractItemView::item:hover {
                background: transparent;
            }
            QComboBox QAbstractItemView::item:selected {
                background: transparent;
                color: black;  /* ou la couleur de ton texte normal */
            }
        """
        )

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
        palette.setColor(QPalette.Highlight, current_color)

        self.combo.setPalette(palette)

        # Appliquer le délégué personnalisé pour la coloration de fond
        delegate = ColorBackgroundDelegate(self.layer_colors, self.combo)
        self.combo.setItemDelegate(delegate)

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
        palette.setColor(QPalette.Highlight, color)
        self.combo.setPalette(palette)
