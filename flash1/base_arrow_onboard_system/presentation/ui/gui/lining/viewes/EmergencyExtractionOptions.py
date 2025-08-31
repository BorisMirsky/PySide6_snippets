import random
import pandas
import math
from typing import Optional, Tuple, List
from PySide6.QtCharts import QChartView
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QPushButton, QLabel, QDoubleSpinBox, QDialog, QWidget
from PySide6.QtCore import Qt, QCoreApplication, QMargins
from PySide6.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QPen

from domain.dto.Workflow import LiningTripOptionsDto, LiningTripResultDto, EmergencyExtractionOptionsDto
from domain.dto.Travelling import PicketDirection, LocationVector1D, SteppedData
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart, AbstractChartOrientationMixin
from presentation.ui.gui.common.elements.SingleLineModel import SingleLineModel
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from domain.calculations.branching import make_urgent_branch
from domain.calculations.helpers import UrgentBranchParameters, find_max_delta_in_progtask_at




QCoreApplication.translate('Lining/extraction options', 'plan_fact')
QCoreApplication.translate('Lining/extraction options', 'plan_prj')
QCoreApplication.translate('Lining/extraction options', 'vozv_fact')
QCoreApplication.translate('Lining/extraction options', 'vozv_prj')
QCoreApplication.translate('Lining/extraction options', 'prof_fact')
QCoreApplication.translate('Lining/extraction options', 'prof_prj')

focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"




def mock_calculate_emergency_extraction(slope: float, shiftiing: float, lifting_left: float,
                                        lifting_right: float) -> SteppedData:
    step_size = 0.185
    track_size = max([shiftiing, lifting_left, lifting_right]) / slope
    step_count = math.ceil(track_size / step_size)
    extraction_trajectory = pandas.DataFrame(columns=['plan_prj', 'vozv_prj', 'prof_prj'])
    extraction_trajectory.index.name = 'step'
    for step in range(step_count):
        extraction_trajectory.loc[step] = {
            'plan_prj': random.random(),
            'vozv_prj': random.random(),
            'prof_prj': random.random()
        }.values()
    return SteppedData(data=extraction_trajectory, step=LocationVector1D(meters=step_size))

#  QDialog чтобы была модальность
class EmergencyExtractionOptions(QDialog):
    def __init__(self, 
            start_extraction_picket: float, 
            options: LiningTripOptionsDto,
            program_task_by_raw_position: AbstractPositionedTableModel,
            # program_task_by_picket: PicketPositionedTableModel,
            measurements: AbstractPositionedTableModel,
            parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent) # = parent, f = Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        #
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)        # disable close window (don't works)
        self.setWindowState(Qt.WindowMaximized)                                    # full screen
        #
        self.__step_size: float = program_task_by_raw_position.step().meters
        self.__extraction_trajectory_model: QStandardItemModel = QStandardItemModel()
        self.__extraction_trajectory_model.setColumnCount(6)
        self.__extraction_trajectory: SteppedData = None

        self.__program_task_by_raw_position: AbstractPositionedTableModel = program_task_by_raw_position
        # self.__program_task_by_picket: AbstractPositionedTableModel = program_task_by_picket        
        self.__program_task_by_picket = PicketPositionedTableModel(
                                            direction= options.program_task.options.picket_direction, 
                                            start_picket= options.program_task.options.start_picket.meters, 
                                            parent= self)
        self.__program_task_by_picket.setSourceModel(program_task_by_raw_position)

        self.__position_line_model: SingleLineModel = SingleLineModel(start_extraction_picket)
        self.__measurements: AbstractPositionedTableModel = measurements
        self.__options: LiningTripOptionsDto = options
        self.__start_extraction_picket: float = start_extraction_picket
        self.__start_extraction_step = self.__program_task_by_picket.getStepByPicket(start_extraction_picket)
        self.__params = UrgentBranchParameters.from_velocity(
                            velocity= self.__options.program_task.options.restrictions['segments'][0]['v_pass'],
                            delta= find_max_delta_in_progtask_at(self.__start_extraction_step, self.__program_task_by_raw_position.dataframe()))

        # ================================================================
        # position_multiplyer: int = self.__options.program_task.options.measuring_trip.options.picket_direction.multiplier()
        # position_range: tuple[LocationVector1D, LocationVector1D] = self.__program_task_by_raw_position.minmaxPosition()
        # position_min: float = position_multiplyer * position_range[
        #     0].meters + self.__options.program_task.options.measuring_trip.options.start_picket.meters
        # position_max: float = position_multiplyer * position_range[
        #     1].meters + self.__options.program_task.options.measuring_trip.options.start_picket.meters

        self.__direction_multiplier = self.__options.picket_direction.multiplier()
        self.position_min, self.position_max = self.__program_task_by_picket.minmaxPosition()
        print('> position_min, position_max ', self.position_min, self.position_max)

        program_task_charts_columns: List[str] = [
            (['plan_fact', 'plan_prj'], ('plan_extraction', 1)),
            (['plan_delta'], ('plan_delta_extraction', 2)),
            (['vozv_fact', 'vozv_prj'], ('vozv_extraction', 3)),
            (['prof_fact_left', 'prof_fact_right', 'prof_prj'], ('prof_extraction', 4)),
            (['prof_delta_left', 'prof_delta_right'], ('prof_delta_extraction', 5))
        ]
        self.__program_task_charts: List[AbstractChartOrientationMixin] = []
        self.__program_task_chart_viewes: List[QChartView] = []

        preview_charts_layout = QVBoxLayout()
        for column_names, trajectory_model_index in program_task_charts_columns:
            minmax_charts_values: List[Tuple[float, float]] = [
                self.__program_task_by_raw_position.minmaxValueByColumn(column_name) for column_name in column_names]
            chart_value_range: Tuple[float, float] = (
                min(minmax_charts_values, key=lambda minmax_value: minmax_value[0])[0],
                max(minmax_charts_values, key=lambda minmax_value: minmax_value[1])[1]
            )

            chart_value_range_length = chart_value_range[1] - chart_value_range[0]
            chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
            chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length

            series = [
                DynamicLineSeries(self.__program_task_by_picket, 0,
                                  self.__program_task_by_raw_position.modelColumnIndexAtName(column_name),
                                  QCoreApplication.translate('Lining trip/process/view/charts/program task',
                                                             column_name))
                for column_name in column_names
            ]

            trajectory = DynamicLineSeries(self.__extraction_trajectory_model, 0, trajectory_model_index[1],
                                           trajectory_model_index[0])
            trajectory.setPen(QPen(QColor("#EBE330"), 4))
            position_line_series = DynamicLineSeries(self.__position_line_model, 0, 1, QCoreApplication.translate(
                'Lining trip/process/view/charts/measurements', 'position'), self)
            position_line_series.setPen(QPen(QColor("magenta"), 2))
            if column_names == ['plan_fact', 'plan_prj']:
                series[0].setPen(QPen(QColor("#41FA00"), 2))
                series[1].setPen(QPen(QColor("red"), 2))
            elif column_names == ['plan_delta']:
                series[0].setPen(QPen(QColor("#41FA00"), 2))
            elif column_names == ['vozv_fact', 'vozv_prj']:
                series[0].setPen(QPen(QColor("cyan"), 2))
                series[1].setPen(QPen(QColor("red"), 2))
            elif column_names == ['prof_fact_left', 'prof_fact_right', 'prof_prj']:
               series[0].setPen(QPen(QColor("#27B14A"), 2))
               series[1].setPen(QPen(QColor("white"), 2))
               series[2].setPen(QPen(QColor("#ff0000"), 2))
            elif column_names == ['prof_delta_left', 'prof_delta_right']:
                series[0].setPen(QPen(Qt.GlobalColor.darkBlue, 2))
                series[1].setPen(QPen(Qt.GlobalColor.darkCyan, 2))

            #
            chart = HorizontalChart((self.position_min, self.position_max),
                                    options.picket_direction == PicketDirection.Backward,
                                    (chart_value_min, chart_value_max),
                                    valueReverse=False, series0=(series + [trajectory]),
                                    x_tick=100, y_tick=10,
                                    xGridLineColor="grey", yGridLineColor="grey", XAxisHideLabels=True
                                    )

            chart.addSeries(position_line_series)
            chart.legend().setLabelColor(QColor('white'))
            chart.layout().setContentsMargins(0, 0, 0, 0)
            chart.setMargins(QMargins(0, 0, 0, 0))
            # chart.legend().
            position_line_series.attachAxis(chart.positionAxis())
            position_line_series.attachAxis(chart.valueAxis())

            self.__chart_view = QChartView(chart)
            self.__chart_view.chart().setBackgroundBrush(QBrush("black"))
            self.__chart_view.setFocusPolicy(Qt.NoFocus)
            self.__chart_view.setMinimumHeight(150)   # 250
            preview_charts_layout.addWidget(self.__chart_view)

            self.__program_task_chart_viewes.append(self.__chart_view)
            self.__program_task_charts.append(chart)
        # ================================================================

        self.__slope_input = QDoubleSpinBox()
        self.__slope_input.setStyleSheet(focus_style)
        self.__slope_input.setObjectName("__slope_input")
        self.__slope_input.setRange(0.1, 10)            # mm
        self.__slope_input.setValue(self.__params.slope)
        self.__slope_input.valueChanged.connect(self.__processingParamsSlopeChanged)    #self.__setParams) #
        self.__velocity_input = QDoubleSpinBox()
        self.__velocity_input.setStyleSheet(focus_style)
        self.__velocity_input.setObjectName("__velocity_input")
        self.__velocity_input.setRange(5, 300)            # km\h
        self.__velocity_input.setValue(self.__params.velocity)
        self.__velocity_input.valueChanged.connect(self.__processingParamsVelocityChanged)
        self.__length_input = QDoubleSpinBox()
        self.__length_input.setStyleSheet(focus_style)
        self.__length_input.setObjectName("__length_input")
        self.__length_input.setRange(1, 1000)        # m
        self.__length_input.setValue(self.__params.length)
        self.__length_input.valueChanged.connect(self.__processingParamsLengthChanged)

        calculate_button = QPushButton(QCoreApplication.translate('Lining/extraction options', 'Calculate'))
        calculate_button.setProperty("optionsWindowPushButton", True)
        calculate_button.setStyleSheet(focus_style)
        self.__acceptButton = QPushButton(QCoreApplication.translate('Lining/extraction options', 'Accept'))
        self.__acceptButton.setProperty("optionsWindowPushButton", True)
        self.__acceptButton.setStyleSheet(focus_style)
        reject_button = QPushButton(QCoreApplication.translate('Lining/extraction options', 'Reject'))
        reject_button.setProperty("optionsWindowPushButton", True)
        reject_button.setStyleSheet(focus_style)
        calculate_button.clicked.connect(self.__recalculatePreview)
        self.__acceptButton.clicked.connect(self.accept)
        reject_button.clicked.connect(self.reject)

        self.__acceptButton.setEnabled(False)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addLayout(preview_charts_layout, 0, 0, 2, 4)

        layout.addWidget(QLabel(QCoreApplication.translate('Lining/extraction options', 'Slope')), 2, 0, 1, 1)
        layout.addWidget(self.__slope_input, 2, 1, 1, 1)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining/extraction options', 'mm')), 2, 2, 1, 1)
        layout.addWidget(calculate_button, 2, 3, 1, 1)

        layout.addWidget(QLabel(QCoreApplication.translate('Lining/extraction options', 'Velocity')), 3, 0, 1, 1)
        layout.addWidget(self.__velocity_input, 3, 1, 1, 1)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining/extraction options', 'km/h')), 3, 2, 1, 1)

        layout.addWidget(QLabel(QCoreApplication.translate('Lining/extraction options', 'Length')), 4, 0, 1, 1)
        layout.addWidget(self.__length_input, 4, 1, 1, 1)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining/extraction options', 'm')), 4, 2, 1, 1)

        layout.addWidget(self.__acceptButton, 6, 2, 1, 2)
        layout.addWidget(reject_button, 6, 0, 1, 2)

        layout.setRowStretch(2, 0)
        layout.setRowStretch(3, 0)
        layout.setRowStretch(4, 0)
        layout.setRowStretch(6, 0)

    def __processingParamsSlopeChanged(self, value):
        self.__params = UrgentBranchParameters.from_slope(value, self.__params.delta)
        self.__velocity_input.blockSignals(True)
        self.__velocity_input.setValue(self.__params.velocity)
        self.__velocity_input.blockSignals(False)
        self.__length_input.blockSignals(True)
        self.__length_input.setValue(self.__params.length)
        self.__length_input.blockSignals(False)

    def __processingParamsVelocityChanged(self, value):
        self.__params = UrgentBranchParameters.from_velocity(value, self.__params.delta)
        self.__slope_input.blockSignals(True)
        self.__slope_input.setValue(self.__params.slope)
        self.__slope_input.blockSignals(False)
        self.__length_input.blockSignals(True)
        self.__length_input.setValue(self.__params.length)
        self.__length_input.blockSignals(False)

    def __processingParamsLengthChanged(self, value):
        self.__params = UrgentBranchParameters.from_length(value, self.__params.delta)
        self.__slope_input.blockSignals(True)
        self.__slope_input.setValue(self.__params.slope)
        self.__slope_input.blockSignals(False)
        self.__velocity_input.blockSignals(True)
        self.__velocity_input.setValue(self.__params.velocity)
        self.__velocity_input.blockSignals(False)

    def parameters(self) -> EmergencyExtractionOptionsDto:
        return EmergencyExtractionOptionsDto(
            lining_trip=LiningTripResultDto(options=self.__options,
                                            measurements=SteppedData(
                                                data=self.__measurements.dataframe(),
                                                step=self.__measurements.step()
                                            )),
            start_extraction_picket=LocationVector1D(meters=self.__start_extraction_picket),
            extraction_trajectory=self.__extraction_trajectory,
            slope=self.__params.slope,
            velocity=self.__params.velocity,
            length=self.__params.length
        )

    # перерасчёт
    def __recalculatePreview(self) -> None:
        self.__extraction_trajectory = SteppedData(
            data= make_urgent_branch(
                                task= self.__program_task_by_raw_position.dataframe(),
                                data_step= self.__step_size,
                                start_step= self.__start_extraction_step,
                                per_mille= self.__params.slope,
                                front_chord= 10),
            step= LocationVector1D(meters=self.__step_size)
        )

        self.__extraction_trajectory.data['v1'] = self.__extraction_trajectory.data["plan_prj"] + self.__extraction_trajectory.data["plan_dF"]
        self.__extraction_trajectory.data['v2'] = self.__extraction_trajectory.data["plan_delta"] * self.__extraction_trajectory.data["front_delta_multiplier"]
        self.__extraction_trajectory.data['v3'] = self.__extraction_trajectory.data["vozv_prj"] + self.__extraction_trajectory.data["vozv_dF"]
        self.__extraction_trajectory.data['v4'] = self.__extraction_trajectory.data["prof_prj"] + self.__extraction_trajectory.data["prof_dF"]
        self.__extraction_trajectory.data['v5'] = self.__extraction_trajectory.data["prof_delta"] * self.__extraction_trajectory.data["front_delta_multiplier"]
        self.__acceptButton.setEnabled(True)

        """
        user_available_railway_markers = []
        user_available_railway_markers_confing: pandas.DataFrame = pandas.read_csv('./resources/configs/user_available_railway_markers.csv', sep = ';')
        for _, row in user_available_railway_markers_confing.iterrows():
            type: RailwayMarkerType = RailwayMarkerType[row['type']]
            location: RailwayMarkerLocation = RailwayMarkerLocation[row['location']]
            user_available_railway_markers.append((
                self.__state.marker_models()[type][0], 
                RailwayMarker(row['title'], type, location), 
                QIcon(row['icon']), row['is_continuation']))
        """
        self.__extraction_trajectory_model.clear()
        #
        for idx, row in self.__extraction_trajectory.data.iterrows():
            position = self.__options.program_task.options.start_picket.meters + self.__direction_multiplier * self.__extraction_trajectory.step.meters * idx
            self.__extraction_trajectory_model.appendRow([
                QStandardItem(f'{position}'),
                QStandardItem(f'{float(row["v1"])}'),
                QStandardItem(f'{float(row["v2"])}'),
                QStandardItem(f'{float(row["v3"])}'),
                QStandardItem(f'{float(row["v4"])}'),
                QStandardItem(f'{float(row["v5"])}')
            ])
