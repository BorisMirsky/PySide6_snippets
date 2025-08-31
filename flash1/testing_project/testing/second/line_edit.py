
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator


class LineEdit(QWidget):
    backSignal = Signal(str)
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        validator = QIntValidator()
        validator.setRange(-10, 100)
        self.lbl_title = QLabel('LineEdit View')
        self.le = QLineEdit()
        self.le.setValidator(validator)
        self.le.editingFinished.connect(self.getResult)
        self.lbl = QLabel("")
        self.back_btn = QPushButton("back")
        self.back_btn.clicked.connect(self.goBack)
        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_title)
        vbox.addWidget(self.le)
        vbox.addWidget(self.lbl)
        vbox.addWidget(self.back_btn)
        self.setLayout(vbox)

    def getResult(self):
        result = int(self.le.text()) ** 2
        self.lbl.setNum(result)
        return result

    def goBack(self):
        self.backSignal.emit('go')

