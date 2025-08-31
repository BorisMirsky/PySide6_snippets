import sys
from PySide6.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QPushButton, QWidget,
                             QStackedLayout, QListWidget,QLineEdit,
                             QVBoxLayout, QStackedWidget,QHBoxLayout,QTextEdit,
                             QGridLayout)
from PySide6.QtCore import *



# class Main(QWidget):
#     def __init__(self, parent=None):
#         super(Main, self).__init__(parent)
#         self.resize(400,400)
#         w1 = Window1()
#         w2 = Window2()
#         w3 = Window3()
#         m = Main()
#         stacked_layout = QStackedLayout()
#         stacked_layout.addWidget(m)
#         stacked_layout.addWidget(w1)
#         stacked_layout.addWidget(w2)
#         stacked_layout.addWidget(w3)
#         self.setLayout(stacked_layout)



class Start(QStackedWidget):
    def __init__(self, parent=None):
        super(Start, self).__init__(parent)
        self.resize(400,400)
        self.stacked_layout = QStackedLayout()
        btn1 = QPushButton("to Window1")
        btn1.clicked.connect(self.__handleBtn1)
        btn2 = QPushButton("to Window2")
        btn2.clicked.connect(self.__handleBtn2)
        btn3 = QPushButton("to Window3")
        btn3.clicked.connect(self.__handleBtn3)
        widg = QWidget()
        vbox = QVBoxLayout()
        widg.setLayout(vbox)
        vbox.addLayout(self.stacked_layout)
        w1 = Window1()
        w2 = Window2()
        w3 = Window3()
        vbox.addWidget(btn1)
        vbox.addWidget(btn2)
        vbox.addWidget(btn3)
        print("666666")
        self.stacked_layout.addWidget(widg)
        self.stacked_layout.addWidget(w1)
        self.stacked_layout.addWidget(w2)
        self.stacked_layout.addWidget(w3)
        self.setLayout(self.stacked_layout)
    def __handleBtn1(self):
        pass
        #self.vbox.addLayout(self.stacked_layout)
        self.stacked_layout.setCurrentIndex(1)
    def __handleBtn2(self):
        pass
        #self.vbox.addLayout(self.stacked_layout)
        self.stacked_layout.setCurrentIndex(2)
    def __handleBtn3(self):
        pass
        #self.vbox.addLayout(self.stacked_layout)
        self.stacked_layout.setCurrentIndex(3)


class Window1(QWidget):
    def __init__(self, parent=None):
        super(Window1, self).__init__(parent)
        self.resize(400,400)
        lbl = QLabel("label1", alignment=Qt.AlignCenter)
        vbox = QVBoxLayout()
        lbl.setStyleSheet("font-size: 18pt;background-color:green;")
        vbox.addWidget(lbl)
        self.setLayout(vbox)

class Window2(QWidget):
    def __init__(self, parent=None):
        super(Window2, self).__init__(parent)
        self.resize(400,400)
        lbl = QLabel("label2", alignment=Qt.AlignCenter)
        vbox = QVBoxLayout()
        lbl.setStyleSheet("font-size: 18pt;background-color:red;")
        vbox.addWidget(lbl)
        self.setLayout(vbox)

class Window3(QWidget):
    def __init__(self, parent=None):
        super(Window3, self).__init__(parent)
        self.resize(400,400)
        lbl = QLabel("label3", alignment=Qt.AlignCenter)
        vbox = QVBoxLayout()
        lbl.setStyleSheet("font-size: 18pt;background-color:cyan;")
        vbox.addWidget(lbl)
        self.setLayout(vbox)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = Start()
    m.show()
    sys.exit(app.exec())

