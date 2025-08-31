import numpy as np
from sympy import symbols
from sympy import Matrix
from sympy import solve
from sympy import lambdify


def recalculate_index(index, degree):

    idx = 0
    if index == 0:
        return idx

    ct = 0
    for idx in range(len(degree)):
        if degree[idx] == 1:
            ct += 1
        if ct == index:
            break
    return idx + 1


def generate_lincond_matrix(f, degree, end_evl_to_zero=False, summ_evl_to_zero=False):
    
    fit_breaks = list() 
    
    locals()[f"sum_y"] = symbols(f'sum_y')  
    locals()[f"last_evl_value"] = symbols(f'last_evl_value')  
    locals()[f"sum_gy"] = symbols(f'sum_gy')  
    
    for i in range(len(degree) + 1):
        locals()[f"ft{i}"] = symbols(f'ft{i}')    
        fit_breaks.append(locals()[f"ft{i}"])

    summ_list = list()       
    for i in range(len(f)):
        locals()[f"s{i}"] = symbols(f's{i}')    
        summ_list.append(locals()[f"s{i}"])

    end_evl_list = list()
    for i in range(len(f)):
        locals()[f"end_evl{i}"] = symbols(f'end_evl{i}')    
        end_evl_list.append(locals()[f"end_evl{i}"])

    summ_evl_list = list()        
    for i in range(len(f)):
        locals()[f"summ_evl{i}"] = symbols(f'summ_evl{i}')    
        summ_evl_list.append(locals()[f"summ_evl{i}"])
        
    beta = list()
    var_list = list()
    b_list = list()
    f_without_none = list()

    for i in range(np.sum(degree) + 1):
        locals()[f"b{i}"] = symbols(f'b{i}')
        locals()[f"f_without_none{i}"] = symbols(f'f_without_none{i}')
        beta.append(locals()[f"b{i}"])
        if f[i] is not None:
            var_list.append(locals()[f"b{i}"])
            f_without_none.append(locals()[f"f_without_none{i}"])
        else:
            b_list.append(locals()[f"b{i}"])
    
    zeta = list()
    z = Matrix(summ_list).T*Matrix(beta) - Matrix([locals()[f"sum_y"]])
    zeta.append(z)
    
    if end_evl_to_zero:
        ez = Matrix(end_evl_list).T*Matrix(beta) - Matrix([locals()[f"last_evl_value"]])
        zeta.append(ez)
    
    if summ_evl_to_zero:
        gz = Matrix(summ_evl_list).T*Matrix(beta) - Matrix([locals()[f"sum_gy"]])
        zeta.append(gz)
    
    condition_number = 1 + int(end_evl_to_zero) + int(summ_evl_to_zero)
    
    summ_list.append(locals()[f"sum_y"])     
    end_evl_list.append(locals()[f"last_evl_value"])   
    summ_evl_list.append(locals()[f"sum_gy"])           

    ct = -1
    for i in range(len(f)):
        if f[i] is not None:
            ct += 1
            if i == 0:
                zeta.append(locals()[f"b{i}"] - f_without_none[ct])

            else:
                u = locals()[f"b{0}"]
                for j in range(1, i + 1):
                    idx = recalculate_index(j, degree)
                    if idx == 0:
                        u += locals()[f"b{j}"] * fit_breaks[idx]
                    else:
                        u += locals()[f"b{j}"] * (fit_breaks[idx] - fit_breaks[idx - 1])
                zeta.append((u - f_without_none[ct]))
    
    conditions_counter = 0
    for i in range(len(f) - 1, -1, -1):
        if conditions_counter >= condition_number:
            break     
        if f[i] is None:       
            var_list.append(locals()[f"b{i}"])
            conditions_counter += 1

    # print("var_list:", var_list)
    solved_system = solve(zeta, var_list, dict=True)
    solved_system = solved_system[0] if type(solved_system) is list else solved_system 
    
    # print("solved_system:", solved_system)
    
    kf_matrix = list()     
    sv = list()
    for i in beta:
        if i in var_list:
            kf_list = list()
            sv_expression = solved_system[i]
            # print("sv_expression:", sv_expression)
            for j in b_list[: -condition_number]:
                u = solved_system[i].simplify().expand().coeff(j)
                kf_list.append(u)
                sv_expression = sv_expression - j*u
            # print("sv_expression:", sv_expression)
            # print("sv_expression_simplified:", sv_expression.simplify())
            sv.append(sv_expression.simplify())
            kf_matrix.append(kf_list)
        
    # print("var_list:", var_list)
    # print("b_list:", b_list)
    # print("kf_matrix:", kf_matrix)
    # print("sv:", sv)
        
    ax = lambdify(summ_list + end_evl_list + summ_evl_list + fit_breaks + var_list + b_list[:-condition_number] + f_without_none, kf_matrix)
    ay = lambdify(summ_list + end_evl_list + summ_evl_list + fit_breaks + var_list + b_list[:-condition_number] + f_without_none, sv)

    return ax, ay
