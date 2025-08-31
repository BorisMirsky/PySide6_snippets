from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys


class ClassInfo(QWidget):
    def __init__(self, parent=None):
        super(ClassInfo, self).__init__(parent)
        self.setStyleSheet("margin:10px; ") #border:1px solid rgb(0, 0, 0); ")
        self.createFirstWidget()
        self.createSecondWidget()
        mainLayout = QGridLayout()
        mainLayout.addLayout(self.firstWidget, 0, 0) #, Qt.AlignCenter)
        mainLayout.addLayout(self.secondWidget, 1, 0) #, Qt.AlignCenter)
        #mainLayout.setRowStretch(2, 2)                                
        #mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.resize(800, 500)

    def createFirstWidget(self):
        myFont=QFont()
        myFont.setBold(True)
        underline_text = "\u0332".join("1. Установка расчёта")
        label1 = QLabel(underline_text)
        label1.setFont(myFont)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label1, alignment=Qt.AlignCenter)
        hbox1.setSpacing(0)
        
        label2 = QLabel("1.1 Установленные скорости км/ч")
        label2.setFont(myFont)
        label3 = QLabel("1.2 Допускаемые сдвиги")
        label3.setFont(myFont)
        label4 = QLabel("Влево")
        label5 = QLabel("Вправо")
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label2)
        hbox2.addStretch(1) 
        hbox2.addWidget(label3)
        hbox2.addStretch(2) 
        hbox2.addWidget(label4)
        hbox2.addWidget(label5)
        hbox2.setSpacing(0)

        label6 = QLabel("Максим. пассажирских")
        lineEdit1 = QLineEdit()
        lineEdit1.setFixedWidth(70)
        textEdit = QTextEdit()
        textEdit.setMinimumHeight(50)
        textEdit.setMaximumHeight(150)
        textEdit.setMinimumWidth(150)
        textEdit.setMaximumWidth(200) 
        hbox3 = QHBoxLayout()
        hbox3.addWidget(label6)
        hbox3.addWidget(lineEdit1)
        hbox3.addStretch(4)
        hbox3.addWidget(textEdit)
        #hbox3.setSpacing(0)
        
        label7 = QLabel("Максим. грузовых")
        lineEdit7 = QLineEdit()
        lineEdit7.setFixedWidth(70)
        hbox4 = QHBoxLayout()
        hbox4.addWidget(label7)
        hbox4.addWidget(lineEdit7)
        hbox4.addStretch(3)
        #hbox4.setSpacing(0)

        self.firstWidget = QVBoxLayout()
        self.firstWidget.addLayout(hbox1)
        self.firstWidget.addLayout(hbox2)
        self.firstWidget.addLayout(hbox3)
        self.firstWidget.addLayout(hbox4)
        #self.firstWidget.setRowStretch(8, 2)                                
        #self.firstWidget.setSpacing(0)
        #self.firstWidget.setVerticalSpacing(0) 

        self.firstWidget.setContentsMargins(100, 100, 100, 0) #left, top, right, bottom
        

    def createSecondWidget(self):
        myFont=QFont()
        myFont.setBold(True)

        underline_text = "\u0332".join("2. Полученный результат")
        label1 = QLabel(underline_text)
        label1.setFont(myFont)
        hbox_1_1 = QHBoxLayout()
        hbox_1_1.addWidget(label1, alignment=Qt.AlignCenter)

        label2 = QLabel("Максимальный сдвиг")
        label3 = QLabel("Количество радиусов")
        lineEdit1 = QLineEdit()
        lineEdit1.setFixedWidth(70)
        hbox_1_2 = QHBoxLayout()
        hbox_1_2.addWidget(label2)
        hbox_1_2.addStretch(2)
        hbox_1_2.addWidget(label3)
        hbox_1_2.addWidget(lineEdit1)
        hbox_1_2.addStretch(2)

        label4 = QLabel("Влево")
        lineEdit2 = QLineEdit()
        lineEdit2.setFixedWidth(70)
        label5 = QLabel("Сумма сдвигов")
        lineEdit3 = QLineEdit()
        lineEdit3.setFixedWidth(70)
        hbox_1_3 = QHBoxLayout()
        hbox_1_3.addWidget(label4)
        hbox_1_3.addWidget(lineEdit2)
        hbox_1_3.addStretch(2)
        hbox_1_3.addStretch(3) 
        hbox_1_3.addWidget(label5)
        hbox_1_3.addWidget(lineEdit3)

        label6 = QLabel("Вправо")
        lineEdit4 = QLineEdit()
        lineEdit4.setFixedWidth(70)
        label7 = QLabel("Сумма модулей сдвигов")
        lineEdit5 = QLineEdit()
        lineEdit5.setFixedWidth(70)
        hbox_1_4 = QHBoxLayout()
        hbox_1_4.addWidget(label6)
        hbox_1_4.addWidget(lineEdit4)
        hbox_1_4.addStretch(4) 
        hbox_1_4.addWidget(label7)
        hbox_1_4.addWidget(lineEdit5)

        self.secondWidget = QVBoxLayout()
        self.secondWidget.addLayout(hbox_1_1)
        self.secondWidget.addLayout(hbox_1_2)
        self.secondWidget.addLayout(hbox_1_3)
        self.secondWidget.addLayout(hbox_1_4)

        self.secondWidget.setContentsMargins(100, 0, 100, 200)

        
    
#app = QApplication(sys.argv)
#cls = ClassInfo()
#cls.show()
#sys.exit(app.exec())
