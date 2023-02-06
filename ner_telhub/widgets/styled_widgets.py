from enum import Enum
import os

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout, QPushButton, QSizePolicy, 
    QToolBar, QWidget
)

resources = os.path.dirname(__file__) + "/../../resources"

class NERButton(QPushButton):
    """
    Creates a button using a provided preset button style
    """
    class Styles(Enum):
        """
        Defines the styles of buttons. When hovering over them, they turn two shades brighter.
        Lighter shades found with https://www.w3schools.com/colors/colors_picker.asp
        """
        DEFAULT = ""
        RED = """QPushButton {color: white; background-color: #FF5656; border-radius: 4px; padding: 3% 8%;}
            QPushButton:hover {background-color: #ff8080; color: white;}
            QPushButton::pressed {background-color : #fc9f9f; color: white;}"""
        GREEN = """QPushButton {color: white; background-color: #1a8f35; border-radius: 4px; padding: 3% 8%;}
            QPushButton:hover {background-color: #20ac40; color: white;}
            QPushButton::pressed {background-color : #67ab76;}"""
        BLUE = """QPushButton {color: white; background-color: #0693E3; border-radius: 4px; padding: 3% 8%;}
            QPushButton:hover {background-color: #1fa9f9; color: white;}
            QPushButton::pressed {background-color : #7dccfa;}"""
        GRAY = """QPushButton {color: white; background-color: #999999; border-radius: 4px; padding: 3% 8%;}
            QPushButton:hover {background-color: #b3b3b3; color: white;}
            QPushButton::pressed {background-color : #c4c4c4;}"""

    def __init__(self, title: str, style=Styles.DEFAULT):
        super().__init__(title)
        self.style = style
        self.setStyleSheet(style.value)

    def addStyle(self, params: str):
        """
        Adds style parameters only to the button's preset style
        Parameters must be a semicolon separated list of styles
        """
        self.setStyleSheet(self.style.value + "QPushButton {" + params + "}")

    def changeStyle(self, style: Styles):
        """
        Replaces button's style with the provided preset style
        """
        self.style = style
        self.setStyleSheet(style.value)


class NERImageButton(NERButton):
    """
    Creates a button using an icon.
    """
    class Icons(Enum):
        """
        Defines file names for available icons.
        """
        EDIT = "edit_icon.png"
        EXPORT = "export_icon.png"
        REFRESH = "refresh_icon.png"
        RESET = "reset_icon.png"
        START = "start_icon.png"
        STOP = "stop_icon.png"
        TRASH = "trash_icon.png"
        CLOSE = "close_icon.png"

    def __init__(self, icon_file: Icons, style=NERButton.Styles.DEFAULT):
        super().__init__("", style=style)
        self.resetIcon(icon_file)
    
    def resetIcon(self, icon_file: Icons):
        self.setIcon(QIcon(os.path.join(resources, icon_file.value)))

class NERToolbar(QToolBar):
    """
    Creates a Toolbar that supports adding Widgets to either side.
    """
    def __init__(self, parent = None):
        super(NERToolbar, self).__init__(parent)

        # Setup left side of toolbar
        left = QWidget()
        self.left_buttons = QHBoxLayout()
        left.setLayout(self.left_buttons)
        self.addWidget(left)

        # Setup middle spacer
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) 
        self.addWidget(self.spacer)

        # Setup right side of toolbar
        right = QWidget()
        self.right_buttons = QHBoxLayout()
        right.setLayout(self.right_buttons)
        self.addWidget(right)

    def addLeft(self, widget: QWidget):
        self.left_buttons.addWidget(widget)
    
    def addRight(self, widget: QWidget):
        self.right_buttons.addWidget(widget)
