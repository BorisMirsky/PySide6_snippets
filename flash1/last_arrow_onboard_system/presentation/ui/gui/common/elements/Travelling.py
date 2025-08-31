# This Python file uses the following encoding: utf-8
from domain.dto.Travelling import BaseRail, MovingDirection, PicketDirection, RailPressType
from domain.units.AbstractUnit import AbstractReadUnit
from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import QCoreApplication, Qt
from .Base import FloatUnitIndicator, StringLabel


QCoreApplication.translate('Travelling/BaseRail', 'Left')
QCoreApplication.translate('Travelling/BaseRail', 'Right')
QCoreApplication.translate('Travelling/PicketDirection', 'Forward')
QCoreApplication.translate('Travelling/PicketDirection', 'Backward')
QCoreApplication.translate('Travelling/MovingDirection', 'Forward')
QCoreApplication.translate('Travelling/MovingDirection', 'Backward')



class BaseRailLabel(StringLabel):
    def __init__(self, rail: BaseRail, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Base rail:'), QCoreApplication.translate('Travelling/BaseRail', rail.name), parent)

class PressRailLabel(StringLabel):
    def __init__(self, rail: RailPressType, parent: QWidget = None):
        super().__init__('Прижим:', QCoreApplication.translate('Travelling/BaseRail', rail.name), parent)

class MovingDirectionLabel(StringLabel):
    def __init__(self, direction: MovingDirection, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Moving direction:'), QCoreApplication.translate('Travelling/MovingDirection', direction.name), parent)

class PicketDirectionLabel(StringLabel):
    def __init__(self, direction: PicketDirection, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Picket direction:'), QCoreApplication.translate('Travelling/PicketDirection', direction.name), parent)

class RailwayInfoPanel(StringLabel):
    def __init__(self, railway_name: str, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Railway name:'), railway_name, parent)


class PassedMetersLabel(FloatUnitIndicator):
    def __init__(self, unit: AbstractReadUnit[float], parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Passed meters:'), unit, 1, parent)

class CurrentPicketLabel(QWidget):
    def __init__(self, picket_position: AbstractReadUnit[float], parent: QWidget = None):
        super().__init__(parent)
        self.__picket_position: AbstractReadUnit[float] = picket_position

        #========================================================
        #name_label_style = '''font-weight: bold;font-size: 14px;'''
        #info_label_style = '''font-weight: bold;font-size: 14px;color: yellow;background-color: black;'''
        #========================================================
        picket_position_prefix_label = QLabel(QCoreApplication.translate('UI/Common', 'Picket: '))
        picket_position_prefix_label.setProperty("infoPanelLabel", True)
        self.__kilometer_value_label = QLabel('---')
        self.__kilometer_value_label.setProperty("infoPanelValueYellowBlack", True)
        kilometer_suffix_label = QLabel(QCoreApplication.translate('UI/Common', 'km'))
        kilometer_suffix_label.setProperty("infoPanelLabel", True)
        self.__meter_value_label = QLabel('---')
        self.__meter_value_label.setProperty("infoPanelValueYellowBlack", True)
        meter_suffix_label = QLabel(QCoreApplication.translate('UI/Common', 'm'))
        meter_suffix_label.setProperty("infoPanelLabel", True)
        self.__millimeter_value_label = QLabel('---')
        self.__millimeter_value_label.setProperty("infoPanelValueYellowBlack", True)
        millimeter_suffix_label = QLabel(QCoreApplication.translate('UI/Common', 'mm'))
        millimeter_suffix_label.setProperty("infoPanelLabel", True)

        # picket_position_prefix_label.setStyleSheet(name_label_style)
        # self.__kilometer_value_label.setStyleSheet(info_label_style)
        # kilometer_suffix_label.setStyleSheet(name_label_style)
        # self.__meter_value_label.setStyleSheet(info_label_style)
        # meter_suffix_label.setStyleSheet(name_label_style)
        # self.__millimeter_value_label.setStyleSheet(info_label_style)
        # millimeter_suffix_label.setStyleSheet(name_label_style)

        self.__kilometer_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.__meter_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.__millimeter_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.__kilometer_value_label.setMargin(5)
        self.__meter_value_label.setMargin(5)
        self.__millimeter_value_label.setMargin(5)
        self.__kilometer_value_label.setMinimumWidth(120)
        self.__meter_value_label.setMinimumWidth(80)
        self.__millimeter_value_label.setMinimumWidth(80)
        #self.setStyleSheet("background-color: #D1F7F2")
        #========================================================
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(picket_position_prefix_label, alignment = Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.__kilometer_value_label)
        layout.addWidget(kilometer_suffix_label)
        layout.addWidget(self.__meter_value_label)
        layout.addWidget(meter_suffix_label)
        layout.addWidget(self.__millimeter_value_label)
        layout.addWidget(millimeter_suffix_label)
        #========================================================
        self.__picket_position.changed.connect(self.__picket_position_changed)
        self.__picket_position_changed(self.__picket_position.read())

    def __picket_position_changed(self, picket: float) ->None:
        self.__kilometer_value_label.setNum(int(picket / 1000))
        self.__meter_value_label.setNum(int(picket) % 1000)
        self.__millimeter_value_label.setNum(int(picket * 1000) % 1000)


class ProgramTaskFileName(StringLabel):
    def __init__(self, program_task_name: str, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'File name:'), program_task_name, parent)

class HowManyMetersLeft(StringLabel):
    def __init__(self, meters: str, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Meters left:'), meters, parent)