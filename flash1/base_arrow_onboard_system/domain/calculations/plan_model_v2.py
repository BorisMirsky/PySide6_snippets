import pandas as pd
import numpy as np
from typing import List
from typing_extensions import Self
from enum import Enum
from cantok import AbstractToken, SimpleToken

from .plan_funcs import new_track_calculation
from .helpers import normative_slope_by_velocity, plan_column_names

class TrackSectionGeometry(Enum):
    Straight = 'прямая'
    Curve = 'кривая'

class TrackElementGeometry(Enum):
    Straight = 'прямая'
    Curve = 'круговая кривая'
    Transition = 'переходная кривая'


class TrackElement:
    """
    """  
    def __init__(self, row: pd.Series):
        self.__parent: TrackSection = None
        self.__geom = TrackElementGeometry(row.geom) 
        self.__start = row.start
        self.__end = row.end
        self.__radius = row.radius
        self.__level = None
        self.__a_nepog = None
        self.__level_delta = None

        self.__new_start = None
        self.__new_end = None
        
        self.__new_radius = np.nan
        self.__new_length = np.nan
        self.__modified = False
    
    def __str__(self):
        return f'TrackElement(geometry={self.name}, start={self.start}, end={self.end}, radius={self.radius_fact})'
    def __repr__(self): 
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            'geom': self.geometry.value, 
            'start': self.start, 
            'end': self.end, 
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
        return self.__parent.parent
    @property
    def name(self) -> str:
        return self.__geom.name
    @property
    def modified(self) -> bool:
        return self.__modified
    
    @property
    def length(self) -> float:
        return self.__end - self.__start
    
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
        return self.get_level_prj()
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
        return int(np.ceil(self.__start/10))
    @property
    def end_index(self) -> int:
        return int(np.floor(self.__end/10))
    
    @property
    def new_start(self) -> float:
        return self.__new_start
    @property
    def new_end(self) -> float:
        return self.__new_end
    
    def start_point(self) -> float:
        # Если положение начала изменилось, то возвращает self.__new_start, иначе self.__start
        return self.new_start if self.new_start is not None else self.start 
    def end_point(self) -> float:
        # Если положение конца изменилось, то возвращает self.__new_end, иначе self.__end
        return self.new_end if self.new_end is not None else self.end 

    @property
    def data(self) -> pd.DataFrame:
        return self.track.data[self.start_index:self.end_index+1]
    
    def get_radius_prj(self) -> float:
        return 50000/self.data.plan_prj.mean() if self.__geom != TrackElementGeometry.Transition else None
    
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


    def shift_new_start(self, delta: float):
        # Сдивагает начало текущего и конец предыдущего элемента на значение delta.
        self.__new_start = self.start + delta        
        # Если вернули прежнее значение, то новое значение сбрасываем в None
        if self.__new_start == self.start:
            self.__new_start = None

    def shift_new_end(self, delta: float):
        # Сдивагает конец текущего и начало следующего элемента на значение delta.        
        self.__new_end = self.end + delta        
        # Если вернули прежнее значение, то новое значение сбрасываем в None
        if self.__new_end == self.end:
            self.__new_end = None

    def shift_start(self, delta: float):
        # Сдивагает начало текущего и конец предыдущего элемента на значение delta.
        self.__modified = True
        self.shift_new_start(delta)
        self.new_length = self.calc_new_length()

        if self.prev_element() is not None:
            self.prev_element().shift_new_end(delta)

    def shift_end(self, delta: float):
        # Сдивагает конец текущего и начало следующего элемента на значение delta.
        self.__modified = True        
        self.shift_new_end(delta)
        self.new_length = self.calc_new_length()

        if self.next_element() is not None:
            self.next_element().shift_new_start(delta)

    def shift(self, delta: float):
        # Сдивагает элемент (начало и конец) на значение delta.
        self.shift_start(delta)
        self.shift_end(delta)

    def next_element(self) -> Self | None:
        elements = self.track.get_elements()
        idx = elements.index(self) + 1
        return elements[idx] if idx < len(elements) else None
    
    def prev_element(self) -> Self | None:
        elements = self.track.get_elements()
        idx = elements.index(self) - 1
        return None if idx < 0 else elements[idx]
 

class TrackSection:
    # def __init__(self, element: TrackElement = None):
    #     self.parent: TrackPlanProjectModel = None
    #     self.__elements: List[TrackElement] = []
    #     self.__geom = TrackSectionGeometry.Straight if element.geometry == TrackElementGeometry.Straight else TrackSectionGeometry.Curve
    #     self.add_element(element)

    # def __init__(self, track_row: pd.Series):
    #     self.parent: TrackPlanProjectModel = None
    #     self.__geom = TrackSectionGeometry(track_row.geom) 
    #     self.__start: float = track_row.start
    #     self.__end: float = track_row.end
    #     self.__k0: float = track_row.k0
    #     self.__k1: float = track_row.k1
    #     self.__elements: List[TrackElement] = []

    def __init__(self, geometry: TrackSectionGeometry, elements: pd.DataFrame):
        self.parent: TrackPlanProjectModel = None
        self.__elements: List[TrackElement] = []
        self.__geom = geometry
        self.__data = None

        for idx, row in elements.iterrows():
            self.add_element(TrackElement(row))

    def __str__(self):
        return f'TrackSection(geometry={self.name}, start={self.start}, end={self.end}, length={self.length})'
    def __repr__(self): 
        return self.__str__()
    
    def element_split(self) -> pd.DataFrame:
        elems = [{'geom': e.geometry.value, 
                  'start': e.start, 
                  'end': e.end, 
                  'length': e.length} for e in self.elements]
        return pd.DataFrame(elems)
    
    @property
    def name(self):
        return self.geometry.value
    
    @property
    def track(self):
        return self.parent
    
    # @property
    # def start(self) -> float:
    #     return self.__start
    # @property
    # def end(self) -> float:
    #     return self.__end

    @property
    def start(self):
        return self.__elements[0].start
    @property
    def end(self):
        return self.__elements[-1].end
    @property
    def start_index(self) -> int:
        return self.__elements[0].start_index
    @property
    def end_index(self) -> int:
        return self.__elements[-1].end_index
    
    # @property
    # def start_index(self) -> int:
    #     return int(np.ceil(self.__start/10))
    # @property
    # def end_index(self) -> int:
    #     return int(np.floor(self.__end/10))
    
    @property
    def data(self) -> pd.DataFrame:
        if self.__data is not None:
            return self.__data
        return self.track.data[self.start_index:self.end_index+1]
    @data.setter
    def data(self, value: pd.DataFrame):
        self.__data = value

    @property
    def length(self):
        return self.end - self.start
    
    @property
    def geometry(self) -> TrackSectionGeometry:
        return self.__geom
    
    @property
    def elements(self) -> List[TrackElement]:
        return self.__elements
    
    # @property
    # def needs_recalc(self) -> bool:
    #     # Возвращает истину если необходимо пересчитать участок пути 
    #     # (есть модифицированые элемнты)
    #     modified_elems = [e for e in self.elements if e.modified]

    #     # TODO: если нет модифицированных элементов, то проверять есть ли изменения
    #     # начало или конца участка
    #     # pass
    #     return len(modified_elems) > 0
    def modified(self) -> bool:
        # Возвращает истину если есть хотя один измененный элемент.
        for e in self.elements:
            if e.modified:
                return True
        return False
    
    def add_element(self, elem: TrackElement):
        elem.parent = self
        self.__elements.append(elem)

    def element_types(self) -> List[int]:
        # Разбиение участка: 0 - круговая кривая или прямая, 1 - переходная кривая.
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.elements]

    def new_lengths(self) -> List[float]:
        # Пользовательские ограничения на длины переходных кривых и круговых кривых. 
        # Np.nan - без ограничения
        # Возвращает список длин в десятиметровках.
        return np.array([elem.new_length for elem in self.elements])/10
        
    def new_radiuses(self) -> List:
        # Пользовательские ограничения на радиус кривых. Np.nan - без ограничения. 
        # Имеет смысл задавать только f[i], где u[i] = 0, т.к. на переходной кривой радиус не может быть константой
        return [elem.new_radius for elem in self.elements]

    def new_arrows(self) -> List[float]:
        # Список стрел, вычисляемых из заданных радиусов.
        return [(np.nan if r is np.nan or r is None else 50000/r) for r in self.new_radiuses()]

    def start_x_points(self) -> List[float]:
        # Возвращвет список точек излома в десятиметровках относительно начала кривой.
        points = [(e.start_point() - self.start)/10 for e in self.elements]
        points = np.array(points[1:])
        return np.ceil(points).astype(int)
    
    def ubound(self):
        return np.inf*np.ones((len(self.data), ))
    def lbound(self):
        return -np.inf*np.ones((len(self.data), ))
    
    def next_section(self):
        next_idx = self.parent.sections.index(self) + 1
        return self.parent.sections[next_idx] if next_idx < len(self.parent.sections) else None
    def prev_section(self):
        prev_idx = self.parent.sections.index(self) - 1
        return None if prev_idx < 0 else self.parent.sections[prev_idx]


class TrackPlanProjectModel:
    """
    Represents the project plan for the track.
    Consists of track elements of 3 types: straights, transitions and curves. 
    """
    def __init__(self, split_by_section: pd.DataFrame, split_by_element: pd.DataFrame, data: pd.DataFrame, step: float = 10):
        self.__split_by_section = split_by_section
        self.__data = data
        self.__step = step
        self.__sections: List[TrackSection] = []
        
        # start_elem_idx = 0 
        # for section_idx, row in split_by_section.iterrows():
        #     section = TrackSection(row)
        #     self.add_section(section)
        #     for elem_idx in range(start_elem_idx, len(split_by_element)):
        #         # print(elem_idx)
        #         start_elem_idx = elem_idx
        #         elem = TrackElement(split_by_element.iloc[elem_idx])
        #         if elem.end - section.end > 0.1:
        #             break
        #         section.add_element(elem)
        for section_idx, section_row in split_by_section.iterrows():
            section_elems = split_by_element.loc[
                (split_by_element.start >= section_row.start) & 
                (split_by_element.end <= section_row.end)]
            section = TrackSection(
                        geometry=TrackSectionGeometry(section_row.geom), 
                        elements=section_elems)
            self.add_section(section)

        #Необходимость выполнения условия равенства суммы натурных и проектных стрел (по умолчанию ставим True, т.к. это условие метода эвольвент)
        self.__sum_equality_condition = True
        
        #Начальные точки излома. Могут быть заданы пользователем, или предложены автоматически с помощью функции "get_start_x_points"
        #Если find_start_x_points = False, то пользователь сам задает начальное приближение для точек излома
        self.__find_start_x_points = False

        #Если optimize_x_point = False, то ищем решение для заданных пользователем точек излома start_x_points, не запускаем оптимизацию
        self.__optimize_x_point = False
        
        #Тип расчета уровня (если -1, считаем как среднее значение, иначе приравниваем к заданному значению)
        self.__curve_urov = -1
        
        #Параметры оптимизации
        #Максимальное количество итераций 
        self.__number_of_nodes_to_expanse = 1000
        #Параметры оптимизационного алгоритма для поиска точек излома start_x_points
        self.__C = 0.5
        self.__D = 10000
        self.__T = 10
        self.__W = 0.8
        self.__epsilon = 1
        #Ограничение на максимальное время расчета в секундах
        self.__stop_by_time = 600
        #Завершаем оптимизацю по нахождению приемлимого решения (stop_by_found_solution = False, то будет искать решение дальше, пытаясь еще уменьшить сдвижки)
        self.__stop_by_found_solution = True
        #Максимальное число итераций в промежуточном алгоритме, есть смысл уменьшать, если одна итерация очень долго считается (такое случается, если неудачно выбраны start_x_points) 
        self.__maxiter = 1000
        #Вывод промежуточного результата оптимизации через число итераций = verbose, если verbose = False, то не печатаем промежуточные результаты
        self.__verbose = 10
        #Оптимизационный метод промежуточного алгоритма
        self.__opt_method = 'COBYLA'
    
    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    @property
    def step(self) -> pd.DataFrame:
        return self.__step
    # @property
    # def track_split(self) -> pd.DataFrame:
    #     return self.__track_split
    @property
    def sections(self) -> List[TrackSection]:
        return self.__sections    
    @property
    def last_section(self) -> TrackSection:
        return None if len(self.__sections) == 0 else self.__sections[-1]
    
    @property
    def optimize_x_point(self):
        self.__optimize_x_point
    @optimize_x_point.setter
    def optimize_x_point(self, value):
        self.__optimize_x_point = value

        
    def add_section(self, section: TrackSection):
        section.parent = self
        self.__sections.append(section)
        
    def get_elements(self) -> List[TrackElement]:
        all_elements = []
        for section in self.__sections:
            all_elements += section.elements
        return all_elements

    def elements(self) -> List[TrackElement]:
        return self.get_elements()
    
    def element_types(self) -> List[int]:
        # Разбиение участка: 0 - круговая кривая/прямая, 1 - переходная кривая.
        return [(1 if elem.geometry == TrackElementGeometry.Transition else 0) for elem in self.get_elements()]

    def new_lengths(self) -> List[float]:
        # Пользовательские ограничения на длины переходных кривых и круговых кривых. 
        # Np.nan - без ограничения
        # Возвращает список длин в десятиметровках.
        return np.array([elem.new_length for elem in self.elements()])/10
        
    def new_radiuses(self) -> List:
        # Пользовательские ограничения на радиус кривых. Np.nan - без ограничения. 
        # Имеет смысл задавать только f[i], где u[i] = 0, т.к. на переходной кривой радиус не может быть константой
        return [elem.new_radius for elem in self.elements()]

    def new_arrows(self) -> List[float]:
        # Список стрел, вычисляемых из заданных радиусов.
        return [(np.nan if r is np.nan or r is None else 50000/r) for r in self.new_radiuses()]

    def start_x_points(self) -> List[float]:
        # Возвращвет список точек излома.
        points = [e.start_point()/10 for e in self.elements()]
        points = np.array(points[1:])
        return np.ceil(points).astype(int)
        
    def to_dataframe(self) -> pd.DataFrame:
        elems = [e.to_dict() for e in self.elements()]
        return pd.DataFrame(elems).round(3)
    def summary(self) -> pd.DataFrame:
        return self.to_dataframe()
    def ubound(self):
        return np.inf*np.ones((len(self.data), ))
    def lbound(self):
        return -np.inf*np.ones((len(self.data), ))
        
    def calc_section(self, section: TrackSection) -> TrackSection:
        optimize_x_point = False
        if self.__optimize_x_point:
            optimize_x_point = [self.__number_of_nodes_to_expanse, self.__C, self.__D, self.__T, self.__W, self.__epsilon, self.__stop_by_time, self.__stop_by_found_solution, self.__maxiter, self.__verbose, SimpleToken()]
        
        # Пересчитываем участок с новыми параметрами
        EV_table, alc_plan, alc_level, x_start_new, x_end = new_track_calculation(
            np.array(section.data.plan_fact), 
            np.array(section.data.vozv_fact), 
            np.array(section.data.V_max), 
            self.__curve_urov, 
            section.element_types(), 
            section.new_arrows(), 
            section.new_lengths(), 
            section.start_x_points(), 
            self.__sum_equality_condition, 
            section.ubound(), 
            section.lbound(), 
            self.__opt_method, 
            optimize_x_point)
        EV_table.columns = plan_column_names()
        
        # Строим новое разбиение элементов (могли изменится положения поворотных точек)
        alc_plan[1] = alc_plan[1] + section.start
        alc_level[1] = alc_level[1] + section.start
        section_split_by_element = build_plan_summary(
                                        base_plan= EV_table, 
                                        alc_plan= alc_plan, 
                                        alc_level= alc_level, 
                                        plan_length= x_end*10+section.start)
        
        new_section = TrackSection(geometry=section.geometry, elements=section_split_by_element)
        new_section.data = EV_table
        return new_section
    
    def calc_curve_section(self, section: TrackSection) -> TrackSection:
        optimize_x_point = False
        if self.__optimize_x_point:
            optimize_x_point = [self.__number_of_nodes_to_expanse, self.__C, self.__D, self.__T, self.__W, self.__epsilon, self.__stop_by_time, self.__stop_by_found_solution, self.__maxiter, self.__verbose, SimpleToken()]
        
        # Пересчитываем участок с новыми параметрами
        EV_table, alc_plan, alc_level, x_start_new, x_end = new_track_calculation(
            np.array(section.data.plan_fact), 
            np.array(section.data.vozv_fact), 
            np.array(section.data.V_max), 
            self.__curve_urov, 
            section.element_types(), 
            section.new_arrows(), 
            section.new_lengths(), 
            section.start_x_points(), 
            self.__sum_equality_condition, 
            section.ubound(), 
            section.lbound(), 
            self.__opt_method, 
            optimize_x_point)
        EV_table.columns = plan_column_names()
        
        # Строим новое разбиение элементов (могли изменится положения поворотных точек)
        alc_plan[1] = alc_plan[1] + section.start
        alc_level[1] = alc_level[1] + section.start

        return EV_table, alc_plan, alc_level, x_start_new, x_end
    
    def split_by_section(self) -> pd.DataFrame:
        return self.__split_by_section
    def split_by_element(self) -> pd.DataFrame:
        return self.to_dataframe()[['geom', 'start', 'end', 'length']]
    
    def calc_new_track(self) -> Self:
        # Находим измененный участок пути и пересчитываем его
        modified_section = None
        for section in self.sections:
            if section.modified:
                modified_section = section
                break
        if modified_section is None:
            return self
        
        # Находим соседей и коректируем их примыкающие границы
        prev_section = modified_section.prev_section()
        next_section = modified_section.next_section()

        # Формируем разбиение по участкам пути

        # Формируем разбиение по элементам пути

        

        # Пересчитываем участки которые были подвергнуты изменениям.
        for section in self.sections:
            if section.needs_recalc:
                if section.geometry == TrackSectionGeometry.Straight:
                    self.calc_straight_section(section)
                if section.geometry == TrackSectionGeometry.Curve:
                    self.calc_curve_section(section)

        return TrackPlanProjectModel(
                    split_by_section=self.split_by_section(), 
                    split_by_element=self.split_by_element(), 
                    data=self.data)
    

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

