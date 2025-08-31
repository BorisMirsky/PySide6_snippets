from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QMessageBox)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, Qt, QPen, QPainter, QColor, QKeyEvent, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QObject, QEvent
import sys
import math
import copy
#from .....common.viewes.CircliBusyIndicator import CircliBusyIndicator
from .ParametersCharts import ChartsWidget, Chart1, Chart2
from .ParametersBottom import BottomWidget
from domain.models.VerticalLineModel import VerticalLineModel
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries
from domain.calculations.plan_model import TrackProjectModel,  TrackProjectType
from domain.dto.Workflow import ProgramTaskCalculationResultDto, ProgramTaskBaseData
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.calculations.progtask import machine_task_from_base_data_new
from domain.dto.Travelling import LocationVector1D
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent2
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from ....viewes.CustomSpinbox import SpinBoxByEnter


focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"


class ParametersMainWidget(QWidget):
    closePlanParametersSignal = Signal(str)
    passDataSignal = Signal(TrackProjectModel)
    updateCalculationResultSignal = Signal(ProgramTaskCalculationResultDto)
    skip_coefficient = 0.002

    def __init__(self, calculation_result: ProgramTaskCalculationResultDto,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        self.changes_list: list = []                                      # стек моделей
        self.unsavedChanges: bool = False
        programTaskModel = StepIndexedDataFramePositionedModel(
            self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step,
            self)
        programTaskModel.reset(self.__calculation_result.calculated_task.step,
                                  self.__calculation_result.calculated_task.data)
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        #
        self.plan_model = TrackProjectModel.create(TrackProjectType.Plan, self.__calculation_result)
        # copy.deepcopy тут не работает =>
        #self.plan_model_immutable_copy = TrackProjectModel.create(TrackProjectType.Plan, self.__calculation_result)
#        self.changes_list.append(self.plan_model_immutable_copy)
        self.changes_list.append(self.plan_model)
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        self.position_min: float = self.position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        self.position_max: float = self.position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        rangeX: tuple[float, float] = (self.position_min, self.position_max)
        #self.summary_len = len(self.plan_model.elements())
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.counter = 0
        self.model1 = VerticalLineModel(self.startPicket + self.position_multiplyer * self.get_summary_row(self.plan_model.elements(), self.counter).to_dict()['start'], rangeX)
        self.model2 = VerticalLineModel(self.startPicket + self.position_multiplyer * self.get_summary_row(self.plan_model.elements(), self.counter).to_dict()['end'], rangeX)
        self.model3 = VerticalLineModel(-1, rangeX)
        #
        self.chart1 = Chart1('plan_prj', 'plan_fact', self.model1, self.model2, self.model3, self.__calculation_result)
        self.chart2 = Chart2('plan_delta', self.__calculation_result)
        chartsWidget = ChartsWidget(self.chart1, self.chart2, self.__calculation_result)
        #
        self.bottom = BottomWidget(self.model1, self.model2, self.model3, self.__calculation_result)
        self.bottom.btn_curve_change_radius.clicked.connect(lambda:  self.__applyReconctruction('curveChangeRadiusSpinBox'))
        self.bottom.btn_curve_shift.clicked.connect(lambda: self.__applyReconctruction('spinBoxCurveShift'))
        self.bottom.btn_curve_change_length.clicked.connect(lambda: self.__applyReconctruction('spinBoxСurveChangeLength'))
        self.bottom.btn_transition_change_length_1.clicked.connect(lambda: self.__applyReconctruction('spinBoxTransitionChangeLenth_1'))
        self.bottom.btn_transition_change_length_2.clicked.connect(lambda: self.__applyReconctruction('spinBoxTransitionChangeLenth_2'))
        self.bottom.btn_transition_shift.clicked.connect(lambda: self.__applyReconctruction('spinBoxTransitionShift'))
        self.bottom.transitionRemoveSignal.connect(lambda: self.__applyReconctruction('transitionRemove'))
        self.bottom.transitionInsertSignal.connect(lambda: self.__applyReconctruction('transitionInsert'))
        self.bottom.okReconstructionSignal.connect(lambda: self.__escapeFunction('ok'))
        self.bottom.cancelReconstructionSignal.connect(lambda: self.__escapeFunction('cancel'))
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
        #
        self.installEventFilter(self)
        #
        vbox = QVBoxLayout()
        infopanel_first = InfopanelFirst(self.__calculation_result)
        infopanel_second = InfopanelSecond(self.__calculation_result)
        #title_window = LabelOnParent2('План. Параметры', 500, 0, 250, 40, infopanel_first)
        #title_window.setWordWrap(True)
        #title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        vbox.addWidget(infopanel_first, 1)
        vbox.addWidget(infopanel_second, 1)
        vbox.addWidget(chartsWidget, 5)
        vbox.addWidget(self.bottom, 2)
        self.setLayout(vbox)
        self.setWindowTitle("Расчёт.План.Параметры")
        self.showMaximized()

    def shift_chart_to_left(self):
        if (self.x_start - self.zoom_factor) >= self.position_min:
            self.x_start = self.x_start - self.zoom_factor
            self.x_stop = self.x_stop - self.zoom_factor
            self.chart1.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
            self.chart2.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)

    def shift_chart_to_right(self):
        if (self.x_stop + self.zoom_factor) <= self.position_max:
            self.x_start = self.x_start + self.zoom_factor
            self.x_stop = self.x_stop + self.zoom_factor
            self.chart1.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
            self.chart2.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)

    def eventFilter(self, watched: QObject, event: QEvent):
        #if event.type() == QEvent.Type.Show:
        #    self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Left:
                self.bottom.setFocus()
            elif event.key() == Qt.Key.Key_Right:
                self.bottom.setFocus()
            elif event.key() == Qt.Key.Key_PageUp and self.zoom_value < 10:
                self.x_start = round(self.x_start + self.zoom_factor)
                self.x_stop = round(self.x_stop - self.zoom_factor)
                if (self.x_stop + self.zoom_factor) > self.position_max:
                    self.x_stop = self.position_max
                if self.position_multiplyer == 1:
                    self.chart1.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                    self.chart2.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                else:
                    self.chart1.chart_view.chart().axisX().setRange(self.x_stop, self.x_start)
                    self.chart2.chart_view.chart().axisX().setRange(self.x_stop, self.x_start)
                self.zoom_value = self.zoom_value + 1
            elif event.key() == Qt.Key.Key_PageDown and self.zoom_value > 0:
                self.x_start = round(self.x_start - self.zoom_factor)
                self.x_stop = round(self.x_stop + self.zoom_factor)
                if (self.x_start - self.zoom_factor) < self.position_min:
                    self.x_start = self.position_min
                if self.position_multiplyer == 1:
                    self.chart1.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                    self.chart2.chart_view.chart().axisX().setRange(self.x_start, self.x_stop)
                else:
                    self.chart1.chart_view.chart().axisX().setRange(self.x_stop, self.x_start)
                    self.chart2.chart_view.chart().axisX().setRange(self.x_stop, self.x_start)
                self.zoom_value = self.zoom_value - 1
            elif event.key() == Qt.Key.Key_Backspace:
                self.bottom.Stack3.hide()
                self.__rollback(-2)
        return False

    # Получить строку из summary по индексу
    def get_summary_row(self, summary_file, row_index: int):
        row = summary_file[row_index]
        return row

    # сеттер счётчика
    def fetchUpdatedCounter(self, value):
        self.counter += value

    # Применение функций переустройства
    def __applyReconctruction(self, type_reconstruction:str):
        self.chart1.series0.clear()
        self.chart2.series.clear()
        curve = self.get_summary_row(self.plan_model.elements(), self.counter)
        #                    круговая
        if type_reconstruction == 'curveChangeRadiusSpinBox':                                                  # радиус
            value = int(self.bottom.curveChangeRadiusSpinBox.value())
            curve.new_radius = value
        elif type_reconstruction == 'spinBoxCurveShift':                                                       # сместить
            value = int(self.bottom.spinBoxCurveShift.value())
            curve.shift(value)
            self.bottom.spinBoxCurveShift.clear()
        elif type_reconstruction == 'spinBoxСurveChangeLength':                                                 # изменить длину
            value = int(self.bottom.spinBoxСurveChangeLength.value()) 
            curve.shift_start(value/ -2)
            curve.shift_end(value / 2)
            self.bottom.spinBoxСurveChangeLength.clear()
        #                       переходная
        elif type_reconstruction == 'spinBoxTransitionChangeLenth_1':                 # Изменить длину
            value = int(self.bottom.spinBoxTransitionChangeLenth_1.value())
            curve.shift_start(value)
            self.bottom.spinBoxTransitionChangeLenth_1.clear()
        elif type_reconstruction == 'spinBoxTransitionChangeLenth_2':
            value = int(self.bottom.spinBoxTransitionChangeLenth_2.value())
            curve.shift_end(value)
            self.bottom.spinBoxTransitionChangeLenth_2.clear()
        elif type_reconstruction == 'spinBoxTransitionShift':                         # Сместить
            value = int(self.bottom.spinBoxTransitionShift.value())
            curve.shift(value)
            self.bottom.spinBoxTransitionShift.clear()
        elif type_reconstruction == 'transitionInsert':                               # Вставить/Разделить
            curve.insert_curve_at(self.bottom.middle_of_transition_segment)
        elif type_reconstruction == 'transitionRemove':                               # Исключить
            curve.remove()
        # ПЕРЕРАСЧЁТ
        try:
            self.new_plan_model = self.plan_model.calc_new_track()

            startPicket = self.options.start_picket.meters
            total_steps = self.new_plan_model.data.shape[0]
            skip = round(self.skip_coefficient * total_steps)
            for i in range(0, total_steps):
                if i % skip == 0:
                    self.chart1.series0.append(startPicket, self.new_plan_model.data.loc[:, 'plan_prj'][i])
                    self.chart2.series.append(startPicket, self.new_plan_model.data.loc[:, 'plan_delta'][i])
                startPicket += self.plan_model.step * self.position_multiplyer

            # пересчёт диапазона для OY
            chart1Min = min(0, self.new_plan_model.data.loc[:, 'plan_prj'].min(), self.new_plan_model.data.loc[:, 'plan_fact'].min())
            chart1Max = max(0, self.new_plan_model.data.loc[:, 'plan_prj'].max(), self.new_plan_model.data.loc[:, 'plan_fact'].max())
            chart1Padding = (chart1Max - chart1Min) * 0.05
            self.chart1.chart_view.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
            # количество тиков
            y_tick1 = self.set_axis_ticks_step(round(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding))))
            if type(y_tick1) == float:
                self.chart1.chart_view.chart().axisY().setLabelFormat("%2g")
            else:
                self.chart1.chart_view.chart().axisY().setLabelFormat("%d")
            self.chart1.chart_view.chart().axisY().setTickInterval(y_tick1)
            #
            chart2Min = min(0, self.new_plan_model.data.loc[:, 'plan_delta'].min())
            chart2Max = max(0, self.new_plan_model.data.loc[:, 'plan_delta'].max())
            chart2Padding = (chart2Max - chart2Min) * 0.05
            self.chart2.chart_view.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
            y_tick2 = self.set_axis_ticks_step(round(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding))))
            if type(y_tick2) == float:
                self.chart2.chart_view.chart().axisY().setLabelFormat("%2g")
            else:
                self.chart2.chart_view.chart().axisY().setLabelFormat("%d")
            self.chart2.chart_view.chart().axisY().setTickInterval(y_tick2)
            #
            self.chart1.chart_view.update()
            self.chart2.chart_view.update()
            #
            self.changes_list.append(self.new_plan_model)
            self.bottom.update_first_stackwidget(self.new_plan_model.elements())
            self.plan_model = self.new_plan_model
            self.bottom.summary = self.new_plan_model
            if not self.unsavedChanges:
                self.unsavedChanges = True
        except ValueError:
            pass
        self.setFocus()

    def update_plan(self, plan: TrackProjectModel):
        # Базовое программное задание
        # В базовом программном задании устанавливаем новый план (из переустройства)
        # Профиль копируем из исходного.
        base = ProgramTaskBaseData(
            measurements_processed=self.__calculation_result.base.measurements_processed,
            detailed_restrictions=self.__calculation_result.base.detailed_restrictions,
            plan=plan.data,
            prof=self.__calculation_result.base.prof,
            alc_plan=None,
            alc_level=None,
            track_split_plan=plan.track_split,
            track_split_prof=self.__calculation_result.base.track_split_prof,
            step=self.__calculation_result.base.step
        )
        self.__calculation_result = ProgramTaskCalculationResultDto(
            options=self.options,
            base=base,
            calculated_task=machine_task_from_base_data_new(base),
            # Пересчитываем машинное программное задание из базового
            summary=base.track_split_plan)
        self.updateCalculationResultSignal.emit(self.__calculation_result)

    # Отмена изменений в зависимости от переданного аргумента:
    #            '0' - сброс всех изменений, '-2' - отказ от последнего изменения
    def __rollback(self, idx: int):
        if len(self.changes_list) > 1:                            # имеет смысл только для '-2'
            self.chart1.series0.clear()
            self.chart2.series.clear()

            startPicket = self.options.start_picket.meters
            total_steps = self.changes_list[idx].data.shape[0]
            skip = round(self.skip_coefficient * total_steps)
            for i in range(0, total_steps):
                if i % skip == 0:
                    self.chart1.series0.append(startPicket, self.changes_list[idx].data.loc[:, 'plan_prj'][i])
                    self.chart2.series.append(startPicket, self.changes_list[idx].data.loc[:, 'plan_delta'][i])
                startPicket += self.changes_list[idx].step * self.position_multiplyer

            #
            chart1Min = min(0, self.changes_list[idx].data.loc[:, 'plan_prj'].min(),
                            self.changes_list[idx].data.loc[:, 'plan_fact'].min())
            chart1Max = max(0, self.changes_list[idx].data.loc[:, 'plan_prj'].max(),
                            self.changes_list[idx].data.loc[:, 'plan_fact'].max())
            chart1Padding = (chart1Max - chart1Min) * 0.05
            self.chart1.chart_view.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
            y_tick1 = self.set_axis_ticks_step(
                round(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding))))
            if type(y_tick1) == float:
                self.chart1.chart_view.chart().axisY().setLabelFormat("%2g")
            else:
                self.chart1.chart_view.chart().axisY().setLabelFormat("%d")
            self.chart1.chart_view.chart().axisY().setTickInterval(y_tick1)
            #
            chart2Min = min(0, self.changes_list[idx].data.loc[:, 'plan_delta'].min())
            chart2Max = max(0, self.changes_list[idx].data.loc[:, 'plan_delta'].max())
            chart2Padding = (chart2Max - chart2Min) * 0.05
            self.chart2.chart_view.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
            y_tick2 = self.set_axis_ticks_step(
                round(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding))))
            if type(y_tick2) == float:
                self.chart2.chart_view.chart().axisY().setLabelFormat("%2g")
            else:
                self.chart2.chart_view.chart().axisY().setLabelFormat("%d")
            self.chart2.chart_view.chart().axisY().setTickInterval(y_tick2)
            self.chart1.chart_view.update()
            self.chart2.chart_view.update()
            #
            self.bottom.summary = self.changes_list[idx]
            self.bottom.update_first_stackwidget(self.changes_list[idx].elements())
            #
            self.plan_model = self.changes_list[idx]
            self.bottom.set_coords_current_segment(self.changes_list[idx].elements(), self.counter)
            self.bottom.summary_len = len(self.plan_model.elements())
            self.bottom.column_starts = self.bottom.get_summary_column(self.plan_model, "start")
            self.bottom.column_ends = self.bottom.get_summary_column(self.plan_model, "end")
            if idx == -2:
                del self.changes_list[-1]    # self.changes_list = self.changes_list[:-2]
            #print('__rollback self.changes_list', idx, [x.elements() for x in self.changes_list])
            self.setFocus()

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

    # Escape => проверка несохранённых изменений. Если 'да' => MessageBox
    def __escapeFunction(self, sygnal_name:str):
        if self.unsavedChanges:                                       # только если были изменения
            if sygnal_name == 'cancel':
                self.__rollback(0)
            elif sygnal_name == 'ok':
                if len(self.changes_list) > 0:
                    self.update_plan(self.plan_model)
                    self.passDataSignal.emit(self.changes_list[-1])            #
        self.closePlanParametersSignal.emit("close")





