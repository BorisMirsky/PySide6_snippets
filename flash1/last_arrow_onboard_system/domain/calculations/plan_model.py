import pandas as pd
import numpy as np
from typing import List
from typing_extensions import Self
from enum import Enum
from cantok import SimpleToken

from .helpers import normative_slope_by_velocity, change_sym_chord
from .project_plan_and_profile.bounded_track_calculation import PlanCalculation
from .project_plan_and_profile.smart_track_split import SmartSplitPlanCalculation
from .project_plan_and_profile.split_profile_calculation import ProfileCalculation
import domain.calculations.project_plan_and_profile.split_plan_calculation_2 as split_plan
# from domain.dto.Travelling import ProgramTaskBaseData
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from domain.dto.Travelling import PicketDirection

# 
def build_plan_summary(base_plan: pd.DataFrame, alc_plan: pd.DataFrame, alc_level: pd.DataFrame, plan_length: float = None) -> pd.DataFrame:
    """
    Строит ведомость кривых на основе 3-х датафреймов: ОСНОВНОЙ-план, ALC-план и ALC-уровнь.
    Если длина плана (в метрах) не задана, то последний элемент ALC не будет включен.
    """
    def get_curve_type(row) -> str:
        if row.geom == 'радиус':
            return TrackElementGeometry.Curve.value #'straight' if abs(row.value) > 4000 else 'curve'
        if row.geom == 'линейный':
            return TrackElementGeometry.Transition.value #'transition'
        raise Exception('Undefined curve type')

    plan_length = (len(base_plan)-1)*10 if plan_length is None else plan_length

    # ALC plan
    alc_plan_ = pd.DataFrame(columns=['position', 'geom', 'value'])
    alc_plan_.position = alc_plan[alc_plan.columns[1]].astype('float')
    alc_plan_.geom = alc_plan[alc_plan.columns[3]]
    alc_plan_.value = alc_plan[alc_plan.columns[5]].astype('float')
    alc_plan_.reset_index(drop=True, inplace=True)
    alc_plan_.loc[len(alc_plan_)] = [plan_length, None, None]
    
    # ALC level
    alc_urov = pd.DataFrame(columns=['position', 'geom', 'value'])
    alc_urov.position = alc_level[alc_level.columns[1]].astype('float')
    alc_urov.geom = alc_level[alc_level.columns[3]]
    alc_urov.value = alc_level[alc_level.columns[5]].astype('float')
    alc_urov.reset_index(drop=True, inplace=True)
    alc_urov.loc[len(alc_urov)] = [plan_length, None, None]
    # Summary
    summary = pd.DataFrame(columns=['geom', 'start', 'end'])
    summary['start'] = alc_plan_.position[:-1].values
    summary['end'] = alc_plan_.position[1:].values
    summary['length'] = summary.end - summary.start 
    summary['radius'] = [(v if g == 'радиус' else None) for g,v in zip(alc_plan_[:-1].geom, alc_plan_[:-1].value)] # в переходных кривых радиус отсутствует
    summary['level'] = [(v if g == 'возвышение' else 0) for g,v in zip(alc_urov[:-1].geom, alc_urov[:-1].value)] # возвышение везде, кроме круговых кривых, равно 0
    # summary['geom'] = alc_plan_.geom.iloc[:-1]
    # summary['curve_type'] = alc_plan_.iloc[:-1].apply(get_curve_type, axis=1)
    summary['geom'] = alc_plan_.iloc[:-1].apply(get_curve_type, axis=1)
    summary.index = range(len(summary))
    
    return summary.round(3)


"""
Функция зажатия сдвижек.
"""
def sz_sdv(start_point_new_sdv, end_point_new_sdv, new_lbound, new_ubound, new_add_evl,
           pkt, recalculated_rix, f, initial_ur, v_max,
           shift, degree_template, min_radius_length, min_per_length, tol, token,
           degree_list, breaks, y_vals, plan_prj, sdv, sdv_shift_const=100):

    nscp = 0
    necp = len(breaks) - 1

    for i in range(len(breaks) - 1):
        if breaks[i + 1] > start_point_new_sdv - sdv_shift_const:
            nscp = i
            break

    for i in range(len(breaks) - 1, 0, -2):
        if breaks[i - 2] < end_point_new_sdv + sdv_shift_const:
            necp = i
            break

    new_f = f.copy()
    if nscp > 0:
        new_f[0] = y_vals[nscp]
    last_f = None
    if necp < len(breaks) - 1:
        last_f = y_vals[necp]

    ba = (pkt <= breaks[necp])
    summ_str = np.sum(recalculated_rix[pkt < breaks[nscp]] - plan_prj[pkt < breaks[nscp]])
    new_summ_str = np.sum(recalculated_rix[pkt > breaks[necp]] - plan_prj[pkt > breaks[necp]])

    s1 = sdv[pkt < breaks[nscp]]
    last_evl = 0
    if len(s1) > 0:
        last_evl = s1[-1] / 2

    s2 = sdv[pkt <= breaks[necp]]
    new_evl = 0
    if len(s2) > 0:
        new_evl = s2[-1] / 2
    summ_sdv = 0

    x = pkt[ba]
    y = recalculated_rix[ba]

    a_evl = None
    if new_add_evl is not None:
        a_evl = np.copy(new_add_evl[ba])

    new_calcer = SmartSplitPlanCalculation(x, y, initial_ur[ba], v_max[ba], new_lbound[ba], new_ubound[ba],
                                       shift, min_radius_length, min_per_length, max_per_length=None,
                                       degree_template=degree_template, f=new_f.copy(), tol=tol, token=token, add_evl=a_evl)

    init_prj = plan_prj[pkt < breaks[nscp]]

    new_degree_list, new_breaks, new_y_vals, new_plan_prj, new_sdv = new_calcer.track_split_calculation(summ_str, last_evl, summ_sdv,
                                                                                                        new_summ_str, new_evl, last_f, breaks[nscp], init_prj)

    new_custom_degree_list = np.concatenate([degree_list[:nscp + 1], new_degree_list[1:]])
    new_custom_degree_list = np.concatenate([new_custom_degree_list, degree_list[necp:]])
    new_custom_breaks = np.concatenate([breaks[:nscp + 1], new_breaks[1: -1]])
    new_custom_breaks = np.concatenate([new_custom_breaks, breaks[necp:]])
    new_custom_y_vals = np.concatenate([y_vals[:nscp + 1], new_y_vals[1: -1]])
    new_custom_y_vals = np.concatenate([new_custom_y_vals, y_vals[necp:]])

    # boolarr = (pkt >= new_breaks[0]) & (pkt <= new_breaks[-1])
    new_project_prj = np.copy(plan_prj)
    new_project_prj[ba] = new_plan_prj
    new_sdv_full = np.copy(sdv)
    new_sdv_full[ba] = new_sdv

    new_custom_calcer = SmartSplitPlanCalculation(pkt, recalculated_rix, initial_ur, v_max, new_lbound, new_ubound,
                                       shift, min_radius_length, min_per_length, max_per_length=None,
                                       degree_template=degree_template, f=f, tol=tol, token=token, add_evl=None)

    new_custom_calcer.degree_list = new_custom_degree_list
    new_custom_calcer.breaks = new_custom_degree_list
    new_custom_calcer.y_vals = new_custom_y_vals

    result = (new_custom_degree_list, new_custom_breaks, new_custom_y_vals, new_project_prj, new_sdv_full)
    new_track_split, new_ev_table = new_custom_calcer.calculate_track_parameters(new_custom_breaks, new_custom_y_vals, new_project_prj, new_sdv_full, f_urov=None)
    return result, new_track_split, new_ev_table

class TrackSectionGeometry(Enum):
    Straight = 'прямая'
    Curve = 'кривая'

class TrackElementGeometry(Enum):
    # Straight = 'прямая'
    Curve = 'круговая кривая'
    Transition = 'переходная кривая'

class TrackProjectType(Enum):
    Plan = 1
    Profile = 2
    Level = 3


class TrackElement:
    """
    """  
    def __init__(self, geom: TrackElementGeometry, start: float, end: float, radius: float = None, level: float = None):
        self.__parent: TrackProjectModel = None
        self.__geom = TrackElementGeometry(geom) 
        self.__start = start
        self.__end = end
        self.__radius = radius
        self.__level = level
        
        self.__a_nepog = None
        self.__level_delta = None

        self.__new_start = None
        self.__new_end = None
        
        self.__new_radius = None
        self.__new_level = None
        self.__new_length = None
        self.__modified = False
    
    def __str__(self):
        return f'TrackElement(geometry={self.name}, start={self.start_point()}, end={self.end_point()}, radius={self.radius_fact})'
    def __repr__(self): 
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            'geom': self.geometry.value, 
            'start': self.start, 
            'end': self.end, 
            'start_picket': self.start_picket, 
            'end_picket': self.end_picket, 
            'length': self.length, 
            'radius_fact': self.radius_fact, 
            'radius_norm': self.radius_norm, 
            'level_fact': self.level_fact, 
            'level_norm': self.level_norm,
            'a_nepog_fact': self.a_nepog_fact, 
            'a_nepog_norm': self.a_nepog_norm,
            'slope_fact': self.slope_fact, 
            'slope_norm': self.slope_norm, 
            'psi_fact': self.psi_fact, 
            'psi_norm': self.psi_norm,
            'v_wheel_fact': self.v_wheel_fact,
            'v_wheel_norm': self.v_wheel_norm,
            'v_max_fact': self.v_max_fact,
            'v_max_norm': self.v_max_norm,
        }
    
    @property
    def parent(self):
        return self.__parent
    @parent.setter
    def parent(self, value):
        self.__parent = value
    @property
    def track(self):
        return self.__parent
    @property
    def name(self) -> str:
        return self.__geom.name
    @property
    def modified(self) -> bool:
        return self.__modified
    @property
    def step(self) -> float:
        return self.track.step
        
    @property
    def length(self) -> float:
        return abs(self.__end - self.__start)
    
    def calc_new_length(self) -> float:
        if self.__new_end is None and self.__new_start is None:
            return np.nan        
        end = self.__end if self.__new_end is None else self.__new_end
        start = self.__start if self.__new_start is None else self.__new_start
        return end - start
    
    @property
    def new_length(self) -> float:
        return self.__new_length 
    @new_length.setter
    def new_length(self, value: float):
        self.__new_length = value
    @property
    def new_radius(self) -> float:
        return self.__new_radius 
    @new_radius.setter
    def new_radius(self, value: float):
        self.__new_radius = value
        self.__modified = True

    @property
    def new_level(self) -> float:
        return self.__new_level 
    @new_level.setter
    def new_level(self, value: float):
        self.__new_level = value
        self.__modified = True

    @property
    def radius_fact(self) -> float:
        if self.__radius is None:
            self.__radius = self.get_radius_prj()
        return self.__radius
    @property
    def radius_norm(self) -> float:
        # Rдоп= V2 max пасс / ((0.7 + 0.0061 * ВНРдоп) * 13)
        return self.v_max_pass**2 / ((0.7 + 0.0061 * self.level_norm) * 13) if self.__geom != TrackElementGeometry.Transition else None
    
    @property
    def level_fact(self) -> float:
        # ВНРсущ = Полученное в расчете
        if self.__level is None:
            self.__level = self.get_level_prj()
        return self.__level
    @property
    def level_norm(self) -> float:
        # ВНРдоп = ((Vmax.пасс**2/13Rсущ)-0,7) / 0,0061)
        val = None
        if self.__geom != TrackElementGeometry.Transition:
            val = (self.v_max_pass**2 / (13*self.radius_fact) - 0.7) / 0.0061
        return val
    @property
    def level_delta(self) -> float:
        if self.__level_delta is None:
            self.__level_delta = self.get_level_delta()
        return self.__level_delta

    @property
    def slope_norm(self) -> float:
        return self.get_slope_norm()
    @property
    def slope_fact(self) -> float:
        return self.get_slope_fact()
    
    @property
    def v_max_pass(self) -> float:
        return self.data.V_max.max()
    @property
    def v_max_fact(self) -> float:
        return self.v_max_pass
    @property
    def v_max_norm(self) -> float:
        # Для переходной кривой: 
            # Vmax доп = (Fv доп*3,6*Lпк.доп)/ВНРдоп(?)
        # Для круговой кривой:
            # V доп=√((0,7+0,0061*ВНРсущ)*13*Rсущ)

        if self.__geom == TrackElementGeometry.Transition:
            return None #(self.v_wheel_norm*3.6*self.level_norm)/self.level_norm
        
        return np.sqrt(abs((0.7 + 0.0061*self.level_fact)*13*self.radius_fact))
    
    @property
    def a_nepog_fact(self) -> float:
        # Анеп=(Vmax.пасс**2/13Rсущ)-0.0061*ВНРсущ
        if self.__geom == TrackElementGeometry.Transition:
            return None
        if self.__a_nepog is None:
            self.__a_nepog = self.v_max_pass**2 / (13*self.radius_fact) - 0.0061*self.level_fact
        return self.__a_nepog 
    @property
    def a_nepog_norm(self) -> float:
        # По умолчанию 0,7
        # Анеп доп=0.4, 0,7, 0,8, 0,9, 1,0, 1,5
        return 0.7
    @property
    def a_nepog_delta(self) -> float:
        return self.get_a_nepog_delta()
    
    @property
    def psi_fact(self) -> float:
        # Пси=(abs(∆Анеп)*Vmaxпасс)/3,6Lпк.сущ.
        return abs(self.a_nepog_delta)*self.v_max_pass / (3.6*self.length)
    @property
    def psi_norm(self) -> float:
        return 0.6
    
    @property
    def v_wheel_fact(self) -> float:
        # Fv=(Vmaxпасс/3,6Lпк.сущ)*∆ВНРсущ
        return (self.v_max_pass / (3.6*self.length))*self.level_delta
    @property
    def v_wheel_norm(self) -> float:
        return 36
    
    @property
    def geometry(self) -> TrackElementGeometry:
        return self.__geom
    @property
    def type(self) -> TrackElementGeometry:
        return self.__geom
    
    @property
    def start(self) -> float:
        return self.__start
    @property
    def end(self) -> float:
        return self.__end
    @property
    def start_index(self) -> int:
        return int(np.ceil(self.__start/self.step))
    @property
    def end_index(self) -> int:
        return int(np.floor(self.__end/self.step))
    @property
    def start_picket(self) -> float:
        return self.track.start_picket + self.__start * self.track.direction_multiplier
    @property
    def end_picket(self) -> float:
        return self.track.start_picket + self.__end * self.track.direction_multiplier
    
    @property
    def new_start(self) -> float:
        return self.__new_start
    @new_start.setter
    def new_start(self, value) -> float:
        self.__new_start = value
    @property
    def new_end(self) -> float:
        return self.__new_end
    @new_end.setter
    def new_end(self, value):
        self.__new_end = value
    
    def start_point(self) -> float:
        # Если положение начала изменилось, то возвращает self.__new_start, иначе self.__start
        return self.__new_start if self.__new_start is not None else self.start 
    def end_point(self) -> float:
        # Если положение конца изменилось, то возвращает self.__new_end, иначе self.__end
        return self.__new_end if self.__new_end is not None else self.end 

    @property
    def data(self) -> pd.DataFrame:
        if self.track is None:
            return None
        return self.track.data[self.start_index:self.end_index+1]
    
    def get_radius_prj(self) -> float:
        if self.data is None:
            return None
        if self.__geom == TrackElementGeometry.Transition:
            return None
        return 50000/self.data.plan_prj.mean()
    
    # def get_level_fact(self) -> float:
    #     return self.data.vozv_fact.mean() if self.__geom != TrackElementGeometry.Transition else None    
    def get_level_prj(self) -> float:
        return self.data.vozv_prj.mean() if self.__geom != TrackElementGeometry.Transition else None

    def get_level_delta(self) -> float:
        # Имеет смысл для переходной кривой. 
        # ВНР_next - ВНР_prev
        if self.__geom != TrackElementGeometry.Transition:
            return 0
        next_value = 0 if (next_elem := self.next_element()) is None else next_elem.level_fact 
        prev_value = 0 if (prev_elem := self.prev_element()) is None else prev_elem.level_fact
        return (next_value if next_value is not None else 0) - (prev_value if prev_value is not None else 0)

    def get_a_nepog_delta(self) -> float:
        # Имеет смысл для переходной кривой. 
        # ВНР_next - ВНР_prev
        if self.__geom != TrackElementGeometry.Transition:
            return 0
        next_value = 0 if (next_elem := self.next_element()) is None else next_elem.a_nepog_fact
        prev_value = 0 if (prev_elem := self.prev_element()) is None else prev_elem.a_nepog_fact
        return (next_value if next_value is not None else 0) - (prev_value if prev_value is not None else 0)
    
    def get_slope_fact(self) -> float:
        # i=∆ВНРсущ/Lпк
        return self.get_level_delta() / self.length if self.__geom == TrackElementGeometry.Transition else None

    def get_slope_norm(self) -> float:
        return normative_slope_by_velocity(self.data.V_max.max()) if self.__geom == TrackElementGeometry.Transition else None


    def __shift_new_start(self, delta: float):
        # Сдивагает начало текущего и конец предыдущего элемента на значение delta.
        self.__new_start = self.start + delta        
        # Если вернули прежнее значение, то новое значение сбрасываем в None
        if self.__new_start == self.start:
            self.__new_start = None

    def __shift_new_end(self, delta: float):
        # Сдивагает конец текущего и начало следующего элемента на значение delta.        
        self.__new_end = self.end + delta        
        # Если вернули прежнее значение, то новое значение сбрасываем в None
        if self.__new_end == self.end:
            self.__new_end = None

    def shift_start(self, delta: float):
        # Сдивагает начало текущего и конец предыдущего элемента на значение delta.
        self.__modified = True
        self.__shift_new_start(delta)
        self.new_length = self.calc_new_length()

        if self.prev_element() is not None:
            self.prev_element().__shift_new_end(delta)

    def shift_end(self, delta: float):
        # Сдивагает конец текущего и начало следующего элемента на значение delta.
        self.__modified = True        
        self.__shift_new_end(delta)
        self.new_length = self.calc_new_length()

        if self.next_element() is not None:
            self.next_element().__shift_new_start(delta)

    def shift(self, delta: float):
        # Сдивагает элемент (начало и конец) на значение delta.
        self.shift_start(delta)
        self.shift_end(delta)

    def next_element(self) -> Self | None:
        elements = self.track.elements()
        idx = elements.index(self) + 1
        return elements[idx] if idx < len(elements) else None
    
    def prev_element(self) -> Self | None:
        elements = self.track.elements()
        idx = elements.index(self) - 1
        return None if idx < 0 else elements[idx]
 
    def insert_curve_at(self, x: float, min_length: float = 20):
        """
            Выполняет прямую вставку (aka. Разделить ПК).
        """
        # начало и конец элемента-вставки
        x1 = x - min_length/2
        x2 = x + min_length/2

        # TODO: Сделать проверку, что все 3-и элемента имеют длину >= min_length

        # создаем два новых элемента (собственно сама вставка и вторая часть переходной)
        new_elem1 = TrackElement(geom=TrackElementGeometry.Curve, start=x1, end=x2)
        new_elem2 = TrackElement(geom=TrackElementGeometry.Transition, start=x2, end=self.end)
        
        # у текущего элемента (переходной) передвигаем конец на начало элемента-вставки
        self.__new_end = x1
        # добавляем новые элементы
        self.track.append_elements_after([new_elem1, new_elem2], self)

    def remove(self):
        '''
            Удаление переходной кривой.
            Реальное удаление пока не реализовано, поэтому делаем следующий костыль: длину переходной кривой устанавливаем 
            в очень маленькое значение (например 0.01).
        '''
        zero_length = 0.01
        self.shift_start(self.length/2 - zero_length/2)
        self.shift_end(zero_length/2 - self.length/2)

    

class TrackProjectModel:
    @classmethod
    def create(cls, project_type: TrackProjectType, task: ProgramTaskCalculationResultDto):
        model = None
        match project_type:
            case TrackProjectType.Plan:
                plan_version = task.options.restrictions['optimization_parameters'].get('calc_plan_version')
                match plan_version:
                    case 'split':
                        model = TrackSplitPlanProjectModel(
                                    track_split=task.base.track_split_plan, 
                                    data=task.base.plan,
                                    start_picket= task.options.start_picket.meters,
                                    picket_direction= task.options.picket_direction)
                    case 'split2':
                        model = TrackSplitPlanProjectModelV2(
                                    track_split=task.base.track_split_plan, 
                                    data=task.base.plan,
                                    start_picket= task.options.start_picket.meters,
                                    picket_direction= task.options.picket_direction)
                    case 'smartsplit':
                        model = TrackSmartSplitPlanProjectModel(
                                    track_split=task.base.track_split_plan, 
                                    data=task.base.plan,
                                    start_picket= task.options.start_picket.meters,
                                    picket_direction= task.options.picket_direction)
                    case _:
                        model = TrackPlanProjectModel(
                                    track_split=task.base.track_split_plan, 
                                    data=task.base.plan,
                                    start_picket= task.options.start_picket.meters,
                                    picket_direction= task.options.picket_direction)
                # model = TrackSplitPlanProjectModelV2(
                #                     track_split=task.base.track_split_plan, 
                #                     data=task.base.plan,
                #                     start_picket= task.options.start_picket.meters,
                #                     picket_direction= task.options.picket_direction)
            case TrackProjectType.Profile:
                model = TrackProfileProjectModel(
                            track_split=task.base.track_split_prof, 
                            data=task.base.prof, 
                            detailed_restrictions=task.base.detailed_restrictions)
            case TrackProjectType.Level:
                model = TrackLevelProjectModel(track_split=task.base.track_split_plan, data=task.base.plan)
            case _:
                raise Exception('Неизвестный тип проекта')
        
        return model

    def __init__(self, start_picket: float, picket_direction: PicketDirection, step = 0.185):
        self.__start_picket = start_picket
        self.__picket_direction = picket_direction
        self.__step = step
        self.__direction_multiplier = picket_direction.multiplier()
        
    @property
    def start_picket(self) -> float:
        return self.__start_picket
    @property
    def picket_direction(self) -> float:
        return self.__picket_direction
    @property
    def direction_multiplier(self) -> int:
        return self.__direction_multiplier
    @property
    def step(self) -> float:
        return self.__step
    
    @property
    def data(self) -> pd.DataFrame:
        pass
    
    @property
    def track_split(self) -> pd.DataFrame:
        pass
    
    def calc_new_track(self) -> Self:
        pass
    
    def picketToPosition(self, picket: float) -> float:
        return (picket - self.__start_picket) * self.__direction_multiplier

class TrackPlanProjectModel(TrackProjectModel):
    """
    Represents the project plan for the track.
    Consists of track elements of 2 types: transitions and curves. 
    """
    @classmethod
    def change_horde(cls, data, init_horde, horde_to_change):
        return change_sym_chord(data, init_horde, horde_to_change)
    
    def __init__(self, track_split: pd.DataFrame, data: pd.DataFrame, step: float = 0.185, start_picket: float = 0, picket_direction: PicketDirection = PicketDirection.Forward):
        super().__init__(start_picket=start_picket, picket_direction=picket_direction, step=step)
        print(f'> Plan reconstruction with {self.__class__.__name__}...')
        self.__track_split = track_split
        self.__data = data

        # из track_split создаем коллекцию элементов
        self.__elements: List[TrackElement] = []
        for idx, row in track_split.iterrows():
            self.add_element(TrackElement(geom=row.geom, start=row.start, end=row.end))

        # создаем PlanCalculation 
        self.__calcer = PlanCalculation(
                            pkt = step * np.arange(len(data)),
                            recalculated_rix = change_sym_chord(data=self.__data.plan_fact, init_horde=10, horde_to_change=0.185),
                            initial_ur = self.__data.vozv_fact,
                            v_max = self.__data.V_max,
                            lower_bound = self.__data.lbound,
                            upper_bound = self.__data.ubound,
                            add_evl = np.zeros(len(self.__data)),
                            token = SimpleToken()
                        )
        self.__update_calcer()
        # self.__pwlf = None
        # self.pwlf_init()

    def __update_calcer(self):
        self.__calcer.breaks = self.breaks()
        self.__calcer.degree_list = self.degree_list()

    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    
    @property
    def track_split(self) -> pd.DataFrame:
        return self.__track_split
    @property
    def calcer(self) -> PlanCalculation:
        return self.__calcer

    def elements(self, geom: TrackElementGeometry = None) -> List[TrackElement]:
        return self.__elements if geom is None else [e for e in self.__elements if e.geometry == geom]
    
    def degree_list(self) -> List[int]:
        # Разбиение участка: 0 - круговая кривая/прямая, 1 - переходная кривая.
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.elements()]

    def new_lengths(self) -> List[float]:
        # Пользовательские ограничения на длины переходных кривых и круговых кривых. 
        # Np.nan - без ограничения
        # Возвращает список длин в десятиметровках.
        return np.array([elem.new_length for elem in self.elements()])/self.step
        
    def new_radiuses(self) -> List:
        # Пользовательские ограничения на радиус кривых. Np.nan - без ограничения. 
        # Имеет смысл задавать только f[i], где u[i] = 0, т.к. на переходной кривой радиус не может быть константой
        return [elem.new_radius for elem in self.elements(TrackElementGeometry.Curve)]

    # def new_arrows(self) -> List[float]:
    #     # Список стрел, вычисляемых из заданных радиусов.
    #     return [(np.nan if r is np.nan or r is None else 50000/r) for r in self.new_radiuses()]
    
    def new_f_vector(self) -> List[float]:
        # Список стрел (), вычисляемых из заданных радиусов.
        return [(None if e.new_radius is None else change_sym_chord(50000/e.new_radius, 10, 0.185)) 
                    for e in self.elements(TrackElementGeometry.Curve)]

    def new_levels(self) -> List[float]:
        # Список задаваемых уровней (ВНР).
        return [(None if e.new_level is None else e.new_level) 
                    for e in self.elements(TrackElementGeometry.Curve)]

    def breaks(self) -> List[float]:
        """
        Возвращвет список точек излома."""
        points = [e.start_point() for e in self.elements()]
        points.append(self.elements()[-1].end_point())
        return np.array(points)
        
    def to_dataframe(self) -> pd.DataFrame:
        elems = [e.to_dict() for e in self.elements()]
        return pd.DataFrame(elems).round(3)
    def summary(self) -> pd.DataFrame:
        return self.to_dataframe()
    def ubound(self):
        return np.inf*np.ones((len(self.data), ))
    def lbound(self):
        return -np.inf*np.ones((len(self.data), ))
    
    def add_element(self, elem: TrackElement):
        elem.parent = self
        self.__elements.append(elem)

    def append_elements_after(self, new_elements: list[TrackElement], element: TrackElement):
        insert_idx = self.elements().index(element)
        for e in new_elements:
            e.parent = self
            insert_idx += 1
            self.elements().insert(insert_idx, e)
        # изменился состав элементов, поэтому обновляем calcer
        self.__update_calcer() 
        

    def pwlf_init(self):
        self.__pwlf = self.__calcer.pwlf_init(
                            degree_list=self.degree_list(), 
                            f=self.new_f_vector(), 
                            add_evl=self.__calcer.add_evl, 
                            sum_evl_to_zero=False)
        self.__calcer.pwlf = self.__pwlf
    
    def calc_new_track(self) -> Self:
        self.pwlf_init()
        breaks, new_y_vals, plan_prj, sdv = self.__calcer.fixed_points_calculation(self.__pwlf, self.breaks(), self.new_f_vector())
        track_split, ev_table = self.__calcer.calculate_track_parameters(breaks, new_y_vals, plan_prj, sdv, f_urov=self.new_levels())
        ev_table.index.name = 'step'

        new_plan = TrackPlanProjectModel(
                        track_split=track_split, 
                        data=ev_table, 
                        start_picket=self.start_picket, 
                        picket_direction=self.picket_direction)

        for src_elem, dst_elem in zip(self.elements(), new_plan.elements()):
            dst_elem.new_radius = src_elem.new_radius
            dst_elem.new_level = src_elem.new_level
            # dst_elem.new_radius = src_elem.new_radius
        return new_plan


class TrackSplitPlanProjectModel(TrackProjectModel):
    """
    Represents the project plan for the track.
    Consists of track elements of 2 types: transitions and curves. 
    """    
    def __init__(self, track_split: pd.DataFrame, data: pd.DataFrame, step: float = 0.185, start_picket: float = 0, picket_direction: PicketDirection = PicketDirection.Forward):
        super().__init__(start_picket=start_picket, picket_direction=picket_direction, step=step)
        print(f'> Plan reconstruction with {self.__class__.__name__}...')
        self.__track_split = track_split
        self.__data = data

        # из track_split создаем коллекцию элементов
        self.__elements: List[TrackElement] = []
        for idx, row in track_split.iterrows():
            self.add_element(TrackElement(geom=row.geom, start=row.start, end=row.end))

        # создаем PlanCalculation 
        self.__calcer = split_plan.PlanCalculation(
                            pkt = step * np.arange(len(data)),
                            initial_rix = self.plan_fact_10,
                            recalculated_rix = self.plan_fact_0185,
                            initial_ur = np.array(self.__data.vozv_fact),
                            v_max = np.array(self.__data.V_max),
                            lower_bound = np.array(self.__data.lbound),
                            upper_bound = np.array(self.__data.ubound),
                            add_evl = np.zeros(len(self.__data)),
                            token = SimpleToken()
                        )
        self.update_calcer()

    @property
    def plan_fact_10(self):
        return np.array(self.__data.plan_fact)
    @property
    def plan_fact_0185(self):
        return np.array(self.__data.loc[:, self.__data.columns[2]])
    
    def update_calcer(self):
        self.__calcer.breaks = self.breaks()
        self.__calcer.degree_list = self.degree_list()

    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    @property
    def track_split(self) -> pd.DataFrame:
        return self.__track_split
    @property
    def calcer(self) -> PlanCalculation:
        return self.__calcer

    def elements(self, geom: TrackElementGeometry = None) -> List[TrackElement]:
        return self.__elements if geom is None else [e for e in self.__elements if e.geometry == geom]
    
    def degree_list(self) -> List[int]:
        # Разбиение участка: 0 - круговая кривая/прямая, 1 - переходная кривая.
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.elements()]

    def new_lengths(self) -> List[float]:
        # Пользовательские ограничения на длины переходных кривых и круговых кривых. 
        # Np.nan - без ограничения
        # Возвращает список длин в десятиметровках.
        return np.array([elem.new_length for elem in self.elements()])/self.step
        
    def new_radiuses(self) -> List:
        # Пользовательские ограничения на радиус кривых. Np.nan - без ограничения. 
        # Имеет смысл задавать только f[i], где u[i] = 0, т.к. на переходной кривой радиус не может быть константой
        return [elem.new_radius for elem in self.elements(TrackElementGeometry.Curve)]

    # def new_arrows(self) -> List[float]:
    #     # Список стрел, вычисляемых из заданных радиусов.
    #     return [(np.nan if r is np.nan or r is None else 50000/r) for r in self.new_radiuses()]
    
    def new_f_vector(self) -> List[float]:
        # Список стрел (), вычисляемых из заданных радиусов.
        return [(None if e.new_radius is None else change_sym_chord(50000/e.new_radius, 10, 0.185)) 
                    for e in self.elements(TrackElementGeometry.Curve)]

    def new_levels(self) -> List[float]:
        # Список задаваемых уровней (ВНР).
        return [(None if e.new_level is None else e.new_level) 
                    for e in self.elements(TrackElementGeometry.Curve)]

    def breaks(self) -> List[float]:
        """
            Возвращвет список точек излома.
        """
        points = [e.start_point() for e in self.elements()]
        points.append(self.elements()[-1].end_point())
        return np.array(points)
        
    def to_dataframe(self) -> pd.DataFrame:
        elems = [e.to_dict() for e in self.elements()]
        return pd.DataFrame(elems).round(3)
    def summary(self) -> pd.DataFrame:
        return self.to_dataframe()
    def ubound(self):
        return np.inf*np.ones((len(self.data), ))
    def lbound(self):
        return -np.inf*np.ones((len(self.data), ))
    
    def add_element(self, elem: TrackElement):
        elem.parent = self
        self.__elements.append(elem)

    def append_elements_after(self, new_elements: list[TrackElement], element: TrackElement):
        insert_idx = self.elements().index(element)
        for e in new_elements:
            e.parent = self
            insert_idx += 1
            self.elements().insert(insert_idx, e)
        # изменился состав элементов, поэтому обновляем calcer
        self.update_calcer() 
        
    
    def calc_new_track(self) -> Self:
        """
        """
        breaks, new_y_vals, plan_prj, sdv = self.__calcer.fixed_points_calculation(
                                                                degree_list=self.degree_list(), 
                                                                breaks= self.breaks(), 
                                                                f=self.new_f_vector())
        track_split, ev_table = self.__calcer.calculate_track_parameters(breaks, new_y_vals, plan_prj, sdv, f_urov=self.new_levels())
        ev_table.index.name = 'step'

        new_plan = TrackSplitPlanProjectModel(
                        track_split=track_split, 
                        data=ev_table, 
                        start_picket=self.start_picket, 
                        picket_direction=self.picket_direction)

        for src_elem, dst_elem in zip(self.elements(), new_plan.elements()):
            dst_elem.new_radius = src_elem.new_radius
            dst_elem.new_level = src_elem.new_level
            # dst_elem.new_radius = src_elem.new_radius
        return new_plan


class TrackSplitPlanProjectModelV2(TrackProjectModel):
    """
        Represents the project plan for the track.
        Consists of track elements of 2 types: transitions and curves. 
    """    
    def __init__(self, track_split: pd.DataFrame, data: pd.DataFrame, step: float = 0.185, start_picket: float = 0, picket_direction: PicketDirection = PicketDirection.Forward):
        super().__init__(start_picket=start_picket, picket_direction=picket_direction, step=step)
        print(f'> Plan reconstruction with {self.__class__.__name__}...')
        self.__track_split = track_split
        self.__data = data

        # из track_split создаем коллекцию элементов
        self.__elements: List[TrackElement] = []
        for idx, row in track_split.iterrows():
            self.add_element(TrackElement(geom=row.geom, start=row.start, end=row.end))

        # создаем PlanCalculation 
        self.__calcer = split_plan.PlanCalculationV2(
                            pkt = step * np.arange(len(data)),
                            initial_rix = self.plan_fact_10,
                            recalculated_rix = self.plan_fact_0185,
                            initial_ur = np.array(self.__data.vozv_fact),
                            v_max = np.array(self.__data.V_max),
                            lower_bound = np.array(self.__data.lbound),
                            upper_bound = np.array(self.__data.ubound),
                            add_evl = np.zeros(len(self.__data)),
                            token = SimpleToken()
                        )
        y_vals = track_split.y_vals_start.to_list() 
        y_vals.append(track_split.y_vals_end.iloc[-1])
        self.__calcer.y_vals = np.array(y_vals)

        self.update_calcer()

    @property
    def plan_fact_10(self):
        return np.array(self.__data.plan_fact)
    @property
    def plan_fact_0185(self):
        return np.array(self.__data.loc[:, self.__data.columns[2]])
    
    def update_calcer(self):
        self.__calcer.breaks = self.breaks()
        self.__calcer.degree_list = self.degree_list()

    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    @property
    def track_split(self) -> pd.DataFrame:
        return self.__track_split
    @property
    def calcer(self) -> PlanCalculation:
        return self.__calcer

    def elements(self, geom: TrackElementGeometry = None) -> List[TrackElement]:
        return self.__elements if geom is None else [e for e in self.__elements if e.geometry == geom]
    
    def degree_list(self) -> List[int]:
        # Разбиение участка: 0 - круговая кривая/прямая, 1 - переходная кривая.
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.elements()]

    def new_lengths(self) -> List[float]:
        # Пользовательские ограничения на длины переходных кривых и круговых кривых. 
        # Np.nan - без ограничения
        # Возвращает список длин в десятиметровках.
        return np.array([elem.new_length for elem in self.elements()])/self.step
        
    def new_radiuses(self) -> List:
        # Пользовательские ограничения на радиус кривых. Np.nan - без ограничения. 
        # Имеет смысл задавать только f[i], где u[i] = 0, т.к. на переходной кривой радиус не может быть константой
        return [elem.new_radius for elem in self.elements(TrackElementGeometry.Curve)]

    # def new_arrows(self) -> List[float]:
    #     # Список стрел, вычисляемых из заданных радиусов.
    #     return [(np.nan if r is np.nan or r is None else 50000/r) for r in self.new_radiuses()]
    
    def new_f_vector(self) -> List[float]:
        # Список стрел (), вычисляемых из заданных радиусов.
        return [(None if e.new_radius is None else change_sym_chord(50000/e.new_radius, 10, 0.185)) 
                    for e in self.elements(TrackElementGeometry.Curve)]

    def new_levels(self) -> List[float]:
        # Список задаваемых уровней (ВНР).
        return [(None if e.new_level is None else e.new_level) 
                    for e in self.elements(TrackElementGeometry.Curve)]
    
    def all_levels(self) -> List[float]:
        # Список всех уровней (ВНР).
        return [(e.level_fact if e.new_level is None else e.new_level) 
                    for e in self.elements(TrackElementGeometry.Curve)]
    
    def breaks(self) -> List[float]:
        """
            Возвращвет список точек излома.
        """
        points = [e.start_point() for e in self.elements()]
        points.append(self.elements()[-1].end_point())
        return np.array(points)
        
    def to_dataframe(self) -> pd.DataFrame:
        elems = [e.to_dict() for e in self.elements()]
        return pd.DataFrame(elems).round(3)
    def summary(self) -> pd.DataFrame:
        return self.to_dataframe()
    def ubound(self):
        return np.inf*np.ones((len(self.data), ))
    def lbound(self):
        return -np.inf*np.ones((len(self.data), ))
    
    def add_element(self, elem: TrackElement):
        elem.parent = self
        self.__elements.append(elem)

    def append_elements_after(self, new_elements: list[TrackElement], element: TrackElement):
        insert_idx = self.elements().index(element)
        for e in new_elements:
            e.parent = self
            insert_idx += 1
            self.elements().insert(insert_idx, e)
        # изменился состав элементов, поэтому обновляем calcer
        self.update_calcer() 

    def calc_new_track(self) -> Self:
        """
        """
        # print(f'degree_list = {self.degree_list()}')
        # print(f'breaks = {self.breaks()}')
        # print(f'new_f_vector = {self.new_f_vector()}')
        # print(f'new_radiuses = {self.new_radiuses()}')
        breaks, new_y_vals, plan_prj, sdv = self.__calcer.fixed_points_calculation(
                                                                degree_list=self.degree_list(), 
                                                                breaks= self.breaks(), 
                                                                f=self.new_f_vector())
        # print(f'new_y_vals = {new_y_vals}')
        # plan_prj - 3 столбец 
        track_split, ev_table = self.__calcer.calculate_track_parameters(breaks, new_y_vals, plan_prj, sdv, f_urov=self.all_levels())
        ev_table.index.name = 'step'

        new_plan = TrackSplitPlanProjectModelV2(
                        track_split=track_split, 
                        data=ev_table, 
                        start_picket=self.start_picket, 
                        picket_direction=self.picket_direction)

        for src_elem, dst_elem in zip(self.elements(), new_plan.elements()):
            dst_elem.new_radius = src_elem.new_radius
            dst_elem.new_level = src_elem.new_level

        return new_plan
    

class TrackSmartSplitPlanProjectModel(TrackProjectModel):
    """
        Represents the project plan for the track.
        Consists of track elements of 2 types: transitions and curves. 
    """    
    def __init__(self, track_split: pd.DataFrame, data: pd.DataFrame, step: float = 0.185, start_picket: float = 0, picket_direction: PicketDirection = PicketDirection.Forward):
        super().__init__(start_picket=start_picket, picket_direction=picket_direction, step=step)
        print(f'> Plan reconstruction with {self.__class__.__name__}...')
        self.__track_split = track_split
        self.__data = data

        # из track_split создаем коллекцию элементов
        self.__elements: List[TrackElement] = []
        for idx, row in track_split.iterrows():
            self.add_element(TrackElement(geom=row.geom, start=row.start, end=row.end))

        # создаем PlanCalculation 
        self.__calcer = SmartSplitPlanCalculation(
                            pkt = step * np.arange(len(data)),
                            # initial_rix = self.plan_fact_10,
                            recalculated_rix = self.plan_fact_0185,
                            initial_ur = np.array(self.__data.vozv_fact),
                            v_max = np.array(self.__data.V_max),
                            lower_bound = np.array(self.__data.lbound),
                            upper_bound = np.array(self.__data.ubound),
                            add_evl = np.zeros(len(self.__data)),
                            token = SimpleToken()
                        )
       
        y_vals = track_split.y_vals_start.to_list() 
        y_vals.append(track_split.y_vals_end.iloc[-1])
        self.__calcer.y_vals = np.array(y_vals)

        self.update_calcer()

    @property
    def plan_fact_10(self):
        return np.array(self.__data.plan_fact)
    @property
    def plan_fact_0185(self):
        return np.array(self.__data.loc[:, self.__data.columns[2]])
    @property
    def level_fact(self):
        return np.array(self.__data.vozv_fact)
    
    def update_calcer(self):
        self.__calcer.breaks = self.breaks()
        self.__calcer.degree_list = self.degree_list()

    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    @property
    def track_split(self) -> pd.DataFrame:
        return self.__track_split
    @property
    def calcer(self) -> PlanCalculation:
        return self.__calcer

    def elements(self, geom: TrackElementGeometry = None) -> List[TrackElement]:
        return self.__elements if geom is None else [e for e in self.__elements if e.geometry == geom]
    
    def degree_list(self) -> List[int]:
        # Разбиение участка: 0 - круговая кривая/прямая, 1 - переходная кривая.
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.elements()]

    def new_lengths(self) -> List[float]:
        # Пользовательские ограничения на длины переходных кривых и круговых кривых. 
        # Np.nan - без ограничения
        # Возвращает список длин в десятиметровках.
        return np.array([elem.new_length for elem in self.elements()])/self.step
        
    def new_radiuses(self) -> List:
        # Пользовательские ограничения на радиус кривых. Np.nan - без ограничения. 
        # Имеет смысл задавать только f[i], где u[i] = 0, т.к. на переходной кривой радиус не может быть константой
        return [elem.new_radius for elem in self.elements(TrackElementGeometry.Curve)]

    # def new_arrows(self) -> List[float]:
    #     # Список стрел, вычисляемых из заданных радиусов.
    #     return [(np.nan if r is np.nan or r is None else 50000/r) for r in self.new_radiuses()]
    
    def new_f_vector(self) -> List[float]:
        # Список стрел (), вычисляемых из заданных радиусов.
        return [(None if e.new_radius is None else change_sym_chord(50000/e.new_radius, 10, 0.185)) 
                    for e in self.elements(TrackElementGeometry.Curve)]

    def new_levels(self) -> List[float]:
        # Список задаваемых уровней (ВНР).
        return [(None if e.new_level is None else e.new_level) 
                    for e in self.elements(TrackElementGeometry.Curve)]
    
    def all_levels(self) -> List[float]:
        # Список всех уровней (ВНР).
        return [(e.level_fact if e.new_level is None else e.new_level) 
                    for e in self.elements(TrackElementGeometry.Curve)]
    
    def breaks(self) -> List[float]:
        """
            Возвращвет список точек излома.
        """
        points = [e.start_point() for e in self.elements()]
        points.append(self.elements()[-1].end_point())
        return np.array(points)
        
    def to_dataframe(self) -> pd.DataFrame:
        elems = [e.to_dict() for e in self.elements()]
        return pd.DataFrame(elems).round(3)
    def summary(self) -> pd.DataFrame:
        return self.to_dataframe()
    # def ubound(self):
    #     return np.inf*np.ones((len(self.data), ))
    # def lbound(self):
    #     return -np.inf*np.ones((len(self.data), ))
    
    def add_element(self, elem: TrackElement):
        elem.parent = self
        self.__elements.append(elem)

    def append_elements_after(self, new_elements: list[TrackElement], element: TrackElement):
        insert_idx = self.elements().index(element)
        for e in new_elements:
            e.parent = self
            insert_idx += 1
            self.elements().insert(insert_idx, e)
        # изменился состав элементов, поэтому обновляем calcer
        self.update_calcer() 

    def remove_curve(self, curve: TrackElement):
        '''
            Удаление круговой кривой (КК).
            Удаляется круговая кривая и ее соседняя переходная слева или справа.

            TODO: Не реализовано: проверка можно ли удалять КК и выбор левой или правой 
            переходной - сейчас всегда правая. 
        '''
        right_transition: TrackElement = curve.next_element()
        left_transition: TrackElement = curve.prev_element()
        
        # конец левой переходной переносим в конец правой переходной
        left_transition.new_end = right_transition.end_point()
        
        # удаляем круговую кривую и правую переходную
        self.__elements.remove(right_transition)
        self.__elements.remove(curve)

    def check_radius_number_limit(self):
        """
            Мы можем применить функцию `Изменить радиус` только к `n - 2` круговым кривым (КК).
            При нескольких изменениях, и при условии превышения лимита `n - 2`,
            будет отменено первое изменение радиуса.
            
            TODO: сейчас при условии превышения лимита инициируем исключение, 
            т.к. не реализовано хранение порядка изменения радиусов. 
        """
        radius_limit = len(self.new_radiuses()) - 2
        new_radius_count = len([r for r in self.new_radiuses() if r is not None])
        if new_radius_count > radius_limit:
            raise Exception(f'Количество одновременно изменяемых радиусов не должно быть больше {radius_limit}.')

    def calc_with_new_shifts(self, startPicket: float, endPicket: float, lbound: float, ubound: float):
        """
            Операция переустройства: Зажатие сдвижек.
            Параметры `start` и `end` задают начало и конец зажимаемого участка в пикетах. Их необходимо преобразовать
            в математическую систему (от нуля до N). 
            Параметры `lbound` и `ubound` задают новые значения максимальной 
            сдвижки на данном участке.
        """
        start = self.picketToPosition(startPicket)
        end = self.picketToPosition(endPicket)

        pkt = self.step * np.arange(len(self.data))
        new_range = (pkt >= start) & (pkt <= end)
        lbound_array = np.array(self.data.lbound)
        lbound_array[new_range] = lbound
        ubound_array = np.array(self.data.ubound)
        ubound_array[new_range] = ubound
        _, new_track_split, new_ev_table = sz_sdv(
                                                start, end, lbound_array, ubound_array, 
                                                new_add_evl = None,
                                                pkt = pkt, 
                                                recalculated_rix = self.plan_fact_0185, 
                                                f = self.calcer.f, 
                                                initial_ur = self.level_fact, 
                                                v_max = np.array(self.data.V_max),
                                                shift = self.calcer.shift,
                                                degree_template = self.calcer.degree_template, 
                                                min_radius_length = self.calcer.min_radius_length, 
                                                min_per_length = self.calcer.min_per_length, 
                                                tol = self.calcer.tol, 
                                                token = self.calcer.token,
                                                degree_list = self.degree_list(), 
                                                breaks = self.breaks(), 
                                                y_vals = self.calcer.y_vals, 
                                                plan_prj = np.array(self.data.plan_prj_0185), 
                                                sdv = np.array(self.data.plan_delta), 
                                                sdv_shift_const=100)
        return TrackSmartSplitPlanProjectModel(
                        track_split=new_track_split, 
                        data=new_ev_table, 
                        start_picket=self.start_picket, 
                        picket_direction=self.picket_direction)
        

    def calc_new_track(self) -> Self:
        """
            Пересчитывет проект плана с новыми параметрами.
        """
        # Проверка количества одновременно изменяемых радиусов
        self.check_radius_number_limit()

        # Пересчет проекта с фиксированными точками излома.
        breaks, new_y_vals, plan_prj, sdv = self.__calcer.fixed_points_calculation(
                                                                degree_list= self.degree_list(), 
                                                                breaks= self.breaks(), 
                                                                f= self.new_f_vector())
        # print(f'new_y_vals = {new_y_vals}')
        # plan_prj - 3 столбец 
        track_split, ev_table = self.__calcer.calculate_track_parameters(breaks, new_y_vals, plan_prj, sdv, f_urov=self.all_levels())
        ev_table.index.name = 'step'
        new_plan = TrackSmartSplitPlanProjectModel(
                        track_split=track_split, 
                        data=ev_table, 
                        start_picket=self.start_picket, 
                        picket_direction=self.picket_direction)

        for src_elem, dst_elem in zip(self.elements(), new_plan.elements()):
            dst_elem.new_radius = src_elem.new_radius
            dst_elem.new_level = src_elem.new_level

        return new_plan
    

class TrackProfileProjectModel(TrackProjectModel):
    """
    """
    def __init__(self, track_split: pd.DataFrame, data: pd.DataFrame, detailed_restrictions: dict[str, np.ndarray], step: float = 0.185, start_picket: float = 0, picket_direction: PicketDirection = PicketDirection.Forward):
        super().__init__(start_picket=start_picket, picket_direction=picket_direction, step=step)
        print('> Profile reconstruction with TrackProfileProjectModel...')
        self.__track_split = track_split
        self.__data = data
        self.__detailed_restrictions = detailed_restrictions

        # из track_split создаем коллекцию элементов
        self.__elements: List[TrackElement] = []
        for idx, row in track_split.iterrows():
            self.add_element(TrackElement(geom=row.geom, start=row.start, end=row.end, radius=row.radius))

        # создаем ProfileCalculation 
        self.__calcer = ProfileCalculation(
                            pkt = step * np.arange(len(data)),
                            recalculated_rix = self.prof_fact_0185,
                            initial_ur = np.array(self.__data.vozv_fact),
                            v_max = np.array(self.__data.V_max),
                            # lower_bound = np.array(self.__data.lbound),
                            # upper_bound = np.array(self.__data.ubound),
                            lower_bound = np.array(detailed_restrictions['lbound_prof']),
                            upper_bound = np.array(detailed_restrictions['ubound_prof']),
                            token = SimpleToken()
                        )
        self.__update_calcer()

    @property
    def track_split(self) -> pd.DataFrame:
        return self.__track_split
    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    @property
    def prof_fact_10(self):
        return np.array(self.__data.prof_fact)
    @property
    def prof_fact_0185(self):
        return np.array(self.__data.loc[:, self.__data.columns[2]])
    
    def __update_calcer(self):
        self.__calcer.breaks = self.breaks()
        self.__calcer.degree_list = self.degree_list()

    def add_element(self, elem: TrackElement):
        elem.parent = self
        self.__elements.append(elem)

    def elements(self, geom: TrackElementGeometry = None) -> List[TrackElement]:
        return self.__elements if geom is None else [e for e in self.__elements if e.geometry == geom]
    
    def degree_list(self) -> List[int]:
        """Разбиение участка: 0 - круговая кривая/прямая, 1 - переходная кривая."""
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.elements()]

    def breaks(self) -> List[float]:
        """Возвращвет список точек излома."""
        points = [e.start_point() for e in self.elements()]
        points.append(self.elements()[-1].end_point())
        return np.array(points)
    
    def new_f_vector(self) -> List[float]:
        # Список стрел (), вычисляемых из заданных радиусов.
        return [(None if e.new_radius is None else change_sym_chord(50000/e.new_radius, 10, 0.185)) 
                    for e in self.elements(TrackElementGeometry.Curve)]
    
    def calc_new_track(self) -> Self:
        """
        """
        breaks, new_y_vals, prof_prj, sdv = self.__calcer.fixed_points_calculation(
                                                                degree_list=self.degree_list(), 
                                                                breaks= self.breaks(), 
                                                                f=self.new_f_vector())
        track_split, ev_table = self.__calcer.calculate_track_parameters(breaks, new_y_vals, prof_prj, sdv)
        ev_table.index.name = 'step'
        new_model = TrackProfileProjectModel(
                        track_split= track_split, 
                        data= ev_table, 
                        detailed_restrictions= self.__detailed_restrictions,
                        start_picket= self.start_picket, 
                        picket_direction= self.picket_direction)

        for src_elem, dst_elem in zip(self.elements(), new_model.elements()):
            dst_elem.new_radius = src_elem.new_radius
            
        return new_model


class TrackLevelProjectModel(TrackProjectModel):
    """
        Wrapper class for level reconstruction. 
    """  
    def __init__(self, track_split: pd.DataFrame, data: pd.DataFrame, step: float = 0.185, start_picket: float = 0, picket_direction: PicketDirection = PicketDirection.Forward):
        super().__init__(start_picket=start_picket, picket_direction=picket_direction, step=step)
        print('> Level reconstruction with TrackLevelProjectModel...')
        self.__track_split = track_split
        self.__data = data

        # из track_split создаем коллекцию элементов
        self.__elements: List[TrackElement] = []
        for idx, row in track_split.iterrows():
            self.add_element(TrackElement(geom=row.geom, start=row.start, end=row.end))

        # создаем PlanCalculation 
        self.__calcer = split_plan.PlanCalculationV2(
                            pkt = step * np.arange(len(self.__data)),
                            initial_rix = self.plan_fact_10,
                            recalculated_rix = self.plan_fact_0185,
                            initial_ur = np.array(self.__data.vozv_fact),
                            v_max = np.array(self.__data.V_max),
                            lower_bound = np.array(self.__data.lbound),
                            upper_bound = np.array(self.__data.ubound),
                            add_evl = np.zeros(len(self.__data)),
                            token = SimpleToken()
                        )
        #  y_vals
        y_vals = track_split.y_vals_start.to_list() 
        y_vals.append(track_split.y_vals_end.iloc[-1])
        self.__calcer.y_vals = np.array(y_vals)
        # breaks
        self.__calcer.breaks = self.breaks()
        # degree_list
        self.__calcer.degree_list = self.degree_list()

    @property
    def track_split(self) -> pd.DataFrame:
        return self.__track_split
    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    
    @property
    def plan_fact_10(self):
        return np.array(self.__data.plan_fact)
    @property
    def plan_fact_0185(self):
        return np.array(self.__data.loc[:, self.__data.columns[2]])
    
    def add_element(self, elem: TrackElement):
        elem.parent = self
        self.__elements.append(elem)

    def elements(self, geom: TrackElementGeometry = None) -> List[TrackElement]:
        return self.__elements if geom is None else [e for e in self.__elements if e.geometry == geom]
    
    def degree_list(self) -> List[int]:
        """Разбиение участка: 0 - круговая кривая/прямая, 1 - переходная кривая."""
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.elements()]

    def breaks(self) -> List[float]:
        """Возвращвет список точек излома."""
        points = [e.start_point() for e in self.elements()]
        points.append(self.elements()[-1].end_point())
        return np.array(points)

    def all_levels(self) -> List[float]:
        # Список задаваемых уровней (ВНР).
        return [(e.level_fact if e.new_level is None else e.new_level) 
                    for e in self.elements(TrackElementGeometry.Curve)]

    def set_straight_level(self, level: float):
        """Выставляет уровень для всех прямых участков в level"""
        for e in self.elements(TrackElementGeometry.Curve):
            if abs(e.radius_fact) > self.__calcer.min_straight_radius:
                e.new_level = level


    def calc_new_track(self) -> Self:
        """
            Пересчитывет проект уровня с новыми параметрами.
        """
        track_split, ev_table = self.__calcer.calculate_track_parameters(
                                                breaks= self.__calcer.breaks, 
                                                y_vals= self.__calcer.y_vals,
                                                plan_prj= np.array(self.data.plan_prj_0185), 
                                                sdv= np.array(self.data.plan_delta), 
                                                f_urov= self.all_levels())
        ev_table.index.name = 'step'

        new_plan = TrackLevelProjectModel(
                        track_split=track_split, 
                        data=ev_table, 
                        start_picket=self.start_picket, 
                        picket_direction=self.picket_direction)
        
        for src_elem, dst_elem in zip(self.elements(), new_plan.elements()):
            dst_elem.new_level = src_elem.new_level

        return new_plan
    
    
        