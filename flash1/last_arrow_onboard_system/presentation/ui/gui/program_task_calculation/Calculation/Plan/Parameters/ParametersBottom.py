from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QTextEdit, QStackedWidget, QLabel, QSpinBox, QLineEdit,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QToolButton)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QShortcut, QMouseEvent, QIntValidator, QKeyEvent, QFocusEvent
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QSize, QEvent

from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.dto.Workflow import ProgramTaskCalculationResultDto, ProgramTaskCalculationOptionsDto
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType, TrackElement
import sys
import os
import pandas
import numpy as np
import copy
import math
from .VerticalLine import  MoveLineController
from domain.models import VerticalLineModel
from .ModelTable import *
from .ParametersCharts import Chart1




focus_style = ("QWidget:focus {border: 3px solid #FF0000; border-radius: 5px; background-color: white}"
               "QPushButton:pressed {color: black}")


class BottomWidget(QWidget):
    updatedCounterSignal = Signal(int)
    transitionRemoveSignal = Signal(str)
    transitionInsertSignal = Signal(int)
    okReconstructionSignal = Signal(str)
    cancelReconstructionSignal = Signal(str)
    def __init__(self,
                 model1: VerticalLineModel,
                 model2: VerticalLineModel,
                 model3: VerticalLineModel,
                 calculation_result: ProgramTaskCalculationResultDto,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        self.summary = TrackProjectModel.create(TrackProjectType.Plan, self.__calculation_result)
        self.summary_len = len(self.summary.elements())
        self.start_summary = self.summary.elements()
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.motion_direction = str(self.__calculation_result.options.picket_direction).split(".")[1]
        #
        programTaskModel: AbstractPositionedTableModel = StepIndexedDataFramePositionedModel(self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step, self)
        programTaskModel.reset(self.__calculation_result.calculated_task.step, self.__calculation_result.calculated_task.data)
        self.options: ProgramTaskCalculationOptionsDto = self.__calculation_result.options
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        self.counter = 0
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        self.currentPicket = self.__calculation_result.options.start_picket.meters
        self.picket_direction = self.__calculation_result.options.picket_direction
        #
        self.groupbox1_title = self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom']   #  "Тип кривой"
        self.groupbox1_title = self.groupbox1_title.capitalize()
        groupbox2_title = "Переустройство"
        self.groupbox1 = QGroupBox(self.groupbox1_title, alignment=Qt.AlignHCenter)
        self.groupbox2 = QGroupBox(groupbox2_title, alignment=Qt.AlignHCenter)
        self.groupbox1.setStyleSheet(self.set_groupbox_title_style(self.groupbox1_title))
        self.groupbox2.setStyleSheet("QGroupBox{font-size: 18px;font-weight: bold;} QGroupBox:title{margin-top: -15px}")
        self.vbox_groupbox1 = QVBoxLayout()
        self.vbox_groupbox2 = QVBoxLayout()
        self.groupbox1.setLayout(self.vbox_groupbox1)
        self.groupbox2.setLayout(self.vbox_groupbox2)
        #
        self.vertical_model1 = model1
        self.vertical_model2 = model2
        self.vertical_model3 = model3
        self.lineMover1 = MoveLineController(self.vertical_model1, self.vertical_model2, self.vertical_model3, self.__calculation_result)
        self.lineMover2 = MoveLineController(self.vertical_model1, self.vertical_model2, self.vertical_model3, self.__calculation_result)
        self.column_starts = self.get_summary_column(self.summary, "start")
        self.column_ends = self.get_summary_column(self.summary, "end")
        #
        self.models_list = []                           # Таблица слева внизу
        self.tables_list = []
        self.Stack1 = QStackedWidget()
        self.Stack1.setStyleSheet("margin-top: 5px")
        self.__create_first_stackwidget(self.summary.elements())
        self.vbox_groupbox1.addWidget(self.Stack1)
        #
        self.Stack2 = QStackedWidget()                   # Таблица в центре внизу
        self.Stack2.setObjectName("Stack2")
        self.__fill_second_stackwidget(self.summary.elements())
        self.vbox_groupbox2.addWidget(self.Stack2)
        self.selected_function_shortcut = QShortcut(Qt.Key_Return, self)              # выбор клавиший 'enter'
        self.selected_function_shortcut.activated.connect(lambda: self.run_reconstruction_function(self.counter))
        #
        # Для первой нижней таблицы список с 'Длина' & 'Pадиус' для всего отрезка
        self.radius_list:list = []
        #                                 Функции переустройства: наполнение
        self.coordVerticaleLine1 = QLabel("")
        self.coordVerticaleLine2 = QLabel("")
        #            круговая изменить радиус
        self.curveChangeRadiusSpinBox = QSpinBox()
        self.curveChangeRadiusSpinBox.setStyleSheet(focus_style)
        self.curveChangeRadiusSpinBox.setFixedWidth(100)
        self.curveChangeRadiusSpinBox.setRange(-1000000, 1000000)
        font = self.curveChangeRadiusSpinBox.font()
        font.setPointSize(16)
        self.curveChangeRadiusSpinBox.setFont(font)
        self.btn_curve_change_radius = QPushButton('Ok')
        self.btn_curve_change_radius.setStyleSheet(focus_style)
        self.btn_curve_change_radius.setProperty("optionsWindowPushButton", True)
        self.current_radius_value:str = None
        self.previous_radius_value:str = None
        self.currentRadius = QLabel("")
        #            круговая сместить
        self.spinBoxCurveShift = QSpinBox()
        self.spinBoxCurveShift.setStyleSheet(focus_style)
        self.spinBoxCurveShift.setFixedWidth(80)
        self.spinBoxCurveShift.setRange(-1000000, 1000000)
        self.spinBoxCurveShift.setFont(font)
        self.spinBoxCurveShift.valueChanged.connect(self.__handleChangeCurveShift)
        self.spinBoxCurveShift.setKeyboardTracking(False)
        self.btn_curve_shift = QPushButton('Ok')
        self.btn_curve_shift.setStyleSheet(focus_style)
        self.btn_curve_shift.setFixedWidth(80)
        self.btn_curve_shift.setProperty("optionsWindowPushButton", True)
        #            круговая изменить длину
        self.spinBoxСurveChangeLength = QSpinBox()
        self.spinBoxСurveChangeLength.setStyleSheet(focus_style)
        self.spinBoxСurveChangeLength.setRange(-1000000, 1000000)
        self.spinBoxСurveChangeLength.setFixedWidth(100)
        self.spinBoxСurveChangeLength.setFont(font)
        self.spinBoxСurveChangeLength.valueChanged.connect(self.__handleSpinboxCurveChangeLength) #__curveChangeLengthNewPositions)
        self.spinBoxСurveChangeLength.setKeyboardTracking(False)
        self.curveChangeLengthValue = QLabel("")
        self.btn_curve_change_length = QPushButton('Ok')
        self.btn_curve_change_length.setStyleSheet(focus_style)
        self.btn_curve_change_length.setProperty("optionsWindowPushButton", True)
        self.btn_curve_change_length.setMinimumWidth(100)
        #                переходная изменить длину
        self.spinBoxTransitionChangeLenth_1 = QSpinBox()
        self.spinBoxTransitionChangeLenth_1.setStyleSheet(focus_style)
        self.spinBoxTransitionChangeLenth_1.setRange(-1000000, 1000000)
        self.spinBoxTransitionChangeLenth_1.setFont(font)
        self.spinBoxTransitionChangeLenth_1.setFixedWidth(100)
        self.spinBoxTransitionChangeLenth_1.valueChanged.connect(self.__handleTransitionChangeLenthVerticaleLine1)
        self.spinBoxTransitionChangeLenth_1.setKeyboardTracking(False)
        self.displayLengthValue = QLabel("")
        self.btn_transition_change_length_1 = QPushButton('Ok')
        self.btn_transition_change_length_1.setStyleSheet(focus_style)
        self.btn_transition_change_length_1.setProperty("optionsWindowPushButton", True)
        self.btn_transition_change_length_1.setFixedWidth(100)
        self.spinBoxTransitionChangeLenth_2 = QSpinBox()
        self.spinBoxTransitionChangeLenth_2.setStyleSheet(focus_style)
        self.spinBoxTransitionChangeLenth_2.setRange(-1000000, 1000000)
        self.spinBoxTransitionChangeLenth_2.setFont(font)
        self.spinBoxTransitionChangeLenth_2.setFixedWidth(100)
        self.spinBoxTransitionChangeLenth_2.valueChanged.connect(self.__handleTransitionChangeLenthVerticaleLine2)
        self.spinBoxTransitionChangeLenth_2.setKeyboardTracking(False)
        self.btn_transition_change_length_2 = QPushButton('Ok')
        self.btn_transition_change_length_2.setStyleSheet(focus_style)
        self.btn_transition_change_length_2.setProperty("optionsWindowPushButton", True)
        self.btn_transition_change_length_2.setFixedWidth(100)
        #                 переходная сместить
        self.spinBoxTransitionShift = QSpinBox()
        self.spinBoxTransitionShift.setStyleSheet(focus_style)
        self.spinBoxTransitionShift.setRange(-1000000, 1000000)
        self.spinBoxTransitionShift.setFont(font)
        self.spinBoxTransitionShift.setFixedWidth(80)
        self.spinBoxTransitionShift.valueChanged.connect(self.__handleTransitionShift)
        self.spinBoxTransitionShift.setKeyboardTracking(False)
        self.btn_transition_shift = QPushButton('Ok')
        self.btn_transition_shift.setStyleSheet(focus_style)
        self.btn_transition_shift.setProperty("optionsWindowPushButton", True)
        self.btn_transition_shift.setMinimumWidth(100)
        #    переходная вставить
        self.middle_of_transition_segment = None
        #self.escapeCounter = 0
        self.transitionTempVerticalFirstLineTopLevel = None
        self.transitionTempVerticalSecondLineTopLevel = None
        self.Stack3 = QStackedWidget()
        self.vbox_groupbox2.addWidget(self.Stack3)
        self.Stack3.hide()
        #
        self.button_to_left = QToolButton(self.groupbox1)
        self.button_to_left.setStyleSheet(focus_style)
        self.abs_path = os.path.dirname(os.path.abspath(__file__))
        self.button_to_left.setIcon(QIcon(os.path.join(self.abs_path, "Data/left-arrow.png")))
        self.button_to_left.setIconSize(QSize(32, 32))
        self.button_to_left.setFixedSize(QSize(35, 35))
        self.button_to_left.clicked.connect(lambda: self.handle_left_button(self.summary_len))
        #
        self.button_to_right = QToolButton(self.groupbox1)
        self.button_to_right.setStyleSheet(focus_style)
        self.button_to_right.setIcon(QIcon(os.path.join(self.abs_path, "Data/right-arrow.png")))
        self.button_to_right.setIconSize(QSize(32, 32))
        self.button_to_right.setFixedSize(QSize(35, 35))
        self.button_to_right.clicked.connect(lambda: self.handle_right_button(self.summary_len))
        #
        self.toRoundRadiusCurve = False
        rightBottomWidget = QWidget()
        rightBottomLayout = QVBoxLayout()
        rightBottomWidget.setLayout(rightBottomLayout)
        self.how_many_changes = QLabel("Количество изменений ")
        reference_btn = QPushButton("Справка")
        reference_btn.setStyleSheet(focus_style)
        reference_btn.setProperty("optionsWindowPushButton", True)
        reference_btn.setMaximumSize(100, 30)
        reference_btn.clicked.connect(self.__openReference)
        hbox_ok = QHBoxLayout()
        backspace_label = QLabel("Отмена последнего действия - клавиша Backspace")
        ok_btn = QPushButton("Ok")
        ok_btn.setStyleSheet(focus_style)
        ok_btn.setProperty("optionsWindowPushButton", True)
        ok_btn.clicked.connect(self.__okReconstruction)
        ok_lbl = QLabel("Принять все изменения и уйти со страницы")
        hbox_ok.addWidget(ok_btn, 1)
        hbox_ok.addWidget(ok_lbl, 9)
        hbox_cancel = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet(focus_style)
        cancel_btn.setProperty("optionsWindowPushButton", True)
        cancel_btn.clicked.connect(self.__cancelReconstruction)
        cancel_lbl = QLabel("Отказаться от всех изменений и уйти со страницы")
        hbox_cancel.addWidget(cancel_btn, 1)
        hbox_cancel.addWidget(cancel_lbl, 9)
        rightBottomLayout.addWidget(reference_btn)
        rightBottomLayout.addWidget(backspace_label)
        rightBottomLayout.addStretch(1)
        rightBottomLayout.addLayout(hbox_ok)
        rightBottomLayout.addLayout(hbox_cancel)
        rightBottomWidget.setFocusPolicy(Qt.NoFocus)
        rightBottomWidget.setStyleSheet("QLabel{font-size: bold 20px;}")
        #
        hbox = QHBoxLayout()
        hbox.addWidget(self.groupbox1, 1)
        hbox.addWidget(self.groupbox2, 1)
        hbox.addWidget(rightBottomWidget, 1)
        self.installEventFilter(self)
        self.setLayout(hbox)

    # уход со страницы + принятие изменений
    def __okReconstruction(self):
        self.okReconstructionSignal.emit("ok")

    # уход со страницы + отказ от изменений
    def __cancelReconstruction(self):
        self.Stack3.hide()
        self.cancelReconstructionSignal.emit("cancel")

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            len_summer = len(self.summary.elements())
            if event.key() == Qt.Key.Key_Left:
                self.handle_left_button(len_summer)
            elif event.key() == Qt.Key.Key_Right:
                self.handle_right_button(len_summer)
            elif event.key() == Qt.Key.Key_Escape:
                self.Stack3.hide()
        return False

    def __openReference(self):
        msg = QMessageBox(self)
        msg.setText("Перемещение (перенос фокуса) по странице клавишей 'tab', 'shift+tab' либо стрелками.\n\n"
                    "Перемещение вертикальных черт (смена диапазона) - стрелки на клавиатуре либо над окном 'Тип Кривой' \n\n"
                    "Запуск выбранной функции переустройства - клавиша Enter \n\n"
                    "Нажать кнопку - клавиша пробел \n\n"
                    "Закрыть открытый интерфейс функции переустройства - клавиша Escape \n\n"
                    "Увеличить/Уменьшить масштаб на 1/10 - клавиши PageUp/PageDown соответственно\n\n"
                    "Сдвинуть график с увеличенным масштабом влево/вправо - \n сочетания клавиш Alt+Left/Alt+Right соответственно \n\n"
                    "Отказ от последнего изменения - клавиша Backspace")
        msg.setStyleSheet("QMessageBox {font: 20px; background-color: #fefefe;}")
        msg.exec()

    # Создание нижней левой таблицы 'Тип кривой'. Запускается один раз при запуске окна
    def __create_first_stackwidget(self, data: list):
        for i in range(0, self.summary_len, 1):
            model = PandasModel(self.__fill_first_stackwidget(data, i))
            model.setHeaderData(3, Qt.Horizontal, ['Параметры', 'Существующие', 'Допускаемые'])
            table = MyTable()
            #
            table_font = QFont()
            table_font.setPointSize(13)
            table.setFont(table_font)
            #
            self.models_list.append(model)
            table.setModel(model)
            self.tables_list.append(table)
            self.Stack1.addWidget(table)

    def update_first_stackwidget(self, elements: list[TrackElement]):
        self.models_list.clear()
        self.tables_list.clear()
        for i in range(self.Stack1.count()):
            widget = self.Stack1.widget(0)
            self.Stack1.removeWidget(widget)
        for i in range(0, len(elements), 1):
            model = PandasModel(self.__fill_first_stackwidget(elements, i))
            model.setHeaderData(3, Qt.Horizontal, ['Параметры', 'Существующие', 'Допускаемые'])
            table = MyTable()
            #
            table_font = QFont()
            table_font.setPointSize(13)
            table.setFont(table_font)
            #
            self.models_list.append(model)
            table.setModel(model)
            self.tables_list.append(table)
            self.Stack1.addWidget(table)
        self.Stack1.setCurrentIndex(self.counter)
        self.Stack2.setCurrentIndex(self.counter)

    # Cтартовое заполнение таблицы. Запускается внутри __create_first_stackwidget().
    def __fill_first_stackwidget(self, data: list, ind: int):
        result = None
        _data = data[ind].to_dict()
        if _data['geom'] == 'переходная кривая':
            # колонка 'существующие'
            table_transition[0][1] = ('%.2f' % _data['length'])
            table_transition[1][1] = ('%.2f' % _data['slope_fact'])
            table_transition[2][1] = ('%.2f' % _data['psi_fact'])
            table_transition[3][1] = ('%.2f' % _data['v_wheel_fact'])
            table_transition[4][1] = ('%.2f' % _data['v_max_fact'])
            # колонка 'Допускаемые'
            table_transition[0][2] = ('%.2f' % _data['length'])
            table_transition[1][2] = ('%.2f' % _data['slope_norm'])
            table_transition[2][2] = ('%.2f' % _data['psi_norm'])
            table_transition[3][2] = ('%.2f' % _data['v_wheel_norm'])
            if _data['v_max_norm']:
                table_transition[4][2] = ('%.2f' % _data['v_max_norm'])
            result = table_transition
        elif _data['geom'] == 'круговая кривая':
            # колонка 'существующие'
            table_curve[0][1] = ('%.2f' % _data['radius_fact'])
            table_curve[1][1] = ('%.2f' % _data['length'])
            table_curve[2][1] = ('%.2f' % _data['level_fact'])
            table_curve[3][1] = ('%.2f' % _data['a_nepog_fact'])
            table_curve[4][1] = ('%.2f' % _data['v_max_fact'])
            # колонка 'Допускаемые'
            table_curve[0][2] = ('%.2f' % _data['radius_norm'])
            table_curve[1][2] = ('%.2f' % _data['length'])
            table_curve[2][2] = ('%.2f' % _data['level_norm'])
            table_curve[3][2] = ('%.2f' % _data['a_nepog_norm'])
            table_curve[4][2] = ('%.2f' % _data['v_max_norm'])
            result = table_curve
        elif _data['geom'] == 'прямая':
            result = table_straight
        return result

    # Заполнение нижней второй таблицы "функции переустройства". Запускается один раз при запуске окна
    def __fill_second_stackwidget(self, data: str):
        listwidget_font = QFont()
        listwidget_font.setPixelSize(20)
        for i in range(0, self.summary_len, 1):
            self.list_widget = QListWidget()
            self.list_widget.setFont(listwidget_font)
            _data = data[i].to_dict()
            if _data['geom'] == 'переходная кривая':
                self.list_widget.addItems(['Изменить Lпк', 'Разделить ПК', 'Сместить ПК', 'Исключить ПК'])
                object_name = 'transition' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)
            elif _data['geom'] == 'круговая кривая':
                self.list_widget.addItems(['Изменить радиус', 'Изменить длину', 'Сместить КК'])   # 'Изменить ВНР',
                object_name = 'curve' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)
            elif _data['geom'] == 'прямая':
                self.list_widget.addItems(['', '', ''])
                object_name = 'straight' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)

    # Запуск выбранной функции переустройства
    def run_reconstruction_function(self, idx):
        # ___ Переходная ___
        if self.Stack2.widget(idx).currentItem().text() == 'Изменить Lпк':
            changeLengthWidget = self.__transitionChangeLength(idx)
            self.Stack3.addWidget(changeLengthWidget)
            self.Stack3.setCurrentWidget(changeLengthWidget)
            self.Stack3.show()
        elif self.Stack2.widget(idx).currentItem().text() == 'Разделить ПК':
            self.Stack3.hide()
            self.__transitionDivide(idx)
        elif self.Stack2.widget(idx).currentItem().text() == 'Сместить ПК':
            chiftWidget = self.__transitionShiftInterface(idx)
            self.Stack3.addWidget(chiftWidget)
            self.Stack3.setCurrentWidget(chiftWidget)
            self.Stack3.show()
        elif self.Stack2.widget(idx).currentItem().text() == 'Исключить ПК':
            self.transitionRemoveSignal.emit('go')
            self.Stack3.hide()
        #     ___ Круговая ___
        elif self.Stack2.widget(idx).currentItem().text() == 'Изменить радиус':
            curveChangeRadius = self.__curveChangeRadius(idx)
            self.Stack3.addWidget(curveChangeRadius)
            self.Stack3.setCurrentWidget(curveChangeRadius)
            self.Stack3.show()
        elif self.Stack2.widget(idx).currentItem().text() == 'Изменить длину':
            curveChangeLengthWidget = self.__curveChangeLength(idx)
            self.Stack3.addWidget(curveChangeLengthWidget)
            self.Stack3.setCurrentWidget(curveChangeLengthWidget)
            self.Stack3.show()
        elif self.Stack2.widget(idx).currentItem().text() == 'Сместить КК':
            interface = self.__curveShift(idx)
            self.Stack3.addWidget(interface)
            self.Stack3.setCurrentWidget(interface)
            self.Stack3.show()

    # Получить строку из summary по индексу
    def get_summary_row(self, summary_file, row_index: int):
        row = summary_file[row_index]
        return row

    # Получить колонку из summary
    def get_summary_column(self, summary_file:list, column_name: str):
        column = []
        for every_dict in summary_file.elements():
            column.append(every_dict.to_dict()[column_name])
        return column

    # кнопка-стрелка 'влево'
    def handle_left_button(self, summary_len: int):
        self.Stack3.hide()
        column_start = self.get_summary_column(self.summary, "start")
        column_end = self.get_summary_column(self.summary, "end")
        if 0 < self.counter < summary_len:
            self.updatedCounterSignal.emit(-1)
            self.counter -= 1
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter('to left', column_start, column_end)
            self.lineMover2.eventFilter('to left', column_start, column_end)
            print('handle_left_button ', self.summary.elements())
            if self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'переходная кривая':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Переходная кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'круговая кривая':
                self.groupbox1.setTitle("Круговая кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Круговая кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'прямая':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Прямая"))
            self.setFocus()

    # кнопка-стрелка 'вправо'
    def handle_right_button(self, summary_len: int):
        self.Stack3.hide()
        column_start = self.get_summary_column(self.summary, "start")
        column_end = self.get_summary_column(self.summary, "end")
        if 0 <= self.counter < (summary_len - 1):
            self.updatedCounterSignal.emit(1)
            self.counter += 1
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter('to right', column_start, column_end)
            self.lineMover2.eventFilter('to right', column_start, column_end)  # ?
            print('handle_right_button ', self.summary.elements())
            if self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'переходная кривая':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Переходная кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'круговая кривая':
                self.groupbox1.setTitle("Круговая кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Круговая кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'прямая':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Прямая"))
            self.setFocus()

    # стиль заголовка левого нижнего групбокса
    def set_groupbox_title_style(self, segment_type:str):
        segment_type_style = {"Круговая кривая":"QGroupBox{font-size:18px; font-weight:bold;} QGroupBox:title{color:red; margin-top: -5px; margin-left: 30px}",
                              "Переходная кривая":"QGroupBox{font-size:18px; font-weight:bold;} QGroupBox:title{color:green;}",
                              "Прямая":"QGroupBox{font-size:18px; font-weight:bold;} QGroupBox:title{color:black;}"}
        return segment_type_style[segment_type]

    # принудительно ставим на место границы последнего (текущего) изменённого диапазона саммари
    def set_coords_current_segment(self, previous_model:list, c:int):   # 'c' - counter
        coord1 = self.startPicket + self.position_multiplyer * self.get_summary_row(previous_model, c).to_dict()['start']
        coord2 = self.startPicket + self.position_multiplyer * self.get_summary_row(previous_model, c).to_dict()['end']
        self.vertical_model1.shiftLine(coord1)
        self.vertical_model2.shiftLine(coord2)

    #=======================================================================================================================
    # Функции, получающие сигналы от спинбоксов (через кнопки), меняют только текстовые метки и значения в таблицах
    #                             Вся перерисовка графиков в ParametersMain.py
    # =======================================================================================================================

    # ________________________________________ Переходная (transition)        _______________________

    #                                 'Изменить длину': обе верт. черты идут в любую сторону
    # Создание интерфейса
    def __transitionChangeLength(self, idx: int):
        groupboxChangeLength = QGroupBox()
        changeLengthLayout = QHBoxLayout()
        groupboxChangeLength.setLayout(changeLengthLayout)
        self.displayLengthValue = QLabel(
            str( round(self.get_summary_row(self.summary.elements(), idx).to_dict()['end'] - self.get_summary_row(self.summary.elements(), idx).to_dict()['start'], 1 )))
        self.displayLengthValue.setStyleSheet("font-size: 18px;font-weight: bold;")
        title_label = QLabel("Длина")
        title_label.setStyleSheet("font-size: 18px;")
        #self.btn_transition_change_length_1.clicked.connect(self.__handleTransitionChangeLenthVerticaleLine1)
        #self.btn_transition_change_length_2.clicked.connect(self.__handleTransitionChangeLenthVerticaleLine2)
        changeLengthLayout.addWidget(self.spinBoxTransitionChangeLenth_1)
        changeLengthLayout.addWidget(self.btn_transition_change_length_1)
        changeLengthLayout.addStretch(1)
        changeLengthLayout.addWidget(title_label)
        changeLengthLayout.addWidget(self.displayLengthValue)
        changeLengthLayout.addStretch(1)
        changeLengthLayout.addWidget(self.spinBoxTransitionChangeLenth_2)
        changeLengthLayout.addWidget(self.btn_transition_change_length_2)
        return groupboxChangeLength

    # левая полоса
    def __handleTransitionChangeLenthVerticaleLine1(self, value):
        res1 = self.get_summary_row(self.summary.elements(), self.counter).to_dict()['start']
        res2 = self.get_summary_row(self.summary.elements(), self.counter).to_dict()['end']
        self.vertical_model1.shiftLine(self.startPicket + self.position_multiplyer * (res1 + value))
        result = round(math.fabs(res2 - res1), 1)
        self.displayLengthValue.setText(str(result))
        #self.models_list[self.counter].setData(self.models_list[self.counter].index(0, 1), result, Qt.EditRole)
        #self.models_list[self.counter].dataChanged.connect(
        #                     self.tables_list[self.counter].update(self.models_list[self.counter].index(0, 1)))

    # правая полоса
    def __handleTransitionChangeLenthVerticaleLine2(self, value):
        res1 = self.get_summary_row(self.summary.elements(), self.counter).to_dict()['start']
        res2 = self.get_summary_row(self.summary.elements(), self.counter).to_dict()['end']
        self.vertical_model2.shiftLine(self.startPicket + self.position_multiplyer * (res2 + value))
        result = round(math.fabs(res2 - res1), 1)
        self.displayLengthValue.setText(str(result))

    #                                'Разделить'
    def __transitionDivide(self, idx: int):
        firstLineX = self.get_summary_row(self.summary.elements(), idx).to_dict()['start']
        secondLineX = self.get_summary_row(self.summary.elements(), idx).to_dict()['end']
        self.middle_of_transition_segment = round(firstLineX + (secondLineX - firstLineX) * 0.5)
        self.transitionInsertSignal.emit('go')

    #                                'Сместить'  (синхронно обе черты в одну сторону)
    # Создание интерфейса
    def __transitionShiftInterface(self, idx: int):
        groupboxTransitionShift = QGroupBox()
        transitionShiftLayout = QHBoxLayout()
        groupboxTransitionShift.setLayout(transitionShiftLayout)
        titleCoordVerticaleLine1 = QLabel("Левая граница")
        titleCoordVerticaleLine1.setStyleSheet("font-size: 18px;")
        titleCoordVerticaleLine2 = QLabel("Правая граница")
        titleCoordVerticaleLine2.setStyleSheet("font-size: 18px;")
        #   ?
        self.coordVerticaleLine1 = QLabel(str(round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['start']))) # / 0.185, 2)))
        self.coordVerticaleLine1.setStyleSheet("font: bold 18px;")
        self.coordVerticaleLine2 = QLabel(str(round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['end']))) # / 0.185, 2)))
        self.coordVerticaleLine2.setStyleSheet("font: bold 18px;")

        title_label = QLabel("Смещение на ")
        title_label.setStyleSheet("font-size: 1px;color: red;font-weight: bold;")
        transitionShiftLayout.addWidget(self.spinBoxTransitionShift)
        transitionShiftLayout.addStretch(1)
        transitionShiftLayout.addWidget(titleCoordVerticaleLine1)
        transitionShiftLayout.addWidget(self.coordVerticaleLine1)
        transitionShiftLayout.addStretch(1)
        transitionShiftLayout.addWidget(titleCoordVerticaleLine2)
        transitionShiftLayout.addWidget(self.coordVerticaleLine2)
        transitionShiftLayout.addStretch(1)
        transitionShiftLayout.addWidget(self.btn_transition_shift)
        return groupboxTransitionShift

    def __handleTransitionShift(self, value):
        res1 = round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), self.counter).to_dict()['start'] + self.position_multiplyer * value)
        res2 = round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), self.counter).to_dict()['end'] + self.position_multiplyer * value)
        self.vertical_model1.shiftLine(res1)
        self.vertical_model2.shiftLine(res2)
        self.coordVerticaleLine1.setText(str(res1))
        self.coordVerticaleLine2.setText(str(res2))
        #self.spinBoxTransitionShift.clear()

    #                             'Исключить' полностью в ParametersMain

    # ____________________________________________________ Круговая ________________________________
    #                                             'Изменить радиус'
    # создать интерфейс
    def __curveChangeRadius(self, idx):
        groupboxCurveChangeRadius = QGroupBox()
        groupboxCurveChangeRadiusLayout = QVBoxLayout()
        groupboxCurveChangeRadiusLayout_1 = QHBoxLayout()
        groupboxCurveChangeRadiusLayout_2 = QHBoxLayout()
        groupboxCurveChangeRadiusLayout.addLayout(groupboxCurveChangeRadiusLayout_1)
        groupboxCurveChangeRadiusLayout.addLayout(groupboxCurveChangeRadiusLayout_2)
        groupboxCurveChangeRadius.setLayout(groupboxCurveChangeRadiusLayout)
        self.btn_curve_change_radius.clicked.connect(self.__handleCurveChangeRadiusSpinBox)
        self.currentRadius.setText( str(round(self.get_summary_row(self.summary.elements(), idx).to_dict()['radius_fact'])))
        self.currentRadius.setStyleSheet("font: bold 18px;")
        how_many_change_label = QLabel("Новый радиус")
        how_many_change_label.setStyleSheet("font: 18px;")
        m_change_label = QLabel("метров")
        m_change_label.setStyleSheet("font: 18px;")
        title_label = QLabel("Радиус = ")
        title_label.setStyleSheet("font: 18px;")
        groupboxCurveChangeRadiusLayout_1.addWidget(how_many_change_label)
        groupboxCurveChangeRadiusLayout_1.addWidget(self.curveChangeRadiusSpinBox)
        groupboxCurveChangeRadiusLayout_1.addWidget(m_change_label)
        groupboxCurveChangeRadiusLayout_1.addWidget(self.btn_curve_change_radius)
        groupboxCurveChangeRadiusLayout.addStretch(3)
        groupboxCurveChangeRadiusLayout_2.addWidget(title_label)
        groupboxCurveChangeRadiusLayout_2.addWidget(self.currentRadius)
        groupboxCurveChangeRadiusLayout_2.addStretch(3)
        groupboxCurveChangeRadiusLayout.addStretch(3)
        return groupboxCurveChangeRadius

    def __handleCurveChangeRadiusSpinBox(self):
        updatedRadius = self.curveChangeRadiusSpinBox.value()
        self.currentRadius.setText(str(updatedRadius))
        #self.models_list[self.counter].setData(self.models_list[self.counter].index(0, 1), updatedRadius, Qt.EditRole)
        #self.models_list[self.counter].dataChanged.connect(self.tables_list[self.counter].update(self.models_list[self.counter].index(0, 1)))
        self.curveChangeRadiusSpinBox.clear()

    #                                             'Изменить длину' (обе верт. черты синхронно идут в разные стороны)
    # создать интерфейс
    def __curveChangeLength(self, idx):
        groupboxCurveShift = QGroupBox()
        сurveVShiftLayout = QVBoxLayout()
        groupboxCurveShift.setLayout(сurveVShiftLayout)
        end = self.get_summary_row(self.summary.elements(), idx).to_dict()['end']
        start = self.get_summary_row(self.summary.elements(), idx).to_dict()['start']
        length = round(math.fabs(end - start))
        how_many_change_label = QLabel("Изменили на ")
        how_many_change_label.setStyleSheet("font: 18px;")
        m_change_label = QLabel("метров")
        m_change_label.setStyleSheet("font: 18px;")
        titleLength = QLabel("Длина")
        titleLength.setStyleSheet("font-size: 16px;")
        titleCoordVerticaleLine1 = QLabel("Левая граница")
        titleCoordVerticaleLine1.setStyleSheet("font-size: 16px;")
        titleCoordVerticaleLine2 = QLabel("Правая граница")
        titleCoordVerticaleLine2.setStyleSheet("font-size: 16px;")
        self.coordVerticaleLine1 = QLabel("")
        self.coordVerticaleLine2 = QLabel("")
        self.coordVerticaleLine1 = QLabel(str(round(self.startPicket + self.position_multiplyer * start)))
        self.coordVerticaleLine2 = QLabel(str(round(self.startPicket + self.position_multiplyer * end)))
        self.coordVerticaleLine2.setStyleSheet("font: bold 16px;")
        self.coordVerticaleLine1.setStyleSheet("font: bold 16px;")
        self.curveChangeLengthValue.setNum(length)
        self.curveChangeLengthValue.setStyleSheet("font: bold 16px;")
        сurveH1ShiftLayout = QHBoxLayout()
        сurveH2ShiftLayout = QHBoxLayout()
        сurveH1ShiftLayout.addStretch(1)
        сurveH1ShiftLayout.addWidget(how_many_change_label)
        сurveH1ShiftLayout.addWidget(self.spinBoxСurveChangeLength)
        сurveH1ShiftLayout.addWidget(m_change_label)
        сurveH1ShiftLayout.addStretch(1)
        сurveH1ShiftLayout.addWidget(self.btn_curve_change_length)
        сurveH2ShiftLayout.addStretch(1)
        сurveH2ShiftLayout.addWidget(titleCoordVerticaleLine1)
        сurveH2ShiftLayout.addWidget(self.coordVerticaleLine1)
        сurveH2ShiftLayout.addStretch(1)
        сurveH2ShiftLayout.addWidget(self.curveChangeLengthValue)
        сurveH2ShiftLayout.addStretch(1)
        сurveH2ShiftLayout.addWidget(titleCoordVerticaleLine2)
        сurveH2ShiftLayout.addWidget(self.coordVerticaleLine2)
        сurveH2ShiftLayout.addStretch(1)
        сurveVShiftLayout.addLayout(сurveH1ShiftLayout)
        сurveVShiftLayout.addLayout(сurveH2ShiftLayout)
        return groupboxCurveShift

    def __handleSpinboxCurveChangeLength(self, value):
        res1 = round(self.startPicket + self.position_multiplyer *
                     (self.get_summary_row(self.summary.elements(), self.counter).to_dict()['start'] - value/2))
        res2 = round(self.startPicket + self.position_multiplyer *
                     (self.get_summary_row(self.summary.elements(), self.counter).to_dict()['end'] + value/2))
        self.vertical_model1.shiftLine(res1)
        self.vertical_model2.shiftLine(res2)
        result = math.fabs(res2 - res1)
        self.curveChangeLengthValue.setNum(result)
        self.coordVerticaleLine1.setText(str(res1))
        self.coordVerticaleLine2.setText(str(res2))


    #                                             'Сместить'   (обе верт. черты синхронно идут в одну сторону)
    # создать интерфейс
    def __curveShift(self, idx):
        groupboxCurveShift = QGroupBox()
        curveShiftLayout = QHBoxLayout()
        groupboxCurveShift.setLayout(curveShiftLayout)
        titleCoordVerticaleLine1 = QLabel("Левая граница: ")
        titleCoordVerticaleLine1.setStyleSheet("font-size: 18px;")
        titleCoordVerticaleLine2 = QLabel("Правая граница: ")
        titleCoordVerticaleLine2.setStyleSheet("font-size: 18px;")
        self.coordVerticaleLine1 = QLabel("")
        self.coordVerticaleLine2 = QLabel("")
        self.coordVerticaleLine1 = QLabel(
                str(round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['start'], 1)))
        self.coordVerticaleLine1.setStyleSheet("font: bold 18px;")
        self.coordVerticaleLine2 = QLabel(
                str(round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['end'], 1)))
        self.coordVerticaleLine2.setStyleSheet("font: bold 18px;")
        #title_label = QLabel("Смещение на ")
        #title_label.setStyleSheet("font-size: 1px;color: red;font-weight: bold;")
        curveShiftLayout.addWidget(self.spinBoxCurveShift)
        curveShiftLayout.addStretch(1)
        curveShiftLayout.addWidget(titleCoordVerticaleLine1)
        curveShiftLayout.addWidget(self.coordVerticaleLine1)
        curveShiftLayout.addStretch(1)
        curveShiftLayout.addWidget(titleCoordVerticaleLine2)
        curveShiftLayout.addWidget(self.coordVerticaleLine2)
        curveShiftLayout.addStretch(1)
        curveShiftLayout.addWidget(self.btn_curve_shift)
        #self.btn_curve_shift.clicked.connect(self.__handleChangeCurveShift)
        return groupboxCurveShift

    def __handleChangeCurveShift(self, value):
        value = int(self.spinBoxCurveShift.value())
        res1 = round(self.startPicket + self.position_multiplyer * (self.get_summary_row(self.summary.elements(), self.counter).to_dict()['start'] + value))
        res2 = round(self.startPicket + self.position_multiplyer * (self.get_summary_row(self.summary.elements(), self.counter).to_dict()['end'] + value))
        self.vertical_model1.shiftLine(res1)
        self.vertical_model2.shiftLine(res2)
        self.coordVerticaleLine1.setText(str(res1))
        self.coordVerticaleLine2.setText(str(res2))
        #self.spinBoxCurveShift.clear()


#===============================================================================================================================

    # размещение кнопок-стрелок в заголовке groupbpx'a
    def resizeEvent(self, event):
        w = self.groupbox1.size().width()
        x = (w - 250) / 2
        self.button_to_left.move(x, -1)
        x = (w - 182) / 2 + 220
        self.button_to_right.move(x, -1)
