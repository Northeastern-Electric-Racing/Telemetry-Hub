from enum import Enum

from PyQt6.QtWidgets import QPushButton


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
