#  'виджет задачник для графика'

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from PySide6.QtGui import *
from NumpyTableModel import NumpyTableModel
from VerticalLine import MoveLineController, VerticalLineModel
import sys
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# игрушечные данные
datachart =[[0,1], [1,-1], [2,-2], [3,-2.5], [4,-2], [5,-1], [6, 0], [7, 0], [8, 2], [9, 0], [10, 1]]


vertical_model = VerticalLineModel()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        charts = MyCharts(vertical_model)
        widget = Arrows(charts, vertical_model)
        vbox = QVBoxLayout()
        vbox.addWidget(charts)
        vbox.addWidget(widget)
        self.setLayout(vbox)


# Графики
class MyCharts(QWidget):
    def __init__(self, model):
        super().__init__()
        #
        self.vertical_model = model
        self.lineMover = MoveLineController(self.vertical_model)
        self.installEventFilter(self.lineMover)
        verticalLine = QLineSeries()
        verticalLine.setPen(QPen(Qt.GlobalColor.cyan, 10))
        self.lineMapper = QVXYModelMapper(self)
        self.lineMapper.setXColumn(0)
        self.lineMapper.setYColumn(1)
        self.lineMapper.setSeries(verticalLine)
        self.lineMapper.setModel(self.vertical_model)
        #
        chart = QChart()
        # scatter chart
        self.model_scatter = NumpyTableModel(np.ones((0, 2)))
        for point in datachart:
            self.model_scatter.appendRow(point)
        scatter_series = QScatterSeries(self.model_scatter)
        scatter_series.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
        scatter_series.setMarkerSize(15.0)
        mapper1 = QVXYModelMapper(self.model_scatter)
        mapper1.setXColumn(0)
        mapper1.setYColumn(1)
        mapper1.setModel(self.model_scatter)
        mapper1.setSeries(scatter_series)
        # line_chart
        self.model_line = NumpyTableModel(np.ones((0, 2)))
        for point in datachart:
            self.model_line.appendRow(point)
        line_series = QLineSeries(self.model_line)
        mapper2 = QVXYModelMapper(self.model_scatter)
        mapper2.setXColumn(0)
        mapper2.setYColumn(1)
        mapper2.setModel(self.model_line)
        mapper2.setSeries(line_series)
        #
        chart.legend().hide()
        chart.addSeries(line_series)
        chart.addSeries(scatter_series)
        chart.addSeries(verticalLine)
        chart.createDefaultAxes()
        chart_view = QChartView(chart)
        chart.axisY().setRange(-5, 5)
        chart_view.setRenderHint(QPainter.Antialiasing)
        vbox = QVBoxLayout()
        vbox.addWidget(chart_view)
        self.setLayout(vbox)


# Навигация + отображение данных
class Arrows(QWidget):
    def __init__(self, charts: any, model: vertical_model):
        super().__init__()
        self.charts = charts
        self.vertical_model = model
        self.vertical_model.positionChanged.connect(self.update_data)
        label_style = "font: bold 16px;"
        self.current_x = QLabel('')
        static_label_current_x = QLabel('Текущий X: \n')
        static_label_current_x.setStyleSheet(label_style)
        self.current_y = QLabel('')
        static_label_current_y = QLabel('Текущий Y: \n')
        static_label_current_y.setStyleSheet(label_style)
        self.shifted_y = QLabel('')
        static_label_shifted_y = QLabel('Смещение Y на: \n')
        static_label_shifted_y.setStyleSheet(label_style)
        #
        label_to_left = QLabel('"A"')
        arrow_to_left = QLabel(self)
        pixmap_to_left = QPixmap('icons8-left-arrow-50.png')
        arrow_to_left.setPixmap(pixmap_to_left)
        label_to_left.setStyleSheet(label_style)
        #
        label_to_right = QLabel('"D"')
        arrow_to_right = QLabel(self)
        pixmap_to_right = QPixmap('icons8-right-arrow-50.png')
        arrow_to_right.setPixmap(pixmap_to_right)
        label_to_right.setStyleSheet(label_style)
        #
        label_to_up = QLabel('"W"')
        arrow_to_up = QLabel(self)
        pixmap_to_up = QPixmap('icons8-arrow-50.png')
        arrow_to_up.setPixmap(pixmap_to_up)
        label_to_up.setStyleSheet(label_style)
        #
        label_to_down = QLabel('"X"')
        arrow_to_down  = QLabel(self)
        pixmap_to_down  = QPixmap('icons8-down-arrow-50.png')
        arrow_to_down .setPixmap(pixmap_to_down)
        label_to_down.setStyleSheet(label_style)
        #
        grid = QGridLayout()
        grid.setSpacing(10)
        shift_label_h = QLabel('Смещение по горизонтали\n на 1 единицу за такт')
        shift_label_h.setStyleSheet(label_style)
        grid.addWidget(shift_label_h, 0, 0)
        grid.addWidget(label_to_left,0,1, alignment=Qt.AlignRight)
        grid.addWidget(arrow_to_left,0,2, alignment=Qt.AlignLeft)
        grid.addWidget(label_to_right,0,3, alignment=Qt.AlignRight)
        grid.addWidget(arrow_to_right,0,4, alignment=Qt.AlignLeft)
        shift_label_v = QLabel('Смещение по вертикали\n на 0.1 единицу за такт')
        shift_label_v.setStyleSheet(label_style)
        grid.addWidget(shift_label_v,1,0)
        grid.addWidget(label_to_up, 1,1, alignment=Qt.AlignRight)
        grid.addWidget(arrow_to_up,1,2, alignment=Qt.AlignLeft)
        grid.addWidget(label_to_down,1,3, alignment=Qt.AlignRight)
        grid.addWidget(arrow_to_down,1,4, alignment=Qt.AlignLeft)
        grid.addWidget(static_label_current_x, 2, 0)
        grid.addWidget(static_label_current_y, 2, 1)
        grid.addWidget(static_label_shifted_y, 2, 2, alignment=Qt.AlignRight)
        grid.addWidget(self.current_x, 3, 0)
        grid.addWidget(self.current_y, 3, 1)
        grid.addWidget(self.shifted_y, 3, 2)
        self.setLayout(grid)

    def update_data(self):
        sender = self.sender()
        label_style = "font: bold 22px;"
        # X
        colored_currentX = "<font color='red'><b>{0}</b></font>".format(str(sender.currentX()))
        self.current_x.setText(colored_currentX)
        self.current_x.setStyleSheet(label_style)
        # Обработка ситуации "Уход по горизонтали за край"
        try:
            # Определяем Y по X
            current_y_digit = [i[1] for i in datachart if i[0] == sender.currentX()][0]
            colored_currentY = "<font color='red'><b>{0}</b></font>".format(str(current_y_digit))
            self.current_y.setText(colored_currentY)
            self.current_y.setStyleSheet(label_style)
        except IndexError:
            pass
        # Если есть смещение по вертикали
        if sender.currentY():
            self.shift_chart_vertical(sender.currentY())
            colored_currentY = "<font color='red'><b>{0}</b></font>".format(str(sender.currentY()))
            self.shifted_y.setText(colored_currentY)
            self.current_x.setStyleSheet(label_style)
        else:
            colored_currentY = "<font color='red'><b>{0}</b></font>".format(str(0.0))
            self.shifted_y.setText(colored_currentY)
            self.shifted_y.setStyleSheet(label_style)

    def shift_chart_vertical(self, shift):
        self.charts.model_scatter.removeRows(0, len(datachart))
        self.charts.model_scatter.insertRows1(shift, datachart)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec()

