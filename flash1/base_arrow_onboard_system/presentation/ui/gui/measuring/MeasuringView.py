# This Python file uses the following encoding: utf-8
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.dto.Travelling import MovingDirection, PicketDirection, BaseRail, LocationVector1D, RailPressType
from domain.dto.Workflow import MeasuringTripOptionsDto, MeasuringTripResultDto
from domain.dto.Markers import RailwayMarker, RailwayMarkerType, RailwayMarkerLocation
from operating.states.measuring.ApplicationMeasuringState import MeasuringOptionsState, MeasuringProcessState, MeasuringSuccessState, MeasuringErrorState, MeasuringFinalState
from operating.states.measuring.ApplicationMeasuringState import ApplicationMeasuringState
from ..common.viewes.TableDataChartsView import DynamicLineSeries, VerticalChart, ChartSlidingWindowProvider, AbstractChartOrientationMixin
from ..common.viewes.LabelOnChart import LabelOnParent
from ..common.viewes.RailwayMarkerView import SelectCurrentMarkerWindow, RailwayMarkerLinesScatter
from ..common.elements.Travelling import CurrentPicketLabel, PassedMetersLabel, BaseRailLabel, PressRailLabel, MovingDirectionLabel, PicketDirectionLabel, RailwayInfoPanel
from ..common.elements.Time import CurrentTimeLabel, ElapsedTimeLabel
from ..common.elements.SingleLineModel import SingleLineModel
from ....models.PicketPositionUnit import PicketPositionUnit
from ....models.PicketPositionedTableModel import PicketPositionedTableModel
from ....models.TranslatedHeadersTableModel import TranslatedHeadersTableModel
from ....utils.store.workflow.zip.Dto import MeasuringTripResultDto_to_archive
from PySide6.QtWidgets import QStackedLayout, QWidget, QDoubleSpinBox, QLabel, QPushButton, QHeaderView, QTableView, QTabWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QMessageBox, QFileDialog, QComboBox, QLineEdit, QAbstractItemView
from PySide6.QtCharts import QChartView, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QAbstractTableModel
from PySide6.QtGui import QKeySequence, QShortcut, QImage, QIcon, QBrush, QPainter
from PySide6.QtStateMachine import QStateMachine
from typing import List, Optional
import zipfile
import pandas
import os


QCoreApplication.translate('Measurement/control units', 'strelograph_work')
QCoreApplication.translate('Measurement/control units', 'strelograph_control')
QCoreApplication.translate('Measurement/control units', 'pendulum_work')
QCoreApplication.translate('Measurement/control units', 'pendulum_control')
QCoreApplication.translate('Measurement/control units', 'pendulum_front')
QCoreApplication.translate('Measurement/control units', 'sagging_left')
QCoreApplication.translate('Measurement/control units', 'sagging_right')
QCoreApplication.translate('Measurement/control units', 'satellite')
QCoreApplication.translate('Measurement/control units', 'position')
QCoreApplication.translate('Measurement/control units', 'tick_counter')
QCoreApplication.translate('Measurement/control units', 'discrete_signals')
QCoreApplication.translate('Measurement/control units', 'left')
QCoreApplication.translate('Measurement/control units', 'middle')
QCoreApplication.translate('Measurement/control units', 'exit')
QCoreApplication.translate('Measurement/control units', 'quit')








#======================================================================
class MeasuringOptionsView(QWidget):
    def __init__(self, state: MeasuringOptionsState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.__state = state

        self.__startPicket = QDoubleSpinBox()
        self.__startPicket.setRange(0, 1000000000)

        self.__trackTitle = QLineEdit()
        self.__trackTitle.setPlaceholderText(QCoreApplication.translate('Measuring trip/options/view','Rail track name'))

        # self.__baseRail = QComboBox()
        # self.__baseRail.addItem(QCoreApplication.translate('Travelling/BaseRail', (BaseRail.Right.name)), BaseRail.Right)
        # self.__baseRail.addItem(QCoreApplication.translate('Travelling/BaseRail', (BaseRail.Left.name)), BaseRail.Left)
        # self.__baseRail.setCurrentText(QCoreApplication.translate('Travelling/BaseRail', (BaseRail.Left.name)))

        self.__pressRail = QComboBox()
        self.__pressRail.addItem(QCoreApplication.translate('Travelling/BaseRail', (RailPressType.Right.name)), RailPressType.Right)
        self.__pressRail.addItem(QCoreApplication.translate('Travelling/BaseRail', (RailPressType.Left.name)), RailPressType.Left)
        self.__pressRail.setCurrentText(QCoreApplication.translate('Travelling/BaseRail', (RailPressType.Left.name)))


        self.__picketDirection = QComboBox()
        self.__picketDirection.addItem(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Forward.name)), PicketDirection.Forward)
        self.__picketDirection.addItem(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Backward.name)), PicketDirection.Backward)
        self.__picketDirection.setCurrentText(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Forward.name)))

        self.__movingDirection = QComboBox()
        self.__movingDirection.addItem(QCoreApplication.translate('Travelling/MovingDirection', (MovingDirection.Forward.name)), MovingDirection.Forward)
        self.__movingDirection.addItem(QCoreApplication.translate('Travelling/MovingDirection', (MovingDirection.Backward.name)), MovingDirection.Backward)
        self.__movingDirection.setCurrentText(QCoreApplication.translate('Travelling/MovingDirection', (MovingDirection.Forward.name)))

        processButton = QPushButton(QCoreApplication.translate('Measuring trip/options/view', 'Process'))
        cancelButton = QPushButton("Выход")  #QCoreApplication.translate('Measuring trip/options/view', 'Exit'))
        processButton.clicked.connect(self.__tryStartMeasuring)
        cancelButton.clicked.connect(self.__state.cancel)
        processButton.setProperty("optionsWindowPushButton", True)
        cancelButton.setProperty("optionsWindowPushButton", True)

        self.setProperty("optionsWindowWidget", True)
        self.__startPicket.setProperty("optionsWindowDoubleSpinBox", True)
        self.__trackTitle.setProperty("optionsWindowLineEdit", True)
        # self.__baseRail.setProperty("optionsWindowComboBox", True)
        self.__pressRail.setProperty("optionsWindowComboBox", True)
        self.__picketDirection.setProperty("optionsWindowComboBox", True)
        self.__movingDirection.setProperty("optionsWindowComboBox", True)



        layout = QGridLayout()
        self.setLayout(layout)
        for column in range(8):
            layout.setColumnStretch(column, 1)

        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        #layout.addWidget(QLabel('application/measuring/options'), 0, 2, 1, 4)
        layout.addWidget(self.__trackTitle, 1, 2, 1, 4)

        layout.addWidget(QLabel(QCoreApplication.translate('UI/Common', 'Picket direction')), 2, 2, 1, 1)
        layout.addWidget(self.__picketDirection, 2, 3, 1, 3)
        layout.addWidget(QLabel(QCoreApplication.translate('UI/Common', 'Moving direction')), 3, 2, 1, 1)
        layout.addWidget(self.__movingDirection, 3, 3, 1, 3)
        layout.addWidget(QLabel(QCoreApplication.translate('UI/Common', 'Start picket')), 4, 2, 1, 1)
        layout.addWidget(self.__startPicket, 4, 3, 1, 3)
    
        layout.addWidget(QLabel('Прижим'), 5, 2, 1, 1)
        layout.addWidget(self.__pressRail, 5, 3, 1, 3)
        layout.addWidget(processButton, 6, 2, 1, 4)
        layout.addWidget(cancelButton, 7, 2, 1, 4)

    def __tryStartMeasuring(self) ->None:
        self.__state.start.emit(MeasuringTripOptionsDto(
            track_title = self.__trackTitle.text(),
            # base_rail = self.__baseRail.currentData(),
            press_rail = self.__pressRail.currentData(),
            start_picket = LocationVector1D(self.__startPicket.value()),
            picket_direction = self.__picketDirection.currentData(),
            moving_direction = self.__movingDirection.currentData()))

class MeasuringProcessView(QWidget):
    def __init__(self, state: MeasuringProcessState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.__state: MeasuringProcessState = state
        #===============================================
        options: MeasuringTripOptionsDto = self.__state.options()
        measurements_model: AbstractPositionedTableModel = self.__state.measurements()
        #print(measurements_model.modelColumns())
        self.__translation_measurements_model = TranslatedHeadersTableModel()
        self.__translation_measurements_model.setSourceModel(measurements_model)
        self.__picket_measurements_model = PicketPositionedTableModel(options.picket_direction, options.start_picket.meters, self)
        self.__picket_measurements_model.setSourceModel(self.__translation_measurements_model)
        #==============================================
        self.__meters_position_provider = self.__state.position_unit()
        self.__picket_position_model = PicketPositionUnit(self.__meters_position_provider, options.picket_direction, options.start_picket.meters)
        
        self.__position_unit_line_model = SingleLineModel(self.__picket_position_model.read() or 0)
        self.__picket_position_model.changed.connect(self.__position_unit_line_model.setPosition)
        #==============================================
        information_panel = QWidget()
        information_panel_layout = QGridLayout()
        information_panel.setLayout(information_panel_layout)
        information_panel.setProperty("topInfoPanel", True)
        information_panel_layout.addWidget(CurrentPicketLabel(self.__picket_position_model), 0, 0, 1, 2)
        information_panel_layout.addWidget(PassedMetersLabel(self.__meters_position_provider), 1, 0, 1, 1)
        information_panel_layout.addWidget(RailwayInfoPanel(options.track_title), 1, 1, 1, 1)
        information_panel_layout.addWidget(PicketDirectionLabel(options.picket_direction), 0, 2, 1, 1)
        information_panel_layout.addWidget(MovingDirectionLabel(options.moving_direction), 1, 2, 1, 1)
        # information_panel_layout.addWidget(BaseRailLabel(options.base_rail), 0, 3, 1, 1)
        information_panel_layout.addWidget(PressRailLabel(options.press_rail), 0, 3, 1, 1)
        
        information_panel_layout.addWidget(CurrentTimeLabel(), 0, 4, 1, 1)
        information_panel_layout.addWidget(ElapsedTimeLabel(), 1, 4, 1, 1)
        #==============================================


        #==============================================
        measurementsView = QTabWidget()
        measurementsView.setProperty("MeasurementsTabWidget", True)
        #
        meterMeasurementsView = QTableView()
        meterMeasurementsView.setFocusPolicy(Qt.NoFocus)
        meterMeasurementsView.setSelectionMode(QAbstractItemView.NoSelection)
        meterMeasurementsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        meterMeasurementsView.setProperty("measurementsTable", True)
        meterMeasurementsView.setModel(self.__translation_measurements_model)
        meterMeasurementsView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        meterMeasurementsView.verticalHeader().hide()
        #
        picketMeasurementsView = QTableView()
        picketMeasurementsView.setFocusPolicy(Qt.NoFocus)
        picketMeasurementsView.setSelectionMode(QAbstractItemView.NoSelection)
        picketMeasurementsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        picketMeasurementsView.setProperty("measurementsTable", True)
        picketMeasurementsView.setModel(self.__picket_measurements_model)
        picketMeasurementsView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        picketMeasurementsView.verticalHeader().hide()
        if __debug__:
            #measurementsView.addTab(meterMeasurementsView, QCoreApplication.translate('Measuring trip/process/view', 'Table'))
            measurementsView.addTab(picketMeasurementsView, QCoreApplication.translate('Measuring trip/process/view', 'Picket table'))
        #==============================================
        #
        self.measuringInProcessFlag = False
        # buttons
        cornerWidget = QWidget()
        cornerHbox = QHBoxLayout()
        cornerWidget.setLayout(cornerHbox)
        # Start button
        self.startMeausermentButton = QPushButton(
            QCoreApplication.translate('Measuring trip/process/view', 'Start measuring trip'))
        self.startMeausermentButton.clicked.connect(self.__onStartMeauserements)
        self.startMeausermentButton.setProperty("centerButton", True)
        # Finish button
        finishMeausermentButton = QPushButton(
            QCoreApplication.translate('Measuring trip/process/view', 'Finish measuring trip'))
        finishMeausermentButton.clicked.connect(self.__onFinishMeauserements)
        finishMeausermentButton.setProperty("centerButton", True)
        # infolabel about markers
        infoLabelMarkers = QLabel("Маркеры (F3)")    # "Markers (F3)"
        infoLabelMarkers.setProperty("measuringInfoLabel", True)
        cornerHbox.addWidget(infoLabelMarkers)
        cornerHbox.addWidget(self.startMeausermentButton)
        cornerHbox.addWidget(finishMeausermentButton)
        cornerHbox.setContentsMargins(0,0,0,0)
        measurementsView.setCornerWidget(cornerWidget)
        #==============================================
        chartView = QWidget()
        chartViewLayout = QHBoxLayout()
        chartView.setLayout(chartViewLayout)
        measurementsView.addTab(chartView, QCoreApplication.translate('Measuring trip/process/view', 'Charts'))
        # ==============================================

        marker_models_with_icons = []
        railway_marker_icons_conig: pandas.DataFrame = pandas.read_csv('./resources/configs/railway_marker_icons.csv', sep = ';', index_col = 'type')
        for type, (model, writer) in self.__state.marker_models().items():
            picket_positioned_marker_model = PicketPositionedTableModel(options.picket_direction, options.start_picket.meters, self)
            picket_positioned_marker_model.setSourceModel(model)
            marker_model_icon = QImage(railway_marker_icons_conig['icon'][type.name]).scaled(32, 32)
            marker_models_with_icons.append((picket_positioned_marker_model, marker_model_icon))

        marker_view = RailwayMarkerLinesScatter(self.__picket_position_model, 
            (10, 1) if options.picket_direction == PicketDirection.Forward else (1, 10), 
            marker_models_with_icons)
        chartViewLayout.addWidget(marker_view, 1)


        user_available_railway_markers = []
        user_available_railway_markers_confing: pandas.DataFrame = pandas.read_csv('./resources/configs/user_available_railway_markers.csv', sep = ';')
        for _, row in user_available_railway_markers_confing.iterrows():
            type: RailwayMarkerType = RailwayMarkerType[row['type']]
            location: RailwayMarkerLocation = RailwayMarkerLocation[row['location']]
            user_available_railway_markers.append((
                self.__state.marker_models()[type][0], 
                RailwayMarker(row['title'], type, location), 
                QIcon(row['icon']), row['is_continuation']))
        
        #platform_model = self.__state.marker_models()[RailwayMarkerType.Platform][0]
        self.__select_marker_window = SelectCurrentMarkerWindow(position_unit = self.__meters_position_provider, 
            marker_step = 0.5, railway_markers = user_available_railway_markers)
            
        self.__open_select_maker_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F3), self)
        self.__open_select_maker_shortcut.activated.connect(self.__show_input_railway_marker_window)

        # ==============================================
        #config = self.__state.config()
        measurement_charts_column_names: List[List[str]] = [
            ['strelograph_work'],
            ['pendulum_work', 'pendulum_control', 'pendulum_front'],
            ['sagging_left', 'sagging_right']
        ]
        measurement_charts: List[AbstractChartOrientationMixin] = []
        measurement_chart_mappers: List[QVXYModelMapper] = []
        measurement_chart_viewes: List[QChartView] = []
        for chart_column_names in measurement_charts_column_names:
            # valueRange - иксы, т.к. тут наоборот
            #chart_value_min: float = min(config['models']['sensors'][column_name]['value_range']['min'] for column_name in chart_column_names)
            #chart_value_max: float = max(config['models']['sensors'][column_name]['value_range']['max'] for column_name in chart_column_names)
            #chart_position_min: float = min(config['models']['sensors'][column_name]['position_range']['min'] for column_name in chart_column_names)
            #chart_position_max: float = max(config['models']['sensors'][column_name]['position_range']['max'] for column_name in chart_column_names)
            chart_series: List[DynamicLineSeries] = [DynamicLineSeries(self.__picket_measurements_model,
                                                                       measurements_model.modelColumnIndexAtName(
                                                                           column_name), 0, QCoreApplication.translate(
                    'Measurement/control units', column_name)) for column_name in chart_column_names]
            #
            chart_series.append(DynamicLineSeries(self.__position_unit_line_model, 1, 0,
                                                  QCoreApplication.translate('Charts/Headers', 'Position'), self))
            #
            #if chart_column_names == ['pendulum_work', 'pendulum_control', 'pendulum_front']:
            #    title_ = 'Уровень'
            #else:
           #     title_ = False
                #self.horizontal_chart_title = LabelOnParent('Уровень', chart_view)
                #self.horizontal_chart_title.setStyleSheet("color:white;font:bold 20px;")
            #
            chart = VerticalChart(chart_series,
                         (0,0),  # не используются
                                      options.picket_direction == PicketDirection.Backward,
                                      (-100,100), False,
                                       x_tick=20, y_tick=100, #title=title_,
                                       #xMinorTickCount=1, yMinorTickCount=10,
                                       xGridLineColor="grey", yGridLineColor="grey")
            #, xMinorGridLineColor="grey", yMinorGridLineColor="grey")
            #
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignTop)
            #
            chart_view = QChartView(chart)
            #
            #if chart_column_names == ['pendulum_work', 'pendulum_control', 'pendulum_front']:
            #    title = 'Уровень'
                #self.horizontal_chart_title = LabelOnParent('Уровень', chart_view)
                #self.horizontal_chart_title.setStyleSheet("color:white;font:bold 20px;")
            #
            chart_view.setFocusPolicy(Qt.NoFocus)
            chart_view.chart().setBackgroundBrush(QBrush("black"))
            chart_view.setRenderHint(QPainter.Antialiasing)
            chartViewLayout.addWidget(chart_view, 1)
            measurement_chart_mappers += [series.mapper() for series in chart_series]
            measurement_chart_viewes.append(chart_view)
            measurement_charts.append(chart)

        self.__chart_slide_window_updater = ChartSlidingWindowProvider(self.__picket_position_model,
                                                                                    measurement_chart_viewes,
                                                                                    measurement_charts,
                             (10, 1) if options.picket_direction == PicketDirection.Forward else (1, 10),
                                                                                    measurement_chart_mappers,
                                                                                    (100, 250),
                                                                       isVertical=True)
        self.__update_chart_slide_window_timer = QTimer(self)
        self.__update_chart_slide_window_timer.timeout.connect(self.__update_chart_sliding_window)
        self.__update_chart_slide_window_timer.start(500)
        self.__update_chart_sliding_window()

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(information_panel, 0)
        layout.addWidget(measurementsView, 1)

    def __show_input_railway_marker_window(self) ->None:
        #print('__show_input_railway_marker_window')
        self.__select_marker_window.show()

    def __update_chart_sliding_window(self):
       self.__chart_slide_window_updater.disableViewUpdates()
       self.__chart_slide_window_updater.updateChartsState()
       self.__chart_slide_window_updater.enableViewUpdates()

    def __onStartMeauserements(self) ->None:
        if self.measuringInProcessFlag == False:
            self.startMeausermentButton.setStyleSheet("border-style:outset; border-width:7px; border-color:red;")
            self.__state.startMeasurementsWriter()
            self.startMeausermentButton.setEnabled(False)
            self.measuringInProcessFlag = True

    def __onFinishMeauserements(self):
        if QMessageBox.question(self, QCoreApplication.translate('Measuring trip/process/finish message box', 'Finish'), QCoreApplication.translate('Measuring trip/process/finish message box', 'Finish the measuring trip?')) == QMessageBox.StandardButton.No:
            return
        self.__state.stopMeasurementsWriter()
        self.__state.finishMeasuringProcess()
       # self.startMeausermentButton.setStyleSheet("")
       # self.startMeausermentButton.setEnabled(True)

    @staticmethod
    def __translation_storage() ->None:
        raise Exception('Do not call this fucking method!!!')
        QCoreApplication.translate('Measuring trip/process/view/charts', 'pendulum_work')

class MeasuringSuccessView(QWidget):
    def __init__(self, state: MeasuringSuccessState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.__state = state

        saveButtom = QPushButton(QCoreApplication.translate('Measuring trip/success/view', 'Save'))
        saveButtom.setProperty("optionsWindowPushButton", True)
        quitButton = QPushButton(QCoreApplication.translate('Measuring trip/success/view', 'Quit'))
        quitButton.setProperty("optionsWindowPushButton", True)

        saveButtom.clicked.connect(self.__saveMeasuringResult)
        quitButton.clicked.connect(self.__finishMeasuring)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel('application/measuring/complete'))
        layout.addWidget(saveButtom)
        layout.addWidget(quitButton)

    def __saveMeasuringResult(self):
        preffered_name: str = f'{self.__state.result().options.track_title}__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.amt'
        saveFile = QFileDialog.getSaveFileName(self, QCoreApplication.translate('Measuring trip/success/view', 'Select save measuring trip file'), preffered_name, '*.amt')[0]
        if saveFile is None or len(saveFile) == 0:
            return
        elif not saveFile.endswith('.amt'):
            saveFile += '.amt'

        try:
            result: MeasuringTripResultDto = self.__state.result()
            MeasuringTripResultDto_to_archive(zipfile.ZipFile(saveFile, 'w'), result)
        except Exception as error:
            QMessageBox.critical(self, QCoreApplication.translate('Measuring trip/success/view', 'Saving error'), str(error))
            os.remove(saveFile)

    def __finishMeasuring(self):
        if QMessageBox.question(self, QCoreApplication.translate('Measuring trip/success/finish message box', 'Quit'),
        QCoreApplication.translate('Measuring trip/success/finish message box', 'Do you really want to go out?')) == QMessageBox.StandardButton.No:
            return

        self.__state.finish.emit()

class MeasuringErrorView(QWidget):
    def __init__(self, state: MeasuringErrorState, parent: QWidget = None):
        super().__init__(parent)
        self.__state = state

        errorLabel = QLabel(str(self.__state.error()))
        quitButton = QPushButton(QCoreApplication.translate('Measuring trip/error/view', 'Quit'))
        quitButton.setProperty("optionsWindowPushButton", True)
        quitButton.clicked.connect(self.__state.finish)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel('application/measuring/error'))
        layout.addWidget(QLabel(QCoreApplication.translate('Measuring trip/error/view', 'Error occured:')))
        layout.addWidget(errorLabel)
        layout.addWidget(quitButton)

class MeasuringView(QWidget):
    def __init__(self, state: ApplicationMeasuringState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.__state: ApplicationMeasuringState = state
        self.__state.options.entered.connect(self.__onOptionsStateEntered)
        self.__state.options.exited.connect(self.__onOptionsStateExited)
        self.__state.process.entered.connect(self.__onProcessStateEntered)
        self.__state.process.exited.connect(self.__onProcessStateExited)
        self.__state.success.entered.connect(self.__onSuccessStateEntered)
        self.__state.success.exited.connect(self.__onSuccessStateExited)
        self.__state.error.entered.connect(self.__onErrorStateEntered)
        self.__state.error.exited.connect(self.__onErrorStateExited)
        self.__state.final.entered.connect(self.__onFinalStateEntered)
        self.__state.final.exited.connect(self.__onFinalStateExited)

        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.setLayout(self.__layout)

    def __onOptionsStateEntered(self) ->None:
        self.__currentView = MeasuringOptionsView(self.__state.options)
        self.__layout.addWidget(self.__currentView)
    def __onOptionsStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onProcessStateEntered(self) ->None:
        self.__currentView = MeasuringProcessView(self.__state.process)
        self.__layout.addWidget(self.__currentView)
    def __onProcessStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onSuccessStateEntered(self) ->None:
        self.__currentView = MeasuringSuccessView(self.__state.success)
        self.__layout.addWidget(self.__currentView)
    def __onSuccessStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onErrorStateEntered(self) ->None:
        self.__currentView = MeasuringErrorView(self.__state.error)
        self.__layout.addWidget(self.__currentView)
    def __onErrorStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onFinalStateEntered(self) ->None:
        pass
    def __onFinalStateExited(self) ->None:
        pass
#======================================================================
