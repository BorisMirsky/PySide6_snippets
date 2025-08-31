import sys
import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *



class MyKey(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" My Key Board")
        self.ui()

    def ui(self):
        self.tb = QLineEdit()
        vb = QVBoxLayout(self)
        vb.addWidget(self.tb)

    def handle_key_press(self, key, text):
        if key == Qt.Key_A:
            print("ypu pressed 'A'")


class KeyHelper(QObject):
    key_pressed = Signal(int, str)

    def __init__(self, window):
        super().__init__(window)
        self._window = window
        self.window.installEventFilter(self)

    @property
    def window(self):
        return self._window

    def eventFilter(self, obj, event):
        if obj is self._window and event.type() == QEvent.KeyPress:
            self.key_pressed.emit(event.key(), event.text())
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    import sys
    myapp = QApplication(sys.argv)
    mywindow = MyKey()
    mywindow.show()
    helper = KeyHelper(mywindow.windowHandle())
    helper.key_pressed.connect(mywindow.handle_key_press)
    sys.exit(myapp.exec())