from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *



class Widget1(QDialog):
    def __init__(self, parent=None):
        super(Widget1, self).__init__(parent)

        self.createTopWidget()
        self.createLeftWidget()
        self.createCenterWidget()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.topVLayout, 0, 0, 1, 7)
        mainLayout.addLayout(self.leftLayout, 1, 0)
        mainLayout.addLayout(self.centerLayout, 1, 1, 2, 7)
        self.setLayout(mainLayout)
        self.setGeometry(100, 100, 1000, 700)
        

    def createTopWidget(self) :
        label1 = QLabel("label1")
        label2 = QLabel("label2")
        label3 = QLabel("label3")
        label4 = QLabel("label4")
        label5 = QLabel("label5")
        label6 = QLabel("label6")
        label7 = QLabel("label7")
        label8 = QLabel("label8")
        label9 = QLabel("label9")
        lineEdit1 = QLineEdit()
        lineEdit1.setFixedWidth(200)
        lineEdit2 = QLineEdit()
        lineEdit2.setFixedWidth(50)
        lineEdit3 = QLineEdit()
        lineEdit3.setFixedWidth(200)
        lineEdit4 = QLineEdit()
        lineEdit4.setFixedWidth(30)
        lineEdit5 = QLineEdit()
        lineEdit5.setFixedWidth(30)
        lineEdit6 = QLineEdit()
        lineEdit6.setFixedWidth(60)
        lineEdit7 = QLineEdit()
        lineEdit7.setFixedWidth(30)
          
        topHLayout_1 = QHBoxLayout()
        topHLayout_1.addWidget(label1)
        topHLayout_1.addWidget(lineEdit1)
        topHLayout_1.addWidget(label2)
        topHLayout_1.addWidget(lineEdit2)
        topHLayout_1.addWidget(label3)
        topHLayout_1.addWidget(lineEdit3)
        
        topHLayout_2 = QHBoxLayout()
        topHLayout_2.addWidget(label4)
        topHLayout_2.addWidget(lineEdit4)
        topHLayout_2.addWidget(label5)
        topHLayout_2.addWidget(lineEdit5)
        topHLayout_2.addWidget(label6)
        topHLayout_2.addWidget(label7)
        topHLayout_2.addWidget(lineEdit6)
        topHLayout_2.addWidget(label7)
        topHLayout_2.addWidget(label8)    
        topHLayout_2.addWidget(label9)
        topHLayout_2.addWidget(lineEdit7)
        
        self.topVLayout = QVBoxLayout()
        self.topVLayout.addLayout(topHLayout_1)
        self.topVLayout.addLayout(topHLayout_2)


    def createLeftWidget(self):
        self.leftLayout = QVBoxLayout()
        
        button1 = QPushButton("btn1")
        button2 = QPushButton("btn2")
        button3 = QPushButton("btn3")
        groupbox = QGroupBox("groupBox")
        vbox1 = QVBoxLayout()
        vbox1.addWidget(button1)
        vbox1.addWidget(button2)
        vbox1.addWidget(button3)
        groupbox.setLayout(vbox1)
        self.leftLayout.addWidget(groupbox)
        
        button4 = QPushButton("btn4")
        button5 = QPushButton("btn5")
        button6 = QPushButton("btn6")
        button7 = QPushButton("btn7")
        self.leftLayout.addWidget(button4)
        self.leftLayout.addWidget(button5)
        self.leftLayout.addWidget(button6)
        self.leftLayout.addWidget(button7)


    def createCenterWidget(self):
        self.centerLayout = QVBoxLayout()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Widget1()
    w.show()
    sys.exit(app.exec())
