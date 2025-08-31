# This Python file uses the following encoding: utf-8
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from .Travelling import (
    MovingDirection, PicketDirection, BaseRail, SteppedData, LocationVector1D, MeasuringTripReverseType,
    ProgramTaskBaseData, RailPressType
    )

from .Markers import RailwayMarker
from dataclasses import dataclass
from typing import Tuple, Dict, List
import pandas

# ==========================================

@dataclass(frozen=True)
class MeasuringTripOptionsDto:
    track_title: str    
    press_rail: RailPressType
    start_picket: LocationVector1D
    picket_direction: PicketDirection
    moving_direction: MovingDirection
    base_rail: BaseRail = BaseRail.Left

@dataclass(frozen=True)
class MeasuringTripResultDto:
    options: MeasuringTripOptionsDto
    measurements: SteppedData
    tags: List[Tuple[RailwayMarker, float]]
    machine_parameters: dict

    @property
    def length(self) -> float:
        return self.measurements.data.index.max() * self.measurements.step.meters
# ==========================================

@dataclass(frozen=True)
class ProgramTaskCalculationOptionsDto:
    measuring_trip: MeasuringTripResultDto
    restrictions: dict
    start_picket: LocationVector1D
    picket_direction: PicketDirection

    def measuringReverseType(self) -> MeasuringTripReverseType:
        """
        Возвращает какой тип преобразования измерительной поездки необходим при заданных опциях
        измерительной поездки (направление пикетажа, поездка задом или передом) и направлением
        пикетажа при выправке:
            * Nothing -      не менять
            * ReverseSigns - инвертировать знаки 
            * ReverseOrder - инвертировать порядок строк (первое измерение становится последним)
            * ReverseFull -  инвертировать и знаки и порядок строк 
        
        Тип определяется на основании 3-х параметров:
            1-й столбец: Направление пикетажа во время выправки
            2-й столбец: Направление пикетажа во время измерительной поездки
            3-й столбец: Измерительная поездка задом или передом
        """
        lining_picket_direction = self.picket_direction
        measuring_picket_direction = self.measuring_trip.options.picket_direction
        measuring_moving_direction = self.measuring_trip.options.moving_direction

        invsersion_matrix = {
            (PicketDirection.Forward, PicketDirection.Forward, MovingDirection.Forward):   MeasuringTripReverseType.Nothing, 
            (PicketDirection.Forward, PicketDirection.Forward, MovingDirection.Backward):  MeasuringTripReverseType.ReverseSigns, 
            (PicketDirection.Forward, PicketDirection.Backward, MovingDirection.Forward):  MeasuringTripReverseType.ReverseFull, 
            (PicketDirection.Forward, PicketDirection.Backward, MovingDirection.Backward): MeasuringTripReverseType.ReverseOrder,    
            (PicketDirection.Backward, PicketDirection.Forward, MovingDirection.Forward):  MeasuringTripReverseType.ReverseFull, 
            (PicketDirection.Backward, PicketDirection.Forward, MovingDirection.Backward): MeasuringTripReverseType.ReverseOrder, 
            (PicketDirection.Backward, PicketDirection.Backward, MovingDirection.Forward): MeasuringTripReverseType.Nothing, 
            (PicketDirection.Backward, PicketDirection.Backward, MovingDirection.Backward): MeasuringTripReverseType.ReverseSigns 
        }
        return invsersion_matrix.get((lining_picket_direction, measuring_picket_direction, measuring_moving_direction))

    def measuringDetailedRestrictionsReverseType(self) -> MeasuringTripReverseType:
        """
        Возвращает какой тип преобразования измерительной поездки необходим при заданных опциях
        измерительной поездки (направление пикетажа, поездка задом или передом) ДЛЯ РАСЧЁТА ДЕТАЛЬНОГО ОГРАНИЧЕНИЯ:
            * Nothing -      не менять
            * ReverseOrder - инвертировать порядок строк (первое измерение становится последним)
        
        Тип определяется на основании 2-х параметров:
            1-й столбец: Направление пикетажа во время измерительной поездки
            2-й столбец: Измерительная поездка задом или передом
        """
        measuring_picket_direction = self.measuring_trip.options.picket_direction
        measuring_moving_direction = self.measuring_trip.options.moving_direction

        invsersion_matrix = {
            (PicketDirection.Forward, MovingDirection.Forward):   MeasuringTripReverseType.Nothing, 
            (PicketDirection.Forward, MovingDirection.Backward):  MeasuringTripReverseType.ReverseOrder, 
            (PicketDirection.Backward, MovingDirection.Forward):  MeasuringTripReverseType.Nothing, 
            (PicketDirection.Backward, MovingDirection.Backward): MeasuringTripReverseType.ReverseOrder,    
        }
        return invsersion_matrix.get((measuring_picket_direction, measuring_moving_direction))


@dataclass(frozen=True)
class ProgramTaskCalculationResultDto:
    options: ProgramTaskCalculationOptionsDto
    base: ProgramTaskBaseData
    calculated_task: SteppedData
    summary: pandas.DataFrame

    @property
    def start_picket(self) -> LocationVector1D:
        return self.options.start_picket 
    
    @property
    def end_picket(self) -> LocationVector1D:
        return LocationVector1D(meters = self.start_picket.meters + self.length*self.options.picket_direction.multiplier())
    
    @property
    def length(self) -> float:
        return self.calculated_task.data.index.max()*self.calculated_task.step.meters
    
    def createStepModel(self) -> StepIndexedDataFramePositionedModel:
        model = StepIndexedDataFramePositionedModel(
            columns = self.calculated_task.data.columns, 
            step = self.calculated_task.step
        )
        model.reset(self.calculated_task.step, self.calculated_task.data)
        return model
    
# ==========================================

@dataclass(frozen=True)
class LiningTripOptionsDto:
    filename: str
    program_task: ProgramTaskCalculationResultDto
    picket_direction: PicketDirection
    start_picket: LocationVector1D
    press_rail: RailPressType
    auto_branching: bool 
    # При новой поездке оба поля пусты. При повторной -- в них уже что-то есть
    current_picket: LocationVector1D
    previous_measurements: SteppedData | None = None

@dataclass(frozen=True)
class LiningTripResultDto:
    options: LiningTripOptionsDto
    measurements: SteppedData

@dataclass(frozen=True)
class EmergencyExtractionOptionsDto:
    lining_trip: LiningTripResultDto
    start_extraction_picket: LocationVector1D
    extraction_trajectory: SteppedData
    slope: float
    velocity: float
    length: float
    auto_branching: bool 
    

@dataclass(frozen=True)
class EmergencyExtractionResultDto:
    options: EmergencyExtractionOptionsDto
    measurements: SteppedData

# ==========================================
