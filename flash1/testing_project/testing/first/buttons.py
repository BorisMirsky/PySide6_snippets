
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Signal


class Buttons(QWidget):
    backSignal = Signal(str)
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self.counter = 0
        self.lbl_title = QLabel('Buttons View')
        self.btn_up = QPushButton('up')
        self.btn_down = QPushButton('down')
        self.btn_up.clicked.connect(self.handle_btn_up)
        self.btn_down.clicked.connect(self.handle_btn_down)
        self.back_btn = QPushButton("back")
        self.back_btn.clicked.connect(self.goBack)
        self.lbl = QLabel(str(self.counter))
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_up)
        hbox.addWidget(self.btn_down)
        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_title)
        vbox.addLayout(hbox)
        vbox.addWidget(self.lbl)
        vbox.addWidget(self.back_btn)
        self.setLayout(vbox)

    def handle_btn_up(self):
        self.counter += 1
        self.lbl.setNum(self.counter)

    def handle_btn_down(self):
        self.counter -= 1
        self.lbl.setNum(self.counter)

    def goBack(self):
        self.backSignal.emit('go')

