
from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QApplication,QPushButton,QSpinBox,QStackedLayout,
                               QHBoxLayout, QGridLayout, QLabel, QFileDialog,QMessageBox, QGroupBox)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush, QKeySequence, QShortcut
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType, TrackProfileProjectModel
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from domain.dto.Workflow import ProgramTaskCalculationResultDto, ProgramTaskBaseData
from domain.calculations.progtask import machine_task_from_base_data_new
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent2
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from .ProfileBottom import BottomWidget
from .VerticalLine import VerticalLineModel, MoveLineController
import math



class ProfileParametersWidget(QWidget):
    quitProfileParameters = Signal(str)
    passDataParametersSignal = Signal(TrackProfileProjectModel)
    updateCalculationResultSignal = Signal(ProgramTaskCalculationResultDto)
    def __init__(self,
                 calculation_result: ProgramTaskCalculationResultDto,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        self.unsavedChanges: bool = False
        self.programTaskModel: AbstractPositionedTableModel = StepIndexedDataFramePositionedModel(self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step, self)
        self.programTaskModel.reset(self.__calculation_result.calculated_task.step, self.__calculation_result.calculated_task.data)
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        #
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(self.programTaskModel)
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = self.programTaskModel.minmaxPosition()
        self.position_min: float = self.position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        self.position_max: float = self.position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        self.counter = 0
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.currentPosition = self.options.start_picket.meters
        self.plan_model = TrackProjectModel.create(TrackProjectType.Profile, self.__calculation_result)
        self.model1 = VerticalLineModel(self.options.start_picket.meters)
        self.model2 = VerticalLineModel(self.options.start_picket.meters + self.position_multiplyer * self.plan_model.elements()[0].to_dict()['end'])
        self.model3 = VerticalLineModel(0)
        self.changes_list: list = []
        self.changes_list.append(self.plan_model)
        #
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
        self.chart1 = HorizontalChart((self.position_min, self.position_max),
                                     self.options.picket_direction == PicketDirection.Backward,
                                     (chart_value_min, chart_value_max), False,
                                     series0=[self.series0], series1=[self.series1], #series2=[self.series2],
                                     x_tick=100, y_tick=10, title=vertical_chart_title,
                                     xMinorTickCount=9, yMinorTickCount=1,
                                     xGridLineColor="gray", yGridLineColor="gray", #XAxisHideLabels=False,
                                     xMinorGridLineColor="gray", yMinorGridLineColor="gray")
        self.chart1.legend().hide()
        self.chart1.layout().setContentsMargins(0, 0, 0, 0)
        self.chart1.setMargins(QMargins(0, 0, 0, 0))
        self.chart1.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart1.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart_view1 = QChartView(self.chart1)
        self.chart_view1.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view1.setRenderHint(QPainter.Antialiasing)
        #
        column_name =  ['prof_delta']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range = (
                    min(chart_value_range0[0], chart_value_range0[1]),
                    max(chart_value_range0[0], chart_value_range0[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min1: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max2: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series2 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                QCoreApplication.translate(
                                                    'Lining trip/process/view/charts/program task', column_name[0]))
        self.series2.setPen(QPen(QColor("#2f8af0"), 2))
        vertical_chart_title = 'Подъёмки, мм'
        self.chart2 = HorizontalChart((self.position_min, self.position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min1, chart_value_max2), False,
                                        series0=[self.series2],
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
        self.chart_view2.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view2.setRenderHint(QPainter.Antialiasing)
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.model1)
        self.lineMapper2 = QVXYModelMapper(self)
        self.lineMapper2.setXColumn(0)
        self.lineMapper2.setYColumn(1)
        self.lineMapper2.setSeries(self.vertical_line_series2)
        self.lineMapper2.setModel(self.model2)
        self.chart1.addSeries(self.vertical_line_series1)
        self.chart1.addSeries(self.vertical_line_series2)
        self.vertical_line_series1.attachAxis(self.chart1.axisX())
        self.vertical_line_series1.attachAxis(self.chart1.axisY())
        self.vertical_line_series2.attachAxis(self.chart1.axisX())
        self.vertical_line_series2.attachAxis(self.chart1.axisY())
        charts_vbox.addWidget(self.chart_view1, 2)
        charts_vbox.addWidget(self.chart_view2, 1)
        #================================================================================
        self.bottom = BottomWidget(self.model1, self.model2, self.__calculation_result)
        self.bottom.btn_curve_change_radius.clicked.connect(lambda: self.__applyReconctruction('curveRadius'))
        self.bottom.btn_curve_shift.clicked.connect(lambda: self.__applyReconctruction('curveShift'))
        self.bottom.btn_curve_change_length.clicked.connect(lambda: self.__applyReconctruction('curveChangeLength'))
        self.bottom.okReconstructionSignal.connect(lambda: self.__escapeFunction('okReconstructionSignal'))
        self.bottom.cancelReconstructionSignal.connect(lambda: self.__escapeFunction('cancelReconstructionSignal'))
        self.bottom.updatedCounterSignal.connect(self.fetchUpdatedCounter)
        #
        self.zoom_value = 0
        self.x_start = self.position_min
        self.x_stop = self.position_max
        self.zoom_factor = (self.x_stop - self.x_start) / 20
        self.shift_chart_to_left_shortcut =  QShortcut(QKeySequence('Alt+Left'), self)
        self.shift_chart_to_left_shortcut.activated.connect(self.shift_chart_to_left)
        self.shift_chart_to_right_shortcut = QShortcut(QKeySequence('Alt+Right'), self)
        self.shift_chart_to_right_shortcut.activated.connect(self.shift_chart_to_right)
        #=================================================================================
        vbox = QVBoxLayout()
        infopanel_first = InfopanelFirst(self.__calculation_result)
        infopanel_second = InfopanelSecond(self.__calculation_result)
        title_window = LabelOnParent2('Профиль. Параметры', 500, 0, 250, 40, infopanel_first)
        title_window.setWordWrap(True)
        title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        vbox.addWidget(infopanel_first, 1)
        vbox.addWidget(infopanel_second, 1)
        vbox.addLayout(charts_vbox, 5)
        vbox.addWidget(self.bottom, 2)
        self.setLayout(vbox)
        self.installEventFilter(self)

    def fetchUpdatedCounter(self, value):
        self.counter += value

    #===================================================
    # Применение функций переустройства
    def __applyReconctruction(self, type_reconstruction: str):
        self.series1.clear()
        self.series2.clear()
        curve = self.get_summary_row(self.plan_model.elements(), self.counter)
        if type_reconstruction == 'curveRadius':
            value = self.bottom.curveChangeRadiusSpinBox.value()
            curve.new_radius = value
        elif type_reconstruction == 'curveShift':
            value = self.bottom.spinBoxCurveShift.value()
            curve.shift(value)
            self.bottom.spinBoxCurveShift.clear()
        elif type_reconstruction == 'curveChangeLength':
            value = self.bottom.spinBoxСurveChangeLength.value()
            curve.shift_start(value / -2)
            curve.shift_end(value / 2)
            self.bottom.spinBoxСurveChangeLength.clear()
        try:
            self.new_plan_model = self.plan_model.calc_new_track()
            startPicket = self.options.start_picket.meters
            scale = 6
            for i in range(0, self.new_plan_model.data.shape[0], 1):
                if i % scale == 0:
                    self.series1.append(startPicket, self.new_plan_model.data.loc[:, 'prof_prj'][i])
                    self.series2.append(startPicket, self.new_plan_model.data.loc[:, 'prof_delta'][i])
                startPicket += self.plan_model.step * self.position_multiplyer
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
            self.chart_view1.update()
            self.chart_view2.update()
            #
            self.changes_list.append(self.new_plan_model)
            self.bottom.update_first_stackwidget(self.new_plan_model.elements())  # ?
            self.plan_model = self.new_plan_model
            self.bottom.summary = self.new_plan_model
            #
            if not self.unsavedChanges:
                self.unsavedChanges = True
        except ValueError:
            pass
        self.setFocus()

    # Отмена изменений в зависимости от переданного аргумента:
    #     '0' - откат к стартовой версии (сброс всех изменений)
    #     '-2' - откат к предпоследней версии (отказ от последнего изменения)
    def __rollback(self, idx: int):
        if len(self.changes_list) > 1:                                     # имеет смысл только для '-2'
            self.series1.clear()
            self.series2.clear()
            startPicket = self.options.start_picket.meters
            scale = 6
            for i in range(0, self.changes_list[idx].data.shape[0], 1):
                if i % scale == 0:
                    self.series1.append(startPicket, self.changes_list[idx].data.loc[:, 'prof_prj'][i])
                    self.series2.append(startPicket, self.changes_list[idx].data.loc[:, 'prof_delta'][i])
                startPicket += self.plan_model.step * self.position_multiplyer
            chart1Min = min(0, self.changes_list[idx].data.loc[:, 'prof_prj'].min(),
                            self.changes_list[idx].data.loc[:, 'prof_fact'].min())
            chart1Max = max(0, self.changes_list[idx].data.loc[:, 'prof_prj'].max(),
                            self.changes_list[idx].data.loc[:, 'prof_fact'].max())
            chart1Padding = (chart1Max - chart1Min) * 0.05
            #self.chart1.chart_view.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
            self.chart_view1.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
            #
            chart2Min = min(0, self.changes_list[idx].data.loc[:, 'prof_delta'].min())
            chart2Max = max(0, self.changes_list[idx].data.loc[:, 'prof_delta'].max())
            chart2Padding = (chart2Max - chart2Min) * 0.05
            self.chart_view2.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
            self.chart_view1.update()
            self.chart_view2.update()
            #
            self.bottom.summary = self.changes_list[idx]
            self.bottom.update_first_stackwidget(self.changes_list[idx].elements())
            #
            self.plan_model = self.changes_list[idx]
            if idx == -2:
                del self.changes_list[-1]
            self.bottom.set_coords_current_segment() #self.plan_model.elements(), self.counter)
            #self.chart1.chart_view.chart().axisX().setRange(self.position_min, self.position_max)
            self.chart_view1.chart().axisX().setRange(self.position_min, self.position_max)
            #self.chart2.chart_view.chart().axisX().setRange(self.position_min, self.position_max)
            self.chart_view2.chart().axisX().setRange(self.position_min, self.position_max)
            self.setFocus()

    def update_profile(self, prof: TrackProjectModel):
        base = ProgramTaskBaseData(
            measurements_processed=self.__calculation_result.base.measurements_processed,
            detailed_restrictions=self.__calculation_result.base.detailed_restrictions,
            plan=self.__calculation_result.base.plan,
            prof=prof.data,
            alc_plan=None,
            alc_level=None,
            track_split_plan=self.__calculation_result.base.track_split_plan,
            track_split_prof=prof.track_split,
            step=self.__calculation_result.base.step
        )
        self.__calculation_result = ProgramTaskCalculationResultDto(
            options=self.options,
            base=base,
            calculated_task=machine_task_from_base_data_new(base),
            summary=base.track_split_plan)
        self.updateCalculationResultSignal.emit(self.__calculation_result)

    def shift_chart_to_left(self):
        self.x_start = self.x_start - self.zoom_factor
        self.x_stop = self.x_stop - self.zoom_factor
        self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)

    def shift_chart_to_right(self):
        self.x_start = self.x_start + self.zoom_factor
        self.x_stop = self.x_stop + self.zoom_factor
        self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
        self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)

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
        if (position / y_tick) < 2:    # чтобы не было разреженного пространства
            y_tick = (y_tick / 2)
        return y_tick

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        elif event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Left:
                self.bottom.setFocus()
            elif event.key() == Qt.Key.Key_Right:
                self.bottom.setFocus()
            elif event.key() == Qt.Key.Key_PageUp and self.zoom_value < 10:
                self.x_start = round(self.x_start + self.zoom_factor)
                self.x_stop = round(self.x_stop - self.zoom_factor)
                self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)
                #self.chart1.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                #self.chart2.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                self.zoom_value = self.zoom_value + 1
            elif event.key() == Qt.Key.Key_PageDown and self.zoom_value > 0:
                self.x_start = round(self.x_start - self.zoom_factor)
                self.x_stop = round(self.x_stop + self.zoom_factor)
                self.chart_view1.chart().axisX().setRange(self.x_start, self.x_stop)
                self.chart_view2.chart().axisX().setRange(self.x_start, self.x_stop)
                #self.chart1.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                #self.chart2.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                self.zoom_value = self.zoom_value - 1
            elif event.key() == Qt.Key.Key_Backspace:
                self.__rollback(-2)
        return False

    # Получить строку из summary по индексу
    def get_summary_row(self, summary_file, row_index: int):
        row = summary_file[row_index]
        return row

    #установка значений в окна
    def __returnData(self, i:int):
        self.currentPosition += i
        self.point_number_label_value.setNum(self.currentPosition)
        self.fact_label_value.setNum(self.__calculation_result.calculated_task.data['vozv_fact'][self.currentPosition])
        self.prj_label_value.setNum(self.__calculation_result.calculated_task.data['vozv_prj'][self.currentPosition])
        self.anep_label_value.setNum(self.__calculation_result.calculated_task.data['a_nepog_fact'][self.currentPosition])
        self.psi_label_value.setNum(self.__calculation_result.calculated_task.data['psi_fact'][self.currentPosition])
        self.fv_label_value.setNum(self.__calculation_result.calculated_task.data['v_wheel_fact'][self.options.start_picket.meters])

    def __rightColumnWidget(self):
        vbox = QVBoxLayout()
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
        self.fact_label_value = QLabel(str(self.__calculation_result.calculated_task.data['vozv_fact'][self.options.start_picket.meters]))
        self.fact_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_bottom_layout_hbox1.addWidget(self.fact_label_value)
        groupbox_bottom_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.prj_label_value = QLabel(str(self.__calculation_result.calculated_task.data['vozv_prj'][self.options.start_picket.meters]))
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
        lifting_label = QLabel("Подъёмки")
        lifting_label.setStyleSheet("font: bold; font-size: 12pt;color:black")
        self.lifting_value = QLabel(str(self.options.start_picket.meters))
        self.lifting_value.setStyleSheet(value_style)
        hbox2.addWidget(lifting_label)
        hbox2.addWidget(self.lifting_value)
        vbox1.addLayout(hbox2)
        vbox.addStretch(5)
        vbox.addStretch(1)
        vbox.addLayout(vbox1)
        return vbox

    def __escapeFunction(self, place: str = False):
        if self.unsavedChanges:
            if place == 'cancelReconstructionSignal':
                self.__rollback(0)
            elif place == 'okReconstructionSignal':
                if len(self.changes_list) > 0:
                    self.update_profile(self.plan_model)
                    self.passDataParametersSignal.emit(self.changes_list[-1])
        self.quitProfileParameters.emit("close")




