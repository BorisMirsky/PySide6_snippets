from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QLineEdit,QPushButton,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout, QLabel)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys


class RightColumnWidget(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()
        groupbox_top = QGroupBox()
        groupbox_vlayout = QVBoxLayout()
        groupbox_top.setLayout(groupbox_vlayout)
        groupbox_top.setTitle("Редактирование")
        self.params_button = QPushButton("Параметры")
        self.shifts_button = QPushButton("Сдвиги")
        groupbox_vlayout.addWidget(self.params_button)
        groupbox_vlayout.addWidget(self.shifts_button)
        self.params_button.clicked.connect(self.__params_button)
        self.shifts_button.clicked.connect(self.__shifts_button)
        self.results_button = QPushButton("Результаты")
        self.settings_button = QPushButton("Установки")
        self.escape_button = QPushButton("Выход(ESC)")
        self.results_button.clicked.connect(self.__results_button)
        self.settings_button.clicked.connect(self.__settings_button)
        self.escape_button.clicked.connect(self.__escape_button)
        self.buttons = []
        self.buttons.append(self.params_button)
        self.buttons.append(self.shifts_button)
        self.buttons.append(self.results_button)
        self.buttons.append(self.settings_button)
        self.buttons.append(self.escape_button)
        #############################################

        vbox1 = QVBoxLayout()
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

        groupbox_bottom = QGroupBox()
        groupbox_bottom_layout = QVBoxLayout()
        groupbox_bottom.setLayout(groupbox_bottom_layout)
        groupbox_bottom_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Натура")
        fact_label.setStyleSheet("font: bold; font-size: 12pt;color:green")
        fact_label_value = QLabel(str(0))
        fact_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_bottom_layout_hbox1.addWidget(fact_label_value)
        groupbox_bottom_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        prj_label_value = QLabel(str(0))
        prj_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox2.addWidget(prj_label)
        groupbox_bottom_layout_hbox2.addWidget(prj_label_value)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox1)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox2)

        shifts_label = QLabel("Сдвиги")
        shifts_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        shifts_label_value = QLabel(str(0))
        shifts_label_value.setStyleSheet(value_style)
        hbox2.addWidget(shifts_label)
        hbox2.addWidget(shifts_label_value)
        groupbox_bottom.setStyleSheet("background-color:white")
        vbox1.addLayout(hbox1)
        vbox1.addWidget(groupbox_bottom)
        vbox1.addLayout(hbox2)





        ##########################################
        vbox.addWidget(groupbox_top)
        vbox.addStretch(1)
        vbox.addWidget(self.results_button)
        vbox.addStretch(1)
        vbox.addWidget(self.settings_button)
        vbox.addStretch(5)
        vbox.addWidget(self.escape_button)
        vbox.addStretch(1)
        vbox.addLayout(vbox1)
        self.setLayout(vbox)


    # ======================= Окраска нажатой кнопки ==================================
    def __params_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __shifts_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __results_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __settings_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __escape_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")


#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     lcw = RightColumnWidget()
#     lcw.show()
#     sys.exit(app.exec())