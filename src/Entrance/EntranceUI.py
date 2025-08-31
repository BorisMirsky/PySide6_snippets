from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import csv
import pandas as pd
import random
from Main import MyWidget
#import qt_material



class MainClass(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.resize(300, 500)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        button_style = "padding :5px; border: 2px solid #8f8f91;border-radius: 6px;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);"
        btn1 = QPushButton("Выправка \n (Программное Задание)")
        btn1.clicked.connect(self.btn1Clicked)
        btn1.setStyleSheet(button_style)
        btn2 = QPushButton("Настройки")
        btn2.setStyleSheet(button_style)
        btn3 = QPushButton("Съёмка")
        btn3.setStyleSheet(button_style)
        btn4 = QPushButton("Расчёт")
        btn4.setStyleSheet(button_style)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
        self.setLayout(layout)

    def btn1Clicked(self):
        fpath, _ = QFileDialog.getOpenFileName(self,f'Open .csv file',"./", f'*.csv')
        self.widget = MyWidget(fpath)
        if fpath:
            self.widget.show()
            #self.close()



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    #qt_material.apply_stylesheet(app, theme='dark_teal.xml')
    gallery = MainClass()
    gallery.show()
    sys.exit(app.exec())