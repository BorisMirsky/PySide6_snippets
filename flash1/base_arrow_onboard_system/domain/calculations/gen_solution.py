from sympy import symbols
from sympy import solve
from sympy import lambdify
from sympy import reduce_inequalities
import numpy as np

def generate_solution_old(msv, x):
    N = len(msv)
    L = len(x)
    b = symbols('b')
    ufunc = list()

    for i in range(L+1):    
        locals()[f"e{i}"] = symbols(f'e{i}')
        ufunc.append(locals()[f"e{i}"])

    for i in range(L+1):
        locals()[f"k{i}"] = symbols(f'k{i}')
        ufunc.append(locals()[f"k{i}"])

    locals()[f"b{0}"] = b - locals()[f"k{0}"]*locals()[f"e{0}"]
    for i in range(1, L+1):
        locals()[f"b{i}"] = (x[i-1] + locals()[f"e{i}"])*(locals()[f"k{i-1}"] - locals()[f"k{i}"]) + locals()[f"b{i-1}"]       
        
    s = 0
    for i in range(N):   
        if i < x[0]:
            h = locals()[f"k{0}"]*i + locals()[f"b{0}"] - msv[i]
        for j in range(1, L):
            if (i >= x[j - 1]) & (i < x[j]):
                h = locals()[f"k{j}"]*i + locals()[f"b{j}"] - msv[i]
        if i >= x[-1]:
            h = locals()[f"k{L}"]*i + locals()[f"b{L}"] - msv[i] 

        s += (N - i - 1)*h
    
    res_func = solve(s, b)[0]      
    find_b = lambdify(ufunc, res_func)
    return find_b

#n -номер находимой переменной, 0 <= n <= 2*L+1 = 2*len(x)+3
#len(f_values) = len(x), по сути fi - это значение в точке xi, но только для участков, где у нас круговая кривая, т.е. где u_values[i] = 0
def generate_solution(msv, x, u_values, f_values, l_values, sum_equality_condition = True):
    N = len(msv)
    L = len(x)
    
    b = symbols('b')
    
    ufunc = list()
    ufunc.append(b)
    wfunc = list()
    wfunc.append(b)
    
    for i in range(L+1):
        locals()[f"k{i}"] = symbols(f'k{i}')
        if u_values[i] == 0:
            locals()[f"k{i}"] = 0
        else:
            ufunc.append(locals()[f"k{i}"])

    for i in range(L+1):   
        wfunc.append(locals()[f"k{i}"])  
        
    locals()[f"e{0}"] = symbols(f'e{0}')    
    ufunc.append(locals()[f"e{0}"])     
    for i in range(1, L+2): 
        locals()[f"e{i}"] = symbols(f'e{i}')
        
    for i in range(1, L+1):   
        #locals()[f"e{i}"] = symbols(f'e{i}')
        if np.isnan(l_values[i-1]) == False:
            if i == 1:
                locals()[f"e{i}"] = locals()[f"e{i-1}"] + l_values[i-1] - x[i-1]
            else:
                locals()[f"e{i}"] = locals()[f"e{i-1}"] + l_values[i-1] + x[i-2] - x[i-1]
        else:
            break  

    for j in range(L, i - 1, -1):   
        #locals()[f"e{j}"] = symbols(f'e{j}')
        if np.isnan(l_values[j]) == False:
            if j == L:
                locals()[f"e{j}"] = N - 1 - locals()[f"e{L + 1}"] - x[L - 1] - l_values[L]
            else:
                locals()[f"e{j}"] = locals()[f"e{j+1}"] + x[j] - x[j-1] - l_values[j] 
        else:
            ufunc.append(locals()[f"e{j}"])      
    
    ufunc.append(locals()[f"e{L+1}"])  

    for i in range(L+2):
        wfunc.append(locals()[f"e{i}"])     
    
    #print(locals()[f"e{0}"], locals()[f"e{1}"], locals()[f"e{2}"], locals()[f"e{3}"], locals()[f"e{4}"], locals()[f"e{5}"])     
    #print(ufunc)
    #print(wfunc)

    tfunc = list()
    for i in range(len(wfunc)):
        if wfunc[i] in ufunc:
            tfunc.append(wfunc[i])           
    ufunc = tfunc    
    
    var_list = list()
    f_condition_list = list()
    
    #for i in range(len(n_values)):
    #    var_to_find.append(ufunc[n_values[i]])
                           
    #for i in range(len(n_values)):                           
    #    ufunc.pop(n_values[i] - i)
                           
    locals()[f"b{0}"] = b - locals()[f"k{0}"]*locals()[f"e{0}"]
    #print(locals()[f"b{0}"])
    for i in range(1, L+1):
        locals()[f"b{i}"] = (x[i-1] + locals()[f"e{i}"])*(locals()[f"k{i-1}"] - locals()[f"k{i}"]) + locals()[f"b{i-1}"]       
        #print(locals()[f"b{i}"])
    ct = 0
    for i in range(L+1):
        if u_values[i] == 0:
            if np.isnan(f_values[i]) == False:
                var_list.append(ufunc[ct])
                f_condition_list.append(locals()[f"b{i}"] - f_values[i])
                ct += 1
    
    if ct + int(sum_equality_condition) > np.sum(u_values):
        print("Warning! Number of variables less than number of conditions. Possibly solution will not be found.")
        
    
    s = 0
    evn = 0
    for i in range(N):   
        if i < x[0]:
            #print(f'x{i}_{0}')
            h = locals()[f"k{0}"]*i + locals()[f"b{0}"] - msv[i]
        for j in range(1, L):
            if (i >= x[j - 1]) & (i < x[j]):
                #print(f'x{i}_{j}')
                h = locals()[f"k{j}"]*i + locals()[f"b{j}"] - msv[i]
        if i >= x[-1]:
            #print(f'x{i}_{L}')
            h = locals()[f"k{L}"]*i + locals()[f"b{L}"] - msv[i] 
        s += h
        evn += (N - i - 1)*h
        #print(h)
    #print(evn)    
    # Чтобы не добавлять переменную e0, т.к. если участок начинается с круговой кривой, она ни на что не влияет
    if ufunc[ct] == locals()[f"e{0}"]:       
        ct += 1    
    var_list.append(ufunc[ct])    
    f_condition_list.append(evn)
    
    if sum_equality_condition == True:
        if ufunc[ct+1] == locals()[f"e{0}"]:       
            ct += 1
        var_list.append(ufunc[ct+1])      
        f_condition_list.append(s)            
    
    res_func = solve(f_condition_list, var_list)
    

    
    vfunc = list()
    var_delta = set(ufunc) - set(var_list)
    for i in range(len(wfunc)):
        if wfunc[i] in var_delta:
            vfunc.append(wfunc[i])
            
    #print(ufunc)
    #print(var_list)
    #print(f_condition_list)   
    #print(res_func)
    #print(vfunc)
    
    find_solution = list()
    for i in range(len(var_list)):
        if isinstance(res_func, dict) == True:
            find_solution.append(lambdify(vfunc, res_func.get(var_list[i])))
        else:
            find_solution.append(lambdify(vfunc, res_func[0][i]))
    return find_solution

def generate_constraints(msv, x, l_values):
    N = len(msv)
    L = len(x)
    
    ufunc = list()
    wfunc = list()      
    
    locals()[f"e{0}"] = symbols(f'e{0}')    
    ufunc.append(locals()[f"e{0}"])     
    for i in range(1, L+2): 
        locals()[f"e{i}"] = symbols(f'e{i}')
        
    for i in range(1, L+1):   
        if np.isnan(l_values[i-1]) == False:
            if i == 1:
                locals()[f"e{i}"] = locals()[f"e{i-1}"] + l_values[i-1] - x[i-1]
            else:
                locals()[f"e{i}"] = locals()[f"e{i-1}"] + l_values[i-1] + x[i-2] - x[i-1]
        else:
            break  

    for j in range(L, i - 1, -1):   
        if np.isnan(l_values[j]) == False:
            if j == L:
                locals()[f"e{j}"] = N - 1 - locals()[f"e{L + 1}"] - x[L - 1] - l_values[L]
            else:
                locals()[f"e{j}"] = locals()[f"e{j+1}"] + x[j] - x[j-1] - l_values[j] 
        else:
            ufunc.append(locals()[f"e{j}"])      
    
    ufunc.append(locals()[f"e{L+1}"])      

    for i in range(L+2):
        wfunc.append(locals()[f"e{i}"])       
    
    #print(ufunc)
    #print(wfunc)
    
    ineq_list = list()
    
    for i in range(L+2):
        ineq_list.append(-1 <= locals()[f"e{i}"])
        ineq_list.append(locals()[f"e{i}"] <= 0)        

    
    ineq_var_list = list()    
    for i in range(len(wfunc)):
        if wfunc[i] in ufunc:
                ineq_var_list.append(wfunc[i])
             
    #print(ineq_list)
    #print(ineq_var_list)
    #print(reduce_inequalities(ineq_list, ineq_var_list))        

    lb = -np.ones((len(ineq_var_list), )) + 10**(-7)
    ub = np.zeros((len(ineq_var_list), ))
    zx = reduce_inequalities(ineq_list, ineq_var_list)
    
    for i in zx.args:
        for j in range(len(ineq_var_list)):
            if i.args[0] == ineq_var_list[j]:
                ub[j] = float(i.args[1])
                break

            if i.args[1] == ineq_var_list[j]:
                lb[j] = float(i.args[0])
                break     
    
    return lb, ub