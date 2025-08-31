import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import * 
from PySide6.QtGui import *

########################## 1 #######################
class Stackedlayout1(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QStackedLayout(self)
        w1 = Widget1()
        w2 = Widget2()
        w3 = Widget3()
        w1.openWidget2Signal.connect(self.openW2)
        w1.openWidget3Signal.connect(self.openW3)
        w2.closeThisWidgetSignal.connect(self.closeW2)
        w3.closeThisWidgetSignal.connect(self.closeW3)
        self.layout.addWidget(w1)
        self.layout.addWidget(w2)
        self.layout.addWidget(w3)
        self.setLayout(self.layout)

    def openW2(self):
        self.layout.setCurrentIndex(1)

    def openW3(self):
        self.layout.setCurrentIndex(2)

    def closeW2(self):
        self.layout.setCurrentIndex(0)

    def closeW3(self):
        self.layout.setCurrentIndex(0)
        

class Widget1(QWidget):
    openWidget2Signal = Signal(str)
    openWidget3Signal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: yellow;")
        btn1 = QPushButton("open Widget2")
        btn1.clicked.connect(self.openWidget2)
        btn2 = QPushButton("open Widget3")
        btn2.clicked.connect(self.openWidget3)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        vbox.addWidget(btn2)
        self.setLayout(vbox)

    def openWidget2(self):
        self.openWidget2Signal.emit('open')

    def openWidget3(self):
        self.openWidget3Signal.emit('open')


        
class Widget2(QWidget):
    closeThisWidgetSignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: red;")
        btn1 = QPushButton("close")
        btn1.clicked.connect(self.closeWidget)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        #vbox.addWidget(btn2)
        self.setLayout(vbox)

    def closeWidget(self):
        self.closeThisWidgetSignal.emit('close')


class Widget3(QWidget):
    closeThisWidgetSignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: magenta;")
        btn1 = QPushButton("close")
        btn1.clicked.connect(self.closeWidget)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        #vbox.addWidget(btn2)
        self.setLayout(vbox)

    def closeWidget(self):
        self.closeThisWidgetSignal.emit('close')


###############

class Stackedlayout2(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QStackedLayout(self)
        w4 = Widget4()
        w5 = Widget5()
        w6 = Widget6()
        w4.openWidget5Signal.connect(self.openW4)
        w4.openWidget6Signal.connect(self.openW5)
        w5.closeThisWidgetSignal.connect(self.closeW4)
        w6.closeThisWidgetSignal.connect(self.closeW5)
        self.layout.addWidget(w4)
        self.layout.addWidget(w5)
        self.layout.addWidget(w6)
        self.setLayout(self.layout)

    def openW4(self):
        self.layout.setCurrentIndex(1)

    def openW5(self):
        self.layout.setCurrentIndex(2)

    def closeW4(self):
        self.layout.setCurrentIndex(0)

    def closeW5(self):
        self.layout.setCurrentIndex(0)
        

class Widget4(QWidget):
    openWidget5Signal = Signal(str)
    openWidget6Signal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: green;")
        btn1 = QPushButton("open Widget5")
        btn1.clicked.connect(self.openWidget5)
        btn2 = QPushButton("open Widget6")
        btn2.clicked.connect(self.openWidget6)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        vbox.addWidget(btn2)
        self.setLayout(vbox)

    def openWidget5(self):
        self.openWidget5Signal.emit('open')

    def openWidget6(self):
        self.openWidget6Signal.emit('open')


        
class Widget5(QWidget):
    closeThisWidgetSignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: blue;")
        btn1 = QPushButton("close")
        btn1.clicked.connect(self.closeWidget)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        #vbox.addWidget(btn2)
        self.setLayout(vbox)

    def closeWidget(self):
        self.closeThisWidgetSignal.emit('close')


class Widget6(QWidget):
    closeThisWidgetSignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: cyan;")
        btn1 = QPushButton("close")
        btn1.clicked.connect(self.closeWidget)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        #vbox.addWidget(btn2)
        self.setLayout(vbox)

    def closeWidget(self):
        self.closeThisWidgetSignal.emit('close')

#####################################################################

class Stackedlayout3(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QStackedLayout(self)
        w7 = Widget7()
        StL1 = Stackedlayout1()
        StL2 = Stackedlayout2()
        w4.openWidget5Signal.connect(self.openW4)
        w4.openWidget6Signal.connect(self.openW5)
        w5.closeThisWidgetSignal.connect(self.closeW4)
        w6.closeThisWidgetSignal.connect(self.closeW5)
        self.layout.addWidget(w4)
        self.layout.addWidget(w5)
        self.layout.addWidget(w6)
        self.setLayout(self.layout)

    def openW4(self):
        self.layout.setCurrentIndex(1)

    def openW5(self):
        self.layout.setCurrentIndex(2)

    def closeW4(self):
        self.layout.setCurrentIndex(0)

    def closeW5(self):
        self.layout.setCurrentIndex(0)


class Widget7(QWidget):
    closeThisWidgetSignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: cyan;")
        btn1 = QPushButton("close")
        btn1.clicked.connect(self.closeWidget)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        #vbox.addWidget(btn2)
        self.setLayout(vbox)

    def closeWidget(self):
        self.closeThisWidgetSignal.emit('close')


        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Stackedlayout2()
    window.show()
    sys.exit(app.exec())
