from PySide6.QtWidgets import (QVBoxLayout, QApplication,QPushButton,QGridLayout,
QListWidget, QWidget, QListWidgetItem)
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import *
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)        
        self.list_widget = QListWidget()     
        self.list_widget.addItem("Option 1")
        self.list_widget.addItem("Option 2")
        self.list_widget.addItem("Option 3")
        self.list_widget.addItem("Option 4")
        self.list_widget.itemDoubleClicked.connect(self.onClicked)
        self.list_widget.itemClicked.connect(self.onClicked)
        layout = QVBoxLayout()
        self.installEventFilter(self)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

   # только клики, на enter не реагирует
    def onClicked(self, item):
        print(item.text())

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress: # and event.matches(QKeySequence.InsertParagraphSeparator):
            i = self.list_widget.text() #currentRow()
            print(i)
        


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec())
