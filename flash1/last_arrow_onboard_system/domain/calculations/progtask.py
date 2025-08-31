import numpy as np
import pandas as pd
from typing import Callable, Tuple
from cantok import AbstractToken, SimpleToken
from .track_funcs import (
    horde_to_horde, data_to_0625, first_project_plan, track_calculation, project_profile
)

from .consts import SYM_CHORD_0185, SYM_CHORD_10
from .plan_model import build_plan_summary, TrackLevelProjectModel
from domain.dto.Workflow import ProgramTaskCalculationOptionsDto, MeasuringTripResultDto
from domain.dto.Travelling import ProgramTaskBaseData, LocationVector1D, SteppedData, MeasuringTripReverseType
from .helpers import ( change_sym_chord, add_sym_chords_to_measurements,
    prep_detailed_restrictions, sdv_to_ver, calc_podjemki, 
    reverse_measuring_trip, plan_column_names, prof_column_names
)
from .project_plan_and_profile.bounded_track_calculation import PlanCalculation
from .project_plan_and_profile.split_profile_calculation import ProfileCalculation
from .project_plan_and_profile.smart_track_split import SmartSplitPlanCalculation
import domain.calculations.project_plan_and_profile.split_plan_calculation_2 as plan_calculation_2

def machine_task_from_base_data(base_task: ProgramTaskBaseData, options: ProgramTaskCalculationOptionsDto, data_step: float = 0.185) -> SteppedData:
    base_step = base_task.step.meters
    
    # Вычисляем длину программного задания
    task_length = data_to_0625(np.array(range(len(base_task.plan)))*base_step, base_step, data_step).shape[0]
    # measurements = options.measuring_trip.measurements.data
    measurements = base_task.measurements_processed.data
    # machine_params = options.measuring_trip.machine_parameters
    
    # Собираем основные данные
    result = {
        'plan_fact':        None, 
        'plan_prj':         np.array(base_task.plan['plan_prj']),
        'plan_delta':       np.array(base_task.plan['plan_delta']), 
        'vozv_fact':        None, 
        'vozv_prj':         np.array(base_task.plan['vozv_prj']),
        'vozv_delta':       None,
        'prof_fact':        None,        
        'prof_fact_left':   None, 
        'prof_fact_right':  None, 
        'prof_prj':         np.array(base_task.prof['prof_prj']),
        'prof_delta':       np.array(base_task.prof['prof_delta']),
        'prof_delta_left':  None,
        'prof_delta_right': None,        
    }
    result['plan_fact'] =       measurements.strelograph_work[:task_length]
    result['plan_prj'] =        data_to_0625(result['plan_prj'], base_step, data_step)
    result['plan_delta'] =      sdv_to_ver(result['plan_delta'], base_step, data_step)
    
    result['vozv_fact'] =       np.array(measurements.pendulum_work.iloc[:task_length])
    result['vozv_prj'] =        data_to_0625(result['vozv_prj'], base_step, data_step)
    result['vozv_delta'] =      result['vozv_prj'] - result['vozv_fact']
    
    result['prof_fact'] =       measurements.sagging_left[:task_length]
    result['prof_fact_left'] =  measurements.sagging_left[:task_length]
    result['prof_fact_right'] = measurements.sagging_right[:task_length]
    result['prof_prj'] =        data_to_0625(result['prof_prj'], base_step, data_step)
    result['prof_delta'] =      sdv_to_ver(result['prof_delta'], base_step, data_step)
    
    result['prof_delta_left'], result['prof_delta_right'] = calc_podjemki(
                                                                urov_naturn = result['vozv_fact'], 
                                                                urov_project = result['vozv_prj'], 
                                                                podjemki = result['prof_delta'] )
    
    result['rail_length'] =     data_to_0625(base_task.plan['rail_length'], base_step, data_step)
    result['fastening_tmp'] =   data_to_0625(base_task.plan['fastening_tmp'], base_step, data_step)
    result['ballast_need'] =    data_to_0625(base_task.plan['ballast_need'], base_step, data_step)
    result['a_nepog_fact'] =    data_to_0625(base_task.plan['a_nepog_fact'], base_step, data_step)
    result['psi_fact'] =        data_to_0625(base_task.plan['psi_fact'], base_step, data_step)
    result['v_wheel_fact'] =    data_to_0625(base_task.plan['v_wheel_fact'], base_step, data_step)
    result['a_nepog_prj'] =     data_to_0625(base_task.plan['a_nepog_prj'], base_step, data_step)
    result['psi_prj'] =         data_to_0625(base_task.plan['psi_prj'], base_step, data_step)
    result['v_wheel_prj'] =     data_to_0625(base_task.plan['v_wheel_prj'], base_step, data_step)

    # segment_restrictions = prep_detailed_restrictions(
    #         picket_start=0, 
    #         data_size=task_length, 
    #         data_step=data_step, 
    #         restrictions_ui=options.restrictions.get('segments'))
    segment_restrictions = prep_detailed_restrictions(
            start_picket=options.start_picket, 
            picket_direction=options.picket_direction,
            data_size=task_length, 
            data_step=data_step, 
            restrictions_ui=options.restrictions.get('segments'))
    result['ubound_plan'] =     segment_restrictions['ubound_plan'][:task_length]
    result['lbound_plan'] =     segment_restrictions['lbound_plan'][:task_length]
    result['ubound_prof'] =     segment_restrictions['ubound_prof'][:task_length]
    result['lbound_prof'] =     segment_restrictions['lbound_prof'][:task_length]

    # Приводим к одинаковой размерности
    if result['plan_delta'].shape[0] > task_length:
        su = result['plan_delta'].shape[0] - task_length
        result['plan_delta'] = result['plan_delta'][:-1*su] 

    if result['prof_delta'].shape[0] > task_length:
        su = result['prof_delta'].shape[0] - task_length
        result['prof_delta'] = result['prof_delta'][:-1*su]
        
    task = pd.DataFrame(result).round(3)
    task.index.name = 'step'

    return SteppedData(data = task, step = LocationVector1D(meters=data_step))


def calctask_base(
                    plan_fact: np.ndarray, 
                    prof_fact: np.ndarray,
                    level_fact: np.ndarray,
                    restrictions: dict[str, np.ndarray], 
                    data_step: float,
                    optimization_parameters: dict = None,
                    cancellation_token: AbstractToken = SimpleToken(),
                    progress: Callable[[float], float] = print) -> dict[str, pd.DataFrame]:
    """
    Расчитывает программное задание и возвращает словарь датафреймов.
    @Params:
        plan_fact - показания стрелографа, пересчитанные из хорды машины в симметричную хорду
        prof_fact - просадки, пересчитанные из хорды машины в симметричную хорду
        level_fact - показания маятника рабочего
        restrictions: dict[str, np.ndarray] = {
            'ubound_plan': [],
            'lbound_plan': [],
            'ubound_prof': [],
            'lbound_prof': [],
            'v_max': [],
        }
        machine_params: dict[str, float] = {
            'measures_step': 0.185,    # шаг у ВПИ
            'back_horde_plan': 4.1,     # хорды ВПИ
            'front_horde_plan': 17.4,
            'back_horde_prof': 2.7,
            'front_horde_prof': 14.3,
            'base_rail': 0,             # 0 - левый, 1 - правый
        }
    @Returns:
        {
            'plan': EV_plan,
            'prof': EV_profile,
            'alc_plan': alc_plan,
            'alc_prof': alc_profile,
            'alc_level': alc_urov
        }
    """           
    
    # Пересчет плана пути на шаг SYM_CHORD_10
    msv_rix = data_to_0625(plan_fact, data_step, SYM_CHORD_10)
    # print(f'msv_rix={msv_rix}')

    # Пересчет уровня (ВНР) на шаг SYM_CHORD_10
    msv_urov = data_to_0625(level_fact, data_step, SYM_CHORD_10)
    if msv_urov.shape[0]>msv_rix.shape[0]:
        msv_urov=msv_urov[:-1]     
    
    # Пересчет профиля на шаг SYM_CHORD_10
    msv_pro = data_to_0625(prof_fact, data_step, SYM_CHORD_10)
            
    # пересчет ограничений
    ubound_plan = data_to_0625(restrictions['ubound_plan'], data_step, SYM_CHORD_10)
    lbound_plan = data_to_0625(restrictions['lbound_plan'], data_step, SYM_CHORD_10)
    ubound_prof = data_to_0625(restrictions['ubound_prof'], data_step, SYM_CHORD_10)
    lbound_prof = data_to_0625(restrictions['lbound_prof'], data_step, SYM_CHORD_10)        
    v_max       = data_to_0625(restrictions['v_max'], data_step, SYM_CHORD_10)      # Пересчет максимальной скорости
            
    # РАССЧЕТ        
    if optimization_parameters is None:
        optimization_parameters = dict()

    ax = first_project_plan(
            plan_fact, 
            msv_rix, 
            length_start=optimization_parameters.get('plan_length_start', 100), 
            min_value=optimization_parameters.get('plan_min_value', 10), 
            Rvalue=optimization_parameters.get('r_value', 5), 
            Rvalue2=optimization_parameters.get('r_value2', 0), 
            d=data_step, 
            L=SYM_CHORD_10, 
            ubound=ubound_plan, 
            lbound=lbound_plan, 
            NR_value = optimization_parameters.get('NR_value', -1),
            max_number_of_radius = optimization_parameters.get('max_number_of_radius', 5),
            min_quality = optimization_parameters.get('min_quality', 20),
            find_good_solution = optimization_parameters.get('find_good_solution', True),
            cons = optimization_parameters.get('transition_curve', [0]),
            max_seconds_for_iteration = optimization_parameters.get('max_seconds_for_iteration', 30),
            token = cancellation_token
        ) 
    
    straight_urov = -1 if optimization_parameters is None else optimization_parameters.get('straight_urov', -1)
    curve_urov = -1 if optimization_parameters is None else optimization_parameters.get('curve_urov', -1)
    straight_calc_type = [1] if optimization_parameters is None else optimization_parameters.get('straight_calc_type', [1])

    # print(f'track_calculation: msv_urov={msv_urov}, v_max={v_max}, ubound_plan={ubound_plan}, lbound_plan={lbound_plan}, curve_urov={curve_urov}, straight_calc_type={straight_calc_type}')
    EV_plan, alc_plan, alc_urov, new_track_split = track_calculation(
                                        msv_rix, 
                                        msv_urov, 
                                        v_max, 
                                        ax, 
                                        ubound=ubound_plan, 
                                        lbound=lbound_plan,
                                        count_urov=straight_urov,
                                        curve_urov=curve_urov, 
                                        calc_type=straight_calc_type,
                                        token = cancellation_token)
    EV_plan.index=range(EV_plan.shape[0])
    EV_plan.columns = plan_column_names()
    
    new_track_split.columns = ['geom', 'start', 'end', 'k0', 'k1']
    new_track_split = new_track_split.round(3)

    EV_profile, alc_profile = project_profile(
                                        msv_pro, 
                                        lbound=lbound_prof, 
                                        ubound=ubound_prof, 
                                        popravki_value=5, 
                                        min_length_from_start_end=2, 
                                        koeff=0.5,
                                        N_split=optimization_parameters.get('n_split', -1), 
                                        condition_start = 'equal', 
                                        condition_end = 'equal')    
    EV_profile.index=range(EV_profile.shape[0])
    EV_profile.columns = prof_column_names()

    # OBSOLETE:
    save_alc = False if optimization_parameters is None else optimization_parameters.get('save_alc', False)
    if save_alc:
        alc_plan.to_csv('../alc_plan.csv', sep=';', index = False)
        alc_urov.to_csv('../alc_urov.csv', sep=';', index = False)

    return {
        'plan': EV_plan,
        'prof': EV_profile,
        'alc_plan': alc_plan,
        'alc_prof': alc_profile,
        'alc_level': alc_urov,
        'restrictions': restrictions,
        'track_split': new_track_split
    }


def calctask_machine(
                    options: ProgramTaskCalculationOptionsDto,
                    data_step: float = 0.185,
                    cancellation_token: AbstractToken = SimpleToken(),
                    progress: Callable[[float], float] = print) -> Tuple[ProgramTaskBaseData, SteppedData, pd.DataFrame]:
    """
    Расчитывает программное задание и возвращает словарь массивов.
    Если параметры машины не заданы, то подставляются параметры ВПИ.
    @Params:
        :param:`measurements`: pd.DataFrame = {
            'strelograph_work': [],
            'sagging_left': [],
            'sagging_right': [],
            'pendulum_work': [],
        }
        :param:`constant_step`: bool -- Задает признак того что измерения сделаны с постоянным шагом или нет 
        :param:`restrictions`: dict[str, np.ndarray] = {
            'ubound_plan': [],
            'lbound_plan': [],
            'ubound_prof': [],
            'lbound_prof': [],
            'v_max': [],
        }
        :param:`machine_params`: dict[str, float] = {
            'measures_step': 0.185,    # шаг у ВПИ
            'back_horde_plan': 4.1,     # хорды ВПИ
            'front_horde_plan': 17.4,
            'back_horde_prof': 2.7,
            'front_horde_prof': 14.3,
            'base_rail': 0,             # 0 - левый, 1 - правый
        }        
        :param:`data_step` -- задает шаг в програмном задании в метрах (= 0.185 по умолчанию)
    @Returns:
        Возвращает DataFrame со следующими столбцами:
        task_data = {            
            'plan_fact': [],
            'plan_prj': [],
            'plan_delta': [],
            'vozv_fact': [],
            'vozv_prj': [],
            'prof_fact': [],
            'prof_prj': [],
            'prof_delta': [],
            'ubound_plan': [],
            'lbound_plan': [],
            'ubound_prof': [],
            'lbound_prof': [],
        }
    """

    # копируем т.к. возможно потребуется инверсия данных (т.е. модификация)   
    measurements = options.measuring_trip.measurements.data.copy()

    if options.measuringReverseType() != MeasuringTripReverseType.Nothing:
        measurements = reverse_measuring_trip(measurements, options.measuringReverseType())
        print(f'MEASURING TRIP REVERSE TYPE: {options.measuringReverseType()}')

    machine_params = options.measuring_trip.machine_parameters | { 'base_rail': options.measuring_trip.options.base_rail.value }
    
    # Задание ограничений    
    segment_restrictions = prep_detailed_restrictions(
        start_picket=options.start_picket, 
        picket_direction=options.picket_direction,
        data_size=len(measurements), 
        data_step=options.measuring_trip.measurements.step.meters, 
        restrictions_ui=options.restrictions.get('segments'))
    
    measurements['strelograph_work'] = horde_to_horde(
                                            measurements['strelograph_work'],                 
                                            machine_params['back_horde_plan'], 
                                            machine_params['front_horde_plan'], 
                                            options.measuring_trip.measurements.step.meters, 
                                            SYM_CHORD_10, 
                                            SYM_CHORD_10)
    # TODO: Проверить расчет профиля через функцию helpers.find_real_prof(msv_rix_l, msv_pro_l, msv_pro_r)
    measurements['sagging_left'] = horde_to_horde(
                                            measurements['sagging_left'],
                                            machine_params['back_horde_prof'], 
                                            machine_params['front_horde_prof'], 
                                            options.measuring_trip.measurements.step.meters, 
                                            SYM_CHORD_10, 
                                            SYM_CHORD_10)
    measurements['sagging_right'] = horde_to_horde(
                                            measurements['sagging_right'],
                                            machine_params['back_horde_prof'], 
                                            machine_params['front_horde_prof'], 
                                            options.measuring_trip.measurements.step.meters, 
                                            SYM_CHORD_10, 
                                            SYM_CHORD_10)  
    
    # Расчет программного задания в симметричной хорде 10х10
    task_data = calctask_base(
                    plan_fact=measurements['strelograph_work'], 
                    prof_fact=measurements['sagging_left'], 
                    level_fact=np.array(measurements['pendulum_work']), 
                    restrictions=segment_restrictions, 
                    data_step=options.measuring_trip.measurements.step.meters,
                    optimization_parameters=options.restrictions['optimization_parameters'],
                    cancellation_token = cancellation_token,
                    progress = progress)
    
    task_data['plan'].index.name = 'step'
    task_data['prof'].index.name = 'step'

    # Ведомость кривых
    # summary = TrackPlanProjectModel(track_split=task_data['track_split'], data=task_data['plan'], step=SYM_CHORD_10).summary()
    summary = build_plan_summary(base_plan=task_data['plan'], alc_plan=task_data['alc_plan'], alc_level=task_data['alc_level'])
    
    # Программное задание на симметричной хорде 10х10
    base_task = ProgramTaskBaseData(
                    measurements_processed= SteppedData(data=measurements, step=LocationVector1D(meters=data_step)),
                    detailed_restrictions= segment_restrictions,
                    plan= task_data['plan'], 
                    prof= task_data['prof'], 
                    alc_plan= task_data['alc_plan'],
                    alc_level= task_data['alc_level'],
                    track_split_plan= summary, #task_data['track_split'],
                    track_split_prof= None, 
                    step= LocationVector1D(meters=SYM_CHORD_10))
    
    # Программное задание для машины с шагом data_step (0.185)
    machine_task = machine_task_from_base_data(base_task=base_task, options=options, data_step=data_step)
    
    return base_task, machine_task, summary

def track_calculation_new(
                    options: ProgramTaskCalculationOptionsDto,
                    data_step: float = 0.185,
                    cancellation_token: AbstractToken = SimpleToken(),
                    progress: Callable[[float], float] = print) -> Tuple[ProgramTaskBaseData, SteppedData, pd.DataFrame]:
    """
    Строит программное задание, используя новый расчет плана.
    """
    print('track_calculation_new')
    machine_params = options.measuring_trip.machine_parameters
    measuring_step = options.measuring_trip.measurements.step.meters
    calc_plan_version = options.restrictions['optimization_parameters'].get('calc_plan_version', 'bounded')

    # Инвертируем измерительную поездку если нужно.   
    measurements = options.measuring_trip.measurements.data.copy()
    if options.measuringReverseType() != MeasuringTripReverseType.Nothing:
        measurements = reverse_measuring_trip(measurements, options.measuringReverseType())
        print(f'MEASURING TRIP REVERSE TYPE: {options.measuringReverseType()}')
    
    # Конвертируем данные измерительной поездки вначале на симметричную хорду 0.185 для расчета
    # плана и профиля, а затем на хорду 10 м для программного задания на машине.    
    measurements = add_sym_chords_to_measurements(
                        measurements= measurements, 
                        machine_params= machine_params, 
                        measuring_step= measuring_step,
                        version= (2 if calc_plan_version == 'fastsmartsplit' else 1)
                    )
    # Преобразуем огранияения в массивы.
    detailed_restrictions = prep_detailed_restrictions(
            start_picket=options.start_picket.meters, 
            picket_direction=options.picket_direction,
            data_size=len(measurements), 
            data_step=measuring_step, 
            restrictions_ui=options.restrictions.get('segments'))
    
    ### Расчитываем план ###
    # Опция calc_plan_version может принимать сл. значения:
    # bounded -- расчет плана как целого участка
    # split   -- расчет плана с разбиение на участки Версия 1
    # split2   -- расчет плана с разбиение на участки Версия 2
    # smartsplit -- расчет плана с разбиение на участки Версия 3
    # fastsmartsplit -- таже версия что и smartsplit, но с другими параметрами tol и updating в функции differential_evolution.
    match calc_plan_version:
            case 'split' | 'split2':
                track_split_plan, ev_plan = plan_calculation_with_split(
                                    measurements= measurements, 
                                    options= options, 
                                    v_max= detailed_restrictions['v_max'],
                                    lower_bound= detailed_restrictions['lbound_plan'],
                                    upper_bound= detailed_restrictions['ubound_plan'],
                                    calc_params= options.restrictions.get('optimization_parameters'),
                                    cancellation_token= cancellation_token)
            case 'bounded':
                track_split_plan, ev_plan = plan_calculation(
                                    measurements= measurements, 
                                    trip_options= options.measuring_trip, 
                                    v_max= detailed_restrictions['v_max'],
                                    lower_bound= detailed_restrictions['lbound_plan'],
                                    upper_bound= detailed_restrictions['ubound_plan'],
                                    calc_params= options.restrictions.get('optimization_parameters'),
                                    cancellation_token= cancellation_token)
            case 'smartsplit':
                track_split_plan, ev_plan = plan_calculation_with_smartsplit(
                                    measurements= measurements, 
                                    options= options, 
                                    v_max= detailed_restrictions['v_max'],
                                    lower_bound= detailed_restrictions['lbound_plan'],
                                    upper_bound= detailed_restrictions['ubound_plan'],
                                    calc_params= options.restrictions.get('optimization_parameters'),
                                    cancellation_token= cancellation_token)
            case 'fastsmartsplit':
                track_split_plan, ev_plan = plan_calculation_with_fastsmartsplit(
                                    measurements= measurements, 
                                    options= options, 
                                    v_max= detailed_restrictions['v_max'],
                                    lower_bound= detailed_restrictions['lbound_plan'],
                                    upper_bound= detailed_restrictions['ubound_plan'],
                                    calc_params= options.restrictions.get('optimization_parameters'),
                                    cancellation_token= cancellation_token)
            case _:
                raise Exception('Неизвестный тип расчета')
    
    ### Расчитываем профиль ###
    track_split_prof, ev_prof = profile_calculation(
                                    measurements= measurements, 
                                    trip_options= options.measuring_trip, 
                                    v_max= detailed_restrictions['v_max'],
                                    lower_bound= detailed_restrictions['lbound_prof'],
                                    upper_bound= detailed_restrictions['ubound_prof'],
                                    calc_params= options.restrictions.get('optimization_parameters'),
                                    cancellation_token= cancellation_token)
    
    # Базовое программное задание на симметричной хорде
    base_task = ProgramTaskBaseData(
                    measurements_processed= SteppedData(data=measurements, step=LocationVector1D(meters=data_step)),
                    detailed_restrictions= detailed_restrictions,
                    plan= ev_plan, 
                    prof= ev_prof, 
                    alc_plan= None,
                    alc_level= None,
                    track_split_plan= track_split_plan,
                    track_split_prof= track_split_prof, 
                    step= LocationVector1D(meters=data_step))
    
    machine_task = machine_task_from_base_data_new(base_task)
    
    return base_task, machine_task, track_split_plan

# ==============================================================================================================================================
def plan_calculation(
        measurements: pd.DataFrame, 
        trip_options: MeasuringTripResultDto, 
        v_max: np.ndarray,
        lower_bound: np.ndarray,
        upper_bound: np.ndarray,
        calc_params: dict,
        cancellation_token: AbstractToken) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    """

    pkt = 0.185 * np.arange(len(measurements))
    add_evl = np.zeros(len(measurements))
    # add_evl = 10*np.ones(len(measurements))
    # add_evl[-1] = 0
    # add_evl[0] = 0

    calcer = PlanCalculation(pkt=pkt, 
                             recalculated_rix=np.array(measurements['strelograph_work_chord_0185']), 
                             initial_ur=np.array(measurements['pendulum_work']), 
                             v_max=v_max, 
                             lower_bound=lower_bound, 
                             upper_bound=upper_bound, 
                             token=cancellation_token, 
                             add_evl=add_evl)
    min_element_length = calc_params.get('min_element_length_plan', 20)
    # если длина участка меньше 100 м, то min_element_length делаем < 20 (например 10 м) иначе расчет будет оооочень долгим
    if trip_options.length <= 120 and min_element_length >= 20:
        min_element_length = 10
        print(f'-> min_element_length for PLAN chaged to {min_element_length}')
    calcer.min_element_length = min_element_length

    plan_prj, sdv = calcer.find_project()
    if plan_prj is None:
        raise Exception("Не удалось найти решение")
    
    # ev_table - имеет шаг 0.185, а данные пересчитаны на хорду 10х10
    # f_urov - размерность по кол-ву радиусов (кол-во нулей в degree_list )
    f_urov = None
    straight_urov = calc_params.get('straight_urov', None)
    if straight_urov is not None:        
        f_urov = [straight_urov for d in calcer.degree_list if d == 0]
    # print(f'f_urov = {f_urov}')
    track_split, ev_table = calcer.calculate_track_parameters(calcer.breaks, calcer.y_vals, plan_prj, sdv, f_urov=f_urov)
    ev_table.index.name = 'step'

    # Пересчитываем уровень в прямых если задан
    # level = calc_params.get('straight_urov', None)
    # if level is not None:
    #     level_model = TrackLevelProjectModel(track_split=track_split, data=ev_table)     
    #     level_model.set_straight_level(level)
    #     new_level_model = level_model.calc_new_track()
    #     track_split, ev_table = new_level_model.track_split, new_level_model.data
    #     # print(f'f_urov = {f_urov}')
    
    return track_split, ev_table

def plan_calculation_with_split(
        measurements: pd.DataFrame, 
        options: ProgramTaskCalculationOptionsDto, 
        v_max: np.ndarray,
        lower_bound: np.ndarray,
        upper_bound: np.ndarray,
        calc_params: dict,
        cancellation_token: AbstractToken) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    """
    pkt = 0.185 * np.arange(len(measurements))
    add_evl = np.zeros(len(measurements))
    # add_evl = 10*np.ones(len(measurements))
    # add_evl[5027:6162] = 8
    # print('add_evl ready')
    # add_evl[-1] = 0
    # add_evl[0] = 0
    PlanClass = plan_calculation_2.PlanCalculation
    if options.restrictions['optimization_parameters'].get('calc_plan_version', 'bounded') == 'split2':
        PlanClass = plan_calculation_2.PlanCalculationV2
    print(f'> Plan calculation with split ({PlanClass.__name__})...')
    calcer = PlanClass(
                pkt= pkt, 
                initial_rix= np.array(measurements['strelograph_work_chord_10']),
                recalculated_rix= np.array(measurements['strelograph_work_chord_0185']), 
                initial_ur= np.array(measurements['pendulum_work']), 
                min_value=options.restrictions['optimization_parameters'].get('plan_min_value', 5), 
                v_max= v_max, 
                add_evl= add_evl,
                lower_bound= lower_bound, 
                upper_bound= upper_bound, 
                token= cancellation_token
            )
    # минимальная длина элемента в плане
    min_element_length = calc_params.get('min_element_length_plan', 10)
    # если длина участка меньше 100 м, то min_element_length делаем < 20 (например 10 м) иначе расчет будет оооочень долгим
    # if options.measuring_trip.length <= 120 and min_element_length >= 20:
    #     min_element_length = 10
    #     print(f'-> min_element_length for PLAN chaged to {min_element_length}')
    calcer.min_element_length = min_element_length

    # минимальный радиус в прямых
    min_straight_radius = calc_params.get('min_straight_radius')
    if min_straight_radius is not None:
        print(f'-> min_straight_radius for PLAN chaged to {min_straight_radius}')
        calcer.min_straight_radius = min_straight_radius

    # y_vals - это величина стрелы в каждой точке breaks
    degree_list, breaks, y_vals, plan_prj, sdv = calcer.calc_with_split()
    if plan_prj is None:
        raise Exception("Не удалось найти решение")
    
    # ev_table - имеет шаг 0.185, а данные пересчитаны на хорду 10х10
    # f_urov - размерность по кол-ву радиусов (кол-во нулей в degree_list )
    f_urov = None
    straight_urov = calc_params.get('straight_urov', None)
    if straight_urov is not None:        
        f_urov = [straight_urov for d in degree_list if d == 0]
    # print(f'f_urov = {f_urov}')
    
    track_split, ev_table = calcer.calculate_track_parameters(breaks, y_vals, plan_prj, sdv, f_urov=f_urov)
    ev_table.index.name = 'step'

    return track_split, ev_table

def plan_calculation_with_smartsplit(
        measurements: pd.DataFrame, 
        options: ProgramTaskCalculationOptionsDto, 
        v_max: np.ndarray,
        lower_bound: np.ndarray,
        upper_bound: np.ndarray,
        calc_params: dict,
        cancellation_token: AbstractToken) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    """
    pkt = 0.185 * np.arange(len(measurements))
    add_evl = np.zeros(len(measurements))
    # add_evl = 10*np.ones(len(measurements))
    # add_evl[5027:6162] = 8
    # print('add_evl ready')
    # add_evl[-1] = 0
    # add_evl[0] = 0
    print('> Plan calculation with SmartSplitPlanCalculation...')
    calcer = SmartSplitPlanCalculation(
                pkt= pkt, 
                recalculated_rix= np.array(measurements['strelograph_work_chord_0185']), 
                initial_ur= np.array(measurements['pendulum_work']), 
                v_max= v_max, 
                add_evl= add_evl,
                lower_bound= lower_bound, 
                upper_bound= upper_bound, 
                token= cancellation_token,
                f= [None, None, None]
            )
    degree_list, breaks, y_vals, plan_prj, sdv = calcer.track_split_calculation()

    f_urov = None
    straight_urov = calc_params.get('straight_urov', None)
    if straight_urov is not None:        
        f_urov = [straight_urov for d in degree_list if d == 0]
    # print(f'f_urov = {f_urov}')

    track_split, ev_table = calcer.calculate_track_parameters(breaks, y_vals, plan_prj, sdv, f_urov=f_urov)
    ev_table.index.name = 'step'

    return track_split, ev_table

def plan_calculation_with_fastsmartsplit(
        measurements: pd.DataFrame, 
        options: ProgramTaskCalculationOptionsDto, 
        v_max: np.ndarray,
        lower_bound: np.ndarray,
        upper_bound: np.ndarray,
        calc_params: dict,
        cancellation_token: AbstractToken) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
        Используется тоже класс SmartSplitPlanCalculation, но с другими параметрами tol и updating в
        функции differential_evolution.
    """
    pkt = 0.185 * np.arange(len(measurements))
    add_evl = np.zeros(len(measurements))
    print('> Plan calculation with FastSmartSplitPlanCalculation...')
    calcer = SmartSplitPlanCalculation(
                pkt= pkt, 
                recalculated_rix= np.array(measurements['strelograph_work_chord_0185']), 
                initial_ur= np.array(measurements['pendulum_work']), 
                v_max= v_max, 
                add_evl= add_evl,
                lower_bound= lower_bound, 
                upper_bound= upper_bound, 
                token= cancellation_token,
                f= [None, None, None],
                differential_evolution_tol=1e3,
                differential_evolution_updating='deferred'
            )
    degree_list, breaks, y_vals, plan_prj, sdv = calcer.track_split_calculation()
    f_urov = None
    straight_urov = calc_params.get('straight_urov', None)
    if straight_urov is not None:        
        f_urov = [straight_urov for d in degree_list if d == 0]
    # print(f'f_urov = {f_urov}')
    track_split, ev_table = calcer.calculate_track_parameters(breaks, y_vals, plan_prj, sdv, f_urov=f_urov)
    ev_table.index.name = 'step'
    return track_split, ev_table

def profile_calculation(
        measurements: pd.DataFrame, 
        trip_options: MeasuringTripResultDto, 
        v_max: np.ndarray,
        lower_bound: np.ndarray,
        upper_bound: np.ndarray,
        calc_params: dict,
        cancellation_token: AbstractToken) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    """
    print('Profile calculation...')
    pkt = 0.185 * np.arange(len(measurements))

    calcer = ProfileCalculation(
                            pkt= pkt, 
                            recalculated_rix= np.array(measurements['sagging_left_chord_0185']), 
                            initial_ur= np.array(measurements['pendulum_work']), 
                            v_max= v_max, 
                            lower_bound= lower_bound, 
                            upper_bound= upper_bound, 
                            token= cancellation_token)
    
    min_element_length = calc_params.get('min_element_length_prof', 5)
    calcer.min_element_length = min_element_length

    breaks, y_vals, prof_prj, sdv = calcer.calc_with_split()
    track_split, ev_table = calcer.calculate_track_parameters(breaks, y_vals, prof_prj, sdv)
    ev_table.index.name = 'step'

    return track_split, ev_table

# ==============================================================================================================================================
def program_task_caculation(
                    options: ProgramTaskCalculationOptionsDto,
                    data_step: float = 0.185,
                    cancellation_token: AbstractToken = SimpleToken(),
                    progress: Callable[[float], float] = print) -> Tuple[ProgramTaskBaseData, SteppedData, pd.DataFrame]:
    """
    Строит программное задание, используя версию расчета заданную в опциях.
    """
    last_version = options.restrictions['optimization_parameters'].get('last_version', True)
    if last_version:
        return track_calculation_new(options=options, data_step=data_step, cancellation_token=cancellation_token, progress=progress)
    
    return calctask_machine(options=options, data_step=data_step, cancellation_token=cancellation_token, progress=progress)

# ==============================================================================================================================================

def machine_task_from_base_data_new(base_task: ProgramTaskBaseData) -> SteppedData:
    """
        Формирует окончательное программное задание для машины из расчитанного базового программного задания.
        Базовое программное задание представлено структурой ProgramTaskBaseData, в которой хранятся измерительная 
        поездка (пересчитанная из хорды машины на хорду 10 на 10, а также возможно инвертированная), план и профиль.
    """
    result = {
        'plan_fact':        np.array(base_task.plan.plan_fact), 
        'plan_prj':         np.array(base_task.plan.plan_prj),
        'plan_delta':       np.array(base_task.plan.plan_delta), 
        'vozv_fact':        np.array(base_task.plan.vozv_fact), 
        'vozv_prj':         np.array(base_task.plan.vozv_prj),
        'vozv_delta':       np.array(base_task.plan.vozv_prj - base_task.plan.vozv_fact),
        'prof_fact':        np.array(base_task.prof.prof_fact),        
        'prof_fact_left':   np.array(base_task.prof.prof_fact), 
        'prof_fact_right':  np.array(base_task.measurements_processed.data.sagging_right), 
        'prof_prj':         np.array(base_task.prof.prof_prj),
        'prof_delta':       np.array(base_task.prof.prof_delta),
        'prof_delta_left':  None,
        'prof_delta_right': None,
        'rail_length':      np.array(base_task.plan.rail_length),
        'fastening_tmp':    np.array(base_task.plan.fastening_tmp),
        'ballast_need':     np.array(base_task.plan.ballast_need),
        'a_nepog_fact':     np.array(base_task.plan.a_nepog_fact),
        'psi_fact':         np.array(base_task.plan.psi_fact),
        'v_wheel_fact':     np.array(base_task.plan.v_wheel_fact),
        'a_nepog_prj':      np.array(base_task.plan.a_nepog_prj),
        'psi_prj':          np.array(base_task.plan.psi_prj),
        'v_wheel_prj':      np.array(base_task.plan.v_wheel_prj),
        'ubound_plan':      np.array(base_task.plan.ubound),
        'lbound_plan':      np.array(base_task.plan.lbound),
        'ubound_prof':      np.array(base_task.prof.ubound),
        'lbound_prof':      np.array(base_task.prof.lbound),
    }    
    result['prof_delta_left'], result['prof_delta_right'] = calc_podjemki(
                                                                urov_naturn = result['vozv_fact'], 
                                                                urov_project = result['vozv_prj'], 
                                                                podjemki = result['prof_delta'] )
    task = pd.DataFrame(result).round(3)
    task.index.name = 'step'
    return SteppedData(data = task, step = base_task.step)