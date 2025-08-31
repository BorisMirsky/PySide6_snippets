from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QLineEdit,
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
        #
        value_style = "font: bold; font-size: 12pt;color:white;background-color:black"
        point_number_label = QLabel("№ точки")
        point_number_label.setStyleSheet("font: bold; font-size: 12pt;color:black")
        point_number_label_value = QLabel(str(1))
        point_number_label_value.setStyleSheet(value_style)
        hbox1.addWidget(point_number_label)
        hbox1.addWidget(point_number_label_value)

        groupbox = QGroupBox()
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)
        groupbox_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Натура")
        fact_label.setStyleSheet("font: bold; font-size: 12pt;color:green")
        fact_label_value = QLabel(str(0))
        fact_label_value.setStyleSheet(value_style)
        groupbox_layout_hbox1.addWidget(fact_label)
        groupbox_layout_hbox1.addWidget(fact_label_value)
        groupbox_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        prj_label_value = QLabel(str(0))
        prj_label_value.setStyleSheet(value_style)
        groupbox_layout_hbox2.addWidget(prj_label)
        groupbox_layout_hbox2.addWidget(prj_label_value)
        groupbox_layout.addLayout(groupbox_layout_hbox1)
        groupbox_layout.addLayout(groupbox_layout_hbox2)

        shifts_label = QLabel("Сдвиги")
        shifts_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        shifts_label_value = QLabel(str(0))
        shifts_label_value.setStyleSheet(value_style)
        hbox2.addWidget(shifts_label)
        hbox2.addWidget(shifts_label_value)
        self.setStyleSheet("background-color:white")

        vbox.addLayout(hbox1)
        vbox.addWidget(groupbox)
        vbox.addLayout(hbox2)
        #self.setMaximumHeight(100)
        #self.setMaximumWidth(100)
        self.setLayout(vbox)

#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     IPF = RightColumnWidget() #InfopanelFirst()
#     IPF.show()
#     sys.exit(app.exec())