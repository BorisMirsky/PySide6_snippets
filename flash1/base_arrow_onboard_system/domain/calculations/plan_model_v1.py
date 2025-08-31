from enum import Enum
import pandas as pd
import numpy as np
from typing import List
from scipy import optimize
from scipy.optimize import fsolve, Bounds, LinearConstraint, NonlinearConstraint
# from gen_solution import generate_solution, generate_constraints

from .helpers import plan_column_names
from .track_funcs import calculate_plan_with_r_and_l, calculate_plan_with_l_points

class TrackCurveGeometry(Enum):
    Straight = 0
    Curve = 1

class CurveElementGeometry(Enum):
    Straight = 'straight'
    Curve = 'curve'
    Transition = 'transition'

class CurveElement:
    """
        start: float
        end: float
        geometry: CurveElementGeometry    
        length: float = None
        radius: float = None
        level: float  = None
    """
    
    def __init__(self, row: pd.Series):
        self.parent = None
        self.geometry = CurveElementGeometry(row.geom) 
        self.start = row.start 
        self.end = row.end
        self.level = row.level
        self.radius = row.radius
        self.length = row.length
    
    def __str__(self):
        return f'CurveElement(geometry={self.name}, start={self.start}, end={self.end}, radius={self.radius})'
    def __repr__(self): 
        return self.__str__()

    def to_dict(self) -> dict:
        return {'geom': self.geometry.value, 'start': self.start, 'end': self.end, 'length': self.length, 'radius': self.radius, 'level': self.level}
    
    @property
    def track(self):
        return self.parent.parent
    
    @property
    def name(self):
        match self.geometry:
            case CurveElementGeometry.Straight:
                return 'прямая'
            case CurveElementGeometry.Curve:
                return 'круговая кривая'
            case CurveElementGeometry.Transition:
                return 'переходная кривая'
            case _:
                raise Exception('Undefined curve type')
            
    def set_start(self, value: float):
        # изменяем начало элемента и вычисляем новую длину
        self.start = value
        self.length = self.end - self.start

    def set_end(self, value: float):
        # изменяем конец элемента и вычисляем новую длину
        self.end = value
        self.length = self.end - self.start

    def shift_start(self, delta: float):
        # Сдивагает начало текущего и конец предыдущего элемента на значение delta.
        self.set_start(self.start + delta)
        self.prev_element().set_end(self.start)

    def shift_end(self, delta: float):
        # Сдивагает конец текущего и начало следующего элемента на значение delta.
        self.set_end(self.end + delta)
        self.next_element().set_start(self.end)

    def shift(self, delta: float):
        # Сдивагает элемент (начало и конец) на значение delta.
        self.shift_start(delta)
        self.shift_end(delta)

    def next_element(self):
        elements = self.track.get_elements()
        idx = elements.index(self) + 1
        return elements[idx] if idx < len(elements) else None
    
    def prev_element(self):
        elements = self.track.get_elements()
        idx = elements.index(self) - 1
        return None if idx < 0 else elements[idx]
    

class TrackCurve:
    def __init__(self, element: CurveElement):
        self.parent = None
        self.__geom = TrackCurveGeometry.Straight if element.geometry == CurveElementGeometry.Straight else TrackCurveGeometry.Curve
        self.__elements: List[CurveElement] = []
        self.add_element(element)

    def __str__(self):
        return f'TrackCurve(geometry={self.name}, start={self.start}, end={self.end}, length={self.length})'
    def __repr__(self): 
        return self.__str__()
    
    @property
    def name(self):
        match self.geometry:
            case TrackCurveGeometry.Straight:
                return 'прямая'
            case TrackCurveGeometry.Curve:
                return 'кривая'
            case _:
                raise Exception('Undefined curve type')
    @property
    def start(self):
        return self.__elements[0].start
    @property
    def end(self):
        return self.__elements[-1].end
    
    @property
    def length(self):
        return self.end - self.start
    
    @property
    def geometry(self) -> TrackCurveGeometry:
        return self.__geom
    
    @property
    def elements(self):
        return self.__elements
    
    def get_plan_column_names(self) -> List[str]:
        return plan_column_names()[:32]

    def get_elements(self, geometry: CurveElementGeometry):        
        return [e for e in self.__elements if e.geometry == geometry]
    
    def get_element_lengths(self, geometry: CurveElementGeometry):
        return [e.length for e in self.get_elements(geometry)]
    
    def get_points(self) -> np.ndarray[float]:
        return np.array([e.start for e in self.elements] + [self.end])
    
    def get_element_radiuses(self):
        return [e.radius for e in self.get_elements(CurveElementGeometry.Curve)]
    
    def change_radius(self, plan: pd.DataFrame):
        next_curve = self.next_curve()
        if next_curve.geometry != TrackCurveGeometry.Straight:
            raise Exception('Need a straight element after the curve to perform correct calcs.')
            
        start_idx = int(np.ceil(self.start/10))
        #end_idx = int(np.floor(self.end/10))
        end_idx = int(np.floor(next_curve.end/10))
        #print(f'start_idx={start_idx}, end_idx={end_idx}')

        msv = plan.Fact.iloc[start_idx:end_idx]
        urov = plan.Vozv.iloc[start_idx:end_idx]
        vmax = plan.V_max.iloc[start_idx:end_idx]

        EV_array, alc_plan, alc_level = calculate_plan_with_r_and_l(
            msv=np.array(msv), 
            urov=np.array(urov), 
            vmax=np.array(vmax), 
            params_l=self.get_element_lengths(CurveElementGeometry.Transition),
            params_r=self.get_element_radiuses(),
            params_k=[plan.Plan_corr.iloc[start_idx], plan.Plan_corr.iloc[end_idx-1]],
            curve_urov=-1,
            straight_urov=-1, 
            mx_evals=50)
        EV_table = pd.DataFrame(columns=self.get_plan_column_names(), data=EV_array)
        plan.iloc[start_idx:end_idx] = EV_table        
        ##
        ## alc_plan и alc_level начинаются с нуля поэтому прибавляем начало кривой:
        ##            0	         1	                           2	       3	                                   4	    5
        ## 0	Место [м]	       0.0	Положение в плане: геометрия	линейный    Положение в плане: длина[м]/радиус[м]	70.55
        ## 0	Место [м]	     70.55	Положение в плане: геометрия	радиус	    Положение в плане: длина[м]/радиус[м]	-375.0
        ## 0	Место [м]	172.502272	Положение в плане: геометрия	линейный	Положение в плане: длина[м]/радиус[м]	120.02
        ## 0	Место [м]	292.522272	Положение в плане: геометрия	радиус	    Положение в плане: длина[м]/радиус[м]	10002.823356
        ##
        alc_plan[1] = alc_plan[1] + self.start
        alc_level[1] = alc_level[1] + self.start
        curve_summary = build_plan_project_summary(alc_plan=alc_plan, alc_level=alc_level)
        self.__update(curve_summary)
        
        # сдвигаем начало следующей кривой в конец текущей
        self.next_curve().set_start(self.end)

        return alc_plan, alc_level
    
    def next_curve(self):
        next_idx = self.parent.curves.index(self) + 1
        return self.parent.curves[next_idx] if next_idx < len(self.parent.curves) else None
    def prev_curve(self):
        prev_idx = self.parent.curves.index(self) - 1
        return None if prev_idx < 0 else self.parent.curves[prev_idx]
    
    def set_start(self, new_start: float):
        # Изменяет начало кривой, т.е. начало первого элемента.
        self.elements[0].set_start(new_start)

    def add_element(self, elem: CurveElement):
        elem.parent = self
        self.__elements.append(elem)

    def __update(self, curve_data: pd.DataFrame):
        # очищаем список элементов и формируем его заново
        self.__elements = []    
        for idx, row in curve_data.iterrows():
            self.add_element(CurveElement(row))
    
    def change_lengths(self, plan: pd.DataFrame, mx_evals: int = 100):
        next_curve = self.next_curve()
        if next_curve.geometry != TrackCurveGeometry.Straight:
            raise Exception('Need a straight element the curve after to perform correct calcs.')
            
        start_idx = int(np.ceil(self.start/10))
        end_idx = int(np.floor(next_curve.end/10))        
        msv = plan.Fact.iloc[start_idx:end_idx]
        urov = plan.Vozv.iloc[start_idx:end_idx]
        vmax = plan.V_max.iloc[start_idx:end_idx]

        EV_array, alc_plan, alc_level = calculate_plan_with_l_points(
            msv=np.array(msv), 
            urov=np.array(urov), 
            vmax=np.array(vmax), 
            l_points=(self.get_points() - self.start),
            params_k=[plan.Plan_corr.iloc[start_idx], plan.Plan_corr.iloc[end_idx-1]],
            curve_urov=-1,
            straight_urov=-1, 
            mx_evals=mx_evals)
        EV_table = pd.DataFrame(columns=self.get_plan_column_names(), data=EV_array)
        plan.iloc[start_idx:end_idx] = EV_table        
        ##
        ## alc_plan и alc_level начинаются с нуля поэтому прибавляем начало кривой:
        ##            0	         1	                           2	       3	                                   4	    5
        ## 0	Место [м]	       0.0	Положение в плане: геометрия	линейный    Положение в плане: длина[м]/радиус[м]	70.55
        ## 0	Место [м]	     70.55	Положение в плане: геометрия	радиус	    Положение в плане: длина[м]/радиус[м]	-375.0
        ## 0	Место [м]	172.502272	Положение в плане: геометрия	линейный	Положение в плане: длина[м]/радиус[м]	120.02
        ## 0	Место [м]	292.522272	Положение в плане: геометрия	радиус	    Положение в плане: длина[м]/радиус[м]	10002.823356
        ##
        alc_plan[1] = alc_plan[1] + self.start
        alc_level[1] = alc_level[1] + self.start
        curve_summary = build_plan_project_summary(alc_plan=alc_plan, alc_level=alc_level)
        self.__update(curve_summary)
        
        # сдвигаем начало следующей кривой в конец текущей
        self.next_curve().set_start(self.end)

        return alc_plan, alc_level
    
class TrackPlanProjectModel:
    """
    Represents a project for the track in the plan plane.
    Consists of curves of two types: straights and curves. 
    """
    def __init__(self, summary: pd.DataFrame):
        self.__curves: List[TrackCurve] = []
                
        for idx, row in summary.iterrows():
            self.add_element(CurveElement(row))
    
    @property
    def curves(self) -> List[TrackCurve]:
        return self.__curves    
    @property
    def last_curve(self) -> TrackCurve:
        return None if len(self.__curves) == 0 else self.__curves[-1]
    
    def add_element(self, elem: CurveElement):
        # if track is empty
        if self.last_curve is None:
            self.add_curve(TrackCurve(elem))
            return
        # to track curve of straight type can be added only straight curve element  
        if self.last_curve.geometry == TrackCurveGeometry.Straight:
            if elem.geometry == CurveElementGeometry.Straight:
                self.last_curve.add_element(elem)
                return
        else:
            if elem.geometry != CurveElementGeometry.Straight:
                self.last_curve.add_element(elem)
                return
            
        # create a new track curve from element
        self.add_curve(TrackCurve(elem))
        
    def add_curve(self, curve: TrackCurve):
        curve.parent = self
        self.__curves.append(curve)
        
    def get_elements(self):
        all_elements = []
        for curve in self.__curves:
            all_elements += curve.elements
        return all_elements

    def to_dataframe(self) -> pd.DataFrame:
        elems = [e.to_dict() for e in self.get_elements()]
        return pd.DataFrame(elems)

def build_plan_project_summary(alc_plan: pd.DataFrame, alc_level: pd.DataFrame, plan_length: float = None) -> pd.DataFrame:
    """
    Строит ведомость кривых на основе 2-х датафреймов: ALC-плана и ALC-уровня.
    Если длина плана (в метрах) не задана, то последний элемент ALC не будет включен.
    """
    def get_curve_type(row) -> str:
        if row.geom == 'радиус':
            return 'straight' if abs(row.value) > 4000 else 'curve'
        if row.geom == 'линейный':
            return 'transition'
        raise Exception('Undefined curve type')

    # ALC plan
    alc_plan_ = pd.DataFrame(columns=['position', 'geom', 'value'])
    alc_plan_.position = alc_plan[alc_plan.columns[1]].astype('float')
    alc_plan_.geom = alc_plan[alc_plan.columns[3]]
    alc_plan_.value = alc_plan[alc_plan.columns[5]].astype('float')
    alc_plan_ = alc_plan_.round(2)
    alc_plan_.reset_index(drop=True, inplace=True)
    if plan_length is not None:
        alc_plan_.loc[len(alc_plan_)] = [plan_length, None, None]
    # ALC level
    alc_urov = pd.DataFrame(columns=['position', 'geom', 'value'])
    alc_urov.position = alc_level[alc_level.columns[1]].astype('float')
    alc_urov.geom = alc_level[alc_level.columns[3]]
    alc_urov.value = alc_level[alc_level.columns[5]].astype('float')
    alc_urov = alc_urov.round(2)
    alc_urov.reset_index(drop=True, inplace=True)
    if plan_length is not None:
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
    return summary

def build_plan_project_model(alc_plan: pd.DataFrame, alc_level: pd.DataFrame, plan_length: float = None) -> TrackPlanProjectModel:
    """
    Строит модель плана пути на основе ведомости кривых.
    """
    summary = build_plan_project_summary(plan_length=plan_length, alc_plan=alc_plan, alc_level=alc_level)
    return TrackPlanProjectModel(summary)



#Нахождение значения заданной кусочно-линейной функции в произвольной точке
def curve_pattern_new(x, x_vector, k_vector, b, x_start, x_end):
    b_vector=np.zeros((len(k_vector), ))
    b_vector[0] = b - k_vector[0]*x_start
    if x < x_vector[0]:
        return k_vector[0]*x + b_vector[0]

    for i in range(1, len(x_vector)):
        b_vector[i] = x_vector[i-1]*(k_vector[i-1] - k_vector[i]) + b_vector[i-1]
        if (x >= x_vector[i-1]) & (x < x_vector[i]):
            return k_vector[i]*x + b_vector[i]
        
    b_vector[-1] = x_vector[-1]*(k_vector[-2] - k_vector[-1]) + b_vector[-2]
    
    if x >= x_vector[-1]:
        return k_vector[-1]*x + b_vector[-1]


# Поиск решения, удовлетворяющего условиям метода эвольвент с заданной точностью и пользовательским ограничениям на сдвижки
#Вход
#msv - Исходные данные по кривой
# u - последовательность прямых и кривых 
# x_points - Значения вектора xi точек перелома кусочно-линейной функции
# optimization_start_point - начальная точка оптимизации
# sdx - (-1; 0] - добавка к начальной точке 0, может оптимизироваться
# edx - [0; +1) - добавка к конечной точке len(msv) - 1, может оптимизироваться

def build_project_plan_track_new(msv, u, x_points, f_vector, l_vector, find_b, sum_equality_condition, ubound, lbound, opt_method, lb_constr, ub_constr, tol=1e-2, maxiter=100, print_results = False):  
    evl_list = list()
    N = len(msv)
    dim_k_to_optimize = np.sum(u) - len(f_vector) + np.sum(np.isnan(f_vector))
    dim_x_to_optimize = len(x_points) + 2 - len(l_vector) + np.sum(np.isnan(l_vector))
    
    if dim_k_to_optimize > 0:
        dim_k_to_optimize = dim_k_to_optimize - int(sum_equality_condition)
    else:
        dim_x_to_optimize = dim_x_to_optimize - int(sum_equality_condition)
    
    #print(len(u), len(x_points), len(f_vector), len(l_vector), len(find_b))
    print("dim_k_to_optimize:", dim_k_to_optimize, "dim_x_to_optimize:", dim_x_to_optimize)
    
    x0_point = -0.5*np.ones((dim_x_to_optimize + dim_k_to_optimize, ))    
    
    if lb_constr.shape[0] <= x0_point.shape[0]:
        x0_point[dim_k_to_optimize : ] = (lb_constr + ub_constr)/2
    #print(len(x0_point))
    
    def calculate_project(xs_vector):
        #print("len(xs_vector)", len(xs_vector))
        s_vector = xs_vector[dim_k_to_optimize: ]
        #print("len(s_vector)", len(s_vector))
        #x_end = N - 1 
        x_end = N - 1 - s_vector[-1]         
        
        
        b = find_b[0](*xs_vector)  
        #Создаем массив коэффициентов k  
        k_vals = np.nan*np.zeros((len(u), ))
        for i in range(len(u)):
            if u[i] == 0:
                k_vals[i] = 0 
        
        ct1 = 1
        for j in range(len(k_vals)): 
            if np.isnan(k_vals[j]):
                if ct1 > len(find_b) - 1:
                    break            
                k_vals[j] = find_b[ct1](*xs_vector) 
                ct1 += 1
        #print("k_vals_ct1", ct1)   
        #print("k_vals", k_vals)  
        
        ct2 = 0
        for j in range(len(k_vals)): 
            if np.isnan(k_vals[j]):
                k_vals[j] = xs_vector[ct2]  
                ct2 += 1
        #print("k_vals_ct2", ct2)
        #print("k_vals", k_vals)
        
        #Создаем массив точек x            
        x_vals = np.nan*np.zeros((len(u), ))
        x_vals[0] = s_vector[0]
        for j in range(1, len(x_vals)): 
            if np.isnan(l_vector[j-1]) == False:
                x_vals[j] = 10000 
            else:
                break
       
        for i in range(len(x_vals)-1, j-1, -1): 
            if np.isnan(l_vector[i]) == False:
                x_vals[i] = 10000   
                
        #print("x_vals", x_vals)
        
        for j in range(1, len(x_vals)): 
            if np.isnan(x_vals[j]):
                if ct1 > len(find_b) - 1:
                    break            
                x_vals[j] = find_b[ct1](*xs_vector) 
                ct1 += 1                
        #print("x_vals_ct1", ct1)
        #print("x_vals", x_vals)     
        
        ct2 = 1
        for j in range(1, len(x_vals)): 
            if np.isnan(x_vals[j]):
                x_vals[j] = x_points[j-1] + s_vector[ct2]
                ct2 += 1
        #print("x_vals_ct2", ct2)
        #print("x_vals", x_vals)
        
        for j in range(1, len(x_vals)): 
            if np.isnan(l_vector[j-1]) == False:
                x_vals[j] = x_vals[j-1] + l_vector[j-1]  
            else:
                break

        for i in range(len(x_vals)-1, j-1, -1): 
            if np.isnan(l_vector[i]) == False:
                if i == len(x_vals)-1:
                    x_vals[-1] = N - 1 - xs_vector[-1] - l_vector[-1]                 
                else:
                    x_vals[i] = x_vals[i+1] - l_vector[i]                  
        #print("x_vals", x_vals)  
        
        if print_results == True:
            print("xs_vector", xs_vector)
            print("x_vals", x_vals)
            print("k_vals", k_vals)        
            # print("x_start", x_start)
            print("x_end", x_end)
        return x_vals, k_vals, b, x_end
        
    def function_to_optimize(xs_vector):

        x_vals, k_vals, b, x_end = calculate_project(xs_vector)
        if print_results == True:
            print(x_vals[1:], k_vals, b, x_vals[0], x_end)
        #Условие минимизации сдвижек 
        evm = 0
        for j in range(N):
            evl=0
            for i in range(j):
                x_proekt = curve_pattern_new(i, np.copy(x_vals[1:]), np.copy(k_vals), b, x_vals[0], x_end)
                diff_strel = msv[i] - x_proekt
                val = (j-i)*diff_strel
                evl = evl + val
            if j == N-1:
                if print_results == True:
                    print('Evolvent_n:', evl)
                evl_list.append(evl)
            evm = evm + evl**2   
            
        #print(x_vector, k_vector, k_vals, b, x_start, x_end, evm)
        return evm  
    
    A=np.zeros((dim_x_to_optimize + dim_k_to_optimize, dim_x_to_optimize + dim_k_to_optimize))    
    for i in range(dim_k_to_optimize, dim_x_to_optimize + dim_k_to_optimize):
        A[i,i]=1
    print("matrix of linear constraints", A)
    
    l_c = -1 + 10**(-7)
    u_c = 0
    
    if lb_constr.shape[0] <= x0_point.shape[0]:
        l_c = np.zeros((dim_x_to_optimize + dim_k_to_optimize, )) - np.inf
        u_c = np.zeros((dim_x_to_optimize + dim_k_to_optimize, )) + np.inf
        l_c[dim_k_to_optimize : ] = lb_constr
        u_c[dim_k_to_optimize : ] = ub_constr
    
    linear_constraint = LinearConstraint(A, l_c, u_c)      
    #print(A, l_c, u_c)      
    
    def cons_f(xs_vector):
        x_vals, k_vals, b, x_end = calculate_project(xs_vector)                     
        cons_l=list()
        for j in range(N):
            evl=0
            for i in range(j):
                x_proekt = curve_pattern_new(i, np.copy(x_vals[1:]), np.copy(k_vals), b, x_vals[0], x_end)
                diff_strel = msv[i] - x_proekt
                val = (j-i)*diff_strel
                evl = evl + val
            cons_l.append(ubound[j]/2 - evl)
            cons_l.append(evl - lbound[j]/2)   
        return np.array(cons_l)
    
    non_linear_constraint_0 = {'type': 'ineq', 'fun': lambda x: cons_f(x)}
    
    p = optimize.minimize(
        function_to_optimize, 
        x0 = x0_point, 
        method = opt_method, 
        tol = tol,        
        constraints=[linear_constraint, non_linear_constraint_0, ],
        #constraints=[linear_constraint, ],
        options={'maxiter': maxiter}
    )    
    x_vals, k_vals, b, x_end = calculate_project(p.x)
    
    if print_results == True:
        print(evl_list)
        
    return p, x_vals, k_vals, b, x_end


# mmsv = np.array([-4.50654110e+00, -3.78109508e+00, -3.77256788e+00, -3.68791763e+00,
#        -4.40763185e+00, -3.32028722e+00, -4.54298348e+00, -3.32506743e+00,
#        -3.36247377e+00, -3.29004414e+00, -7.18131800e+00, -2.47547945e+01,
#        -4.79192346e+01, -6.97974793e+01, -9.22228101e+01, -1.20328252e+02,
#        -1.39050203e+02, -1.45803037e+02, -1.45595384e+02, -1.48831341e+02,
#        -1.46555223e+02, -1.47559469e+02, -1.49561192e+02, -1.47075571e+02,
#        -1.48039942e+02, -1.49179745e+02, -1.48015894e+02, -1.42065801e+02,
#        -1.31499762e+02, -1.20196639e+02, -1.08070852e+02, -9.29365478e+01,
#        -8.05533111e+01, -6.74678247e+01, -5.43556917e+01, -3.77378327e+01,
#        -2.85200194e+01, -1.50746459e+01, -4.97858218e+00, -3.14545788e-01,
#         1.02646524e+00, -1.41989684e-02,  2.69493973e+00,  3.83609766e+00,
#         3.70076303e+00])

# N = len(mmsv)
# u = [1, 1, 1, 1, 1]
# u = [0, 1, 0, 1, 0]
# f = [np.nan, np.nan, np.nan, np.nan, np.nan]
# #f = [np.nan, np.nan, np.nan, np.nan, np.nan]
# x_points = [11, 17, 27, 39]
# l = [np.nan, np.nan, np.nan, 11.84, np.nan]
# l = [np.nan, np.nan, np.nan, np.nan, np.nan]
# #l = [10.7, 5.315, np.nan, 11.84, 5.5]

# sum_equality_condition = True
# ubound = 40*np.ones((N, ))
# lbound = -40*np.ones((N, ))

# f_ev = 0
# for i in range(N):
#     f_ev += (N - 1 - i) * mmsv[i]
    
# find_b = generate_solution(mmsv, x_points, u, f, l, sum_equality_condition)
# lb, ub = generate_constraints(mmsv, x_points, l)

# %%time
# p, x_vals, k_vals, b, x_end = build_project_plan_track_new(
#     mmsv, u, x_points, f, l, find_b, sum_equality_condition, 
#     ubound, lbound, 
#     opt_method = 'COBYLA',
#     lb_constr = lb, ub_constr = ub,
#     tol=1e-2, maxiter=10000, print_results = False
# )
# print(p)

# N=len(mmsv)   

# azy = list()
# for i in range(len(mmsv)):
#     azy.append(curve_pattern_new(i, x_vals[1:], k_vals, b, x_vals[0], x_end))
# azy=np.array(azy)

# EV_table=np.zeros((len(mmsv),42))

# EV_table[:,0]=mmsv
# EV_table[:,1]=azy
# EV_table[:,2]=EV_table[:,0]-EV_table[:,1]
# EV_table[0,3]=EV_table[0,2]
# for i in range(1,len(mmsv)):
#     EV_table[i,3]=EV_table[i-1,3]+EV_table[i,2]
# EV_table[0,4]=0
# EV_table[1,4]=EV_table[0,3]
# for i in range(2,len(mmsv)):
#     EV_table[i,4]=EV_table[i-1,4]+EV_table[i-1,3] 
# EV_table[:,4]=2*EV_table[:,4]

# EV_table[:,10]=EV_table[:,1]  
# EV_table[:,13]=EV_table[:,4]     
    
# plt.plot(mmsv)
# plt.plot(azy)

# plt.plot(EV_table[:,13])

# print("Разность эвольвент на конце участка:", EV_table[:,13][-1], "Сумма разности стрел:", EV_table[:,3][-1])