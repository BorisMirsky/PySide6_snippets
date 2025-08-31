from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
from ServiceInfo import get_csv_column, DATA_LEN, FILENAME
from Charts import Chart1, Chart2, ChartsWidget
from Bottom import BottomWidget
from VerticalLine import VerticalLineModel, MoveLineController


model1 = VerticalLineModel(0)
model2 = VerticalLineModel(0)
model3 = VerticalLineModel(-10)

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        c1 = Chart1('plan_prj', 'plan_fact', model1, model2, model3)
        c2 = Chart2('plan_delta')
        charts = ChartsWidget(c1, c2)
        bottom = BottomWidget(model1, model2, model3)
        vbox = QVBoxLayout()
        vbox.addWidget(charts, 3)
        vbox.addWidget(bottom, 1)
        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget()
    MW.show()
    sys.exit(app.exec())

