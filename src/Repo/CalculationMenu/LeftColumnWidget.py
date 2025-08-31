from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QLineEdit,QPushButton,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QGridLayout, QLabel)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys


class LeftColumnWidget(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()
        #
        groupbox_top = QGroupBox()
        groupbox_top_vlayout = QVBoxLayout()
        groupbox_top.setLayout(groupbox_top_vlayout)
        self.plan_button = QPushButton("План")
        self.level_button = QPushButton("Уровень")
        self.profile_button = QPushButton("Профиль")
        self.plan_button.clicked.connect(self.__plan_button)
        self.level_button.clicked.connect(self.__level_button)
        self.profile_button.clicked.connect(self.__profile_button)
        self.plan_green = True
        self.plan_yellow = False
        self.plan_red = False
        self.level_green = True
        self.level_yellow = False
        self.level_red = False
        self.profile_green = True
        self.profile_yellow = False
        self.profile_red = False
        groupbox_top_hlayout1 = QHBoxLayout()
        groupbox_top_hlayout2 = QHBoxLayout()
        groupbox_top_hlayout3 = QHBoxLayout()

        self.img1 = QLabel(self)
        if self.plan_green:
            #print('plan_green')
            self.pixmap1 = QPixmap('Data/green_narrow1')
        elif self.plan_yellow:
            #print('plan_yellow')
            self.pixmap1 = QPixmap('Data/yellow_narrow1')
        elif self.plan_red:
            #print('plan_red')
            self.pixmap1 = QPixmap('Data/red_narrow1')
        self.img1.setPixmap(self.pixmap1)
        img2 = QLabel(self)
        pixmap2 = QPixmap('Data/green_narrow2')
        img2.setPixmap(pixmap2)
        img3 = QLabel(self)
        pixmap3 = QPixmap('Data/green_narrow3')
        img3.setPixmap(pixmap3)

        groupbox_top_hlayout1.addWidget(self.img1)
        groupbox_top_hlayout1.addWidget(self.plan_button)
        groupbox_top_hlayout2.addWidget(img2)
        groupbox_top_hlayout2.addWidget(self.level_button)
        groupbox_top_hlayout3.addWidget(img3)
        groupbox_top_hlayout3.addWidget(self.profile_button)
        groupbox_top_vlayout.addLayout(groupbox_top_hlayout1)
        groupbox_top_vlayout.addLayout(groupbox_top_hlayout2)
        groupbox_top_vlayout.addLayout(groupbox_top_hlayout3)
        self.results_button = QPushButton("Результаты")
        self.settings_button = QPushButton("Установки")
        self.print_button = QPushButton("Печать")
        self.save_button = QPushButton("Сохранить")
        self.escape_button = QPushButton("Выход(ESC)")
        self.results_button.clicked.connect(self.__results_button)
        self.settings_button.clicked.connect(self.__settings_button)
        self.print_button.clicked.connect(self.__print_button)
        self.save_button.clicked.connect(self.__save_button)
        self.escape_button.clicked.connect(self.__escape_button)
        #
        groupbox_left_bottom = QGroupBox()
        groupbox_left_bottom_layout = QVBoxLayout()
        groupbox_left_bottom.setLayout(groupbox_left_bottom_layout)
        groupbox_left_bottom_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Пикетаж")
        groupbox_left_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_left_bottom_layout_hbox2 = QHBoxLayout()
        km_value_label = QLabel("")
        km_value_label.setStyleSheet("font-size:10pt; color:white; background-color:black")
        km_label = QLabel("КМ")
        m_value_label = QLabel("")
        m_value_label.setStyleSheet("font-size:10pt; color:white; background-color:black")
        m_label = QLabel("КМ")
        groupbox_left_bottom_layout_hbox2.addWidget(km_value_label)
        groupbox_left_bottom_layout_hbox2.addWidget(km_label)
        groupbox_left_bottom_layout_hbox2.addWidget(m_value_label)
        groupbox_left_bottom_layout_hbox2.addWidget(m_label)
        groupbox_left_bottom_layout_hbox3 = QHBoxLayout()
        scale_label = QLabel("Масштаб")
        scale_value_label = QLabel("1")
        scale_value_label.setStyleSheet("font-size:10pt; color:white; background-color:black")
        groupbox_left_bottom_layout_hbox3.addWidget(scale_label)
        groupbox_left_bottom_layout_hbox3.addWidget(scale_value_label)
        groupbox_left_bottom_layout.addLayout(groupbox_left_bottom_layout_hbox1)
        groupbox_left_bottom_layout.addLayout(groupbox_left_bottom_layout_hbox2)
        groupbox_left_bottom_layout.addLayout(groupbox_left_bottom_layout_hbox3)
        #
        self.buttons = []  # список для хранения кнопок, нужен для изменения цвета нажатой кнопки
        self.buttons.append(self.print_button)
        self.buttons.append(self.plan_button)
        self.buttons.append(self.profile_button)
        self.buttons.append(self.results_button)
        self.buttons.append(self.settings_button)
        self.buttons.append(self.save_button)
        self.buttons.append(self.escape_button)
        self.buttons.append(self.level_button)
        #
        vbox.addWidget(groupbox_top)
        vbox.addStretch(1)
        vbox.addWidget(self.results_button)
        vbox.addStretch(1)
        vbox.addWidget(self.settings_button)
        vbox.addStretch(1)
        vbox.addWidget(self.print_button)
        vbox.addStretch(5)
        vbox.addWidget(self.save_button)
        vbox.addWidget(self.escape_button)
        #vbox.addStretch(5)
        vbox.addWidget(groupbox_left_bottom)
        self.setLayout(vbox)


    # ============================ Меняем цвет бирюлек и окно на график ===============================================
    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        if key == Qt.Key_Z:
            self.pixmap1 = QPixmap('Data/yellow_narrow1')
            self.img1.setPixmap(self.pixmap1)
            self.plan_red = False
            self.plan_yellow = True
            self.plan_green = False
            print('Z')
        elif key == Qt.Key_X:
            self.pixmap1 = QPixmap('Data/red_narrow1')
            self.img1.setPixmap(self.pixmap1)
            self.plan_red = True
            self.plan_yellow = False
            self.plan_green = False
            print('Key_X ')
        elif key == Qt.Key_C:
            self.pixmap1 = QPixmap('Data/green_narrow1')
            self.img1.setPixmap(self.pixmap1)
            self.plan_red = False
            self.plan_yellow = False
            self.plan_green = True
            print('Key_C ')
        #if key == Qt.Key_V:
            #print('Key_V ')



    # ======================= Окраска нажатой кнопки ==================================
    def __plan_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __level_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __profile_button(self):
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

    def __print_button(self):
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

    def __save_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    lcw = LeftColumnWidget()
    lcw.show()
    sys.exit(app.exec())