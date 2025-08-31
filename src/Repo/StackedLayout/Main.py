from PySide6.QtWidgets import (QWidget, QLabel,  QVBoxLayout,
                               QApplication, QHBoxLayout,
                               QStackedWidget, QPushButton)
from PySide6.QtGui import QFont, Qt, QPen,QColor
from PySide6.QtCore import Qt, QObject, QCoreApplication, Signal
import sys


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.button = QPushButton('Test')
        self.button.clicked.connect(self.handleButton)
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def handleButton(self):
        print('Hello World')


		
def main():
   app = QApplication(sys.argv)
   ex = Main()
   ex.show()
   sys.exit(app.exec())

