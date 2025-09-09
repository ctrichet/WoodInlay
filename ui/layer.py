from PyQt5.QtWidgets import (
    QWidget, QGraphicsScene, QTreeWidget,
)
from PyQt5.QtGui import QPainter
from ui.views import ZoomableView

class LayerWidget(QWidget):
    """Classe mère pour SvgLayerWidget et ImageLayerWidget."""
    def __init__(self, tree_header="Éléments"):
        super().__init__()
        self.tree_items_by_id = {}
        self.items_by_id = {}

        # TreeWidget associé au layer
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([tree_header])
        self.tree.setMinimumWidth(200)
        # On laisse le choix du delegate à la sous-classe
        self.tree_delegate_set = False

        # Scene et vue
        self.scene = QGraphicsScene()
        self.view = ZoomableView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
