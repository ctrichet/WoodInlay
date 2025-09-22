#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   styles/colors.py                                           !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/22 16:07:05 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/22 16:07:05 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#

from abc import ABC, abstractmethod


class Colors(ABC):
    header = "#232323"
    base = "#202020"
    alternate_base = "#363636"
    highlight = "#3399FF"
    highlighted_text = "#FFFFFF"
    text = "#FFFFFF"
    outline = "#000000"
    preselection = "#800080"
    plus_tab = "#BEBEBE"
    svg_frame = "#303030"

    separation = "#404040"
    button_hover = "#005A9E"
    button_pressed = "#003F6B"
    tab_hover = "#007ACC"
    dock_title = "#FFFFFF"
    tooltip_bg = "#2E2E2E"
    tooltip_text = "#FFFFFF"

    @abstractmethod
    def __init__(self):
        pass


def styleSheet():
    return f"""
    /* ==================== FOND PRINCIPAL ==================== */
    QMainWindow {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
    }}

    QWidget {{
        background-color: {Colors.base};
        color: {Colors.text};
    }}

    QDialog {{
        background-color: {Colors.base};
        color: {Colors.text};
    }}

    /* ==================== QTabWidget / QTabBar ==================== */
    QTabWidget::pane {{
        background-color: {Colors.base};

    }}
    QTabBar::tab {{
        background-color: {Colors.base};
        color: {Colors.text};
        padding: 5px;
    }}
    QTabBar::tab:selected {{
        background-color: {Colors.highlight};
        color: {Colors.highlighted_text};
    }}
    QTabBar::tab:hover {{
        background-color: {Colors.tab_hover};
    }}
    QTabBar::tab:!selected {{
        margin-top: 2px;
    }}

    /* ==================== QDockWidget ==================== */
    QDockWidget {{
        background-color: {Colors.base};
        titlebar-close-icon: url(none);
        titlebar-normal-icon: url(none);
    }}
    QDockWidget::title {{
        background-color: {Colors.alternate_base};
        color: {Colors.dock_title};
        padding: 3px;
    }}

    /* ==================== QGraphicsView / QGraphicsScene ==================== */
    QGraphicsView {{
        background-color: {Colors.alternate_base};
        border: none;
    }}
    QGraphicsScene {{
        background-color: {Colors.alternate_base};
    }}

    /* ==================== QTreeWidget / QAbstractItemView ==================== */
    QTreeWidget, QAbstractItemView {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
        alternate-background-color: {Colors.base};
        selection-background-color: {Colors.highlight};
        selection-color: {Colors.highlighted_text};
    }}
    QTreeWidget::item {{
        border-bottom: 1px solid {Colors.separation};
        padding: 0px;
    }}
    QTreeWidget::item:hover {{
        background-color: {Colors.preselection};
        color: {Colors.highlighted_text};
    }}
    QTreeWidget::item:selected {{
        background-color: {Colors.highlight};
        color: {Colors.highlighted_text};
    }}
    QHeaderView::section {{
        background-color: {Colors.base};
        color: {Colors.text};
        border: none;
        padding: 4px;
    }}

    /* ==================== Scrollbars ==================== */
    QScrollBar:vertical {{
        background-color: {Colors.alternate_base};
        border: none;
    }}
    QScrollBar:horizontal {{
        background-color: {Colors.alternate_base};
        border: none;
    }}
    QScrollBar::groove:vertical {{
        background-color: {Colors.alternate_base};
        border: none;
    }}
    QScrollBar::groove:horizontal {{
        background-color: {Colors.alternate_base};
        border: none;
    }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background-color: {Colors.base};
        border-radius: 8px;
        border: 1px solid {Colors.alternate_base};
        min-height: 8px;
        min-width: 8px;
    }}
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
        background-color: {Colors.highlight};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        background: none;
        height: 0;
        width: 0;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    /* ==================== QPushButton / QToolButton ==================== */
    QPushButton, QToolButton {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
        border: 0px solid {Colors.outline};
        border-radius: 6px;
        padding: 4px 4px;
    }}
    QPushButton:hover, QToolButton:hover {{
        background-color: {Colors.button_hover};
    }}
    QPushButton:pressed, QToolButton:pressed {{
        background-color: {Colors.button_pressed};
    }}
    QToolButton#close_btn {{
        background-color: transparent;
        border-radius: 6px;
        padding: 2px;
    }}

    /* ==================== Tooltip ==================== */
    QToolTip {{
        background-color: {Colors.tooltip_bg};
        color: {Colors.tooltip_text};
        border: 0px solid {Colors.highlight};
    }}

    /* ==================== QFileDialog ==================== */

    /* Barre d'adresse */
    QFileDialog QLineEdit {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
        border: 0px solid {Colors.outline};
        border-radius: 4px;
        padding: 2px 4px;
    }}

    /* Champ de saisie du nom de fichier */
    QFileDialog QWidget#fileNameEdit QLineEdit {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
        border: 0px solid {Colors.outline};
        border-radius: 4px;
        padding: 2px 4px;
    }}

    /* ComboBox des types de fichiers supportés */
    QFileDialog QComboBox {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
        border: 0px solid {Colors.outline};
        border-radius: 4px;
        padding: 2px 4px;
    }}
    QFileDialog QComboBox::drop-down {{
        border: none;
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
    }}
    QFileDialog QComboBox QAbstractItemView {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
        selection-background-color: {Colors.highlight};
        selection-color: {Colors.highlighted_text};
    }}

    QFileDialog QToolButton {{
        background-color: {Colors.alternate_base};
        border: 0px solid {Colors.outline};
        border-radius: 4px;
        padding: 0;
        margin: 0;
        qproperty-iconSize: 24px 24px;
    }}

    QFileDialog QToolButton:hover {{
        background-color: {Colors.button_hover};
    }}

    QFileDialog QToolButton:pressed {{
        background-color: {Colors.button_pressed};
    }}

    QFileDialog QToolButton::menu-indicator {{
        subcontrol-origin: padding;
        subcontrol-position: center;
    }}
    QFileDialog QListView::item,
    QFileDialog QTreeView::item {{
        border-bottom: 1px solid {Colors.separation};
        padding: 0px;
    }}
    QFileDialog QAbstractItemView {{
        background-color: {Colors.alternate_base};
        border: none;
        alternate-background-color: {Colors.base};
        selection-background-color: {Colors.highlight};
        selection-color: {Colors.highlighted_text};
    }}
    QFileDialog QListView::item:selected,
    QFileDialog QTreeView::item:selected {{
        background-color: {Colors.highlight};
        color: {Colors.highlighted_text};
    }}
    QFileDialog QHeaderView::section {{
        background-color: {Colors.alternate_base};
        color: {Colors.text};
        border: 1px solid {Colors.base};
        font-weight: bold;
        padding: 4px;
        min-height: 40px
    }}
    QHeaderView::section:checked::up-arrow,
    QHeaderView::section:checked::down-arrow {{
        width: 12px;
        height: 12px;
    }}
    """
