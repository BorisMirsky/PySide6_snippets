# This Python file uses the following encoding: utf-8
from DataframeTableModel import DataframeTableModel
from DistanceProvider import DistanceProvider
from MockModels import SinMockModel
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer
from Chart import LineChartClass
import sys



app = QApplication(sys.argv)


class TabWidgetClass(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        #
        # sensor1 = SinMockModel(amplitude=5, frequency=2, parent=app)
        # sensor2 = SinMockModel(amplitude=4, frequency=3, parent=app)
        # sensor3 = SinMockModel(amplitude=3, frequency=4, parent=app)
        # sensor4 = SinMockModel(amplitude=2, frequency=5, parent=app)
        insertionTimer = QTimer(qApp)
        chart1 = LineChartClass(sensor1, sensor2, insertionTimer)
        chart2 = LineChartClass(sensor3, sensor4, insertionTimer)
        #
        tabwidget = QTabWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(chart1)
        vbox.addWidget(chart2)
        tabwidget.addTab(QLabel("___"), "Table")
        tabwidget.setLayout(vbox) #, "LineCharts")

        #layout = QGridLayout()
        #tabwidget = QTabWidget()
        #label1 = QLabel("Widget in Tab 1.")
        #label2 = QLabel("Widget in Tab 2.")
        #tabwidget.addTab(label1, "Table")
        #tabwidget.addTab(label2, "LineCharts")
        #layout.addWidget(tabwidget, 0, 0)
        #self.setLayout(layout)
        return



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    #position = DistanceProvider(app)
    sensor1 = SinMockModel(amplitude=5, frequency=2, parent=app)
    sensor2 = SinMockModel(amplitude=4, frequency=3, parent=app)
    sensor3 = SinMockModel(amplitude=3, frequency=4, parent=app)
    sensor4 = SinMockModel(amplitude=2, frequency=5, parent=app)
    # insertionTimer = QTimer(qApp)
    # chart1 = LineChartClass(sensor1, sensor2, insertionTimer)
    # chart2 = LineChartClass(sensor3, sensor4, insertionTimer)
    tab_class = TabWidgetClass()
    # vbox = QVBoxLayout()
    # vbox.addWidget(chart1)
    # vbox.addWidget(chart2)
    # tab_class.addTab(vbox)
    tab_class.show()
    sys.exit(app.exec())
