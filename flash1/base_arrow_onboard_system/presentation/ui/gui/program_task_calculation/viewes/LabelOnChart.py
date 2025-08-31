from PySide6.QtWidgets import QWidget, QLabel
#from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
#from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
#from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
#import sys




class LabelOnParent(QLabel):
    def __init__(self, title, parent):
        super(LabelOnParent, self).__init__(title, parent)
        self.move(1600,10)