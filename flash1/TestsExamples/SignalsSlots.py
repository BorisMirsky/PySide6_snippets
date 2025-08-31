import sys
from PySide6.QtCharts import QCandlestickSeries, QChart, QChartView, QCandlestickSet, QLineSeries
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,QPushButton
from PySide6.QtCore import Qt, QPointF, QObject, QTimer # pyqtSignal
from PySide6.QtCore import Signal, Slot


#########################################################################################
class Worker(QObject):
    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        #myapp = MyApp()
        #self.onJob()

    @Slot(str, str, int)
    def onJob(self, strA, strB, int1):
        print('from Worker class: ', strA, strB, int1)

class MyApp(QWidget):
    signal = Signal(str, str, int)
    def __init__(self, parent= None):
        super(MyApp, self).__init__(parent)
        self.resize(300, 100)
        self.qqq = None
        self.btn = QPushButton("start", self)
        self.btn.clicked.connect(self.start)
        self.show()

    def start(self):
        otherClass = Worker()
        self.signal.connect(otherClass.onJob)
        self.signal.emit("foo", "baz", 10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())