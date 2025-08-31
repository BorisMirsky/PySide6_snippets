from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import sys
import numpy as np
import pandas as pd


class Check(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Check Window")
        self.textbox1 = QLineEdit(self)
        self.textbox1.setGeometry(100, 100, 300, 30)
        self.textbox2 = QLineEdit(self)
        self.textbox2.setGeometry(100, 150, 300, 30)
        self.textbox3 = QLineEdit(self)
        self.textbox3.setGeometry(100, 200, 300, 30)

        self.lbox1 = QListWidget()
        self.lbox2 = QListWidget(self)
        self.lbox2.setGeometry(100, 250, 300, 500)
        self.textbox1.setObjectName("textbox1")
        self.textbox2.setObjectName("textbox2")
        self.textbox3.setObjectName("textbox3")

        QApplication.instance().focusChanged.connect(self.on_focusChanged)

    def on_focusChanged(self):
        fwidget = QApplication.focusWidget()
        if fwidget is not None:
            print("focus widget name ", fwidget.objectName())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Check()
    window.show()
    sys.exit(app.exec())