from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QTextEdit, QStackedWidget, QLabel,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QToolButton)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QShortcut, QMouseEvent
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QSize, QEvent
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.calculations.plan_model import  TrackProjectModel, TrackProjectType
from domain.dto.Workflow import ProgramTaskCalculationResultDto
import sys
import os
from .VerticalLine import  MoveLineController
from domain.models.VerticalLineModel import VerticalLineModel
from .ModelTable import *
#from .ParametersCharts import Chart1
import pandas
import math

focus_style = ("QWidget:focus {border: 3px solid #FF0000; border-radius: 5px; background-color: white}"
               "QPushButton:pressed {color: black}")



class BottomWidget(QWidget):
    updatedCounterSignal = Signal(int)
    okReconstructionSignal = Signal(str)
    cancelReconstructionSignal = Signal(str)
    def __init__(self,
                 model1: VerticalLineModel,
                 model2: VerticalLineModel,
                 calculation_result: ProgramTaskCalculationResultDto,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        self.counter = 0
        self.summary = TrackProjectModel.create(TrackProjectType.Profile, self.__calculation_result)
        self.start_summary = self.summary.elements()
        self.summary_len = len(self.summary.elements())
        self.startPicket = self.__calculation_result.options.start_picket.meters
        #
        self.options = self.__calculation_result.options
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        self.groupbox1_title = self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom']
        self.groupbox1_title = self.groupbox1_title.capitalize()
        groupbox2_title = "Переустройство"
        self.groupbox1 = QGroupBox("Вертикальная кривая", alignment=Qt.AlignHCenter)
        self.groupbox2 = QGroupBox(groupbox2_title, alignment=Qt.AlignHCenter)
        self.groupbox1.setStyleSheet(self.set_groupbox_title_style(self.groupbox1_title))
        self.groupbox2.setStyleSheet("QGroupBox{font-size: 22px;font-weight: bold;} QGroupBox:title{margin-top: -15px}")
        self.vbox_groupbox1 = QVBoxLayout()
        self.vbox_groupbox2 = QVBoxLayout()
        self.groupbox1.setLayout(self.vbox_groupbox1)
        self.groupbox2.setLayout(self.vbox_groupbox2)
       #
        self.vertical_model1 = model1
        self.vertical_model2 = model2
        self.lineMover1 = MoveLineController(self.vertical_model1, self.vertical_model2, self.__calculation_result)
        self.lineMover2 = MoveLineController(self.vertical_model1, self.vertical_model2, self.__calculation_result)
        #
        self.models_list = []        # Таблица слева внизу
        self.tables_list = []
        self.Stack1 = QStackedWidget()
        self.__fill_first_stackwidget(self.summary.elements())
        self.Stack1.setStyleSheet("margin-top: 5px")
        self.vbox_groupbox1.addWidget(self.Stack1)
        #
        self.Stack2 = QStackedWidget()
        self.Stack2.setObjectName("Stack2")
        self.Stack2.setStyleSheet("margin-top: 3px")
        self.__fill_second_stackwidget(self.summary.elements())
        self.vbox_groupbox2.addWidget(self.Stack2)
        self.selected_function_shortcut = QShortcut(Qt.Key_Return, self)                       # выбор клавиший 'enter'
        self.selected_function_shortcut.activated.connect(lambda: self.run_reconstruction_function(self.counter))

        #             круговая изменить радиус
        self.curveChangeRadiusSpinBox = QSpinBox()
        self.curveChangeRadiusSpinBox.setStyleSheet(focus_style)
        self.curveChangeRadiusSpinBox.setFixedWidth(100)
        self.curveChangeRadiusSpinBox.setRange(-1000000, 1000000)
        font = self.curveChangeRadiusSpinBox.font()
        font.setPointSize(16)
        self.curveChangeRadiusSpinBox.setFont(font)
        self.btn_curve_change_radius = QPushButton('Ok')
        self.btn_curve_change_radius.setStyleSheet(focus_style)
        self.btn_curve_change_radius.setFixedWidth(100)
        self.btn_curve_change_radius.setProperty("optionsWindowPushButton", True)

        #             круговая сместить
        self.spinBoxCurveShift = QSpinBox()
        self.spinBoxCurveShift.setStyleSheet(focus_style)
        self.spinBoxCurveShift.setFixedWidth(80)
        self.spinBoxCurveShift.setRange(-1000000, 1000000)
        self.spinBoxCurveShift.setFont(font)
        self.spinBoxCurveShift.valueChanged.connect(self.__handleChangeCurveShift)
        self.btn_curve_shift = QPushButton('Ok')
        self.btn_curve_shift.setStyleSheet(focus_style)
        self.btn_curve_shift.setFixedWidth(100)
        self.btn_curve_shift.setProperty("optionsWindowPushButton", True)

        # круговая изменить длину
        self.spinBoxСurveChangeLength = QSpinBox()
        self.spinBoxСurveChangeLength.setStyleSheet(focus_style)
        self.spinBoxСurveChangeLength.setRange(-1000000, 1000000)
        self.spinBoxСurveChangeLength.setFixedWidth(100)
        self.spinBoxСurveChangeLength.setFont(font)
        self.spinBoxСurveChangeLength.valueChanged.connect(self.__handleSpinboxCurveChangeLength)
        self.spinBoxСurveChangeLength.setKeyboardTracking(False)
        self.curveChangeLengthValue = QLabel("")
        self.btn_curve_change_length = QPushButton('Ok')
        self.btn_curve_change_length.setStyleSheet(focus_style)
        self.btn_curve_change_length.setFixedWidth(100)
        self.btn_curve_change_length.setProperty("optionsWindowPushButton", True)

        # переходная изменить длину
        self.spinBoxTransitionChangeLenth_1 = QSpinBox()
        self.spinBoxTransitionChangeLenth_1.setStyleSheet(focus_style)
        self.spinBoxTransitionChangeLenth_1.setFont(font)
        self.spinBoxTransitionChangeLenth_2 = QSpinBox()
        self.spinBoxTransitionChangeLenth_2.setStyleSheet(focus_style)
        self.spinBoxTransitionChangeLenth_2.setFont(font)
        # переходная сместить
        self.spinBoxTransitionShift = QSpinBox()
        self.spinBoxTransitionShift.setStyleSheet(focus_style)
        self.spinBoxTransitionShift.setFont(font)
        #
        self.escapeCounter = 0
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
        self.button_to_left.clicked.connect(self.handle_left_button)
        #
        self.button_to_right = QToolButton(self.groupbox1)
        self.button_to_right.setStyleSheet(focus_style)
        self.button_to_right.setIcon(QIcon(os.path.join(self.abs_path, "Data/right-arrow.png")))
        self.button_to_right.setIconSize(QSize(32, 32))
        self.button_to_right.setFixedSize(QSize(35, 35))
        self.button_to_right.clicked.connect(self.handle_right_button)
        #
        self.toRoundRadiusCurve = False
        rightBottomWidget = QWidget()
        rightBottomLayout = QVBoxLayout()
        rightBottomWidget.setLayout(rightBottomLayout)
        self.how_many_changes = QLabel("Количество изменений ")
        reference_btn = QPushButton("Справка")
        backspace_label = QLabel("Отмена последнего действия - клавиша Backspace")
        reference_btn.setStyleSheet(focus_style)
        reference_btn.setFixedWidth(100)
        reference_btn.setProperty("optionsWindowPushButton", True)
        reference_btn.setMaximumSize(70, 30)
        reference_btn.clicked.connect(self.__openReference)
        #rightBottomLayout.addWidget(self.how_many_changes)
        rightBottomLayout.addWidget(reference_btn)
        rightBottomLayout.addStretch(1)
        rightBottomLayout.addWidget(backspace_label)
        hbox_ok = QHBoxLayout()
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
        cancel_btn.setFixedWidth(120)
        cancel_btn.setProperty("optionsWindowPushButton", True)
        cancel_btn.clicked.connect(self.__cancelReconstruction)
        cancel_lbl = QLabel("Отказаться от всех изменений и уйти со страницы")
        hbox_cancel.addWidget(cancel_btn, 1)
        hbox_cancel.addWidget(cancel_lbl, 9)
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

    def __openReference(self):
        msg = QMessageBox(self)
        msg.setText("Перемещение (перенос фокуса) по странице клавишей 'tab', 'shift+tab' либо стрелками.\n\n"
                    "Перемещение вертикальных черт (смена диапазона) - стрелки на клавиатуре либо над окном 'Тип Кривой' \n"
                    "Запуск выбранной функции переустройства - клавиша Enter \n"
                    "Нажать кнопку - клавиша пробел "
                    "Закрыть открытый интерфейс функции переустройства - клавиша Escape")
        msg.setStyleSheet("QMessageBox {font: 20px; background-color: #fefefe;}")
        msg.exec()

    #Создание нижней левой таблицы 'Тип кривой'. Запускается один раз при запуске окна
    def __fill_first_stackwidget(self, data: list):
        for i in range(0, self.summary_len, 1):
            self.model = PandasModel(self.__get_data_by_index(data, i))
            self.model.setHeaderData(3, Qt.Horizontal, ['Параметры', 'Существующие', 'Допускаемые'])
            self.table = MyTable()
            #
            table_font = QFont()
            table_font.setPointSize(13)
            self.table.setFont(table_font)
            #
            self.models_list.append(self.model)
            self.table.setModel(self.model)
            self.tables_list.append(self.table)
            self.Stack1.addWidget(self.table)

    # стартовое заполнение таблицы. Запускается внутри __fill_first_stackwidget().
    def __get_data_by_index(self, data: list, ind: int):
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
                self.list_widget.addItem('')   #['Изменить Lпк', 'Разделить ПК', 'Сместить ПК', 'Исключить ПК'])
                self.Stack2.addWidget(self.list_widget)
            if _data['geom'] == 'круговая кривая':
                self.list_widget.addItems(['Изменить радиус', 'Изменить длину', 'Сместить КК'])   # 'Изменить ВНР',
                object_name = 'curve' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)
            elif _data['geom'] == 'прямая':
                self.list_widget.addItems(['', '', ''])
                object_name = 'straight' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)

    def update_first_stackwidget(self, elements: list):
        self.models_list.clear()
        self.tables_list.clear()
        # clear stacked widget
        for i in range(self.Stack1.count()):
            widget = self.Stack1.widget(0)
            self.Stack1.removeWidget(widget)
        for i in range(0, len(elements), 1):
            model = PandasModel(self.__fill_first_stackwidget(elements))
            model.setHeaderData(3, Qt.Horizontal, ['Параметры', 'Существующие', 'Допускаемые'])
            table = MyTable()
            table_font = QFont()
            table_font.setPointSize(13)
            table.setFont(table_font)
            self.models_list.append(model)
            table.setModel(model)
            self.tables_list.append(table)
            self.Stack1.addWidget(table)
        self.Stack1.setCurrentIndex(self.counter)
        self.Stack2.setCurrentIndex(self.counter)

    # Запуск выбранной функции переустройства
    def run_reconstruction_function(self, idx):
        #     ___ Круговая ___
        if self.Stack2.widget(idx).currentItem().text() == 'Изменить радиус':
            curveChangeRadius = self.__curveChangeRadius(idx)
            self.Stack3.addWidget(curveChangeRadius)
            self.Stack3.setCurrentWidget(curveChangeRadius)
            self.Stack3.show()
            self.escapeCounter = 1
        elif self.Stack2.widget(idx).currentItem().text() == 'Изменить длину':
            curveChangeLengthWidget = self.__curveChangeLength(idx)
            self.Stack3.addWidget(curveChangeLengthWidget)
            self.Stack3.setCurrentWidget(curveChangeLengthWidget)
            self.Stack3.show()
            self.escapeCounter = 1
        elif self.Stack2.widget(idx).currentItem().text() == 'Сместить КК':
            interface = self.__curveShift(idx)
            self.Stack3.addWidget(interface)
            self.Stack3.setCurrentWidget(interface)
            self.Stack3.show()
            self.escapeCounter = 1

    # принудительно ставим на место границы последнего (текущего) изменённого диапазона саммари
    def set_coords_current_segment(self, previous_model: list, c: int):
        coord1 = self.startPicket + self.position_multiplyer * self.get_summary_row(previous_model, c).to_dict()[
            'start']
        coord2 = self.startPicket + self.position_multiplyer * self.get_summary_row(previous_model, c).to_dict()['end']
        self.vertical_model1.shiftLine(coord1)
        self.vertical_model2.shiftLine(coord2)

    # Получить строку из summary
    def get_summary_row(self, summary_file, row_index: int):
        row = summary_file[row_index]
        return row

    # Получить колонку из summary
    def get_summary_column(self, summary_file:list, column_name: str):
        column = []
        for every_dict in summary_file.elements():
            column.append(every_dict.to_dict()[column_name])
        return column

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Left:
                self.handle_left_button()
            elif event.key() == Qt.Key.Key_Right:
                self.handle_right_button()
            elif event.key() == Qt.Key.Key_Escape:
                self.Stack3.hide()
        return False

    # кнопка-стрелка 'влево'
    def handle_left_button(self):
        self.Stack3.hide()
        column_start = self.get_summary_column(self.summary, "start")
        column_end = self.get_summary_column(self.summary, "end")
        if 0 < self.counter < self.summary_len:
            self.updatedCounterSignal.emit(-1)
            self.counter -= 1
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter('to left', column_start, column_end)
            self.lineMover2.eventFilter('to left', column_start, column_end)
            if self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'переходная кривая':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Переходная кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'круговая кривая':
                self.groupbox1.setTitle("Вертикальная кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Круговая кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'прямая':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Прямая"))

    # кнопка-стрелка 'вправо'
    def handle_right_button(self):
        self.Stack3.hide()
        column_start = self.get_summary_column(self.summary, "start")
        column_end = self.get_summary_column(self.summary, "end")
        if 0 <= self.counter < (self.summary_len - 1):
            self.updatedCounterSignal.emit(1)
            self.counter += 1
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter('to right', column_start, column_end)
            self.lineMover2.eventFilter('to right', column_start, column_end)                                                         # ?
            if self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'переходная кривая':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Переходная кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'круговая кривая': #'curve':
                self.groupbox1.setTitle("Вертикальная кривая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Круговая кривая"))
            elif self.get_summary_row(self.summary.elements(), self.counter).to_dict()['geom'] == 'прямая': #'straight':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet(self.set_groupbox_title_style("Прямая"))

    # стиль заголовка левого нижнего групбокса
    def set_groupbox_title_style(self, segment_type: str):
        segment_type_style = {
            "Круговая кривая": "QGroupBox{font-size:18px; font-weight:bold;} QGroupBox:title{color:red; margin-top: -5px; margin-left: 30px}",
            "Переходная кривая": "QGroupBox{font-size:18px; font-weight:bold;} QGroupBox:title{color:green;}",
            "Прямая": "QGroupBox{font-size:18px; font-weight:bold;} QGroupBox:title{color:black;}"}
        return segment_type_style[segment_type]


    #==============================    Функции переустройства    ============================================================
    # Здесь только меняют текстовые метки и значения в таблицах. Вся перерисовка графиков в ProfileMain.py

    # ____________________________________________________ Круговая ________________________________
    #                                             Изменить радиус
    # создать интерфейс
    def __curveChangeRadius(self, idx):
        groupboxCurveChangeRadius = QGroupBox()
        groupboxCurveChangeRadiusLayout = QVBoxLayout()
        groupboxCurveChangeRadiusLayout_1 = QHBoxLayout()
        groupboxCurveChangeRadiusLayout_2 = QHBoxLayout()
        groupboxCurveChangeRadiusLayout.addLayout(groupboxCurveChangeRadiusLayout_1)
        groupboxCurveChangeRadiusLayout.addLayout(groupboxCurveChangeRadiusLayout_2)
        groupboxCurveChangeRadius.setLayout(groupboxCurveChangeRadiusLayout)
        self.curveChangeRadiusSpinBox.setRange(-1000000, 1000000)
        self.btn_curve_change_radius.clicked.connect(self.__handleCurveChangeRadiusSpinBox)
        self.currentRadius = QLabel(str('%.2f' % self.get_summary_row(self.summary.elements(), idx).to_dict()['radius_fact']))
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
        groupboxCurveChangeRadiusLayout_1.addStretch(1)
        groupboxCurveChangeRadiusLayout_1.addWidget(self.btn_curve_change_radius)
        groupboxCurveChangeRadiusLayout_2.addWidget(title_label)
        groupboxCurveChangeRadiusLayout_2.addWidget(self.currentRadius)
        groupboxCurveChangeRadiusLayout_2.addStretch(1)
        return groupboxCurveChangeRadius

    def __handleCurveChangeRadiusSpinBox(self):
        updatedRadius = self.curveChangeRadiusSpinBox.value()
        self.currentRadius.setText(str(updatedRadius))  # меняем метку в интерфейсе
        #self.models_list[self.counter].setData(self.models_list[self.counter].index(0, 1), updatedRadius, Qt.EditRole)
        #self.models_list[self.counter].dataChanged.connect(self.tables_list[self.counter].update(self.models_list[self.counter].index(0, 1)))
        self.curveChangeRadiusSpinBox.clear()

    #                                        Изменить длину (обе верт. черты синхронно сдвигаются\раздвигаются)
    # создать интерфейс
    def __curveChangeLength(self, idx):
        groupboxCurveShift = QGroupBox()
        сurveVShiftLayout = QVBoxLayout()
        groupboxCurveShift.setLayout(сurveVShiftLayout)
        length = round((self.get_summary_row(self.summary.elements(), idx).to_dict()['end']) - (self.get_summary_row(self.summary.elements(), idx).to_dict()['start']))
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
        self.coordVerticaleLine1 = QLabel(str(round(self.startPicket +  self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['start'])))
        self.coordVerticaleLine1.setStyleSheet("font: bold 16px;")
        self.coordVerticaleLine2 = QLabel(str(round(self.startPicket +  self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['end'])))
        self.coordVerticaleLine2.setStyleSheet("font: bold 16px;")
        self.curveChangeLengthValue = QLabel(str(length))
        self.curveChangeLengthValue.setStyleSheet("font: bold 16px;")
        сurveH1ShiftLayout = QHBoxLayout()
        сurveH2ShiftLayout = QHBoxLayout()
        сurveH1ShiftLayout.addStretch(1)
        сurveH1ShiftLayout.addWidget(how_many_change_label)
        сurveH1ShiftLayout.addWidget(self.spinBoxСurveChangeLength)
        сurveH1ShiftLayout.addWidget(m_change_label)
        сurveH1ShiftLayout.addStretch(1)
        сurveH1ShiftLayout.addWidget(self.btn_curve_change_length)
        сurveH1ShiftLayout.addStretch(1)
        сurveH2ShiftLayout.addStretch(1)
        сurveH2ShiftLayout.addWidget(titleCoordVerticaleLine1)
        сurveH2ShiftLayout.addWidget(self.coordVerticaleLine1)
        сurveH2ShiftLayout.addStretch(1)
        сurveH2ShiftLayout.addWidget(titleLength)
        сurveH2ShiftLayout.addWidget(self.curveChangeLengthValue)
        сurveH2ShiftLayout.addStretch(1)
        сurveH2ShiftLayout.addWidget(titleCoordVerticaleLine2)
        сurveH2ShiftLayout.addWidget(self.coordVerticaleLine2)
        сurveH2ShiftLayout.addStretch(1)
        сurveVShiftLayout.addLayout(сurveH1ShiftLayout)
        сurveVShiftLayout.addLayout(сurveH2ShiftLayout)
        return groupboxCurveShift

    def __handleSpinboxCurveChangeLength(self, value):
        res1 = round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), self.counter).to_dict()['start'] - self.position_multiplyer * value/2)
        res2 = round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), self.counter).to_dict()['end'] + self.position_multiplyer * value/2)
        self.vertical_model1.shiftLine(res1)
        self.vertical_model2.shiftLine(res2)
        result = math.fabs(res2 - res1)
        self.curveChangeLengthValue.setNum(result)
        self.coordVerticaleLine1.setText(str(res1))
        self.coordVerticaleLine2.setText(str(res2))
        # меняем значение в таблице
        #self.models_list[self.counter].setData(self.models_list[self.counter].index(1, 1), round(result, 1), Qt.EditRole)
        #self.models_list[self.counter].dataChanged.connect(self.tables_list[self.counter].update(self.models_list[self.counter].index(1, 1)))


    #                                            Сместить   (обе верт. черты синхронно идут в одну сторону)
    # создать виджет (интерфейс)
    def __curveShift(self, idx):
        groupboxCurveShift = QGroupBox()
        vbox = QVBoxLayout()
        hbox_1 = QHBoxLayout()
        hbox_2 = QHBoxLayout()
        vbox.addLayout(hbox_1)
        vbox.addLayout(hbox_2)
        curveShiftLayout = QHBoxLayout()
        groupboxCurveShift.setLayout(vbox)
        titleCoordVerticaleLine1 = QLabel("Левая граница")
        titleCoordVerticaleLine1.setStyleSheet("font-size: 18px;")
        titleCoordVerticaleLine2 = QLabel("Правая граница")
        titleCoordVerticaleLine2.setStyleSheet("font-size: 18px;")
        self.coordVerticaleLine1 = QLabel(
                str(round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['start'])))
        self.coordVerticaleLine1.setStyleSheet("font: bold 18px;")
        self.coordVerticaleLine2 = QLabel(
                str(round(self.startPicket + self.position_multiplyer * self.get_summary_row(self.summary.elements(), idx).to_dict()['end'])))
        self.coordVerticaleLine2.setStyleSheet("font: bold 18px;")
        title_label = QLabel("Смещение на ")
        title_label.setStyleSheet("font: 18px;")
        hbox_1.addWidget(title_label)
        hbox_1.addWidget(self.spinBoxCurveShift)
        hbox_1.addWidget(self.btn_curve_shift)
        curveShiftLayout.addStretch(1)
        hbox_2.addWidget(titleCoordVerticaleLine1)
        hbox_2.addWidget(self.coordVerticaleLine1)
        curveShiftLayout.addStretch(1)
        hbox_2.addWidget(titleCoordVerticaleLine2)
        hbox_2.addWidget(self.coordVerticaleLine2)
        return groupboxCurveShift

    def __handleChangeCurveShift(self, value):
        res1 = round(self.startPicket + self.position_multiplyer * (self.get_summary_row(self.summary.elements(), self.counter).to_dict()['start'] + value))
        res2 = round(self.startPicket + self.position_multiplyer * (self.get_summary_row(self.summary.elements(), self.counter).to_dict()['end'] + value))
        self.vertical_model1.shiftLine(res1)
        self.vertical_model2.shiftLine(res2)
        self.coordVerticaleLine1.setText(str(res1))
        self.coordVerticaleLine2.setText(str(res2))

 ###################################################################################3
    def __okReconstruction(self):
        self.okReconstructionSignal.emit("ok")

    def __cancelReconstruction(self):
        self.Stack3.hide()
        self.cancelReconstructionSignal.emit("cancel")

 ####################################################################################

    # размещение кнопок-стрелок в заголовке groupbpx'a
    def resizeEvent(self, event):
        w = self.groupbox1.size().width()
        x = (w - 250) / 2
        self.button_to_left.move(x, -1)
        x = (w - 182) / 2 + 220
        self.button_to_right.move(x, -1)
