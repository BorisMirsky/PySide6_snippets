
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QApplication, QPushButton, QLineEdit, QSpinBox, QComboBox,
                               QHBoxLayout, QGridLayout, QLabel, QMessageBox, QGroupBox)
from PySide6.QtGui import QFont, QShortcut, Qt, QPen, QPainter, QColor, QBrush, QIntValidator, QKeySequence
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from domain.dto.Workflow import ProgramTaskCalculationResultDto, ProgramTaskBaseData
from domain.calculations.progtask import machine_task_from_base_data_new
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from .....common.viewes.CircliBusyIndicator import CircliBusyIndicator
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from .VerticalLine import VerticalLineModel, MoveLineController
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent2
import math


focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"




class LevelReconstructionWidget(QWidget):
    passDataSignal = Signal(TrackProjectModel)
    closeLevelReconstructionSignal = Signal(str)
    okReconstructionSignal = Signal(str)
    cancelReconstructionSignal = Signal(str)
    runSpinnerSignal = Signal(str)
    stopSpinnerSignal = Signal(str)
    updateCalculationResultSignal = Signal(ProgramTaskCalculationResultDto)
    def __init__(self, calculation_result: ProgramTaskCalculationResultDto, parent: QWidget = None):
        super().__init__(parent)
        self.position = 0
        self.__calculation_result = calculation_result#
        programTaskModel: AbstractPositionedTableModel = StepIndexedDataFramePositionedModel(self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step, self)
        programTaskModel.reset(self.__calculation_result.calculated_task.step, self.__calculation_result.calculated_task.data)
        self.plan_model = TrackProjectModel.create(TrackProjectType.Level, self.__calculation_result)
        self.updatedData: TrackProjectModel = None
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        #
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        self.position_min: float = self.position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        self.position_max: float = self.position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        #
        self.changes_list: list = []
        self.changes_list.append(self.plan_model)
        self.unsavedChanges: bool = False
        self.summary_len = len(self.plan_model.elements())
        self.counter = 0

        self.current_segment = self.plan_model.elements()[self.counter]
        self.segment_type = self.current_segment.geometry.value
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.range_points = self.defineRange(self.position)
        #
        self.okReconstructionSignal.connect(lambda: self.__escapeFunction('okReconstructionSignal'))
        self.cancelReconstructionSignal.connect(lambda: self.__escapeFunction('cancelReconstructionSignal'))
        #
        self.model1 = VerticalLineModel(self.options.start_picket.meters)
        self.model2 = VerticalLineModel(self.options.start_picket.meters +
                                        self.position_multiplyer * self.plan_model.elements()[0].to_dict()['end'])
        self.lineMover1 = MoveLineController(self.model1, self.model2, self.startPicket, self.__calculation_result)
        self.lineMover2 = MoveLineController(self.model1, self.model2, self.startPicket, self.__calculation_result)
        #
        grid = QGridLayout()
        infopanel_first = InfopanelFirst(self.__calculation_result)
        infopanel_second = InfopanelSecond(self.__calculation_result)
        title_window = LabelOnParent2('ВНР. Переустройство', 500, 0, 250, 40, infopanel_first)
        title_window.setWordWrap(True)
        title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        grid.addWidget(infopanel_first, 0, 0, 1, 10)
        grid.addWidget(infopanel_second, 1, 0, 1, 10)
        #
        # #=============================================== Charts ===================================================
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
        charts_vbox = QVBoxLayout()
        column_name = ['vozv_fact', 'vozv_prj']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        self.chart1_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        self.chart1_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series0.setPen(QPen(QColor("#2f8af0"), 2))
        self.series1.setPen(QPen(QColor("red"), 2))
        self.chart1 = HorizontalChart((self.position_min, self.position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (self.chart1_value_min, self.chart1_value_max), False,
                                        series0=[self.series0], series1=[self.series1],
                                        x_tick=100,  y_tick=10,
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
        self.chart_view1.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view1, 2)

        column_name = ['vozv_delta']
        chart_value_range: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        self.chart2_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        self.chart2_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series3 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                QCoreApplication.translate(
                                                    'Lining trip/process/view/charts/program task', column_name[0]))
        self.series3.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart2 = HorizontalChart((self.position_min, self.position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (self.chart2_value_min, self.chart2_value_max), False,
                                        series0=[self.series3],
                                        x_tick=100,  y_tick=10, title="Исправл., мм",
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
        self.chart_view2.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view2, 1)

        column_name = ['a_nepog_fact', 'a_nepog_prj']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0], 0.7, -0.7),
                             max(chart_value_range0[1], chart_value_range1[1], 0.7, -0.7))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        self.chart3_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        self.chart3_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series4 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series5 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series4.setPen(QPen(QColor("#2f8af0"), 2))
        self.series5.setPen(QPen(QColor("red"), 2))
        self.chart3 = HorizontalChart((self.position_min, self.position_max),
                                              self.options.picket_direction == PicketDirection.Backward,
                                              (self.chart3_value_min, self.chart3_value_max), False,
                                              series0=[self.series4], series1=[self.series5],
                                              x_tick=100,  y_tick=10, title='Анеп, м/с\u00B2',
                                              xMinorTickCount=9, yMinorTickCount=1,
                                              xGridLineColor="gray", yGridLineColor="gray",
                                              xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                              levelBoundaryLine1=0.7, levelBoundaryLine2=-0.7)
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
        self.chart_view3 = QChartView(self.chart3)
        self.chart_view3.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view3.setRenderHint(QPainter.Antialiasing)
        self.chart_view3.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view3, 1)

        column_name = ['psi_prj', 'psi_fact']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0], 0.7), max(chart_value_range0[1], chart_value_range1[1], 0.7))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        self.chart4_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        self.chart4_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series6 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series7 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series7.setPen(QPen(QColor("#2f8af0"), 2))
        self.series6.setPen(QPen(QColor("red"), 2))
        self.chart4 = HorizontalChart((self.position_min, self.position_max),
                                              self.options.picket_direction == PicketDirection.Backward,
                                              (self.chart4_value_min, self.chart4_value_max), False,
                                              series0=[self.series6], series1=[self.series7],
                                              x_tick=100, y_tick=10,
                                              title= (chr(936) + ' (Пси)' + ' м/c\u00B3'),
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
        self.chart_view4 = QChartView(self.chart4)
        self.chart_view4.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view4.setRenderHint(QPainter.Antialiasing)
        self.chart_view4.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view4, 1)

        column_name = ['v_wheel_fact', 'v_wheel_prj']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0], 35), max(chart_value_range0[1], chart_value_range1[1], 35))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        self.chart5_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        self.chart5_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series8 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
        self.series9 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
        self.series9.setPen(QPen(QColor("red"), 2))
        self.series8.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart5 = HorizontalChart((self.position_min, self.position_max),
                                              self.options.picket_direction == PicketDirection.Backward,
                                              (self.chart5_value_min, self.chart5_value_max), False,
                                              series0=[self.series8], series1=[self.series9],
                                              x_tick=100, y_tick=10, title="Fv, мм/м",
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
        self.chart_view5 = QChartView(self.chart5)
        self.chart_view5.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view5.setRenderHint(QPainter.Antialiasing)
        self.chart_view5.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view5, 1)
        self.installEventFilter(self)
        #
        self.correctionsSpinboxValue =  QSpinBox()
        font = self.correctionsSpinboxValue.font()
        font.setPointSize(15)
        self.correctionsSpinboxValue.setFont(font)
        self.correctionsSpinboxValue.setStyleSheet(focus_style)
        self.correctionsSpinboxValue.setRange(-150, 150)
        if self.current_segment.geometry.value == "переходная кривая":
            self.correctionsSpinboxValue.setDisabled(True)
        self.btn_corrections = QPushButton('Ok')
        self.btn_corrections.setStyleSheet(focus_style)
        self.btn_corrections.setProperty("optionsWindowPushButton", True)
        self.btn_corrections.setFixedWidth(80)
        self.btn_corrections.clicked.connect(self.__rerenderCharts)
        #
        self.zoom_value = 0
        self.x_start = self.position_min
        self.x_stop = self.position_max
        self.zoom_factor = (self.x_stop - self.x_start) / 20
        self.shift_chart_to_left_shortcut = QShortcut(QKeySequence('Alt+Left'), self)
        self.shift_chart_to_left_shortcut.activated.connect(self.shift_chart_to_left)
        self.shift_chart_to_right_shortcut = QShortcut(QKeySequence('Alt+Right'), self)
        self.shift_chart_to_right_shortcut.activated.connect(self.shift_chart_to_right)
        #=================================================================================
        grid.addLayout(charts_vbox, 2, 0, 8, 9)
        rcw = self.rightColumnWidget()
        grid.addLayout(rcw, 2, 9, 8, 1)
        self.setLayout(grid)


    def __escapeFunction(self, value: str = False):
        if self.unsavedChanges:
            if value == 'cancelReconstructionSignal':
                self.__rollback(0)
            elif value == 'okReconstructionSignal':
                if len(self.changes_list) > 0:
                    self.update_level(self.new_plan_model)
                    self.passDataSignal.emit(self.changes_list[-1])
        self.closeLevelReconstructionSignal.emit("close")


    # примет точку, вернёт диапазон точки
    # ОТВАЛИЛОСЬ                                                                        !!!
    def defineRange(self, position):
        result=[]
        for elem in range(0, self.summary_len, 1):
            #start = self.summary.elements()[elem].to_dict()['start'] + self.startPicket
            start = self.plan_model.elements()[elem].to_dict()['start'] + self.startPicket
            #end = self.summary.elements()[elem].to_dict()['end'] + self.startPicket
            end = self.plan_model.elements()[elem].to_dict()['end'] + self.startPicket
            if start <= position < end:
                result = [start, end]
                self.counter = elem
        return result


    def __quitLevelReconstruction(self):
        self.closeLevelReconstructionSignal.emit("close")

    def shift_chart_to_left(self):
        self.x_start = self.x_start - self.zoom_factor
        self.x_stop = self.x_stop - self.zoom_factor
        self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view3.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view4.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view5.chart().axisX().setRange(self.x_start, self.x_stop)

    def shift_chart_to_right(self):
        self.x_start = self.x_start + self.zoom_factor
        self.x_stop = self.x_stop + self.zoom_factor
        self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view3.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view4.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view5.chart().axisX().setRange(self.x_start, self.x_stop)

    def eventFilter(self, watched: QObject, event: QEvent):
        column_start = self.get_summary_column(self.plan_model, "start")
        column_end = self.get_summary_column(self.plan_model, "end")
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Right:
                if 0 <= self.counter < (self.summary_len - 1):
                    self.counter = self.counter + 1
                    self.lineMover1.eventFilter('to right', column_start, column_end)
                    self.lineMover2.eventFilter('to right', column_start, column_end)
                    self.__returnData(self.counter)
            elif event.key() == Qt.Key.Key_Left:
                if 0 < self.counter < self.summary_len:
                    self.counter = self.counter - 1
                    self.lineMover1.eventFilter('to left', column_start, column_end)
                    self.lineMover2.eventFilter('to left', column_start, column_end)
                    self.__returnData(self.counter)
            elif event.key() == Qt.Key.Key_PageUp and self.zoom_value < 10:
                self.x_start = round(self.x_start + self.zoom_factor)
                self.x_stop = round(self.x_stop - self.zoom_factor)
                if (self.x_stop + self.zoom_factor) > self.position_max:
                    self.x_stop = self.position_max
                self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view3.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view4.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view5.chart().axisX().setRange(self.x_start, self.x_stop)
                self.zoom_value = self.zoom_value + 1
            elif event.key() == Qt.Key.Key_PageDown and self.zoom_value > 0:
                self.x_start = round(self.x_start - self.zoom_factor)
                self.x_stop = round(self.x_stop + self.zoom_factor)
                if (self.x_start - self.zoom_factor) < self.position_min:
                    self.x_start = self.position_min
                self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view3.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view4.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view5.chart().axisX().setRange(self.x_start, self.x_stop)
                self.zoom_value = self.zoom_value - 1
            elif event.key() == Qt.Key.Key_Backspace:
                self.__rollback(-2)
        return False

    def rightColumnWidget(self):
        vbox = QVBoxLayout()
        vbox1 = QVBoxLayout()
        hbox2 = QHBoxLayout()
        value_style = "font: bold; font-size: 12pt;color:white;background-color:black"
        groupbox_speed = QGroupBox()
        groupbox_speed_layout = QHBoxLayout()
        groupbox_speed.setLayout(groupbox_speed_layout)
        speed_label = QLabel("Скорость")
        speed_label.setStyleSheet("font-size: 12pt;")
        self.speed_sb = QComboBox()
        self.speed_sb.setStyleSheet(focus_style)
        self.speed_sb.addItem(str(self.options.restrictions['segments'][0]['v_gruz']))  # 80
        self.speed_sb.addItem(str(self.options.restrictions['segments'][0]['v_pass']))  # 120
        font = self.speed_sb.font()
        font.setPointSize(12)
        self.speed_sb.setFont(font)
        groupbox_speed_layout.addWidget(speed_label)
        groupbox_speed_layout.addWidget(self.speed_sb)
        groupbox_bottom = QGroupBox()
        groupbox_bottom_layout = QVBoxLayout()
        groupbox_bottom.setLayout(groupbox_bottom_layout)
        groupbox_bottom_layout_hbox1 = QHBoxLayout()
        #
        vbox_ok = QVBoxLayout()
        ok_btn = QPushButton("Ok")
        ok_btn.setStyleSheet(focus_style)
        ok_btn.setProperty("optionsWindowPushButton", True)
        ok_btn.clicked.connect(self.__okReconstruction)
        ok_lbl = QLabel(" %s \n %s \n %s" % ('Принять', 'все изменения', 'и уйти со страницы'), self)
        vbox_ok.addWidget(ok_lbl, 9)
        vbox_ok.addWidget(ok_btn, 1)
        vbox_cancel = QVBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet(focus_style)
        cancel_btn.setProperty("optionsWindowPushButton", True)
        cancel_btn.clicked.connect(self.__cancelReconstruction)
        cancel_lbl = QLabel(" %s \n %s \n %s" % ('Отказаться от', 'всех изменений', 'и уйти со страницы'), self)
        vbox_cancel.addWidget(cancel_lbl, 9)
        vbox_cancel.addWidget(cancel_btn, 1)
        #
        #fact_label = QLabel("Натура")
        #fact_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        #fact_label_value = QLabel(str(0))
        #fact_label_value.setStyleSheet(value_style)
        #groupbox_bottom_layout_hbox1.addWidget(fact_label)
        #groupbox_bottom_layout_hbox1.addWidget(fact_label_value)
        groupbox_bottom_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.prj_label_value = QLabel()
        self.prj_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox2.addWidget(prj_label)
        groupbox_bottom_layout_hbox2.addWidget(self.prj_label_value)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox1)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox2)
        corrections_label = QLabel("Исправл.")
        corrections_label.setStyleSheet("font: bold; font-size: 12pt;")
        hbox2.addWidget(corrections_label)
        #self.correctionsSpinboxValue.setStyleSheet(value_style)
        hbox2.addWidget(self.correctionsSpinboxValue)
        groupbox_bottom.setStyleSheet("background-color:white")
        vbox1.addWidget(groupbox_bottom)
        vbox1.addLayout(hbox2)
        vbox1.addWidget(self.btn_corrections)
        groupbox_bottom1 = QGroupBox()
        groupbox_bottom1_layout = QVBoxLayout()
        groupbox_bottom1.setLayout(groupbox_bottom1_layout)
        groupbox_bottom1_layout_hbox1 = QHBoxLayout()
        self.anep_label_value_prj = QLabel(str(0))
        self.anep_label_value_prj.setStyleSheet(value_style)
        anep_label_value = QLabel("Анеп")
        anep_label_value.setStyleSheet("font: bold; font-size: 12pt;color:red")
        groupbox_bottom1_layout_hbox1.addWidget(anep_label_value)
        groupbox_bottom1_layout_hbox1.addWidget(self.anep_label_value_prj)
        groupbox_bottom1_layout_hbox2 = QHBoxLayout()
        psi_label = QLabel(chr(936) + ' (Пси)')
        psi_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.psi_label_value_prj = QLabel(str(0))
        self.psi_label_value_prj.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox2.addWidget(psi_label)
        groupbox_bottom1_layout_hbox2.addWidget(self.psi_label_value_prj)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox1)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox2)
        groupbox_bottom1_layout_hbox3 = QHBoxLayout()
        fv_label = QLabel("Fv.")
        fv_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.fv_label_value_prj = QLabel(str(0))
        self.fv_label_value_prj.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox3.addWidget(fv_label)
        groupbox_bottom1_layout_hbox3.addWidget(self.fv_label_value_prj)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox3)
        #
        vbox.addStretch(3)
        vbox.addLayout(vbox_ok)
        vbox.addLayout(vbox_cancel)
        vbox.addStretch(5)
        vbox.addWidget(groupbox_speed)
        vbox.addLayout(vbox1)
        vbox.addWidget(groupbox_bottom1)
        return vbox

    def __okReconstruction(self):
        self.okReconstructionSignal.emit("ok")

    def __cancelReconstruction(self):
        self.cancelReconstructionSignal.emit("cancel")

    # Отмена изменений в зависимости от переданного аргумента:
    #     '0' - сброс всех изменений
    #     '-2' -отказ от последнего изменения
    def __rollback(self, idx: int):
        if len(self.changes_list) > 1:
            self.series1.clear()
            self.series3.clear()
            self.series5.clear()
            self.series6.clear()
            self.series9.clear()
            startPicket = self.options.start_picket.meters
            scale = 6
            for i in range(0, self.changes_list[idx].data.shape[0], 1):
                if i % scale == 0:
                    self.series1.append(startPicket, self.changes_list[idx].data.loc[:, 'vozv_prj'][i])
                    self.series3.append(startPicket, self.changes_list[idx].data.loc[:, 'vozv_prj'][i] -
                                        self.changes_list[idx].data.loc[:, 'vozv_fact'][i])
                    self.series5.append(startPicket, self.changes_list[idx].data.loc[:, 'a_nepog_prj'][i])
                    self.series6.append(startPicket, self.changes_list[idx].data.loc[:, 'psi_prj'][i])
                    self.series9.append(startPicket, self.changes_list[idx].data.loc[:, 'v_wheel_prj'][i])
                startPicket += self.plan_model.step * self.position_multiplyer
            self.chart_view1.update()
            self.chart_view2.update()
            self.chart_view3.update()
            self.chart_view4.update()
            self.chart_view5.update()
            chart1Min = min(0, self.changes_list[idx].data.loc[:, 'vozv_prj'].min(),
                            self.changes_list[idx].data.loc[:, 'vozv_fact'].min())
            chart1Max = max(0, self.changes_list[idx].data.loc[:, 'vozv_prj'].max(),
                            self.changes_list[idx].data.loc[:, 'vozv_fact'].max())
            chart1Padding = (chart1Max - chart1Min) * 0.05
            self.chart_view1.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
            #
            self.changes_list[idx].data['vozv_delta'] = self.changes_list[idx].data.loc[:,'vozv_prj'] - self.changes_list[idx].data.loc[:, 'vozv_fact']
            chart2Min = min(0, self.changes_list[idx].data.loc[:, 'vozv_delta'].min())
            chart2Max = max(0, self.changes_list[idx].data.loc[:, 'vozv_delta'].max())
            chart2Padding = (chart2Max - chart2Min) * 0.05
            self.chart_view2.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
            #
            chart3Min = min(0, self.changes_list[idx].data.loc[:, 'a_nepog_fact'].min(), 0.7, -0.7,
                            self.changes_list[idx].data.loc[:, 'a_nepog_prj'].min())
            chart3Max = max(0, self.changes_list[idx].data.loc[:, 'a_nepog_fact'].max(), 0.7, -0.7,
                            self.changes_list[idx].data.loc[:, 'a_nepog_prj'].max())
            chart3Padding = (chart3Max - chart3Min) * 0.05
            self.chart_view3.chart().axisY().setRange(chart3Min - chart3Padding, chart3Max + chart3Padding)
            #
            chart4Min = min(0, self.changes_list[idx].data.loc[:, 'psi_prj'].min(), 0.7,
                            self.changes_list[idx].data.loc[:, 'psi_fact'].min())
            chart4Max = max(0, self.changes_list[idx].data.loc[:, 'psi_prj'].max(), 0.7,
                            self.changes_list[idx].data.loc[:, 'psi_fact'].max())
            chart4Padding = (chart4Max - chart4Min) * 0.05
            self.chart_view4.chart().axisY().setRange(chart4Min - chart4Padding, chart4Max + chart4Padding)
            #
            chart5Min = min(0, self.changes_list[idx].data.loc[:, 'v_wheel_fact'].min(), 0.7,
                            self.changes_list[idx].data.loc[:, 'v_wheel_prj'].min())
            chart5Max = max(0, self.changes_list[idx].data.loc[:, 'v_wheel_fact'].max(), 0.7,
                            self.changes_list[idx].data.loc[:, 'v_wheel_prj'].max())
            chart5Padding = (chart5Max - chart5Min) * 0.05
            self.chart_view5.chart().axisY().setRange(chart5Min - chart5Padding, chart5Max + chart5Padding)
            #
            self.plan_model = self.changes_list[idx]
            if idx == -2:
                del self.changes_list[-1]
            self.set_coords_current_segment(self.plan_model.elements(), self.counter)
            self.chart_view1.chart().axisX().setRange(self.position_min, self.position_max)
            self.chart_view2.chart().axisX().setRange(self.position_min, self.position_max)
            self.chart_view3.chart().axisX().setRange(self.position_min, self.position_max)
            self.chart_view4.chart().axisX().setRange(self.position_min, self.position_max)
            self.chart_view5.chart().axisX().setRange(self.position_min, self.position_max)
            self.setFocus()


    # перерисовка графиков
    def __rerenderCharts(self):
        if self.current_segment.geometry.value == "круговая кривая":
            value = self.correctionsSpinboxValue.value()
            self.series1.clear()    # 'vozv_prj'
            self.series3.clear()    # 'new_vozv_delta'    previous - 'vozv_delta'
            self.series5.clear()    # 'a_nepog_prj'
            self.series6.clear()    # 'psi_prj'
            self.series9.clear()    # 'v_wheel_prj'
            curve = self.get_summary_row(self.plan_model.elements(), self.counter)
            curve.new_level = value
            try:
                self.new_plan_model = self.plan_model.calc_new_track()
                self.updatedData = self.new_plan_model
                startPicket = self.options.start_picket.meters
                # новая колонка 'Исправления'
                self.new_plan_model.data['new_vozv_delta'] = self.new_plan_model.data.loc[:, 'vozv_prj'] - self.new_plan_model.data.loc[:, 'vozv_fact']
                scale = 6
                for i in range(0, self.new_plan_model.data.shape[0], 1):
                    if i % scale == 0:
                        self.series1.append(startPicket, self.new_plan_model.data.loc[:, 'vozv_prj'][i])
                        self.series3.append(startPicket, self.new_plan_model.data.loc[:, 'new_vozv_delta'][i])
                        self.series5.append(startPicket, self.new_plan_model.data.loc[:, 'a_nepog_prj'][i])
                        self.series6.append(startPicket, self.new_plan_model.data.loc[:, 'psi_prj'][i])
                        self.series9.append(startPicket, self.new_plan_model.data.loc[:, 'v_wheel_prj'][i])
                    startPicket += self.plan_model.step * self.position_multiplyer
                self.chart_view1.update()
                self.chart_view2.update()
                self.chart_view3.update()
                self.chart_view4.update()
                self.chart_view5.update()
                #
                chart1Min = min(0, self.new_plan_model.data.loc[:, 'vozv_prj'].min(),
                                    self.new_plan_model.data.loc[:, 'vozv_fact'].min(), self.chart1_value_min)
                chart1Max = max(0, self.new_plan_model.data.loc[:, 'vozv_prj'].max(),
                                    self.new_plan_model.data.loc[:, 'vozv_fact'].max(), self.chart1_value_max)
                chart1Padding = (chart1Max - chart1Min) * 0.05
                self.chart_view1.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
                y_tick1 = self.set_axis_ticks_step(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding)))
                if type(y_tick1) == float:
                    self.chart_view1.chart().axisY().setLabelFormat("%2g")
                else:
                    self.chart_view1.chart().axisY().setLabelFormat("%d")
                self.chart_view1.chart().axisY().setTickInterval(y_tick1)
                #
                chart2Min = min(0, self.new_plan_model.data.loc[:, 'new_vozv_delta'].min()) #, self.chart2_value_min)
                #chart2Min = min(0, self.new_plan_model.data['new_vozv_delta'].min()) #, self.chart2_value_min)
                chart2Max = max(0, self.new_plan_model.data.loc[:, 'new_vozv_delta'].max()) #, self.chart2_value_max)
                #chart2Max = max(0, self.new_plan_model.data['new_vozv_delta'].max()) #, self.chart2_value_max)
                #print('chart2Min, chart2Max ', chart2Min, chart2Max)
                chart2Padding = (chart2Max - chart2Min) * 0.05
                self.chart_view2.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
                y_tick2 = self.set_axis_ticks_step(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding)))
                if type(y_tick2) == float:
                    self.chart_view2.chart().axisY().setLabelFormat("%2g")
                else:
                    self.chart_view2.chart().axisY().setLabelFormat("%d")
                self.chart_view2.chart().axisY().setTickInterval(y_tick2)
                #
                chart3Min = min(0, self.new_plan_model.data.loc[:, 'a_nepog_fact'].min(), 0.7,
                                self.new_plan_model.data.loc[:, 'a_nepog_prj'].min(), self.chart3_value_min)
                chart3Max = max(0, self.new_plan_model.data.loc[:, 'a_nepog_fact'].max(), 0.7,
                                self.new_plan_model.data.loc[:, 'a_nepog_prj'].max(), self.chart3_value_max)
                chart3Padding = (chart3Max - chart3Min) * 0.05
                self.chart_view3.chart().axisY().setRange(chart3Min - chart3Padding, chart3Max + chart3Padding)
                y_tick3 = self.set_axis_ticks_step(math.fabs((chart3Min - chart3Padding) - (chart3Max + chart3Padding)))
                self.chart_view3.chart().axisY().setTickInterval(y_tick3)
                if type(y_tick3) == float:
                    self.chart_view3.chart().axisY().setLabelFormat("%2g")
                else:
                    self.chart_view3.chart().axisY().setLabelFormat("%d")
                self.chart_view3.chart().axisY().setRange(chart3Min - chart3Padding, chart3Max + chart3Padding)
                #
                chart4Min = min(0, self.new_plan_model.data.loc[:, 'psi_prj'].min(), 0.7,
                                self.new_plan_model.data.loc[:, 'psi_fact'].min(), self.chart4_value_min)
                chart4Max = max(0, self.new_plan_model.data.loc[:, 'psi_prj'].max(), 0.7,
                                self.new_plan_model.data.loc[:, 'psi_fact'].max(), self.chart4_value_max)
                chart4Padding = (chart4Max - chart4Min) * 0.05
                self.chart_view4.chart().axisY().setRange(chart4Min - chart4Padding, chart4Max + chart4Padding)
                y_tick4 = self.set_axis_ticks_step(math.fabs((chart4Min - chart4Padding) - (chart4Max + chart4Padding)))
                self.chart_view4.chart().axisY().setTickInterval(y_tick4)
                if type(y_tick4) == float:
                    self.chart_view4.chart().axisY().setLabelFormat("%2g")
                else:
                    self.chart_view4.chart().axisY().setLabelFormat("%d")
                #
                chart5Min = min(0, self.new_plan_model.data.loc[:, 'v_wheel_fact'].min(), 35,
                                self.new_plan_model.data.loc[:, 'v_wheel_prj'].min(), self.chart5_value_min)
                chart5Max = max(0, self.new_plan_model.data.loc[:, 'v_wheel_fact'].max(), 35,
                                self.new_plan_model.data.loc[:, 'v_wheel_prj'].max(), self.chart5_value_max)
                chart5Padding = (chart5Max - chart5Min) * 0.05
                self.chart_view5.chart().axisY().setRange(chart5Min - chart5Padding, chart5Max + chart5Padding)
                y_tick5 = self.set_axis_ticks_step(math.fabs((chart5Min - chart5Padding) - (chart5Max + chart5Padding)))
                self.chart_view5.chart().axisY().setTickInterval(y_tick5)
                if type(y_tick5) == float:
                    self.chart_view5.chart().axisY().setLabelFormat("%2g")
                else:
                    self.chart_view5.chart().axisY().setLabelFormat("%d")
            except ValueError:
                pass
        elif self.current_segment.geometry.value == "переходная кривая":
            self.__openWarningWindow()
        self.changes_list.append(self.new_plan_model)
        #self.stopSpinnerSignal.emit('stop')
        if not self.unsavedChanges:
            self.unsavedChanges = True
        self.correctionsSpinboxValue.clear()
        self.setFocus()


    def update_level(self, level: TrackProjectModel):
        base = ProgramTaskBaseData(
            measurements_processed=self.__calculation_result.base.measurements_processed,
            detailed_restrictions=self.__calculation_result.base.detailed_restrictions,
            plan=level.data,
            prof=self.__calculation_result.base.prof,
            alc_plan=None,
            alc_level=None,
            track_split_plan=level.track_split,
            track_split_prof=self.__calculation_result.base.track_split_prof,
            step=self.__calculation_result.base.step
        )
        self.__calculation_result = ProgramTaskCalculationResultDto(
            options=self.options,
            base=base,
            calculated_task=machine_task_from_base_data_new(base),
            summary=base.track_split_plan)
        self.updateCalculationResultSignal.emit(self.__calculation_result)


    # количество тиков на оси в зависимости от диапазона
    def set_axis_ticks_step(self, position):
        y_tick = 1 #None
        if 0 < position < 0.5:
            y_tick = 0.1
        elif 0.5 < position < 1:
            y_tick = 0.2
        elif 1 < position < 5:
            y_tick = 1
        elif 5 < position < 10:
            y_tick = 2
        elif 10 < position < 50:
            y_tick = 10
        elif 50 < position < 100:
            y_tick = 20
        elif 100 < position < 500:
            y_tick = 100
        elif 500 < position < 1000:
            y_tick = 200
        elif 1000 < position < 5000:
            y_tick = 1000
        elif 5000 < position:
            y_tick = 2000
        if (position / y_tick) < 2:
            y_tick = (y_tick / 2)
        return y_tick

    def __openWarningWindow(self):
        msg = QMessageBox(self)
        msg.setText("Это переходная кривая.\n\n"
                    "Изменения тут невозможны")
        msg.exec()

    # принудительно ставим на место границы последнего (текущего) изменённого диапазона саммари
    def set_coords_current_segment(self, previous_model: list, c: int):
        coord1 = self.startPicket + self.position_multiplyer * self.get_summary_row(previous_model, c).to_dict()[
            'start']
        coord2 = self.startPicket + self.position_multiplyer * self.get_summary_row(previous_model, c).to_dict()['end']
        self.model1.shiftLine(coord1)
        self.model2.shiftLine(coord2)

    # Получить колонку from summary
    def get_summary_column(self, summary_file:list, column_name: str):
        column = []
        for every_dict in summary_file.elements():
            column.append(every_dict.to_dict()[column_name])
        return column

    # Получить строку из summary по индексу
    def get_summary_row(self, summary_file, row_index: int):
        row = summary_file[row_index]
        return row

    # установка значений в окна
    def __returnData(self, counter:int):
        if self.updatedData:
            current_segment = self.updatedData.elements()[counter]
            self.prj_label_value.setNum(round(current_segment.level_fact, 3)) \
                if current_segment.level_fact else self.prj_label_value.setNum(0)
            self.anep_label_value_prj.setNum(round(current_segment.a_nepog_fact, 3))\
                if current_segment.a_nepog_fact else self.anep_label_value_prj.setNum(0)
            self.psi_label_value_prj.setNum(round(current_segment.psi_fact, 3)) \
                if current_segment.psi_fact else self.psi_label_value_prj.setNum(0)
            self.fv_label_value_prj.setNum(round(current_segment.v_max_fact, 3)) \
                if current_segment.v_max_fact else self.fv_label_value_prj.setNum(0)
        else:
            current_segment = self.plan_model.elements()[counter]
            self.prj_label_value.setNum(round(current_segment.level_fact, 3)) \
                if current_segment.level_fact else self.prj_label_value.setNum(0)
            self.anep_label_value_prj.setNum(round(current_segment.a_nepog_fact, 3)) \
                if current_segment.a_nepog_fact else self.anep_label_value_prj.setNum(0)
            self.psi_label_value_prj.setNum(round(current_segment.psi_fact, 3)) \
                if current_segment.psi_fact else self.psi_label_value_prj.setNum(0)
            self.fv_label_value_prj.setNum(round(current_segment.v_max_fact, 3)) \
                if current_segment.v_max_fact else self.fv_label_value_prj.setNum(0)

