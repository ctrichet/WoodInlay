# |===========================================================   .=<|||>=.   ==|#
# |                                                              |(:)|||||     |#
# |   utils/debug.py                                             !!!!!!|||
# |                                                         /||||||||||||/.:::::,
# |   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
# |                                                        ||||||/.::::::::::::::
# |   Created: 2025/09/21 14:32:45 ctrichet                 \|||/.::::::::::::::'
# |   Updated: 2025/09/21 14:32:45 ctrichet                      :::......
# |                                                              :::::(|):     |#
# |===========================================================   ':::::::'   ==|#

import inspect

DEBUG = True


def debug_log(message=""):
    """Affiche un message de debug avec nom de fonction et numéro de ligne."""
    if not DEBUG:
        return
    frame = inspect.currentframe().f_back
    lineno = frame.f_lineno
    funcname = frame.f_code.co_name
    print(f"[DEBUG] {funcname} (line {lineno}): {message}")
