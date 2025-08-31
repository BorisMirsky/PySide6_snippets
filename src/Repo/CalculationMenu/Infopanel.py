from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QLineEdit,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout, QLabel)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
#import numpy as np
#import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)
#from NumpyTableModel import NumpyTableModel
#from VerticalLine import MoveLineController, VerticalLineModel
#from ServiceInfo import get_csv_column, DATA_LEN, FILENAME
#from Charts import Chart1, Chart2, ChartsWidget
#from Bottom import BottomWidget
#from VerticalLine import VerticalLineModel1,VerticalLineModel2, MoveLineController
#from Data
#from dataclasses import dataclass
#from typing import Optional, List
#from enum import Enum




class InfopanelFirst(QWidget):
    def __init__(self):
        super().__init__()
        self.information_panel_first_layout = QHBoxLayout()
        value_style = "font:bold;font-size:13pt;color:black;background-color:white"
        peregon_label = QLabel("Перегон")
        path_number_label = QLabel("Путь")
        peregon_value = QLabel()
        peregon_value.setStyleSheet(value_style)
        path_value = QLabel()
        path_value.setStyleSheet(value_style)
        machine_label = QLabel("Машина")
        machine_value = QLabel()
        machine_value.setStyleSheet(value_style)
        self.information_panel_first_layout.addWidget(peregon_label)
        self.information_panel_first_layout.addWidget(peregon_value, 5)
        self.information_panel_first_layout.addStretch(3)
        self.information_panel_first_layout.addWidget(path_number_label)
        self.information_panel_first_layout.addWidget(path_value, 3)
        self.information_panel_first_layout.addStretch(3)
        self.information_panel_first_layout.addWidget(machine_label)
        self.information_panel_first_layout.addWidget(machine_value, 5)
        self.setMaximumHeight(50)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.information_panel_first_layout)


class InfopanelSecond(QWidget):
    def __init__(self):
        super().__init__()
        self.information_panel_second_layout = QHBoxLayout()
        value_style = "font:bold;font-size:13pt;color:black;background-color:white"
        start_label = QLabel("Начало")
        start_km_value = QLabel()
        start_km_value.setStyleSheet(value_style)
        start_km_label = QLabel("KM+")
        start_m_value = QLabel()
        start_m_value.setStyleSheet(value_style)
        start_m_label = QLabel("M")
        length_label = QLabel("Длина")
        length_value = QLabel()
        length_value.setMaximumHeight(25)
        length_value.setStyleSheet(value_style)
        length_m_label = QLabel("M")
        end_label = QLabel("Конец")
        end_km_value = QLabel()
        end_km_value.setStyleSheet(value_style)
        end_km_label = QLabel("KM+")
        end_m_value = QLabel()
        end_m_value.setStyleSheet(value_style)
        end_m_label = QLabel("M")
        current_date_label = QLabel("Дата")
        current_date_value = QLabel()
        current_date_value.setStyleSheet(value_style)
        clamp_label = QLabel("Прижим")
        clamp_value = QLabel()
        clamp_value.setMaximumHeight(25)
        clamp_value.setStyleSheet("font:bold;font-size:13pt;color:red;background-color:white")

        self.information_panel_second_layout.addWidget(start_label)
        self.information_panel_second_layout.addWidget(start_km_value,3)
        self.information_panel_second_layout.addWidget(start_km_label)
        self.information_panel_second_layout.addWidget(start_m_value,3)
        self.information_panel_second_layout.addWidget(start_m_label)
        self.information_panel_second_layout.addStretch(3)
        self.information_panel_second_layout.addWidget(length_label)
        self.information_panel_second_layout.addWidget(length_value,3)
        self.information_panel_second_layout.addWidget(length_m_label)
        self.information_panel_second_layout.addStretch(3)
        self.information_panel_second_layout.addWidget(end_label)
        self.information_panel_second_layout.addWidget(end_km_value,3)
        self.information_panel_second_layout.addWidget(end_km_label)
        self.information_panel_second_layout.addWidget(end_m_value,3)
        self.information_panel_second_layout.addWidget(end_m_label)
        self.information_panel_second_layout.addStretch(3)
        self.information_panel_second_layout.addWidget(current_date_label)
        self.information_panel_second_layout.addWidget(current_date_value,2)
        self.information_panel_second_layout.addWidget(clamp_label)
        self.information_panel_second_layout.addWidget(clamp_value, 2)
        self.setMaximumHeight(50)
        self.setContentsMargins(0,0,0,0)

        self.setLayout(self.information_panel_second_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    IPF = InfopanelFirst() #InfopanelFirst()
    IPF.show()
    sys.exit(app.exec())
