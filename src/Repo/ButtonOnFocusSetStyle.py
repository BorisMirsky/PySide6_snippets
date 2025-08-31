from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys

#https://it.kgsu.ru/Python_Qt/pyqt5_062.html

class MyLineEdit(QLineEdit):
    def __init__(self, id, parent = None):
        QLineEdit.__init__(self, parent)
        self.id = id
    def focusInEvent(self, e):
        print("Получен фокус полем", self.id)
        QLineEdit.focusInEvent(self, e)
        #self.focusInEvent(self, e)
        self.setStyleSheet("QLineEdit { background-color: red }")
    def focusOutEvent(self, e):
        print("Потерян фокус полем", self.id)
        QLineEdit.focusOutEvent(self, e)
        self.setStyleSheet("QLineEdit { background-color: white }")

class MyWindow(QWidget):
    def __init__ (self, parent = None):
        QWidget.__init__(self, parent)
        self.resize(300, 100)
        self.button = QPushButton("Установить фокус на поле 2")
        self.line1 = MyLineEdit (1)
        self.line2 = MyLineEdit (2)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.button)
        self.vbox.addWidget(self.line1)
        self.vbox.addWidget(self.line2)
        self.setLayout(self.vbox)
        self.button.clicked.connect(self.on_clicked)
        # Задаем порядок обхода с помощью клавиши <Tab>
        QWidget.setTabOrder(self.line1, self.line2)
        QWidget.setTabOrder(self.line2, self.button)
    def on_clicked(self):
        self.line2.setFocus()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())



    sys.exit(app.exec())

