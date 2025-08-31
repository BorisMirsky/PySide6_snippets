
from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QApplication,QPushButton,QSpinBox,QStackedLayout,
                               QHBoxLayout, QGridLayout, QLabel, QFileDialog,QMessageBox, QGroupBox)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.calculations.plan_model import TrackPlanProjectModel, TrackElementGeometry
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent, LabelOnParent2
from .VerticalLine import VerticalLineModel




class ProfileLiftingWidget(QWidget):
    quitProfileLifting = Signal(str)
    #openProfileParametersSignal = Signal(int)
    #openPlanShiftsSignal = Signal(int)
    def __init__(self, state: ProgramTaskCalculationSuccessState,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
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
        self.counter = 0
       # self.summary = TrackPlanProjectModel(self.__state.calculation_result().base.track_split,
       #                                      self.__state.calculation_result().base.plan)
      #  self.summary_len = len(self.summary.elements())
        self.startPicket = self.__state.calculation_result().options.start_picket.meters
        self.currentPosition = self.options.start_picket.meters
        self.model = VerticalLineModel(self.options.start_picket.meters)
        #                                      self.__state.calculation_result().base.track_split_plan
        self.plan_model = TrackPlanProjectModel(self.__state.calculation_result().base.track_split_plan,
                                                self.__state.calculation_result().base.plan)
        self.model1 = VerticalLineModel(self.options.start_picket.meters)
        self.model2 = VerticalLineModel(self.options.start_picket.meters + self.plan_model.elements()[0].to_dict()['end'])
        #
        grid = QGridLayout()
        infopanel_first = InfopanelFirst(self.__state)
        infopanel_second = InfopanelSecond(self.__state)
        grid.addWidget(infopanel_first, 0, 0, 1, 10)
        grid.addWidget(infopanel_second, 1, 0, 1, 10)

        # #=============================================== Charts ===================================================
        self.program_task_charts_column_names: List[str] = [
            ['prof_fact', 'prof_prj'],
            ['prof_delta']
        ]
        charts_vbox = QVBoxLayout()
        for column_name in self.program_task_charts_column_names:
            if column_name == ['prof_fact', 'prof_prj']:
                chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
                #chart_value_range2: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[2])
                chart_value_range = (
                    min(chart_value_range0[0], chart_value_range1[0]), #chart_value_range2[0]),
                    max(chart_value_range0[1], chart_value_range1[1])) #chart_value_range2[1]))
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
                # self.series2 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                #                                  self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                #                                  QCoreApplication.translate(
                #                                      'Lining trip/process/view/charts/program task', column_name[2]))
                self.series0.setPen(QPen(QColor("cyan"), 2))
                self.series1.setPen(QPen(QColor("red"), 2))
                #self.series2.setPen(QPen(QColor("red"), 2))
                vertical_chart_title = "Вертикальные стрелы изгиба, мм"
                self.chart = HorizontalChart((position_min, position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0], series1=[self.series1],   #series2=[self.series2],
                                        x_tick=100, y_tick=20, title=vertical_chart_title,
                                        xMinorTickCount=9, yMinorTickCount=1,
                                        xGridLineColor="gray", yGridLineColor="gray", #XAxisHideLabels=False,
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
            else:
                chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
                #chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
                chart_value_range = (
                    min(chart_value_range0[0], chart_value_range0[1]),
                    max(chart_value_range0[0], chart_value_range0[1]))
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
                chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
                self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                QCoreApplication.translate(
                                                    'Lining trip/process/view/charts/program task', column_name[0]))
                # self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                #                                 self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                #                                 QCoreApplication.translate(
                #                                     'Lining trip/process/view/charts/program task', column_name[1]))
                self.series0.setPen(QPen(QColor("green"), 2))
                #self.series1.setPen(QPen(QColor("blue"), 2))
                vertical_chart_title = 'Подъёмки, мм'
                self.chart = HorizontalChart((position_min, position_max),
                                        self.options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0], #series1=[self.series1],
                                        x_tick=100, y_tick=20, title=vertical_chart_title,
                                        xMinorTickCount=9, yMinorTickCount=1,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
                                        #XAxisHideLabels=False)
                #

            self.chart.legend().hide()
            self.chart.layout().setContentsMargins(0, 0, 0, 0)
            self.chart.setMargins(QMargins(0, 0, 0, 0))
            self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
            self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
            self.chart_view = QChartView(self.chart)
            #self.chart_view.setFocusPolicy(Qt.NoFocus)
            self.chart_view.chart().setBackgroundBrush(QBrush("black"))
            self.chart_view.setRenderHint(QPainter.Antialiasing)
            #
            self.vertical_line_series = QLineSeries()
            self.vertical_line_series.setPen(QPen(Qt.GlobalColor.magenta, 2))
            self.lineMapper = QVXYModelMapper(self)
            self.lineMapper.setXColumn(0)
            self.lineMapper.setYColumn(1)
            self.lineMapper.setSeries(self.vertical_line_series)
            self.lineMapper.setModel(self.model)
            self.chart.addSeries(self.vertical_line_series)
            self.vertical_line_series.attachAxis(self.chart.axisX())
            self.vertical_line_series.attachAxis(self.chart.axisY())
            #
            if column_name == ['prof_fact', 'prof_prj']:
                charts_vbox.addWidget(self.chart_view, 2)
            else:
                charts_vbox.addWidget(self.chart_view, 1)
        #
        self.installEventFilter(self)
        #=================================================================================
        grid.addLayout(charts_vbox, 2, 0, 8, 9)
        rcw = self.__rightColumnWidget()
        grid.addLayout(rcw, 2, 9, 8, 1)
        #
        # title_window = LabelOnParent2('Профиль. Главная страница', 500, 0, 250, 40, self.infopanel_first)
        # title_window.setWordWrap(True)
        # title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        #
        self.setWindowTitle("Перерасчёт.Уровень")
        self.setLayout(grid)
        #self.showMaximized()
        self.setFocus()

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            self.setFocus()
            if event.key() == Qt.Key.Key_Left:
                self.model.shiftLine(-1)
                #print('Key_Left')
                #self.__returnData(-1)
                return True
            elif event.key() == Qt.Key.Key_Right:
                self.model.shiftLine(1)
                #print('Key_Right')
                #self.__returnData(1)
                return True
        return False

    # установка значений в окна
    # def __returnData(self, i:int):
    #     self.currentPosition += i
    #     self.point_number_label_value.setNum(self.currentPosition)
    #     self.fact_label_value.setNum(self.__state.calculation_result().calculated_task.data['vozv_fact'][self.currentPosition])
    #     self.prj_label_value.setNum(self.__state.calculation_result().calculated_task.data['vozv_prj'][self.currentPosition])
    #     self.anep_label_value.setNum(self.__state.calculation_result().calculated_task.data['a_nepog_fact'][self.currentPosition])
    #     self.psi_label_value.setNum(self.__state.calculation_result().calculated_task.data['psi_fact'][self.currentPosition])
    #     self.fv_label_value.setNum(self.__state.calculation_result().calculated_task.data['v_wheel_fact'][self.options.start_picket.meters])

    def __rightColumnWidget(self):
        vbox = QVBoxLayout()
        #
        vbox_ok = QVBoxLayout()
        ok_btn = QPushButton("Ok")
        ok_btn.clicked.connect(self.__okChange)
        ok_lbl = QLabel(" %s \n %s \n %s" % ('Принять', 'все изменения', 'и уйти со страницы'), self)
        vbox_ok.addWidget(ok_lbl)
        vbox_ok.addWidget(ok_btn)
        vbox_cancel = QVBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.__okChange)
        cancel_lbl = QLabel(" %s \n %s \n %s" % ('Отказаться от', 'всех изменений', 'и уйти со страницы'), self)
        vbox_cancel.addWidget(cancel_lbl)
        vbox_cancel.addWidget(cancel_btn)
        #
        # groupbox_top = QGroupBox()
        # groupbox_vlayout = QVBoxLayout()
        # groupbox_top.setLayout(groupbox_vlayout)
        # groupbox_top.setTitle("Редактирование")
        # self.parameters_button = QPushButton("Параметры")
        # self.lifting_button = QPushButton("Подъёмки")
        # groupbox_vlayout.addWidget(self.parameters_button)
        # groupbox_vlayout.addWidget(self.lifting_button)
        # self.parameters_button.clicked.connect(self.__handleParametersButton)
        # self.lifting_button.clicked.connect(self.__handleLiftingButton)
        # self.results_button = QPushButton("Результаты")
        # self.settings_button = QPushButton("Установки")
        self.escape_button = QPushButton("Выход (ESC)")
        # self.results_button.clicked.connect(self.__results_button)
        # self.settings_button.clicked.connect(self.__settings_button)
        self.escape_button.clicked.connect(self.__escape_button)
        # self.buttons = []
        # self.buttons.append(self.parameters_button)
        # self.buttons.append(self.lifting_button)
        # self.buttons.append(self.results_button)
        # self.buttons.append(self.settings_button)
        # self.buttons.append(self.escape_button)
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

        ##########################################
        #vbox.addWidget(groupbox_top)
        vbox.addStretch(1)
        vbox.addLayout(vbox_ok)
        vbox.addLayout(vbox_cancel)
        #vbox.addStretch(1)
        #vbox.addWidget(self.settings_button)
        vbox.addStretch(5)
        vbox.addWidget(self.escape_button)
        vbox.addStretch(1)
        vbox.addLayout(vbox1)
        return vbox


    def __handleParametersButton(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")
        #self.reconstructionMain = LevelReconstructionWidget(self.model1, self.model2, self.__state)
        #self.reconstructionMain.show()

    def __handleLiftingButton(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")
        #model = VerticalLineModel(self.options.start_picket.meters)
        #self.speedMain = SpeedMainWidget(self.__state) #, model)
        #self.speedMain.show()


    def __okChange(self):
        pass


    def __okChange(self):
        pass

    def __results_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __settings_button(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
               btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet("")

    def __escape_button(self):
        # sender = self.sender()
        # for btn in self.buttons:
        #     if btn is sender:
        #         btn.setStyleSheet("background-color: blue")
        #     else:
        #         btn.setStyleSheet("")
        #print("__escape_button")
        self.quitProfileLifting.emit('close')

    # # Получить колонку from summary
    # def get_summary_column(self, summary_file:list, column_name: str):
    #     column = []
    #     for every_dict in summary_file.elements():
    #         column.append(every_dict.to_dict()[column_name])
    #     return column
