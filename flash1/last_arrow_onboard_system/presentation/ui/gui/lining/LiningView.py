
# This Python file uses the following encoding: utf-8
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.dto.Workflow import LiningTripOptionsDto, LiningTripResultDto, EmergencyExtractionOptionsDto, EmergencyExtractionResultDto
from domain.dto.Travelling import PicketDirection, LocationVector1D, SteppedData, RailPressType
from domain.dto.DiscreteSignals import DiscreteSignalsContainer
from operating.states.lining.ApplicationLiningState import SelectLiningTripModeState, NewLiningOptionsState, ContinueLiningOptionsState, EmergencyExtractionRecoveryOptionsState, LiningProcessState, LiningSuccessState, LiningErrorState, EmergencyExtractionProcessState, EmergencyExtractionSuccessState, EmergencyExtractionErrorState, LiningFinalState, ApplicationLiningState
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from presentation.utils.store.workflow.zip.Dto import ProgramTaskCalculationResultDto_from_archive, LiningTripResultDto_from_archive, EmergencyExtractionResultDto_to_archive, EmergencyExtractionResultDto_from_archive
from presentation.ui.gui.common.elements.Files import FileSelector
from presentation.ui.gui.common.elements.Travelling import CurrentPicketLabel, PassedMetersLabel, RailwayInfoPanel, PicketDirectionLabel, PressRailLabel, BaseRailLabel, ProgramTaskFileName, HowManyMetersLeft
from presentation.ui.gui.common.elements.Time import ElapsedTimeLabel, CurrentTimeLabel #, ControlUnitConnection
from presentation.ui.gui.common.elements.SingleLineModel import SingleLineModel
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.models.PicketPositionUnit import PicketPositionUnit
from presentation.ui.gui.common.viewes.TableDataChartsView import (DynamicLineSeries, VerticalChart, HorizontalChart,
                                                                   ChartSlidingWindowProvider, AbstractChartOrientationMixin)
from presentation.ui.gui.common.elements.ArrowPointerIndicator import ArrowPointerIndicator
from presentation.ui.gui.lining.elements.FooterControlsPanel import FooterControlsPanel
from presentation.ui.gui.lining.viewes.EmergencyExtractionOptions import EmergencyExtractionOptions
from presentation.ui.gui.lining.viewes.GaugesPanel import GaugesPanel
from presentation.ui.gui.lining.elements.Equalizer import EqualizerPanel
from presentation.utils.store.workflow.zip.Dto import LiningTripResultDto_to_archive
from resources.style.StyleManager import StyleManager
from tools.helpers import ButtonFactory
from .ShowResult import ShowLiningResult
from domain.models.StepIndexedDataFramePositionedModel import ReducedStepIndexedPositionedModel
from ..common.viewes.MarkersChart import MarkersChart
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent2
from presentation.ui.gui.common.viewes.WindowTitle import Window

from PySide6.QtWidgets import QGroupBox, QInputDialog, QHeaderView, QDoubleSpinBox, QStackedLayout, QComboBox, \
    QTableView, QWidget, QLabel, QScrollArea, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, \
    QMessageBox, QDialog, QSizePolicy, QApplication, QCheckBox
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QElapsedTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QStandardItemModel, QStandardItem, QPixmap
from typing import Optional, List, Tuple
from itertools import cycle
import traceback
import zipfile
import math
import os
from pathlib import Path
import cProfile
#from line_profiler import profile



# Начать выправку - Продолжить выправку - Возобновить отвод - Отмена
class SelectLiningTripModeView(QWidget):
    def __init__(self, state: SelectLiningTripModeState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: SelectLiningTripModeState = state

        # Установка глобального стиля
        self.setStyleSheet(StyleManager.menu_button_style())
        self.custom_font = StyleManager.load_font()
        self.__window = Window("Выправка")

        # Логотип
        self.logo_label = QLabel()
        self.original_pixmap = QPixmap("resources/images/logo_vniizht_strela.png")
        if not self.original_pixmap.isNull():
            self.logo_label.setPixmap(self.original_pixmap.scaled(800, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                                                  Qt.TransformationMode.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        else:
            self.logo_label.setText("[Ошибка загрузки логотипа]")
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_label.setFont(self.custom_font)

        self.button_widgets = [
            ButtonFactory.create_button(QCoreApplication.translate('Lining/Select mode', text), callback,
                                        self.custom_font)
            for text, callback in [
                ("Выправка", self.__state.new_lining_trip),
                ("Просмотр результатов выправки", self.__state.continue_lining_trip),
                ("Continue lining trip", self.__state.continue_lining_trip),  # нужно ли??
                ("Emergency extraction recovery", self.__state.emergency_extraction_recovery_trip),
                ("Выход", self.__state.cancel)
            ]
        ]

        # Макет
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        button_layout = QGridLayout()


        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.logo_label)
        main_layout.addLayout(button_layout)

        button_layout.setContentsMargins(20, 20, 20, 20)
        button_layout.setSpacing(10)

        button_layout.addWidget(self.button_widgets[0], 0, 0, 1, 2)  # ВЫПРАВКА
        button_layout.addWidget(self.button_widgets[1], 0, 2, 1, 2)  # ПОСМОТРЕТЬ РЕЗУЛЬТАТЫ ВЫПРАВКИ
        button_layout.addWidget(self.button_widgets[3], 1, 0, 1, 2)  # ВОЗОБНОВИТЬ
        button_layout.addWidget(self.button_widgets[4], 1, 2, 1, 2)  # ВЫХОД

        self.__window.addLayout(main_layout, 1)
        self.setLayout(self.__window)

        if QApplication.instance():
            QApplication.instance().focusChanged.connect(self.update_button_focus) #Принудительно добавляем стили для кнопки
        QTimer.singleShot(0, self.set_initial_focus) #Принудительно передаёт фокус первой кнопке

        self.setMinimumSize(800, 800)

    def set_initial_focus(self):
        """Принудительно передаёт фокус первой кнопке"""
        if hasattr(self, 'button_widgets') and self.button_widgets:
            self.button_widgets[0].setFocus()
    def keyPressEvent(self, event):
        """Если нажата клавиша Escape, нажимаем кнопку 'Выход'"""

        if event.key() == Qt.Key.Key_Escape:
            self.button_widgets[4].click()  # Нажимаем кнопку "Выход"
            event.accept()
        else:
            super().keyPressEvent(event)  # Передаём остальные события дальше

    # def handle_escape(self):
    #     """Обрабатывает Escape, нажимая кнопку 'Выход'"""
    #     self.button_widgets[4].click()

    def update_button_focus(self):
        """Обновляет стиль активной кнопки в IdleView"""
        buttons = self.findChildren(QPushButton)  # Находим все кнопки внутри IdleView

        for button in buttons:
            if button.hasFocus():
                button.setStyleSheet(StyleManager.active_menu_button_style())
            else:
                button.setStyleSheet(StyleManager.menu_button_style())  # Сбрасываем стиль

        self.repaint()

        # self.__emergency_extraction_recovery_trip_button = QPushButton(QCoreApplication.translate('Lining/Select mode', 'Emergency extraction recovery'))
        # self.__watch_lining_result_button = QPushButton("Просмотр результатов выправки")
        # self.__continue_lining_trip_button = QPushButton(QCoreApplication.translate('Lining/Select mode', 'Continue lining trip'))
        # self.__new_lining_trip_button = QPushButton("Выправка")  #QCoreApplication.translate('Lining/Select mode', 'Lining trip'))
        # self.__cancel_button = QPushButton("Выход") #QCoreApplication.translate('Lining/Select mode', 'Quit'))
        # #
        # self.__emergency_extraction_recovery_trip_button.clicked.connect(self.__state.emergency_extraction_recovery_trip)
        # self.__watch_lining_result_button.clicked.connect(self.__state.continue_lining_trip)
        # self.__new_lining_trip_button.clicked.connect(self.__state.new_lining_trip)
        # self.__cancel_button.clicked.connect(self.__state.cancel)
        # #
        # self.__emergency_extraction_recovery_trip_button.setProperty("optionsWindowPushButton", True)
        # self.__watch_lining_result_button.setProperty("optionsWindowPushButton", True)
        # self.__continue_lining_trip_button.setProperty("optionsWindowPushButton", True)
        # self.__new_lining_trip_button.setProperty("optionsWindowPushButton", True)
        # self.__cancel_button.setProperty("optionsWindowPushButton", True)
        #
        # layout = QGridLayout()
        # for column in range(5):
        #     layout.setColumnStretch(column, 1)
        # for row in range(6):
        #     layout.setRowStretch(row, 1)
        # self.setLayout(layout)
        # layout.addWidget(self.__new_lining_trip_button, 1, 1, 1, 3)
        # layout.addWidget(self.__watch_lining_result_button, 2, 1, 1, 3)
        # layout.addWidget(self.__emergency_extraction_recovery_trip_button, 3, 1, 1, 3)
        # layout.addWidget(self.__cancel_button, 4, 1, 1, 3)

# Начать выправку
class NewLiningOptionsView(QWidget):
    def __init__(self, state: NewLiningOptionsState, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__state: NewLiningOptionsState = state
        self.__programTask = None
        self.__window = Window("Выправка")

        self.__startPicket = QDoubleSpinBox()
        self.__startPicket.setRange(-1000000000, 1000000000)
        self.__programTaskSelector = FileSelector('*.apt')
        self.__programTaskSelector.filepathChanged.connect(self.__onProgramTaskChanged)
        self.__picketDirection = QComboBox()
        self.__picketDirection.addItem(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Forward.name)), PicketDirection.Forward)
        self.__picketDirection.addItem(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Backward.name)), PicketDirection.Backward)
        # self.__picketDirection.currentIndexChanged.connect(self.__onPicketDirectionChanged)
        self.__picketDirection.setEnabled(False) #False)
        # Прижим
        self.__pressRail = QComboBox()
        self.__pressRail.addItem(QCoreApplication.translate('Travelling/BaseRail', (RailPressType.Right.name)), RailPressType.Right)
        self.__pressRail.addItem(QCoreApplication.translate('Travelling/BaseRail', (RailPressType.Left.name)), RailPressType.Left)
        self.__pressRail.setCurrentText(QCoreApplication.translate('Travelling/BaseRail', RailPressType.Left.name))
        # Автоматический отвод
        self.__autoBranchCheckBox = QCheckBox('Автоматический отвод')
        self.__autoBranchCheckBox.setChecked(True)

        processButton = QPushButton(QCoreApplication.translate('Lining trip/options/process button', 'Process'))
        cancelButton = QPushButton("Выход") #QCoreApplication.translate('Lining trip/options/cancel button', 'Quit'))
        processButton.clicked.connect(self.__selectProgramTaskFile)
        cancelButton.clicked.connect(self.__state.cancel)
        processButton.setProperty("optionsWindowPushButton", True)
        cancelButton.setProperty("optionsWindowPushButton", True)

        layout = QGridLayout()
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        for column in range(8):
            layout.setColumnStretch(column, 1)

        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        #layout.addWidget(QLabel('application/lining/options'), 0, 2, 1, 4)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining trip/options/view', 'Program task:')), 1, 2, 1, 1)
        layout.addWidget(self.__programTaskSelector, 1, 3, 1, 3)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining trip/options/view', 'Направление выправки')), 2, 2, 1, 1)
        layout.addWidget(self.__picketDirection, 2, 3, 1, 3)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining trip/options/view', 'Start picket')), 3, 2, 1, 1)
        layout.addWidget(self.__startPicket, 3, 3, 1, 3)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining trip/options/view', 'Прижим')), 4, 2, 1, 1)
        layout.addWidget(self.__pressRail, 4, 3, 1, 3)
        layout.addWidget(self.__autoBranchCheckBox, 5, 3, 1, 3)
        layout.addWidget(processButton, 6, 2, 1, 4)
        layout.addWidget(cancelButton, 7, 2, 1, 4)

    def __setStartPicket(self):
        # self.__startPicket.setValue(self.__programTask.options.start_picket.meters)
        # self.__picketDirection.setCurrentText(QCoreApplication.translate('Travelling/PicketDirection', self.__programTask.options.picket_direction.name))
        pass

    def __onProgramTaskChanged(self, path: str) ->None:
        try:
            self.__programTask = ProgramTaskCalculationResultDto_from_archive(zipfile.ZipFile(self.__programTaskSelector.filepath(), 'r'))
        except Exception as error:
            QMessageBox.critical(self, QCoreApplication.translate('Lining trip/options/view', 'Read program task file error'), str(error))
            return        
        # self.__setStartPicket()
        self.__startPicket.setValue(self.__programTask.options.start_picket.meters)
        self.__picketDirection.setCurrentText(QCoreApplication.translate('Travelling/PicketDirection', self.__programTask.options.picket_direction.name))
        self.__pressRail.setCurrentText(QCoreApplication.translate('Travelling/BaseRail', self.__programTask.options.measuring_trip.options.press_rail.name))

    def __onPicketDirectionChanged(self, index: int) ->None:
        if self.__programTask is not None:
            pass

    def __selectProgramTaskFile(self) ->None:
        try:
            # programTask = ProgramTaskCalculationResultDto_from_archive(zipfile.ZipFile(self.__programTaskSelector.filepath(), 'r'))
            if self.__programTask is None:
                QMessageBox.critical(self, QCoreApplication.translate('Lining trip/options/view', 'Read program task file error'), QCoreApplication.translate('Lining trip/options/view', 'Program task was not selected'))
                return
            self.__state.start.emit(LiningTripOptionsDto(
                filename = Path(self.__programTaskSelector.filepath()).name,
                program_task = self.__programTask, 
                start_picket = LocationVector1D(self.__startPicket.value()),
                picket_direction = self.__picketDirection.currentData(),
                press_rail = self.__pressRail.currentData(),
                auto_branching = self.__autoBranchCheckBox.isChecked(),
                current_picket = LocationVector1D(self.__startPicket.value()) ))
        except Exception as error:
            QMessageBox.critical(self, QCoreApplication.translate('Lining trip/options/view', 'Read program task file error'), str(error))
            return

# класс переделан из 'продолжить выправку' в 'просмотр результатов выправки'
class ContinueLiningOptionsView(QWidget):
    passDataSignal = Signal(LiningTripResultDto_from_archive)
    def __init__(self, state: ContinueLiningOptionsState, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__state: ContinueLiningOptionsState = state
        self.__liningTripSelector = FileSelector('*.alt')
        self.__window = Window("Просмотр результатов выправки")

        processButton = QPushButton(QCoreApplication.translate('Lining trip/options/process button', 'Process'))
        processButton.setProperty("optionsWindowPushButton", True)
        cancelButton = QPushButton("Выход") #QCoreApplication.translate('Lining trip/options/cancel button', 'Quit'))
        cancelButton.setProperty("optionsWindowPushButton", True)
        processButton.clicked.connect(self.__selectProgramTaskFile)
        cancelButton.clicked.connect(self.__state.cancel)
        layout = QGridLayout()
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        for column in range(8):
            layout.setColumnStretch(column, 1)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        #layout.addWidget(QLabel('application/lining/options'), 0, 2, 1, 4)
        layout.addWidget(QLabel("Результат выправки"),1, 2, 1, 1) #QCoreApplication.translate('Lining trip/options/view', 'Lining trip:')), 1, 2, 1, 1)
        layout.addWidget(self.__liningTripSelector, 1, 3, 1, 3)
        layout.addWidget(processButton, 5, 2, 1, 4)
        layout.addWidget(cancelButton, 6, 2, 1, 4)

    def __selectProgramTaskFile(self) ->None:
        try:
            result = LiningTripResultDto_from_archive(zipfile.ZipFile(self.__liningTripSelector.filepath(), 'r'))
            #self.passDataSignal.emit(result)
            #self.__state.start.emit(result.options)
                #LiningTripResultDto_from_archive(zipfile.ZipFile(self.__liningTripSelector.filepath(), 'r')).options)
            self.showLiningResultView = ShowLiningResult(result)
            self.showLiningResultView.showFullScreen()             #show()
        except Exception as error:
            QMessageBox.critical(self,
                                 QCoreApplication.translate('Lining trip/options/view', 'Read program task file error'),
                                 str(error))
            return

    # def __selectProgramTaskFile(self) ->None:
    #     try:
    #         self.__state.start.emit(LiningTripResultDto_from_archive(zipfile.ZipFile(self.__liningTripSelector.filepath(), 'r')).options)
    #     except Exception as error:
    #         print(traceback.format_exc())
    #         QMessageBox.critical(self, QCoreApplication.translate('Lining trip/options/view', 'Read program task file error'), str(error))
    #         return


# Возобновить отвод
class EmergencyExtractionRecoveryOptionsView(QWidget):
    def __init__(self, state: EmergencyExtractionRecoveryOptionsState, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__state: EmergencyExtractionRecoveryOptionsState = state
        self.__liningTripSelector = FileSelector('*.aex')
        self.__window = Window("Возобновить отвод")
        processButton = QPushButton(QCoreApplication.translate('Lining trip/options/process button', 'Process'))
        processButton.setProperty("optionsWindowPushButton", True)
        cancelButton = QPushButton("Выход") #QCoreApplication.translate('Lining trip/options/cancel button', 'Cancel'))
        cancelButton.setProperty("optionsWindowPushButton", True)
        processButton.clicked.connect(self.__selectProgramTaskFile)
        cancelButton.clicked.connect(self.__state.cancel)

        layout = QGridLayout()
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        for column in range(8):
            layout.setColumnStretch(column, 1)

        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        #layout.addWidget(QLabel('application/lining/options'), 0, 2, 1, 4)
        layout.addWidget(QLabel(QCoreApplication.translate('Lining trip/options/view', 'Emergenct extraction:')), 1, 2, 1, 1)
        layout.addWidget(self.__liningTripSelector, 1, 3, 1, 3)
        layout.addWidget(processButton, 5, 2, 1, 4)
        layout.addWidget(cancelButton, 6, 2, 1, 4)
    def __selectProgramTaskFile(self) ->None:
        try:
            self.__state.start.emit(EmergencyExtractionResultDto_from_archive(zipfile.ZipFile(self.__liningTripSelector.filepath(), 'r')).options.lining_trip.options)
        except Exception as error:
            print(traceback.format_exc())
            QMessageBox.critical(self, QCoreApplication.translate('Lining trip/options/view', 'Read program task file error'), str(error))
            return


# проверка стартовой загрузки
def profile(func):
    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.txt'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result
    return wrapper

#@profile



# Выправка
class LiningProcess(QWidget):
    #pathAdjustmentActivated: Signal = Signal()
    #endProgramTask: Signal = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        # measurmentsModel: AbstractPositionedTableModel = self.__state.measurements()
        # self.__measurmentsByPicketModel = PicketPositionedTableModel(self.options.picket_direction, self.options.start_picket.meters, self)
        # self.__measurmentsByPicketModel.setSourceModel(measurmentsModel)
        # ========================================
       
        self.liningInProcessFlag = False              # флаг "Выправка запущена"
        self.confirmationFinishLining = False
        self.isAutoBranching = False
        self.isUIBlocked = False
        self.isEmergencyExtraction = False
        self.auto_branching_txt = 'Идет автоматический отвод'

        #self.layout: QStackedLayout = QStackedLayout()
        #self.layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
        self.lininigViewWidget: QWidget = QWidget()
        self.emergencyExtractionViewWidget: QWidget = QWidget()
        

        self.tooltip =  QLabel('Для начала выправки нажмите (Старт или F4)')
        self.tooltip.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        self.__control_unit_connection_label = QLabel('---')
        self.__processor_strelograph_work_label = QLabel('---')
        self.__processor_strelograph_work_label.setObjectName("sensorsValue")
        self.__processor_plan_prj_label = QLabel('---')
        self.__processor_plan_prj_label.setObjectName("sensorsValue")
        self.__processor_indicator_lining_label = QLabel("---")
        self.__processor_indicator_lining_label.setObjectName("sensorsValue")
        self.__processor_indicator_lifting_left_label = QLabel('---')
        self.__processor_indicator_lifting_left_label.setObjectName("sensorsValue")
        self.__processor_indicator_lifting_right_label = QLabel('---')
        self.__processor_indicator_lifting_right_label.setObjectName("sensorsValue")
        self.__processor_pendulum_work_label = QLabel('---')
        self.__processor_pendulum_work_label.setObjectName("sensorsValue")
        self.__processor_cant_prj_label = QLabel('---')
        self.__processor_cant_prj_label.setObjectName("sensorsValue")
        self.__processor_left_sagging_label = QLabel('---')
        self.__processor_left_sagging_label.setObjectName("sensorsValue")
        self.__processor_right_sagging_label = QLabel('---')
        self.__processor_right_sagging_label.setObjectName("sensorsValue")
        self.__processor_project_sagging_label = QLabel('---')
        self.__processor_project_sagging_label.setObjectName("sensorsValue")
       


    def initLiningProcess(self, state: LiningProcessState, parent: QWidget = None):

        self.__state: LiningProcessState = state
        self.options: LiningTripOptionsDto = self.__state.options()

        self.position_unit = self.__state.position_unit()
        #self.__picket_position_model.write(self.__programTaskByPicketModel.startPicket())
        self.__picket_position_model = PicketPositionUnit(self.position_unit, self.options.picket_direction, self.options.start_picket.meters)
        
        #self.__disconnectSignals()

        # vertical line
        self.__position_line_model = SingleLineModel(self.__picket_position_model.read())

        self.programTaskModel = ReducedStepIndexedPositionedModel(
                                step= self.options.program_task.calculated_task.step, 
                                data= self.options.program_task.calculated_task.data)
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.program_task.options.picket_direction, 
                                                                     self.options.program_task.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(self.programTaskModel)

        self.__direction_multiplier: int = self.options.picket_direction.multiplier()
        self.position_min, self.position_max = self.__programTaskByPicketModel.minmaxPosition()

        self.__render()
        self.__connectSignals()
        return self.lininigViewWidget

    
    def initEmergencyExtractionProcessView(self, 
                                           state: EmergencyExtractionProcessState, 
                                           parent: QWidget = None):

        self.__state: EmergencyExtractionProcessState = state
        self.extraction_options: EmergencyExtractionOptionsDto = self.__state.options()
        self.options: LiningTripOptionsDto = self.extraction_options.lining_trip.options
        self.__step = self.extraction_options.extraction_trajectory.step.meters

        self.isEmergencyExtraction = True

        self.position_unit = self.__state.position_unit()
        self.__picket_position_model = self.__state.picket_position_unit()
        self.__extraction_trajectory_model: QStandardItemModel = QStandardItemModel()
        self.__extraction_trajectory_model.setColumnCount(6)



        #self.__disconnectSignals()
        # vertical line
        self.__position_line_model = SingleLineModel(self.__picket_position_model.read())


        self.programTaskModel = ReducedStepIndexedPositionedModel(
            step= self.extraction_options.extraction_trajectory.step, 
            data= self.extraction_options.extraction_trajectory.data)
        self.__programTaskByPicketModel = PicketPositionedTableModel(
            self.options.program_task.options.picket_direction,
            self.options.program_task.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(self.programTaskModel)


        self.__direction_multiplier: int = self.options.picket_direction.multiplier()
        self.position_min, self.position_max = self.__programTaskByPicketModel.minmaxPosition()


        self.__render()
        self.__connectSignals()
        # Запускаем алгоритм выправки
        self.__state.lining_processor().start()
        # Запускаем запись показаний датчиков
        self.__state.measurements_writer().start()

        return self.emergencyExtractionViewWidget
        
    
    def __connectSignals(self):

        self.__picket_position_model.changed.connect(self.__updatePositionSingleLineModel)
        self.__picket_position_model.changed.connect(self.__position_line_model.setPosition)
        
        #Автоматический отвод
        self.__state.auto_branching().started.connect(self.__auto_branch_started)
        self.__state.auto_branching().stopped.connect(self.__auto_branch_stopped)

        self.__state.units().event_dispatcher().traced_event_received.connect(self.__onControlUnitConnectChanged)
        self.__state.units().get_read_only_unit('strelograph_work').changed.connect(self.__onStrelographWorkChanged)
        self.__state.units().get_read_only_unit('pendulum_work').changed.connect(self.__onPendulumWorkChanged)
        self.__state.units().get_read_only_unit('sagging_left').changed.connect(self.__onSaggingLeftChanged)
        self.__state.units().get_read_only_unit('sagging_right').changed.connect(self.__onSaggingRightChanged)
        self.__state.units().get_read_only_unit('satellite').changed.connect(self.__lining_difference_model_changed_satellite)
        # "Натурное значение контрольного маятника;"
        self.__state.units().get_read_only_unit('pendulum_control').changed.connect(self.__pendulum_control_difference_model_changed_real)
        self.__state.units().discrete_signals_container().changed.connect(self.__updateDiscreteSignals)

        self.__state.plan_project_machine().changed.connect(self.__onPlanProjectMachineChanged)
        self.__state.plan_delta_unit().changed.connect(self.__onIndicatorLiningChanged)
        self.__state.vozv_project_work_provider().changed.connect(self.__onVozvProjectWorkChanged)
        # "Проектное значение контрольного маятника;"
        self.__state.vozv_project_control_unit().changed.connect(self.__pendulum_control_difference_model_changed_prj)

        self.__state.prof_project_machine().changed.connect(self.__onSaggingPrjChanged)
        self.__state.indicator_lifting_left().changed.connect(self.__onIndicatorLiftingLeftChanged)
        self.__state.indicator_lifting_right().changed.connect(self.__onIndicatorLiftingRightChanged)
        self.__state.indicator_lining().changed.connect(self.__lining_difference_model_changed)
        self.__state.indicator_pendulum_work().changed.connect(self.__pendulum_work_difference_model_changed)
        self.__state.indicator_pendulum_control().changed.connect(self.__pendulum_control_difference_model_changed)
        self.__state.indicator_lifting_left().changed.connect(self.__left_lifting_difference_model_changed)
        self.__state.indicator_lifting_right().changed.connect(self.__right_lifting_difference_model_changed)

    def disconnectSignals(self):
        
        self.__picket_position_model.changed.disconnect(self.__updatePositionSingleLineModel)
        self.__picket_position_model.changed.disconnect(self.__position_line_model.setPosition)

        self.__state.auto_branching().started.disconnect(self.__auto_branch_started)
        self.__state.auto_branching().stopped.disconnect(self.__auto_branch_stopped)

        self.__state.units().event_dispatcher().traced_event_received.disconnect(self.__onControlUnitConnectChanged)
        self.__state.units().get_read_only_unit('strelograph_work').changed.disconnect(self.__onStrelographWorkChanged)
        self.__state.units().get_read_only_unit('pendulum_work').changed.disconnect(self.__onPendulumWorkChanged)
        self.__state.units().get_read_only_unit('sagging_left').changed.disconnect(self.__onSaggingLeftChanged)
        self.__state.units().get_read_only_unit('sagging_right').changed.disconnect(self.__onSaggingRightChanged)
        self.__state.units().get_read_only_unit('satellite').changed.disconnect(self.__lining_difference_model_changed_satellite)
        # "Натурное значение контрольного маятника;"
        self.__state.units().get_read_only_unit('pendulum_control').changed.disconnect(self.__pendulum_control_difference_model_changed_real)
        self.__state.units().discrete_signals_container().changed.disconnect(self.__updateDiscreteSignals)

        self.__state.plan_project_machine().changed.disconnect(self.__onPlanProjectMachineChanged)
        self.__state.plan_delta_unit().changed.disconnect(self.__onIndicatorLiningChanged)
        self.__state.vozv_project_work_provider().changed.disconnect(self.__onVozvProjectWorkChanged)
        # "Проектное значение контрольного маятника;"
        self.__state.vozv_project_control_unit().changed.disconnect(self.__pendulum_control_difference_model_changed_prj)

        self.__state.prof_project_machine().changed.disconnect(self.__onSaggingPrjChanged)
        self.__state.indicator_lifting_left().changed.disconnect(self.__onIndicatorLiftingLeftChanged)
        self.__state.indicator_lifting_right().changed.disconnect(self.__onIndicatorLiftingRightChanged)
        self.__state.indicator_lining().changed.disconnect(self.__lining_difference_model_changed)
        self.__state.indicator_pendulum_work().changed.disconnect(self.__pendulum_work_difference_model_changed)
        self.__state.indicator_pendulum_control().changed.disconnect(self.__pendulum_control_difference_model_changed)
        self.__state.indicator_lifting_left().changed.disconnect(self.__left_lifting_difference_model_changed)
        self.__state.indicator_lifting_right().changed.disconnect(self.__right_lifting_difference_model_changed)

    def __render(self):


        grid = QGridLayout()
        grid.setSpacing(0)
        #########################################  top chart (plan_delta, сдвижки) ####################3################3
        column_name_plan_delta = 'plan_delta'
        chart_value_range_plan_delta: Tuple[float, float] = self.programTaskModel.minmaxValueByColumn(column_name_plan_delta)
        chart_value_range_length_plan_delta = chart_value_range_plan_delta[1] - chart_value_range_plan_delta[0]
        chart_value_min_plan_delta: float = chart_value_range_plan_delta[
                                                0] - 0.00001 - 0.05 * chart_value_range_length_plan_delta
        chart_value_max_plan_delta: float = chart_value_range_plan_delta[
                                                1] + 1.00001 + 0.05 * chart_value_range_length_plan_delta
        self.seriesPlanDelta = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                     self.programTaskModel.modelColumnIndexAtName(column_name_plan_delta),
                                                     QCoreApplication.translate(
                                                         'Lining trip/process/view/charts/program task',
                                                         column_name_plan_delta))
        # ========================================
        
        positionLineSeriesPlanDelta = DynamicLineSeries(self.__position_line_model, 0, 1,
                                                            QCoreApplication.translate(
                                                                'Lining trip/process/view/charts/measurements',
                                                                'position'))
        positionLineSeriesPlanDelta.setPen(QPen(Qt.GlobalColor.magenta, 2))
        # верхний отдельный график
        chartPlanDelta = HorizontalChart((self.position_min, self.position_max),
                                                  self.options.picket_direction == PicketDirection.Backward,
                                                  (chart_value_min_plan_delta, chart_value_max_plan_delta), False,
                                                  areaSeries=self.seriesPlanDelta, areaSeriesColor="#41FA00",
                                                  titleLeftSide="С д в и г и",
                                                  x_tick=100, y_tick=10,
                                                  xGridLineColor="grey", yGridLineColor="grey")
        chartPlanDelta.setMargins(QMargins(0, 0, 0, 0))
        chartPlanDelta.legend().hide()
        chartPlanDelta.addSeries(positionLineSeriesPlanDelta)
        positionLineSeriesPlanDelta.attachAxis(chartPlanDelta.positionAxis())
        positionLineSeriesPlanDelta.attachAxis(chartPlanDelta.valueAxis())
        chartPlanDelta.layout().setContentsMargins(0, 0, 0, 0)
        chartPlanDelta.setMaximumHeight(150)
        chartViewPlanDelta = QChartView(chartPlanDelta)
        chartViewPlanDelta.setFocusPolicy(Qt.NoFocus)
        chartViewPlanDelta.chart().setBackgroundBrush(QBrush("#black"))
        chartViewPlanDelta.setRenderHint(QPainter.Antialiasing)
        grid.addWidget(chartViewPlanDelta, 0, 0, 1, 7)
        # =============================================== infopanel =============================================================
        information_panel_first = QWidget()
        information_panel_first.setMaximumHeight(40)
        information_panel_first_layout = QHBoxLayout()
        information_panel_first_layout.setSpacing(0)
        information_panel_first.setLayout(information_panel_first_layout)
        information_panel_first.layout().setContentsMargins(0, 0, 0, 0)
        information_panel_first.setProperty("topInfoPanel", True)
        information_panel_first_layout.addWidget(CurrentPicketLabel(self.__picket_position_model))
        information_panel_first_layout.addStretch(1)
        information_panel_first_layout.addWidget(PicketDirectionLabel(self.options.picket_direction))
        information_panel_first_layout.addStretch(1)
        information_panel_first_layout.addWidget(
            # BaseRailLabel(self.options.program_task.options.measuring_trip.options.base_rail)
            PressRailLabel(self.options.press_rail)
        )
        information_panel_first_layout.addStretch(1)
        information_panel_first_layout.addWidget(CurrentTimeLabel())
        information_panel_first_layout.addStretch(1)
        information_panel_first_layout.addWidget(QLabel("Связь с БУ: "))
        
        information_panel_first_layout.addWidget(self.__control_unit_connection_label)
        information_panel_first_layout.addStretch(1)
        #
        information_panel_second = QWidget()
        information_panel_second.setMaximumHeight(40)
        information_panel_second_layout = QHBoxLayout()
        information_panel_second_layout.setSpacing(0)
        information_panel_second.setLayout(information_panel_second_layout)
        information_panel_second.layout().setContentsMargins(0, 0, 0, 0)
        information_panel_second.setProperty("topInfoPanel", True)
        information_panel_second_layout.addWidget(PassedMetersLabel(self.position_unit))
        information_panel_second_layout.addStretch(1)
        information_panel_second_layout.addWidget(
            RailwayInfoPanel(self.options.program_task.options.measuring_trip.options.track_title), 2)
        information_panel_second_layout.addStretch(1)

    
        information_panel_second_layout.addWidget(self.tooltip)
        information_panel_second_layout.addStretch(1)

        if self.isEmergencyExtraction:
            self.tooltip.hide()

        information_panel_second_layout.addWidget(ElapsedTimeLabel())
        information_panel_second_layout.addStretch(1)
        #information_panel_second_layout.addWidget(ProgramTaskFileName(""))
        #information_panel_second_layout.addStretch(1)
        #self.meters_left_label = QLabel("Осталось менее 10 метров  ")
        # ==============================================
    
        grid.addWidget(information_panel_first, 1, 0, 1, 7)
        grid.addWidget(information_panel_second, 2, 0, 1, 7)
        #===========================================================================================================
        self.sensors_charts_grid = QGridLayout()
        grid.addLayout(self.sensors_charts_grid, 3, 0, 7, 2)

        sensor_box_widget1 = QWidget()
        sensor_box_layout1 = QVBoxLayout()
        sensor_box_widget1.setLayout(sensor_box_layout1)
        sensor_box_widget1.setProperty("sensorWidgetBox", True)
        sensor_label_work_strelograph = QLabel("Рабочий стрелограф")
        sensor_label_work_strelograph.setObjectName("labelWorkStrelograph")
        sensor_label_project = QLabel("Проект")
        sensor_label_project.setObjectName("labelProject")

        
        sensor_box_layout1.addWidget(sensor_label_work_strelograph)
        sensor_box_layout1.addWidget(self.__processor_strelograph_work_label)
        sensor_box_layout1.addWidget(sensor_label_project)
        sensor_box_layout1.addWidget(self.__processor_plan_prj_label)
        self.sensors_charts_grid.addWidget(sensor_box_widget1, 0, 0)
        #
        sensor_box_widget2 = QWidget()
        sensor_box_widget2.setProperty("sensorWidgetBox", True)
        sensor_box_layout2 = QVBoxLayout()
        sensor_box_widget2.setLayout(sensor_box_layout2)
        sensor_label_shifts = QLabel("Сдвиги")
        sensor_label_shifts.setObjectName("labelWorkStrelograph")
      
        sensor_box_layout2.addWidget(sensor_label_shifts)
        sensor_box_layout2.addWidget(self.__processor_indicator_lining_label)
        self.sensors_charts_grid.addWidget(sensor_box_widget2, 1, 0)
        #
        sensor_box_widget3 = QWidget()
        sensor_box_widget3.setProperty("sensorWidgetBox", True)
        sensor_box_layout3 = QVBoxLayout()
        sensor_box_widget3.setLayout(sensor_box_layout3)
        sensor_label_work_level = QLabel("Возвышение рабочее")
        sensor_label_work_level.setObjectName("labelWorkLevel")
        sensor_label_vozv = QLabel("Возвышение проект")
        sensor_label_vozv.setObjectName("labelProject")

        sensor_box_layout3.addWidget(sensor_label_work_level)
        sensor_box_layout3.addWidget(self.__processor_pendulum_work_label)
        sensor_box_layout3.addWidget(sensor_label_vozv)
        sensor_box_layout3.addWidget(self.__processor_cant_prj_label)
        self.sensors_charts_grid.addWidget(sensor_box_widget3, 2, 0)
        #
        sensor_box_widget4 = QWidget()
        sensor_box_widget4.setProperty("sensorWidgetBox", True)
        sensor_box_layout4 = QVBoxLayout()
        sensors_sagging_hbox = QHBoxLayout()
        sensor_box_widget4.setLayout(sensor_box_layout4)
        sensor_label_sagging = QLabel("Просадки")
        sensor_label_sagging.setObjectName("sensorTitle")
        sensor_label_sagging_left = QLabel("левые")
        sensor_label_sagging_right = QLabel("правые")
        sensor_label_sagging_prj = QLabel("проект")
        sensor_label_sagging_left.setObjectName("saggingLeft")
        sensor_label_sagging_right.setObjectName("saggingRight")
        sensor_label_sagging_prj.setObjectName("labelProject")
        sensors_labels_sagging_hbox = QHBoxLayout()
        sensors_labels_sagging_hbox.addWidget(sensor_label_sagging_left)
        sensors_labels_sagging_hbox.addWidget(sensor_label_sagging_right)
        sensors_labels_sagging_hbox.addWidget(sensor_label_sagging_prj)
     
        sensors_sagging_hbox.addWidget(self.__processor_left_sagging_label)
        sensors_sagging_hbox.addWidget(self.__processor_right_sagging_label)
        sensors_sagging_hbox.addWidget(self.__processor_project_sagging_label)
        sensor_box_layout4.addWidget(sensor_label_sagging)
        sensor_box_layout4.addLayout(sensors_labels_sagging_hbox)
        sensor_box_layout4.addLayout(sensors_sagging_hbox)
        self.sensors_charts_grid.addWidget(sensor_box_widget4, 3, 0)
        #
        sensor_box_widget5 = QWidget()
        sensor_box_widget5.setProperty("sensorWidgetBox", True)
        sensor_box_layout5 = QVBoxLayout()
        sensor_lifting_hbox = QHBoxLayout()
        sensor_box_widget5.setLayout(sensor_box_layout5)
        sensor_label_lifting = QLabel("Подъёмка")
        sensor_label_lifting.setObjectName("sensorTitle")
        labels_lifting_hbox = QHBoxLayout()
        label_lifting_left = QLabel("левая")
        label_lifting_left.setObjectName("saggingLeft")        # liftingLeft
        label_lifting_right = QLabel("правая")
        label_lifting_right.setObjectName("saggingRight")     # liftingRight
        labels_lifting_hbox.addWidget(label_lifting_left)
        labels_lifting_hbox.addWidget(label_lifting_right)

        sensor_lifting_hbox.addWidget(self.__processor_indicator_lifting_left_label)
        sensor_lifting_hbox.addWidget(self.__processor_indicator_lifting_right_label)
        sensor_box_layout5.addWidget(sensor_label_lifting)
        sensor_box_layout5.addLayout(labels_lifting_hbox)
        sensor_box_layout5.addLayout(sensor_lifting_hbox)
        self.sensors_charts_grid.addWidget(sensor_box_widget5, 4, 0)

        if not self.isEmergencyExtraction:
            self.__liningCharts()
        else: 
            self.__emergencyExtractionCharts()

        markers_chart = MarkersChart(options = self.options.program_task.options, verticalModel=self.__position_line_model, parent=self).getChart()
        self.sensors_charts_grid.addWidget(markers_chart, 5, 1, 1, 5)


        
        self.chartSlideWindowUpdater = ChartSlidingWindowProvider(
            position=self.__picket_position_model,
            viewes=self.program_task_chart_viewes,
            charts=self.program_task_charts,
            windowSize=(1, 20),
            mappers=self.program_task_chart_mappers,
            windowPoints=(100, 250),
            isVertical=False,
            program_task_by_picket=self.__programTaskByPicketModel)

    
        self.__indicators()
        self.__infomarkers()
        self.__buttons()
        self.__equalizer()

        #============================================= 3я колонка (с приборами)================================
        gauges_left_column_widget = QWidget()
        gauges_left_column_layout = QVBoxLayout()
        gauges_left_column_widget.setLayout(gauges_left_column_layout)
        gauges_left_column_layout_1 = QHBoxLayout()
        gauges_left_column_layout_1.addWidget(self.__left_lifting_indicator)
        gauges_left_column_layout_1.addWidget(self.__right_lifting_indicator)
        gauges_left_column_layout_2 = QHBoxLayout()
        gauges_left_column_layout_2.addWidget(self.label_base_rail)
        gauges_left_column_layout_2.addWidget(self.label_clamp)
        gauges_left_column_layout_3 = QHBoxLayout()
        gauges_left_column_layout_3.addWidget(self.button_f1)
        gauges_left_column_layout_3.addWidget(self.button_f3)
        gauges_left_column_layout_3.addWidget(self.button_f4)
        gauges_left_column_layout_3.addWidget(self.button_f5)
      
        gauges_left_column_layout_4 = QHBoxLayout()
        gauges_left_column_layout_4.addWidget(self.button_f6)
        gauges_left_column_layout_4.addWidget(self.button_quit)
        gauges_left_column_layout_4.addWidget(self.button_edit)
      
        gauges_left_column_layout.addLayout(gauges_left_column_layout_1, 2)
        gauges_left_column_layout.addLayout(gauges_left_column_layout_2, 0)
        gauges_left_column_layout.addLayout(gauges_left_column_layout_3, 0)
        gauges_left_column_layout.addLayout(gauges_left_column_layout_4, 0)
        gauges_left_column_layout.addWidget(self.__work_strelograph_indicator, 3)
        #gauges_left_column_widget.setFocusPolicy(Qt.NoFocus)
        grid.addWidget(gauges_left_column_widget, 3, 2, 8, 4)

        # ============================================= 4я колонка (с приборами)================================
        gauges_right_column_widget = QWidget()
        gauges_right_column_layout = QVBoxLayout()
        gauges_right_column_widget.setLayout(gauges_right_column_layout)
        gauges_right_column_layout.addWidget(self.__work_pendulum_indicator, 1)
        gauges_right_column_layout.addWidget(self.__pendulum_control_indicator, 1)
        gauges_right_column_layout.addWidget(self.equalizer, 1)
        grid.addWidget(gauges_right_column_widget, 3, 6, 8, 1)
        #
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 6)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 1)
        grid.setColumnStretch(5, 1)
        grid.setColumnStretch(6, 3)
        #
        grid.setRowStretch(0, 2)
        grid.setRowStretch(1, 0)
        grid.setRowStretch(2, 0)
        grid.setRowStretch(3, 1)
        grid.setRowStretch(4, 1)
        grid.setRowStretch(5, 1)
        grid.setRowStretch(6, 1)
        grid.setRowStretch(7, 1)
        grid.setRowStretch(8, 1)
        grid.setRowStretch(9, 1)


        if not self.isEmergencyExtraction:
            self.lininigViewWidget.setLayout(grid)
        else: self.emergencyExtractionViewWidget.setLayout(grid)
        #self.layout.addWidget(self.__lininigViewWidget)
        #self.layout.setCurrentIndex(0)

    
    def __liningCharts(self):

        ######################################  charts  #############################################################
        program_task_charts_column_names: List[str] = [
            ['plan_fact','plan_prj'],
            ['plan_delta'],
            ['vozv_fact', 'vozv_prj'],
            ['prof_fact_left', 'prof_fact_right', 'prof_prj'],
            ['prof_delta_left', 'prof_delta_right']
        ]
        self.program_task_charts: List[AbstractChartOrientationMixin] = []
        self.program_task_chart_mappers: List[QVXYModelMapper] = []
        self.program_task_chart_viewes: List[QChartView] = []

        for column_name in program_task_charts_column_names:
            if column_name == ['plan_delta']:
                chart_value_range: Tuple[float, float] = self.programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                self.chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
                self.chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
                chart = HorizontalChart((self.position_min, self.position_max),
                                                    self.options.picket_direction == PicketDirection.Backward,
                                                    (self.chart_value_min, self.chart_value_max), False,
                                                    areaSeries=self.seriesPlanDelta, areaSeriesColor="#41FA00",
                                                    x_tick=100, y_tick=10,
                                                    xGridLineColor="grey", yGridLineColor="grey",
                                                    XAxisHideLabels=True)
                chart.name = column_name[0]
            elif column_name == ['plan_fact','plan_prj'] or column_name == ['vozv_fact', 'vozv_prj'] or column_name == ['prof_delta_left', 'prof_delta_right']:
                chart_value_range0: Tuple[float, float] = self.programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range1: Tuple[float, float] = self.programTaskModel.minmaxValueByColumn(column_name[1])
                chart_value_range = (min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                self.chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
                self.chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
                self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                     self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                     QCoreApplication.translate(
                                                         'Lining trip/process/view/charts/program task', column_name[0]))
                self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                     self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                     QCoreApplication.translate(
                                                         'Lining trip/process/view/charts/program task', column_name[1]))

                if column_name == ['plan_fact','plan_prj']:
                    self.series0.setPen(QPen(QColor("#41FA00"), 2))
                    self.series1.setPen(QPen(QColor("#ff0000"), 2))
                    XAxisHideLabels_value = False
                    is_y_zero_axe_visible_value = False
                elif column_name == ['vozv_fact', 'vozv_prj']:
                    self.series0.setPen(QPen(Qt.GlobalColor.cyan, 2))
                    self.series1.setPen(QPen(QColor("#ff0000"), 2))
                    XAxisHideLabels_value = True
                    is_y_zero_axe_visible_value = True
                elif column_name == ['prof_delta_left', 'prof_delta_right']:
                    self.series0.setPen(QPen(QColor("#27B14A"), 2))                        # F9D98A
                    self.series1.setPen(QPen(Qt.GlobalColor.white, 2))                  # darkBlue
                    is_y_zero_axe_visible_value = True
                chart = HorizontalChart( (self.position_min, self.position_max),
                                          self.options.picket_direction == PicketDirection.Backward,
                                          (self.chart_value_min, self.chart_value_max), False,
                                          series0 = [self.series0], series1 = [self.series1],
                                          x_tick=100, y_tick=10, title="",
                                          xGridLineColor="grey", yGridLineColor="grey",
                                          XAxisHideLabels=XAxisHideLabels_value,
                                          is_y_zero_axe_visible = is_y_zero_axe_visible_value)
                chart.name = column_name[0]

            elif column_name == ['prof_fact_left', 'prof_fact_right', 'prof_prj']:
                chart_value_range0: Tuple[float, float] = self.programTaskModel.minmaxValueByColumn(column_name[0])
                chart_value_range1: Tuple[float, float] = self.programTaskModel.minmaxValueByColumn(column_name[1])
                chart_value_range2: Tuple[float, float] = self.programTaskModel.minmaxValueByColumn(column_name[2])
                chart_value_range = (min(chart_value_range0[0], chart_value_range1[0], chart_value_range2[0]),
                                  max(chart_value_range0[1], chart_value_range1[1], chart_value_range2[1]))
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                self.chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
                self.chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
                self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
                self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
                self.series2 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                                 self.programTaskModel.modelColumnIndexAtName(column_name[2]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[2]))
                self.series0.setPen(QPen(QColor('#27B14A'), 2))
                self.series1.setPen(QPen(Qt.GlobalColor.white, 2))
                self.series2.setPen(QPen(QColor('#ff0000'), 2))
                chart = HorizontalChart((self.position_min, self.position_max),
                                         self.options.picket_direction == PicketDirection.Backward,
                                         (self.chart_value_min, self.chart_value_max), False,
                                         series0 = [self.series0], series1=[self.series1], series2=[self.series2],
                                         x_tick=100, y_tick=10,
                                         xGridLineColor="grey", yGridLineColor="grey",
                                         XAxisHideLabels=True, is_y_zero_axe_visible=True)
                chart.name = column_name[0]
            chart.column_names = column_name
            positionLineSeries = DynamicLineSeries(self.__position_line_model, 0, 1,
                                                     QCoreApplication.translate(
                                                         'Lining trip/process/view/charts/measurements', 'position'))
            positionLineSeries.setPen(QPen(Qt.GlobalColor.magenta, 2))

            chart.addSeries(positionLineSeries)
            positionLineSeries.attachAxis(chart.positionAxis())
            positionLineSeries.attachAxis(chart.valueAxis())

            chart.legend().hide()
            chart.layout().setContentsMargins(0, 0, 0, 0)
            chart.setMargins(QMargins(0,0,0,0))
            chart_view = QChartView(chart)
            #
            chart_view.setFocusPolicy(Qt.NoFocus)
            chart_view.chart().setBackgroundBrush(QBrush("#30B44"))
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setProperty("liningChartView", True)
            if column_name == ['plan_fact','plan_prj']:
                self.sensors_charts_grid.addWidget(chart_view, 0, 1, 1, 5)
            elif column_name == ["plan_delta"]:
                self.sensors_charts_grid.addWidget(chart_view, 1, 1, 1, 5)
            elif column_name == ['vozv_fact', 'vozv_prj']:
                self.sensors_charts_grid.addWidget(chart_view, 2, 1, 1, 5)
            elif column_name == ['prof_fact_left', 'prof_fact_right', 'prof_prj']:
                self.sensors_charts_grid.addWidget(chart_view, 3, 1, 1, 5)
            elif column_name == ['prof_delta_left', 'prof_delta_right']:
                self.sensors_charts_grid.addWidget(chart_view, 4, 1, 1, 5)

            self.program_task_chart_viewes.append(chart_view)
            self.program_task_charts.append(chart)



    def __emergencyExtractionCharts(self):
        ############################### НАЧАЛО 'Графики ОТВОДА' #############################################
        program_task_charts_columns: List[str] = [
            (['plan_fact', 'plan_prj'], ('plan_extraction', 1)),
            (['plan_delta'], ('plan_extraction', 2)),
            (['vozv_fact', 'vozv_prj'], ('vozv_extraction', 3)),
            (['prof_fact_left', 'prof_fact_right', 'prof_prj'], ('prof_extraction', 4)),
            (['prof_delta_left', 'prof_delta_right'], ('prof_extraction', 5))         # ['prof_delta']
        ]
        self.program_task_chart_viewes: List[QChartView] = []
        self.program_task_charts: List[QChartView] = []
        self.program_task_chart_mappers: List[QChartView] = []

        for idx, row in self.extraction_options.extraction_trajectory.data.iterrows():
            # position = step * self.extraction_options.extraction_trajectory.step.meters + options.program_task.options.measuring_trip.options.start_picket.meters
            position = self.options.start_picket.meters + self.__direction_multiplier * self.__step * idx
            self.__extraction_trajectory_model.appendRow([
                QStandardItem(f'{position}'),
                QStandardItem(f'{float(row["v1"])}'),
                QStandardItem(f'{float(row["v2"])}'),
                QStandardItem(f'{float(row["v3"])}'),
                QStandardItem(f'{float(row["v4"])}'),
                QStandardItem(f'{float(row["v5"])}')])

        for column_names, trajectory_model_index in program_task_charts_columns:
            minmax_charts_values: List[Tuple[float, float]] = [
                self.programTaskModel.minmaxValueByColumn(column_name) for column_name in column_names]
            chart_value_range: Tuple[float, float] = (
                min(minmax_charts_values, key=lambda minmax_value: minmax_value[0])[0],
                max(minmax_charts_values, key=lambda minmax_value: minmax_value[1])[1]
            )

            chart_value_range_length = chart_value_range[1] - chart_value_range[0]
            chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
            chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
            # графики датчиков
            series = [
                DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                  self.programTaskModel.modelColumnIndexAtName(column_name),
                                  QCoreApplication.translate('Lining trip/process/view/charts/program task',
                                                             column_name))
                for column_name in column_names
            ]
            # графики отвода
            trajectory = DynamicLineSeries(self.__extraction_trajectory_model,
                                           0, trajectory_model_index[1], trajectory_model_index[0])
            trajectory.setPen(QPen(QColor("#EBE330"), 2))
            position_line_series = DynamicLineSeries(self.__position_line_model, 0, 1, QCoreApplication.translate(
                'Lining trip/process/view/charts/measurements', 'position'))
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
            elif column_names == ['prof_delta_left', 'prof_delta_right']:   #'prof_delta']:
                series[0].setPen(QPen(QColor("#F9D98A"), 2))
                series[1].setPen(QPen(Qt.GlobalColor.darkBlue, 2))

            chart = HorizontalChart((self.position_min, self.position_max),
                                    self.options.picket_direction == PicketDirection.Backward,
                                    (chart_value_min, chart_value_max),
                                    valueReverse=False, series0=(series + [trajectory]),
                                    x_tick=100, y_tick=10,
                                    xGridLineColor="grey", yGridLineColor="grey"
                                    )
            chart.addSeries(position_line_series)
            chart.legend().setLabelColor(QColor('white'))
            position_line_series.attachAxis(chart.positionAxis())
            position_line_series.attachAxis(chart.valueAxis())
            self.program_task_charts.append(chart)
            positionLineSeries = DynamicLineSeries(self.__position_line_model, 0, 1,
                                                   QCoreApplication.translate(
                                                       'Lining trip/process/view/charts/measurements', 'position'))
            positionLineSeries.setPen(QPen(Qt.GlobalColor.magenta, 2))
            chart.addSeries(positionLineSeries)
            positionLineSeries.attachAxis(chart.positionAxis())
            positionLineSeries.attachAxis(chart.valueAxis())
            chart.legend().hide()
            chart.layout().setContentsMargins(0, 0, 0, 0)
            chart.setMargins(QMargins(0, 0, 0, 0))
            chart_view = QChartView(chart)
            #
            chart_view.setFocusPolicy(Qt.NoFocus)
            chart_view.chart().setBackgroundBrush(QBrush("#30B44"))
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setProperty("liningChartView", True)
            if column_names == ['plan_fact', 'plan_prj']:
                self.sensors_charts_grid.addWidget(chart_view, 0, 1, 1, 5)
            elif column_names == ["plan_delta"]:
                self.sensors_charts_grid.addWidget(chart_view, 1, 1, 1, 5)
            elif column_names == ['vozv_fact', 'vozv_prj']:
                self.sensors_charts_grid.addWidget(chart_view, 2, 1, 1, 5)
            elif column_names == ['prof_fact_left', 'prof_fact_right', 'prof_prj']:
                self.sensors_charts_grid.addWidget(chart_view, 3, 1, 1, 5)
            elif column_names == ['prof_delta_left', 'prof_delta_right']:
                self.sensors_charts_grid.addWidget(chart_view, 4, 1, 1, 5)
            self.program_task_chart_viewes.append(chart_view)
        ############################### конец 'Графики ОТВОДА' #############################################


    def __indicators(self):
         ################################### Индикаторы ######################################################################
        # Cтрелограф с тремя кнопками (у Навигатора - левый большой), ex ArrowPointerStrelographWorkIndicator
        self.__work_strelograph_indicator = ArrowPointerIndicator(chunks=[
            (4, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (1, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (4, Qt.GlobalColor.white),
        ], lineWidth=1000000, indicatorType='strelographWorkIndicator')
        #self.__state.units().get_readwrite_unit('indicator_lining').changed.connect(self.__lining_difference_model_changed)

        # рабочий маятник (у Навигатора - правый большой)
        self.__work_pendulum_indicator = ArrowPointerIndicator(
            chunks=[
                (4, Qt.GlobalColor.white),
                (1, Qt.GlobalColor.red),
                (1, Qt.GlobalColor.white),
                (1, Qt.GlobalColor.red),
                (4, Qt.GlobalColor.white),
        ], lineWidth=1000000, indicatorType='commonIndicator')
        #self.__state.units().get_readwrite_unit('indicator_pendulum_work').changed.connect(self.__pendulum_work_difference_model_changed)

        # индикатор отклонения ВНР по контрольному маятнику (у Навигатора - маленький цветной)
        # ex ArrowPointerControlLevelIndicator
        self.__pendulum_control_indicator = ArrowPointerIndicator(chunks=[
            (2, Qt.GlobalColor.red),
            (7, Qt.GlobalColor.yellow),
            (3, Qt.GlobalColor.green),
            (7, Qt.GlobalColor.yellow),
            (2, Qt.GlobalColor.red),
        ], lineWidth=4, indicatorType='controlLevelIndicator', )
        #self.__state.units().get_readwrite_unit('indicator_pendulum_control').changed.connect(self.__pendulum_control_difference_model_changed)
       

        # левый индикатор просадки (у Навигатора счётчик)
        self.__left_lifting_indicator = ArrowPointerIndicator(chunks=[
            (4, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (1, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (4, Qt.GlobalColor.white),
        ], lineWidth=1000000, indicatorType='commonIndicator', inverse_arrow_rotation=True)
        #self.__state.units().get_readwrite_unit('indicator_lifting_left').changed.connect(self.__left_lifting_difference_model_changed)
        

        # правый индикатор просадки (у Навигатора счётчик)
        self.__right_lifting_indicator = ArrowPointerIndicator(chunks=[
            (4, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (1, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (4, Qt.GlobalColor.white),
        ], lineWidth=1000000,  indicatorType='commonIndicator', inverse_arrow_rotation=True)
        #self.__state.units().get_readwrite_unit('indicator_lifting_right').changed.connect(self.__right_lifting_difference_model_changed)
        
    def __infomarkers(self):
        
        ################################### инфометки под индикаторами  ##################################
        __selected_base_rail = '' # str(self.options.program_task.options.measuring_trip.options.base_rail).split('.')[1]
        selected_base_rail = "Базовый рельс {0}".format(__selected_base_rail)
        self.label_base_rail = QLabel(selected_base_rail)
        self.label_base_rail.setContentsMargins(0,0,0,0)
        self.label_base_rail.setProperty("labelInfo", True)
        self.label_base_rail.setAlignment(Qt.AlignCenter)
        __selected_clamp = ""
        selected_clamp = "Прижим {0}".format(__selected_clamp)
        self.label_clamp = QLabel(selected_clamp)
        self.label_clamp.setContentsMargins(0,0,0,0)
        self.label_clamp.setProperty("labelInfo", True)
        self.label_clamp.setAlignment(Qt.AlignCenter)

    

    def __buttons(self):
             ################################### кнопки по центру ###################################
        self.button_f1 = QPushButton("Справка F1")
        self.button_f1.clicked.connect(self.__selected_f1)
        self.button_f1.setProperty("centerButton", True)
        self.button_f3 = QPushButton("Обзор F3")
        self.button_f3.setProperty("centerButton", True)
        self.button_f3.clicked.connect(self.__selected_f3)
        self.button_f4 = QPushButton(QCoreApplication.translate('Lining trip/process/view', "Старт F4"))
        self.button_f4.setProperty("centerButton", True)
        
        self.button_f5 = QPushButton("Отвод F5")
        self.button_f5.setProperty("centerButton", True)
        self.button_f6 = QPushButton("Задатчик F6")
        self.button_f6.setProperty("centerButton", True)
        self.button_f6.clicked.connect(self.__goInEqualizer)
        self.button_edit = QPushButton("Коррекция пути F8")
        self.button_edit.setProperty("centerButton", True)
        
        if not self.isEmergencyExtraction:
            self.button_quit = QPushButton("Окончание выправки F7")
            self.button_quit.setProperty("centerButton", True)
            self.button_quit.clicked.connect(lambda: self.__finishLinning())

            self.button_f5.clicked.connect(self.__startEmergencyExtractionDialog)
            self.button_f4.clicked.connect(self.__selected_f4)
            self.button_edit.clicked.connect(self.__showPathAdjustmentDialog)
        else:
            self.button_quit = QPushButton("Окончание работы F7")
            self.button_quit.setProperty("centerButton", True)
            self.button_quit.clicked.connect(lambda: self.__finishExtraction())
            
            self.button_f5.setStyleSheet("border-style:outset; border-width:7px; border-color:red;")

            self.button_f4.setEnabled(False)
            self.button_f4.blockSignals(True)

            self.button_f5.setEnabled(False)
            self.button_f5.blockSignals(True)
            
            self.button_edit.setEnabled(False)
            self.button_edit.blockSignals(True)


        self.button_f1.setFocusPolicy(Qt.NoFocus)
        self.button_f3.setFocusPolicy(Qt.NoFocus)
        self.button_f4.setFocusPolicy(Qt.NoFocus)
        self.button_f5.setFocusPolicy(Qt.NoFocus)
        self.button_f6.setFocusPolicy(Qt.NoFocus)
        self.button_quit.setFocusPolicy(Qt.NoFocus)
        self.button_edit.setFocusPolicy(Qt.NoFocus)
        
    def __equalizer(self):
        ################################## Эквалайзер ####################################################
        self.equalizer = EqualizerPanel(
            self.__state.lining_adjustment(),
            self.__state.raising_adjustment(),
            self.__state.vozv_adjustment(),
            self.__state.lining_adjustment_percent(),
            self.__state.raising_adjustment_percent(),
            self.__state.vozv_adjustment_percent(),
            self.__state.project_vozv_adjustment(),
            self.__state.project_raising_adjustment()
        )

    def __auto_branch_started(self, pos:float):
        self.isAutoBranching = True
        self.tooltip.show()
        self.tooltip.setText(self.auto_branching_txt)
        self.isUIBlocked = True
        self.blockUI()
              
    def __auto_branch_stopped(self, pos:float):
        self.isAutoBranching = False
        self.tooltip.hide()
        self.tooltip.setText('')
        self.isUIBlocked = False
        self.blockUI()

    def __updateDiscreteSignals(self, signals: DiscreteSignalsContainer):
        self.__work_strelograph_indicator.state_button_1 = signals.enable_shifting
        self.__work_strelograph_indicator.state_button_2 = signals.enable_lifting_left
        self.__work_strelograph_indicator.state_button_3 = signals.enable_lifting_right
        self.__work_strelograph_indicator.update()

    def __finishLinning(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(QCoreApplication.translate('Lining trip/success/finish message box', 'Quit'))
        msg.setIcon(QMessageBox.Question)
        msg.setText(QCoreApplication.translate('Lining trip/success/finish message box', 'Do you really want to go out?'))
        buttonAccept = msg.addButton("Да", QMessageBox.YesRole)
        buttonCancel = msg.addButton("Нет", QMessageBox.RejectRole)
        msg.setDefaultButton(buttonAccept)
        msg.exec()
        
        if msg.clickedButton() == buttonAccept:
            self.__state.finishLiningProcess()
        

    def __finishExtraction(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(QCoreApplication.translate('Lining trip/success/finish message box', 'Quit'))
        msg.setIcon(QMessageBox.Question)
        msg.setText("Вы действительно хотите выйти ?")
        buttonAccept = msg.addButton("Да", QMessageBox.YesRole)
        buttonCancel = msg.addButton("Нет", QMessageBox.RejectRole)
        msg.setDefaultButton(buttonAccept)
        msg.exec()
        if msg.clickedButton() == buttonAccept:
            self.__state.finishLiningState()
       

    def __finishExtraction(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(QCoreApplication.translate('Lining trip/success/finish message box', 'Quit'))
        msg.setIcon(QMessageBox.Question)
        msg.setText("Вы действительно хотите выйти ?")
        buttonAccept = msg.addButton("Да", QMessageBox.YesRole)
        buttonCancel = msg.addButton("Нет", QMessageBox.RejectRole)
        msg.setDefaultButton(buttonAccept)
        msg.exec()
        if msg.clickedButton() == buttonCancel:
            return
        elif msg.clickedButton() == buttonAccept:
            self.__state.finishLiningProcess()
        # if QMessageBox.question(self, QCoreApplication.translate('Lining trip/success/finish message box', 'Quit'),
        #                         QCoreApplication.translate('Lining trip/success/finish message box',
        #                                                    'Do you really want to go out?')
        #                         ) == QMessageBox.StandardButton.No:
        #     return
        # else:
        #     self.__state.finishLiningState()


    def __goInEqualizer(self):
        if (self.isUIBlocked): return
        self.equalizer.left_vertical_slider1.setFocus(Qt.FocusReason.ShortcutFocusReason)

    # ============================= стрелочные индикаторы =================================
    def __lining_difference_model_changed(self, value) -> None:          # с тремя цветными кнопками: стрелка
        self.__work_strelograph_indicator.setValue4(value)

    def __lining_difference_model_changed_satellite(self, value) -> None:    # с тремя цветными кнопками: satellite
        self.__work_strelograph_indicator.setValue5(value)

    def __pendulum_work_difference_model_changed(self, value) -> None:
        self.__work_pendulum_indicator.setValue(value)

    def __pendulum_control_difference_model_changed(self, value) -> None:         # цветной
        self.__pendulum_control_indicator.setValue1(value)

    def __pendulum_control_difference_model_changed_real(self, value) -> None:    # цветной
        self.__pendulum_control_indicator.setValue2(value)

    def __pendulum_control_difference_model_changed_prj(self, value) -> None:      # цветной
        self.__pendulum_control_indicator.setValue3(value)

    def __left_lifting_difference_model_changed(self, value) -> None:
        self.__left_lifting_indicator.setValue(value)

    def __right_lifting_difference_model_changed(self, value) -> None:
        self.__right_lifting_indicator.setValue(value)

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus()

    def keyPressEvent(self, keyEvent):
        super().keyPressEvent(keyEvent)
        key = keyEvent.key()
        if key == Qt.Key_F1:
            if self.isUIBlocked: return
            print("___нажата f1___")
        elif key == Qt.Key_F3:
            if self.isUIBlocked: return
            print("___нажата f3___")
        elif key == Qt.Key_F4:
            if self.isUIBlocked: return
            print("___нажата f4___")
            self.__selected_f4()
        elif key == Qt.Key_F5:
            if self.isUIBlocked: return
            self.__startEmergencyExtractionDialog()
        elif key == Qt.Key_F6:
            if self.isUIBlocked: return
            self.equalizer.left_vertical_slider1.setFocus(Qt.FocusReason.ShortcutFocusReason)
        elif key == Qt.Key_F7:
            self.__finishLinning()
        elif key == Qt.Key_F8:
            if self.isUIBlocked: return
            self.__showPathAdjustmentDialog()

    def __selected_f1(self):
        print("___нажата f1___")

    def __selected_f3(self):
        print("___нажата f3___")

    def __selected_f4(self):
        if not self.liningInProcessFlag:   # Выправка не запущена
            print("___нажата Старт___")
            # Запускаем алгоритм выправки
            self.__state.lining_processor().start()
            # Запускаем запись показаний датчиков
            self.__state.measurements_writer().start()
            # Запускаем динамическое масштабирование графиков
            # self.__picket_position_model.changed.connect(self.__update_chart_sliding_window)
            # Переводим позицию на начало програмного задания
            self.__picket_position_model.write(self.__programTaskByPicketModel.startPicket())
            #
            self.liningInProcessFlag = True
            self.button_f4.setStyleSheet("border-style:outset; border-width:7px; border-color:red;")
            
            self.tooltip.hide()
            self.button_f4.setEnabled(False)
            self.button_f4.blockSignals(True)
            #self.button_f4.setProperty("liningOnAir", True)    # setObjectName

    def __showPathAdjustmentDialog(self):
        if self.isUIBlocked: return
        if self.__direction_multiplier == 1:
            maxValue = self.position_max
            minValue = self.position_min
        else:
            maxValue = self.position_min
            minValue = self.position_max
        result = QInputDialog.getDouble(self, "Корректировка позиции", "Новая позиция (м):",
                                        value=self.__picket_position_model.read(), minValue=minValue, maxValue=maxValue,   #self.position_max,
                                        decimals=2, step=0.5)
        if result[1]:
            self.__picket_position_model.write(result[0])

    # ==========================================================================================
    def __onControlUnitConnectChanged(self, value: float) ->None:
        
        self.__control_unit_connection_label.setText("   {:4f}    ".format(value) or 0)   # {:4f}
        self.__control_unit_connection_label.setContentsMargins(0,0,0,0)
        if value < 0.016:
            style = "font: 16px; background-color: green;"
        else:
            style = "font: 16px; background-color: red;"
        self.__control_unit_connection_label.setStyleSheet(style)

        #self.__control_unit_connection_label.setNum(value or 0)

    # ==========================================================================================
    def __onStrelographWorkChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_strelograph_work_label.setNum(round(value, 1) or 0)
        #if abs(value) > 1000:
        #     self.__processor_strelograph_work_label.setStyleSheet(self.small_number_style)
        #else: self.__processor_strelograph_work_label.setStyleSheet(self.big_number_style)
    def __onPlanProjectMachineChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_plan_prj_label.setNum(round(value, 1) or 0)
    def __onProfProjectMachineChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_prof_prj_label.setNum(round(value, 1) or 0)
    def __onIndicatorLiningChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_indicator_lining_label.setNum(round(value, 1) or 0)
    def __onIndicatorLiftingLeftChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_indicator_lifting_left_label.setNum(round(value, 1) or 0)
    def __onIndicatorLiftingRightChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_indicator_lifting_right_label.setNum(round(value, 1) or 0)
    def __onIndicatorPendulumWorkChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_indicator_pendulum_work_label.setNum(round(value, 1) or 0)
    def __onIndicatorPendulumControlChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_indicator_pendulum_control_label.setNum(round(value, 1) or 0)
    def __onVozvProjectWorkChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_cant_prj_label.setNum(round(value, 1) or 0)
    def __onPendulumWorkChanged(self, value: float):
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_pendulum_work_label.setNum(round(value, 1) or 0)
    #def __onPendulumFrontChanged(self):
   #     self.__processor_pendulum_front_label.setNum(value or 0)
    def __onPendulumControlChanged(self, value: float):
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_pendulum_control_label.setNum(round(value, 1) or 0)
    def __onSaggingLeftChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_left_sagging_label.setNum(round(value, 1) or 0)
    def __onSaggingRightChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_right_sagging_label.setNum(round(value, 1) or 0)
    def __onSaggingPrjChanged(self, value: float) ->None:
        #value = float('{:.1f}'.format(round(value, 1)))
        self.__processor_project_sagging_label.setNum(round(value, 1) or 0)

    def __update_chart_sliding_window(self):
        self.chartSlideWindowUpdater.disableViewUpdates()
        self.chartSlideWindowUpdater.updateChartsState()
        self.chartSlideWindowUpdater.enableViewUpdates()

    # Окно Отвода
    def __startEmergencyExtractionDialog(self) ->None:
        if (self.isUIBlocked): return
        dialog = EmergencyExtractionOptions(
            start_extraction_picket= self.__picket_position_model.read(),
            options = self.__state.options(),
            program_task_by_raw_position = self.__state.program_task(),
            # program_task_by_picket = self.__programTaskByPicketModel,
            measurements = self.__state.measurements()
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.parameters()
            if options is not None:
                self.__state.emergency_extraction.emit(options)

    def __updatePositionSingleLineModel(self):  
        if self.liningInProcessFlag or self.isEmergencyExtraction:   # запрет на перезапуск при включённой выправке
            position_remain = (self.position_max - self.__position_line_model.position()) * self.__direction_multiplier
            # вывод диалога окончания выправки
            if position_remain <= 0:
                if not self.confirmationFinishLining:
                    self.confirmationFinishLining = True
                    # сохранение выправки
                    self.__state.save_result_to_backup()
                    # диалог окончания
                    self.__finishLinning()
            if 0 <= max(0, position_remain) < 10:
                value = str(round(max(0, position_remain), 1))
                self.tooltip.show()
                if (self.isAutoBranching):
                    self.tooltip.setText(self.auto_branching_txt + '. Осталось менее 10 метров: ' + value)
                else:
                    self.tooltip.setText('Осталось менее 10 метров: ' + value)
                

    def blockUI(self):
        btns = [self.button_f1, self.button_f3, self.button_f5,
                self.button_f6, self.button_edit,
                self.equalizer.left_vertical_slider1, self.equalizer.left_vertical_slider2,
                self.equalizer.left_vertical_slider3, self.equalizer.center_vertical_slider1,
                self.equalizer.center_vertical_slider2, self.equalizer.center_vertical_slider3,
                self.equalizer.right_vertical_slider1,self.equalizer.right_vertical_slider2, ]
        
        for btn in btns:
            btn.setEnabled(not self.isUIBlocked)
            btn.blockSignals(self.isUIBlocked)
        

        #self.repaint()
class LiningSuccessView(QWidget):
    def __init__(self, state: LiningSuccessState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: LiningSuccessState = state
        self.__window = Window("Выправка")

        saveButtom = QPushButton(QCoreApplication.translate('Lining trip/success/view', 'Save'))
        saveButtom.setProperty("optionsWindowPushButton", True)
        quitButton = QPushButton(QCoreApplication.translate('Lining trip/success/view', 'Quit'))
        quitButton.setProperty("optionsWindowPushButton", True)

        saveButtom.clicked.connect(self.__saveLiningResult)
        quitButton.clicked.connect(self.__finishMeasuring)

        layout = QVBoxLayout()
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #layout.addWidget(QLabel('application/lining/success'))
        layout.addWidget(saveButtom)
        layout.addWidget(quitButton)

    def __saveLiningResult(self):
        preffered_name: str = f'{self.__state.result().options.program_task.options.measuring_trip.options.track_title}__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.alt'
        saveFile = QFileDialog.getSaveFileName(self, QCoreApplication.translate('Lining trip/success/view', 'Select save measuring file'), preffered_name, '*.alt')[0]
        if saveFile is None or len(saveFile) == 0:
            return
        elif not saveFile.endswith('.alt'):
            saveFile += '.alt'

        try:
            result: LiningTripResultDto = self.__state.result()
            LiningTripResultDto_to_archive(zipfile.ZipFile(saveFile, 'w'), result)
        except Exception as error:
            print(traceback.format_exc())
            QMessageBox.critical(self, QCoreApplication.translate('Lining trip/success/view', 'Saving error'), str(error))
            os.remove(saveFile)

    def __finishMeasuring(self):
        if QMessageBox.question(self, QCoreApplication.translate('Lining trip/success/view', 'Quit'), QCoreApplication.translate('Lining trip/success/view','Do you really want to go out?')) == QMessageBox.StandardButton.Yes:
            self.__state.finish.emit()

class LiningErrorView(QWidget):
    def __init__(self, state: LiningErrorState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: LiningErrorState = state
        self.__window = Window("Выправка")

        errorLabel = QLabel(str(self.__state.error()))
        quitButton = QPushButton('Quit')
        quitButton.setProperty("optionsWindowPushButton", True)
        quitButton.clicked.connect(self.__state.finish)

        layout = QVBoxLayout()
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel('application/lining/error'))
        layout.addWidget(QLabel('Error occured:'))
        layout.addWidget(errorLabel)
        layout.addWidget(quitButton)

class EmergencyExtractionSuccessView(QWidget):
    def __init__(self, state: EmergencyExtractionSuccessState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: EmergencyExtractionSuccessState = state

        saveButtom = QPushButton(QCoreApplication.translate('Lining trip/success/view', 'Save'))
        saveButtom.setProperty("optionsWindowPushButton", True)
        quitButton = QPushButton(QCoreApplication.translate('Lining trip/success/view', 'Quit'))
        quitButton.setProperty("optionsWindowPushButton", True)

        saveButtom.clicked.connect(self.__saveLiningResult)
        quitButton.clicked.connect(self.__finishMeasuring)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #layout.addWidget(QLabel('application/lining/success'))
        layout.addWidget(saveButtom)
        layout.addWidget(quitButton)

    def __saveLiningResult(self):
        result: EmergencyExtractionResultDto = self.__state.result()
        preffered_name: str = f'{result.options.lining_trip.options.program_task.options.measuring_trip.options.track_title}__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.aex'
        saveFile = QFileDialog.getSaveFileName(self, QCoreApplication.translate('Lining trip/success/view', 'Select save measuring file'), preffered_name, '*.aex')[0]
        if saveFile is None or len(saveFile) == 0:
            return
        elif not saveFile.endswith('.aex'):
            saveFile += '.aex'

        try:
            EmergencyExtractionResultDto_to_archive(zipfile.ZipFile(saveFile, 'w'), result)
        except Exception as error:
            print(traceback.format_exc())
            QMessageBox.critical(self, 'Saving error', str(error))
            os.remove(saveFile)
    def __finishMeasuring(self):
        if QMessageBox.question(self, 'Quit', 'Do you really want to go out?') == QMessageBox.StandardButton.Yes:
            self.__state.finish.emit()

class EmergencyExtractionErrorView(QWidget):
    def __init__(self, state: EmergencyExtractionErrorState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: EmergencyExtractionErrorState = state

        errorLabel = QLabel(str(self.__state.error()))
        quitButton = QPushButton('Quit')
        quitButton.setProperty("optionsWindowPushButton", True)
        quitButton.clicked.connect(self.__state.finish)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #layout.addWidget(QLabel('application/lining/error'))
        layout.addWidget(QLabel('Error occured:'))
        layout.addWidget(errorLabel)
        layout.addWidget(quitButton)

class LiningView(QWidget):
    def __init__(self, state: ApplicationLiningState, parent: QWidget = None):   # state1:ProgramTaskCalculationSuccessState,
        super().__init__(parent)
        self.__state: ApplicationLiningState = state
        #self.__state1: ProgramTaskCalculationSuccessState = state1
        self.__state.select_mode.entered.connect(self.__onSelectModeStateEntered)
        self.__state.select_mode.exited.connect(self.__onSelectModeStateExited)
        self.__state.new_trip_options.entered.connect(self.__onNewTripOptionsStateEntered)
        self.__state.new_trip_options.exited.connect(self.__onNewTripOptionsStateExited)
        self.__state.continue_trip_options.entered.connect(self.__onContinueTripOptionsStateEntered)
        #self.continueLiningOptionsView = ContinueLiningOptionsView(ContinueLiningOptionsState)
       # self.continueLiningOptionsView.passDataSignal.connect(self.__onContinueTripOptionsStateEntered)
        self.__state.continue_trip_options.exited.connect(self.__onContinueTripOptionsStateExited)
        self.__state.emergency_extraction_recovery_options.entered.connect(self.__onEmergencyExtractionRecoveryStateEntered)
        self.__state.emergency_extraction_recovery_options.exited.connect(self.__onEmergencyExtractionRecoveryStateExited)
        self.__state.lining_process.entered.connect(self.__onLiningProcessStateEntered)
        self.__state.lining_process.exited.connect(self.__onLiningProcessStateExited)
        self.__state.lining_success.entered.connect(self.__onLiningSuccessStateEntered)
        self.__state.lining_success.exited.connect(self.__onLiningSuccessStateExited)
        self.__state.lining_error.entered.connect(self.__onLiningErrorStateEntered)
        self.__state.lining_error.exited.connect(self.__onLiningErrorStateExited)
        self.__state.emergency_extraction_process.entered.connect(self.__onEmergencyExtractionProcessStateEntered)
        self.__state.emergency_extraction_process.exited.connect(self.__onEmergencyExtractionProcessStateExited)
        self.__state.emergency_extraction_success.entered.connect(self.__onEmergencyExtractionSuccessStateEntered)
        self.__state.emergency_extraction_success.exited.connect(self.__onEmergencyExtractionSuccessStateExited)
        self.__state.emergency_extraction_error.entered.connect(self.__onEmergencyExtractionErrorStateEntered)
        self.__state.emergency_extraction_error.exited.connect(self.__onEmergencyExtractionErrorStateExited)
        self.__state.final.entered.connect(self.__onFinalStateEntered)
        self.__state.final.exited.connect(self.__onFinalStateExited)


        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.setLayout(self.__layout)


        self.LiningProcess = LiningProcess()


    def __onSelectModeStateEntered(self) ->None:
        self.__currentView = SelectLiningTripModeView(self.__state.select_mode)   # second state   , self.__state1
        self.__layout.addWidget(self.__currentView)
    def __onSelectModeStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onNewTripOptionsStateEntered(self) ->None:
        self.__currentView = NewLiningOptionsView(self.__state.new_trip_options)
        self.__layout.addWidget(self.__currentView)
    def __onNewTripOptionsStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onContinueTripOptionsStateEntered(self) ->None:      # , data
        self.__currentView = ContinueLiningOptionsView(self.__state.continue_trip_options)
        self.__layout.addWidget(self.__currentView)
        #result = LiningTripResultDto_from_archive(zipfile.ZipFile(self.__liningTripSelector.filepath(), 'r'))
        #self.__state.start.emit(result.options)
        # LiningTripResultDto_from_archive(zipfile.ZipFile(self.__liningTripSelector.filepath(), 'r')).options)
        #self.__currentView = ShowLiningResult(data)
        #self.__layout.addWidget(self.__currentView)
        #self.__currentView.show()
    def __onContinueTripOptionsStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onEmergencyExtractionRecoveryStateEntered(self) ->None:
        self.__currentView = EmergencyExtractionRecoveryOptionsView(self.__state.emergency_extraction_recovery_options)
        self.__layout.addWidget(self.__currentView)
    def __onEmergencyExtractionRecoveryStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onLiningProcessStateEntered(self) ->None:
        self.__currentView = self.LiningProcess.initLiningProcess(self.__state.lining_process)
        self.__layout.addWidget(self.__currentView)
    def __onLiningProcessStateExited(self) ->None:
        self.LiningProcess.disconnectSignals()
        self.__currentView.deleteLater()
    def __onLiningSuccessStateEntered(self) ->None:
        self.__currentView = LiningSuccessView(self.__state.lining_success)
        self.__layout.addWidget(self.__currentView)
    def __onLiningSuccessStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onLiningErrorStateEntered(self) ->None:
        self.__currentView = LiningErrorView(self.__state.lining_error)
        self.__layout.addWidget(self.__currentView)
    def __onLiningErrorStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onEmergencyExtractionProcessStateEntered(self) ->None:
        #self.__currentView = EmergencyExtractionProcessView(self.__state.emergency_extraction_process)
        #self.__layout.addWidget(self.__currentView)
        self.__currentView = self.LiningProcess.initEmergencyExtractionProcessView(self.__state.emergency_extraction_process)
        self.__layout.addWidget(self.__currentView)

    def __onEmergencyExtractionProcessStateExited(self) ->None:
        self.LiningProcess.disconnectSignals()
        self.__currentView.deleteLater()
    def __onEmergencyExtractionSuccessStateEntered(self) ->None:
        self.__currentView = EmergencyExtractionSuccessView(self.__state.emergency_extraction_success)
        self.__layout.addWidget(self.__currentView)
    def __onEmergencyExtractionSuccessStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onEmergencyExtractionErrorStateEntered(self) ->None:
        self.__currentView = EmergencyExtractionErrorView(self.__state.emergency_extraction_error)
        self.__layout.addWidget(self.__currentView)
    def __onEmergencyExtractionErrorStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onFinalStateEntered(self) ->None:
        pass
    def __onFinalStateExited(self) ->None:
        pass




