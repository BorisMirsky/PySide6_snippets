from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys 
  
class Window(QWidget): 
    def __init__(self): 
        super().__init__() 
        self.setWindowTitle("Tooltip") 
        self.setGeometry(0, 0, 300, 300) 
        widget1 = QPushButton('Widget1', self)
        widget2 = QPushButton('Widget2', self)
        widget3 = QPushButton('Widget3', self)
        #widget4 = QPushButton('Widget4', self)
        #widget5 = QPushButton('Widget5', self)
        widget1.setToolTip("This is a button widget1!")
        widget2.setToolTip("This is a button widget2!")
        widget3.setToolTip("This is a button widget3!")
        #widget4.setToolTip("This is a button widget4!") 
        #widget5.setToolTip("This is a button widget5!")
        label1 = QLabel("label1")
        label1.setToolTip("This is a button label1!")
        hbox = QHBoxLayout()
        hbox.addWidget(widget1)
        hbox.addWidget(label1)
        hbox.addWidget(widget2)
        hbox.addWidget(widget3)
        #hbox.addWidget(widget4)
        #hbox.addWidget(widget5)
        self.setLayout(hbox)
        self.show() 
  

App = QApplication(sys.argv) 
window = Window() 
sys.exit(App.exec()) 
