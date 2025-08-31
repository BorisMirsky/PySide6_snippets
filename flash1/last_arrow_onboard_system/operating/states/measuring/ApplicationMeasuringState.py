# This Python file uses the following encoding: utf-8
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.models.UnitsToModelWriter import UnitsToModelWriter
from domain.markers.RailwayMarkersSyncronization import RailwayMarkerPositionWriter
from domain.markers.BaseRailwayMarkerModel import BaseRailwayMarkerModel
from domain.markers.AbstractMarkerModel import AbstractMarkerModel
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from domain.dto.Workflow import MeasuringTripOptionsDto, MeasuringTripResultDto
from domain.dto.Travelling import LocationVector1D, SteppedData
from domain.dto.Markers import RailwayMarker, RailwayMarkerType
from presentation.machine.units.StrelographUnit import StrelographUnit

from PySide6.QtStateMachine import QStateMachine, QFinalState, QState
from PySide6.QtCore import QEvent, Signal
from typing import Optional, Tuple, Dict
import pandas


class MeasuringOptionsState(QState):
    start: Signal = Signal(MeasuringTripOptionsDto)
    cancel: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.setObjectName('MeasuringOptionsState')
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/measuring/options][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/measuring/options][exited]')

class MeasuringProcessState(QState):
    success: Signal = Signal(MeasuringTripResultDto)
    error: Signal = Signal(Exception)
    def __init__(self, config: dict, units: AbstractUnitProvider, rfid_tag_scanner: AbstractRfidScanner, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.setObjectName('MeasuringProcessState')
        # ======================================================
        self.__config: dict = config
        self.__position_unit: AbstractReadWriteUnit[float] = None
        self.__units: AbstractUnitProvider = units
        self.__sensors: Dict[str, AbstractReadUnit] = units.get_all_read_only_units()
        self.__controls: Dict[str, AbstractReadWriteUnit] = units.get_all_readwrite_units()
        self.__rfid_tag_scanner: AbstractRfidScanner = rfid_tag_scanner
        # ======================================================
        self.__options: MeasuringTripOptionsDto = None
        self.__measurements: AbstractPositionedTableModel = None
        self.__measurements_writer: UnitsToModelWriter = None
        self.__railway_marker_models: Dict[RailwayMarkerType, Tuple[AbstractMarkerModel, RailwayMarkerPositionWriter]] = None
    def config(self) ->dict:
        return self.__config
    def position_unit(self) ->AbstractReadWriteUnit[float]:
        return self.__position_unit
    def sensors(self) ->Dict[str, AbstractReadUnit]:
        return self.__sensors
    def rfid_tag_scanner(self) ->AbstractRfidScanner:
        self.__rfid_tag_scanner

    def options(self) ->MeasuringTripOptionsDto:
        return self.__options
    def measurements(self) ->AbstractPositionedTableModel:
        return self.__measurements
    def measurements_writer(self) ->UnitsToModelWriter:
        return self.__measurements_writer
    def marker_models(self) ->Dict[RailwayMarkerType, Tuple[AbstractMarkerModel, RailwayMarkerPositionWriter]]:
        return self.__railway_marker_models

    def finishMeasuringProcess(self) ->None:
        markers = sum([model.markers() for model, _ in self.__railway_marker_models.values()], [])
        print(f'Counted markers: {len(markers)}')
        self.success.emit(MeasuringTripResultDto(
            options = self.__options, 
            measurements = SteppedData(self.__measurements.dataframe(), self.__measurements.step()), 
            tags = markers,
            machine_parameters = self.__config.get('machine_parameters')))

    def startMeasurementsWriter(self):
        if self.__measurements_writer:
            self.__position_unit.write(0)
            self.__measurements_writer.start()
    def stopMeasurementsWriter(self):
        if self.__measurements_writer:
            self.__measurements_writer.stop()
    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/measuring/process][entered]')
        self.__options = event.arguments()[0]

        # Разрешение на общение с контроллером машины
        self.__controls['enable_register'].write(1) # разрешаем общение с контроллером машины
        # print(f"enable_register={self.__controls['enable_register'].read()}")

        # Установка прижима для стелографа
        strelograph_unit: StrelographUnit = self.__units.get_read_only_unit('strelograph_work')
        strelograph_unit.set_press_type(self.__options.press_rail)
        
        self.__railway_marker_models = dict()
        self.__position_unit = self.__units.create_position_unit(self.__options.moving_direction)
        self.__position_unit.write(0)        
        
        for marker_type in RailwayMarkerType:
            marker_model = BaseRailwayMarkerModel(self)
            marker_writer = RailwayMarkerPositionWriter(position_provider = self.__position_unit, markers = marker_model, parent = self)
            self.__railway_marker_models[marker_type] = (marker_model, marker_writer)

        # self.__rfid_tag_scanner.tagReceived.connect(lambda tag, rssi: self.__railway_marker_models[RailwayMarkerType.RfidTag][1].markerReceived(tag))
        self.__rfid_tag_scanner.tagReceived.connect(self.__tagReceivedHandler)
        self.__measurements = StepIndexedDataFramePositionedModel(columns = list(self.__sensors.keys()), step = LocationVector1D(0.185))
        self.__measurements_writer = UnitsToModelWriter(self.__measurements, self.__position_unit, self.__sensors, LocationVector1D(meters = 0.1))

    def __tagReceivedHandler(self, tag, rssi):
        self.__railway_marker_models[RailwayMarkerType.RfidTag][1].markerReceived(tag)

    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/measuring/process][exited]')
        self.__controls['enable_register'].write(0) # запрещаем общение с контроллером машины
        self.__measurements_writer.stop()
        self.__measurements_writer.deleteLater()
        self.__measurements.deleteLater()
        self.__railway_marker_models = None
        self.__measurements_writer = None
        self.__measurements = None
        self.__options = None

class MeasuringSuccessState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.setObjectName('MeasuringSuccessState')
        self.__result: MeasuringTripResultDto = None
    def result(self) ->MeasuringTripResultDto:
        return self.__result
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/measuring/success][entered]')
        self.__result = event.arguments()[0]
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/measuring/success][exited]')
        self.__result = None

class MeasuringErrorState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.setObjectName('MeasuringErrorState')
        self.__error: Exception = None
    def error(self) ->Exception:
        return self.__error
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/measuring/error][entered]')
        self.__error = event.arguments()[0]
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/measuring/error][exited]')
        self.__error = None

class MeasuringFinalState(QFinalState):
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(parent)
        self.setObjectName('MeasuringFinalState')
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/measuring/final][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/measuring/final][exited]')

class ApplicationMeasuringState(QState):
    def __init__(self, config: dict, units: AbstractUnitProvider, rfid_tag_scanner: AbstractRfidScanner, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.setObjectName('ApplicationMeasuringState')
        self.options = MeasuringOptionsState(self)
        self.process = MeasuringProcessState(config, units, rfid_tag_scanner, self)
        self.success = MeasuringSuccessState(self)
        self.error = MeasuringErrorState(self)
        self.final = MeasuringFinalState(self)

        self.options.addTransition(self.options.start, self.process)
        self.options.addTransition(self.options.cancel, self.final)
        self.process.addTransition(self.process.success, self.success)
        self.process.addTransition(self.process.error, self.error)
        self.success.addTransition(self.success.finish, self.final)
        self.error.addTransition(self.error.finish, self.final)
        self.setInitialState(self.options)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/measuring][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/measuring][exited]')


