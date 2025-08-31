import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import * 
from PySide6.QtGui import *


class Window1(QWidget):
    def __init__(self):
        super().__init__()
        self.w2 = Window2()
        self.btn = QPushButton('open Window2')    
        self.btn.clicked.connect(self.__openWindow)     
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn)
        self.setLayout(vbox)

    def __openWindow(self):
        self.w2.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            print("QQQ")
        elif event.key() == Qt.Key_W:
            print("WWW")
        #event.accept() 
    
class Window2(QWidget):
    def __init__(self):
        super().__init__()
        self.w3 = Window3()
        self.btn = QPushButton('open Window3')    
        self.btn.clicked.connect(self.__openWindow)       
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn)
        self.setLayout(vbox)

    def __openWindow(self):
        self.w3.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            print("AAA")
        elif event.key() == Qt.Key_S:
            print("SSS")


class Window3(QWidget):
    def __init__(self):
        super().__init__()
        #self.w3 = Window2()
        self.btn = QPushButton('fuck off')    
        self.btn.clicked.connect(self.__openWindow)       
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn)
        self.setLayout(vbox)

    def __openWindow(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_D:
            print("DDD")
        elif event.key() == Qt.Key_F:
            print("FFF")


            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window1()
    window.show()
    sys.exit(app.exec())
