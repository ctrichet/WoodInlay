#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   utils/__init__.py                                          !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from .debug import debug_log, DEBUG
from .geometry import rotate_vector

__all__ = [
    "debug_log",
    "DEBUG",
    "rotate_vector",
]
