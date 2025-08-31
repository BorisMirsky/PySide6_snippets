from .Travelling import BaseRail
from dataclasses import dataclass
from enum import Enum

class LiftingServoValveMovement(Enum):
    Up = 1
    Stop = 0
    Down = -1

    @staticmethod
    def from_signal_bits(up_signal: bool, down_signal: bool):
        if (up_signal == False) and (down_signal == False):
            return LiftingServoValveMovement.Stop
        elif (up_signal == True) and (down_signal == False):
            return LiftingServoValveMovement.Up
        elif (up_signal == False) and (down_signal == True):
            return LiftingServoValveMovement.Down
        elif (up_signal == True) and (down_signal == True):
            return LiftingServoValveMovement.Stop

class ShiftingServoValveMovement(Enum):
    Right = 1
    Stop = 0
    Left = -1

    @staticmethod
    def from_signal_bits(left_signal: bool, right_signal: bool):
        if (left_signal == False) and (right_signal == False):
            return ShiftingServoValveMovement.Stop
        elif (left_signal == True) and (right_signal == False):
            return ShiftingServoValveMovement.Left
        elif (left_signal == False) and (right_signal == True):
            return ShiftingServoValveMovement.Right
        elif (left_signal == True) and (right_signal == True):
            return ShiftingServoValveMovement.Stop

@dataclass(frozen = True, slots = True)
class DiscreteSignalsContainer:
    # =======================================================
    press: bool # Левый либо правый прижим
    base_rail: BaseRail # Базовый рельс
    # =======================================================
    enable_lifting_right: bool # Разрешение на правую подъёмку
    lifting_right_movement: LiftingServoValveMovement # Направление движения правого ПРУ
    # =======================================================
    enable_lifting_left: bool # Разрешение на левую подъёмку
    lifting_left_movement: LiftingServoValveMovement # Направление движения левого ПРУ
    # =======================================================
    enable_shifting: bool # Разрешение на рихтовку
    shifting_movement: ShiftingServoValveMovement # Направление рихтовки
    # =======================================================

    @staticmethod
    def from_code(current_signals: int):
        return DiscreteSignalsContainer(
                press = bool((current_signals >> 2) & 1),
                base_rail = BaseRail.Left if ((current_signals >> 3) & 1) == 0 else BaseRail.Right,
                enable_lifting_right = bool((current_signals >> 4) & 1),
                lifting_right_movement = LiftingServoValveMovement.from_signal_bits(
                    up_signal = bool((current_signals >> 8) & 1), down_signal = bool((current_signals >> 7) & 1)
                ),
                enable_lifting_left = bool((current_signals >> 5) & 1),
                lifting_left_movement = LiftingServoValveMovement.from_signal_bits(
                    up_signal = bool((current_signals >> 10) & 1), down_signal = bool((current_signals >> 9) & 1)
                ),
                enable_shifting = bool((current_signals >> 6) & 1),
                shifting_movement = ShiftingServoValveMovement.from_signal_bits(
                    left_signal = bool((current_signals >> 12) & 1), right_signal = bool((current_signals >> 11) & 1)
                ),
            )