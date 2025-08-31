from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton, QLabel, QHBoxLayout, QStackedLayout
from PySide6.QtCore import *
import sys

class First(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        lbl = QLabel("class First")
        btn = QPushButton("first btn")
        btn.clicked.connect(self.handleBtn)
        widget = QWidget()
        vbox = QVBoxLayout()
        widget.setLayout(vbox)
        vbox.addWidget(lbl)
        vbox.addWidget(btn)
        self.setLayout(vbox)

    def handleBtn(self):
        print("___666___")


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        lbl = QLabel("class Main")
        btn = QPushButton("main btn")
        btn.clicked.connect(self.__handleBtn)
        self.first = First()
        widget = QWidget()
        vbox = QVBoxLayout()
        widget.setLayout(vbox)
        vbox.addWidget(lbl)
        vbox.addWidget(btn)
        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(widget)
        self.stackedLayout.addWidget(self.first)
        self.setLayout(self.stackedLayout)

    def __handleBtn(self):
        #self.stackedLayout.addWidget(self.first)
        self.stackedLayout.setCurrentIndex(1)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())