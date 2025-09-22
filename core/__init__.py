#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   core/__init__.py                                           !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 17:09:42 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
# |===========================================================   .=<|||>=.   ==|#
# |                                                              |(:)|||||     |#
# |   core/__init__.py                                           !!!!!!|||
# |                                                         /||||||||||||/.:::::,
# |   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
# |                                                        ||||||/.::::::::::::::
# |   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
# |   Updated: 2025/09/22 16:46:58 ctrichet                      :::......
# |                                                              :::::(|):     |#
# |===========================================================   ':::::::'   ==|#
# |===========================================================   .=<|||>=.   ==|#
# |                                                              |(:)|||||     |#
# |   core/__init__.py                                           !!!!!!|||
# |                                                         /||||||||||||/.:::::,
# |   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
# |                                                        ||||||/.::::::::::::::
# |   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
# |   Updated: 2025/09/22 16:34:59 ctrichet                      :::......
# |                                                              :::::(|):     |#
# |===========================================================   ':::::::'   ==|#
# |===========================================================   .=<|||>=.   ==|#
# |                                                              |(:)|||||     |#
# |   core/__init__.py                                           !!!!!!|||
# |                                                         /||||||||||||/.:::::,
# |   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
# |                                                        ||||||/.::::::::::::::
# |   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
# |   Updated: 2025/09/22 16:29:06 ctrichet                      :::......
# |                                                              :::::(|):     |#
# |===========================================================   ':::::::'   ==|#

from .nesting_manager import NestingManager
from .model_items import PathItem, CompositeGroupItem, GroupItem, DuplicataGroupItem
from .duplication_manager import perform_unique_duplication
from .nesting_manager import NestingManager, NestingWorker

__all__ = [
    "PathItem",
    "CompositeGroupItem",
    "GroupItem",
    "DuplicataGroupItem",
    "perform_unique_duplication",
    "NestingManager",
    "NestingWorker",
]
