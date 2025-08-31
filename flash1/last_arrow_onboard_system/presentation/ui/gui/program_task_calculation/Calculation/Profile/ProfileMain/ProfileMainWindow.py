
from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QApplication,QPushButton,QSpinBox,QStackedLayout,
                               QHBoxLayout, QGridLayout, QLabel, QFileDialog,QMessageBox, QGroupBox)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.calculations.plan_model import TrackPlanProjectModel, TrackElementGeometry, TrackProjectModel, TrackProjectType
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel, \
    ReducedStepIndexedPositionedModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent, LabelOnParent2
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from domain.models.VerticalLineModel import VerticalLineModel
from ..ProfileLifting.ProfileLiftingWindow import ProfileLiftingWidget
from ..ProfileParameters.ProfileParametersWindow import ProfileParametersWidget
from presentation.ui.gui.common.elements.Base import setWindowTitle
from presentation.ui.gui.common.viewes.WindowTitle import Window

import math
import pandas


focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"


class ProfileView(QWidget):
    def __init__(self,
                 calculation_result:ProgramTaskCalculationResultDto,
                 #state: ProgramTaskCalculationSuccessState,
                 parent: QWidget = None,
                 window: Window = None):
        super().__init__(parent)
        #self.__state = state
        self.__calculation_result = calculation_result
        #
        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.__window = window
        self.setLayout(self.__layout)
        #
        self.profileMain = ProfileMainWidget(self.__calculation_result)
        self.__openProfileMain()
        self.setLayout(self.__layout)

    def __clearCurrentView(self):
        if self.__currentView:
            self.__currentView = None

    def update_calculation_result(self, data):
        self.__calculation_result = data

    def __openProfileMain(self):
        self.__clearCurrentView()
        self.__currentView = self.profileMain
        self.__currentView.openProfileParametersSignal.connect(self.__openProfileParameters)
        # self.__currentView.openProfileShiftsSignal.connect(self.__openProfileShifts)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)
        #setWindowTitle(self, "Профиль")
        self.__window.setTitle("Профиль")

    def __openProfileParameters(self):
        self.__clearCurrentView()
        self.__currentView = ProfileParametersWidget(self.__calculation_result)
        self.__currentView.quitProfileParameters.connect(self.__openProfileMain)
        self.__currentView.passDataParametersSignal.connect(self.profileMain.rerenderCharts)
        self.__currentView.updateCalculationResultSignal.connect(self.update_calculation_result)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)
        #setWindowTitle(self, "Профиль > Параметры")
        self.__window.setTitle("Профиль > Параметры")

    # def __openProfileLifting(self):
    #     self.__clearCurrentView()
    #     self.__currentView = SpeedMainWidget(self.__state)
    #     self.__currentView.closeLevelSpeedSignal.connect(self.__openLevelMain)
    #     self.__currentView.passDataSignal.connect(self.levelMain.rerenderCharts)
    #     self.__layout.addWidget(self.__currentView)
    #     self.__layout.setCurrentWidget(self.__currentView)


class ProfileMainWidget(QWidget):
    passDataSignal = Signal(TrackProjectModel)
    profileMainSignal = Signal(str)
    openProfileParametersSignal = Signal(str)
    openProfileLiftingSignal = Signal(str)
    skip_coefficient = 0.002

    def __init__(self,  calculation_result: ProgramTaskCalculationResultDto, parent: QWidget = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        # self.programTaskModel: AbstractPositionedTableModel = StepIndexedDataFramePositionedModel(self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step, self)
        # self.programTaskModel.reset(self.__calculation_result.calculated_task.step, self.__calculation_result.calculated_task.data)
        self.programTaskModel = ReducedStepIndexedPositionedModel(
            step=self.__calculation_result.calculated_task.step,
            data=self.__calculation_result.calculated_task.data,
            parent=self,
        )
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        #
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(self.programTaskModel)
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = self.programTaskModel.minmaxPosition()
        position_min: float = self.position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        position_max: float = self.position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        rangeX: tuple[float, float] = (position_min, position_max)

        self.counter = 0
        self.motion_step = 1
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.currentPicket = self.options.start_picket.meters
        self.model = VerticalLineModel(self.options.start_picket.meters, rangeX, accValue=True)
        self.plan_model = TrackProjectModel.create(TrackProjectType.Profile, self.__calculation_result)
        self.liftings_min, self.liftings_max = 0, 0
        self.__prof_delta_values(self.__calculation_result.calculated_task.data['prof_delta'])
        self.model1 = VerticalLineModel(self.options.start_picket.meters, rangeX, accValue=True)
        self.model2 = VerticalLineModel(self.options.start_picket.meters + self.plan_model.elements()[0].to_dict()['end'], rangeX, accValue=True)
        self.updatedData: TrackProjectModel = None
        #
        grid = QGridLayout()
        self.infopanel_first = InfopanelFirst(self.__calculation_result)
        self.infopanel_second = InfopanelSecond(self.__calculation_result)
        grid.addWidget(self.infopanel_first, 0, 0, 1, 10)
        grid.addWidget(self.infopanel_second, 1, 0, 1, 10)
        #
        #title_window = LabelOnParent2('Профиль. Главная страница', 500, 0, 250, 40, self.infopanel_first)
        #title_window.setWordWrap(True)
        #title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")

        # #=============================================== Charts ===================================================
        charts_vbox = QVBoxLayout()
        column_name = ['prof_fact', 'prof_prj']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (
                    min(chart_value_range0[0], chart_value_range1[0]),
                    max(chart_value_range0[1], chart_value_range1[1]))
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
        self.series0.setPen(QPen(QColor("#2f8af0"), 2))
        self.series1.setPen(QPen(QColor("red"), 2))
        vertical_chart_title = "Вертикальные стрелы изгиба, мм"
        self.chart1 = HorizontalChart((position_min, position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0], series1=[self.series1],
                                        x_tick=100, y_tick=10, title=vertical_chart_title,
                                        xMinorTickCount=9, yMinorTickCount=1,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
        self.chart1.legend().hide()
        self.chart1.layout().setContentsMargins(0, 0, 0, 0)
        self.chart1.setMargins(QMargins(0, 0, 0, 0))
        self.chart1.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart1.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart_view1 = QChartView(self.chart1)
        self.chart_view1.setFocusPolicy(Qt.NoFocus)
        self.chart_view1.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view1.setRenderHint(QPainter.Antialiasing)
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.model)
        self.chart1.addSeries(self.vertical_line_series1)
        self.vertical_line_series1.attachAxis(self.chart1.axisX())
        self.vertical_line_series1.attachAxis(self.chart1.axisY())
        charts_vbox.addWidget(self.chart_view1, 2)

        column_name = ['prof_delta']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range = (chart_value_range0[0], chart_value_range0[1])
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series2 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                QCoreApplication.translate(
                                                    'Lining trip/process/view/charts/program task', column_name[0]))
        self.series2.setPen(QPen(QColor("#2f8af0"), 2))
        vertical_chart_title = 'Подъёмки, мм'
        self.chart2 = HorizontalChart((position_min, position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series2],   #series1=[self.series3],
                                        x_tick=100, y_tick=10, title=vertical_chart_title,
                                        xMinorTickCount=9, yMinorTickCount=1,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
        self.chart2.legend().hide()
        self.chart2.layout().setContentsMargins(0, 0, 0, 0)
        self.chart2.setMargins(QMargins(0, 0, 0, 0))
        self.chart2.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart2.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart_view2 = QChartView(self.chart2)
        self.chart_view2.setFocusPolicy(Qt.NoFocus)
        self.chart_view2.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view2.setRenderHint(QPainter.Antialiasing)
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper2 = QVXYModelMapper(self)
        self.lineMapper2.setXColumn(0)
        self.lineMapper2.setYColumn(1)
        self.lineMapper2.setSeries(self.vertical_line_series2)
        self.lineMapper2.setModel(self.model)
        self.chart2.addSeries(self.vertical_line_series2)
        self.vertical_line_series2.attachAxis(self.chart2.axisX())
        self.vertical_line_series2.attachAxis(self.chart2.axisY())
        charts_vbox.addWidget(self.chart_view2, 1)
        #
        self.installEventFilter(self)
        #=================================================================================
        grid.addLayout(charts_vbox, 2, 0, 8, 9)
        rcw = self.__rightColumnWidget()
        grid.addLayout(rcw, 2, 9, 8, 1)
        bottom = self.__bottomWidget()
        grid.addWidget(bottom, 10, 0, 1, 10)
        self.setLayout(grid)
        self.setFocus()

    def __bottomWidget(self):
        bottom_widget = QWidget()
        hbox = QHBoxLayout()
        label1 = QLabel("Максимальный сдвиг влево")
        label2 = QLabel("Максимальный сдвиг вправо")
        label_mm1 = QLabel("mm")
        label_mm2 = QLabel("mm")
        self.label_value1 = QLabel(str(round((self.liftings_max))))
        self.label_value2 = QLabel(str(round((self.liftings_min))))
        value_style = "font: bold; font-size: 13pt; color:black; background-color:white"
        label_style = "font-size: 13pt;color:black;"
        for i in (self.label_value1, self.label_value2):
            i.setStyleSheet(value_style)
        for i in (label1, label2, label_mm1, label_mm2):
            i.setStyleSheet(label_style)
        hbox.addWidget(label1)
        hbox.addWidget(self.label_value1)
        hbox.addWidget(label_mm1)
        hbox.addStretch(1)
        hbox.addWidget(label2)
        hbox.addWidget(self.label_value2)
        hbox.addWidget(label_mm2)
        hbox.addStretch(1)
        #hbox.addWidget(label3)
        #hbox.addWidget(self.label_value3)
        #hbox.addWidget(label_mm3)
        #hbox.addStretch(1)
        #hbox.addWidget(label4)
        #hbox.addWidget(self.label_value4)
        #hbox.addWidget(label_mm4)
        #hbox.addStretch(1)
        bottom_widget.setMaximumHeight(50)
        bottom_widget.setContentsMargins(0, 0, 0, 0)
        bottom_widget.setLayout(hbox)
        return bottom_widget

    # нахождение данных для нижней панели
    def __prof_delta_values(self, datacolumn: pandas.Series):
        if datacolumn.min() < 0:
            self.liftings_min = round(datacolumn.min())
        else:
            self.liftings_min = round(datacolumn[100:-100].min())
        self.liftings_max = round(datacolumn.max())
        return (self.liftings_min, self.liftings_max)


    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            self.setFocus()
            if event.key() == Qt.Key.Key_Left:
                self.model.shiftLine(self.position_multiplyer * self.motion_step * -1)
                self.__returnData(self.motion_step * -1)
            elif event.key() == Qt.Key.Key_Right:
                self.model.shiftLine(self.position_multiplyer * self.motion_step)
                self.__returnData(self.motion_step)
            elif event.key() == Qt.Key.Key_Escape:
                self.__escape_button()
                #self.profileMainSignal.emit('close')
        return False

    def rerenderCharts(self, data):
        self.updatedData = data
        self.series1.clear()
        self.series2.clear()
        self.new_plan_model = data

        startPicket = self.options.start_picket.meters
        total_steps = self.new_plan_model.data.shape[0]
        skip = round(self.skip_coefficient * total_steps)
        for i in range(0, total_steps):
            if i % skip == 0:
                self.series1.append(startPicket, self.new_plan_model.data.loc[:, 'prof_prj'][i])
                self.series2.append(startPicket, self.new_plan_model.data.loc[:, 'prof_delta'][i])
            startPicket += self.plan_model.step * self.position_multiplyer

        self.chart_view1.update()
        self.chart_view2.update()
        #
        chart1Min = min(0, self.new_plan_model.data.loc[:, 'prof_prj'].min(),
                        self.new_plan_model.data.loc[:, 'prof_fact'].min())
        chart1Max = max(0, self.new_plan_model.data.loc[:, 'prof_prj'].max(),
                        self.new_plan_model.data.loc[:, 'prof_fact'].max())
        chart1Padding = (chart1Max - chart1Min) * 0.05
        self.chart_view1.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
        y_tick1 = self.set_axis_ticks_step(round(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding))))
        if type(y_tick1) == float:
            self.chart_view1.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view1.chart().axisY().setLabelFormat("%d")
        self.chart_view1.chart().axisY().setTickInterval(y_tick1)
        #
        chart2Min = min(0, self.new_plan_model.data.loc[:, 'prof_delta'].min())
        chart2Max = max(0, self.new_plan_model.data.loc[:, 'prof_delta'].max())
        chart2Padding = (chart2Max - chart2Min) * 0.05
        self.chart_view2.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
        y_tick2 = self.set_axis_ticks_step(round(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding))))
        if type(y_tick2) == float:
            self.chart_view2.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view2.chart().axisY().setLabelFormat("%d")
        self.chart_view2.chart().axisY().setTickInterval(y_tick2)
        #
        bottom_panel_values = self.__prof_delta_values(self.new_plan_model.data['prof_delta'])   #.loc[:, 'prof_delta'])
        self.liftings_min, self.liftings_max = bottom_panel_values[0], bottom_panel_values[1]
        self.label_value1.setNum(round(self.liftings_max))
        self.label_value2.setNum(round(self.liftings_min))

    # количество тиков на оси в зависимости от диапазона (position)
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
        elif 5000 < position < 10000:
            y_tick = 2000
        elif 10000 < position < 50000:
            y_tick = 10000
        elif 50000 < position < 100000:
            y_tick = 20000
        elif 100000 < position:
            y_tick = 50000
        if (position / y_tick) < 2:
            y_tick = (y_tick / 2)
        return y_tick

    #установка значений в окна
    def __returnData(self, i:int):
        self.currentPicket += self.position_multiplyer * i
        idx = int((self.currentPicket - self.__calculation_result.options.start_picket.meters) * self.position_multiplyer / self.plan_model.step)
        self.point_number_label_value.setNum(self.currentPicket)
        # если данные перерисовались
        if self.updatedData:
            self.fact_label_value.setNum(round(self.updatedData.data['prof_fact'][idx]))
            self.prj_label_value.setNum(round(self.updatedData.data['prof_prj'][idx]))
            self.lifting_value.setNum(round(self.updatedData.data['prof_delta'][idx]))
        else:
            self.fact_label_value.setNum(round(self.__calculation_result.calculated_task.data['prof_fact'][idx]))
            self.prj_label_value.setNum(round(self.__calculation_result.calculated_task.data['prof_prj'][idx]))
            self.lifting_value.setNum(round(self.__calculation_result.calculated_task.data['prof_delta'][idx]))

    def __rightColumnWidget(self):
        vbox = QVBoxLayout()
        groupbox_top = QGroupBox()
        groupbox_vlayout = QVBoxLayout()
        groupbox_top.setLayout(groupbox_vlayout)
        groupbox_top.setTitle("Редактирование")
        groupbox_top.setStyleSheet("QGroupBox:title{margin-top: -10px}")
        self.parameters_button = QPushButton("Параметры")
        self.parameters_button.setStyleSheet(focus_style)
        self.parameters_button.setProperty("optionsWindowPushButton", True)
        self.parameters_button.setFixedWidth(150)
        self.lifting_button = QPushButton("Подъёмки")
        self.lifting_button.setStyleSheet(focus_style)
        self.lifting_button.setProperty("optionsWindowPushButton", True)
        self.lifting_button.setFixedWidth(150)
        groupbox_vlayout.addWidget(self.parameters_button)
        #groupbox_vlayout.addWidget(self.lifting_button)
        self.parameters_button.clicked.connect(self.__handleParametersButton)
        self.lifting_button.clicked.connect(self.__handleLiftingButton)
        self.results_button = QPushButton("Результаты")
        self.settings_button = QPushButton("Установки")
        self.escape_button = QPushButton("Выход (ESC)")
        self.escape_button.setStyleSheet(focus_style)
        self.escape_button.setProperty("optionsWindowPushButton", True)
        self.results_button.clicked.connect(self.__results_button)
        self.settings_button.clicked.connect(self.__settings_button)
        self.escape_button.clicked.connect(self.__escape_button)
        self.buttons = []
        self.buttons.append(self.parameters_button)
        self.buttons.append(self.lifting_button)
        self.buttons.append(self.results_button)
        self.buttons.append(self.settings_button)
        self.buttons.append(self.escape_button)
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        value_style = "font: bold; font-size: 12pt;color:white;background-color:black"
        point_number_label = QLabel("№ точки")
        point_number_label.setStyleSheet("font: bold; font-size: 12pt;color:black")
        self.point_number_label_value = QLabel(str(self.options.start_picket.meters))
        self.point_number_label_value.setStyleSheet(value_style)
        hbox1.addWidget(point_number_label)
        hbox1.addWidget(self.point_number_label_value)
        #
        groupbox_bottom = QGroupBox()
        groupbox_bottom_layout = QVBoxLayout()
        groupbox_bottom.setLayout(groupbox_bottom_layout)
        groupbox_bottom_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Натура")
        fact_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.fact_label_value = QLabel()
        self.fact_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_bottom_layout_hbox1.addWidget(self.fact_label_value)
        groupbox_bottom_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.prj_label_value = QLabel()
        self.prj_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox2.addWidget(prj_label)
        groupbox_bottom_layout_hbox2.addWidget(self.prj_label_value)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox1)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox2)
        groupbox_bottom.setStyleSheet("background-color:white")
        vbox1.addLayout(hbox1)
        vbox1.addWidget(groupbox_bottom)
        #
        hbox2 = QHBoxLayout()
        lifting_label = QLabel("Подъём")
        lifting_label.setStyleSheet("font: bold; font-size: 12pt;color:black")
        self.lifting_value = QLabel()
        self.lifting_value.setStyleSheet(value_style)
        hbox2.addWidget(lifting_label)
        hbox2.addWidget(self.lifting_value)
        vbox1.addLayout(hbox2)

        ##########################################
        vbox.addWidget(groupbox_top)
        #vbox.addStretch(1)
        #vbox.addWidget(self.results_button)
        #vbox.addStretch(1)
        #vbox.addWidget(self.settings_button)
        vbox.addStretch(5)
        vbox.addWidget(self.escape_button)
        vbox.addStretch(1)
        vbox.addLayout(vbox1)
        return vbox

        # ======================= Окраска нажатой кнопки ==================================

    def __handleParametersButton(self):
        self.openProfileParametersSignal.emit('open')

    def __handleLiftingButton(self):
        self.openProfileLiftingSignal.emit('open')

    def __results_button(self):
        pass

    def __settings_button(self):
        pass

    def __escape_button(self):
        if self.updatedData:
            self.passDataSignal.emit(self.updatedData)
        self.profileMainSignal.emit('close')
