from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton, QLabel, QHBoxLayout, QStackedLayout
from PySide6.QtCore import *
import sys

class First(QWidget):
    signalChangeLayout1 = Signal(str)
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        lbl = QLabel("class First")
        btn = QPushButton("first btn")
        btn.clicked.connect(self.handleBtnFirst)
        widget = QWidget()
        vbox = QVBoxLayout()
        widget.setLayout(vbox)
        vbox.addWidget(lbl)
        vbox.addWidget(btn)
        self.setLayout(vbox)

    def handleBtnFirst(self):
        self.signalChangeLayout1.emit("go!")
        print("signalChangeLayout1")


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        lbl = QLabel("class Main")
        btn = QPushButton("main btn")
        btn.clicked.connect(self.__handleBtnMain)
        self.first = First()
        self.first.signalChangeLayout1.connect(self.change_layout_1_to_2)
        widget = QWidget()
        vbox = QVBoxLayout()
        widget.setLayout(vbox)
        vbox.addWidget(lbl)
        vbox.addWidget(btn)
        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(widget)
        self.stackedLayout.addWidget(self.first)
        self.setLayout(self.stackedLayout)

    def change_layout_1_to_2(self):
        print("change_layout_1_to_2")
        self.setWindowTitle("change_layout_1_to_2")
        self.stackedLayout.setCurrentIndex(0)

    def __handleBtnMain(self):
        print("__handleBtnMain")
        self.setWindowTitle("change_layout_2_to_1")
        self.stackedLayout.setCurrentIndex(1)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())