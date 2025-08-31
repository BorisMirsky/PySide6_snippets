from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import threading, time, datetime


class ExportCurrentTime(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(100, 30)
        self.initUI()

    def initUI(self):
        self.label = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.start()                                      #
        self.timer.timeout.connect(self.displayTime)
        self.setLayout(layout)
        return

    def displayTime(self):
        self.label.setText(QDateTime.currentDateTime().toString('hh:mm:ss'))
        return


#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    gui = ExportCurrentTime()
#    gui.show()
#    sys.exit(app.exec())
