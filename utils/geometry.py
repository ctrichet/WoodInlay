#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   utils/geometry.py                                          !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

from PyQt5.QtCore import QPointF
from math import radians, cos, sin

def rotate_vector(vec: QPointF, angle_degrees: float) -> QPointF:
    """Rotation d'un vecteur QPointF autour de l'origine."""
    angle_rad = radians(angle_degrees)
    x = vec.x() * cos(angle_rad) - vec.y() * sin(angle_rad)
    y = vec.x() * sin(angle_rad) + vec.y() * cos(angle_rad)
    return QPointF(x, y)
