from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSpinBox
from PySide6.QtCharts import QLineSeries, QChart, QChartView
from PySide6.QtCore import Qt, QObject, QPointF
import sys
from math import sin

#  https://stackoverflow.com/questions/74740422/when-qspinbox-changed-in-pyqt5-can-i-send-a-signal-selectively

class MyClass(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        self.sb1 = QSpinBox()
        self.sb1.lineEdit().setObjectName("sb1")
        self.sb1.setRange(-1000, 1000)
        self.sb1.setKeyboardTracking(False)
        self.sb1.valueChanged.connect(self.func)
        #self.sb1.lineEdit().returnPressed.connect(self.func)
        self.sb2 = QSpinBox()
        self.sb2.setKeyboardTracking(False)
        self.sb2.valueChanged.connect(self.func)
        self.sb2.lineEdit().setObjectName("sb2")
        self.sb2.setRange(-1000, 1000)
        #self.sb2.lineEdit().returnPressed.connect(self.func)
        vbox = QVBoxLayout()
        vbox.addWidget(self.sb1)
        vbox.addWidget(self.sb2)
        self.setLayout(vbox)

    def func(self, value):
        sender = self.sender()
        #emitter = sender.
        print(value) # emitter) #sender.objectName()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyClass()
    window.show()
    sys.exit(app.exec())