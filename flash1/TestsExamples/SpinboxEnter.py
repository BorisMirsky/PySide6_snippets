from PySide6.QtWidgets import *
from PySide6 import QtCore, QtGui
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 400)
        self.spin = QSpinBox(self)
        self.spin.setGeometry(100, 100, 250, 40)
        #self.spin.setPrefix("Prefix ")
        #self.spin.setSuffix(" Suffix")
        self.label = QLabel("Label ", self)
        self.label.setGeometry(100, 150, 300, 70)
        self.spin.editingFinished.connect(self.do_action)

    def do_action(self):
        current = self.spin.value()
        print(current)
        #self.label.setText("Editing finished, final value : " + str(current))


App = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(App.exec())