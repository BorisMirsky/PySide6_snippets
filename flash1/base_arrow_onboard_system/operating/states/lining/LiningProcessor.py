# This Python file uses the following encoding: utf-8
from domain.dto.DiscreteSignals import DiscreteSignalsContainer
from domain.dto.Travelling import BaseRail, LocationVector1D
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.calculations.helpers import project_to_machine_chord
from presentation.machine.units.DiscreteSignalsUnit import DiscreteSignalsUnit

from PySide6.QtCore import QObject, QTimer
from typing import Optional


class LiningProcessor(QObject):
    def __init__(self,
        # base
        base_rail: BaseRail,
        machine_parameters: dict,
        position_unit: AbstractReadUnit[float],
        program_task: AbstractPositionedTableModel,
        measurements: AbstractPositionedTableModel,
        units: AbstractUnitProvider,    
        # Добавки к стрелам задаваемые пользователем
        lining_adjustment: AbstractReadUnit[float],
        vozv_adjustment: AbstractReadUnit[float],
        raising_adjustment: AbstractReadUnit[float],
        lining_adjustment_percent: AbstractReadUnit[float], 
        vozv_adjustment_percent: AbstractReadUnit[float],
        raising_adjustment_percent: AbstractReadUnit[float],
        project_vozv_adjustment: AbstractReadUnit[float],
        project_raising_adjustment: AbstractReadUnit[float],
        # calculated out controls
        # Проектные значения
        plan_project_machine: AbstractReadWriteUnit[float],
        plan_delta_unit: AbstractReadWriteUnit[float],
        prof_project_machine: AbstractReadWriteUnit[float],
        vozv_difference_provider: AbstractReadWriteUnit[float],
        vozv_project_work_provider: AbstractReadWriteUnit[float],
        vozv_project_control_unit: AbstractReadWriteUnit[float],
        # Индикаторы
        indicator_lining: AbstractReadWriteUnit[float],
        indicator_pendulum_front: AbstractReadWriteUnit[float],
        indicator_pendulum_work: AbstractReadWriteUnit[float],
        indicator_pendulum_control: AbstractReadWriteUnit[float],
        indicator_lifting_left: AbstractReadWriteUnit[float],
        indicator_lifting_right: AbstractReadWriteUnit[float],
        # Сервовентили
        side_movement_servo_valve: AbstractReadWriteUnit[float],
        right_lifting_servo_valve: AbstractReadWriteUnit[float],
        left_lifting_servo_valve: AbstractReadWriteUnit[float],
        # lining timer
        timer: int = 50,
        # QObject parent
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        # base
        self.__base_rail: BaseRail = base_rail
        self.__machine_parameters: dict = machine_parameters
        self.__position_unit: AbstractReadUnit[float] = position_unit
        self.__program_task: AbstractPositionedTableModel = program_task
        self.__measurements: AbstractPositionedTableModel = measurements
        self.__units: AbstractUnitProvider = units
        # sensors
        self.__sattelite: AbstractReadUnit[float] = self.__units.get_read_only_unit('satellite')
        self.__strelograph_work: AbstractReadUnit[float] = self.__units.get_read_only_unit('strelograph_work')
        self.__pendulum_front: AbstractReadUnit[float] = self.__units.get_read_only_unit('pendulum_front')
        self.__pendulum_work: AbstractReadUnit[float] = self.__units.get_read_only_unit('pendulum_work')
        self.__pendulum_control: AbstractReadUnit[float] = self.__units.get_read_only_unit('pendulum_control')
        self.__right_sagging: AbstractReadUnit[float] = self.__units.get_read_only_unit('sagging_right')
        self.__left_sagging: AbstractReadUnit[float] = self.__units.get_read_only_unit('sagging_left')
        self.__discrete_signals: AbstractReadUnit[DiscreteSignalsContainer] = DiscreteSignalsUnit(self.__units.get_read_only_unit('discrete_signals'))
        # Пользовательские задатчики
        self.__lining_adjustment: AbstractReadUnit[float] = lining_adjustment
        self.__vozv_adjustment: AbstractReadUnit[float] = vozv_adjustment
        self.__raising_adjustment: AbstractReadUnit[float] = raising_adjustment
        self.__lining_adjustment_percent: AbstractReadUnit[float] = lining_adjustment_percent
        self.__vozv_adjustment_percent: AbstractReadUnit[float] = vozv_adjustment_percent
        self.__raising_adjustment_percent: AbstractReadUnit[float] = raising_adjustment_percent
        self.__project_vozv_adjustment: AbstractReadUnit[float] = project_vozv_adjustment
        self.__project_raising_adjustment: AbstractReadUnit[float] = project_raising_adjustment
        # Проектные значения
        self.__plan_project_machine: AbstractReadWriteUnit[float] = plan_project_machine
        self.__plan_delta_unit: AbstractReadWriteUnit[float] = plan_delta_unit
        self.__prof_project_machine: AbstractReadWriteUnit[float] = prof_project_machine
        self.__vozv_difference_provider: AbstractReadWriteUnit[float] = vozv_difference_provider
        self.__vozv_project_work_provider: AbstractReadWriteUnit[float] = vozv_project_work_provider
        self.__vozv_project_control_unit: AbstractReadWriteUnit[float] = vozv_project_control_unit
        # Индикаторы
        self.__indicator_lining: AbstractReadWriteUnit[float] = indicator_lining
        self.__indicator_pendulum_front: AbstractReadWriteUnit[float] = indicator_pendulum_front
        self.__indicator_pendulum_work: AbstractReadWriteUnit[float] = indicator_pendulum_work
        self.__indicator_pendulum_control: AbstractReadWriteUnit[float] = indicator_pendulum_control
        self.__indicator_lifting_left: AbstractReadWriteUnit[float] = indicator_lifting_left
        self.__indicator_lifting_right: AbstractReadWriteUnit[float] = indicator_lifting_right
        # Сервовентили
        self.__side_movement_servo_valve: AbstractReadWriteUnit[float] = side_movement_servo_valve
        self.__right_lifting_servo_valve: AbstractReadWriteUnit[float] = right_lifting_servo_valve
        self.__left_lifting_servo_valve: AbstractReadWriteUnit[float] = left_lifting_servo_valve
        # other
        self.__lining_system_sattelite_multiplier = int(machine_parameters.get('lining_system_movable', False))
        self.__levelling_system_sattelite_multiplier = int(machine_parameters.get('levelling_system_movable', False))

        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.__processLining)
        self.__timer.setInterval(timer)
  
    def start(self):
        self.__timer.start()
    def stop(self):
        self.__timer.stop()
        self.__send_zero_to_servo_valves()
        self.__send_zero_to_indicators()

    def __send_zero_to_servo_valves(self):
        self.__side_movement_servo_valve.write(0)
        self.__right_lifting_servo_valve.write(0)
        self.__left_lifting_servo_valve.write(0)

    def __send_zero_to_indicators(self):
        self.__indicator_lining.write(0)
        self.__indicator_lifting_left.write(0)
        self.__indicator_lifting_right.write(0)
        self.__indicator_pendulum_front.write(0)
        self.__indicator_pendulum_work.write(0)
        self.__indicator_pendulum_control.write(0)
        
        
    def __processLining(self):

        # Текущее состояние системы
        current_position = self.__position_unit.read()# позиция
        current_discrete_signals: DiscreteSignalsContainer = self.__discrete_signals.read()# дискретные сигналы
        work_position = current_position + self.__sattelite.read()# положение в рабочей зоне
        front_position = current_position + self.__machine_parameters['front_horde_plan']# положение в передней зоне 
        control_position = current_position - self.__machine_parameters['back_horde_plan']# положение в задней зоне (контрольного маятника)
        # Текущее состояние системы со сдвигом на хорды
        program_task_front = self.__program_task.rowAtPosition(LocationVector1D(front_position))
        program_task_work = self.__program_task.rowAtPosition(LocationVector1D(work_position))
        program_task_control = self.__program_task.rowAtPosition(LocationVector1D(control_position))
        
        if program_task_work is None:
            self.__send_zero_to_servo_valves()
            self.__send_zero_to_indicators()
            return

        front_delta_multiplier = program_task_front.get('front_delta_multiplier', 1) if program_task_front is not None else 1

        # ЗАДАЕМ ПРОФИЛЬ
        # Базовый рельс правый если возвышение положительное
        self.__base_rail = BaseRail.Right if program_task_work['vozv_prj'] > 0 else BaseRail.Left
        
        # Пересчет стрел в профиле на хорду машины с учетом сателлита
        front_chord_profile = self.__machine_parameters['front_horde_prof'] - self.__sattelite.read()*self.__levelling_system_sattelite_multiplier
        back_chord_profile = self.__machine_parameters['back_horde_prof'] + self.__sattelite.read()*self.__levelling_system_sattelite_multiplier
        M = back_chord_profile/(back_chord_profile+front_chord_profile)
        prof_prj = program_task_work['prof_prj']
        prof_prj_machine = project_to_machine_chord(prof_prj, 10, front_chord_profile, back_chord_profile)
        
        # Вычисляем подъемку
        prof_delta_front = (program_task_front['prof_delta'] if program_task_front is not None else 0)*front_delta_multiplier        
        prof_dF = program_task_work.get('prof_dF', 0)
        prof_difference_right = prof_prj_machine + prof_dF - M*prof_delta_front*-1 - self.__right_sagging.read()
        prof_difference_left = prof_prj_machine + prof_dF - M*prof_delta_front*-1 - self.__left_sagging.read()
        # добавляем задатчик
        prof_difference_right = prof_difference_right + self.__raising_adjustment.read() + prof_difference_right*self.__raising_adjustment_percent.read()/100
        prof_difference_left = prof_difference_left + self.__raising_adjustment.read() + prof_difference_left*self.__raising_adjustment_percent.read()/100
        
        # ВЫЧИСЛЯЕМ ВОЗВЫШЕНИЕ
        # Берем показания записи переднего маятника для рабочей зоны
        # OBSOLETE:
        # measurements_in_work_area = self.__measurements.rowAtPosition(LocationVector1D(work_position - self.__machine_parameters['front_horde_plan']))
        # if measurements_in_work_area is not None:
        #     vozv_fact_work = measurements_in_work_area.pendulum_front
        # else:
        #     vozv_fact_work = (self.__pendulum_front.read() + self.__pendulum_work.read())/2
        vozv_fact_work = self.__pendulum_work.read()

        vozv_delta_front = (program_task_front['vozv_prj'] - self.__pendulum_front.read()) if program_task_front is not None else 0
        vozv_delta_front = vozv_delta_front * front_delta_multiplier
        vozv_dF = program_task_work.get('vozv_dF', 0)
        vozv_difference = (program_task_work['vozv_prj'] + vozv_dF - M*vozv_delta_front - vozv_fact_work)*-1
        # добавляем задатчики
        # TODO: поменять знаки
        vozv_difference = vozv_difference - self.__vozv_adjustment.read() - vozv_difference*self.__vozv_adjustment_percent.read()/100
        
        if self.__base_rail == BaseRail.Right:           
            prof_difference_left = prof_difference_left - vozv_difference
            
        elif self.__base_rail == BaseRail.Left:
            prof_difference_right = prof_difference_right + vozv_difference

        # todo: Если разница между проектным возвышение в контольной точке и контрольным маятником > 1 мм,
        # то делаем поправку.                                     
                         
        # Подаем ток на ПРАВЫЙ серво-вентиль если есть сигнал разрешения подъемки
        if current_discrete_signals.enable_lifting_right:
            # print(f'RAISING RIGHT: {prof_difference_right}')
            self.__right_lifting_servo_valve.write(prof_difference_right)
        else:
            self.__right_lifting_servo_valve.write(0)
        
        # Подаем ток на ЛЕВЫЙ серво-вентиль если есть сигнал разрешения подъемки
        if current_discrete_signals.enable_lifting_left:
            # print(f'RAISING LEFT: {prof_difference_left}')
            self.__left_lifting_servo_valve.write(prof_difference_left)
        else:
            self.__left_lifting_servo_valve.write(0)
            
        # Устанавливаем индикаторы подъемки
        self.__indicator_lifting_left.write(prof_difference_left)
        self.__indicator_lifting_right.write(prof_difference_right)
        
        # Выводим на интерфейс проектный профиль
        self.__prof_project_machine.write(prof_prj_machine) 
        
        # Индикатор маятника рабочего
        # self.__indicator_pendulum_work.write(vozv_difference)
        self.__indicator_pendulum_work.write((program_task_work['vozv_prj'] - vozv_fact_work)*-1)
        # передаем на интерфейс
        self.__vozv_difference_provider.write(vozv_difference)
        self.__vozv_project_work_provider.write(program_task_work['vozv_prj'])
        
        # Индикатор маятника контрольного(заднего)
        if program_task_control is not None:
            vozv_difference_control = program_task_control['vozv_prj'] - self.__pendulum_control.read()
            self.__indicator_pendulum_control.write(vozv_difference_control*-1)
            self.__vozv_project_control_unit.write(program_task_control['vozv_prj'])
        else:
            self.__indicator_pendulum_control.write(0)

        # ЗАДАЕМ ПЛАН         
        # Пересчет стрел в плане на хорду машины с учетом сателлита
        front_chord_plan = self.__machine_parameters['front_horde_plan'] - self.__sattelite.read() * self.__lining_system_sattelite_multiplier
        back_chord_plan = self.__machine_parameters['back_horde_plan'] + self.__sattelite.read() * self.__lining_system_sattelite_multiplier
        plan_prj = program_task_work['plan_prj']
        plan_prj_machine = project_to_machine_chord(plan_prj, 10, front_chord_plan, back_chord_plan)
        
        # вычисляем сдвижку
        M = back_chord_plan/(back_chord_plan+front_chord_plan)        
        plan_delta_front = (program_task_front['plan_delta'] if program_task_front is not None else 0)*front_delta_multiplier
        
        plan_dF = program_task_work.get('plan_dF', 0)
        plan_difference = plan_prj_machine + plan_dF - M*plan_delta_front*-1 - self.__strelograph_work.read()
        
        # добавляем задатчики
        plan_difference = plan_difference + self.__lining_adjustment.read() + plan_difference*self.__lining_adjustment_percent.read()/100
        
        # Подаем ток на серво-вентиль РИХТОВКИ если есть сигнал разрешения сдвижки        
        if current_discrete_signals.enable_shifting:
            # print(f'LINING: {plan_difference}')
            self.__side_movement_servo_valve.write(plan_difference)
        else:
            self.__side_movement_servo_valve.write(0)
        
        # Индикатор
        self.__indicator_lining.write(plan_difference)
        # Выводим на интерфейс
        self.__plan_project_machine.write(plan_prj_machine) 
        self.__plan_delta_unit.write(program_task_work['plan_delta'])
