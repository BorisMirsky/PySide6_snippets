
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QApplication
#from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
import numpy as np

#https://stackoverflow.com/questions/67249276/how-to-set-a-background-color-to-a-set-of-qlabels-in-pyqt5
class Sensors(QWidget):
    def __init__(self):
        super().__init__()
        # styles
        title_style="color: black;font: bold 15px;"
        sensors_style=("background-color:black;color: White;padding:2px;font: bold 12px;border: 2px solid black;border-radius:9px;")
        widget_box_style1="background-color:green;"
        widget_box_style2="background-color:cyan;"
        # box 1


        #
        label_title_1 = QLabel("Подъёмки")
        label_title_1_left = QLabel("левая/")
        label_title_1_right = QLabel("правая/")
        label_title_1_prj = QLabel("проект")
        label_title_1.setStyleSheet(title_style)
        label_title_1_left.setStyleSheet("color: gray;font: bold 11px;")
        label_title_1_right.setStyleSheet("color: yellow;font: bold 11px;")
        label_title_1_prj.setStyleSheet("color: red;font: bold 11px;")
        box1_titles_hbox = QHBoxLayout()
        box1_titles_hbox.addWidget(label_title_1_left)
        box1_titles_hbox.addWidget(label_title_1_right)
        box1_titles_hbox.addWidget(label_title_1_prj)        
        sensor1_1 = QLabel("1.1")
        sensor1_2 = QLabel("2.2")
        sensor1_3 = QLabel("3.3")
        sensor1_1.setStyleSheet(sensors_style)
        sensor1_2.setStyleSheet(sensors_style)
        sensor1_3.setStyleSheet(sensors_style)
        box1_vbox = QVBoxLayout()
        box1_hbox = QHBoxLayout()
        box1_hbox.addWidget(sensor1_1)
        box1_hbox.addWidget(sensor1_2)
        box1_hbox.addWidget(sensor1_3)
        box1_vbox.addWidget(label_title_1)
        box1_vbox.addLayout(box1_titles_hbox)
        box1_vbox.addLayout(box1_hbox)
        box1_widget = QWidget()
        box1_widget.setStyleSheet(widget_box_style1)
        box1_widget.setLayout(box1_vbox)
        #
        label_title_2 = QLabel("Сдвижки")
        label_title_2.setStyleSheet(title_style)
        sensor2_1 = QLabel("3.3")
        sensor2_2 = QLabel("4.4")
        
        label_title_2_left = QLabel("натура")
        label_title_2_right = QLabel("проект")
        label_title_2_left.setStyleSheet("color: blue;font: bold 11px;")
        label_title_2_right.setStyleSheet("color: red;font: bold 11px;")
        
        sensor2_1.setStyleSheet(sensors_style)
        sensor2_2.setStyleSheet(sensors_style)
        box2_vbox = QVBoxLayout()
        box2_hbox = QHBoxLayout()
        box2_titles_hbox = QHBoxLayout()
        box2_titles_hbox.addWidget(label_title_2_left)
        box2_titles_hbox.addWidget(label_title_2_right)
        box2_hbox.addWidget(sensor2_1)
        box2_hbox.addWidget(sensor2_2)
        box2_vbox.addWidget(label_title_2)
        box2_vbox.addLayout(box2_titles_hbox)
        box2_vbox.addLayout(box2_hbox)
        box2_widget = QWidget()
        box2_widget.setStyleSheet(widget_box_style2)
        box2_widget.setLayout(box2_vbox)
        #
        vbox = QVBoxLayout()
        vbox.addWidget(box1_widget)
        vbox.addWidget(box2_widget)
        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Sensors()
    window.show()
    sys.exit(app.exec())
