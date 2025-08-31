import numpy as np
import pandas as pd
import scipy as sc
from typing import Callable
from dataclasses import dataclass
from domain.dto.Travelling import PicketDirection, MovingDirection, MeasuringTripReverseType
# from ..dto.Travelling import PicketDirection, MovingDirection, MeasuringTripReverseType
from .track_funcs import horde_to_horde
from .consts import (    
    CST_PLAN_UP, CST_PLAN_DOWN, CST_PROFILE_DOWN, CST_PROFILE_UP, V_MAX_TRAIN, SYM_CHORD_0185, SYM_CHORD_10
)


def plan_column_names() -> list[str]:
    return ["plan_fact", "First_plan", "Fact_Plan", "Sum_Fact_Plan", "EV", "Coord", "tangens", "Popravka", "8", "Popravka_razn", "plan_prj", "Fact_Plan_corr",
            "Sum_Fact_Plan_corr", "plan_delta", "ubound", "lbound", "vozv_fact", "V_max", "R", "a_nepog", "Max_v_dop", "Min_vozv", "l_perex", "mean_vozv", "Uklon_otvoda",
            "narast_a_nepog", "rail_length", "fastening_tmp", "ballast_need", "vozv_prj", "a_nepog_fact", "psi_fact", "v_wheel_fact", "a_nepog_prj", "psi_prj", 
            "v_wheel_prj", "36", "37", "38", "39", "40", "41"]

def prof_column_names() -> list[str]:
    return ["prof_fact","First_prof","Fact_Prof","Sum_Fact_Prof","EV","Coord","tangens","Popravka","8","Popravka_razn","prof_prj","Fact_Prof_corr",
            "Sum_Fact_Prof_corr","prof_delta","ubound","lbound","vozv_fact","V_max","R","a_nepog","Max_v_dop","Min_vozv","l_perex","mean_vozv","Uklon_otvoda",
            "narast_a_nepog","rail_length", "fastening_tmp", "ballast_need", "vozv_prj", "a_nepog_fact", "psi_fact", "v_wheel_fact", "a_nepog_prj", "psi_prj", 
            "v_wheel_prj", "36", "37", "38", "39", "40", "41"]

def project_to_machine_chord(project_arrow: float, chord_symmetric: float, front_chord: float, back_chord: float) ->float:
    """
    Пересчет проектных стрел (плана или профиля) из симметричной хорды в хорды машины.
    """
    return project_arrow * front_chord * back_chord / chord_symmetric**2

def program_task_to_machine_chords(task: pd.DataFrame, machine_params: dict) -> pd.DataFrame:
    task.plan_prj = project_to_machine_chord(task.plan_prj, chord_symmetric=10, front_chord=machine_params['front_horde_plan'], back_chord=machine_params['back_horde_plan'])
    task.prof_prj = project_to_machine_chord(task.prof_prj, chord_symmetric=10, front_chord=machine_params['front_horde_prof'], back_chord=machine_params['back_horde_prof'])
    return task

def rix_calc(x_points, y_points, step):
    x_points = np.array(x_points)
    y_points = np.array(y_points) 
    tck = sc.interpolate.interp1d(x_points, y_points)
    res_x = list()
    res_y = list()
    point_x = x_points[0]
    while point_x < x_points[-1]:
        res_x.append(point_x)
        res_y.append(tck(point_x))      
        point_x += step
    return pd.DataFrame([res_x, res_y]).T

#
def norm_measuring_trip(trip, step: float):
    norm_trip = pd.DataFrame()
    new_col = rix_calc(trip.position, trip.strelograph_work, step)
    norm_trip['position'] = new_col[0]
    norm_trip['strelograph_work'] = new_col[1]

    new_col = rix_calc(trip.position, trip.pendulum_work, step)
    norm_trip['pendulum_work'] = new_col[1]

    new_col = rix_calc(trip.position, trip.pendulum_control, step)
    norm_trip['pendulum_control'] = new_col[1]

    new_col = rix_calc(trip.position, trip.pendulum_front, step)
    norm_trip['pendulum_front'] = new_col[1]
    
    new_col = rix_calc(trip.position, trip.sagging_left, step)
    norm_trip['sagging_left'] = new_col[1]
    
    new_col = rix_calc(trip.position, trip.sagging_right, step)
    norm_trip['sagging_right'] = new_col[1]
    return norm_trip


def sdv_to_ver(data, L, d):
    # Интерполяция сдвижек и подъемок.
    # L - расстояние между точками в исходных данных data (10 метров)
    # d - требуемое расстояние между точками (сколько должно быть в файле VER)

    def f(x,x_points,y_points):
        # Расчет сдвижек и преобразование в VER-формат
        tck = sc.interpolate.splrep(x_points, y_points)
        return sc.interpolate.splev(x, tck)

    res = list()
    xpt = L*np.arange(data.shape[0]).astype(float)
    SL = int((data.shape[0]-1)*L/d)
    xpt[-1] = SL*d        
    
    for i in range(SL+1):
        res.append(f(i*d,xpt,data))   
        
    return np.array(res)


def default_restrictions(size: int) -> dict:
    """
    Возвращает словарь ограничений по умолчанию.
    """
    restrictions = dict()       
    # default params        
    restrictions['ubound_plan'] = (CST_PLAN_UP*np.ones((size,))).tolist()
    restrictions['lbound_plan'] = (CST_PLAN_DOWN*np.ones((size,))).tolist()
    restrictions['ubound_prof'] = (CST_PROFILE_UP*np.ones((size,))).tolist()
    restrictions['lbound_prof'] = (CST_PROFILE_DOWN*np.ones((size,))).tolist()
    restrictions['v_max'] = (V_MAX_TRAIN*np.ones((size,))).tolist()

    return restrictions

# def default_restrictions(size: int) -> dict:
#     """
#     Возвращает словарь ограничений по умолчанию.
#     """
#     restrictions = dict()       
#     # default params        
#     restrictions['ubound_plan'] = (50*np.ones((size,))).tolist()
#     restrictions['lbound_plan'] = (-50*np.ones((size,))).tolist()
#     restrictions['ubound_prof'] = (40*np.ones((size,))).tolist()
#     restrictions['lbound_prof'] = (40*np.ones((size,))).tolist()
#     restrictions['v_max'] = (V_MAX_TRAIN*np.ones((size,))).tolist()
#     return restrictions

def default_machine_params():
    # по умолчанию - параметры вагона-путеизмерителя
    return {
            'measures_step': 0.185,
            'back_horde_plan': 4.1,
            'front_horde_plan': 17.4,
            'back_horde_prof': 2.7,
            'front_horde_prof': 14.3,
            'base_rail': 0 
            }


def range_indexes(picket_start, data_step, data_size, range_start, range_end):
    """
    Возвращает индекс начала и индекс конца участка (range_start, range_end).
    Если начало участка не задано, то индекс начала = 0, а если не задан конец участка, 
    то индекс конца = data_size-1.
    """
    if range_start is None:
        range_start = picket_start
    if range_end is None:
        range_end = picket_start + (data_size-1)*data_step
        
    idx_start = int((range_start - picket_start)/data_step)
    
    if idx_start < 0:
        idx_start = 0
    if idx_start > data_size:
        idx_start = -1
        
    idx_end = round((range_end - picket_start)/data_step)
    if idx_end < 0:
        idx_end = -1
    else:
        # если не точное попадание (не делится на цело), то захватываемя чуть большую область +1
        if (range_end - picket_start) % data_step != 0:
            idx_end += 1 
        if idx_end > data_size-1:
            idx_end = data_size-1
        
    return int(idx_start), int(idx_end)

def prep_progtask_restrictions(picket_start: float, data_size: int, data_step: float, restrictions_ui: list) -> dict:
    """
        OBSOLETE.
    """
    restrictions = dict()   
    v_pass = np.ones(data_size)
    v_gruz = np.ones(data_size)
    shifting_left = np.ones(data_size)
    shifting_right = np.ones(data_size)
    raising_ubound = np.ones(data_size)
    raising_lbound = np.ones(data_size)
    
    for r in restrictions_ui:
        idx_start, idx_end = range_indexes(picket_start, data_step, data_size, r.get('range_start'), r.get('range_end'))
        if idx_start == -1 or idx_end == -1:
            continue

        if 'v_pass' in r:
            v_pass[idx_start:idx_end+1] = r['v_pass']
        if 'v_gruz' in r:
            v_gruz[idx_start:idx_end+1] = r['v_gruz']
        if 'shifting_left' in r:
            shifting_left[idx_start:idx_end+1] = r['shifting_left']
        if 'shifting_right' in r:
            shifting_right[idx_start:idx_end+1] = r['shifting_right'] 
        if 'raising_ubound' in r:
            raising_ubound[idx_start:idx_end+1] = r['raising_ubound']
        if 'raising_lbound' in r:
            raising_lbound[idx_start:idx_end+1] = r['raising_lbound']
    
    restrictions['lbound_plan'] = shifting_right
    restrictions['ubound_plan'] = shifting_left
    
    restrictions['ubound_prof'] = raising_ubound
    restrictions['lbound_prof'] = raising_lbound
    
    restrictions['v_max'] = v_pass
    restrictions['v_gruz'] = v_pass
    
    return restrictions

def progtask_otvod(i_otv: float, deltas: np.array, data_step: float=0.625):
    otvod = np.array(deltas)    
    x = np.array(range(len(deltas)))*data_step
    y = i_otv*x
    y_reversed = y[::-1]

    diff_left = pd.Series(abs(deltas - y))
    diff_right = pd.Series(abs(deltas - y_reversed))
    idx_left = diff_left[diff_left<i_otv].index[0]
    idx_right = diff_right[diff_right<i_otv].index[-1]
    
    otvod[:idx_left] = y[:idx_left]
    otvod[idx_right:] = y_reversed[idx_right:]
    return otvod, idx_left, idx_right


def reverse_task_order(task: pd.DataFrame) -> pd.DataFrame:
    """
    Поворачивает программное задание, знаки не меняет.
    Если колонка position присутствует в датафрейме, то ее порядок не меняется, всегда идет от 0 и по возрастанию.
    """
    reversed_task = task.iloc[::-1]    
    # инвертируем обратно индекс и position (если присутствует)
    if 'position' in reversed_task.columns:
        reversed_task['position'] = reversed_task.position.values[::-1] 
    reversed_task.index = reversed_task.index[::-1]
    return reversed_task

def reverse_task_signs(task: pd.DataFrame) -> pd.DataFrame:
    # Меняем знаки у некоторых столбцов
    task.plan_fact = -1*task.plan_fact
    task.plan_prj = -1*task.plan_prj
    task.plan_delta = -1*task.plan_delta
    task.vozv_fact = -1*task.vozv_fact
    task.vozv_prj = -1*task.vozv_prj
    return task
    
def reverse_task(task: pd.DataFrame) -> pd.DataFrame:
    return reverse_task_signs(reverse_task_order(task))

def reverse_measuring_trip(trip_data: pd.DataFrame, reverse: MeasuringTripReverseType) -> pd.DataFrame:
    """
    Модифицирует измерительную поездку в соответствии с заданным типом инверсии `reverse`.
    """
    if reverse == MeasuringTripReverseType.Nothing:
        return trip_data     
    # инвертируем порядок
    if reverse == MeasuringTripReverseType.ReverseOrder or reverse == MeasuringTripReverseType.ReverseFull:
        trip_data = trip_data.iloc[::-1]
        trip_data.index = trip_data.index[::-1]
    # инвертируем знаки 
    if reverse == MeasuringTripReverseType.ReverseSigns or reverse == MeasuringTripReverseType.ReverseFull:
        trip_data.strelograph_work = -1*trip_data.strelograph_work
        trip_data.pendulum_work = -1*trip_data.pendulum_work
        trip_data.pendulum_control = -1*trip_data.pendulum_control
        trip_data.pendulum_front = -1*trip_data.pendulum_front
    return trip_data

# def reverse_program_task(task: pd.DataFrame, inverse_position: bool = False) -> pd.DataFrame:
#     # инвертируем задание
#     reversed_task = task.iloc[::-1]    
    
#     # Приняли, что у колонки position значения всегда идут от 0 и по возрастанию
#     # если не указано обратное параметром inverse_position    
#     if not inverse_position:
#         # инвертируем обратно, т.к. вначале инвертируется весь датафрейм
#         reversed_task['position'] = reversed_task.position.values[::-1]
        
#     # Меняем знаки у некоторых параметров
#     reversed_task.plan_fact = -1*reversed_task.plan_fact
#     reversed_task.plan_prj = -1*reversed_task.plan_prj
#     reversed_task.plan_delta = -1*reversed_task.plan_delta
#     reversed_task.vozv_fact = -1*reversed_task.vozv_fact
#     reversed_task.vozv_prj = -1*reversed_task.vozv_prj    
#     return reversed_task


def nop(task: pd.DataFrame) -> pd.DataFrame:
    return task
 
def get_reverse_function_to_apply(lining_picket_direction: PicketDirection, measuring_picket_direction: PicketDirection, measuring_moving_direction: MovingDirection) -> Callable:
    """
    TODO: OBSOLETE.
    Возвращает функцию, которая реализует один из 4-х вариантов инверсии программного задания:
    1. nop - задание не нуждается ни в одном из типов инверсии
    2. reverse_task_signs - инвертируются только знаки определенных столбцов задания
    3. reverse_task_order - инвертируется только порядок строк задания (первая строка становится последней)
    4. reverse_task - инвертируются и знаки и порядок строк задания
    
    Функция выбирается на основании 3-х параметров:
    - Направление пикетажа во время выправки
    - Направление пикетажа во время измерительной поездки
    - Измерительная поездка задом или передом
    """
    task_invsersion_matrix = {
        (PicketDirection.Forward, PicketDirection.Forward, MovingDirection.Forward):   nop, 
        (PicketDirection.Forward, PicketDirection.Forward, MovingDirection.Backward):  reverse_task_signs, 
        (PicketDirection.Forward, PicketDirection.Backward, MovingDirection.Forward):  reverse_task, 
        (PicketDirection.Forward, PicketDirection.Backward, MovingDirection.Backward): reverse_task_order,    
        (PicketDirection.Backward, PicketDirection.Forward, MovingDirection.Forward):  reverse_task, 
        (PicketDirection.Backward, PicketDirection.Forward, MovingDirection.Backward): reverse_task_order, 
        (PicketDirection.Backward, PicketDirection.Backward, MovingDirection.Forward): nop, 
        (PicketDirection.Backward, PicketDirection.Backward, MovingDirection.Backward): reverse_task_signs 
    }
    return task_invsersion_matrix.get((lining_picket_direction, measuring_picket_direction, measuring_moving_direction))


def normalize_data_step(step: float, data: pd.DataFrame, columns: list[str]):
    """
    Данные всегда должны содержать столбец position и еще хотя бы один стобец с данным.
    """
    norm_data = pd.DataFrame()
    for colname in columns:
        norm_col = rix_calc(data.position, data[colname], step)
        norm_data['position'] = norm_col[0]
        norm_data[colname] = norm_col[1]

    return norm_data

def find_max_delta_in_progtask_at(start_step: int, task: pd.DataFrame) -> float:
    """
    Возвращает максимальное значение подъемки, сдвижки или возвышения в точке start_step.
    """    
    vozv_delta = task.vozv_prj - task.vozv_fact    
    return max(
        abs(task.plan_delta[start_step]), 
        abs(vozv_delta[start_step]), 
        abs(task.prof_delta[start_step]) )


@dataclass(frozen = True)
class UrgentBranchParameters:
    """
    Using example:
        value = UrgentBranchParameters.from_slope(1, find_max_delta_in_progtask_at(task))
        value = UrgentBranchParameters.from_slope(2, value.delta)
        value = UrgentBranchParameters.from_length(150, value.delta)
        value = UrgentBranchParameters.from_velocity(80, value.delta)
    """
    slope: float
    velocity: float
    length: float
    delta: float

    @staticmethod
    def velocity_by_slope(s: float) -> int:
        if s <= 1:
            return 120
        if 1 < s <= 2:
            return 100
        if 2 < s <= 3:
            return 80
        if 3 < s <= 4:
            return 60
        return 40

    @staticmethod
    def slope_by_velocity(v: int) -> float:
        #Допускаемый уклон отвода
        if v > 120:
            i_otv = 1
        elif (v > 100) & (v <= 120):
            i_otv = 2        
        elif (v > 80) & (v <= 100):
            i_otv = 3
        elif (v > 60) & (v <= 80):
            i_otv = 4  
        else:
            i_otv = 5 
        return i_otv

    @staticmethod
    def from_slope(slope: float, delta: float):
        return UrgentBranchParameters(
            delta=delta, 
            slope=slope, 
            velocity=UrgentBranchParameters.velocity_by_slope(slope), 
            length=abs(delta/slope))
    
    @staticmethod
    def from_velocity(velocity: float, delta: float):
        return UrgentBranchParameters(
            delta=delta, 
            slope=UrgentBranchParameters.slope_by_velocity(velocity), 
            velocity=velocity, 
            length=abs(delta/UrgentBranchParameters.slope_by_velocity(velocity)))
    
    @staticmethod
    def from_length(length: float, delta: float):
        return UrgentBranchParameters(
            delta=delta, 
            slope=abs(delta/length), 
            velocity=UrgentBranchParameters.velocity_by_slope(abs(delta/length)), 
            length=length)


# Нахождение просадки по просадкам левой и правой
# Вызов: msv_prof = find_real_prof(msv_rix_l, msv_pro_l, msv_pro_r)
def find_real_prof(rixt, profl, profr):
    msv_prof = list()
    for i in range(rixt.shape[0]):
        if rixt[i] >= 0:
            msv_prof.append(profr[i])
        else:
            msv_prof.append(profl[i])  
    msv_prof = np.array(msv_prof)
    return msv_prof


# Вызов: podjemka_l, podjemka_r = calc_podjemki(urov_naturn, urov_project, podjemki)
def calc_podjemki(urov_naturn, urov_project, podjemki):
    """
    Если поправка ВНР > 0, то прибавляем к подъемке левой головки рельса, 
    правая остается подъемкой «чистого» профиля, если < 0, то прибавляем к правой, 
    левая будет подъемкой «чистого» профиля.
    """
    podjemka_l = np.zeros(len(podjemki))
    podjemka_r = np.zeros(len(podjemki))
    urov_popravka = urov_naturn - urov_project
    for i in range(urov_popravka.shape[0]):
        if urov_popravka[i] >= 0:
            podjemka_l[i] = podjemki[i] + urov_popravka[i]
        else:
            podjemka_r[i] = podjemki[i] + urov_popravka[i]  
    return podjemka_l, podjemka_r


def normative_slope_by_velocity(v_pass: int) -> float:
    """
    Допускаемые уклоны отвода возвышения наружного рельса в кривых.
    """
    if 220 < v_pass <= 250:
        return 0.7
    if 200 < v_pass <= 220:
        return 0.8
    if 180 < v_pass <= 200:
        return 0.9
    if 160 < v_pass <= 180:
        return 1.0
    if 140 < v_pass <= 160:
        return 1.1
    if 120 < v_pass <= 140:
        return 1.2
    if 110 < v_pass <= 120:
        return 1.4
    if 100 < v_pass <= 110:
        return 1.5
    if 95 < v_pass <= 100:
        return 1.6
    if 90 < v_pass <= 95:
        return 1.7
    if 85 < v_pass <= 90:
        return 1.8
    if 80 < v_pass <= 85:
        return 1.9
    if 75 < v_pass <= 80:
        return 2.1
    if 70 < v_pass <= 75:
        return 2.3
    if 65 < v_pass <= 70:
        return 2.5
    if 60 < v_pass <= 65:
        return 2.7
    if 55 < v_pass <= 60:
        return 2.8
    if 50 < v_pass <= 55:
        return 2.9
    if 40 < v_pass <= 50:
        return 3
    if 25 < v_pass <= 40:
        return 3.1
    # if v_pass == 25:
    #     return 3.2
    # raise Exception('Invalid passenger speed value')
    return 3.2

def prep_detailed_restrictions(start_picket: float, picket_direction: PicketDirection, data_size: int, data_step: float, restrictions_ui: list) -> dict[str, np.ndarray]:
    """
    Преобразует описатели ограничений в словарь массивов ограничений с шагом data_step.
    """
    
    def prep_detailed_restriction(detailed: dict, common: np.ndarray):
        for x1x2, y1y2 in zip(detailed['x'], detailed['y']):
            start, end = x1x2[0], x1x2[1]
            start_idx = int(np.ceil( (start - start_picket) * picket_direction.multiplier() / data_step ))
            if start_idx < 0:
                start_idx = 0
            end_idx = int(np.floor( (end - start_picket) * picket_direction.multiplier() / data_step ))    
            # TODO: переделать на присвоение массива (полученного из формулы прямой линии)
            # сейчас значения ограничений на участке x1x2 одинаковые (т.е. горизогтальная прямая)
            common[start_idx:end_idx+1] = y1y2[0]
        
    restrictions = dict() 
    
    # Формируем общие ограничения: всегда первый эдемент списка restrictions_ui
    common_restrictions = restrictions_ui[0]
    v_pass_array = np.full(data_size, common_restrictions['v_pass'])
    v_gruz_array = np.full(data_size, common_restrictions['v_gruz'])
    shifting_left_array = np.full(data_size, common_restrictions['shifting_left'])
    shifting_right_array = np.full(data_size, common_restrictions['shifting_right'])
    raising_ubound_array = np.full(data_size, common_restrictions['raising_ubound'])
    raising_lbound_array = np.full(data_size, common_restrictions['raising_lbound'])

    # Формируем детальные огрнаничения если есть: всегда второй эдемент списка restrictions_ui
    detailed_restrictions = dict() if len(restrictions_ui) <= 1 else restrictions_ui[1]
    if 'v_pass' in detailed_restrictions:
        prep_detailed_restriction(detailed_restrictions['v_pass'], v_pass_array)
    if 'v_gruz' in detailed_restrictions:
        prep_detailed_restriction(detailed_restrictions['v_gruz'], v_gruz_array)
    if 'shifting_left' in detailed_restrictions:
        prep_detailed_restriction(detailed_restrictions['shifting_left'], shifting_left_array)
    if 'shifting_right' in detailed_restrictions:
        prep_detailed_restriction(detailed_restrictions['shifting_right'], shifting_right_array)
    if 'raising_ubound' in detailed_restrictions:
        prep_detailed_restriction(detailed_restrictions['raising_ubound'], raising_ubound_array)
    if 'raising_lbound' in detailed_restrictions:
        prep_detailed_restriction(detailed_restrictions['raising_lbound'], raising_lbound_array)
    
    restrictions['lbound_plan'] = shifting_right_array
    restrictions['ubound_plan'] = shifting_left_array
    restrictions['ubound_prof'] = raising_ubound_array
    restrictions['lbound_prof'] = raising_lbound_array
    restrictions['v_pass'] = v_pass_array
    restrictions['v_max'] = v_pass_array
    restrictions['v_gruz'] = v_gruz_array
    
    return restrictions


def change_sym_chord(data, init_horde, horde_to_change):
    ih = 1000 * init_horde
    ch = 1000 * horde_to_change
    z = (data**2 + ih**2)/data/2
    new_data = z - np.sign(z)*(z**2 - ch**2)**0.5
    return new_data

def change_machine_chord_to_sym_chord_10(measurements: np.ndarray, back_chord: float, front_chord: float, measuring_step: float = 0.185) -> np.ndarray:
    measurements_0185 = horde_to_horde(
                                measurements,
                                back_chord, 
                                front_chord, 
                                measuring_step, 
                                SYM_CHORD_0185, 
                                SYM_CHORD_0185)  
    return change_sym_chord(measurements_0185, SYM_CHORD_0185, SYM_CHORD_10)
