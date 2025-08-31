from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from Charts import ClassCharts 
from Info import ClassInfo
from OneChart import Chart
from Plan1 import Plan1Class
from Plan2 import Plan2Class
from Skorostej import SkorostejClass



class Widget(QWidget): 
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.buttonsList = []               
        self.createTopWidget()
        self.createStackedWidget()
        self.createBottomWidget()
        mainLayout = QGridLayout()
        mainLayout.addLayout(self.topLayout, 0, 0)
        mainLayout.addLayout(self.centerLayout, 1, 0, 7, 0)
        mainLayout.addLayout(self.bottomLayout, 6, 0)   
        self.setLayout(mainLayout)
        self.setGeometry(100, 100, 1200, 900)
        self.setWindowTitle("Таблицы результатов")
        
    def createTopWidget(self) :
        self.btn1 = QPushButton("Инфо")
        self.btn1.setFixedSize(QSize(60, 25))
        self.btn2 = QPushButton("Скоростей")
        self.btn2.setFixedSize(QSize(80, 25))
        self.btn3 = QPushButton("Динамический")
        self.btn3.setFixedSize(QSize(100, 25))
        self.btn4 = QPushButton("План1")
        self.btn4.setFixedSize(QSize(70, 25))
        self.btn6 = QPushButton("План2")
        self.btn6.setFixedSize(QSize(70, 25))
        self.btn1.clicked.connect(self.buttonClicked)
        self.btn2.clicked.connect(self.buttonClicked)
        self.btn3.clicked.connect(self.buttonClicked)
        self.btn4.clicked.connect(self.buttonClicked)
        self.btn6.clicked.connect(self.buttonClicked)
        self.buttonsList.append(self.btn1)
        self.buttonsList.append(self.btn2)
        self.buttonsList.append(self.btn3)
        self.buttonsList.append(self.btn4)
        self.buttonsList.append(self.btn6)
        btn5 = QPushButton("Профиль")
        btn5.setFixedSize(QSize(70, 25))
        btn7 = QPushButton("Уровень")
        btn7.setFixedSize(QSize(70, 25))
        btn8 = QPushButton("Профиль")
        btn8.setFixedSize(QSize(70, 25))
        btn9 = QPushButton("Балласт")
        btn9.setFixedSize(QSize(70, 25))
        groupbox1 = QGroupBox("Анализ")
        groupbox2 = QGroupBox("Проектные параметры")
        groupbox3 = QGroupBox("Разбивочные данные")
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()

        hbox1.addWidget(self.btn2)
        hbox1.addWidget(self.btn3)
        groupbox1.setLayout(hbox1)
        hbox1.addStretch()
        hbox2.addWidget(self.btn4)
        hbox2.addWidget(btn5)
        groupbox2.setLayout(hbox2)
        hbox2.addStretch()
        hbox3.addWidget(self.btn6)
        hbox3.addWidget(btn7)
        hbox3.addWidget(btn8)
        groupbox3.setLayout(hbox3)
        hbox3.addStretch()

        HBoxLayout1 = QHBoxLayout()
        HBoxLayout1.addWidget(self.btn1)
        HBoxLayout1.addWidget(groupbox1)
        HBoxLayout1.addWidget(groupbox2)
        HBoxLayout1.addWidget(groupbox3)
        HBoxLayout1.addWidget(btn9)

        HBoxLayout2 = QHBoxLayout()
        lineEdit = QLineEdit()
        lineEdit.setFixedWidth(1200)
        HBoxLayout2.addWidget(lineEdit)

        HBoxLayout3 = QHBoxLayout()
        label1 = QLabel("28.6.2000")
        label2 = QLabel("Анализ допускаемых скоростей")
        label3 = QLabel("Таблица 2.1")   
        HBoxLayout3.addWidget(label1)
        HBoxLayout3.addStretch(1)
        HBoxLayout3.addWidget(label2)
        HBoxLayout3.addStretch(1)
        HBoxLayout3.addWidget(label3)
       
        self.topLayout = QVBoxLayout()
        self.topLayout.addLayout(HBoxLayout1)
        self.topLayout.addLayout(HBoxLayout2)
        self.topLayout.addLayout(HBoxLayout3)

    def createStackedWidget(self):
        placeholder_label = QLabel(" ")
        self.stacked_widget = QStackedWidget()   
        tbl = SkorostejClass() 
        info = ClassInfo()
        charts = ClassCharts()
        plan1 = Plan1Class()
        plan2 = Plan2Class()
        self.stacked_widget.addWidget(placeholder_label)
        self.stacked_widget.addWidget(tbl) 
        self.stacked_widget.addWidget(charts) 
        self.stacked_widget.addWidget(info)
        self.stacked_widget.addWidget(plan1)
        self.stacked_widget.addWidget(plan2)
        self.centerLayout = QVBoxLayout()
        self.centerLayout.addWidget(self.stacked_widget)

    def createBottomWidget(self):
        chart = Chart() 
        chart.setFixedHeight(200)
        self.bottomLayout = QVBoxLayout()
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(chart)

    def buttonClicked(self):
        sender = self.sender()
        for btn in self.buttonsList:
            if btn is sender:
                if sender.text() == "Скоростей":
                    self.stacked_widget.setCurrentIndex(1)
                    btn.setStyleSheet("background-color : blue; color: white;")
                elif sender.text() == "Динамический":
                    self.stacked_widget.setCurrentIndex(2)
                    btn.setStyleSheet("background-color : blue; color: white;")
                elif sender.text() == "Инфо":
                    self.stacked_widget.setCurrentIndex(3)
                    btn.setStyleSheet("background-color : blue; color: white;")
                elif sender.text() == "План1":
                    self.stacked_widget.setCurrentIndex(4)
                    btn.setStyleSheet("background-color : blue; color: white;")
                elif sender.text() == "План2":
                    self.stacked_widget.setCurrentIndex(5)
                    btn.setStyleSheet("background-color : blue; color: white;")
            else:
                btn.setStyleSheet("")  


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = Widget()
    gallery.show()
    sys.exit(app.exec())
