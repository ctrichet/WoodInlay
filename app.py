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
