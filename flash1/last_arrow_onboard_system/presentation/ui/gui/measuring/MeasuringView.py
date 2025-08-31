# This Python file uses the following encoding: utf-8
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.dto.Travelling import MovingDirection, PicketDirection, BaseRail, LocationVector1D, RailPressType
from domain.dto.Workflow import MeasuringTripOptionsDto, MeasuringTripResultDto
from domain.dto.Markers import RailwayMarker, RailwayMarkerType, RailwayMarkerLocation
from operating.states.measuring.ApplicationMeasuringState import MeasuringOptionsState, MeasuringProcessState, MeasuringSuccessState, MeasuringErrorState, MeasuringFinalState
from operating.states.measuring.ApplicationMeasuringState import ApplicationMeasuringState
from ..common.viewes.TableDataChartsView import DynamicLineSeries, VerticalChart, ChartSlidingWindowProvider, AbstractChartOrientationMixin
from ..common.viewes.LabelOnChart import LabelOnParent
from ..common.viewes.RailwayMarkerView import SelectCurrentMarkerWindow, RailwayMarkerLinesScatter, SelectCurrentMarker
from ..common.elements.Travelling import CurrentPicketLabel, PassedMetersLabel, BaseRailLabel, PressRailLabel, MovingDirectionLabel, PicketDirectionLabel, RailwayInfoPanel
from ..common.elements.Time import CurrentTimeLabel, ElapsedTimeLabel
from ..common.elements.SingleLineModel import SingleLineModel
from ....models.PicketPositionUnit import PicketPositionUnit
from ....models.PicketPositionedTableModel import PicketPositionedTableModel
from ....models.TranslatedHeadersTableModel import TranslatedHeadersTableModel
from ....utils.store.workflow.zip.Dto import MeasuringTripResultDto_to_archive
from presentation.ui.gui.common.viewes.WindowTitle import Window

from PySide6.QtWidgets import (
    QStackedLayout, QWidget, QDoubleSpinBox, QLabel, QPushButton,
    QHeaderView, QTableView, QTabWidget, QHBoxLayout, QVBoxLayout, 
    QGridLayout, QMessageBox, QFileDialog, QComboBox, 
    QLineEdit, QAbstractItemView,
    QApplication
)
from PySide6.QtCharts import QChartView, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QAbstractTableModel
from PySide6.QtGui import (
    QKeySequence, QShortcut, QImage, QIcon, QBrush, QPainter,
    QFont, QPen, QColor
)
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

        self.__window = Window("Измерительная поездка")

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
        self.setLayout(self.__window)
        self.__window.addLayout(layout, 1)
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

    charts: list[VerticalChart] = []
    y_axis_scale = 10

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
        self.__window = Window("Измерительная поездка")
        self.legend_font_size = 16
        #==============================================
        self.__meters_position_provider = self.__state.position_unit()
        self.__picket_position_model = PicketPositionUnit(self.__meters_position_provider, options.picket_direction, options.start_picket.meters)
        
        self.__position_unit_line_model = SingleLineModel(self.__picket_position_model.read() or 0)
        self.__picket_position_model.changed.connect(self.__position_unit_line_model.setPosition)
        self.__picket_position_model.changed.connect(self.__on_position_changed)
        self.__on_position_changed(self.__picket_position_model.read())

        self.__strelograph_work_edit_line = QLineEdit()
        self.__state.sensors().get('strelograph_work').changed.connect(
            self.__onStrelographWorkChanged
        )

        self.__pendulum_work_edit_line = QLineEdit()
        self.__state.sensors().get('pendulum_work').changed.connect(
            self.__onPendulumWorkChanged
        )
        self.__pendulum_control_edit_line = QLineEdit()
        self.__state.sensors().get('pendulum_control').changed.connect(
            self.__onPendulumControlChanged
        )
        self.__pendulum_front_edit_line = QLineEdit()
        self.__state.sensors().get('pendulum_front').changed.connect(
            self.__onPendulumFrontChanged
        )
        self.__sagging_left_edit_line = QLineEdit()
        self.__state.sensors().get('sagging_left').changed.connect(
            self.__onSaggingLeftChanged
        )

        self.__sagging_right_edit_line = QLineEdit()
        self.__state.sensors().get('sagging_right').changed.connect(
            self.__onSaggingRightChanged
        )
        self.__position_scaler = QComboBox()
        self.__position_scaler.addItems(["10 м", "50 м", "100 м", "500 м", "1000 м"])
        self.__position_scaler.setCurrentIndex(0)
        self.__position_scaler.currentIndexChanged.connect(
            self.__update_scale_value
        )
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
        self.marker_view = None
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
        singleMarkersButton = QPushButton("Одиночный маркер (F3)")
        singleMarkersButton.clicked.connect(self.__show_input_single_railway_marker)
        singleMarkersButton.setProperty("centerButton", True)

        longMarkersButton = QPushButton("Продолжительный  маркер (F4)")
        longMarkersButton.clicked.connect(self.__show_input_long_railway_marker)
        longMarkersButton.setProperty("centerButton", True)


        cornerHbox.addWidget(singleMarkersButton)
        cornerHbox.addWidget(longMarkersButton)
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
        
        scaler_container = QHBoxLayout()
        scaler_container.setAlignment(Qt.AlignCenter)

        scaler_label = QLabel("Масштаб:")
        scaler_label.setAlignment(Qt.AlignCenter)
        scaler_label.setObjectName('measuring_section_label')
        scaler_container.addWidget(scaler_label)
        scaler_container.addWidget(self.__position_scaler)
        scaler_container.addStretch()

        self.marker_view = RailwayMarkerLinesScatter(
            self.__picket_position_model, 
            (10, 1) if options.picket_direction == PicketDirection.Forward else (1, 10), 
            marker_models_with_icons,
            options=options
        )
        
        self.marker_view.setMaximumWidth(220)
        legend_font = QFont()
        legend_font.setPixelSize(self.legend_font_size)
        self.marker_view.chart().legend().setFont(legend_font)

        vl = QVBoxLayout()
        vl.addLayout(scaler_container)
        vl.addWidget(self.marker_view, 1)

        chartViewLayout.addLayout(vl)

        self.__select_marker = SelectCurrentMarker(position_unit = self.__meters_position_provider, 
                marker_step = 0.5,  parent= None)
            
        self.__single_select_maker_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F3), self)
        self.__single_select_maker_shortcut.activated.connect(self.__show_input_single_railway_marker)

        self.__long_select_maker_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F4), self)
        self.__long_select_maker_shortcut.activated.connect(self.__show_input_long_railway_marker)

        self.__start_meauserement_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F5), self)
        self.__start_meauserement_shortcut.activated.connect(self.__onStartMeauserements)

        self.__finish_meauserement_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F9), self)
        self.__finish_meauserement_shortcut.activated.connect(self.__onFinishMeauserements)

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

        colors_associations = {
            'strelograph_work': '#0000FF',
            'pendulum_work': '#0000FF',
            'pendulum_control': '#FF0000',
            'pendulum_front': '#33CC33',
            'sagging_left': '#0000FF',
            'sagging_right': '#FF0000',
        }
        chart_reverse_y = False
        # Инвертировать ось Y
        if (
            self.__state.options().moving_direction == MovingDirection.Forward 
            and self.__state.options().picket_direction == PicketDirection.Backward
        ):
            chart_reverse_y = True
        
        if (
            self.__state.options().moving_direction == MovingDirection.Backward 
            and self.__state.options().picket_direction == PicketDirection.Forward
        ):
            chart_reverse_y = True

        for chart_column_names in measurement_charts_column_names:
            chart_and_line_edits = QHBoxLayout()
            chart_and_line_edits.setAlignment(Qt.AlignCenter)
   
            chart_series: List[DynamicLineSeries] = [DynamicLineSeries(
                self.__picket_measurements_model,
                measurements_model.modelColumnIndexAtName(column_name), 
                0, 
                QCoreApplication.translate('Measurement/control units', column_name),
                color=colors_associations.get(column_name)
            ) for column_name in chart_column_names]

            chart_series.append(DynamicLineSeries(
                self.__position_unit_line_model, 1, 0,
                QCoreApplication.translate('Charts/Headers', 'Position'),
                self
            ))
            
            for col_name in chart_column_names:
                widget: QLineEdit = getattr(self, f'_MeasuringProcessView__{col_name}_edit_line')
                widget.setObjectName('measuring_sections_edit_lines')
                widget.setStyleSheet(f"""color: {colors_associations.get(col_name, 'red')};""")
                widget.setAlignment(Qt.AlignCenter)
                # widget.setMaximumWidth(80)
                chart_and_line_edits.addWidget(widget)

            chart = VerticalChart(
                chart_series,
                (0, 10),  # Position Range
                options.picket_direction == PicketDirection.Backward,
                (-100, 100),
                False,
                x_tick=20,
                y_tick=100, 
                #title=title_,
                #xMinorTickCount=1, yMinorTickCount=10,
                xGridLineColor="grey", yGridLineColor="grey",
                legend_font_size=self.legend_font_size
            )
            chart.axisY().setReverse(chart_reverse_y)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignTop)
            chart_view = QChartView(chart)
            chart_view.setFocusPolicy(Qt.NoFocus)
            chart_view.chart().setBackgroundBrush(QBrush("black"))
            chart_view.setRenderHint(QPainter.Antialiasing)

            # График снизу
            vert_layout = QVBoxLayout()
            vert_layout.addLayout(chart_and_line_edits)
            vert_layout.addWidget(chart_view)

            # Убедимся, что layout и виджет имеют необходимые отступы
            vert_layout.setContentsMargins(0, 0, 0, 0)  # Добавление отступов для лучшего отображения

            # Создание контейнера для layout
            chart_container = QWidget()
            chart_container.setLayout(vert_layout)

            # Добавление контейнера с графиком и заголовком в основной layout
            # add 1 for streching on all empty space
            chartViewLayout.addWidget(chart_container, 1)

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
        self.setLayout(self.__window)
        self.__window.addLayout(layout)
        layout.addWidget(information_panel, 0)
        layout.addWidget(measurementsView, 1)

        self.charts = measurement_charts

    def __on_position_changed(self, position: float) -> None:
        """
            Смена масштаба оси Y в графиках
        """
        if (
            self.__state.options().picket_direction == PicketDirection.Forward and 
            self.__state.options().moving_direction == MovingDirection.Forward
        ) or (
            self.__state.options().picket_direction == PicketDirection.Forward and 
            self.__state.options().moving_direction == MovingDirection.Backward
        ):
            max_pos = max(self.y_axis_scale + self.__state.options().start_picket.meters, position)
            min_pos = max(
                self.__state.options().start_picket.meters, max_pos - self.y_axis_scale
            )
        
        if (
            self.__state.options().picket_direction == PicketDirection.Backward and 
            self.__state.options().moving_direction == MovingDirection.Forward
        ) or (
            self.__state.options().picket_direction == PicketDirection.Backward and 
            self.__state.options().moving_direction == MovingDirection.Backward
        ):
            threshold = self.__state.options().start_picket.meters - self.y_axis_scale
            if position > threshold:
                max_pos = self.__state.options().start_picket.meters
            else:
                max_pos = max(position + self.y_axis_scale, position)
            
            min_pos = min(max_pos - self.y_axis_scale, position)
        
        for chart in self.charts:
            chart.axisY().setRange(min_pos, max_pos)
           
    def __update_scale_value(self, index: int) -> None:
        """
            Меняем значения масштаба относительно выбора в combobox
        """
        scale_values = [10, 50, 100, 500, 1000]  # Масштабы
        new_range = scale_values[index]
        self.y_axis_scale = new_range
        self.marker_view.scale_change(new_range)
        
    def __onStrelographWorkChanged(self, value: float) -> None:
        self.__strelograph_work_edit_line.setText(
            f'{round(value, 3)}' if value else '-'
        )
            
    def __onPendulumWorkChanged(self, value: float) -> None:
        self.__pendulum_work_edit_line.setText(
            f'{round(value, 3)}' if value else '-'
        )
    
    def __onPendulumControlChanged(self, value: float) -> None:
        self.__pendulum_control_edit_line.setText(
            f'{round(value, 3)}' if value else '-'
        )
    
    def __onPendulumFrontChanged(self, value: float) -> None:
        self.__pendulum_front_edit_line.setText(
            f'{round(value, 3)}' if value else '-'
        )

    def __onSaggingLeftChanged(self, value: float) -> None:
        self.__sagging_left_edit_line.setText(
            f'{round(value, 3)}' if value else '-'
        )

    def __onSaggingRightChanged(self, value: float) -> None:
        self.__sagging_right_edit_line.setText(
            f'{round(value, 3)}'
        )

    def __show_input_railway_marker_window(self) -> None:
        #print('__show_input_railway_marker_window')
        self.__select_marker_window.show()
    def __get_marker(self, is_continuation=False):
        user_available_railway_markers_confing: pandas.DataFrame = pandas.read_csv('./resources/configs/user_available_railway_markers.csv', sep = ';')
        for _, row in user_available_railway_markers_confing.iterrows():
            type: RailwayMarkerType = RailwayMarkerType[row['type']]
            location: RailwayMarkerLocation = RailwayMarkerLocation[row['location']]
            if is_continuation == row['is_continuation']:
                return (self.__state.marker_models()[type][0], 
                RailwayMarker(row['title'], type, location), 
                QIcon(row['icon']), row['is_continuation'])

    def __show_input_single_railway_marker(self) -> None:
        marker =  self.__get_marker(is_continuation = False)
        if marker:
            self.__select_marker.marker_selected(marker)
    
    def __show_input_long_railway_marker(self) -> None:
        marker =  self.__get_marker(is_continuation = True)
        if marker:
            self.__select_marker.marker_selected(marker)
    
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
        self.__window = Window("Измерительная поездка")

        saveButtom = QPushButton(QCoreApplication.translate('Measuring trip/success/view', 'Save'))
        saveButtom.setProperty("optionsWindowPushButton", True)
        quitButton = QPushButton(QCoreApplication.translate('Measuring trip/success/view', 'Quit'))
        quitButton.setProperty("optionsWindowPushButton", True)

        saveButtom.clicked.connect(self.__saveMeasuringResult)
        quitButton.clicked.connect(self.__finishMeasuring)

        layout = QVBoxLayout()
        self.setLayout(self.__window)
        self.__window.addLayout(layout, 1)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #layout.addWidget(QLabel('application/measuring/complete'))
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
        self.__window = Window("Измерительная поездка")

        errorLabel = QLabel(str(self.__state.error()))
        quitButton = QPushButton(QCoreApplication.translate('Measuring trip/error/view', 'Quit'))
        quitButton.setProperty("optionsWindowPushButton", True)
        quitButton.clicked.connect(self.__state.finish)

        layout = QVBoxLayout()
        self.setLayout(self.__window)
        self.__window.addLayout(layout, 1)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #layout.addWidget(QLabel('application/measuring/error'))
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
