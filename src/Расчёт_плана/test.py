import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import * 
from PySide6.QtGui import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("QGridLayout Example")
        layout = QGridLayout()
        layout.addWidget(self.top_group(), 0, 0, 1, 2)
        layout.addWidget(self.bottom_left(), 1, 0)
        layout.addWidget(self.bottom_right(), 1, 1)
        self.setLayout(layout)

    def top_group(self):
        return QPushButton("Button Spans two Cols")

    def bottom_left(self):
        return QPushButton("Button bottom left")

    def bottom_right(self):
        return QPushButton("Button bottom right")


        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
