#This Python file uses the following encoding: utf-8
from domain.dto.Workflow import ProgramTaskCalculationOptionsDto, ProgramTaskCalculationResultDto
from domain.dto.Travelling import PicketDirection, LocationVector1D, MovingDirection
from operating.states.program_task_calculation.ProgramTaskCalculationState import (ProgramTaskCalculationState, ProgramTaskCalculationOptionsState, ProgramTaskCalculationProcessState,
                                                                                   ProgramTaskCalculationSuccessState, ProgramTaskCalculationErrorState, ProgramTaskCalculationFinalState)
from operating.states.lining.ApplicationLiningState import LiningProcessState
from ....utils.store.workflow.zip.Dto import MeasuringTripResultDto_from_archive, ProgramTaskCalculationResultDto_to_archive, ProgramTaskCalculationResultDto_from_archive
from ..common.viewes.CircliBusyIndicator import CircliBusyIndicator
from ..common.elements.Time import ElapsedTimeLabel
from ..common.elements.Files import FileSelector
from .Restrictions.SetRestrictions import WindowSettingsRestrictions
from .Calculation.CalculationCommonWindow.CalculationView import ProgramTaskCalculationSuccessView
from .OptionsReconstruction import OptionsReconstruction
from ..detailed_restrictions.DetailedRestrictionsView import DetailedRestrictionsWidget
from presentation.ui.gui.common.elements.Base import setWindowTitle
from presentation.ui.gui.common.viewes.WindowTitle import Window
from PySide6.QtWidgets import (QStackedLayout, QWidget, QLabel, QPushButton, QGroupBox,
                               QDoubleSpinBox, QAbstractSpinBox, QGridLayout,
                               QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog,
                               QErrorMessage, QComboBox, QDialog, QLineEdit)
from PySide6.QtCore import Qt, QSize, QRect, QDateTime, QObject, QCoreApplication, Slot, Signal
from PySide6.QtGui import QMovie 
import zipfile
import os



class ProgramTaskCalculationOptionsView(QWidget):
    openDetailedRestrictionsSignal = Signal(ProgramTaskCalculationOptionsDto)
    def __init__(self, state: ProgramTaskCalculationOptionsState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: ProgramTaskCalculationOptionsState = state
        self.__measuringTrip = None
        self.__measuringTripSelector = FileSelector('*.amt')
        self.__measuringTripSelector.filepathChanged.connect(self.__onMeasuringTripChanged)
        self.__window = Window("Расчёт программного задания")
        #
        #self.setMaximumHeight(1200)
        #self.setMinimumWidth(700)
        detailedRestrictionsButton = QPushButton("Детальные ограничения")
        optionsReconstructionButton = QPushButton("Настройки алгоритма расчёта")
        processButton = QPushButton("Рассчитать программное задание")
        processMockProgramTaskButton = QPushButton("Открыть программное задание")
        cancelButton = QPushButton("Выход")
        #
        detailedRestrictionsButton.setProperty("optionsWindowPushButton", True)
        optionsReconstructionButton.setProperty("optionsWindowPushButton", True)
        processButton.setProperty("optionsWindowPushButton", True)
        processMockProgramTaskButton.setProperty("optionsWindowPushButton", True)
        cancelButton.setProperty("optionsWindowPushButton", True)
        #
        detailedRestrictionsButton.clicked.connect(self.__setDetailedRestrictions)
        optionsReconstructionButton.clicked.connect(self.__setOptionsReconstruction)
        processButton.clicked.connect(self.__tryStartMeasuring)
        processMockProgramTaskButton.clicked.connect(self.__tryStartMockProgramTask)
        cancelButton.clicked.connect(self.__state.cancel)
        #
        self.windowSettingsRestrictions = WindowSettingsRestrictions(self.__state.restrictions())
        #
        self.__startPicket = QDoubleSpinBox()
        self.__startPicket.setRange(-1000000000, 1000000000)
        self.__startPicket.setEnabled(False)
        self.__startPicket.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.__picketDirection = QComboBox()
        self.__picketDirection.addItem(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Forward.name)),
                                          PicketDirection.Forward)
        self.__picketDirection.addItem(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Backward.name)),
                                         PicketDirection.Backward)
        # self.__picketDirection.setCurrentText(QCoreApplication.translate('Travelling/PicketDirection', (PicketDirection.Forward.name)))
        self.__picketDirection.setCurrentIndex(-1)
        self.__picketDirection.setEnabled(False) #можно включить чтобы было серым поле направления выправки без возможности поменять значение
        self.__picketDirection.currentIndexChanged.connect(self.__onPicketDirectionChanged)
        self.__programTaskSelector = FileSelector('*.apt')
        #
        top_groupbox_hlayout1, top_groupbox_hlayout2, top_groupbox_hlayout3 = QHBoxLayout(), QHBoxLayout(), QHBoxLayout()
        top_groupbox_hlayout1.addWidget(QLabel("Выбрать участок"))
        top_groupbox_hlayout1.addWidget(self.__measuringTripSelector)
        top_groupbox_hlayout2.addWidget(QLabel(QCoreApplication.translate('UI/Common', 'Направление выправки')))
        top_groupbox_hlayout2.addWidget(self.__picketDirection)
        top_groupbox_hlayout3.addWidget(QLabel(QCoreApplication.translate('UI/Common', 'Start picket')))
        top_groupbox_hlayout3.addWidget(self.__startPicket)
        #
        self.windowSettingsRestrictions.wrapping_groupbox_layout.insertLayout(0, top_groupbox_hlayout1)
        self.windowSettingsRestrictions.wrapping_groupbox_layout.insertLayout(1, top_groupbox_hlayout2)
        self.windowSettingsRestrictions.wrapping_groupbox_layout.insertLayout(2, top_groupbox_hlayout3)
        self.windowSettingsRestrictions.wrapping_groupbox_layout.insertWidget(-1, detailedRestrictionsButton)
        self.windowSettingsRestrictions.wrapping_groupbox_layout.insertWidget(-2, optionsReconstructionButton)
        self.windowSettingsRestrictions.wrapping_groupbox_layout.insertWidget(-3, processButton)
        #
        bottom_groupbox = QGroupBox("Ручное переустройство", alignment=Qt.AlignHCenter)
        bottom_groupbox.setStyleSheet("QGroupBox{font-size: 16px;}")
        bottom_groupbox_vlayout = QVBoxLayout()
        bottom_groupbox.setLayout(bottom_groupbox_vlayout)
        bottom_groupbox_hlayout = QHBoxLayout()
        bottom_groupbox_hlayout.addWidget(QLabel("Выбрать программное задание"))
        bottom_groupbox_hlayout.addWidget(self.__programTaskSelector)
        bottom_groupbox_vlayout.addLayout(bottom_groupbox_hlayout)
        bottom_groupbox_vlayout.addWidget(processMockProgramTaskButton)
        bottom_groupbox.setContentsMargins(10,30,10,30)
        #
        grid = QGridLayout()
        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        for column in range(8):
            grid.setColumnStretch(column, 1)
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.windowSettingsRestrictions, 0, 2, 1, 4)
        #grid.addWidget(optionsReconstructionButton, 3, 2, 1, 4)             # Настройки расчёта
        #grid.addWidget(processButton, 4, 2, 1, 4)
        grid.addWidget(bottom_groupbox, 5, 2, 2, 4)                        # Ручное переустройство
        grid.addWidget(cancelButton, 7, 2, 1, 4)
        grid.setContentsMargins(10, 10, 10, 30)
        #
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.__layout.addWidget(grid_widget)
        self.__window.addLayout(self.__layout, 1)
        self.setLayout(self.__window)
        


    def __onPicketDirectionChanged(self, index: int) ->None:
        if self.__measuringTrip is not None:
            if self.__measuringTrip.options.picket_direction == self.__picketDirection.currentData():
                self.__startPicket.setValue(self.__measuringTrip.options.start_picket.meters)
            else:
                railway_lenth = self.__measuringTrip.measurements.data.index.max() * self.__measuringTrip.measurements.step.meters
                self.__startPicket.setValue(self.__measuringTrip.options.start_picket.meters + railway_lenth * self.__measuringTrip.options.picket_direction.multiplier())

    def __onMeasuringTripChanged(self, path: str) -> None:
        try:
            self.__measuringTrip = MeasuringTripResultDto_from_archive(zipfile.ZipFile(self.__measuringTripSelector.filepath(), 'r'))
            self.__startPicket.setValue(self.__measuringTrip.options.start_picket.meters)

            """Из .амт поездки вытаскиваем направление пикетажа и движения машины
                Если направление движение == назад => направление выправки инвертируется"""
            moving_direction = PicketDirection(self.__measuringTrip.options.picket_direction)
            if self.__measuringTrip.options.moving_direction == MovingDirection.Backward:
                moving_direction = PicketDirection.inverted(moving_direction)
            index = self.__picketDirection.findData(moving_direction)
            if index != -1:
                self.__picketDirection.setCurrentIndex(index)

            self.__onPicketDirectionChanged(index)

            # self.__picketDirection.setCurrentText(QCoreApplication.translate('Travelling/PicketDirection', self.__measuringTrip.options.picket_direction.name))
        except Exception as error:            
            QMessageBox.critical(self, QCoreApplication.translate('Program task calculation/options/view', 'Read measurments file error'), str(error))
            return

    # ---> по кнопке 'Рассчитать программное задание'
    def __tryStartMeasuring(self) ->None:
        
        try:
            measuringTrip = MeasuringTripResultDto_from_archive(zipfile.ZipFile(self.__measuringTripSelector.filepath(), 'r'))
            # Проверка что направление пикетада выьрано
            if self.__picketDirection.currentData() is None:
                QMessageBox.critical(self, 'Не выбрано направление пикетажа', 'Выберите направление пикетажа для выправки')
                return
            
            options = ProgramTaskCalculationOptionsDto(
                measuring_trip = measuringTrip,
                restrictions = self.windowSettingsRestrictions.edited_restrictions(),
                start_picket = LocationVector1D(self.__startPicket.value()),
                picket_direction = self.__picketDirection.currentData())
            
            self.__state.start.emit(options)
        except Exception as error:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, QCoreApplication.translate('Program task calculation/options/view', 'Read measurments file error'), str(error))
            return
        
    #  по кнопке 'Открыть программное задание'  (групбокс РУЧНОЕ ПЕРЕУСТРОЙСТВО)
    def __tryStartMockProgramTask(self) -> None:
        try:
            programTask = ProgramTaskCalculationResultDto_from_archive(
                zipfile.ZipFile(self.__programTaskSelector.filepath(), 'r'))
            self.__state.open.emit(programTask)
        except Exception as error:
            QMessageBox.critical(self,
                                 QCoreApplication.translate('Lining trip/options/view', 'Read program task file error'),
                                 str(error))
            return

    #  по кнопке 'детальные ограничения'
    def __setDetailedRestrictions(self) -> None:
        # Проверка что направление пикетада выьрано
        if self.__picketDirection.currentData() is None:
            QMessageBox.critical(self, 'Не выбрано направление пикетажа', 'Выберите направление пикетажа для выправки')
            return
        
        try:
            options = ProgramTaskCalculationOptionsDto(
                measuring_trip=self.__measuringTrip,
                restrictions=self.windowSettingsRestrictions.edited_restrictions(),
                start_picket=LocationVector1D(self.__startPicket.value()),
                picket_direction=self.__picketDirection.currentData())
            self.openDetailedRestrictionsSignal.emit(options)
            self.detailedRestrictionsWidget = DetailedRestrictionsWidget(options, window=self.__window)
            self.detailedRestrictionsWidget.detailedRestrictionsSignal.connect(self.__closeDetailedRestrictions)
            self.__layout.addWidget(self.detailedRestrictionsWidget)
            self.__layout.setCurrentWidget(self.detailedRestrictionsWidget)
        except Exception as error:
            QMessageBox.critical(self, " ",  str('Участок (.amt файл) не выбран'))
            print(error)
            return

    # переход по кнопке 'Настройки расчёта'
    def __setOptionsReconstruction(self) -> None:
        restrictions = self.windowSettingsRestrictions.edited_restrictions()
        self.optionsReconstruction = OptionsReconstruction(restrictions, window=self.__window)
        self.optionsReconstruction.closeOptionsReconstructionSignal.connect(self.__closeOptionsReconstruction)
        self.__layout.addWidget(self.optionsReconstruction)
        #self.__layout.setCurrentIndex(2)
        self.__layout.setCurrentWidget(self.optionsReconstruction)

    def __closeDetailedRestrictions(self):
        self.__window.setTitle("Расчёт программного задания")
        self.__layout.setCurrentIndex(0)

    def __closeOptionsReconstruction(self):
        self.__layout.setCurrentIndex(0)
        self.__window.setTitle("Расчёт программного задания")



# Кнопка 'Рассчитать программное задание'
class ProgramTaskCalculationProcessView(QWidget):
    def __init__(self, state: ProgramTaskCalculationProcessState, parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
        self.__window = Window("Расчёт программного задания")
    
        # кнопка отмены
        cancelButton = QPushButton(QCoreApplication.translate('Program task calculation/process/view', 'Cancel'))
        cancelButton.clicked.connect(self.__state.calculator().cancellation_token().cancel)
        cancelButton.setProperty("optionsWindowPushButton", True)

        layout = QGridLayout()
        layout.setContentsMargins(10,10,10,10)
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        #layout.addWidget(QLabel('application/program_task_calculation/process'), 0, 0, 1, 1)
        layout.addWidget(ElapsedTimeLabel(), 0, 1, 1, 1)
        #busyIndicator = CircliBusyIndicator()
        #busyIndicator.start()
        #layout.addWidget(busyIndicator, 1, 0, 1, 2)
        
        label = QLabel() 
        #label.setGeometry(QRect(25, 25, 200, 200)) 
        #label.setMinimumSize(QSize(250, 250)) 
        #label.setMaximumSize(QSize(250, 250)) 
        layout.addWidget(label, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
  
        # Loading the GIF 
        movie = QMovie("./resources/images/loading_gears.gif") 
        movie.start() 
        label.setMovie(movie) 

        layout.addWidget(cancelButton, 2, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)

# class ProgramTaskCalculationSuccessView(QWidget):
#     def __init__(self, state: ProgramTaskCalculationSuccessState, parent: QWidget = None):
#         super().__init__(parent)
#         self.__state = state

#         saveButtom = QPushButton(QCoreApplication.translate('Program task calculation/success/view', 'Save'))
#         quitButton = QPushButton(QCoreApplication.translate('Program task calculation/success/view', 'Quit'))

#         saveButtom.clicked.connect(self.__saveMeasuringResult)
#         quitButton.clicked.connect(self.__finishMeasuring)

#         layout = QVBoxLayout()
#         self.setLayout(layout)
#         layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         layout.addWidget(QLabel('application/program_task_calculation/success'))
#         layout.addWidget(saveButtom)
#         layout.addWidget(quitButton)

#     def __saveMeasuringResult(self):
#         preffered_name: str = f'{self.__state.calculation_result().options.measuring_trip.options.track_title}__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.apt'
#         saveFile = QFileDialog.getSaveFileName(self, QCoreApplication.translate('Program task calculation/success/view', 'Select save program task file'), preffered_name, '*.apt')[0]
#         if saveFile is None or len(saveFile) == 0:
#             return
#         elif not saveFile.endswith('.apt'):
#             saveFile += '.apt'

#         try:
#             result: ProgramTaskCalculationResultDto = self.__state.calculation_result()
#             ProgramTaskCalculationResultDto_to_archive(zipfile.ZipFile(saveFile, 'w'), result)
#         except Exception as error:
#             QMessageBox.critical(self, QCoreApplication.translate('Program task calculation/success/view', 'Saving error'), str(error))
#             os.remove(saveFile)

#     def __finishMeasuring(self):
#         if QMessageBox.question(self, QCoreApplication.translate('Program task calculation/success/finish message box', 'Quit'),
#         QCoreApplication.translate('Program task calculation/success/finish message box', 'Do you really want to go out?')) == QMessageBox.StandardButton.No:
#             return

#         self.__state.finish.emit()

class ProgramTaskCalculationErrorView(QWidget):
    def __init__(self, state: ProgramTaskCalculationErrorState, parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
        self.__window = Window("Расчёт программного задания > Отмена")

        errorLabel = QLabel(str(self.__state.error()))
        quitButton = QPushButton(QCoreApplication.translate('Program task calculation/success/view', 'Quit'))
        quitButton.clicked.connect(self.__state.finish)

        layout = QVBoxLayout()
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #layout.addWidget(QLabel('application/program_task_calculation/error'))
        layout.addWidget(QLabel(QCoreApplication.translate('Program task calculation/error/view', 'Error occured:')))
        layout.addWidget(errorLabel)
        layout.addWidget(quitButton)

# stacked layout Расчёта/Переустройства
class ProgramTaskCalculationView(QWidget):
    def __init__(self, state: ProgramTaskCalculationState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: ProgramTaskCalculationState = state
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
        #
        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.setLayout(self.__layout)

    def __onOptionsStateEntered(self) ->None:
        self.__currentView = ProgramTaskCalculationOptionsView(self.__state.options)
        #self.__currentView = OptionsStackedView(self.__state.options)
        self.__layout.addWidget(self.__currentView)
        #self.__currentView.detailedRestrictionsSignal.connect(self.__onDetailedRestrictionsEntered)
    def __onOptionsStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onProcessStateEntered(self) ->None:
        self.__currentView = ProgramTaskCalculationProcessView(self.__state.process)
        self.__layout.addWidget(self.__currentView)
    def __onProcessStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onSuccessStateEntered(self) ->None:
        self.__currentView = ProgramTaskCalculationSuccessView(self.__state.success)
        self.__layout.addWidget(self.__currentView)
        #setWindowTitle(self, "Переустройство")
    def __onSuccessStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onErrorStateEntered(self) ->None:
        self.__currentView = ProgramTaskCalculationErrorView(self.__state.error)
        self.__layout.addWidget(self.__currentView)
    def __onErrorStateExited(self) ->None:
        self.__currentView.deleteLater()
    def __onFinalStateEntered(self) ->None:
        pass
    def __onFinalStateExited(self) ->None:
        pass






