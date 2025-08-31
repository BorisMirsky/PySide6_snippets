from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSpinBox
from PySide6.QtCore import Signal
import sys



class SpinBoxByEnter(QSpinBox):
    valueHasChanged = Signal(int)
    def __init__(self, object_name:str):
        super().__init__()
        self.setObjectName(object_name)
        self.lineEdit().returnPressed.connect(self.spinBoxReturnPressed)

    def spinBoxReturnPressed(self):
        result = self.sender().text()
        self.valueHasChanged.emit(result)

