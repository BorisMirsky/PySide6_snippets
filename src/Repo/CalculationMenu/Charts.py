
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QKeySequence
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
import numpy as np
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel
from ServiceInfo import *


# график с двумя нитками
class Chart1(QWidget):
    def __init__(self,
                 model: VerticalLineModel,
                 chart_column_name1: str,
                 chart_column_name2:str,
                 title:str,
                 top_chart:False):
        super().__init__()
        self.vertical_model = model
        self.chart_column_name1 = chart_column_name1
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, chart_column_name1)
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        self.chart_column_name2 = chart_column_name2
        self.data2 = get_csv_column(FILENAME, chart_column_name2)
        self.series2 = QLineSeries()
        for i in range(0, DATA_LEN, 1):
            self.series2.append(i, self.data2[i])
        self.series2.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.series2)
        y_axis = QValueAxis()
        y_axis.setRange(min(self.data1), max(self.data1))
        y_axis.setLabelFormat("%0.2f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        y_axis.setTitleText(title)
        x_axis = QValueAxis()
        x_axis.setRange(self.x_start, self.x_stop)
        x_axis.setLabelFormat("%d")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(200)
        if top_chart==True:
            x_axis.setLabelsVisible(True)
        else:
            x_axis.setLabelsVisible(False)
        self.chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(x_axis)
        self.series1.attachAxis(y_axis)
        #
        self.vertical_line_series = QLineSeries()
        self.vertical_line_series.setPen(QPen(Qt.GlobalColor.magenta, 4))
        self.lineMapper = QVXYModelMapper(self)
        self.lineMapper.setXColumn(0)
        self.lineMapper.setYColumn(1)
        self.lineMapper.setSeries(self.vertical_line_series)
        self.lineMapper.setModel(self.vertical_model)
        self.chart.addSeries(self.vertical_line_series)
        self.vertical_line_series.attachAxis(x_axis)
        self.vertical_line_series.attachAxis(y_axis)
        #
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        x_axis.setLabelsFont(labelsFont)
        y_axis.setLabelsFont(labelsFont)
        axisBrush = QBrush(Qt.GlobalColor.black)
        x_axis.setLabelsBrush(axisBrush)
        y_axis.setLabelsBrush(axisBrush)
        y_axis.setTitleBrush(axisBrush)
        self.installEventFilter(self)
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.layout().setContentsMargins(0,0,0,0)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.vertical_model.shiftLine(1)
                print("Chart1 D")
                return True
            elif event.key() == Qt.Key.Key_A:
                self.vertical_model.shiftLine(-1)
                print("Chart1 D")
                return True
        return False



class Chart2(QWidget):
    def __init__(self,
                 chart_column_name: str,
                 model: VerticalLineModel,
                 title:str):
        super().__init__()
        self.vertical_model = model
        self.chart_column_name = chart_column_name
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, self.chart_column_name)
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        #
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)

        self.y_axis = QValueAxis()
        self.y_axis.setRange(min(self.data1) - 5, max(self.data1) + 5)
        self.y_axis.setLabelFormat("%0.2f")
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickInterval(10)
        self.y_axis.setTitleText(title)
        axisBrush = QBrush(Qt.GlobalColor.black)
        self.y_axis.setTitleBrush(axisBrush)
        #
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setLabelFormat("%d")
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickInterval(200)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        # self.x_axis.setLabelFormat("@")
        self.x_axis.setLabelsVisible(False)
        self.series1.attachAxis(self.x_axis)
        self.series1.attachAxis(self.y_axis)
        #
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        self.x_axis.setLabelsFont(labelsFont)
        self.y_axis.setLabelsFont(labelsFont)
        self.x_axis.setLabelsBrush(axisBrush)
        self. y_axis.setLabelsBrush(axisBrush)
        #
        self.vertical_line_series = QLineSeries()
        self.vertical_line_series.setPen(QPen(Qt.GlobalColor.magenta, 4))
        self.lineMapper = QVXYModelMapper(self)
        self.lineMapper.setXColumn(0)
        self.lineMapper.setYColumn(1)
        self.lineMapper.setSeries(self.vertical_line_series)
        self.lineMapper.setModel(self.vertical_model)
        self.chart.addSeries(self.vertical_line_series)
        self.vertical_line_series.attachAxis(self.x_axis)
        self.vertical_line_series.attachAxis(self.y_axis)
        self.installEventFilter(self)
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.vertical_model.shiftLine(1)
                print("Chart2 D")
                return True
            elif event.key() == Qt.Key.Key_A:
                self.vertical_model.shiftLine(-1)
                print("Chart2 A")
                return True
        return False


class ChartsWidget(QWidget):
    def __init__(self,
                 chart_column_name1: str,chart_column_name2: str,chart_column_name3: str,
                 chart_column_name4: str,chart_column_name5: str,chart_column_name6: str,
                 chart_column_name7: str,chart_column_name8: str,
                 title1:str,title2:str,title3:str,title4:str,title5:str,
                 model: VerticalLineModel):
        super().__init__()
        self.setContentsMargins(0,0,0,0)
        chart1 = Chart1(model,chart_column_name1,chart_column_name2,title1,top_chart=True)
        chart2 = Chart2(chart_column_name3,model,title2)
        chart3 = Chart1(model,chart_column_name4, chart_column_name5,title3,top_chart=False)
        chart4 = Chart1(model,chart_column_name6, chart_column_name7,title4,top_chart=False)
        chart5 = Chart2(chart_column_name8,model,title5)
        vbox = QVBoxLayout()
        vbox.addWidget(chart1,2)
        vbox.addWidget(chart2,1)
        vbox.addWidget(chart3,1)
        vbox.addWidget(chart4,1)
        vbox.addWidget(chart5,1)
        self.setLayout(vbox)



model = VerticalLineModel


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ChartsWidget('plan_prj', 'plan_fact', 'plan_delta',
                      'vozv_fact','vozv_prj','prof_fact',
                      'prof_prj',  'lbound_plan',
                      "Стрелы изгиба, мм", "Сдвиги, мм", "ВНР, мм",
                      "Стрелы, мм","Подъёмки, мм", model)
    cw.show()
    sys.exit(app.exec())




