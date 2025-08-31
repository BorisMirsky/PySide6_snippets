import pandas as pd
import numpy as np
from typing import List
from enum import Enum
import datetime
import random
from scipy import optimize
from scipy.optimize import LinearConstraint
from cantok import SimpleToken

from .gen_solution import generate_solution, generate_constraints
from .track_funcs import count_curve_parametres, count_new_params

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
    if print_results == True:
        print("dim_k_to_optimize:", dim_k_to_optimize, "dim_x_to_optimize:", dim_x_to_optimize)
    
    x0_point = -0.5*np.ones((dim_x_to_optimize + dim_k_to_optimize, ))    
    
    if lb_constr.shape[0] <= x0_point.shape[0]:
        x0_point[dim_k_to_optimize : ] = (lb_constr + ub_constr)/2
        
    def minimize_sq(ks_vector):
        sq = 0
        xks_vector = np.concatenate([ks_vector, x0_point[dim_k_to_optimize : ]])
        x_vals, k_vals, b, x_end = calculate_project(xks_vector)
        for i in range(N):
            x_proekt = curve_pattern_new(i, np.copy(x_vals[1:]), np.copy(k_vals), b, x_vals[0], x_end)
            diff_strel = msv[i] - x_proekt
            sq += diff_strel**2
        return sq    
    
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
   
    t = datetime.datetime.now()
    if dim_k_to_optimize > 0:
        k_vector_opt =  optimize.minimize(minimize_sq, 
        x0 = x0_point[: dim_k_to_optimize], 
        method = opt_method, 
        tol = tol,        
        options={'maxiter': maxiter})
        
        if k_vector_opt.success == True:
            x0_point[: dim_k_to_optimize] = k_vector_opt.x
            
        if print_results == True:
            print(k_vector_opt)
            print("x0_point:", x0_point)
            print("time passed:", datetime.datetime.now() - t)    
    
    A=np.zeros((dim_x_to_optimize + dim_k_to_optimize, dim_x_to_optimize + dim_k_to_optimize))    
    for i in range(dim_k_to_optimize, dim_x_to_optimize + dim_k_to_optimize):
        A[i,i]=1
        
    if print_results == True:
        print("matrix of linear constraints", A)
    
    l_c = -1 + 10**(-7)
    u_c = 0
    
    if lb_constr.shape[0] <= x0_point.shape[0]:
        l_c = np.zeros((dim_x_to_optimize + dim_k_to_optimize, )) - 10**100
        u_c = np.zeros((dim_x_to_optimize + dim_k_to_optimize, )) + 10**100
        l_c[dim_k_to_optimize : ] = lb_constr
        u_c[dim_k_to_optimize : ] = ub_constr

    if print_results == True:
        print("vectors of linear constraints", l_c, u_c)
        
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

class Node:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.childs = list()
        self.action = list()
        self.mean_value = 0.0      
        self.max_value = -np.inf         
        self.result = np.nan
        self.sum_squared_results = 0.0        
        self.number_of_visits = 0.0
        self.end_node = False

    def AppendChild(self, child):
        self.childs.append(child)
        child.parent = self

def play_episode(mmsv, u, f, l, x_points, sum_equality_condition, ubound, lbound, opt_method, maxiter = 10000):

    find_b = generate_solution(mmsv, x_points, u, f, l, sum_equality_condition)
    lb, ub = generate_constraints(mmsv, x_points, l)    
    
    
    p, x_vals, k_vals, b, x_end = build_project_plan_track_new(
        mmsv, u, x_points, f, l, find_b, sum_equality_condition, 
        ubound, lbound, 
        opt_method = opt_method,
        lb_constr = lb, ub_constr = ub,
        tol=1e-2, maxiter=maxiter, print_results = False)
    
    if p.success == True:
        reward = 1/p.fun   
        return reward, True, p, x_vals, k_vals, b, x_end    
        
    p, x_vals, k_vals, b, x_end = build_project_plan_track_new(
                                                mmsv, u, x_points, f, l, find_b, sum_equality_condition, 
                                                ubound = 10**100*np.ones((len(mmsv), )), lbound = -10**100*np.ones((len(mmsv), )), 
                                                opt_method = opt_method,
                                                lb_constr = lb, ub_constr = ub,
                                                tol=1e-2, maxiter=maxiter, print_results = False)  
    reward = -p.fun
        
    return reward, False, p, x_vals, k_vals, b, x_end

def get_x_points(x_start, actions_list):
    N = len(x_start)
    x_start_new = x_start.copy()
    for i in range(len(actions_list)):
        j = i % N
        x_start_new[j] += actions_list[i]
    return x_start_new

def get_x_points_chars(x, l):
    y = np.zeros((len(x), ))

    for i in range(len(l) - 1, 0, -1):
        if np.isnan(l[i]) == False:
            y[i - 1] = -100
        else:
            break

    if i > 1:        
        for j in range(i):
            if np.isnan(l[j]) == False:
                y[j] = -100
            else:
                break   

    dim_index = j            
    for k in range(j, i):
        if np.isnan(l[k]) == False:
            y[dim_index] += 1
            y[k] = -1
        else:
            dim_index = k
    return y

def get_possible_actions_list(x_start_new, points_chars, actions_list, L):
    N = len(x_start_new)
    j = (len(actions_list))%N
    possible_actions_list = list()
    
    #Free-point case
    if points_chars[j] == 0:    
        if j == 0:
            if x_start_new[j] > 0:
                possible_actions_list.append([-1])
        else:
            if x_start_new[j] > x_start_new[j-1] + 1:
                possible_actions_list.append([-1])  

        possible_actions_list.append([0])   

        if j >= N - 1:
            if x_start_new[j] < L - 1:
                possible_actions_list.append([1])
        else:
            if x_start_new[j] < x_start_new[j+1] - 1:
                possible_actions_list.append([1]) 
                
    #Point with linked points case
    elif points_chars[j] > 0:
        ulist = list()
        if j == 0:
            if x_start_new[j] > 0:
                for k in range(int(points_chars[j]) + 1):
                    ulist.append(-1)
                possible_actions_list.append(ulist)
        else:
            if x_start_new[j] > x_start_new[j-1] + 1:
                for k in range(int(points_chars[j]) + 1):
                    ulist.append(-1)  
                possible_actions_list.append(ulist) 
                
        ulist = list()        
        for k in range(int(points_chars[j]) + 1):
            ulist.append(0)   
        possible_actions_list.append(ulist)
        
        ulist = list()
        if j + int(points_chars[j]) >= N - 1:
            if x_start_new[j + int(points_chars[j])] < L - 1:
                for k in range(int(points_chars[j]) + 1):
                    ulist.append(1)
                possible_actions_list.append(ulist)
        else:
            if x_start_new[j + int(points_chars[j])] < x_start_new[j + int(points_chars[j]) + 1] - 1:
                for k in range(int(points_chars[j]) + 1):
                    ulist.append(1) 
                possible_actions_list.append(ulist)
        
    #Linked-point case      
    #По идее сюда никогда не должны попадать
    elif points_chars[j] == -1:
        possible_actions_list.append(actions_list[-1])
        print("ERROR!")
        
    #Fixed point case
    elif points_chars[j] == -100: 
        possible_actions_list.append([0])
        
    return possible_actions_list

def mcts(number_of_nodes_to_expanse, C, D, T, W, epsilon,
         msv, u, f, l, x_start, sum_equality_condition, ubound, lbound, opt_method,
         stop_by_time = False, stop_by_found_solution = False, maxiter = 10000, verbose = False, token = SimpleToken()):

    root_node = Node('root')
    x_points = x_start
    points_chars = get_x_points_chars(x_start.copy(), l)
    #print("points_chars", points_chars)
    x_dict = dict()
        
    start_time = datetime.datetime.now()    
    
    # for node_to_expanse in tqdm(range(number_of_nodes_to_expanse)):
    for node_to_expanse in range(number_of_nodes_to_expanse):

        #Проверяем условие остановки 
        token.check()        
        
        #Проверяем условие остановки по времени
        if stop_by_time is not False:
            calculation_time = datetime.datetime.now() - start_time
            time_passed = calculation_time.days*24*3600 + calculation_time.seconds
            if time_passed > stop_by_time:
                print("Time exceed! Calculation duration:", time_passed, "second")
                break
        
        # Selection strategy
        node = root_node    
        isSelected = False
        while len(node.childs) > 0:
            #Если дошли до конечной ноды, заканчиваем поиск
            if node.end_node == True:
                break   

            #Если у ноды есть ребенок, у которых не было ни одного посещения, выбираем его
            for i in range(len(node.childs)):
                if node.childs[i].number_of_visits == 0:
                    node = node.childs[i]
                    isSelected = True
                    break

            if isSelected == True:
                break

            #Если у всех детей были посещения, движемся дальше  
            #Если общее количество ноды меньше константы Т, осуществяем выбор ребенка случайным образом
            if node.number_of_visits <= T:
                if len(node.childs) > 0:
                    node = random.choice(node.childs)

            # Иначе выбираем ребенка по методу UCB        
            else:       
                ucb_array = np.zeros((len(node.childs), ))
                for i in range(len(node.childs)):
                    v = (1 - W)*node.childs[i].mean_value + W*node.childs[i].max_value
                    s1 = np.log(node.number_of_visits)/node.childs[i].number_of_visits
                    s2 = (node.childs[i].sum_squared_results + node.childs[i].number_of_visits*v**2 + D)/node.childs[i].number_of_visits
                    ucb_array[i] = v - C*s1**0.5 - s2**0.5
                selected_node = np.argmax(ucb_array)
                node = node.childs[selected_node]

        if node.end_node == True:
            break  
            
        #print(node, node.name, node.childs, node.mean_value, node.number_of_visits)
        # Play-Out strategy    
        #Находим путь до узла по предыдущим действиям начиная со стартового положения
        a_node = node
        actions_list = list()
        count_actions = 0
        for i in range(number_of_nodes_to_expanse):
            if (not a_node.parent) == True:
                break
            else:
                actions_list += a_node.action
                a_node = a_node.parent
                count_actions += 1

        actions_list =  actions_list[::-1]

        x_start_new = get_x_points(x_start.copy(), actions_list.copy())
        
        new_reward, new_p = x_dict.get(tuple(x_start_new), (-np.inf, -1))

        if new_p == -1:
            new_reward, new_success, new_p, new_x_vals, new_k_vals, new_b, new_x_end = play_episode(msv, u, f, l, x_start_new.copy(),
                                                                                                    sum_equality_condition, ubound, lbound, opt_method, maxiter = maxiter)   
            x_dict[tuple(x_start_new)] = [new_reward, new_p]
            
        # Expansion strategy
        a_node = node
        possible_actions_list = get_possible_actions_list(x_start_new.copy(), points_chars.copy(), actions_list.copy(), len(msv))                    
        #print("actions_list", actions_list, "possible_actions_list:", possible_actions_list)
        
        for j in range(len(possible_actions_list)):
            child = Node(f'child_{a_node.name}_{j}')
            child.parent = a_node
            child.action = list(possible_actions_list[j])

            a_node.AppendChild(child)  

        # Backpropagation strategy
        a_node = node
        for i in range(count_actions): 
            a_node.mean_value = (a_node.mean_value*a_node.number_of_visits + new_reward)/(a_node.number_of_visits + 1)
            a_node.sum_squared_results += new_reward**2
            a_node.number_of_visits += 1    
            if new_reward > a_node.max_value:
                a_node.max_value = new_reward         
            #Переходим на уровень выше 
            a_node = a_node.parent
        if verbose is not False:
            if node_to_expanse % verbose == 0:
                print("step:", node_to_expanse, "best_reward:", root_node.max_value, "x_start_new:", x_start_new)    
        #Обновление значений в root Node и пути до лучшей попытки
        root_node.mean_value = (root_node.mean_value*root_node.number_of_visits + new_reward)/(root_node.number_of_visits + 1)
        root_node.sum_squared_results += new_reward**2
        root_node.number_of_visits += 1    
        if new_reward > root_node.max_value:
            root_node.max_value = new_reward
            root_node.end_node = [x_start_new, new_p, new_x_vals, new_k_vals, new_b, new_x_end]
            
        #Проверяем условие остановки по нахождению приемлимого решения            
        if (new_success == True) & (stop_by_found_solution == True):
            break
            
    # Taking best try after stopping MCTS
    best_try_reward = root_node.max_value
    best_try_optimization = root_node.end_node
    
    return best_try_reward, best_try_optimization

def calculate_track_params(mmsv, urov, vmax, curve_urov, u, x_vals, k_vals, b, x_end):
    N=len(mmsv)   
    azy = list()
    for i in range(len(mmsv)):
        azy.append(curve_pattern_new(i, x_vals[1:], k_vals, b, x_vals[0], x_end))
    azy=np.array(azy)

    EV_table=np.zeros((len(mmsv), 42))

    EV_table[:, 0] = mmsv
    EV_table[:, 1] = azy
    EV_table[:, 2] = EV_table[:, 0] - EV_table[:, 1]
    EV_table[0, 3] = EV_table[0, 2]
    
    for i in range(1, len(mmsv)):
        EV_table[i, 3] = EV_table[i-1, 3] + EV_table[i, 2]
    EV_table[0, 4] = 0
    EV_table[1, 4] = EV_table[0, 3]
    
    for i in range(2, len(mmsv)):
        EV_table[i, 4] = EV_table[i-1, 4] + EV_table[i-1, 3] 
    EV_table[:, 4] = 2*EV_table[:, 4]

    EV_table[:, 10] = EV_table[:, 1]  
    EV_table[:, 13] = EV_table[:, 4]    

    #Записываем значения уровня на участке
    EV_table[:, 16]=urov
    #Записываем значения максимальной скорости на участке    
    EV_table[:, 17]=vmax    
    
    curve_type = len(u) - np.sum(u)
    start_point = 0
    p_points = np.concatenate([x_vals, np.array([x_end])])
    
    #print(x_vals, k_vals, b, x_end)
    #print(p_points)
    
    EV_table, alc_plan, alc_urov = count_curve_parametres(np.copy(EV_table), urov.copy(), vmax.copy(), curve_type, p_points = p_points, start_point = start_point, a_np_max = 0.7,
                                                         calculation_for_profile = False, start_in_curve = not bool(u[0]), end_in_curve = not bool(u[-1]))    
    if curve_urov != -1:
        alc_urov[alc_urov.columns[5]][alc_urov[alc_urov.columns[3]] == 'возвышение'] = curve_urov    

    return EV_table, alc_plan, alc_urov    

def new_track_calculation(msv, urov, vmax, curve_urov, u, f, l, x_start, sum_equality_condition, ubound, lbound, opt_method, optimize_x_point = False):
        
    if optimize_x_point == False:
        find_b = generate_solution(msv, x_start, u, f, l, sum_equality_condition)
        lb, ub = generate_constraints(msv, x_start, l)
        p, x_vals, k_vals, b, x_end = build_project_plan_track_new(msv, u, x_start, f, l, find_b, sum_equality_condition, ubound, lbound,
                                                                   opt_method = opt_method, lb_constr = lb, ub_constr = ub, tol=1e-2, maxiter=10000, print_results = False)
        # print(p)
    else:   
        best_try_reward, best_try_optimization = mcts(number_of_nodes_to_expanse = optimize_x_point[0], C = optimize_x_point[1], D = optimize_x_point[2],
                                                      T = optimize_x_point[3], W = optimize_x_point[4], epsilon = optimize_x_point[5],
                                                      msv = msv, u = u, f = f, l = l, x_start = x_start,
                                                      sum_equality_condition = sum_equality_condition, ubound = ubound, lbound = lbound, opt_method = opt_method,
                                                      stop_by_time = optimize_x_point[6], stop_by_found_solution = optimize_x_point[7], maxiter = optimize_x_point[8],
                                                      verbose = optimize_x_point[9], token = optimize_x_point[10])
        
        print("success:", best_try_optimization[1].success, ", min square value:", best_try_optimization[1].fun)
        x_start_new, new_p, x_vals, k_vals, b, x_end = best_try_optimization
        print(x_start_new, new_p, x_vals, k_vals, b, x_end)
        
    EV_table, alc_plan, alc_urov = calculate_track_params(msv.copy(), urov.copy(), vmax.copy(), curve_urov, u.copy(), x_vals, k_vals, b, x_end)
    EV_table = pd.DataFrame(EV_table)
    EV_table = count_new_params(EV_table.copy(), alc_urov.copy())
    
    return EV_table, alc_plan, alc_urov, x_vals, x_end

