#############################################################   .=<|||>=.   ####
#|                                                              |(0)|||||      #
#|   app.py                                                     !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/08/12 11:43:00 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/08/12 11:43:00 ctrichet                      :::......
#|                                                              :::::(0):      #
#############################################################   ':::::::'   ####

import sys
from PyQt5.QtWidgets import QApplication
from woodinlay import WoodInlayManager
from ui.main_window import MainWindow
from ui.tab_bar import CustomTabBar

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = WoodInlayManager()
    window = MainWindow(manager)

    manager.window = window
    CustomTabBar._window = window
    manager.parse_svg_or_group()
    window.show()

    sys.exit(app.exec_())