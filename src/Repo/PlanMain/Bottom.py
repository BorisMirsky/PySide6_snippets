
from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,QTextEdit,QStackedWidget,QLabel,QGridLayout,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QToolButton)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QShortcut
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QSize
import sys
#from ServiceInfo import *
#from VerticalLine import VerticalLineModel1, VerticalLineModel2 #, MoveLineController

"""
имя 1го групбокса должно меняться
      
"""


class BottomWidget(QWidget):
    def __init__(self):
        super().__init__()
        #grid = QGridLayout()
        hbox = QHBoxLayout()
        label1 = QLabel("Сумма сдвигов")
        label2 = QLabel("Сумма модулей сдвигов")
        label3 = QLabel("Максимальный сдвиг влево")
        label4 = QLabel("Максимальный сдвиг вправо")
        label_mm1 = QLabel("mm")
        label_mm2 = QLabel("mm")
        label_mm3 = QLabel("mm")
        label_mm4 = QLabel("mm")
        label_value1 = QLabel("     ")
        label_value2 = QLabel("     ")
        label_value3 = QLabel("     ")
        label_value4 = QLabel("     ")
        value_style = "font: bold; font-size: 13pt;color:black;background-color:white"
        label_style = "font: bold; font-size: 13pt;color:black;"
        mm_style = "font: bold; font-size: 11pt;color:black;"
        for i in (label_value1,label_value2,label_value3,label_value4):
            i.setStyleSheet(value_style)
        for i in (label1, label2, label3, label4):
            i.setStyleSheet(label_style)
        for i in (label_mm1,label_mm2,label_mm3,label_mm4):
            i.setStyleSheet(mm_style)

        hbox.addWidget(label1) #, 0, 0)
        hbox.addWidget(label_value1) #, 0, 1)
        hbox.addWidget(label_mm1) #, 0, 2)
        hbox.addStretch(1)

        hbox.addWidget(label2) #, 1, 0)
        hbox.addWidget(label_value2) #, 1, 1)
        hbox.addWidget(label_mm2) #, 1, 2)
        hbox.addStretch(1)

        hbox.addWidget(label3) #, 0, 3)
        hbox.addWidget(label_value3) #, 0, 4)
        hbox.addWidget(label_mm3) #, 0, 5)
        hbox.addStretch(1)

        hbox.addWidget(label4) #, 1, 3)
        hbox.addWidget(label_value4)  #, 1, 4)
        hbox.addWidget(label_mm4)   #, 1, 5)
        hbox.addStretch(1)

        self.setMaximumHeight(80)
        self.setLayout(hbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    BW = BottomWidget()
    BW.show()
    sys.exit(app.exec())
