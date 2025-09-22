#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   utils/__init__.py                                          !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 18:30:47 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
from .debug import debug_log, DEBUG
from .geometry import rotate_vector

__all__ = [
    "debug_log",
    "DEBUG",
    "rotate_vector",
]
