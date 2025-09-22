#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   app.py                                                     !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 18:38:20 githubactions                 :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   app.py                                                     !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 16:34:59 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   app.py                                                     !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 16:29:06 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.tab_bar import CustomTabBar
from styles.colors import styleSheet

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Windows")
    app.setStyleSheet(styleSheet())
    window = MainWindow()
    CustomTabBar._window = window
    window.show()

    sys.exit(app.exec_())
