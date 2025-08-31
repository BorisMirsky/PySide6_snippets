from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
#import numpy as np
#import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)
#from NumpyTableModel import NumpyTableModel
#from VerticalLine import MoveLineController, VerticalLineModel
from ServiceInfo import get_csv_column, DATA_LEN, FILENAME
from Charts import Chart1, Chart2 #, ChartsWidget
from Bottom import BottomWidget
from VerticalLine import VerticalLineModel1,VerticalLineModel2     #, MoveLineController
from HorizontalLine import HorizontalLineModel
from Infopanel import InfopanelFirst, InfopanelSecond
from RightColumnWidget import  RightColumnWidget
#from Data
#from dataclasses import dataclass
#from typing import Optional, List
#from enum import Enum

#self.__edited_restrictions['segments'][0]['shifting_right']
# restricrions = {'segments': [{'v_pass':10, 'v_gruz':123, 'shifting_right':44, 'shifting_left':33,
#                               'raising_ubound':444, 'raising_lbound':3}]}

#model1 = VerticalLineModel1 #(100)
#model2 = VerticalLineModel2 #(None)

class MainWidget(QWidget):
    def __init__(self, v_model1:VerticalLineModel1,
                 v_model2:VerticalLineModel2):         #,    h_model:HorizontalLineModel):
        super().__init__()
        self.vertical_model1 = v_model1
        self.vertical_model2 = v_model2
        grid = QGridLayout()
        infopanel_first = InfopanelFirst()
        infopanel_second = InfopanelSecond()
        grid.addWidget(infopanel_first, 0, 0, 1, 7)
        grid.addWidget(infopanel_second, 1, 0, 1, 7)
        chart1 = Chart1('plan_prj', 'plan_fact')
        chart2 = Chart2('plan_delta', self.vertical_model1) #, self.horizontal_model)  # self.vertical_model2,
        chart2.installEventFilter(chart2)
        grid.addWidget(chart1, 2, 0, 5, 6)
        grid.addWidget(chart2, 7, 0, 3, 6)
        rcw = RightColumnWidget()
        grid.addWidget(rcw, 2, 6, 1, 1)
        bottom = BottomWidget()
        grid.addWidget(bottom, 10, 0, 1, 6)
        self.setLayout(grid)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget(VerticalLineModel1(DATA_LEN * 0.5), VerticalLineModel2()) #, HorizontalLineModel())
    MW.show()
    sys.exit(app.exec())

