
from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QScatterSeries, QLineSeries, QVXYModelMapper, QChart, QChartView, QBarCategoryAxis, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
import sys
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel



##################################################################################################################
class MarkersWindow(QWidget):
    mysignal = Signal(str)
    def __init__(self):
        super().__init__()
        self.resize(450, 650)
        self.list_widget = QListWidget()
        all_markers = ['ОПОРА контактной сети [справа]', 'ОПОРА контактной сети [слева]',
                       'ПЛАТФОРМА [начало справа]', 'ПЛАТФОРМА [конец справа]',
                       'ПЛАТФОРМА [начало слева]', 'ПЛАТФОРМА [конец слева]',
                       'ТОННЕЛЬ [начало]','ТОННЕЛЬ [конец]',
                       'ТРУБА', 'УТС',
                       'СТРЕЛКА крестовина [вправо]','СТРЕЛКА крестовина [влево]',
                       'СТРЕЛКА остряк [вправо]', 'СТРЕЛКА остряк [влево]',
                       'Разное [справа]', 'Разное [слева]']
        my_font = QFont("Times New Roman", 16)
        my_font.setBold(True)
        self.list_widget.setFont(my_font)
        #
        icon_picket = QIcon('static/picket.png')
        item_picket_right = QListWidgetItem(icon_picket, 'ПИКЕТ [справа]')
        item_picket_left = QListWidgetItem(icon_picket, 'ПИКЕТ [слева]')
        self.list_widget.addItem(item_picket_right)
        self.list_widget.addItem(item_picket_left)
        #
        icon_bridge = QIcon('static/bridge.jpg')
        item_bridge_right = QListWidgetItem(icon_bridge, 'МОСТ [начало]')
        item_bridge_left = QListWidgetItem(icon_bridge, 'МОСТ [конец]')
        self.list_widget.addItem(item_bridge_right)
        self.list_widget.addItem(item_bridge_left)
        #
        icon_crossing = QIcon('static/pereezd.png')
        item_crossing_right = QListWidgetItem(icon_crossing, 'ПЕРЕЕЗД [начало]')
        item_crossing_left = QListWidgetItem(icon_crossing, 'ПЕРЕЕЗД [конец]')
        self.list_widget.addItem(item_crossing_right)
        self.list_widget.addItem(item_crossing_left)
        #
        icon_traffic_light = QIcon('static/traffic-light.png')
        item_traffic_light_right = QListWidgetItem(icon_traffic_light, 'СИГНАЛ (светофор справа)')
        item_traffic_light_left = QListWidgetItem(icon_traffic_light, 'СИГНАЛ (светофор слева)')
        self.list_widget.addItem(item_traffic_light_right)
        self.list_widget.addItem(item_traffic_light_left)
        #
        self.list_widget.addItems(all_markers)
        self.select_marker_shortcut = QShortcut(Qt.Key_Return, self)
        self.close_window_shortcut = QShortcut(Qt.Key_Escape, self)
        #
        self.select_marker_shortcut.activated.connect(lambda: self.__selection_changed())
        self.close_window_shortcut.activated.connect(lambda: self.close())
        #
        vbox = QVBoxLayout()
        vbox.addWidget(self.list_widget)
        self.setLayout(vbox)

    def __selection_changed(self):
        if self.list_widget.currentItem():
            #print(self.list_widget.currentItem().text())
            return self.mysignal.emit(self.list_widget.currentItem().text())


vertical_model = VerticalLineModel()

##################################################################################################################
class Chart(QWidget):
    def __init__(self, timer: QTimer(qApp), n: int, model: any, parent: QWidget = None):
        super().__init__(parent)
        self.positionValue = 0
        self.insertionTimer = timer
        self.vertical_model = model
        self.counter = 0
        self.minPosition = 0
        #
        self.model1 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model2 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model3 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model4 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model5 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model6 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model7 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model8 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model9 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model10 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model11 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model12 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.line_model = NumpyTableModel(np.ones((0, 2)), qApp)    #  ось || OX
        self.series1 = QScatterSeries(self.model1)
        self.series2 = QScatterSeries(self.model2)
        self.series3 = QScatterSeries(self.model3)
        self.series4 = QScatterSeries(self.model4)
        self.series5 = QScatterSeries(self.model5)
        self.series6 = QScatterSeries(self.model6)
        self.series7 = QScatterSeries(self.model7)
        self.series8 = QScatterSeries(self.model8)
        self.series9 = QScatterSeries(self.model9)
        self.series10 = QScatterSeries(self.model10)
        self.series11 = QScatterSeries(self.model11)
        self.series12 = QScatterSeries(self.model12)
        self.horizont_line_series = QLineSeries(self.line_model)
        #
        self.horizont_line_series.setPen(QPen(Qt.GlobalColor.magenta, 3))
        self.line_mapper = QVXYModelMapper(self.line_model)    # horizont line
        self.line_mapper.setXColumn(1)
        self.line_mapper.setYColumn(0)
        self.line_mapper.setModel(self.line_model)
        self.line_mapper.setSeries(self.horizont_line_series)
        #
        self.mapper1 = QVXYModelMapper(self.model1)
        self.mapper1.setXColumn(1)
        self.mapper1.setYColumn(0)
        self.mapper1.setModel(self.model1)
        self.mapper1.setSeries(self.series1)
        #
        self.mapper2 = QVXYModelMapper(self.model2)
        self.mapper2.setXColumn(1)
        self.mapper2.setYColumn(0)
        self.mapper2.setModel(self.model2)
        self.mapper2.setSeries(self.series2)
        #
        self.mapper3 = QVXYModelMapper(self.model3)
        self.mapper3.setXColumn(1)
        self.mapper3.setYColumn(0)
        self.mapper3.setModel(self.model3)
        self.mapper3.setSeries(self.series3)
        #
        self.mapper4 = QVXYModelMapper(self.model4)
        self.mapper4.setXColumn(1)
        self.mapper4.setYColumn(0)
        self.mapper4.setModel(self.model4)
        self.mapper4.setSeries(self.series4)
        #
        self.mapper5 = QVXYModelMapper(self.model5)
        self.mapper5.setXColumn(1)
        self.mapper5.setYColumn(0)
        self.mapper5.setModel(self.model5)
        self.mapper5.setSeries(self.series5)
        #
        self.mapper6 = QVXYModelMapper(self.model6)
        self.mapper6.setXColumn(1)
        self.mapper6.setYColumn(0)
        self.mapper6.setModel(self.model6)
        self.mapper6.setSeries(self.series6)
        #
        self.mapper7 = QVXYModelMapper(self.model7)
        self.mapper7.setXColumn(1)
        self.mapper7.setYColumn(0)
        self.mapper7.setModel(self.model7)
        self.mapper7.setSeries(self.series7)
        #
        self.mapper8 = QVXYModelMapper(self.model8)
        self.mapper8.setXColumn(1)
        self.mapper8.setYColumn(0)
        self.mapper8.setModel(self.model8)
        self.mapper8.setSeries(self.series8)
        #
        self.mapper9 = QVXYModelMapper(self.model9)
        self.mapper9.setXColumn(1)
        self.mapper9.setYColumn(0)
        self.mapper9.setModel(self.model9)
        self.mapper9.setSeries(self.series9)
        #
        self.mapper10 = QVXYModelMapper(self.model10)
        self.mapper10.setXColumn(1)
        self.mapper10.setYColumn(0)
        self.mapper10.setModel(self.model10)
        self.mapper10.setSeries(self.series10)
        #
        self.mapper11 = QVXYModelMapper(self.model11)
        self.mapper11.setXColumn(1)
        self.mapper11.setYColumn(0)
        self.mapper11.setModel(self.model11)
        self.mapper11.setSeries(self.series11)
        #
        self.mapper12 = QVXYModelMapper(self.model12)
        self.mapper12.setXColumn(1)
        self.mapper12.setYColumn(0)
        self.mapper12.setModel(self.model12)
        self.mapper12.setSeries(self.series12)
        #
        self.mapper_for_mapping_only = QVXYModelMapper(self.model1)     # Этот маппер только для отображения
        self.mapper_for_mapping_only.setXColumn(0)
        self.mapper_for_mapping_only.setYColumn(1)
        #
        self.vertical_line_series = QLineSeries()
        self.vertical_line_series.setPen(QPen(Qt.GlobalColor.cyan, 3))
        self.lineMapper = QVXYModelMapper(self)
        self.lineMapper.setXColumn(1)
        self.lineMapper.setYColumn(0)
        self.lineMapper.setSeries(self.vertical_line_series)
        self.lineMapper.setModel(self.vertical_model)
        self.vertical_line_position = 0
        #
        self.call_markers_window_shortcut = QShortcut(Qt.Key_Space, self)    # вызов окна пробелом
        self.markers_window = MarkersWindow()
        self.call_markers_window_shortcut.activated.connect(lambda: self.markers_window.show())
        self.markers_window.mysignal.connect(self.add_artificial_object)
        #
        self.value = None       # флаг проверки единичный\неединичный ИССО
        #
        self.axisX = QValueAxis()  #QBarCategoryAxis()
        self.axisY = QValueAxis()
        #
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.series2)
        self.chart.addSeries(self.series3)
        self.chart.addSeries(self.series4)
        self.chart.addSeries(self.series5)
        self.chart.addSeries(self.series6)
        self.chart.addSeries(self.series7)
        self.chart.addSeries(self.series8)
        self.chart.addSeries(self.series9)
        self.chart.addSeries(self.series10)
        self.chart.addSeries(self.series11)
        self.chart.addSeries(self.series12)
        self.chart.addSeries(self.horizont_line_series)
        self.chart.addSeries(self.vertical_line_series)
        #
        self.chart.setAxisX(self.axisX)
        self.chart.setAxisY(self.axisY)
        #
        self.series1.attachAxis(self.axisX)
        self.series1.attachAxis(self.axisY)
        self.series2.attachAxis(self.axisX)
        self.series2.attachAxis(self.axisY)
        self.series3.attachAxis(self.axisX)
        self.series3.attachAxis(self.axisY)
        self.series4.attachAxis(self.axisX)
        self.series4.attachAxis(self.axisY)
        self.series5.attachAxis(self.axisX)
        self.series5.attachAxis(self.axisY)
        self.series6.attachAxis(self.axisX)
        self.series6.attachAxis(self.axisY)
        self.series7.attachAxis(self.axisX)
        self.series7.attachAxis(self.axisY)
        self.series8.attachAxis(self.axisX)
        self.series8.attachAxis(self.axisY)
        self.series9.attachAxis(self.axisX)
        self.series9.attachAxis(self.axisY)
        self.series10.attachAxis(self.axisX)
        self.series10.attachAxis(self.axisY)
        self.series11.attachAxis(self.axisX)
        self.series11.attachAxis(self.axisY)
        self.series12.attachAxis(self.axisX)
        self.series12.attachAxis(self.axisY)
        self.vertical_line_series.attachAxis(self.axisX)
        self.vertical_line_series.attachAxis(self.axisY)
        #self.horizont_line_series.attachAxis(self.axisX)
        #self.horizont_line_series.attachAxis(self.axisY)
        self.chart.legend().setVisible(False)
        #
        self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(False)             # прячем сетку графикa
        self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(False)
        #
        self.vlayout = QVBoxLayout()
        self.insertionTimer.start(n)
        self.insertionTimer.timeout.connect(self.update_field)
        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.vlayout.addWidget(self.view)
        self.setLayout(self.vlayout)

    # на каждом тике счётчика
    def update_field(self) ->None:
        self.check_not_single_artificial_object(self.value)           # проверка: есть ли неединичный ИССО
        maxPosition = max(50, self.counter + 5)
        self.minPosition = max(0, maxPosition - 50)
        self.vertical_line_position = maxPosition - 10 #self.minPosition + 10                        # где будет стоять отсечка
        self.vertical_model.keep_line_position(self.vertical_line_position)        # Удержание отсечки в поле видимости
        self.chart.axisY().setRange(self.minPosition, maxPosition)
        self.mapper_for_mapping_only.setFirstRow(self.minPosition)                 # mapper только для отображения позиции
        self.line_model.appendRow([self.counter, 0.5])                               # линейный график, типа наш жд путь
        self.positionValue += 1
        self.counter += 1
        # print('self.minPosition ', self.minPosition,
        #       'maxPosition ', maxPosition,
        #       'self.vertical_line_position ', self.vertical_line_position,
        #       'self.positionValue ', self.positionValue)
    positionValue = 0


    # генерится и добавляется ИССО (Artificial Object)
    def add_artificial_object(self, value) ->None:
        if value == 'ПИКЕТ [справа]':
            self.value = None                                                # флажок
            self.series1.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            self.series1.setMarkerSize(20.0)
            star = QImage(40, 40, QImage.Format_ARGB32)
            star.fill(Qt.transparent)
            img = QPixmap("static/picket.png")
            painter = QPainter(star)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(painter.pen().color())
            painter.drawPixmap(0, 0, img)
            painter.end()
            self.series1.setBrush(star)
            self.series1.setPen(QColor(Qt.transparent))
            self.model1.appendRow([self.vertical_line_position, 0.8])
        elif value == 'ПИКЕТ [слева]':
            self.value = None
            self.series1.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            self.series1.setMarkerSize(20.0)
            self.series1.setColor('red')
            self.model1.appendRow([self.vertical_line_position, 0.2])
        elif value == 'ОПОРА контактной сети [справа]':
            self.value = None
            self.series2.setMarkerShape(QScatterSeries.MarkerShapeCircle)
            self.series2.setMarkerSize(25.0)
            self.series2.setColor('green')
            self.model2.appendRow([self.vertical_line_position, 0.8])
        elif value == 'ОПОРА контактной сети [слева]':
            self.value = None
            self.series2.setMarkerShape(QScatterSeries.MarkerShapeCircle)
            self.series2.setMarkerSize(25.0)
            self.series2.setColor('green')
            self.model2.appendRow([self.vertical_line_position, 0.2])
        elif value == 'СИГНАЛ (светофор справа)':
            self.value = None
            self.series3.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            self.series3.setMarkerSize(50.0)
            sign = QImage(50, 50, QImage.Format_ARGB32)
            sign.fill(Qt.transparent)
            img = QPixmap("static/traffic-light.png")
            painter = QPainter(sign)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(painter.pen().color())
            painter.drawPixmap(0, 0, img)
            painter.end()
            self.series3.setBrush(sign)
            self.series3.setPen(QColor(Qt.transparent))
            self.model3.appendRow([self.vertical_line_position, 0.8])
        elif value == 'СИГНАЛ (светофор слева)':
            self.value = None
            self.series3.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            self.series3.setMarkerSize(50.0)
            sign = QImage(50, 50, QImage.Format_ARGB32)
            sign.fill(Qt.transparent)
            img = QPixmap("static/traffic-light.png")
            painter = QPainter(sign)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(painter.pen().color())
            painter.drawPixmap(0, 0, img)
            painter.end()
            self.series3.setBrush(sign)
            self.series3.setPen(QColor(Qt.transparent))
            #
            self.model3.appendRow([self.vertical_line_position, 0.2])
        elif value == 'ТРУБА':
            self.value = None
            self.series4.setMarkerShape(QScatterSeries.MarkerShapeTriangle)
            self.series4.setMarkerSize(35.0)
            self.series4.setColor('darkBlue')
            self.model4.appendRow([self.vertical_line_position, 0.5])
        elif value == 'УТС':
            self.value = None
            self.series5.setMarkerShape(QScatterSeries.MarkerShapeStar)
            self.series5.setMarkerSize(35.0)
            self.series5.setColor('darkGreen')
            self.model5.appendRow([self.vertical_line_position, 0.5])
        elif value == 'СТРЕЛКА крестовина [вправо]':
            self.value = None
            self.series6.setMarkerShape(QScatterSeries.MarkerShapePentagon)
            self.series6.setMarkerSize(25.0)
            self.series6.setColor('darkRed')
            self.model6.appendRow([self.vertical_line_position, 0.8])
        elif value == 'СТРЕЛКА крестовина [влево]':
            self.value = None
            self.series6.setMarkerShape(QScatterSeries.MarkerShapePentagon)
            self.series6.setMarkerSize(25.0)
            self.series6.setColor('darkRed')
            self.model6.appendRow([self.vertical_line_position, 0.2])
        elif value == 'СТРЕЛКА остряк [вправо]':
            self.value = None
            self.series7.setMarkerShape(QScatterSeries.MarkerShapeCircle)
            self.series7.setMarkerSize(40.0)
            self.series7.setColor('darkYellow')
            self.model7.appendRow([self.vertical_line_position, 0.8])
        elif value == 'СТРЕЛКА остряк [влево]':
            self.value = None
            self.series7.setMarkerShape(QScatterSeries.MarkerShapeCircle)
            self.series7.setMarkerSize(40.0)
            self.series7.setColor('darkYellow')
            self.model7.appendRow([self.vertical_line_position, 0.2])
        elif value == 'Разное [справа]':
            self.value = None
            self.series8.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            self.series8.setMarkerSize(35.0)
            self.series8.setColor('darkCyan')
            self.model8.appendRow([self.vertical_line_position, 0.8])
        elif value == 'Разное [слева]':
            self.value = None
            self.series8.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            self.series8.setMarkerSize(35.0)
            self.series8.setColor('darkCyan')
            self.model8.appendRow([self.vertical_line_position, 0.2])
        # not single
        elif '[начало' in value.split(' ')[1]:
            self.value = value
        elif '[конец' in value.split(' ')[1]:
            self.value = None


    #  ИССО имеющий НАЧАЛО и КОНЕЦ
    def check_not_single_artificial_object(self, value) ->None:
        if value:
            if value == 'ПЕРЕЕЗД [начало]':
                self.series9.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
                self.series9.setMarkerSize(30.0)
                star = QImage(40, 40, QImage.Format_ARGB32)
                star.fill(Qt.transparent)
                img = QPixmap("static/pereezd.png")
                painter = QPainter(star)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(painter.pen().color())
                painter.drawPixmap(0, 0, img)
                painter.end()
                self.series9.setBrush(star)
                self.series9.setPen(QColor(Qt.transparent))
                self.model9.appendRow([self.vertical_line_position, 0.5])
            elif value == 'ПЛАТФОРМА [начало справа]':
                self.series10.setMarkerShape(QScatterSeries.MarkerShapeTriangle)
                self.series10.setMarkerSize(25.0)
                self.series10.setColor('cyan')
                self.model10.appendRow([self.vertical_line_position, 0.8])
            elif value == 'ПЛАТФОРМА [начало слева]':
                self.series10.setMarkerShape(QScatterSeries.MarkerShapeTriangle)
                self.series10.setMarkerSize(25.0)
                self.series10.setColor('cyan')
                self.model10.appendRow([self.vertical_line_position, 0.2])
            elif value == 'МОСТ [начало]':
                self.series11.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
                self.series11.setMarkerSize(40.0)
                star = QImage(40, 40, QImage.Format_ARGB32)
                star.fill(Qt.transparent)
                img = QPixmap("static/bridge.jpg")
                painter = QPainter(star)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(painter.pen().color())
                painter.drawPixmap(0, 0, img)
                painter.end()
                self.series11.setBrush(star)
                self.series11.setPen(QColor(Qt.transparent))
                self.model11.appendRow([self.vertical_line_position, 0.5])
            elif value == 'ТОННЕЛЬ [начало]':
                self.series12.setMarkerShape(QScatterSeries.MarkerShapePentagon)
                self.series12.setMarkerSize(35.0)
                self.series12.setColor('magenta')
                self.model12.appendRow([self.vertical_line_position, 0.5])


class Main(QWidget):
    def __init__(self,  timer: QTimer(qApp), n: int):
        super().__init__()
        self.timer = timer
        chart = Chart(insertionTimer, n, vertical_model)
        vbox = QVBoxLayout()
        vbox.addWidget(chart)
        self.setLayout(vbox)



if __name__ == '__main__':
    insertionTimer = QTimer(qApp)
    app = QApplication(sys.argv)
    window = Main(insertionTimer, 100)
    window.show()
    sys.exit(app.exec())