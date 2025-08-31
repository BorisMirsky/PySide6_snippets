import sys
import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


class Spindemo(QWidget):
    def __init__(self, parent=None):
        super(Spindemo, self).__init__(parent)
        layout = QVBoxLayout()
        self.l1 = QLabel("current value:")
        self.l1.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.l1)
        self.sp = QComboBox()
        self.sp.addItem('222')
        self.sp.addItem('333')
        self.sp.addItem('444')
        layout.addWidget(self.sp)
        self.sp.currentTextChanged.connect(self.valuechange)
        self.setLayout(layout)

    def valuechange(self, value):
        self.l1.setText("current value:" + str(value))


def main():
    app = QApplication(sys.argv)
    ex = Spindemo()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()