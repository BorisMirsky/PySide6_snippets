from PySide6.QtWidgets import QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtGui import QColor, QBrush
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


class MyClass(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,300)
        self.installEventFilter(self)


    def eventFilter(self, QObject object, QEvent event):
        if object == target and event.type() == QEvent.KeyPress:
            keyEvent = QKeyEvent(event)
            if keyEvent.key() == Qt.Key_S:
                print("__S__")
                return True
            elif keyEvent.key() == Qt.Key_A:
                print("__A__")
                return True

    return False
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mc = MyClass()
    mc.show()
    sys.exit(app.exec())
