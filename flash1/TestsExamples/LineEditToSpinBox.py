
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSpinBox
from PySide6.QtCore import Signal, QEvent, Qt
from PySide6.QtGui import QKeyEvent
import sys


class MySpinBox(QSpinBox):
    valueHasChanged = Signal(int)

    def __init__(self, object_name: str):
        super().__init__()
        self.setObjectName(object_name)
        self.lineEdit().enterEvent()    returnPressed.connect(self.spinBoxReturnPressed)

    def spinBoxReturnPressed(self):
        result = self.text()   #self.sender().text()
        self.valueHasChanged.emit(result)



class MyClass(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 200)
        self.sb1 = MySpinBox('_sb1_')
        self.sb1.setRange(-1000, 1000)
        self.sb1.valueHasChanged.connect(self.returnValue)
        # self.sb2 = MySpinBox('_sb2_')
        # self.sb2.setRange(-1000, 1000)
        # self.sb2.valueHasChanged.connect(self.returnValue)
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.sb1)
        #vbox.addWidget(self.sb2)

    def returnValue(self):
        print(self.sb1.value(), type(self.sb1.value()))   #self.sender().objectName(), self.sender())
        return

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            keyEvent = QKeyEvent(event)
            if keyEvent.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
                self.focusNextPrevChild(True)
        return super().event(event)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyClass()
    window.show()
    sys.exit(app.exec())