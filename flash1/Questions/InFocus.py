from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys

"""
Вопрос 1
Есть 3 простых виджета. Каждый из них при попадании в фокус должен получать стиль.
Как пробовал сделать:
Такое не работает:
     if self.btn.hasFocus():
           self.setStyleSheet(st)  

Можно сделать по отдельному классу для каждого виджета и там прописать 
    def focusInEvent(self, e):
        self.setStyleSheet(st)
    def focusOutEvent(self, e):
        self.setStyleSheet(" ")
        
Работает, но по некоторым причинам это не подходит

Вопрос 2.
Как переопределить поведение стрелок влево-вправо и ходить между виджетами стрелками, а не tab\tab+shift.
"""



#st = "border: 3px solid; border-color:red; background-color: cyan"
st = """QPushButton{ background-color: cyan; }
        QPushButton:focus{background-color: cyan;border: 2px solid; border-color:black;}"""



class InFocus(QWidget):
    def __init__(self, parent=None):
        super(InFocus, self).__init__(parent)
        hbox = QHBoxLayout()
        self.btn1 = QPushButton()
        self.btn1.setStyleSheet(st) #"QPushButton:focus { border: 3px solid; border-color:red;}")
        self.btn2 = QPushButton()
        self.btn2.setStyleSheet(st) #"QLineEdit:focus {border: 3px solid; border-color:red;}")
        self.btn3 = QPushButton()
        self.btn3.setStyleSheet(st) #"QSpinBox:focus {border: 3px solid; border-color:red;}")
        hbox.addWidget(self.btn1)
        hbox.addWidget(self.btn2)
        hbox.addWidget(self.btn3)
        self.setLayout(hbox)

    def keyPressEvent(self, keyEvent):
        super().keyPressEvent(keyEvent)
        key = keyEvent.key()
        if key == Qt.Key_Right:
            pass
        elif key == Qt.Key_Left:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = InFocus()
    w.resize(300, 100)
    w.show()
    sys.exit(app.exec())
