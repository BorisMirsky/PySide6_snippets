# This Python file uses the following encoding: utf-8
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
from domain.dto.Workflow import LiningTripOptionsDto, LiningTripResultDto, EmergencyExtractionOptionsDto, EmergencyExtractionResultDto
from domain.dto.Travelling import LocationVector1D, SteppedData, MovingDirection, BaseRail
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from domain.units.MemoryBufferUnit import MemoryBufferUnit
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from domain.models.UnitsToModelWriter import UnitsToModelWriter
from domain.markers.RailwayMarkersSyncronization import RailwayMarkerPositionSyncronizer
from domain.markers.BaseRailwayMarkerModel import BaseRailwayMarkerModel
from domain.markers.AbstractMarkerModel import AbstractMarkerModel
from presentation.utils.store.workflow.zip.Dto import LiningTripResultDto_to_archive, EmergencyExtractionResultDto_to_archive
from .LiningProcessor import LiningProcessor
from .AutoBranching import AutoBranchingProcessor
from presentation.machine.units.StrelographUnit import StrelographUnit
from presentation.models.PicketPositionUnit import PicketPositionUnit
from PySide6.QtStateMachine import QStateMachine, QFinalState, QState
from PySide6.QtCore import QEvent, Signal, QDateTime
from typing import Optional
from pathlib import Path
import zipfile
import os


class SelectLiningTripModeState(QState):
    emergency_extraction_recovery_trip: Signal = Signal()
    continue_lining_trip: Signal = Signal()
    new_lining_trip: Signal = Signal()
    cancel: Signal = Signal()

    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/lining/select_mode][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/select_mode][exited]')

class NewLiningOptionsState(QState):
    start: Signal = Signal(LiningTripOptionsDto)
    cancel: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/lining/new/options][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/new/options][exited]')


class ContinueLiningOptionsState(QState):
    start: Signal = Signal(LiningTripOptionsDto)
    cancel: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/lining/continue/options][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/continue/options][exited]')

class EmergencyExtractionRecoveryOptionsState(QState):
    start: Signal = Signal(LiningTripOptionsDto)
    cancel: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/lining/emergency_extraction_recovery/options][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/emergency_extraction_recovery/options][exited]')

class LiningProcessState(QState):
    emergency_extraction: Signal = Signal(EmergencyExtractionOptionsDto)
    success: Signal = Signal(LiningTripResultDto)
    error: Signal = Signal(Exception)
    
    def __init__(self, config: dict, units: AbstractUnitProvider, rfid_tag_scanner: AbstractRfidScanner, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        # base
        self.__config: dict = config
        self.__position_unit: AbstractReadWriteUnit[float] = None
        self.__units: AbstractUnitProvider = units
        self.__rfid_tag_scanner: AbstractRfidScanner = rfid_tag_scanner
        # optional
        self.__options: LiningTripOptionsDto = None
        self.__program_task: AbstractPositionedTableModel = None
        self.__measurements: AbstractPositionedTableModel = None
        self.__measurements_writer: UnitsToModelWriter = None
        self.__lining_processor: LiningProcessor = None
        self.__auto_branching: AutoBranchingProcessor = None
        self.__marker_position_syncronizer: RailwayMarkerPositionSyncronizer = None
        self.__marker_model: AbstractMarkerModel = None
    
    def measurements(self) ->AbstractPositionedTableModel:
        return self.__measurements
    def config(self) ->dict:
        return self.__config
    def position_unit(self) ->AbstractReadUnit[float]:
        return self.__position_unit
    def units(self) ->AbstractUnitProvider:
        return self.__units
    def rfid_tag_scanner(self) ->AbstractRfidScanner:
        return self.__rfid_tag_scanner

    def options(self) ->LiningTripOptionsDto:
        return self.__options
    def program_task(self) ->AbstractPositionedTableModel:
        return self.__program_task    
    def measurements_writer(self) ->UnitsToModelWriter:
        return self.__measurements_writer
    def lining_processor(self) ->LiningProcessor:
        return self.__lining_processor
    def auto_branching(self) ->AutoBranchingProcessor:
        return self.__auto_branching
    def marker_position_syncronizer(self) ->RailwayMarkerPositionSyncronizer:
        return self.__marker_position_syncronizer
    def marker_model(self) ->AbstractMarkerModel:
        return self.__marker_position_syncronizer

    # Индикаторы
    def indicator_pendulum_control(self):
        return self.__indicator_pendulum_control
    def indicator_pendulum_front(self):
        return self.__indicator_pendulum_front
    def indicator_pendulum_work(self):
        return self.__indicator_pendulum_work
    def indicator_lining(self):
        return self.__indicator_lining
    def indicator_lifting_left(self):
        return self.__indicator_lifting_left
    def indicator_lifting_right(self):
        return self.__indicator_lifting_right
    
    def plan_project_machine(self) ->AbstractReadWriteUnit[float]:
        return self.__plan_project_machine
    def plan_delta_unit(self) ->AbstractReadWriteUnit[float]:
        return self.__plan_delta_unit
    def prof_project_machine(self) ->AbstractReadWriteUnit[float]:
        return self.__prof_project_machine 
    def vozv_project_work_provider(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_project_work_provider
    def vozv_project_control_unit(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_project_control_unit
    def lining_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__lining_adjustment
    def vozv_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_adjustment
    def raising_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__raising_adjustment

    def lining_adjustment_percent(self) ->AbstractReadWriteUnit[float]:
        return self.__lining_adjustment_percent
    def vozv_adjustment_percent(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_adjustment_percent
    def raising_adjustment_percent(self) ->AbstractReadWriteUnit[float]:
        return self.__raising_adjustment_percent
    def project_vozv_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__project_vozv_adjustment
    def project_raising_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__project_raising_adjustment

    def finishLiningProcess(self) ->None:
        self.finishLiningState()
        
    def finishLiningState(self) ->None:
        self.save_result_to_backup()
        
        self.success.emit(
            LiningTripResultDto(
                options = self.__options, 
                measurements = SteppedData(
                    data = self.__measurements.dataframe(),
                    step = self.__measurements.step())
            ))
        
    def save_result_to_backup(self):
        """
            Делает резервную копию выправляемого участка при условии, что кол-во записей в таблице больше 1.
        """
        if self.__measurements.rowCount() < 2:
            return
        
        # конструируем путь для сохранения 
        saveFolder = Path(os.path.expanduser(self.__config.get('settings', {}).get('backups_path', '.')))
        if not Path.exists(saveFolder):
            saveFolder.mkdir(parents=True)
        preffered_name = f'{self.__options.program_task.options.measuring_trip.options.track_title}__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.alt'
        savePath = Path.joinpath(saveFolder, preffered_name)
        # сохраняем в архив
        try:
            result = LiningTripResultDto(
                        options = self.__options, 
                        measurements = SteppedData(
                            data = self.__measurements.dataframe(),
                            step = self.__measurements.step()) )
            LiningTripResultDto_to_archive(zipfile.ZipFile(savePath, 'w'), result)
        except Exception as error:
            print(error)

    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/lining/process][entered]') #
        self.__options: LiningTripOptionsDto = event.arguments()[0]

        # Разрешение на общение с контроллером машины
        self.__units.get_readwrite_unit('enable_register').write(1) 
        
        # Установка прижима для стелографа
        strelograph_unit: StrelographUnit = self.__units.get_read_only_unit('strelograph_work')
        strelograph_unit.set_press_type(self.__options.press_rail)
        
        # ==============================================
        # TODO -- высчитать начальное положение для position_unit???
        self.__position_unit = self.__units.create_position_unit(MovingDirection.Forward)##
        self.__position_unit.write(0.0)
        # ==============================================        
        self.__lining_adjustment = MemoryBufferUnit(0.0, self)
        self.__vozv_adjustment = MemoryBufferUnit(0.0, self)
        self.__raising_adjustment = MemoryBufferUnit(0.0, self)
        self.__lining_adjustment_percent = MemoryBufferUnit(0.0, self)
        self.__vozv_adjustment_percent = MemoryBufferUnit(0.0, self)
        self.__raising_adjustment_percent = MemoryBufferUnit(0.0, self)
        self.__project_vozv_adjustment = MemoryBufferUnit(0.0, self)
        self.__project_raising_adjustment = MemoryBufferUnit(0.0, self)
        
        self.__plan_project_machine = MemoryBufferUnit(0.0, self)
        self.__plan_delta_unit = MemoryBufferUnit(0.0, self)
        self.__prof_project_machine = MemoryBufferUnit(0.0, self)
        self.__vozv_project_work_provider = MemoryBufferUnit(0.0, self)
        self.__vozv_project_control_unit = MemoryBufferUnit(0.0, self)
        self.__vozv_difference_provider = MemoryBufferUnit(0.0, self)

        self.__indicator_lining = MemoryBufferUnit(0.0, self)
        self.__indicator_pendulum_front = MemoryBufferUnit(0.0, self)
        self.__indicator_pendulum_work = MemoryBufferUnit(0.0, self)
        self.__indicator_pendulum_control = MemoryBufferUnit(0.0, self)
        self.__indicator_lifting_left = MemoryBufferUnit(0.0, self)
        self.__indicator_lifting_right = MemoryBufferUnit(0.0, self)

        self.__side_movement_servo_valve = MemoryBufferUnit(0.0, self)
        self.__right_lifting_servo_valve = MemoryBufferUnit(0.0, self)
        self.__left_lifting_servo_valve = MemoryBufferUnit(0.0, self)

        # Модель програмного задания
        self.__program_task = StepIndexedDataFramePositionedModel( ##
            columns = self.__options.program_task.calculated_task.data.columns, 
            step = self.__options.program_task.calculated_task.step, 
            parent = self
        )
        self.__program_task.reset(self.__options.program_task.calculated_task.step, self.__options.program_task.calculated_task.data)
        
        # Модель для авто-отвода
        self.__auto_branching = AutoBranchingProcessor(
                                    enabled = self.__options.auto_branching,
                                    track_length = self.__program_task.minmaxPosition()[1].meters)
        
        # Список всех юнитов для логирования
        all_units = self.__units.get_all_read_only_units() | self.__units.get_all_readwrite_units() | {
            'log_lining_adjustment': self.__lining_adjustment,
            'log_vozv_adjustment': self.__vozv_adjustment,
            'log_raising_adjustment': self.__raising_adjustment,
            'log_lining_adjustment_percent': self.__lining_adjustment_percent,
            'log_vozv_adjustment_percent': self.__vozv_adjustment_percent,
            'log_raising_adjustment_percent': self.__raising_adjustment_percent,
            'log_project_vozv_adjustment': self.__project_vozv_adjustment,
            'log_project_raising_adjustment': self.__project_raising_adjustment,
            'log_plan_project_machine': self.__plan_project_machine,
            'log_plan_delta_unit': self.__plan_delta_unit,
            'log_prof_project_machine': self.__prof_project_machine,
            'log_vozv_difference_provider': self.__vozv_difference_provider,
            'log_vozv_project_work_provider': self.__vozv_project_work_provider,
            'log_vozv_project_control_unit': self.__vozv_project_control_unit, 
            'log_indicator_lining': self.__indicator_lining,
            'log_indicator_pendulum_front': self.__indicator_pendulum_front,
            'log_indicator_pendulum_work': self.__indicator_pendulum_work,
            'log_indicator_pendulum_control': self.__indicator_pendulum_control,
            'log_indicator_lifting_left': self.__indicator_lifting_left,
            'log_indicator_lifting_right': self.__indicator_lifting_right,
            'log_side_movement_servo_valve': self.__side_movement_servo_valve,
            'log_right_lifting_servo_valve': self.__right_lifting_servo_valve,
            'log_left_lifting_servo_valve': self.__left_lifting_servo_valve 
        } | self.__auto_branching.log_units()

        # Модель для записи значений юнитов в таблицу
        self.__measurements = StepIndexedDataFramePositionedModel(list(all_units.keys()), LocationVector1D(0.185), self)
        self.__measurements_writer = UnitsToModelWriter(self.__measurements, self.__position_unit, all_units, LocationVector1D(meters = 0.1))
        
        # Маркеры
        self.__marker_model = BaseRailwayMarkerModel()
        for marker, position in self.__options.program_task.options.measuring_trip.tags:
            self.__marker_model.insertMarkerAtPosition(marker, position)
        self.__marker_position_syncronizer = RailwayMarkerPositionSyncronizer(position_provider = self.__position_unit, markers = self.__marker_model, parent = self)
        self.__rfid_tag_scanner.tagReceived.connect(lambda tag, rssi: self.__marker_position_syncronizer.syncronizeByMarker(tag))
        
        # Модель для расчета выправки
        self.__lining_processor = LiningProcessor(
            # base_rail = self.__options.program_task.options.measuring_trip.options.base_rail,
            base_rail = BaseRail.Left,
            machine_parameters = self.__config.get('machine_parameters', {}),
            position_unit = self.__position_unit,
            program_task = self.__program_task,
            measurements = self.__measurements,
            units = self.__units,            
            lining_adjustment = self.__lining_adjustment,
            vozv_adjustment = self.__vozv_adjustment,
            raising_adjustment = self.__raising_adjustment,
            lining_adjustment_percent = self.__lining_adjustment_percent,
            vozv_adjustment_percent = self.__vozv_adjustment_percent,
            raising_adjustment_percent = self.__raising_adjustment_percent,
            project_vozv_adjustment = self.__project_vozv_adjustment,
            project_raising_adjustment = self.__project_raising_adjustment,
            plan_project_machine = self.__plan_project_machine,
            plan_delta_unit = self.__plan_delta_unit,
            prof_project_machine = self.__prof_project_machine,
            vozv_difference_provider = self.__vozv_difference_provider,
            vozv_project_work_provider = self.__vozv_project_work_provider,
            vozv_project_control_unit = self.__vozv_project_control_unit,
            indicator_lining = self.__indicator_lining,
            indicator_pendulum_front = self.__indicator_pendulum_front,
            indicator_pendulum_work = self.__indicator_pendulum_work,
            indicator_pendulum_control = self.__indicator_pendulum_control,
            indicator_lifting_left = self.__indicator_lifting_left,
            indicator_lifting_right = self.__indicator_lifting_right,
            side_movement_servo_valve = self.__side_movement_servo_valve,
            right_lifting_servo_valve = self.__right_lifting_servo_valve,
            left_lifting_servo_valve = self.__left_lifting_servo_valve,
            auto_branching = self.__auto_branching,
            timer = self.__config['models']['connection'].get('lining_timer', 50),
            parent = self)
        
        self.__indicator_pendulum_front.changed.connect(self.__units.get_readwrite_unit('indicator_pendulum_front').write)
        self.__indicator_pendulum_work.changed.connect(self.__units.get_readwrite_unit('indicator_pendulum_work').write)
        self.__indicator_pendulum_control.changed.connect(self.__units.get_readwrite_unit('indicator_pendulum_control').write)
        self.__indicator_lifting_right.changed.connect(self.__units.get_readwrite_unit('indicator_lifting_right').write)
        self.__indicator_lifting_left.changed.connect(self.__units.get_readwrite_unit('indicator_lifting_left').write)
        self.__indicator_lining.changed.connect(self.__units.get_readwrite_unit('indicator_lining').write)
        self.__right_lifting_servo_valve.changed.connect(self.__units.get_readwrite_unit('lifting_right').write)
        self.__left_lifting_servo_valve.changed.connect(self.__units.get_readwrite_unit('lifting_left').write)
        self.__side_movement_servo_valve.changed.connect(self.__units.get_readwrite_unit('lining').write)
        # self.__measurements_writer.start()
        # self.__lining_processor.start()

    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/process][exited]')
        self.__units.get_readwrite_unit('enable_register').write(0) # запрещаем общение с контроллером машины
        self.__measurements_writer.stop()
        self.__lining_processor.stop()
        self.__lining_processor.deleteLater()
        self.__marker_position_syncronizer.deleteLater()
        self.__measurements_writer.deleteLater()
        self.__measurements.deleteLater()
        self.__program_task.deleteLater()

        self.__lining_processor = None
        self.__marker_position_syncronizer = None
        self.__measurements_writer = None
        self.__measurements = None
        self.__program_task = None
        self.__options = None

class LiningSuccessState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__result: LiningTripResultDto = None
    def result(self) ->LiningTripResultDto:
        return self.__result
    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/lining/success][entered]')
        self.__result = event.arguments()[0]
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/success][exited]')
        self.__result = None

class LiningErrorState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: QState = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__error: Exception = None
    def error(self) ->Exception :
        return self.__error
    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/lining/error][entered]')
        self.__error = event.arguments()[0]
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/error][exited]')
        self.__error = None

class EmergencyExtractionProcessState(QState):
    success: Signal = Signal(EmergencyExtractionResultDto)
    error: Signal = Signal(Exception)
    def __init__(self, config: dict, units: AbstractUnitProvider, rfid_tag_scanner: AbstractRfidScanner, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        # base
        self.__config: dict = config
        self.__position_unit: AbstractReadWriteUnit[float] = None
        self.__units: AbstractUnitProvider = units
        self.__rfid_tag_scanner: AbstractRfidScanner = rfid_tag_scanner
        # optional
        self.__options: EmergencyExtractionOptionsDto = None
        self.__program_task: AbstractPositionedTableModel = None
        self.__measurements: AbstractPositionedTableModel = None
        self.__measurements_writer: UnitsToModelWriter = None
        self.__lining_processor: LiningProcessor = None
        self.__auto_branching: AutoBranchingProcessor = None
        self.__marker_position_syncronizer: RailwayMarkerPositionSyncronizer = None
        self.__marker_model: AbstractMarkerModel = None
    
    def config(self) ->dict:
        return self.__config
    def position_unit(self) ->AbstractReadUnit[float]:
        return self.__position_unit
    def picket_position_unit(self) ->AbstractReadUnit[float]:
        return self.__picket_position_unit
    def units(self) ->AbstractUnitProvider:
        return self.__units
    def rfid_tag_scanner(self) ->AbstractRfidScanner:
        return self.__rfid_tag_scanner

    def options(self) ->EmergencyExtractionOptionsDto:
        return self.__options
    def program_task(self) ->AbstractPositionedTableModel:
        return self.__program_task
    def measurements(self) ->AbstractPositionedTableModel:
        return self.__measurements
    def measurements_writer(self) ->UnitsToModelWriter:
        return self.__measurements_writer
    def lining_processor(self) ->LiningProcessor:
        return self.__lining_processor
    def marker_position_syncronizer(self) ->RailwayMarkerPositionSyncronizer:
        return self.__marker_position_syncronizer
    def marker_model(self) ->AbstractMarkerModel:
        return self.__marker_position_syncronizer
    def auto_branching(self) ->AutoBranchingProcessor:
        return self.__auto_branching

    # Индикаторы
    def indicator_pendulum_control(self):
        return self.__indicator_pendulum_control
    def indicator_pendulum_front(self):
        return self.__indicator_pendulum_front
    def indicator_pendulum_work(self):
        return self.__indicator_pendulum_work
    def indicator_lining(self):
        return self.__indicator_lining
    def indicator_lifting_left(self):
        return self.__indicator_lifting_left
    def indicator_lifting_right(self):
        return self.__indicator_lifting_right
    
    def plan_project_machine(self) ->AbstractReadWriteUnit[float]:
        return self.__plan_project_machine
    def plan_delta_unit(self) ->AbstractReadWriteUnit[float]:
        return self.__plan_delta_unit
    def prof_project_machine(self) ->AbstractReadWriteUnit[float]:
        return self.__prof_project_machine 
    def vozv_project_work_provider(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_project_work_provider
    def vozv_project_control_unit(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_project_control_unit
    def lining_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__lining_adjustment
    def vozv_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_adjustment
    def raising_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__raising_adjustment

    def lining_adjustment_percent(self) ->AbstractReadWriteUnit[float]:
        return self.__lining_adjustment_percent
    def vozv_adjustment_percent(self) ->AbstractReadWriteUnit[float]:
        return self.__vozv_adjustment_percent
    def raising_adjustment_percent(self) ->AbstractReadWriteUnit[float]:
        return self.__raising_adjustment_percent
    def project_vozv_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__project_vozv_adjustment
    def project_raising_adjustment(self) ->AbstractReadWriteUnit[float]:
        return self.__project_raising_adjustment

    def finishLiningProcess(self) ->None:
        self.finishLiningState()

    def finishLiningState(self) ->None:
        self.save_result_to_backup()    # делаем резервную копию отвода
        self.success.emit(
            EmergencyExtractionResultDto(
                options = self.__options, 
                measurements = SteppedData(
                    data = self.__measurements.dataframe(),
                    step = self.__measurements.step())
            ))

    def save_result_to_backup(self):
        """
            Делает резервную копию выправляемого участка при условии, что кол-во записей в таблице больше 1.
        """
        if self.__measurements.rowCount() < 2:
            return
        
        # конструируем путь для сохранения 
        saveFolder = Path(os.path.expanduser(self.__config.get('settings', {}).get('backups_path', '.')))
        if not Path.exists(saveFolder):
            saveFolder.mkdir(parents=True)
        track_title = self.__options.lining_trip.options.program_task.options.measuring_trip.options.track_title
        preffered_name = f'{track_title}__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.aex'
        savePath = Path.joinpath(saveFolder, preffered_name)
        # сохраняем в архив
        try:
            result = EmergencyExtractionResultDto(
                        options = self.__options, 
                        measurements = SteppedData(
                            data = self.__measurements.dataframe(),
                            step = self.__measurements.step()) )
            EmergencyExtractionResultDto_to_archive(zipfile.ZipFile(savePath, 'w'), result)
        except Exception as error:
            print(error)

    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/emergency_extraction/process][entered]')
        self.__units.get_readwrite_unit('enable_register').write(1) # разрешаем общение с контроллером машины
        self.__options: EmergencyExtractionOptionsDto = event.arguments()[0]
        # ======== Program task transformations ========
        # TODO -- высчитать начальное положение для position_unit
        self.__position_unit = self.__units.create_position_unit(MovingDirection.Forward)
        self.__picket_position_unit = PicketPositionUnit(self.__position_unit, self.__options.lining_trip.options.picket_direction, self.__options.lining_trip.options.start_picket.meters)
        self.__picket_position_unit.write(self.__options.start_extraction_picket.meters)
        # ==============================================
        self.__lining_adjustment = MemoryBufferUnit(0.0, self)
        self.__vozv_adjustment = MemoryBufferUnit(0.0, self)
        self.__raising_adjustment = MemoryBufferUnit(0.0, self)
        self.__lining_adjustment_percent = MemoryBufferUnit(0.0, self)
        self.__vozv_adjustment_percent = MemoryBufferUnit(0.0, self)
        self.__raising_adjustment_percent = MemoryBufferUnit(0.0, self)
        self.__project_vozv_adjustment = MemoryBufferUnit(0.0, self)
        self.__project_raising_adjustment = MemoryBufferUnit(0.0, self)
        
        self.__plan_project_machine = MemoryBufferUnit(0.0, self)
        self.__plan_delta_unit = MemoryBufferUnit(0.0, self)
        self.__prof_project_machine = MemoryBufferUnit(0.0, self)
        self.__vozv_project_work_provider = MemoryBufferUnit(0.0, self)
        self.__vozv_project_control_unit = MemoryBufferUnit(0.0, self)
        self.__vozv_difference_provider = MemoryBufferUnit(0.0, self)

        self.__indicator_lining = MemoryBufferUnit(0.0, self)
        self.__indicator_pendulum_front = MemoryBufferUnit(0.0, self)
        self.__indicator_pendulum_work = MemoryBufferUnit(0.0, self)
        self.__indicator_pendulum_control = MemoryBufferUnit(0.0, self)
        self.__indicator_lifting_left = MemoryBufferUnit(0.0, self)
        self.__indicator_lifting_right = MemoryBufferUnit(0.0, self)

        self.__side_movement_servo_valve = MemoryBufferUnit(0.0, self)
        self.__right_lifting_servo_valve = MemoryBufferUnit(0.0, self)
        self.__left_lifting_servo_valve = MemoryBufferUnit(0.0, self)
        
        # Модель програмного задания
        self.__program_task = StepIndexedDataFramePositionedModel(
            columns = self.__options.extraction_trajectory.data.columns, 
            step = self.__options.extraction_trajectory.step, 
            parent = self
        )
        self.__program_task.reset(self.__options.extraction_trajectory.step, self.__options.extraction_trajectory.data)
        
        # Модель для авто-отвода
        self.__auto_branching = AutoBranchingProcessor(
                                    enabled = self.__options.auto_branching,
                                    track_length = self.__program_task.minmaxPosition()[1].meters)
        
        # Список всех юнитов для логирования
        all_units = self.__units.get_all_read_only_units() | self.__units.get_all_readwrite_units() | {
            'log_lining_adjustment': self.__lining_adjustment,
            'log_vozv_adjustment': self.__vozv_adjustment,
            'log_raising_adjustment': self.__raising_adjustment,
            'log_lining_adjustment_percent': self.__lining_adjustment_percent,
            'log_vozv_adjustment_percent': self.__vozv_adjustment_percent,
            'log_raising_adjustment_percent': self.__raising_adjustment_percent,
            'log_project_vozv_adjustment': self.__project_vozv_adjustment,
            'log_project_raising_adjustment': self.__project_raising_adjustment,
            'log_plan_project_machine': self.__plan_project_machine,
            'log_plan_delta_unit': self.__plan_delta_unit,
            'log_prof_project_machine': self.__prof_project_machine,
            'log_vozv_difference_provider': self.__vozv_difference_provider,
            'log_vozv_project_work_provider': self.__vozv_project_work_provider,
            'log_vozv_project_control_unit': self.__vozv_project_control_unit, 
            'log_indicator_lining': self.__indicator_lining,
            'log_indicator_pendulum_front': self.__indicator_pendulum_front,
            'log_indicator_pendulum_work': self.__indicator_pendulum_work,
            'log_indicator_pendulum_control': self.__indicator_pendulum_control,
            'log_indicator_lifting_left': self.__indicator_lifting_left,
            'log_indicator_lifting_right': self.__indicator_lifting_right,
            'log_side_movement_servo_valve': self.__side_movement_servo_valve,
            'log_right_lifting_servo_valve': self.__right_lifting_servo_valve,
            'log_left_lifting_servo_valve': self.__left_lifting_servo_valve  
        } | self.__auto_branching.log_units()

        # Модель для записи значений юнитов в таблицу
        self.__measurements = StepIndexedDataFramePositionedModel(list(all_units.keys()), LocationVector1D(0.185), self)
        self.__measurements_writer = UnitsToModelWriter(self.__measurements, self.__position_unit, all_units, LocationVector1D(meters = 0.1))
       
        # Маркеры
        self.__marker_model = BaseRailwayMarkerModel()
        for marker, position in self.__options.lining_trip.options.program_task.options.measuring_trip.tags:
            self.__marker_model.insertMarkerAtPosition(marker, position)
        self.__marker_position_syncronizer = RailwayMarkerPositionSyncronizer(position_provider = self.__position_unit, markers = self.__marker_model, parent = self)
        self.__rfid_tag_scanner.tagReceived.connect(lambda tag, rssi: self.__marker_position_syncronizer.syncronizeByMarker(tag))
        
        # Модель для расчета выправки
        self.__lining_processor = LiningProcessor(
            base_rail = BaseRail.Left, # self.__options.lining_trip.options.program_task.options.measuring_trip.options.base_rail,
            machine_parameters = self.__config.get('machine_parameters', {}),
            position_unit = self.__position_unit,
            program_task = self.__program_task,
            measurements = self.__measurements,
            units = self.__units,            
            lining_adjustment = self.__lining_adjustment,
            vozv_adjustment = self.__vozv_adjustment,
            raising_adjustment = self.__raising_adjustment,
            lining_adjustment_percent = self.__lining_adjustment_percent,
            vozv_adjustment_percent = self.__vozv_adjustment_percent,
            raising_adjustment_percent = self.__raising_adjustment_percent,
            project_vozv_adjustment = self.__project_vozv_adjustment,
            project_raising_adjustment = self.__project_raising_adjustment,
            plan_project_machine = self.__plan_project_machine,
            plan_delta_unit = self.__plan_delta_unit,
            prof_project_machine = self.__prof_project_machine,
            vozv_difference_provider = self.__vozv_difference_provider,
            vozv_project_work_provider = self.__vozv_project_work_provider,
            vozv_project_control_unit = self.__vozv_project_control_unit,
            indicator_lining = self.__indicator_lining,
            indicator_pendulum_front = self.__indicator_pendulum_front,
            indicator_pendulum_work = self.__indicator_pendulum_work,
            indicator_pendulum_control = self.__indicator_pendulum_control,
            indicator_lifting_left = self.__indicator_lifting_left,
            indicator_lifting_right = self.__indicator_lifting_right,
            side_movement_servo_valve = self.__side_movement_servo_valve,
            right_lifting_servo_valve = self.__right_lifting_servo_valve,
            left_lifting_servo_valve = self.__left_lifting_servo_valve,
            auto_branching = self.__auto_branching,
            timer = self.__config['models']['connection'].get('lining_timer', 50),
            parent = self)

        self.__indicator_pendulum_front.changed.connect(self.__units.get_readwrite_unit('indicator_pendulum_front').write)
        self.__indicator_pendulum_work.changed.connect(self.__units.get_readwrite_unit('indicator_pendulum_work').write)
        self.__indicator_pendulum_control.changed.connect(self.__units.get_readwrite_unit('indicator_pendulum_control').write)
        self.__indicator_lifting_right.changed.connect(self.__units.get_readwrite_unit('indicator_lifting_right').write)
        self.__indicator_lifting_left.changed.connect(self.__units.get_readwrite_unit('indicator_lifting_left').write)
        self.__indicator_lining.changed.connect(self.__units.get_readwrite_unit('indicator_lining').write)
        self.__right_lifting_servo_valve.changed.connect(self.__units.get_readwrite_unit('lifting_right').write)
        self.__left_lifting_servo_valve.changed.connect(self.__units.get_readwrite_unit('lifting_left').write)
        self.__side_movement_servo_valve.changed.connect(self.__units.get_readwrite_unit('lining').write)
        # self.__measurements_writer.start()
        # self.__lining_processor.start()
    
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/emergency_extraction/process][exited]')
        self.__measurements_writer.stop()
        self.__lining_processor.stop()
        self.__lining_processor.deleteLater()
        self.__marker_position_syncronizer.deleteLater()
        self.__measurements_writer.deleteLater()
        self.__measurements.deleteLater()
        self.__program_task.deleteLater()

        self.__lining_processor = None
        self.__marker_position_syncronizer = None
        self.__measurements_writer = None
        self.__measurements = None
        self.__program_task = None
        self.__options = None


class EmergencyExtractionSuccessState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__result: EmergencyExtractionResultDto = None
    def result(self) ->EmergencyExtractionResultDto:
        return self.__result
    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/emergency_extraction/success][entered]')
        self.__result = event.arguments()[0]
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/emergency_extraction/success][exited]')
        self.__result = None

class EmergencyExtractionErrorState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__error: Exception = None
    def error(self) ->Exception:
        return self.__error
    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/emergency_extraction/error][entered]')
        self.__error = event.arguments()[0]
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/emergency_extraction/error][exited]')
        self.__error = None

class LiningFinalState(QFinalState):
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(parent)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/lining/final][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining/final][exited]')


class ApplicationLiningState(QState):
    def __init__(self, config: dict, units: AbstractUnitProvider, rfid_tag_scanner: AbstractRfidScanner, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        # =========================================================
        # States
        self.select_mode = SelectLiningTripModeState(parent = self)
        self.new_trip_options = NewLiningOptionsState(parent = self)
        self.continue_trip_options = ContinueLiningOptionsState(parent = self)
        self.emergency_extraction_recovery_options = EmergencyExtractionRecoveryOptionsState(parent = self)

        self.lining_process = LiningProcessState(config = config, units = units, rfid_tag_scanner = rfid_tag_scanner, parent = self)
        self.lining_success = LiningSuccessState(parent = self)
        self.lining_error = LiningErrorState(parent = self)
        
        self.emergency_extraction_process = EmergencyExtractionProcessState(config = config, units = units, rfid_tag_scanner = rfid_tag_scanner, parent = self)
        self.emergency_extraction_success = EmergencyExtractionSuccessState(parent = self)
        self.emergency_extraction_error = EmergencyExtractionErrorState(parent = self)

        self.final = LiningFinalState(parent = self)


        # =========================================================
        # Transitions
        self.select_mode.addTransition(self.select_mode.emergency_extraction_recovery_trip, self.emergency_extraction_recovery_options)
        self.select_mode.addTransition(self.select_mode.continue_lining_trip, self.continue_trip_options)
        self.select_mode.addTransition(self.select_mode.new_lining_trip, self.new_trip_options)
        self.select_mode.addTransition(self.select_mode.cancel, self.final)

        self.emergency_extraction_recovery_options.addTransition(self.emergency_extraction_recovery_options.start, self.lining_process)
        self.continue_trip_options.addTransition(self.continue_trip_options.start, self.lining_process)
        self.new_trip_options.addTransition(self.new_trip_options.start, self.lining_process)
        self.emergency_extraction_recovery_options.addTransition(self.emergency_extraction_recovery_options.cancel, self.select_mode)
        self.continue_trip_options.addTransition(self.continue_trip_options.cancel, self.select_mode)
        self.new_trip_options.addTransition(self.new_trip_options.cancel, self.select_mode)

        self.lining_process.addTransition(self.lining_process.success, self.lining_success)
        self.lining_process.addTransition(self.lining_process.error, self.lining_error)
        self.lining_process.addTransition(self.lining_process.emergency_extraction, self.emergency_extraction_process)
        self.emergency_extraction_process.addTransition(self.emergency_extraction_process.success, self.emergency_extraction_success)
        self.emergency_extraction_process.addTransition(self.emergency_extraction_process.error, self.emergency_extraction_error)
        
        self.emergency_extraction_success.addTransition(self.emergency_extraction_success.finish, self.final)
        self.emergency_extraction_error.addTransition(self.emergency_extraction_success.finish, self.final)

        self.lining_success.addTransition(self.lining_success.finish, self.final)
        self.lining_error.addTransition(self.lining_success.finish, self.final)

        self.setInitialState(self.select_mode)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/lining][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/lining][exited]')



