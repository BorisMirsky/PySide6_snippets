from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QLineEdit,QCheckBox,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout, QLabel)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys


class RightColumnWidget(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        widget = QWidget()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        label_name = QLabel("План")
        label_name.setStyleSheet("font:bold; font-size:16pt;") # color:white;background-color:black")
        hbox1.addWidget(label_name)
        label_prj_name = QLabel("Проект")
        label_prj_name.setStyleSheet("font:bold; font-size:13pt; color:red;") #background-color:black")
        label_prj_value = QLabel()
        label_prj_value.setStyleSheet("font:bold; font-size:13pt; color:yellow; background-color:blue")
        hbox2.addWidget(label_prj_name)
        hbox2.addWidget(label_prj_value)
        label_fact_name = QLabel("Натура")
        label_fact_name.setStyleSheet("font:bold; font-size:13pt; color:green;")
        label_fact_value = QLabel()
        label_fact_value.setStyleSheet("font:bold; font-size:13pt; color:yellow; background-color:blue")
        hbox2.addWidget(label_fact_name)
        hbox2.addWidget(label_fact_value)
        self.checkBox_prj = QCheckBox("Проект")
        self.checkBox_prj.stateChanged.connect(self.handleCheckBoxPrj)
        self.checkBox_fact = QCheckBox("Натура")
        self.checkBox_fact.stateChanged.connect(self.handleCheckBoxFact)
        hbox3.addWidget(self.checkBox_prj)
        hbox3.addWidget(self.checkBox_fact)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)


    def handleCheckBoxPrj(self, checked):
        if checked:
            print('prj 1')
        else:
            print('prj 0')
        self.show()
 
    def handleCheckBoxFact(self, checked):
        if checked:
            print('fact 1')
        else:
            print('fact 0')  
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    IPF = RightColumnWidget() #InfopanelFirst()
    IPF.show()
    sys.exit(app.exec())
