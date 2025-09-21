#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   ui/__init__.py                                             !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/21 14:42:31 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/21 14:42:31 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#

# |===========================================================   .=<|||>=.   ==|#
# |                                                              |(:)|||||     |#
# |   ui/__init__.py                                             !!!!!!|||
# |                                                         /||||||||||||/.:::::,
# |   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
# |                                                        ||||||/.::::::::::::::
# |   Created: 2025/09/21 14:32:45 ctrichet                 \|||/.::::::::::::::'
# |   Updated: 2025/09/21 14:32:45 ctrichet                      :::......
# |                                                              :::::(|):     |#
# |===========================================================   ':::::::'   ==|#

from .main_window import MainWindow
from .svg_layer import SvgLayerWidget
from .image_layer import ImageLayerWidget
from .views import ImageView, SvgView
from .toolbar import CollapsibleToolbar
from .dialogs import (
    BackgroundSelectionDialog,
    NestingConfigDialog,
)
from .svg_preview import PreviewDock
from .tab_bar import CustomTabBar
from .delegates import ColorBackgroundDelegate
from .layer import LayerWidget

__all__ = [
    "MainWindow",
    "LayerWidget",
    "SvgLayerWidget",
    "ImageLayerWidget",
    "SvgView",
    "ImageView",
    "CollapsibleToolbar",
    "BackgroundSelectionDialog",
    "NestingConfigDialog",
    "CustomTabBar",
    "ColorBackgroundDelegate",
    "LayerWidget",
    "PreviewDock",
]
