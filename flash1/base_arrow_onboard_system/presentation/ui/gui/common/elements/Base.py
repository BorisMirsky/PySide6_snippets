# This Python file uses the following encoding: utf-8
from domain.units.AbstractUnit import AbstractReadUnit
from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

class FloatUnitIndicator(QWidget):
    def __init__(self, title: str, unit: AbstractReadUnit[float], precision: int = 1, parent: QWidget = None):
        super().__init__(parent)
        self.__unit: AbstractReadUnit[float] = unit
        self.__precision: int = precision
        #========================================================
        name_label_style = '''font-weight: bold;font-size: 14px;'''
        info_label_style = '''font-weight: bold;font-size: 14px;color: yellow;background-color: black;'''
        #========================================================
        self.__title_label = QLabel(title)
        self.__title_label.setProperty("infoPanelLabel", True)
        self.__value_label = QLabel('---')
        self.__value_label.setProperty("infoPanelValueBlueWhite", True)
        # self.__title_label.setStyleSheet(name_label_style)
        # self.__value_label.setStyleSheet(info_label_style)
        self.__value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.__value_label.setMinimumWidth(80)
        self.__value_label.setMargin(5)
        #========================================================
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.__title_label, 0)
        layout.addWidget(self.__value_label, 1)
        #========================================================
        self.__unit.changed.connect(self.__unit_changed)
        self.__unit_changed(self.__unit.read())

    def __unit_changed(self, value: float) ->None:
        result = '{:.1f}'.format(round(value, 1))           
        self.__value_label.setNum(float(result))

class StringLabel(QWidget):
    def __init__(self, title: str, value: str, parent: QWidget = None):
        super().__init__(parent)
        #========================================================
        #name_label_style = '''font-weight: bold;font-size: 14px;'''
        #info_label_style = '''font-weight: bold;font-size: 14px;color: yellow;background-color: black;'''
        #========================================================
        value = "     " + value + "     "
        self.__title_label = QLabel(title)
        self.__title_label.setProperty("infoPanelLabel", True)
        self.__value_label = QLabel(value)
        self.__value_label.setProperty("infoPanelValueBlueWhite", True)
        #self.__value_label.setContentsMargins(20,5,20,5)
        # self.__title_label.setStyleSheet(name_label_style)
        # self.__value_label.setStyleSheet(info_label_style)
        self.__value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__title_label.setFrameShadow(QLabel.Shadow.Raised)
        self.__title_label.setProperty("infoPanelLabel", True)
        self.__value_label.setFrameShape(QLabel.Shape.StyledPanel)
        self.__value_label.setProperty("infoPanelValueBlueWhite", True)
        #========================================================
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.__title_label, 0)
        layout.addWidget(self.__value_label, 1)

    def setTitle(self, title: str) ->str:
        return self.__title_label.setText(title)
    def title(self) ->str:
        return self.__title_label.text()

    def setText(self, text: str) ->str:
        return self.__value_label.setText(text)
    def text(self) ->str:
        return self.__value_label.text()

