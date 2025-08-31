from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
from ServiceInfo import get_csv_column, DATA_LEN, FILENAME
from Charts import ChartsWidget
from Bottom import BottomWidget
from VerticalLine import VerticalLineModel1,VerticalLineModel2
from HorizontalLine import HorizontalLineModel
from Infopanel import InfopanelFirst, InfopanelSecond
from RightColumnWidget import  RightColumnWidget

#self.__edited_restrictions['segments'][0]['shifting_right']
# restricrions = {'segments': [{'v_pass':10, 'v_gruz':123, 'shifting_right':44, 'shifting_left':33,
#                               'raising_ubound':444, 'raising_lbound':3}]}



class MainWidget(QWidget):
    def __init__(self, v_model:VerticalLineModel1):
        super().__init__()
        self.vertical_model = v_model
        grid = QGridLayout()
        infopanel_first = InfopanelFirst()
        infopanel_second = InfopanelSecond()
        grid.addWidget(infopanel_first, 0, 0, 1, 10)
        grid.addWidget(infopanel_second, 1, 0, 1, 10)
        charts_widget = ChartsWidget('plan_prj', 'plan_fact', 'plan_delta', self.vertical_model)
        grid.addWidget(charts_widget, 2, 0, 8, 9)
        rcw = RightColumnWidget()
        right_vbox = QVBoxLayout()
        right_vbox.addStretch(5)
        right_vbox.addWidget(rcw)
        grid.addLayout(right_vbox, 2, 9, 1, 1)
        bottom = BottomWidget()
        grid.addWidget(bottom, 10, 0, 1, 10)
        self.setLayout(grid)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget(VerticalLineModel1(DATA_LEN * 0.5))
    MW.show()
    sys.exit(app.exec())

