import sys
import random
# from PySide6.QtCore import *
# from PySide6.QtWidgets import *
# from PySide6.QtCharts import *
# from PySide6.QtGui import *
from PySide6.QtCore import Signal, QTimer, QPointF
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QScatterSeries, QLineSeries, QVXYModelMapper, QChart, QChartView, QBarCategoryAxis, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor

img = "image.png"

class Window(QChartView):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.resize(400, 300)
        self.setRenderHint(QPainter.Antialiasing)
        self.m_dataTable = self.generateRandomData(1, 10, 5)
        chart = QChart()
        self.setChart(chart)
        chart.setTitle('Scatter chart')
        self.getSeries(chart)
        chart.createDefaultAxes()
        chart.legend().setVisible(False)

    # передаёт в график список списков серий
    def getSeries(self, chart):
        for i, data_list in enumerate(self.m_dataTable):
            series = QScatterSeries(chart)
            series.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            series.setMarkerSize(15.0)
            for value, _ in data_list:
                series.append(value)
                print(value)
                #series.setSelectedColor('darkred')
            series.setName('Series ' + str(i))
            chart.addSeries(series)

    # генерит список списков серий
    # listCount - количество классов
    def generateRandomData(self, listCount, valueMax, valueCount):              # valueMax - максимальное значение по 'x'
        random.seed()
        dataTable = []
        for i in range(listCount):                    # сколько классов
            dataList = []
            yValue = 0.0                              # valueCount сколько шаров в классе
            f_valueCount = float(valueCount)          # максимальное значение по 'x'
            for j in range(valueCount):
                value = QPointF(j + random.random() * valueMax / f_valueCount, yValue)
                label = 'Slice ' + str(i) + ':' + str(j)
                dataList.append((value, label))
            dataTable.append(dataList)
        return dataTable


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())