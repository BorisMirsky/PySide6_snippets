import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import * 
from PySide6.QtGui import *


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.stack1 = QTextEdit('<h2>TextEdit</h2>')
        self.stack2 = QLabel('<h2>Hello World</h2>', alignment=Qt.AlignCenter)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.stack1)
        self.stacked_widget.addWidget(self.stack2)

        self.lestWidget = QListWidget()
        self.lestWidget.setFixedWidth(100)
        self.lestWidget.addItems(['TextEdit', 'Label'])
        self.lestWidget.currentRowChanged.connect(self.display)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.lestWidget)
        hbox.addWidget(self.stacked_widget)

    def display(self, i):
        self.stacked_widget.setCurrentIndex(i)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
