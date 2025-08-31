
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication,QHBoxLayout, QGridLayout, QLabel
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QPointF, QMargins
import sys
import numpy as np
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.models import VerticalLineModel
from domain.calculations.plan_model import TrackProjectModel,  TrackProjectType

class Chart1(QWidget):
    def __init__(self, chart_column_name1: str,
                 chart_column_name2:str,
                 model1: VerticalLineModel,
                 model2: VerticalLineModel,
                 model3: VerticalLineModel,
                 calculation_result: ProgramTaskCalculationResultDto,
                 parent: QWidget = None):
        super().__init__(parent)
        self.vertical_model1 = model1
        self.vertical_model2 = model2
        self.vertical_model3 = model3
        self.chart_column_name1 = chart_column_name1
        self.chart_column_name2 = chart_column_name2
        self.__calculation_result = calculation_result
        programTaskModel = StepIndexedDataFramePositionedModel(
            self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step,
            self)
        programTaskModel.reset(self.__calculation_result.calculated_task.step,
                                  self.__calculation_result.calculated_task.data)
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        self.position_min: float = position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        self.position_max: float = position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(self.chart_column_name1)
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(self.chart_column_name2)
        chart_value_range = ( min(chart_value_range0[0], chart_value_range1[0]),
                              max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                             programTaskModel.modelColumnIndexAtName(self.chart_column_name1),
                                             QCoreApplication.translate(
                                                 'Lining trip/process/view/charts/program task', self.chart_column_name1))
        self.series0.setPen(QPen(QColor("red"), 2))
        self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                             programTaskModel.modelColumnIndexAtName(self.chart_column_name2),
                                             QCoreApplication.translate(
                                                 'Lining trip/process/view/charts/program task', self.chart_column_name2))
        self.series1.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart = HorizontalChart ( (self.position_min, self.position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0], series1=[self.series1],
                                        x_tick=100, y_tick=10,
                                        title="Стрелы изгиба, мм", xMinorTickCount = 9,
                                        xGridLineColor = "gray", yGridLineColor = "gray",
                                        xMinorGridLineColor = "gray", yMinorGridLineColor = "gray")
        self.chart.legend().hide()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart_view = QChartView(self.chart)
        self.chart_view.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setFocusPolicy(Qt.NoFocus)
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.vertical_line_series3 = QLineSeries()
        self.vertical_line_series3.setPen(QPen(Qt.GlobalColor.yellow, 2))
        #
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.vertical_model1)
        self.lineMapper2 = QVXYModelMapper(self)
        self.lineMapper2.setXColumn(0)
        self.lineMapper2.setYColumn(1)
        self.lineMapper2.setSeries(self.vertical_line_series2)
        self.lineMapper2.setModel(self.vertical_model2)
        self.lineMapper3 = QVXYModelMapper(self)
        self.lineMapper3.setXColumn(0)
        self.lineMapper3.setYColumn(1)
        self.lineMapper3.setSeries(self.vertical_line_series3)
        self.lineMapper3.setModel(self.vertical_model3)
        #
        self.chart.addSeries(self.vertical_line_series1)
        self.chart.addSeries(self.vertical_line_series2)
        self.chart.addSeries(self.vertical_line_series3)
        self.vertical_line_series1.attachAxis(self.chart.axisX())
        self.vertical_line_series1.attachAxis(self.chart.axisY())
        self.vertical_line_series2.attachAxis(self.chart.axisX())
        self.vertical_line_series2.attachAxis(self.chart.axisY())
        self.vertical_line_series3.attachAxis(self.chart.axisX())
        self.vertical_line_series3.attachAxis(self.chart.axisY())
        #
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

class Chart2(QWidget):
    def __init__(self, chart_column_name: str,
                 calculation_result: ProgramTaskCalculationResultDto,
                 parent: QWidget = None):
        super().__init__(parent)
        self.chart_column_name = chart_column_name
        self.__calculation_result = calculation_result
        programTaskModel = StepIndexedDataFramePositionedModel(
            self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step, self)
        programTaskModel.reset(self.__calculation_result.calculated_task.step,
                                  self.__calculation_result.calculated_task.data)
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        self.position_min: float = position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        self.position_max: float = position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        chart_value_range: (float, float) = programTaskModel.minmaxValueByColumn(self.chart_column_name)
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        self.chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        self.chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                        programTaskModel.modelColumnIndexAtName(self.chart_column_name),
                                        QCoreApplication.translate(
                                            'Lining trip/process/view/charts/program task', self.chart_column_name))
        self.series.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart = HorizontalChart((self.position_min, self.position_max),
                                 self.options.picket_direction == PicketDirection.Backward,
                                 (self.chart_value_min, self.chart_value_max), False, series0=[self.series],
                                 x_tick=100, y_tick=10,
                                 title="Сдвиги, мм", xMinorTickCount=9,
                                 xGridLineColor="gray", yGridLineColor="gray",
                                 xMinorGridLineColor="gray", yMinorGridLineColor="gray")
        self.chart.legend().hide()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setFocusPolicy(Qt.NoFocus)
        self.chart_view.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

class ChartsWidget(QWidget):
    def __init__(self, chart1:QWidget, chart2:QWidget, calculation_result: ProgramTaskCalculationResultDto):
        super().__init__()
        self.__calculation_result = calculation_result
        self.chart1 = chart1
        self.chart2 = chart2
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart1, 2)
        vbox.addWidget(self.chart2, 1)
        self.setLayout(vbox)
