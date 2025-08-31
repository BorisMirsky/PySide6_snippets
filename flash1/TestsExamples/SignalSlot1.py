import sys
from PySide6.QtCharts import QCandlestickSeries, QChart, QChartView, QCandlestickSet, QLineSeries
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,QPushButton,QSpinBox,QDialog,QDial,QHBoxLayout
from PySide6.QtCore import Qt, QPointF, QObject, QTimer # pyqtSignal
from PySide6.QtCore import Signal, Slot



class ZeroSpinBox(QSpinBox):
    atzero = Signal(int)
    zeros = 0
    def __init__(self):
        super(ZeroSpinBox, self).__init__()
        self.valueChanged.connect(self.checkzero)

    def checkzero(self):
        if self.value() == 0:
            self.zeros += 1
            self.atzero.emit(self.zeros)



class Form(QDialog):
    def __init__(self):
        super(Form, self).__init__()
        dial = QDial()
        dial.setNotchesVisible(True)
        zerospinbox = ZeroSpinBox()
        layout = QHBoxLayout()
        layout.addWidget(dial)
        layout.addWidget(zerospinbox)
        self.setLayout(layout)

        dial.valueChanged.connect(zerospinbox.setValue)
        zerospinbox.valueChanged.connect(dial.setValue)
        zerospinbox.atzero.connect(self.announce)
        self.setWindowTitle("Signals")

    def announce(self, zeros):
        print("zerospinbox has been at zero " + str(zeros) + " times.")



app = QApplication(sys.argv)
form = Form()
form.show()
app.exec()