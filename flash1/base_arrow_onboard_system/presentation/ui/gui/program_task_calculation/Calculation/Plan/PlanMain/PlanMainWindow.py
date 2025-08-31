
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QApplication,QGroupBox,
                               QHBoxLayout, QGridLayout, QLabel,QPushButton, QStackedLayout, QMessageBox)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from domain.calculations.plan_model import TrackProjectModel,  TrackProjectType
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from .VerticalLine import VerticalLineModel
from ..Shifts.ShiftsMain import ShiftsMainWidget
from ..Parameters.ParametersMain import ParametersMainWidget
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent2
import math
import  pandas

focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"


class PlanView(QWidget):
    def __init__(self,  calculation_result,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        self.updatedData: TrackProjectModel = False
        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.setLayout(self.__layout)
        self.planMain = PlanMainWidget(self.__calculation_result)
        self.__openPlanMain()
        self.setLayout(self.__layout)

    def __clearCurrentView(self):
        if self.__currentView is not None:
            self.__currentView = None

    def __openPlanMain(self):
        self.__clearCurrentView()
        self.__currentView = self.planMain
        self.__currentView.openPlanParametersSignal.connect(self.__openPlanParameters)
        # self.__currentView.openPlanShiftsSignal.connect(self.__openPlanShifts)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)

    def __openPlanParameters(self):
        self.__clearCurrentView()
        self.__currentView = ParametersMainWidget(self.__calculation_result)
        self.__currentView.closePlanParametersSignal.connect(self.__openPlanMain)
        self.__currentView.passDataSignal.connect(self.planMain.rerenderCharts)
        self.__currentView.updateCalculationResultSignal.connect(self.update_calculation_result)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)

    def update_calculation_result(self, data):
        self.__calculation_result = data

    # def __openPlanShifts(self):
    #     self.__clearCurrentView()
    #     self.__currentView = ShiftsMainWidget(self.__calculation_result)
    #     self.__currentView.closePlanShiftsSignal.connect(self.__closePlanShifts)
    #     self.__currentView.passDataSignal.connect(self.planMain.rerenderCharts)
    #     self.__layout.addWidget(self.__currentView)
    #     self.__layout.setCurrentWidget(self.__currentView)


class PlanMainWidget(QWidget):
    planMainSignal = Signal(str)                         # close PlanMain
    passDataSignal = Signal(TrackProjectModel)           # отдаёт данные на уровень выше
    openPlanParametersSignal = Signal(int)
    openPlanShiftsSignal = Signal(int)
    def __init__(self, calculation_result,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        self.updatedData: TrackProjectModel = None
        self.plan_model = TrackProjectModel.create(TrackProjectType.Plan, self.__calculation_result)
        programTaskModel = StepIndexedDataFramePositionedModel(
                                    self.__calculation_result.calculated_task.data.columns,
                                    self.__calculation_result.calculated_task.step,
                                    self)
        programTaskModel.reset(self.__calculation_result.calculated_task.step,
                                  self.__calculation_result.calculated_task.data)
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        position_min: float = self.position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        position_max: float = self.position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        self.currentPicket = self.__calculation_result.options.start_picket.meters
        self.picket_direction = self.__calculation_result.options.picket_direction
        self.model = VerticalLineModel(self.options.start_picket.meters)
        #self.__warningMessage()
        #print('self.__calculation_result.data.columns ', self.__calculation_result.calculated_task.data.columns)
        #
        self.shifts_min, self.shifts_max, self.shifts_sum, self.shifts_abs = 0,0,0,0
        self.__plan_delta_values(self.__calculation_result.calculated_task.data['plan_delta'])
        self.motion_step = 1
        grid = QGridLayout()
        infopanel_first = InfopanelFirst(self.__calculation_result)
        infopanel_second = InfopanelSecond(self.__calculation_result)
        title_window = LabelOnParent2('План. Главная', 500, 0, 250, 40, infopanel_first)
        title_window.setWordWrap(True)
        title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        grid.addWidget(infopanel_first, 0, 0, 1, 10)
        grid.addWidget(infopanel_second, 1, 0, 1, 10)
        # #=============================================== Charts ===================================================
        program_task_charts_column_names: List[str] = [['plan_fact', 'plan_prj'], ['plan_delta']]
        charts_vbox = QVBoxLayout()
        for column_name in program_task_charts_column_names:
            if column_name == ['plan_fact', 'plan_prj']:
                chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
                chart_value_range = (
                        min(chart_value_range0[0], chart_value_range1[0]),
                        max(chart_value_range0[1], chart_value_range1[1])
                )
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
                chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
                self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
                self.series0.setPen(QPen(QColor("#2f8af0"), 2))
                self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
                self.series1.setPen(QPen(QColor("red"), 2))
                self.chart1 = HorizontalChart( (position_min, position_max),
                                                self.options.picket_direction == PicketDirection.Backward,
                                                (chart_value_min, chart_value_max), False,
                                                series0=[self.series0], series1=[self.series1],
                                                x_tick=100, y_tick=10,
                                                title = "Стрелы изгиба, мм",
                                                xMinorTickCount=9,
                                                xGridLineColor="gray", yGridLineColor="gray",
                                                xMinorGridLineColor="gray", yMinorGridLineColor="gray")
                #
                self.chart1.legend().hide()
                self.chart1.layout().setContentsMargins(0, 0, 0, 0)
                self.chart1.setMargins(QMargins(0, 0, 0, 0))
                self.chart1.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
                self.chart1.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
                self.chart_view1 = QChartView(self.chart1)
                self.chart_view1.setFocusPolicy(Qt.NoFocus)
                self.chart_view1.chart().setBackgroundBrush(QBrush("black"))
                self.chart_view1.setRenderHint(QPainter.Antialiasing)
                #
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
                #
            else:
                chart_value_range: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                self.shifts_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
                self.shifts_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
                self.series = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                QCoreApplication.translate(
                                                    'Lining trip/process/view/charts/program task', column_name[0]))
                self.series.setPen(QPen(QColor("#2f8af0"), 2))
                self.chart2 = HorizontalChart((position_min, position_max),
                                         self.options.picket_direction == PicketDirection.Backward,
                                         (self.shifts_value_min, self.shifts_value_max),  False, series0=[self.series],
                                         x_tick=100, y_tick=10,
                                         title = "Сдвиги, мм", xMinorTickCount=10,
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
                #
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
        #=================================================================================
        self.installEventFilter(self)
        grid.addLayout(charts_vbox, 2, 0, 8, 9)
        rcw = self.__rightColumnWidget()
        bottom = self.__bottomWidget()
        grid.addLayout(rcw, 2, 9, 8, 1)
        grid.addWidget(bottom, 10, 0, 1, 10)
        self.setWindowTitle("Расчёт.План")
        self.setLayout(grid)
        self.showMaximized()
        self.setFocus()

    # нахождение данных для нижней панели
    def __plan_delta_values(self, datacolumn: pandas.Series):
        self.shifts_min = round(datacolumn.min(), 1)
        self.shifts_max = round(datacolumn.max(), 1)
        self.shifts_sum = round(datacolumn.sum(), 1)
        self.shifts_abs = round(datacolumn.abs().sum(), 1)
        return (self.shifts_min, self.shifts_max, self.shifts_sum, self.shifts_abs)

    # пока что не надо
    def __warningMessage(self):
        msg = QMessageBox(self)
        msg.setText("Ответственность \n за изменение и применение \n рассчитанного программного задания \n лежит "
                    "на операторе рихтовочной машины.")
        buttonAccept = msg.addButton("Всё понятно", QMessageBox.YesRole)
        msg.exec()

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
        return False

    def rerenderCharts(self, data):
        self.updatedData = data            # прилетели с уровня ниже, улетят на уровень выше
        #
        self.series1.clear()
        self.series.clear()
        self.new_plan_model = data
        startPicket = self.options.start_picket.meters
        scale = 6
        for i in range(0, self.new_plan_model.data.shape[0], 1):
            if i % scale == 0:
                self.series1.append(startPicket, self.new_plan_model.data.loc[:, 'plan_prj'][i])
                self.series.append(startPicket, self.new_plan_model.data.loc[:, 'plan_delta'][i])
            startPicket += self.plan_model.step * self.position_multiplyer
        self.chart_view1.update()
        self.chart_view2.update()
        chart1Min = min(0, self.new_plan_model.data.loc[:, 'plan_prj'].min(),
                        self.new_plan_model.data.loc[:, 'plan_fact'].min())
        chart1Max = max(0, self.new_plan_model.data.loc[:, 'plan_prj'].max(),
                        self.new_plan_model.data.loc[:, 'plan_fact'].max())
        chart1Padding = (chart1Max - chart1Min) * 0.05
        self.chart_view1.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
        y_tick1 = self.set_axis_ticks_step(round(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding))))
        if type(y_tick1) == float:
            self.chart_view1.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view1.chart().axisY().setLabelFormat("%d")
        self.chart_view1.chart().axisY().setTickInterval(y_tick1)
        #
        chart2Min = min(0, self.new_plan_model.data.loc[:, 'plan_delta'].min())
        chart2Max = max(0, self.new_plan_model.data.loc[:, 'plan_delta'].max())
        chart2Padding = (chart2Max - chart2Min) * 0.05
        self.chart_view2.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
        y_tick2 = self.set_axis_ticks_step(round(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding))))
        if type(y_tick2) == float:
            self.chart_view2.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view2.chart().axisY().setLabelFormat("%d")
        self.chart_view2.chart().axisY().setTickInterval(y_tick2)
        #
        bottom_panel_values = self.__plan_delta_values(self.new_plan_model.data.loc[:, 'plan_delta'])
        self.shifts_min, self.shifts_max, self.shifts_sum, self.shifts_abs = bottom_panel_values[0], bottom_panel_values[1], bottom_panel_values[2], bottom_panel_values[3]
        self.label_value4.setNum(round(self.shifts_min))
        self.label_value3.setNum(round(self.shifts_max))
        self.label_value1.setNum(round(self.shifts_sum))
        self.label_value2.setNum(round(self.shifts_abs))


    # количество тиков на оси в зависимости от диапазона (position)
    def set_axis_ticks_step(self, position):
        y_tick = 1
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

    # установка значений в окна датчиков в правой колонке
    def __returnData(self, i:int):
        self.currentPicket += self.position_multiplyer * i
        idx = math.fabs(int( (self.currentPicket - self.__calculation_result.options.start_picket.meters) * self.position_multiplyer / self.plan_model.step ))
        self.point_number_label_value.setNum(round(self.currentPicket))
        # если данные перерисовались
        if self.updatedData:
            self.fact_label_value.setNum(round(self.updatedData.data['plan_fact'][idx]))
            self.prj_label_value.setNum(round(self.updatedData.data['plan_prj'][idx]))
            self.shifts_label_value.setNum(round(self.updatedData.data['plan_delta'][idx]))
        else:
            self.fact_label_value.setNum(
                round(self.__calculation_result.calculated_task.data['plan_fact'][idx]))
            self.prj_label_value.setNum(
                round(self.__calculation_result.calculated_task.data['plan_prj'][idx]))
            self.shifts_label_value.setNum(
                round(self.__calculation_result.calculated_task.data['plan_delta'][idx]))

    def __bottomWidget(self):
        bottom_widget = QWidget()
        hbox = QHBoxLayout()
        label1 = QLabel("Сумма сдвигов")
        label2 = QLabel("Сумма модулей сдвигов")
        label3 = QLabel("Максимальный сдвиг влево")
        label4 = QLabel("Максимальный сдвиг вправо")
        label_mm1 = QLabel("mm")
        label_mm2 = QLabel("mm")
        label_mm3 = QLabel("mm")
        label_mm4 = QLabel("mm")
        self.label_value1 = QLabel(str(round(self.shifts_sum)))
        self.label_value2 = QLabel(str(round(self.shifts_abs)))
        self.label_value3 = QLabel(str(round(self.shifts_max)))
        self.label_value4 = QLabel(str(round(self.shifts_min)))
        value_style = "font: bold; font-size: 13pt; color:black; background-color:white"
        label_style = "font-size: 13pt;color:black;"
        for i in (self.label_value1, self.label_value2, self.label_value3, self.label_value4):
            i.setStyleSheet(value_style)
        for i in (label1, label2, label3, label4, label_mm1, label_mm2, label_mm3, label_mm4):
            i.setStyleSheet(label_style)
        hbox.addWidget(label1)
        hbox.addWidget(self.label_value1)
        hbox.addWidget(label_mm1)
        hbox.addStretch(1)
        hbox.addWidget(label2)
        hbox.addWidget(self.label_value2)
        hbox.addWidget(label_mm2)
        hbox.addStretch(1)
        hbox.addWidget(label3)
        hbox.addWidget(self.label_value3)
        hbox.addWidget(label_mm3)
        hbox.addStretch(1)
        hbox.addWidget(label4)
        hbox.addWidget(self.label_value4)
        hbox.addWidget(label_mm4)
        hbox.addStretch(1)
        bottom_widget.setMaximumHeight(50)
        bottom_widget.setContentsMargins(0, 0, 0, 0)
        bottom_widget.setLayout(hbox)
        return bottom_widget

    def __rightColumnWidget(self):
        vbox = QVBoxLayout()
        groupbox_top = QGroupBox()
        groupbox_vlayout = QVBoxLayout()
        groupbox_top.setLayout(groupbox_vlayout)
        groupbox_top.setTitle("Редактирование")
        self.params_button = QPushButton("Параметры")
        self.params_button.setStyleSheet(focus_style)
        self.params_button.setProperty("optionsWindowPushButton", True)
        self.params_button.setFixedWidth(150)
        self.shifts_button = QPushButton("Сдвиги")
        self.shifts_button.setStyleSheet(focus_style)
        groupbox_vlayout.addWidget(self.params_button)
        #groupbox_vlayout.addWidget(self.shifts_button)
        self.params_button.clicked.connect(self.__params_button)
        self.shifts_button.clicked.connect(self.__shifts_button)
        self.results_button = QPushButton("Результаты")
        self.results_button.setStyleSheet(focus_style)
        self.settings_button = QPushButton("Установки")
        self.settings_button.setStyleSheet(focus_style)
        self.escape_button = QPushButton("Выход(ESC)")
        self.escape_button.setProperty("optionsWindowPushButton", True)
        self.escape_button.setFixedWidth(150)
        self.escape_button.setStyleSheet(focus_style)
        self.results_button.clicked.connect(self.__results_button)
        self.settings_button.clicked.connect(self.__settings_button)
        self.escape_button.clicked.connect(self.__escape_button)
        # self.buttons = []
        # self.buttons.append(self.params_button)
        # self.buttons.append(self.shifts_button)
        # self.buttons.append(self.results_button)
        # self.buttons.append(self.settings_button)
        # self.buttons.append(self.escape_button)
        #############################################
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        #
        value_style = "font: bold; font-size: 12pt;color:white;background-color:black"
        point_number_label = QLabel("Текущее\n положение")
        point_number_label.setStyleSheet("font: bold; font-size: 10pt;color:black")
        self.point_number_label_value = QLabel(str(1))
        self.point_number_label_value.setStyleSheet(value_style)
        hbox1.addWidget(point_number_label)
        hbox1.addWidget(self.point_number_label_value)
        groupbox_bottom = QGroupBox()
        groupbox_bottom_layout = QVBoxLayout()
        groupbox_bottom.setLayout(groupbox_bottom_layout)
        groupbox_bottom_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Натура")
        fact_label.setStyleSheet("font: bold; font-size: 12pt;color:green")
        self.fact_label_value = QLabel(str(0))
        self.fact_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_bottom_layout_hbox1.addWidget(self.fact_label_value)
        groupbox_bottom_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.prj_label_value = QLabel(str(0))
        self.prj_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox2.addWidget(prj_label)
        groupbox_bottom_layout_hbox2.addWidget(self.prj_label_value)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox1)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox2)
        shifts_label = QLabel("Сдвиги")
        shifts_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.shifts_label_value = QLabel(str(0))
        self.shifts_label_value.setStyleSheet(value_style)
        hbox2.addWidget(shifts_label)
        hbox2.addWidget(self.shifts_label_value)
        groupbox_bottom.setStyleSheet("background-color:white")
        vbox1.addLayout(hbox1)
        vbox1.addWidget(groupbox_bottom)
        vbox1.addLayout(hbox2)
        vbox.addWidget(groupbox_top)
        #vbox.addStretch(1)
        #vbox.addWidget(self.results_button)
        #vbox.addStretch(1)
        #vbox.addWidget(self.settings_button)
        vbox.addStretch(5)
        vbox.addWidget(self.escape_button)
        vbox.addStretch(1)
        vbox.addLayout(vbox1)
        #self.setLayout(vbox)
        return vbox

    def __params_button(self):
        self.openPlanParametersSignal.emit(self.currentPicket)

    def __shifts_button(self):
        self.openPlanShiftsSignal.emit(self.currentPicket)

    def __results_button(self):
        pass

    def __settings_button(self):
        pass

    def __escape_button(self):
        if self.updatedData:
            self.passDataSignal.emit(self.updatedData)
        self.planMainSignal.emit('close')

