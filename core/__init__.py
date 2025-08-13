#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   core/__init__.py                                           !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from .nesting import Individual, NestingEngine, approximate_polygon
from .model_items import PathItem, CompositeGroupItem, GroupItem, DuplicataGroupItem
from .svg_parser import parse_svg_or_group
from .duplication_manager import perform_unique_duplication
__all__ = [
    "Individual",
    "NestingEngine",
    "approximate_polygon",
    "PathItem",
    "CompositeGroupItem",
    "GroupItem",
    "DuplicataGroupItem",
    "perform_unique_duplication",
]
