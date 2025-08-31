
from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QApplication,QPushButton,QSpinBox,QComboBox,
                               QHBoxLayout, QGridLayout, QLabel, QFileDialog,QMessageBox, QGroupBox)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType  #TrackPlanProjectModel
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from .VerticalLine import VerticalLineModel, MoveLineController


class SpeedMainWidget(QWidget):
    closeLevelSpeedSignal = Signal(str)
    passDataSignal = Signal(TrackProjectModel)
    okChangeSpeedSignal = Signal(str)
    cancelChangeSpeedSignal = Signal(str)
    def __init__(self,
                 position:float,
                 state: ProgramTaskCalculationSuccessState,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
        self.position = position
        self.programTaskModel: AbstractPositionedTableModel = self.__state.program_task()
        self.options: ProgramTaskCalculationResultDto = self.__state.calculation_result().options
        #
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(self.programTaskModel)
        position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = self.programTaskModel.minmaxPosition()
        position_min: float = position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        position_max: float = position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        #
        self.counter = 0
        #self.summary = TrackPlanProjectModel(self.__state.calculation_result().base.track_split_plan,
        #                                     self.__state.calculation_result().base.plan)
        self.summary = TrackProjectModel.create(TrackProjectType.Level, self.__state.calculation_result())               # = plan_model
        self.summary_len = len(self.summary.elements())
        self.current_segment = self.summary.elements()[self.counter]
        self.segment_type = self.current_segment.geometry.value
        self.startPicket = self.__state.calculation_result().options.start_picket.meters
        self.currentPosition = self.options.start_picket.meters
        range_points = self.defineRange(self.position)
        self.model1 = VerticalLineModel(range_points[0])
        self.model2 = VerticalLineModel(range_points[1])
        self.lineMover1 = MoveLineController(self.model1, self.model2, self.startPicket)
        self.lineMover2 = MoveLineController(self.model1, self.model2, self.startPicket)

        self.okChangeSpeedSignal .connect(lambda: self.__escapeFunction('okChangeSpeedSignal'))
        self.cancelChangeSpeedSignal.connect(lambda: self.__escapeFunction('cancelChangeSpeedSignal'))
        #
        grid = QGridLayout()
        infopanel_first = InfopanelFirst(self.__state)
        infopanel_second = InfopanelSecond(self.__state)
        grid.addWidget(infopanel_first, 0, 0, 1, 10)
        grid.addWidget(infopanel_second, 1, 0, 1, 10)
        #
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.model1)
        #
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper2 = QVXYModelMapper(self)
        self.lineMapper2.setXColumn(0)
        self.lineMapper2.setYColumn(1)
        self.lineMapper2.setSeries(self.vertical_line_series2)
        self.lineMapper2.setModel(self.model2)
        #
        self.vertical_line_series3 = QLineSeries()
        self.vertical_line_series3.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper3 = QVXYModelMapper(self)
        self.lineMapper3.setXColumn(0)
        self.lineMapper3.setYColumn(1)
        self.lineMapper3.setSeries(self.vertical_line_series3)
        self.lineMapper3.setModel(self.model1)
        #
        self.vertical_line_series4 = QLineSeries()
        self.vertical_line_series4.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper4 = QVXYModelMapper(self)
        self.lineMapper4.setXColumn(0)
        self.lineMapper4.setYColumn(1)
        self.lineMapper4.setSeries(self.vertical_line_series4)
        self.lineMapper4.setModel(self.model2)
        #
        self.vertical_line_series5 = QLineSeries()
        self.vertical_line_series5.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper5 = QVXYModelMapper(self)
        self.lineMapper5.setXColumn(0)
        self.lineMapper5.setYColumn(1)
        self.lineMapper5.setSeries(self.vertical_line_series5)
        self.lineMapper5.setModel(self.model1)
        #
        self.vertical_line_series6 = QLineSeries()
        self.vertical_line_series6.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper6 = QVXYModelMapper(self)
        self.lineMapper6.setXColumn(0)
        self.lineMapper6.setYColumn(1)
        self.lineMapper6.setSeries(self.vertical_line_series6)
        self.lineMapper6.setModel(self.model2)
        #
        self.vertical_line_series7 = QLineSeries()
        self.vertical_line_series7.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper7 = QVXYModelMapper(self)
        self.lineMapper7.setXColumn(0)
        self.lineMapper7.setYColumn(1)
        self.lineMapper7.setSeries(self.vertical_line_series7)
        self.lineMapper7.setModel(self.model1)
        #
        self.vertical_line_series8 = QLineSeries()
        self.vertical_line_series8.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper8 = QVXYModelMapper(self)
        self.lineMapper8.setXColumn(0)
        self.lineMapper8.setYColumn(1)
        self.lineMapper8.setSeries(self.vertical_line_series8)
        self.lineMapper8.setModel(self.model2)
        #
        self.vertical_line_series9 = QLineSeries()
        self.vertical_line_series9.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper9 = QVXYModelMapper(self)
        self.lineMapper9.setXColumn(0)
        self.lineMapper9.setYColumn(1)
        self.lineMapper9.setSeries(self.vertical_line_series9)
        self.lineMapper9.setModel(self.model1)
        #
        self.vertical_line_series10 = QLineSeries()
        self.vertical_line_series10.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper10 = QVXYModelMapper(self)
        self.lineMapper10.setXColumn(0)
        self.lineMapper10.setYColumn(1)
        self.lineMapper10.setSeries(self.vertical_line_series10)
        self.lineMapper10.setModel(self.model2)

        ############################################################################
        #program_task_charts_column_names: List[str] = [['vozv_fact', 'vozv_prj'], ['vozv_delta'],  ['a_nepog_fact', 'a_nepog_prj'], ['psi_prj', 'psi_fact'], ['v_wheel_fact', 'v_wheel_prj']]
        charts_vbox = QVBoxLayout()
        column_name = ['vozv_fact', 'vozv_prj']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series1.setPen(QPen(QColor("red"), 2))
        self.chart1 = HorizontalChart((position_min, position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0], series1=[self.series1],
                                        x_tick=100,  # y_tick=20,
                                        title="Уровень, мм",
                                        xMinorTickCount=9, yMinorTickCount=1,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                        levelBoundaryLine1='pass', levelBoundaryLine2='pass')
        self.chart1.legend().hide()
        self.chart1.layout().setContentsMargins(0, 0, 0, 0)
        self.chart1.setMargins(QMargins(0, 0, 0, 0))
        self.chart1.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart1.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart1.addSeries(self.vertical_line_series1)
        self.vertical_line_series1.attachAxis(self.chart1.axisX())
        self.vertical_line_series1.attachAxis(self.chart1.axisY())
        self.chart1.addSeries(self.vertical_line_series2)
        self.vertical_line_series2.attachAxis(self.chart1.axisX())
        self.vertical_line_series2.attachAxis(self.chart1.axisY())
        self.chart_view1 = QChartView(self.chart1)
        self.chart_view1.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view1.setRenderHint(QPainter.Antialiasing)
        charts_vbox.addWidget(self.chart_view1, 2)

        column_name = ['vozv_delta']
        chart_value_range: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series3 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                QCoreApplication.translate(
                                                    'Lining trip/process/view/charts/program task', column_name[0]))
        self.chart2 = HorizontalChart((position_min, position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series3],
                                        x_tick=100,  title="Исправл., мм",              # y_tick=?
                                        xMinorTickCount=9, yMinorTickCount=1,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
        self.chart2.legend().hide()
        self.chart2.layout().setContentsMargins(0, 0, 0, 0)
        self.chart2.setMargins(QMargins(0, 0, 0, 0))
        self.chart2.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart2.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)

        self.chart2.addSeries(self.vertical_line_series3)
        self.vertical_line_series3.attachAxis(self.chart2.axisX())
        self.vertical_line_series3.attachAxis(self.chart2.axisY())
        self.chart2.addSeries(self.vertical_line_series4)
        self.vertical_line_series4.attachAxis(self.chart2.axisX())
        self.vertical_line_series4.attachAxis(self.chart2.axisY())

        self.chart_view2 = QChartView(self.chart2)
        self.chart_view2.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view2.setRenderHint(QPainter.Antialiasing)
        charts_vbox.addWidget(self.chart_view2, 1)

        column_name = ['a_nepog_fact', 'a_nepog_prj']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series4 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series5 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series5.setPen(QPen(QColor("red"), 2))
        self.chart3 = HorizontalChart((position_min, position_max),
                                              self.options.picket_direction == PicketDirection.Backward,
                                              (chart_value_min, chart_value_max), False,
                                              series0=[self.series4], series1=[self.series5],
                                              x_tick=100,  title='Анеп, м/с\u00B2',
                                              xMinorTickCount=9, yMinorTickCount=1,
                                              xGridLineColor="gray", yGridLineColor="gray",
                                              xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                              levelBoundaryLine1=0.7, levelBoundaryLine2=0.7)
        self.chart3.legend().hide()
        self.chart3.layout().setContentsMargins(0, 0, 0, 0)
        self.chart3.setMargins(QMargins(0, 0, 0, 0))
        self.chart3.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart3.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart3.addSeries(self.vertical_line_series5)
        self.vertical_line_series5.attachAxis(self.chart3.axisX())
        self.vertical_line_series5.attachAxis(self.chart3.axisY())
        self.chart3.addSeries(self.vertical_line_series6)
        self.vertical_line_series6.attachAxis(self.chart3.axisX())
        self.vertical_line_series6.attachAxis(self.chart3.axisY())
        chart_view3 = QChartView(self.chart3)
        chart_view3.chart().setBackgroundBrush(QBrush("black"))
        chart_view3.setRenderHint(QPainter.Antialiasing)
        charts_vbox.addWidget(chart_view3, 1)

        column_name = ['psi_prj', 'psi_fact']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series6 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series7 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series6.setPen(QPen(QColor("red"), 2))
        self.chart4 = HorizontalChart((position_min, position_max),
                                              self.options.picket_direction == PicketDirection.Backward,
                                              (chart_value_min, chart_value_max), False,
                                              series0=[self.series6], series1=[self.series7],
                                              x_tick=100, title= (chr(936) + ' (Пси)' + ' м/c\u00B3'),
                                              xMinorTickCount=9, yMinorTickCount=1,
                                              xGridLineColor="gray", yGridLineColor="gray",
                                              xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                              levelBoundaryLine1=0.7, levelBoundaryLine2='pass')
        self.chart4.legend().hide()
        self.chart4.layout().setContentsMargins(0, 0, 0, 0)
        self.chart4.setMargins(QMargins(0, 0, 0, 0))
        self.chart4.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart4.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart4.addSeries(self.vertical_line_series7)
        self.vertical_line_series7.attachAxis(self.chart4.axisX())
        self.vertical_line_series7.attachAxis(self.chart4.axisY())
        self.chart4.addSeries(self.vertical_line_series8)
        self.vertical_line_series8.attachAxis(self.chart4.axisX())
        self.vertical_line_series8.attachAxis(self.chart4.axisY())
        chart_view4 = QChartView(self.chart4)
        chart_view4.chart().setBackgroundBrush(QBrush("black"))
        chart_view4.setRenderHint(QPainter.Antialiasing)
        charts_vbox.addWidget(chart_view4, 1)

        column_name = ['v_wheel_fact', 'v_wheel_prj']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series8 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series9 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series9.setPen(QPen(QColor("red"), 2))
        self.chart5 = HorizontalChart((position_min, position_max),
                                              self.options.picket_direction == PicketDirection.Backward,
                                              (chart_value_min, chart_value_max), False,
                                              series0=[self.series8], series1=[self.series9],
                                              x_tick=100, title="Fv, мм",
                                              xMinorTickCount=9, yMinorTickCount=1,
                                              xGridLineColor="gray", yGridLineColor="gray",
                                              xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                              levelBoundaryLine1=35, levelBoundaryLine2='pass')
        self.chart5.legend().hide()
        self.chart5.layout().setContentsMargins(0, 0, 0, 0)
        self.chart5.setMargins(QMargins(0, 0, 0, 0))
        self.chart5.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart5.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart5.addSeries(self.vertical_line_series9)
        self.vertical_line_series9.attachAxis(self.chart5.axisX())
        self.vertical_line_series9.attachAxis(self.chart5.axisY())
        self.chart5.addSeries(self.vertical_line_series10)
        self.vertical_line_series10.attachAxis(self.chart5.axisX())
        self.vertical_line_series10.attachAxis(self.chart5.axisY())
        chart_view5 = QChartView(self.chart5)
        chart_view5.chart().setBackgroundBrush(QBrush("black"))
        chart_view5.setRenderHint(QPainter.Antialiasing)
        charts_vbox.addWidget(chart_view5, 1)
        self.installEventFilter(self)
        #=================================================================================
        grid.addLayout(charts_vbox, 2, 0, 8, 9)
        rcw = self.__rightColumnWidget()
        grid.addLayout(rcw, 2, 9, 8, 1)
        #self.setWindowTitle("Перерасчёт.Уровень.Скорость")
        self.setWindowTitle("Calculation.Level.Speed")
        self.setLayout(grid)
        self.showMaximized()
        self.setFocus()


    def __escapeFunction(self, value: str = False):
            if value == 'cancelReconstructionSignal':
                pass       # ?
            elif value == 'okReconstructionSignal':
                if len(self.changes_list) > 0:
                    self.passDataSignal.emit(self.changes_list[-1])
            self.closeLevelSpeedSignal.emit("close")


    def __quitLevelSpeed(self):
        self.closeLevelSpeedSignal.emit("close")


    def eventFilter(self, watched: QObject, event: QEvent):
        column_start = self.get_summary_column(self.summary, "start")
        column_end = self.get_summary_column(self.summary, "end")
        if event.type() == QEvent.Type.KeyPress:
            self.setFocus()
            if event.key() == Qt.Key.Key_Right:
                if 0 <= self.counter < (self.summary_len - 1):
                    self.lineMover1.eventFilter('to right', column_start, column_end, self.counter)
                    self.lineMover2.eventFilter('to right', column_start, column_end, self.counter)
                    self.__returnData(self.counter)
                    self.counter = self.counter + 1
                    self.current_segment = self.summary.elements()[self.counter]
                return True
            elif event.key() == Qt.Key.Key_Left:
                if 0 < self.counter < self.summary_len:
                    self.lineMover1.eventFilter('to left', column_start, column_end, self.counter)
                    self.lineMover2.eventFilter('to left', column_start, column_end, self.counter)
                    self.__returnData(self.counter)
                    self.counter = self.counter - 1
                    self.current_segment = self.summary.elements()[self.counter]
                return True
            elif event.key() == Qt.Key.Key_Escape:
                pass
                #self.__quitLevelSpeed()
        return False

    # примет позицию из MainLevel, вернёт диапазон с этой позицией
    def defineRange(self, position):
        result=[]
        for elem in range(0, self.summary_len, 1):
            start = self.summary.elements()[elem].to_dict()['start'] + self.startPicket
            end = self.summary.elements()[elem].to_dict()['end'] + self.startPicket
            if start <= position < end:
                result = [start, end]
                self.counter = elem
        return result

    def __rightColumnWidget(self):
        vbox = QVBoxLayout()
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        #
        vbox_ok = QVBoxLayout()
        ok_btn = QPushButton("Ok")
        ok_btn.clicked.connect(self.__okChangeSpeed)
        ok_lbl = QLabel(" %s \n %s \n %s" % ('Принять', 'все изменения', 'и уйти со страницы'), self)
        vbox_ok.addWidget(ok_lbl, 9)
        vbox_ok.addWidget(ok_btn, 1)
        vbox_cancel = QVBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.__cancelChangeSpeed)
        cancel_lbl = QLabel(" %s \n %s \n %s" % ('Отказаться от', 'всех изменений', 'и уйти со страницы'), self)
        vbox_cancel.addWidget(cancel_lbl, 9)
        vbox_cancel.addWidget(cancel_btn, 1)
        #
        groupbox_speed = QGroupBox()
        groupbox_speed_layout = QHBoxLayout()
        groupbox_speed.setLayout(groupbox_speed_layout)
        speed_label = QLabel("Скорость")
        speed_label.setStyleSheet("font-size: 12pt;")
        self.speed_sb = QSpinBox()
        self.speed_sb.setRange(0, 360)
        #
        #if self.current_segment.geometry.value == "переходная кривая":                                     # !
        #    self.speed_sb.setDisabled(True)
        #
        self.speed_sb.editingFinished.connect(self.__handleSpinBox)
        font = self.speed_sb.font()
        font.setPointSize(12)
        self.speed_sb.setFont(font)
        groupbox_speed_layout.addWidget(speed_label)
        groupbox_speed_layout.addWidget(self.speed_sb)
        #
        value_style = "font: bold; font-size: 12pt;color:white;background-color:black"
        groupbox_bottom = QGroupBox()
        groupbox_bottom_layout = QVBoxLayout()
        groupbox_bottom.setLayout(groupbox_bottom_layout)
        groupbox_bottom_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Натура")
        fact_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.fact_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['vozv_fact'][self.options.start_picket.meters]))
        self.fact_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_bottom_layout_hbox1.addWidget(self.fact_label_value)
        groupbox_bottom_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.prj_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['vozv_prj'][self.options.start_picket.meters]))
        self.prj_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox2.addWidget(prj_label)
        groupbox_bottom_layout_hbox2.addWidget(self.prj_label_value)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox1)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox2)
        #
        corrections_label = QLabel("Исправл.")
        corrections_label.setStyleSheet("font: bold;font-size: 12pt;")  # font: bold;
        self.corrections_label_value = QLabel(str(0))
        self.corrections_label_value.setStyleSheet(value_style)
        hbox2.addWidget(corrections_label)
        hbox2.addWidget(self.corrections_label_value)
        groupbox_bottom.setStyleSheet("background-color:white")
        vbox1.addLayout(hbox1)
        vbox1.addWidget(groupbox_bottom)
        vbox1.addLayout(hbox2)
        #
        groupbox_bottom1 = QGroupBox()
        groupbox_bottom1_layout = QVBoxLayout()
        groupbox_bottom1.setLayout(groupbox_bottom1_layout)
        groupbox_bottom1_layout_hbox1 = QHBoxLayout()
        anep_label = QLabel("Анеп")
        anep_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.anep_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['a_nepog_fact'][self.options.start_picket.meters]))
        self.anep_label_value.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox1.addWidget(anep_label)
        groupbox_bottom1_layout_hbox1.addWidget(self.anep_label_value)
        groupbox_bottom1_layout_hbox2 = QHBoxLayout()
        psi_label = QLabel(chr(936) + ' (Пси)')
        psi_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.psi_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['psi_fact'][self.options.start_picket.meters]))
        self.psi_label_value.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox2.addWidget(psi_label)
        groupbox_bottom1_layout_hbox2.addWidget(self.psi_label_value)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox1)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox2)
        groupbox_bottom1_layout_hbox3 = QHBoxLayout()
        fv_label = QLabel("Fv.")
        fv_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.fv_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['v_wheel_fact'][self.options.start_picket.meters]))
        self.fv_label_value.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox3.addWidget(fv_label)
        groupbox_bottom1_layout_hbox3.addWidget(self.fv_label_value)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox3)
        #
        groupbox_bottom2 = QGroupBox()
        groupbox_bottom2_layout = QVBoxLayout()
        groupbox_bottom2.setLayout(groupbox_bottom2_layout)
        groupbox_bottom2_layout_hbox1 = QHBoxLayout()
        anep_label = QLabel("Анеп")
        anep_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.anep_label_value = QLabel(str(
            self.__state.calculation_result().calculated_task.data['a_nepog_prj'][self.options.start_picket.meters]))
        self.anep_label_value.setStyleSheet(value_style)
        groupbox_bottom2_layout_hbox1.addWidget(anep_label)
        groupbox_bottom2_layout_hbox1.addWidget(self.anep_label_value)
        groupbox_bottom2_layout_hbox2 = QHBoxLayout()
        psi_label = QLabel(chr(936) + ' (Пси)')
        psi_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.psi_label_value = QLabel(
            str(self.__state.calculation_result().calculated_task.data['psi_prj'][self.options.start_picket.meters]))
        self.psi_label_value.setStyleSheet(value_style)
        groupbox_bottom2_layout_hbox2.addWidget(psi_label)
        groupbox_bottom2_layout_hbox2.addWidget(self.psi_label_value)
        groupbox_bottom2_layout.addLayout(groupbox_bottom2_layout_hbox1)
        groupbox_bottom2_layout.addLayout(groupbox_bottom2_layout_hbox2)
        groupbox_bottom2_layout_hbox3 = QHBoxLayout()
        fv_label = QLabel("Fv.")
        fv_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.fv_label_value = QLabel(str(
            self.__state.calculation_result().calculated_task.data['v_wheel_prj'][self.options.start_picket.meters]))
        self.fv_label_value.setStyleSheet(value_style)
        groupbox_bottom2_layout_hbox3.addWidget(fv_label)
        groupbox_bottom2_layout_hbox3.addWidget(self.fv_label_value)
        groupbox_bottom2_layout.addLayout(groupbox_bottom2_layout_hbox3)
        ##########################################
        vbox.addStretch(3)
        vbox.addLayout(vbox_ok) #ok_btn)
        vbox.addLayout(vbox_cancel) #cancel_btn)
        vbox.addStretch(1)
        vbox.addWidget(groupbox_speed)
        vbox.addLayout(vbox1)
        vbox.addWidget(groupbox_bottom1)
        vbox.addWidget(groupbox_bottom2)
        return vbox


    def __okChangeSpeed(self):
        self.okChangeSpeedSignal.emit("ok")

    def __cancelChangeSpeed(self):
        self.cancelChangeSpeedSignal.emit("cancel")

    # Получить колонку from summary
    def get_summary_column(self, summary_file:list, column_name: str):
        column = []
        for every_dict in summary_file.elements():
            column.append(every_dict.to_dict()[column_name])
        return column


    def __handleSpinBox(self):
        value = self.speed_sb.value()
        self.setFocus()

        # установка значений в окна
    def __returnData(self, counter: int):
        current_segment = self.summary.elements()[counter]
        self.prj_label_value.setNum(
            round(current_segment.level_norm, 1)) if current_segment.level_norm else self.prj_label_value.setNum(0)
        #self.fact_label_value.setNum()
        # self.anep_label_value_prj.setNum(round(current_segment.a_nepog_norm,
        #                                        1)) if current_segment.a_nepog_norm else self.anep_label_value_prj.setNum(0)
        # self.psi_label_value_prj.setNum(
        #         round(current_segment.psi_norm, 1)) if current_segment.psi_norm else self.psi_label_value_prj.setNum(0)
        # self.fv_label_value_prj.setNum(
        #         round(current_segment.v_max_norm, 1)) if current_segment.v_max_norm else self.fv_label_value_prj.setNum(0)
