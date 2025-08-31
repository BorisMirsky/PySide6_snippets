
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSpinBox, QLineEdit
from PySide6.QtCore import Signal, QEvent, Qt
from PySide6.QtGui import QKeyEvent, QIntValidator, QValidator
import sys

class MyClass(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 200)
        #self.sb1 = QSpinBox()
        onlyInt = QIntValidator()
        onlyInt.setRange(-1000000, 1000000)
        self.sb1 = QLineEdit()
        self.sb1.setValidator(onlyInt)
        self.sb1.setRange(-1000, 1000)
        self.sb1.editingFinished.connect(self.returnValue)
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