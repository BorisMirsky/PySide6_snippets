from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
from ServiceInfo import get_csv_column, DATA_LEN, FILENAME
from Charts import Chart1, Chart2, ChartsWidget
from Bottom import BottomWidget
from VerticalLine import VerticalLineModel1,VerticalLineModel2, MoveLineController


"""
делать:

у таблицы headers потерялись

смещение для графика (D & A) - подправить

Размер шрифта увеличить - в таблице и правый виджет

'количество изменений' должно выделяться, не просто строка

добавить фокусполиси для виджетов: два хода таба - на кого?

функции переустройства пусть возвращают всю строку из саммари (сделать и закомментировать)

перемещение табом - непонятно как перейти на изменение масштаба, не всегда понятно

"""


model1 = VerticalLineModel1(0)
model2 = VerticalLineModel2(0)

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        c1 = Chart1('plan_prj', 'plan_fact', model1, model2)
        c2 = Chart2('plan_delta')
        charts = ChartsWidget(c1, c2)
        bottom = BottomWidget(model1, model2)
        vbox = QVBoxLayout()
        vbox.addWidget(charts, 3)
        vbox.addWidget(bottom, 1)

        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget()
    MW.show()
    sys.exit(app.exec())

