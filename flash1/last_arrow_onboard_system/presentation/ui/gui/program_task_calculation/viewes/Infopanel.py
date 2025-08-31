from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QLineEdit,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout, QLabel)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
from ...common.elements.Time import CurrentTimeLabel
from domain.dto.Workflow import LiningTripResultDto, ProgramTaskCalculationResultDto
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel


# state1: LiningTripResultDto = False, state: ProgramTaskCalculationSuccessState = False,
class InfopanelFirst(QWidget):
    def __init__(self, state,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
        # domain.dto.Workflow.ProgramTaskCalculationResultDto
        peregon, machine = None, None
        if type(state) == ProgramTaskCalculationResultDto:             # Для перерасчёта  calculation_result()
            options: ProgramTaskCalculationResultDto = self.__state.options
            peregon = options.measuring_trip.options.track_title
            machine = options.measuring_trip.machine_parameters['description']
        elif type(state) == LiningTripResultDto:                        # Для выправки
            peregon = self.__state.options.program_task.options.measuring_trip.options.track_title
            machine = self.__state.options.program_task.options.measuring_trip.machine_parameters['description']
        information_panel_first_layout = QHBoxLayout()
        value_style = "font-size:13pt;color:black;background-color:white"         # font:bold;
        peregon_label = QLabel("Перегон")
        path_number_label = QLabel("Путь")
        peregon_value = QLabel(peregon)
        peregon_value.setStyleSheet(value_style)
        path_value = QLabel()
        path_value.setStyleSheet(value_style)
        machine_value = QLabel(machine)
        machine_value.setStyleSheet(value_style)
        information_panel_first_layout.addWidget(peregon_label, 1)
        information_panel_first_layout.addWidget(peregon_value, 5)
        information_panel_first_layout.addStretch(3)
        #information_panel_first_layout.addWidget(path_number_label, 1)
        #information_panel_first_layout.addWidget(path_value, 1)
        #information_panel_first_layout.addStretch(3)
        information_panel_first_layout.addWidget(machine_value, 3)
        information_panel_first_layout.addStretch(3)
        information_panel_first_layout.addWidget(CurrentTimeLabel(), 3)
        self.setMaximumHeight(50)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(information_panel_first_layout)

#state: ProgramTaskCalculationSuccessState, state1: LiningTripResultDto = False,
class InfopanelSecond(QWidget):
    def __init__(self, state,  parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
        rail_dict = {"Right": "Правый", "Left": "Левый"}
        # state = calculation_result
        start_km, start_m, length, end_km, end_m, rail = None, None, 0, None,None, None
        clamp_value = QLabel()
        if type(state) is ProgramTaskCalculationResultDto:   #ProgramTaskCalculationSuccessState:
            options: ProgramTaskCalculationResultDto = self.__state.options
            start_km = str(int(options.start_picket.meters // 1000))
            start_m = str(int(options.start_picket.meters % 1000))
            length = round(self.__state.length, 1)
            end_km = str(int(self.__state.end_picket.meters // 1000))
            end_m = str(int(self.__state.end_picket.meters % 1000))
            rail = options.measuring_trip.options.press_rail
            clamp_value = QLabel(rail_dict[str(rail).split('.')[1]])
        elif type(state) is LiningTripResultDto:
            start_km = str(int(self.__state.options.start_picket.meters // 1000))
            start_m = str(int(self.__state.options.start_picket.meters % 1000))
            length = round(self.__state.options.program_task.length, 1)
            end_km = str(int(self.__state.options.program_task.end_picket.meters // 1000))
            end_m = str(int(self.__state.options.program_task.end_picket.meters % 1000))
            rail = self.__state.options.program_task.options.measuring_trip.options.press_rail.name
            clamp_value = QLabel(rail_dict[rail])
        self.information_panel_second_layout = QHBoxLayout()
        value_style = "font-size:13pt;color:black;background-color:white"         # font:bold;
        start_label = QLabel("Начало")
        start_km_value = QLabel(start_km)
        start_km_value.setStyleSheet(value_style)
        start_km_label = QLabel("KM+")
        start_m_value = QLabel(start_m)
        start_m_value.setStyleSheet(value_style)
        start_m_label = QLabel("M")
        length_label = QLabel("Длина")
        value_length = float('{:.1f}'.format(length))
        length_value = QLabel(str(value_length))
        length_value.setMaximumHeight(25)
        length_value.setStyleSheet(value_style)
        length_m_label = QLabel("M")
        end_label = QLabel("Конец")
        end_km_value = QLabel(end_km)
        end_km_value.setStyleSheet(value_style)
        end_km_label = QLabel("KM+")
        end_m_value = QLabel(end_m)
        end_m_value.setStyleSheet(value_style)
        end_m_label = QLabel("M")
        clamp_label = QLabel("Прижим")
        clamp_value.setMaximumHeight(25)
        clamp_value.setStyleSheet(value_style)
        self.information_panel_second_layout.addWidget(start_label, 1)
        self.information_panel_second_layout.addWidget(start_km_value, 1)
        self.information_panel_second_layout.addWidget(start_km_label, 1)
        self.information_panel_second_layout.addWidget(start_m_value, 1)
        self.information_panel_second_layout.addWidget(start_m_label, 1)
        self.information_panel_second_layout.addStretch(3)
        self.information_panel_second_layout.addWidget(length_label, 1)
        self.information_panel_second_layout.addWidget(length_value, 1)
        self.information_panel_second_layout.addWidget(length_m_label, 1)
        self.information_panel_second_layout.addStretch(3)
        self.information_panel_second_layout.addWidget(end_label, 1)
        self.information_panel_second_layout.addWidget(end_km_value, 1)
        self.information_panel_second_layout.addWidget(end_km_label, 1)
        self.information_panel_second_layout.addWidget(end_m_value, 1)
        self.information_panel_second_layout.addWidget(end_m_label, 1)
        self.information_panel_second_layout.addStretch(3)
        self.information_panel_second_layout.addWidget(clamp_label, 1)
        self.information_panel_second_layout.addWidget(clamp_value, 1)
        self.setMaximumHeight(50)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(self.information_panel_second_layout)
