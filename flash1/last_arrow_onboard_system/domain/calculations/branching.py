import numpy as np
import pandas as pd
from enum import Enum
from .helpers import find_max_delta_in_progtask_at


class BranchType(Enum):
    Fact = 0
    Project = 1

# def calc_dF(start_step: int, length_in_steps: int, length_in_meters: float, fact: pd.Series, project: pd.Series, data_step = 0.185) -> pd.Series:
#     # Fi+(fi-Fi)*Li/L = Fi + dF
#     Fi = project[start_step:start_step+length_in_steps]
#     fi = fact[start_step:start_step+length_in_steps]
#     Li = np.array(range(length_in_steps))*data_step # расстояние от начала экстренного отвода на i-ом шаге
#     return (fi - Fi)*Li/length_in_meters

def calc_dF(branch_to: BranchType, start_step: int, length_in_steps: int, length_in_meters: float, fact: pd.Series, project: pd.Series, data_step = 0.185) -> pd.Series:
    # Fi+(fi-Fi)*Li/L = Fi + dF
    L = length_in_meters
    Fi = project[start_step:start_step+length_in_steps]
    fi = fact[start_step:start_step+length_in_steps]
    Li = np.array(range(length_in_steps))*data_step # расстояние от начала экстренного отвода на i-ом шаге    
    return (fi-Fi)*Li/L if branch_to.Fact else (fi-Fi)*((L-Li)/L)

def make_urgent_branch(task: pd.DataFrame, start_step: int, per_mille: float, front_chord: float, data_step = 0.185) -> pd.DataFrame:
    """
    Экстренный отвод. 
    Отвод от проектных данных к натурным (срочное окончание работ).
    """  
        
    # находим максимальное значение из подъемки, сдвижки или возвышения
    delta_max = find_max_delta_in_progtask_at(start_step, task)
    
    Lm = abs(delta_max/per_mille)          # длина отвода в метрах
    Ls = int(np.ceil(Lm/data_step))        # длина отвода в шагах - количество элементов массива с шагом data_step
    Li = np.array(range(Ls))*data_step     # расстояние от начала экстренного отвода на i-ом шаге
    
    front_chord_start_step = start_step + int(front_chord/data_step) # начало передней зоны машины    
    end_step = front_chord_start_step + Ls                           # конец программного задания     
    
    branch = task.iloc[:end_step].copy()
    
    # Формируем программное задание    
    branch['front_delta_multiplier'] = np.ones(end_step)
    # branch.front_delta_multiplier[front_chord_start_step:end_step] = (Lm-Li)/Lm
    branch.loc[front_chord_start_step:end_step, "front_delta_multiplier"] = (Lm-Li)/Lm
    
    # проект отвода возвышения
    branch['vozv_prj'] = task['vozv_prj'][:end_step]
    branch['vozv_fact'] = task['vozv_fact'][:end_step]
    branch['vozv_dF'] = np.zeros(end_step)
    
    # заполняем участок отвода для рабочей зоны
    # branch.vozv_dF[start_step:start_step+Ls] = calc_dF(start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.vozv_fact, project=task.vozv_prj)
    branch.loc[start_step:start_step+Ls, "vozv_dF"] = calc_dF(branch_to=BranchType.Fact, start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.vozv_fact, project=task.vozv_prj)
    
    # заполняем участок отвода для передней зоны фактическими данными
    # branch.vozv_dF[start_step+Ls:end_step] = task.vozv_fact[start_step+Ls:end_step] - task.vozv_prj[start_step+Ls:end_step]
    branch.loc[start_step+Ls:end_step, "vozv_dF"] = task.vozv_fact[start_step+Ls:end_step] - task.vozv_prj[start_step+Ls:end_step]

    # Отвод в плане
    branch['plan_prj'] = task['plan_prj'][:end_step]
    branch['plan_fact'] = task['plan_fact'][:end_step]
    branch['plan_dF'] = np.zeros(end_step)
    # branch.plan_dF[start_step:start_step+Ls] = calc_dF(start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.plan_fact, project=task.plan_prj)
    # branch.plan_dF[start_step+Ls:end_step] = task.plan_fact[start_step+Ls:end_step] - task.plan_prj[start_step+Ls:end_step]
    branch.loc[start_step:start_step+Ls, "plan_dF"] = calc_dF(branch_to=BranchType.Fact, start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.plan_fact, project=task.plan_prj)
    branch.loc[start_step+Ls:end_step, "plan_dF"] = task.plan_fact[start_step+Ls:end_step] - task.plan_prj[start_step+Ls:end_step]
    
    # Отвод в профиле
    branch['prof_prj'] = task['prof_prj'][:end_step]
    branch['prof_fact'] = task['prof_fact'][:end_step]
    branch['prof_dF'] = np.zeros(end_step)
    # branch.prof_dF[start_step:start_step+Ls] = calc_dF(start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.prof_fact, project=task.prof_prj)
    # branch.prof_dF[start_step+Ls:end_step] = task.prof_fact[start_step+Ls:end_step] - task.prof_prj[start_step+Ls:end_step]
    branch.loc[start_step:start_step+Ls, "prof_dF"] = calc_dF(branch_to=BranchType.Fact, start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.prof_fact, project=task.prof_prj)
    branch.loc[start_step+Ls:end_step, "prof_dF"] = task.prof_fact[start_step+Ls:end_step] - task.prof_prj[start_step+Ls:end_step]
    
    return branch 


def branch_from_fact_to_project(task: pd.DataFrame, start_step: int, per_mille: float, front_chord: float, data_step = 0.185) -> pd.DataFrame:
    """
    Отвод от натурных данных к проекту, т.е начало работ.
    """  
    
    # находим максимальное значение из подъемки, сдвижки или возвышения
    delta_max = find_max_delta_in_progtask_at(start_step=start_step, task=task)
    
    Lm = abs(delta_max/per_mille)          # длина отвода в метрах
    Ls = int(np.ceil(Lm/data_step))        # длина отвода в шагах - количество элементов массива с шагом data_step
    Li = np.array(range(Ls))*data_step     # расстояние от начала экстренного отвода на i-ом шаге
    
    front_chord_start_step = start_step + int(front_chord/data_step) # начало передней зоны машины    
    end_step = front_chord_start_step + Ls                           # конец отвода для передней зоны (программного задания)
    
    branch = task.iloc[:end_step].copy()
    
    # Формируем программное задание    
    branch['front_delta_multiplier'] = np.ones(end_step)    
    branch.front_delta_multiplier[front_chord_start_step:end_step] = Li/Lm
    
    # проект отвода возвышения
    branch['vozv_prj'] = task['vozv_prj'][:end_step]
    branch['vozv_fact'] = task['vozv_fact'][:end_step]
    branch['vozv_dF'] = np.zeros(end_step)
    # заполняем участок отвода для рабочей зоны
    branch.vozv_dF[start_step:start_step+Ls] = calc_dF(branch_to=BranchType.Project, start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.vozv_fact, project=task.vozv_prj)
    # заполняем участок отвода для передней зоны фактическими данными
    branch.vozv_dF[start_step+Ls:end_step] = task.vozv_fact[start_step+Ls:end_step] - task.vozv_prj[start_step+Ls:end_step]
    
    # Отвод в плане
    branch['plan_prj'] = task['plan_prj'][:end_step]
    branch['plan_fact'] = task['plan_fact'][:end_step]
    branch['plan_dF'] = np.zeros(end_step)
    branch.plan_dF[start_step:start_step+Ls] = calc_dF(branch_to=BranchType.Project, start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.plan_fact, project=task.plan_prj)
    branch.plan_dF[start_step+Ls:end_step] = task.plan_fact[start_step+Ls:end_step] - task.plan_prj[start_step+Ls:end_step]
    
    # Отвод в профиле
    branch['prof_prj'] = task['prof_prj'][:end_step]
    branch['prof_fact'] = task['prof_fact'][:end_step]
    branch['prof_dF'] = np.zeros(end_step)
    branch.prof_dF[start_step:start_step+Ls] = calc_dF(branch_to=BranchType.Project, start_step=start_step, length_in_steps=Ls, length_in_meters=Lm, fact=task.prof_fact, project=task.prof_prj)
    branch.prof_dF[start_step+Ls:end_step] = task.prof_fact[start_step+Ls:end_step] - task.prof_prj[start_step+Ls:end_step]
    
    return branch    

def branch_from_project_to_fact(task: pd.DataFrame, start_step: int, per_mille: float, front_chord: float, data_step = 0.185) -> pd.DataFrame:
    return make_urgent_branch(
            task=task, 
            start_step=start_step, 
            per_mille=per_mille, 
            front_chord=front_chord, 
            data_step=data_step)


