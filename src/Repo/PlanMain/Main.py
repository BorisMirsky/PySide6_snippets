from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
from Charts import ChartsWidget
from Bottom import BottomWidget
from Infopanel import InfopanelFirst, InfopanelSecond
from RightColumn import RightColumnWidget


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        infopanel_first = InfopanelFirst()
        infopanel_second = InfopanelSecond()
        #grid.addWidget(infopanel_first, 0, 0, 1, 10)
        #grid.addWidget(infopanel_second, 1, 0, 1, 10)
        charts_widget = ChartsWidget('plan_prj', 'plan_fact', 'plan_delta') #, self.vertical_model)
        grid.addWidget(charts_widget, 2, 0, 8, 9)
        rcw = RightColumnWidget()
        bottom = BottomWidget()
        #grid.addWidget(rcw, 2, 9, 8, 1)
        #grid.addWidget(bottom, 10, 0, 1, 10)
        self.setLayout(grid)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget()
    MW.show()
    sys.exit(app.exec())

