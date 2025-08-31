import sys
from PySide6.QtCharts import QCandlestickSeries, QChart, QChartView, QCandlestickSet, QLineSeries
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,QPushButton,QSpinBox,QDialog,QDial,QHBoxLayout,QProgressBar
from PySide6.QtCore import Qt, QPointF, QObject, QTimer # pyqtSignal
from PySide6.QtCore import Signal, Slot




class GUI(QApplication):
    gui_signal = Signal(object, str, tuple)

    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__([])
        self.gui_signal.connect(self.method_call)

    @Slot(object, str, tuple)
    def method_call(self, obj, method_name, data):
        if hasattr(obj, method_name):
            method = getattr(obj, method_name)
            args, kwargs = data
            if hasattr(method, '__call__'):
                method(*args, **kwargs)

    def anymethod(self, obj, method_name, *args, **kwargs):
        self.gui_signal.emit(obj, method_name, (args, kwargs))

class MyApp(object):
    def __init__(self):
        self.gui = GUI()
        self.progressBar = QProgressBar(maximum=100)
        self.progressBar.show()
        self.total = 200
        self.done = 100
        QTimer.singleShot(300, self.update_progress)

    def update_progress(self):
        perc = (self.done * 100) / self.total
        self.gui.anymethod(self.progressBar, 'setValue', int(perc))

    def run(self):
        return self.gui.exec()

if __name__ == '__main__':
    import sys
    app = MyApp()
    sys.exit(app.run())