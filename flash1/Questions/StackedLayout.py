from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import *
import sys


class UpdateLabel(QWidget):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.btn = QPushButton("go")
        self.btn.clicked.connect(self.updateCounter)
        self.lblClass = QLabel("Это импортируемый класс")
        self.lbl = QLabel(str(self.counter))
        hbox = QHBoxLayout()
        hbox.addWidget(self.lblClass)
        hbox.addWidget(self.lbl)
        hbox.addWidget(self.btn)
        self.setLayout(hbox)

    def updateCounter(self):
        self.counter += 1
        self.lbl.setNum(self.counter)


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        self.importedCls = UpdateLabel()
        self.counter = self.importedCls.counter
        self.importedCls.btn.clicked.connect(self.updateCounter)
        self.lblTitle = QLabel("это внешний класс")
        self.lbl = QLabel(str(self.counter))
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.lblTitle)
        hbox.addWidget(self.lbl)
        vbox.addLayout(hbox)
        vbox.addWidget(self.importedCls)
        self.setLayout(vbox)

    def updateCounter(self):
        self.counter += 1
        self.lbl.setNum(self.counter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())