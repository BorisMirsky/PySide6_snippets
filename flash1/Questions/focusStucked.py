import sys
import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


# class Main(QWidget):
#     def __init__(self, parent=None):
#         super(Main, self).__init__(parent)
#         self.resize(300,300)
#         layout = QVBoxLayout()
#         w = QWidget()
#         sb = QSpinBox()
#         sb.setRange(-10,10)
#         layout.addWidget(w)
#         layout.addWidget(sb)                                 # ?!
#         self.installEventFilter(self)
#         self.setLayout(layout)
#
#     def eventFilter(self, watched: QObject, event: QEvent):
#         if event.type() == QEvent.Type.KeyPress:
#             if event.key() == Qt.Key.Key_S:
#                 print("__S__")
#                 return True
#             elif event.key() == Qt.Key.Key_A:
#                 print("__A__")
#                 return True
#         return False
#
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Main()
#     ex.show()
#     sys.exit(app.exec())


class SpinBox(QSpinBox):
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_S:
            print("__S__")
            self.window().label.setText("S")
        elif key == Qt.Key.Key_A:
            print("__A__")
            self.window().label.setText("A")
        else:
            self.window().label.clear()
            return super().keyPressEvent(event)  # !!! +++


class Main(QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.w = QWidget()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel{color: #D98C00; font: 20pt}")
        layoutH = QHBoxLayout(self.w)
        layoutH.addWidget(self.label)

        sb = SpinBox(self)  # +
        sb.setRange(-10, 10)

        layout = QVBoxLayout(self)
        layout.addWidget(self.w)
        layout.addWidget(sb)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_S:
            print("__S__")
            self.label.setText("S")
        elif key == Qt.Key.Key_A:
            print("__A__")
            self.label.setText("A")
        else:
            self.label.clear()
        super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.resize(300, 300)
    ex.show()
    sys.exit(app.exec())