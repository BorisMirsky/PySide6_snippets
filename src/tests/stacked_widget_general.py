import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import * 
from PySide6.QtGui import *


class Center1(QWidget):
    def __init__(self):
        super().__init__()

    def center(self):
        label = QLabel("1_Label_1")
        return label
        
class Center2(QWidget):
    def __init__(self):
        super().__init__()

    def center(self):
        label = QLabel("2_Label_2")
        return label

class CenterDefault(QWidget):
    def __init__(self):
        super().__init__()

    def center(self):
        label = QLabel("CenterDefaultLabel")
        return label


    
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.centerDef = CenterDefault()
        self.center1 = Center1()
        self.center2 = Center2()
        
        self.setWindowTitle("QGridLayout Example")
        self.layout = QGridLayout()

        self.btn1 = QPushButton("Button1", self)
        self.btn2 = QPushButton("Button2", self)
        self.btn1.clicked.connect(self.buttonClicked)
        self.btn2.clicked.connect(self.buttonClicked)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.centerDef.center())
        self.stacked_widget.addWidget(self.center1.center()) #.center())
        self.stacked_widget.addWidget(self.center2.center())  #.center())
        
        self.layout.addWidget(self.top_group(), 0, 0, 1, 2)
        self.layout.addWidget(self.bottom_left(), 1, 0)
        self.layout.addWidget(self.bottom_right(), 1, 1)
        self.layout.addWidget(self.stacked_widget, 2, 0, 1, 2)
        self.setLayout(self.layout)
        self.setGeometry(100, 100, 300, 300)

    def buttonClicked(self):
        sender = self.sender()
        if sender.text() == "Button1":
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.stacked_widget.setCurrentIndex(2)
        
    def top_group(self):
        return QPushButton("Button Spans two Cols")

    def bottom_left(self):
        return self.btn1 #QPushButton("Button bottom left")

    def bottom_right(self):
        return self.btn2  #QPushButton("Button bottom right")

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
