#from Charts import ChartClass
from ChartsRaschetPlana import ChartClass
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class AlignDelegate(QStyledItemDelegate):     
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter
        

class MyWidget(QWidget):
    def __init__(self, datafile):     #, parent=None):
        super().__init__()
        self.datafile = datafile
        self.initUI()

    def initUI(self):
        self.createTopWidget()
        self.createLeftWidget()
        self.createCenterWidget()
        self.createLeftBottomWidget()
        mainLayout = QGridLayout()
        mainLayout.addLayout(self.topLayout, 0, 0, 1, 10)
        mainLayout.addLayout(self.leftLayout, 1, 0, 2, 1)            #1,0,2,2
        mainLayout.addLayout(self.centerLayout, 1, 1, 3, 10)         # 1,2,3,10
        mainLayout.addLayout(self.leftBottomLayout, 2, 0, 3, 2)      # 2,0,3,2
        mainLayout.setColumnStretch(10, 1)
        mainLayout.setSpacing(1)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setRowStretch(1, 1)
        self.setLayout(mainLayout)
        self.setGeometry(100, 100, 1200, 1000)     # 1920*1024
        self.setWindowTitle("Расчёт плана, продольного и поперечного профиля")
        self.sshFile="darkorange.stylesheet"   # Внешний файл с таблицей стилей взят здесь:
        with open(self.sshFile,"r") as fh:               # http://www.yasinuludag.com/darkorange.stylesheet
            self.setStyleSheet(fh.read())


    def createTopWidget(self) :
        label_1_1 = QLabel("Перегон")
        label_1_2 = QLabel("Путь")
        label_1_3 = QLabel("Машина")
        lineEdit_1_1 = QLineEdit()
        lineEdit_1_1.setFixedWidth(600)
        lineEdit_1_2 = QLineEdit()
        lineEdit_1_2.setFixedWidth(50)
        lineEdit_1_3 = QLineEdit()
        lineEdit_1_3.setFixedWidth(200)
        label_2_1 = QLabel("Начало")
        label_2_2 = QLabel("КМ+")
        label_2_3 = QLabel("М")
        label_2_4 = QLabel("Длина")
        label_2_5 = QLabel("М")
        label_2_6 = QLabel("Конец")
        label_2_7 = QLabel("КМ+")
        label_2_8 = QLabel("М")
        label_2_9 = QLabel("Дата")
        label_2_10 = QLabel("Прижим")
        lineEdit_2_1 = QLineEdit()
        lineEdit_2_1.setFixedWidth(30)
        lineEdit_2_2 = QLineEdit()
        lineEdit_2_2.setFixedWidth(30)
        lineEdit_2_3 = QLineEdit()
        lineEdit_2_3.setFixedWidth(60)
        lineEdit_2_4 = QLineEdit()
        lineEdit_2_4.setFixedWidth(30)
        lineEdit_2_5 = QLineEdit()
        lineEdit_2_5.setFixedWidth(60)
        lineEdit_2_6 = QLineEdit()
        lineEdit_2_6.setFixedWidth(100)
        lineEdit_2_7 = QLineEdit()
        lineEdit_2_7.setFixedWidth(60)          
        topHLayout_1 = QHBoxLayout()
        topHLayout_1.addWidget(label_1_1)
        topHLayout_1.addWidget(lineEdit_1_1)
        topHLayout_1.addWidget(label_1_2)
        topHLayout_1.addWidget(lineEdit_1_2)
        topHLayout_1.addWidget(label_1_3)
        topHLayout_1.addWidget(lineEdit_1_3)        
        topHLayout_2 = QHBoxLayout()
        topHLayout_2.addWidget(label_2_1)
        topHLayout_2.addWidget(lineEdit_2_1)
        topHLayout_2.addWidget(label_2_2)
        topHLayout_2.addWidget(lineEdit_2_2)
        topHLayout_2.addWidget(label_2_3)
        topHLayout_2.addStretch(1) 
        topHLayout_2.addWidget(label_2_4)
        topHLayout_2.addWidget(lineEdit_2_3)
        topHLayout_2.addWidget(label_2_5)
        topHLayout_2.addStretch(1) 
        topHLayout_2.addWidget(label_2_6)
        topHLayout_2.addWidget(lineEdit_2_4)
        topHLayout_2.addWidget(label_2_7)
        topHLayout_2.addWidget(lineEdit_2_5)
        topHLayout_2.addWidget(label_2_8)    
        topHLayout_2.addWidget(label_2_9)
        topHLayout_2.addWidget(lineEdit_2_6)
        topHLayout_2.addWidget(label_2_10)
        topHLayout_2.addWidget(lineEdit_2_7)        
        self.topLayout = QVBoxLayout()
        self.topLayout.addLayout(topHLayout_1)
        self.topLayout.addLayout(topHLayout_2)


    def createLeftWidget(self):
        self.leftLayout = QVBoxLayout()        
        button1 = QPushButton("План")
        button2 = QPushButton("Уровень")
        button3 = QPushButton("Профиль")
        groupbox = QGroupBox("Редактирование")
        vbox1 = QVBoxLayout()
        vbox1.addWidget(button1)
        vbox1.addWidget(button2)
        vbox1.addWidget(button3)
        groupbox.setLayout(vbox1)
        self.leftLayout.addWidget(groupbox)        
        button4 = QPushButton("Результаты")
        button5 = QPushButton("Установки")
        button6 = QPushButton("Печать")
        button7 = QPushButton("Выход (ESC)")
        self.leftLayout.addStretch(1)
        self.leftLayout.addWidget(button4)
        self.leftLayout.addStretch(1)
        self.leftLayout.addWidget(button5)
        self.leftLayout.addStretch(1)
        self.leftLayout.addWidget(button6)
        self.leftLayout.addStretch(3)
        self.leftLayout.addWidget(button7)
        self.leftLayout.addStretch(1)


    def createLeftBottomWidget(self):
        label1 = QLabel("Пикетаж")
        label1.setFixedWidth(50)
        label2 = QLabel("КМ")
        label3 = QLabel("М")
        label4 = QLabel("Масштаб")
        lineEdit1 = QLineEdit()
        lineEdit2 = QLineEdit()
        lineEdit3 = QLineEdit()
        lineEdit1.setFixedWidth(50)
        lineEdit2.setFixedWidth(50)
        lineEdit3.setFixedWidth(50)
        self.leftBottomLayout = QVBoxLayout()
        HLayout1 = QHBoxLayout()
        HLayout2 = QHBoxLayout()
        HLayout1.addWidget(lineEdit1)
        HLayout1.addWidget(label2)
        HLayout1.addWidget(lineEdit2)
        HLayout1.addWidget(label3)
        HLayout1.addStretch(1)
        HLayout2.addWidget(label4)
        HLayout2.addWidget(lineEdit3)
        HLayout2.addStretch(1)
        self.leftBottomLayout.addWidget(label1)
        self.leftBottomLayout.addLayout(HLayout1)
        self.leftBottomLayout.addLayout(HLayout2)
        #self.leftBottomLayout.setContentsMargins(5, 5, 5, 5)


    def createCenterWidget(self):
        chart1 = ChartClass(self.datafile, 1)
        #chart1.setTitle("План")
        #chart1.setTitleFont(QFont('Impact', 20, QFont.Bold))  # QFont.italic))
        chart2 = ChartClass(self.datafile, 2)
        #chart2.setTitle("Уровень")
        #chart2.setTitleFont(QFont('Impact', 20, QFont.Bold))  # QFont.italic))
        chart3 = ChartClass(self.datafile, 3)
        #chart3.setTitle("Профиль")
        #chart3.setTitleFont(QFont('Impact', 20, QFont.Bold))  # QFont.italic))
        chart4 = ChartClass(self.datafile, 4)
        chart5 = ChartClass(self.datafile, 5)
        self.centerLayout = QVBoxLayout()
        self.centerLayout.addWidget(chart1)
        self.centerLayout.addWidget(chart2)
        self.centerLayout.addWidget(chart3)
        self.centerLayout.addWidget(chart4)
        self.centerLayout.addWidget(chart5)

        self.__charts = [chart1, chart2, chart3, chart4, chart5]
        
    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_D:
            self.move_line(1)
        if event.key() == Qt.Key.Key_A:
            self.move_line(-1)

    def move_line(self, xDiff: float):
        for chart in self.__charts:
            chart.move_line(xDiff)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet('.QPushButton { font-size: 12pt;}')
    #app.setStyleSheet('.QLabel { font-size: 12pt;}')
    gallery = MyWidget("example_csv_file.csv")
    gallery.show()
    sys.exit(app.exec())
