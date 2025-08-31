from PySide6.QtWidgets import QWidget, QVBoxLayout,QPushButton, QApplication, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtGui import Qt, QPen, QIntValidator, QBrush
from PySide6.QtCore import Qt,  QCoreApplication
import sys


class ChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(700, 500)
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.x_start = 0
        self.x_stop = 500
        self.y_axis = QValueAxis()
        self.y_axis.setRange(0, 20)
        self.y_axis.setLabelFormat("%0.2f")
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickInterval(5)
        axisBrush = QBrush(Qt.GlobalColor.black)
        self.y_axis.setTitleBrush(axisBrush)
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setLabelFormat("%d")
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickInterval(100)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series = QLineSeries()
        for i in range(0, 500, 1):
            self.series.append(i, 10)
        self.series.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.series)
        self.series.attachAxis(self.x_axis)
        self.series.attachAxis(self.y_axis)
        right_column = self.right_column()
        chart_view = QChartView(self.chart)
        hbox = QHBoxLayout()
        hbox.addWidget(chart_view, 8)
        hbox.addWidget(right_column, 2)
        self.setLayout(hbox)

    def right_column(self):
        self.right_column_widget = QWidget()
        self.right_column_layout = QVBoxLayout()
        self.right_column_widget.setLayout(self.right_column_layout)
        self.lineEdit1 = QLineEdit()
        self.lineEdit1.setPlaceholderText("Значение 1")
        self.lineEdit1.setValidator(QIntValidator(-999, 999, self))
        self.lineEdit2 = QLineEdit()
        self.lineEdit2.setPlaceholderText("Значение 2")
        self.lineEdit2.setValidator(QIntValidator(-999, 999, self))
        self.btn = QPushButton("go!")
        self.btn.clicked.connect(self.__handleChart)
        self.right_column_layout.addStretch(1)
        self.right_column_layout.addWidget(self.lineEdit1)
        self.right_column_layout.addWidget(self.lineEdit2)
        self.right_column_layout.addWidget(self.btn)
        self.right_column_layout.addStretch(1)
        self.right_column_layout.addStretch(1)
        return self.right_column_widget

    def __handleChart(self):
        for i in range(int(self.lineEdit1.text()), int(self.lineEdit2.text()), 1):
            print(i)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ChartWindow()
    cw.show()
    sys.exit(app.exec())
