# This Python file uses the following encoding: utf-8

# Вот тут надо написать плашку с данными. Что за плашка -- см. рисунок
# ...
from AbstractModels import AbstractReadModel
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import QGridLayout, QWidget, QLabel
import sys


#
# lbl_css_1 = ("font-weight: bold;font-size: 20px;color: white;background-color:black; border: 1px solid red;")
# lbl_css_2 = ("font-weight: bold;font-size: 20px;color: white;background-color:black;border: 1px solid blue; ")
#
#
# class TaskClass(QWidget):
#     def __init__(self, model):
#         super().__init__()
#         self.model = model
#         self.setWindowTitle("Задание 1")
#         hbox1 = QHBoxLayout()
#         label1_1 = QLabel("датчик 1")
#         label1_1.setStyleSheet(lbl_css_2)
#         label1_2 = QLabel("")
#         label1_2.setStyleSheet(lbl_css_1)
#         label1_3 = QLabel("датчик 3")
#         label1_3.setStyleSheet(lbl_css_2)
#         label1_4 = QLabel("")
#         label1_4.setStyleSheet(lbl_css_1)
#         hbox1.addWidget(label1_1)
#         hbox1.addWidget(label1_2)
#         hbox1.addWidget(label1_3)
#         hbox1.addWidget(label1_4)
#         hbox2 = QHBoxLayout()
#         label2_1 = QLabel("датчик 2")
#         label2_1.setStyleSheet(lbl_css_2)
#         label2_2 = QLabel("")
#         label2_2.setStyleSheet(lbl_css_1)
#         label2_3 = QLabel("датчик 4")
#         label2_3.setStyleSheet(lbl_css_2)
#         label2_4 = QLabel("")
#         label2_4.setStyleSheet(lbl_css_1)
#         hbox2.addWidget(label2_1)
#         hbox2.addWidget(label2_2)
#         hbox2.addWidget(label2_3)
#         hbox2.addWidget(label2_4)
#         vbox = QVBoxLayout()
#         vbox.addLayout(hbox1)
#         vbox.addLayout(hbox2)
#         self.setLayout(vbox)
#         return


class InformationLabelClass(QWidget):
    def __init__(self,
                sensor_1: AbstractReadModel[float],
                sensor_2: AbstractReadModel[float],
                sensor_3: AbstractReadModel[float],
                sensor_4: AbstractReadModel[float],
                parent: QWidget = None) ->None:
        super().__init__(parent)

        self.__sensor_1_view = QLabel('--')
        self.__sensor_2_view = QLabel('--')
        self.__sensor_3_view = QLabel('--')
        self.__sensor_4_view = QLabel('--')
        #
        self.__time_counter = QLabel('--')
        time_counter = QTimer(self)
        time_counter.timeout.connect(self.__returnTimerValue)
        time_counter.start(10)
        self.counter = 0
        #
        sensor_1.valueChanged.connect(lambda: self.__sensor_1_view.setNum(sensor_1.read()))
        sensor_2.valueChanged.connect(lambda: self.__sensor_2_view.setNum(sensor_2.read()))
        sensor_3.valueChanged.connect(lambda: self.__sensor_3_view.setNum(sensor_3.read()))
        sensor_4.valueChanged.connect(lambda: self.__sensor_4_view.setNum(sensor_4.read()))

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('Sensor 1:'), 0, 0)
        layout.addWidget(self.__sensor_1_view, 0, 1)
        layout.addWidget(QLabel('Sensor 2:'), 0, 2)
        layout.addWidget(self.__sensor_2_view, 0, 3)
        layout.addWidget(QLabel('Sensor 3:'), 1, 0)
        layout.addWidget(self.__sensor_3_view, 1, 1)
        layout.addWidget(QLabel('Sensor 4:'), 1, 2)
        layout.addWidget(self.__sensor_4_view, 1, 3)

    def __returnTimerValue(self):
        self.counter = self.counter + 1
        self.__time_counter.setNum(self.counter)


