from PySide6.QtWidgets import QWidget,  QVBoxLayout, QApplication,QGroupBox, QHBoxLayout, QGridLayout, QLabel
from PySide6.QtGui import Qt, QPen, QPainter, QColor, QBrush, QKeySequence
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from domain.dto.Travelling import PicketDirection, LocationVector1D
from .VerticalLine import VerticalLineModel  
from .HorizontalLine import HorizontalLineModel
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond


class ShiftsMainWidget(QWidget):
    closePlanShiftsSignal = Signal(str)
    def __init__(self, state: ProgramTaskCalculationSuccessState, position: int):
        super().__init__()
        self.__state = state
        self.position = position
        self.options: ProgramTaskCalculationResultDto = self.__state.calculation_result().options
        programTaskModel: AbstractPositionedTableModel = self.__state.program_task()
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,
                                                                     self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        self.startPicket = self.__state.calculation_result().options.start_picket.meters
        position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        position_min: float = position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        position_max: float = position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        # #=============================================== Charts ===================================================
        program_task_charts_column_names: List[str] = [
            ['plan_fact', 'plan_prj'],
            ['plan_delta']
        ]
        charts_vbox = QVBoxLayout()
        for column_name in program_task_charts_column_names:
            if column_name == ['plan_fact', 'plan_prj']:
                chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
                chart_value_range = (
                    min(chart_value_range0[0], chart_value_range1[0]),
                    max(chart_value_range0[1], chart_value_range1[1]))
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
                chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
                self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
                self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
                self.series1.setPen(QPen(QColor("red"), 2))
                self.chart = HorizontalChart((position_min, position_max),
                                                self.options.picket_direction == PicketDirection.Backward,
                                                (chart_value_min, chart_value_max), False,
                                                series0=[self.series0], series1=[self.series1],
                                                x_tick=100, #y_tick=20,
                                                title="Сдвиги, мм", xMinorTickCount=9,
                                                xGridLineColor="gray", yGridLineColor="gray",
                                                xMinorGridLineColor="gray", yMinorGridLineColor="gray")

            else:
                chart_value_range: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
                chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
                self.series = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                QCoreApplication.translate(
                                                    'Lining trip/process/view/charts/program task', column_name[0]))
                self.chart = HorizontalChart((position_min, position_max),
                                         self.options.picket_direction == PicketDirection.Backward,
                                         (chart_value_min, chart_value_max), False,series0=[self.series],
                                         x_tick=100, #y_tick=20,
                                         title="Стрелы изгиба, мм", xMinorTickCount=9,
                                         xGridLineColor="gray", yGridLineColor="gray",
                                         xMinorGridLineColor="gray", yMinorGridLineColor="gray")
                # центральная
                self.vertical_model_center = VerticalLineModel(self.position)
                self.vertical_line_series1 = QLineSeries()
                self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.cyan, 4))
                # левая
                # self.vertical_model_left = VerticalLineModel(self.position - 1)
                self.vertical_line_series2 = QLineSeries()
                self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))
                # # правая
                # self.vertical_model_right = VerticalLineModel(self.position + 1)
                self.vertical_line_series3 = QLineSeries()
                self.vertical_line_series3.setPen(QPen(Qt.GlobalColor.magenta, 2))
                # горизонтальная
                self.left_vertical_line_flag = False
                self.right_vertical_line_flag = False
                #
                self.horizontal_line_series = QLineSeries()
                self.horizontal_line_series.setPen(QPen(Qt.GlobalColor.magenta, 2))  # горизонтальная
                #
                # центральная
                self.lineMapper1 = QVXYModelMapper(self)
                self.lineMapper1.setXColumn(0)
                self.lineMapper1.setYColumn(1)
                self.lineMapper1.setSeries(self.vertical_line_series1)
                self.lineMapper1.setModel(self.vertical_model_center)                             # !
                # левая
                self.lineMapper2 = QVXYModelMapper(self)
                self.lineMapper2.setXColumn(0)
                self.lineMapper2.setYColumn(1)
                self.lineMapper2.setSeries(self.vertical_line_series2)
                #self.lineMapper2.setModel(self.vertical_model_left)
                # правая
                self.lineMapper3 = QVXYModelMapper(self)
                self.lineMapper3.setXColumn(0)
                self.lineMapper3.setYColumn(1)
                self.lineMapper3.setSeries(self.vertical_line_series3)
                #self.lineMapper3.setModel(self.vertical_model_right)
                # горизонтальная
                self.lineMapper4 = QVXYModelMapper(self)
                self.lineMapper4.setXColumn(1)
                self.lineMapper4.setYColumn(0)
                #self.lineMapper4.setSeries(self.horizontal_line_series)
                #
                self.chart.addSeries(self.vertical_line_series1)
                self.chart.addSeries(self.vertical_line_series2)
                self.chart.addSeries(self.vertical_line_series3)
                self.chart.addSeries(self.horizontal_line_series)
                self.vertical_line_series1.attachAxis(self.chart.axisX())
                self.vertical_line_series1.attachAxis(self.chart.axisY())
                self.vertical_line_series2.attachAxis(self.chart.axisX())
                self.vertical_line_series2.attachAxis(self.chart.axisY())
                self.vertical_line_series3.attachAxis(self.chart.axisX())
                self.vertical_line_series3.attachAxis(self.chart.axisY())
                self.horizontal_line_series.attachAxis(self.chart.axisX())
                self.horizontal_line_series.attachAxis(self.chart.axisY())

            self.installEventFilter(self)
            self.chart.legend().hide()
            self.chart.layout().setContentsMargins(0, 0, 0, 0)
            self.chart.setMargins(QMargins(0, 0, 0, 0))
            self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
            self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
            chart_view = QChartView(self.chart)
            chart_view.chart().setBackgroundBrush(QBrush("black"))
            chart_view.setRenderHint(QPainter.Antialiasing)
            if column_name == ['plan_fact', 'plan_prj']:
                charts_vbox.addWidget(chart_view, 2)
            else:
                charts_vbox.addWidget(chart_view, 1)

        self.rugby_gate = False

        grid = QGridLayout()
        infopanel_first = InfopanelFirst(self.__state)
        infopanel_second = InfopanelSecond(self.__state)
        grid.addWidget(infopanel_first, 0, 0, 1, 10)
        grid.addWidget(infopanel_second, 1, 0, 1, 10)
        grid.addLayout(charts_vbox, 2, 0, 8, 9)
        rcw = self.__rightColumnWidget()
        right_vbox = QVBoxLayout()
        right_vbox.addStretch(5)
        right_vbox.addLayout(rcw)
        grid.addLayout(right_vbox, 2, 9, 1, 1)
        bottom = self.__bottomWidget()
        grid.addLayout(bottom, 10, 0, 1, 10)
        self.setWindowTitle("Расчёт.План.Сдвиги")
        self.setLayout(grid)
        self.showMaximized()
        self.setFocus()

    def __bottomWidget(self):
        grid = QGridLayout()
        label1 = QLabel("Сумма сдвигов")
        label2 = QLabel("Сумма модулей сдвигов")
        label3 = QLabel("Максимальный сдвиг влево")
        label4 = QLabel("Максимальный сдвиг вправо")
        label_mm1 = QLabel("mm")
        label_mm2 = QLabel("mm")
        label_mm3 = QLabel("mm")
        label_mm4 = QLabel("mm")
        label_value1 = QLabel()
        label_value2 = QLabel()
        label_value3 = QLabel()
        label_value4 = QLabel()
        value_style = "font: bold; font-size: 13pt;color:red;background-color:white"
        label_style = "font: bold; font-size: 13pt;color:red;"
        mm_style = "font: bold; font-size: 11pt;color:black;"
        for i in (label_value1,label_value2,label_value3,label_value4):
            i.setStyleSheet(value_style)
        for i in (label1, label2, label3, label4):
            i.setStyleSheet(label_style)
        for i in (label_mm1,label_mm2,label_mm3,label_mm4):
            i.setStyleSheet(mm_style)
        grid.addWidget(label1, 0, 0)
        grid.addWidget(label_value1, 0, 1)
        grid.addWidget(label_mm1, 0, 2)
        grid.addWidget(label2, 1, 0)
        grid.addWidget(label_value2, 1, 1)
        grid.addWidget(label_mm2, 1, 2)
        grid.addWidget(label3, 0, 3)
        grid.addWidget(label_value3, 0, 4)
        grid.addWidget(label_mm3, 0, 5)
        grid.addWidget(label4, 1, 3)
        grid.addWidget(label_value4, 1, 4)
        grid.addWidget(label_mm4, 1, 5)
        return grid
        #self.setMaximumHeight(80)
        #self.setLayout(grid)

    def __rightColumnWidget(self):
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        value_style = "font: bold; font-size: 12pt;color:white;background-color:black"
        point_number_label = QLabel("№ точки")
        point_number_label.setStyleSheet("font: bold; font-size: 12pt;color:black")
        self.point_number_label_value = QLabel(str(self.position))
        self.point_number_label_value.setStyleSheet(value_style)
        hbox1.addWidget(point_number_label)
        hbox1.addWidget(self.point_number_label_value)
        groupbox = QGroupBox()
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)
        groupbox_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Натура")
        fact_label.setStyleSheet("font: bold; font-size: 12pt;color:green")
        self.fact_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['plan_fact'][self.position]))
        self.fact_label_value.setStyleSheet(value_style)
        groupbox_layout_hbox1.addWidget(fact_label)
        groupbox_layout_hbox1.addWidget(self.fact_label_value)
        groupbox_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.prj_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['plan_prj'][self.position]))
        self.prj_label_value.setStyleSheet(value_style)
        groupbox_layout_hbox2.addWidget(prj_label)
        groupbox_layout_hbox2.addWidget(self.prj_label_value)
        groupbox_layout.addLayout(groupbox_layout_hbox1)
        groupbox_layout.addLayout(groupbox_layout_hbox2)
        shifts_label = QLabel("Сдвиги")
        shifts_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.shifts_label_value = QLabel(str(self.__state.calculation_result().calculated_task.data['plan_delta'][self.position]))
        self.shifts_label_value.setStyleSheet(value_style)
        hbox2.addWidget(shifts_label)
        hbox2.addWidget(self.shifts_label_value)
        self.setStyleSheet("background-color:white")
        vbox.addLayout(hbox1)
        vbox.addWidget(groupbox)
        vbox.addLayout(hbox2)
        return vbox

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            self.setFocus()
            if event.key() == Qt.Key.Key_Left:
                self.vertical_model_center.shiftLine(-1)
                self.point_number_label_value.setNum(self.position)
                self.fact_label_value.setNum(
                    self.__state.calculation_result().calculated_task.data['plan_fact'][self.position])
                self.prj_label_value.setNum(
                    self.__state.calculation_result().calculated_task.data['plan_prj'][self.position])
                self.shifts_label_value.setNum(
                    self.__state.calculation_result().calculated_task.data['plan_delta'][self.position])
                self.position += 1
                return True
            elif event.key() == Qt.Key.Key_Right:
                self.vertical_model_center.shiftLine(1)
                self.point_number_label_value.setNum(self.position)
                self.fact_label_value.setNum(
                    self.__state.calculation_result().calculated_task.data['plan_fact'][self.position])
                self.prj_label_value.setNum(
                    self.__state.calculation_result().calculated_task.data['plan_prj'][self.position])
                self.shifts_label_value.setNum(
                    self.__state.calculation_result().calculated_task.data['plan_delta'][self.position])
                self.position -= 1
                return True
            # построили по бокам ещё 2 вертикальные линиим
            elif event.key() == Qt.Key.Key_A:
                #if self.left_vertical_line_flag == False and not self.right_vertical_line_flag == False:
                self.horizontal_model = HorizontalLineModel(20, self.position - 10, self.position + 10)
                self.lineMapper4.setModel(self.horizontal_model)
                self.vertical_model_left = VerticalLineModel(self.position - 10)
                self.vertical_model_right = VerticalLineModel(self.position + 10)
                self.lineMapper2.setModel(self.vertical_model_left)
                self.lineMapper3.setModel(self.vertical_model_right)
                self.left_vertical_line_flag = True
                self.right_vertical_line_flag = True
                #else:
                #    print("self.left_vertical_line_flag != False and not self.right_vertical_line_flag != False")
                return True
            elif event.key() == Qt.Key.Key_S:
                if self.left_vertical_line_flag and self.right_vertical_line_flag:
                    self.horizontal_model = HorizontalLineModel(20, self.position - 10, self.position + 10)
                    self.lineMapper4.setModel(self.horizontal_model)
                return True
            elif event.key() == Qt.Key.Key_Z:
                if self.left_vertical_line_flag and self.right_vertical_line_flag:
                    self.horizontal_model.shiftLine(-1)
                return True
            elif event.key() == Qt.Key.Key_X:
                if self.left_vertical_line_flag and self.right_vertical_line_flag:
                    self.horizontal_model.shiftLine(1)
                return True
            elif event.key() == Qt.Key.Key_Escape:
                self.closePlanShiftsSignal.emit("close")
        return False


#                 return True
#             elif event.key() == Qt.Key.Key_S:   #QKeySequence("Ctrl+D"):  #Qt.Key.Key_Control | Qt.Key.Key_D):
#                 self.vertical_model_left = VerticalLineModel(self.position - 10)
#                 self.lineMapper2.setModel(self.vertical_model_left)
#                 self.left_vertical_line_flag = True
#                 #self.vertical_model_left.shiftLine(-1)
#                 #self.position -= 1
#                 #self.position -= 1
#                 return True
#             elif event.key() == Qt.Key.Key_D:   #QKeySequence("Ctrl+Left"):      #Qt.Key.Key_Control | Qt.Key.Key_X):
#                 self.vertical_model_right = VerticalLineModel(self.position + 10)
#                 self.lineMapper3.setModel(self.vertical_model_right)
#                 self.right_vertical_line_flag = True
#                 #self.vertical_model_right.shiftLine(1)
#                 #self.position += 1
#                 return True
#             elif event.key() == Qt.Key.Key_Return and self.right_vertical_line_flag and self.left_vertical_line_flag:
#                 #self.horizontal_model = HorizontalLineModel(10, self.position - 10, self.position + 10)
#                 #self.lineMapper4.setModel(self.horizontal_model)
#                 print("___enter___", self.position)
            #     #self.shift_to_lower = self.vertical_model1.currentX()                  # !
            #     self.run_reconstruction(self.vertical_model1.currentX())
            #     return True
            # # Двигаем горизонтальную черту
            # elif event.key() == Qt.Key.Key_S:                      # ПЕРЕДЕЛАТЬ В СТРЕЛКУ
            #     self.horizontal_model.shiftLine(-1)
            #     return True
            # # ЗАКРЫТИЕ ЦИКЛА
            # elif event.key() == Qt.Key.Key_Escape:
            #     self.stop_reconstruction()
            #     return True
            # # ОТМЕНА ПОСЛЕДНЕГО ДЕЙСТВИЯ
            # elif event.key() == QKeySequence(Qt.Key.Key_Backspace):  #, Qt.Key.Key_Control):   # Key_Back
            #     return True
        #return False


    # # запускается по enter
    #def run_reconstruction(self, current_x_point):pass
    #     self.vertical_line_series1.hide()
    #     if self.rugby_gate == False:                        # первое использование
    #         print(1, current_x_point)
    #         #self.lineMapper2.setSeries(self.vertical_line_series2)
    #         self.vertical_model2 = VerticalLineModel2(self.vertical_model1.currentX() - 100)
    #         self.lineMapper2.setModel(self.vertical_model2)
    #         #self.lineMapper3.setSeries(self.vertical_line_series3)
    #         self.vertical_model3 = VerticalLineModel2(self.vertical_model1.currentX() + 100)
    #         self.lineMapper3.setModel(self.vertical_model3)
    #         #self.current_x_point = self.vertical_model1.currentX()
    #         #self.lineMapper4.setSeries(self.horizontal_line_series)
    #         self.y_range = get_csv_column_range(FILENAME, self.chart_column_name,
    #                                             round(current_x_point - 100), round(current_x_point + 100))
    #         self.horizontal_model = HorizontalLineModel(max(self.y_range), current_x_point - 100,
    #                                                     current_x_point + 100)
    #         self.lineMapper4.setModel(self.horizontal_model)
    #         self.rugby_gate = True
    #     else:
    #         print(2, current_x_point)
    #         self.vertical_line_series2.show()
    #         self.vertical_line_series3.show()
    #         self.horizontal_line_series.show()
    #
    #

    # запускается по esc
    #def stop_reconstruction(self):pass
    #     self.vertical_line_series1.show()
    #     self.vertical_line_series2.hide()
    #     self.vertical_line_series3.hide()
    #     self.horizontal_line_series.hide()

