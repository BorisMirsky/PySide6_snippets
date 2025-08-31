import sys
from PySide6.QtWidgets import QApplication,  QWidget,QSpinBox,QVBoxLayout, QLineEdit
from PySide6.QtCore import Qt, QPointF, QObject, QTimer # pyqtSignal
from PySide6.QtGui import QIntValidator



class TwoEnterKeys(QWidget):
    #atzero = Signal(int)
    zeros = 0
    def __init__(self):
        super(TwoEnterKeys, self).__init__()
        vbox=QVBoxLayout()
        self.setLayout(vbox)
        self.le = QLineEdit()
        onlyInt = QIntValidator()
        onlyInt.setRange(-1000000, 1000000)
        self.le.setValidator(onlyInt)
        self.le.returnPressed.connect(self.checkLineEdit)
        vbox.addWidget(self.le)


    def checkLineEdit(self):
        print(self.le.text())






app = QApplication(sys.argv)
form = TwoEnterKeys()
form.show()
app.exec()