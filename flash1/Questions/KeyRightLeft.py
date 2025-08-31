import sys
import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


class Main(QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.resize(300,300)
        layout = QVBoxLayout()
        w = QWidget()
        layout.addWidget(w)
        #self.installEventFilter(self)
        self.setLayout(layout)
        self._global_keyPressEvent()


    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key_Right:
                print("__Key_Right__")
                return True
            elif event.key() == Qt.Key.Key_Left:
                print("__Key_Left__")
                return True
            if event.key() == Qt.Key_Up:
                print("__Key_Up__")
                return True
            elif event.key() == Qt.Key.Key_Down:
                print("__Key_Down__")
                return True
        return False



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
