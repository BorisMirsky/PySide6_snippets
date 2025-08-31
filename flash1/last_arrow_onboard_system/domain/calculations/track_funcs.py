import pandas as pd
import numpy as np
import scipy as sc
import datetime
import hyperopt
from scipy import optimize
from scipy.optimize import fsolve, Bounds, LinearConstraint
from tqdm.notebook import tqdm
from hyperopt import tpe, fmin, hp, Trials, STATUS_OK
from cantok import SimpleToken

from functools import partialmethod
tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)


def data_to_0625(msv,l,L): 
    data=list()   
    d=10**-5
    while int(np.floor(d/l))<len(msv)-1:  
        w=int(np.floor(d/l))
        x1=0
        x2=l        
        y1=msv[w]
        y2=msv[w+1]      
        ka=(y1-y2)/(x1-x2)
        kb=y1-ka*x1
        fx=ka*(d-w*l)+kb
        data.append(fx)
        d+=L        
    data=np.array(data)
    return data

# Нахождение рихтовки по рихтовкам левой и правой
def find_real_rix(msv_rix_l,msv_rix_r):
    data=np.zeros((len(msv_rix_l),))
    for i in range(len(msv_rix_l)):
        if (msv_rix_l[i]>0) & (msv_rix_r[i]>0):
            data[i]=msv_rix_l[i]
        else:
            data[i]=msv_rix_r[i]     
    return data

# Нахождение стрел по координатам
def to_strela(x, y, machine_horde_1, machine_horde_2, d, lng):
    f_new=list()

    machine_horde_length = machine_horde_1 + machine_horde_2

    x_vipr=np.zeros((len(x)+2,))
    y_vipr=np.zeros((len(y)+2,)) 

    x_vipr[1:-1]=x
    y_vipr[1:-1]=y

    x_vipr[0]=x_vipr[1]+(machine_horde_1/d)*(x_vipr[1]-x_vipr[2])
    y_vipr[0]=y_vipr[1]+(machine_horde_1/d)*(y_vipr[1]-y_vipr[2]) 

    x_vipr[-1]=x_vipr[-2]+(machine_horde_2/d)*(x_vipr[-2]-x_vipr[-3])
    y_vipr[-1]=y_vipr[-2]+(machine_horde_2/d)*(y_vipr[-2]-y_vipr[-3])            

    xC_prev=x_vipr[1]-d
    yC_prev=y_vipr[1]
    hC_prev=0
    #tck = sc.interpolate.splrep(x_vipr, y_vipr, s=0)
    tck,_ = sc.interpolate.splprep([x, y], s=0, per=False)

    for i in tqdm(range(lng)):        
        hC = float(fsolve(find_next_point, hC_prev + 1/lng, args=(xC_prev, yC_prev, tck, d)))
        xC, yC = sc.interpolate.splev(hC, tck)

        xC_prev=xC
        yC_prev=yC  
        hC_prev=hC
        
        h1, h2, fstr = fsolve(find_root_4, [hC - machine_horde_1/d/lng, hC + machine_horde_2/d/lng, 1], args=(xC, yC, tck, machine_horde_1, machine_horde_2))
        #print(i, h1, hC, h2, hC-h1, h2-hC)
        x1, y1 = sc.interpolate.splev(h1, tck)
        x2, y2 = sc.interpolate.splev(h2, tck)

        aH = (y2-y1)/(x2-x1)  
        bH = y1-aH*x1    
        xH = x1 + (x2-x1)*machine_horde_1/machine_horde_length
        yH = y1 + (y2-y1)*machine_horde_1/machine_horde_length

        if (yC-aH*xC-bH)*(x2-x1)<=0:
            znak=1
        else:
            znak=-1

        f_new.append(znak*((xC-xH)**2+(yC-yH)**2)**0.5*1000)

    f_new=np.array(f_new)
    return f_new

# Нахождение координат по стрелам
def find_coord(msv,x0,y0,d,machine_horde_1,machine_horde_2):
    x=np.zeros((len(msv),))
    y=np.zeros((len(msv),))

    x[0]=x0
    y[0]=y0
    for i in range(1,len(msv)):
        x[i]=x[i-1]+d*np.cos(msv[i])
        y[i]=y[i-1]+d*np.sin(msv[i])   
        
    # point_start = fsolve(find_root_1, [x0-machine_horde_1, y0, x0+machine_horde_2], args=(x0, y0, x, y, machine_horde_1, machine_horde_2, msv[0]/1000))
    # point_end = fsolve(find_root_2, [x[-1]-machine_horde_1, y[-1], x[-1]+machine_horde_2], args=(x[-1], y[-1], x, y, machine_horde_1, machine_horde_2, msv[-1]/1000))
    #print(point_start,point_end)
    
    # x=np.concatenate([np.array([point_start[0]]), x])
    # x=np.concatenate([x, np.array([point_end[1]])])    
    # y=np.concatenate([np.array([point_start[1]]), y])
    # y=np.concatenate([y, np.array([point_end[2]])])         
    return x,y

def find_fi(msv,l1,l2):
    phi=np.zeros((len(msv),))
    for i in range(len(msv)):
        if msv[i]==0:
            phi[i]=0
        else:
            x0=(l1+l2)/2
            y0=(msv[i]**2-l1*l2)/2/msv[i]
            R=np.sign(msv[i])*(x0**2+y0**2)**0.5
            phi[i]=np.arctan(1/R)
    return phi

def find_psi(msv,d):
    return d*np.cumsum(msv)

def change_coord_system(x, y, coord_x, coord_y, xR2_sh, yR2_sh, xR2, yR2):
    a1=(xR2*xR2_sh+yR2*yR2_sh)/(xR2_sh**2+yR2_sh**2)
    a2=(xR2_sh*yR2-xR2*yR2_sh)/(xR2_sh**2+yR2_sh**2)
    x_new=x*a1-y*a2+coord_x
    y_new=x*a2+y*a1+coord_y
    return x_new,y_new

#Пересчет из несимметричной хорды в симметричную
def horde_to_horde(data, machine_horde_1, machine_horde_2, d, mh1, mh2):    
    # print('horde_to_horde')
    phi = find_fi(data/1000, machine_horde_1, machine_horde_2)
    psi = find_psi(phi, d)
    xx, yy = find_coord(psi, 0, 0, d, machine_horde_1, machine_horde_2)    
    res_to_strela=to_strela(xx, yy, mh1, mh2, d, len(data))         
    return res_to_strela

# Пересчет Из ALC-формата в формат с расстоянием 10 метров между точками
def alc_urov_to_10(alc_urov, res_shape):
    #alc_urov - данные по уровню в формате alc, pd.DataFrame
    #res_shape - количество строк в выходном массиве (количество точек через 10 метров)
    
    res=np.zeros((res_shape,))
    ct=0
    for i in range(alc_urov.shape[0]):
        sx = int(alc_urov[alc_urov.columns[1]].iloc[i])
        if i<alc_urov.shape[0]-1: 
            ex = int(alc_urov[alc_urov.columns[1]].iloc[i+1]) 
        else:
            ex = res_shape*10         
        typex = alc_urov[alc_urov.columns[3]].iloc[i]
        rx = alc_urov[alc_urov.columns[5]].iloc[i]

        if typex == 'возвышение':
            for j in range(int(10*np.ceil(sx/10)), ex, 10):
                res[ct] = rx
                ct+=1
        else:
            x1 = sx
            x2 = sx + rx
            
            if i>0:
                y1 = alc_urov[alc_urov.columns[5]].iloc[i-1]
            else:
                y1 = 0
            if i<alc_urov.shape[0]-1:                
                y2 = alc_urov[alc_urov.columns[5]].iloc[i+1]     
            else:
                y2 = 0
                
            a = (y2-y1)/(x2-x1)
            b=y1-a*x1
            
            for j in range(int(np.ceil(sx/10))*10, ex, 10):
                res[ct]=a*j + b
                ct+=1
    return res

def f(x,x_points,y_points):
    tck = sc.interpolate.splrep(x_points, y_points)
    return sc.interpolate.splev(x, tck)

def find_root_1(t, x0, y0, x_real, y_real, l1, l2, ff):
    return [(t[0]-x0)**2+(t[1]-y0)**2-l1**2-ff**2,
           (t[2]-x0)**2+(f(t[2], x_real, y_real)-y0)**2-l2**2-ff**2,
           (t[0]-t[2])**2+(t[1]-f(t[2], x_real, y_real))**2-(l1+l2)**2]

def find_root_2(t, x0, y0, x_real, y_real, l1, l2, ff):
    return [(t[0]-x0)**2+(f(t[0], x_real, y_real)-y0)**2-l1**2-ff**2,
           (t[1]-x0)**2+(t[2]-y0)**2-l2**2-ff**2,
           (t[0]-t[1])**2+(f(t[0], x_real, y_real)-t[2])**2-(l1+l2)**2]

def find_root_4(t, x0, y0, intrp, l1, l2):
    x1 = sc.interpolate.splev(t[0], intrp)[0]
    x2 = sc.interpolate.splev(t[1], intrp)[0]
    y1 = sc.interpolate.splev(t[0], intrp)[1]
    y2 = sc.interpolate.splev(t[1], intrp)[1]
    return [(x2-x1)**2+(y2-y1)**2-(l1+l2)**2,
           (x1 - x0)**2 + (y1 - y0)**2 - l1**2 -t[2]**2,
           (x2 - x0)**2 + (y2 - y0)**2 - l2**2 -t[2]**2]

# def find_next_point(t, x1, y1, intrp, d_len):
#     return (t - x1)**2 + (sc.interpolate.splev(t, intrp) - y1)**2 - d_len**2

def find_next_point(t, x1, y1, intrp, d_len):
    h = sc.interpolate.splev(t, intrp)
    return (h[0] - x1)**2 + (h[1] - y1)**2 - d_len**2

#Функция определения радиусности кривой
def find_curve_type(msv,k0,k1,max_type_search,max_mean_sq_val, start_in_curve = True, end_in_curve = False):
    i=0
    curve_type=0
    l=len(msv)
    
    while curve_type<=max_type_search:
        curve_type+=1        
        x0_point = find_start_point(np.copy(msv), curve_type, start_in_curve, end_in_curve)
        initial_point, res_quality = find_optimization_initial_point(np.copy(msv), curve_type, x0_point, k0, k1, 0, 0, "SLSQP", maxiter=1000, cons = False, start_in_curve = start_in_curve, end_in_curve = end_in_curve)  
        print('Quality of approximation (detecting for curve type):', res_quality/l)
        if res_quality/l<=max_mean_sq_val:  
            print('Found curve with type =', curve_type, 'with quality of approximation = ', res_quality/l)
            return curve_type,np.array(initial_point)  
    print('Found curve; type not found. Used type = ', curve_type, 'with quality  of approximation = ', res_quality/l)    
    if res_quality < 10**10:
        return curve_type,np.array(initial_point)
    else:
        return 1, find_start_point(np.copy(msv), 1, start_in_curve, end_in_curve)        

# Нахождение начальной точки для задач оптимизации кусочно-линейной функции
def find_optimization_initial_point(msv, L, x0_point, k0, k1, sdx, edx, opt_method, maxiter=1000, cons = False, start_in_curve = False, end_in_curve = False):   
    Lx=2*L - int(start_in_curve) - int(end_in_curve)
    N=len(msv)
    
    def sq_linear_n(xs_vector):
        xx_vector=xs_vector[:Lx]
        kk_vector=xs_vector[Lx:]
            
        sm=0
        for js in range(N):
            sm+=(curve_pattern(js, np.copy(xx_vector), np.copy(kk_vector), N, k0, k1, sdx, edx, start_in_curve, end_in_curve)-msv[js])**2
        return sm
    
    A=np.zeros((2*Lx-1,Lx+L))    
    for i in range(Lx):
        A[i,i]=1

    for i in range(Lx-1):
        A[Lx+i,i]=-1
        A[Lx+i,i+1]=1    

    def eq_cons(xs_vector):
        cons_f=list()
        xx_vector=xs_vector[:Lx]
        kk_vector=xs_vector[Lx:]
            
        sm=0        
        for js in range(N):
            sm+=(curve_pattern(js, np.copy(xx_vector), np.copy(kk_vector), N, k0, k1, sdx, edx, start_in_curve, end_in_curve)-msv[js])            
        cons_f.append(sm)
        return cons_f        
    
    eq_constraint = {'type': 'eq', 'fun': lambda x: eq_cons(x)} 
        
    l_c=1
    u_c=N-2
    linear_constraint = LinearConstraint(A, l_c, u_c)  

    if cons==True:
        constr=[linear_constraint, eq_constraint]
    else:
        constr=[linear_constraint, ]    
    
    p = optimize.minimize(
        sq_linear_n, 
        x0=x0_point, 
        method=opt_method, 
        constraints=constr,
        options={'maxiter': maxiter}
    )

    if p.success==True:
        return p.x, p.fun  
    
    return x0_point, np.inf

#Нахождение начальной точки для функции "find_optimization_initial_point"
def find_start_point(msv, x, start_in_curve, end_in_curve): 
    N=len(msv)
    y = int(start_in_curve) + int(end_in_curve)
    start_point=np.ones((3*x - y,))
    for i in range(2*x - y):
        start_point[i]=(i+1)*N/(2*x-y+1)
    return start_point

#Нахождение значения заданной кусочно-линейной функции в произвольной точке
def curve_pattern(x, x_vector, k_vector, N, k0, k1, x_start, x_end, start_in_curve, end_in_curve):
    #print(x_vector, k_vector)
    if (start_in_curve == False) & (end_in_curve == False):
        b_vector=np.zeros((len(k_vector),))
        b_vector[0]=k0-k_vector[0]*x_start

        if x<x_vector[0]:
            return k_vector[0]*x+b_vector[0]

        for i in range(len(k_vector)):
            if (x>=x_vector[2*i]) & (x<x_vector[2*i+1]):
                return k_vector[i]*x_vector[2*i]+b_vector[i]
            if i<len(k_vector)-1:         
                b_vector[i+1]=k_vector[i]*x_vector[2*i]+b_vector[i]-k_vector[i+1]*x_vector[2*i+1]              
                if (x>=x_vector[2*i+1]) & (x<x_vector[2*i+2]):                              
                    return k_vector[i+1]*x+b_vector[i+1]

        ks=(k1-b_vector[-1]-k_vector[-1]*x_vector[-2])/(N-x_vector[-1]-1+x_end)  
        bs=k1-ks*(N-1+x_end)
        return ks*x+bs
    
    if (start_in_curve == True) & (end_in_curve == False):
        b_vector = np.zeros((len(k_vector),))
        b_vector[-1]=k1-k_vector[-1]*(N-1+x_end)

        if x>x_vector[-1]:
            return k_vector[-1]*x+b_vector[-1]        
        
        for i in range(len(k_vector)-1):
            if (x>=x_vector[-1-2*i-1]) & (x<x_vector[-1-2*i]):
                return k_vector[-1-i]*x_vector[-1-2*i]+b_vector[-1-i]
            if i<len(k_vector)-1:         
                b_vector[-i-2]=k_vector[-1-i]*x_vector[-1-2*i]+b_vector[-1-i]-k_vector[-1-i-1]*x_vector[-1-2*i-1]              
                if (x>=x_vector[2*i+1]) & (x<x_vector[2*i+2]):                              
                    return k_vector[-1-i-1]*x+b_vector[-1-i-1]

        return k_vector[0]*x_vector[0]+b_vector[0]   
    
    if (start_in_curve == False) & (end_in_curve == True):
        #print(k_vector, b_vector)
        b_vector = np.zeros((len(k_vector),))
        b_vector[0] = k0-k_vector[0]*x_start

        if x<x_vector[0]:
            return k_vector[0]*x+b_vector[0]

        for i in range(len(k_vector)-1):
            if (x>=x_vector[2*i]) & (x<x_vector[2*i+1]):
                return k_vector[i]*x_vector[2*i]+b_vector[i]
            if i<len(k_vector)-1:         
                b_vector[i+1]=k_vector[i]*x_vector[2*i]+b_vector[i]-k_vector[i+1]*x_vector[2*i+1]              
                if (x>=x_vector[2*i+1]) & (x<x_vector[2*i+2]):                              
                    return k_vector[i+1]*x+b_vector[i+1]
                
        return k_vector[-1]*x_vector[-1]+b_vector[-1] 
    
    if (start_in_curve == True) & (end_in_curve == True):
        return k_vector[0]     
    

# Поиск решения, удовлетворяющего условиям метода эвольвент с заданной точностью и пользовательским ограничениям на сдвижки
def build_project_plan_track(msv, L, x0_point, k0, k1, sdx, edx, constaints, ubound, lbound, tol=1e-2, maxiter=100, start_in_curve = False, end_in_curve = False):  
    #L-curve type
    Lx=2*L - int(start_in_curve) - int(end_in_curve)
    N=len(msv)
    
    def sq_linear_n(xs_vector):
        xx_vector=xs_vector[:Lx]
        kk_vector=xs_vector[Lx:]
        sm=0
        evm=0
        for js in range(N):
            sm+=(curve_pattern(js,np.copy(xx_vector),np.copy(kk_vector),N,k0,k1, sdx, edx, start_in_curve, end_in_curve)-msv[js])
            evm+=(N-js-1)*(curve_pattern(js,np.copy(xx_vector),np.copy(kk_vector),N,k0,k1, sdx, edx, start_in_curve, end_in_curve)-msv[js])
        return sm**2+evm**2 

    
    A=np.zeros((2*Lx-1,Lx+L))    
    for i in range(Lx):
        A[i,i]=1

    for i in range(Lx-1):
        A[Lx+i,i]=-1
        A[Lx+i,i+1]=1    
    
    if constaints == 0:  
        l_c=1
        u_c=N-2
    elif isinstance(constaints[0], (int, float)):
        constaints = np.array(constaints)/10
        l_c=np.ones((2*Lx-1,))
        u_c=(N-2)*np.ones((2*Lx-1,))
     
        l_c[0] = np.max([constaints[0][0], 1])
        u_c[0] = np.min([constaints[1][0], N-2])   
        for i in range(1,Lx-1,1):
            l_c[i] = l_c[0]
            u_c[i] = N-2          
        l_c[Lx-1] = np.max([N - 1 - constaints[1][-1], 1])
        u_c[Lx-1] = np.min([N - 1 - constaints[0][-1], N-2])
        for i in range(1,len(constaints[0])-1,1):
            l_c[Lx+2*i-1] = np.max([constaints[0][i], 1])
            u_c[Lx+2*i-1] = np.min([constaints[1][i], N-2]) 
                        
    else:
        constaints = np.array(constaints)/10  
        l_c=np.ones((2*Lx-1,))
        u_c=(N-2)*np.ones((2*Lx-1,))
     
        l_c[0] = np.max([constaints[0][0], 1])
        u_c[0] = np.min([constaints[1][0], N-2])   
        for i in range(1,Lx-1,1):
            l_c[i] = l_c[0]
            u_c[i] = N-2          
        l_c[Lx-1] = np.max([N - 1 - constaints[1][-1], 1])
        u_c[Lx-1] = np.min([N - 1 - constaints[0][-1], N-2])
        for i in range(1,len(constaints[0])-1,1):
            l_c[Lx+2*i-1] = np.max([constaints[0][i], 1])
            u_c[Lx+2*i-1] = np.min([constaints[1][i], N-2]) 
        
    linear_constraint = LinearConstraint(A, l_c, u_c)  
    
    def eq_cons(xs_vector):
        cons_f=list()
        xx_vector=xs_vector[:Lx]
        kk_vector=xs_vector[Lx:]
        evm=0
        sm=0        
        for js in range(N):
            sm+=(curve_pattern(js, np.copy(xx_vector), np.copy(kk_vector), N, k0, k1, sdx, edx, start_in_curve, end_in_curve)-msv[js])            
            evm+=(N-js-1)*(curve_pattern(js, np.copy(xx_vector), np.copy(kk_vector), N, k0, k1, sdx, edx, start_in_curve, end_in_curve)-msv[js])  
        cons_f.append(sm)
        cons_f.append(evm)
        return cons_f        
        
    def cons_f(xs_vector):
        xx_vector=xs_vector[:Lx]
        kk_vector=xs_vector[Lx:]
        cons_l=list()
        for j in range(N):
            evl=0
            for i in range(j):
                x_proekt = curve_pattern(i, np.copy(xx_vector), np.copy(kk_vector), N, k0, k1, sdx, edx, start_in_curve, end_in_curve) 
                diff_strel = msv[i] - x_proekt
                val = (j-i)*diff_strel
                evl = evl + val
            cons_l.append(ubound[j]/2 - evl)
            cons_l.append(evl - lbound[j]/2)   
        return np.array(cons_l)
    
    non_linear_constraint_0 = {'type': 'ineq', 'fun': lambda x: cons_f(x)}
    non_linear_constraint_1 = {'type': 'eq', 'fun': lambda x: eq_cons(x)}
    
    p = optimize.minimize(
        sq_linear_n, 
        x0=x0_point, 
        method='SLSQP', 
        tol=tol,        
        constraints=[linear_constraint, non_linear_constraint_0, non_linear_constraint_1],
        options={'maxiter': maxiter}
    )
    xf_vector=p.x[:Lx] 
    kf_vector=p.x[Lx:]
    bf_vector=np.zeros((len(kf_vector),))    
    sf_vector=np.zeros((len(kf_vector),))  
    bf_vector[0]=k0    
    sq=p.fun
    for i in range(len(kf_vector)):
        sf_vector[i]=kf_vector[i]*xf_vector[2*i]+bf_vector[i]  
        if i<len(kf_vector)-1:   
            bf_vector[i+1]=kf_vector[i]*xf_vector[2*i]+bf_vector[i]-kf_vector[i+1]*xf_vector[2*i+1]           
    xxf_vector=np.copy(xf_vector).astype(int)
    #print('------------------', p)
    return p,xf_vector,kf_vector,sf_vector,bf_vector,xxf_vector,sq

# Поиск решения, удовлетворяющего условиям метода эвольвент с заданной точностью с учетом изменения значений вектора k
def optimize_k(msv, L, x0_point, ubound, lbound, sdx, edx, opt_method,cons, tol=1e-2, maxiter=100, required_precision = 10e-6, max_time_condition_seconds = 3, start_in_curve = False, end_in_curve = False):
    #if cons != 0:
    #    cons[-1][:2*L] = list(np.array(cons[-1][:2*L]) + len(msv))

    class Trigger(Exception):
        pass

    class ObjectiveFunctionWrapper:
        def __init__(self, fun, fun_tol=None, time_start = None, max_time=None):
            self.fun = fun
            self.best_x = None
            self.time_start = time_start or None
            self.best_f = np.inf
            self.fun_tol = fun_tol or -np.inf
            self.max_time = max_time or np.inf        
            self.number_of_f_evals = 0
            self.opt_res = 0

        def __call__(self, x):
            _f, p_res = self.fun(x)
            
            self.number_of_f_evals += 1

            if _f < self.best_f:
                self.best_x, self.best_f, self.opt_res = x, _f, p_res

            return _f

        def stop(self, *args):
            u = (datetime.datetime.now()-self.time_start).seconds
            if self.best_f < self.fun_tol:
                print(f"Found f value below tolerance of {fun_tol} in {self.number_of_f_evals} f-evals and {u} seconds: k = {self.best_x}, f(x) = {self.best_f}")             
                raise Trigger               
            if u > self.max_time:
                #print(f"Time exceeded. Found f value in {self.number_of_f_evals} f-evals and {u} seconds:\
                #    \nx = {self.best_x}\
                #    \nf(x) = {self.best_f}")   
                raise Trigger          
    
    def sq_linear_n(k_vector): 
        if (start_in_curve == True) & (end_in_curve == True):        
            k0 = 0
            k1 = 0        
        if (start_in_curve == False) & (end_in_curve == True):        
            k0 = k_vector[0]
            k1 = 0 
        if (start_in_curve == True) & (end_in_curve == False):        
            k0 = 0
            k1 = k_vector[0]
        if (start_in_curve == False) & (end_in_curve == False):        
            k0 = k_vector[0]
            k1 = k_vector[1]  
            
        start_point=find_start_point(msv,L, start_in_curve, end_in_curve)
        SLSQP_initial_point,_ = find_optimization_initial_point(np.copy(msv), L, find_start_point(np.copy(msv), L, start_in_curve, end_in_curve), k0, k1, sdx, edx,
                                                                'SLSQP', maxiter=1000, start_in_curve = start_in_curve, end_in_curve = end_in_curve) 
        #q, xf_vector, kf_vector, sf_vector, bf_vector, xxf_vector, sq = build_project_plan_track(np.copy(msv), L, SLSQP_initial_point, k0, k1, sdx, edx, 0, ubound, lbound, tol=10e-5, maxiter=100)
        #cons = ([8,8,-100], [len(msv)-5, len(msv)-5,100])
        #cons = 0        
        q, xf_vector, kf_vector, sf_vector, bf_vector, xxf_vector, sq = build_project_plan_track(np.copy(msv), L, SLSQP_initial_point, k0, k1, sdx, edx, cons, ubound, lbound, tol=10e-5,
                                                                                                 maxiter=100, start_in_curve = start_in_curve, end_in_curve = end_in_curve)
        return q.fun, q 
    
    fBounds = Bounds(x0_point - 3, x0_point + 3)
    fun_tol = required_precision
    max_time = max_time_condition_seconds #in seconds
    f_wrapped = ObjectiveFunctionWrapper(sq_linear_n, fun_tol, datetime.datetime.now(), max_time)
    
    try:
        optimize.minimize(
        f_wrapped, 
        x0=x0_point, 
        method=opt_method,
        bounds=fBounds,
        tol=1e-4,
        options={'maxiter': 100},
        callback=f_wrapped.stop
    )
    except Trigger:
        pass
    except Exception as e:  # catch other errors
        raise e   
    #print(f_wrapped.opt_res)

    return f_wrapped.best_f, f_wrapped.best_x, f_wrapped.opt_res

# Функция, оптимизирующая начало и конец кривой
def optimize_msv(msv_rix, c_type, first_point_0, last_point_0, max_left_side_diap, max_right_side_diap, ubound, lbound, cons, req_precision, start_in_curve = False, end_in_curve = False):
    
    def objective(search_space):
        z1=first_point_0 - search_space["i"]
        z2=last_point_0 + search_space["j"] 

        if int(start_in_curve) + int(end_in_curve) == 2:
            k_start_point = np.array([0, 0])
        elif int(start_in_curve) + int(end_in_curve) == 1:
            k_start_point = np.array([0]) 
        else:
            k_start_point = np.array([0, 0])           
          
        loss,k_vals,opt_results = optimize_k(msv_rix[z1:z2+1], c_type, k_start_point, ubound[z1:z2+1], lbound[z1:z2+1], search_space["sdx"], search_space["edx"], 'SLSQP',
                                   cons, tol=1e-2, maxiter=100, required_precision = 1e-6, max_time_condition_seconds = 10, start_in_curve = start_in_curve, end_in_curve = end_in_curve)
        
        #print(search_space, loss)
        
        return {'loss': loss, 'k_vals': k_vals, 'sdx': search_space["sdx"], 'edx': search_space["edx"], 'msv': msv_rix[z1:z2+1], 'success': opt_results.success, 'opt_results': opt_results, 'status': STATUS_OK}

    def stop_func(*args):
        losses = args[0].losses()
        
        if losses[-1] < req_precision:
            return True, args
        return False, args
    
    trials = Trials()
    search_space = {"i": hp.randint('i', 0, max_left_side_diap + 1),
                    "j": hp.randint('j', 0, max_right_side_diap + 1),
                    "sdx": hp.uniform('sdx', -1, 0),
                    "edx": hp.uniform('edx', 0, 1)}
    #mx_evals= int(max_left_side_diap*max_right_side_diap/3)
    mx_evals= 10
    
    best_params = fmin(
        fn=objective, space=search_space, algo=hyperopt.anneal.suggest,#algo=tpe.suggest,
        max_evals=mx_evals, trials=trials, rstate=np.random.default_rng(42), verbose=False,
        early_stop_fn=stop_func
    )
    
    return trials

#Функция разбиения участка на прямые и кривые
def first_project_plan(msv, msv_rix, length_start, min_value, Rvalue, Rvalue2, d, L, ubound, lbound, NR_value = -1, stc = -1, max_number_of_radius = 5, min_quality = 20, find_good_solution = True, cons = [0], max_seconds_for_iteration = 30, token = SimpleToken()):
    length_start = int(length_start*0.185/d)
    i_num = -1
    
    ws_list=list()
    last_curve_end_point=-1
    i=-1
    count=0
    while i<len(msv)-length_start-1:
        i=i+1       
        #Проверяем начало кривой
        if np.min(np.abs(msv[i:i+length_start]))>=min_value:
            token.check()
            
            i_num += 1
            if len(cons) <= i_num:
                gcons = 0
            else:
                gcons = cons[i_num]
            
            znak=np.sign(np.mean(msv[i:i+length_start]))
            #Ищем конец кривой  
            for j in range(i+1,len(msv)):
                #if j==len(msv)-2:
                #    ws_list.append([c_type, [new_i, new_j], 2, [new_i, new_j]])
                #    return ws_list    
                
                if znak>0:
                    if msv[j]<Rvalue:
                        break
                if znak<=0:
                    if msv[j]>-Rvalue:
                        break          
            #Ищем максимальное значение для конца кривой
            
            for s in range(j+1,len(msv)): 
                if znak>0:
                    if msv[s]<-Rvalue2:
                        break
                if znak<=0:
                    if msv[s]>Rvalue2:
                        break      
                        
            if j+1 >= len(msv):
                s = len(msv)
                
            #Ищем начало кривой 
            hvalue=msv[i+length_start-1]            
            if hvalue>0:              
                for ii in range(i+length_start-1,-1,-1):   
                    if msv[ii]<Rvalue:                      
                        break    
            if hvalue<=0:                 
                for ii in range(i+length_start-1,-1,-1):   
                    if msv[ii]>-Rvalue:                       
                        break  
                        
            #Ищем минимальное значение для начала кривой
            if ii-1 <= 0:
                r = 0
            else:
                for r in range(ii-1,-1,-1): 
                    if hvalue>0:
                        if msv[r]<-Rvalue2:
                            break
                    if hvalue<=0:
                        if msv[r]>Rvalue2:
                            break   
                            
            #if stc == -1:
            #    start_in_curve = False
            #    end_in_curve = False                
            #else:
            #    start_in_curve = stc[i_num][0]
            #    end_in_curve = stc[i_num][0]
            
            start_in_curve = False
            end_in_curve = False 
            
            if (ii == 0) & (np.abs(msv[i]) > min_value):
                start_in_curve = True
                #continue
            if (j == len(msv) - 1) & (np.abs(msv[j]) > min_value): 
                end_in_curve = True
                #continue
            
            first_point_0 = np.ceil(ii*d/L).astype(int)
            last_point_0 = np.floor(j*d/L).astype(int)
            
            # if last_point_0 < first_point_0:
            #     last_point_0 = first_point_0

            last_val_first_point = np.floor(r*d/L).astype(int)
            last_val_last_point = np.ceil(s*d/L).astype(int)

            max_left_side_diap = np.max([np.min([first_point_0 - last_val_first_point + 1, first_point_0 - last_curve_end_point]), 1])
            max_right_side_diap = np.max([last_val_last_point - last_point_0 + 1, 1])
            
            if NR_value == -1:
                c_type, _ = find_curve_type(np.copy(msv_rix[first_point_0:last_point_0+1]),msv_rix[first_point_0],msv_rix[last_point_0], max_number_of_radius, min_quality,
                                        start_in_curve=start_in_curve, end_in_curve=end_in_curve)  
            else:
                c_type = NR_value[i_num]
            #c_type, _ = find_curve_type(np.copy(msv_rix[first_point_0:last_point_0+1]),0,0,20,35)  
            
            print('-------------------CURVE------------------------')
            print(f'By length {d}: First point: from {r} to {ii},\nLast point: from {j} to {s}')
            print(f'By length {L}: First point: from {first_point_0 - max_left_side_diap} to {first_point_0},\nLast point: from {last_point_0} to {last_point_0 + max_right_side_diap}\nEnd point of last curve:{last_curve_end_point}')
            print('---SEARCHING FOR SOLUTION...---')
            
            req_precision = 1e-6

            if int(start_in_curve) + int(end_in_curve) == 2:
                k_start_point = np.array([0, 0])
            elif int(start_in_curve) + int(end_in_curve) == 1:
                k_start_point = np.array([0]) 
            else:
                k_start_point = np.array([0, 0])    
            
            pre_opt_res = np.zeros((max_left_side_diap*max_right_side_diap, 4))
            ct=0
            for left_i in range(max_left_side_diap):
                for right_j in range(max_right_side_diap):
                    token.check()
                    if last_point_0 + right_j - first_point_0 + left_i <3:
                        pre_opt_res[ct,2] = np.inf 
                        ct+=1
                        continue
                    arr=msv_rix[first_point_0 - left_i : last_point_0 + right_j + 1]
                    pre_opt_res[ct,0]=left_i
                    pre_opt_res[ct,1]=right_j
                    if find_good_solution == True:
                        hx = optimize_k(arr, c_type, k_start_point, ubound[first_point_0 - left_i : last_point_0 + right_j + 1], lbound[first_point_0 - left_i : last_point_0 + right_j + 1], 0, 0, 'SLSQP',
                                                       gcons, tol=1e-2, maxiter=100, required_precision = req_precision, max_time_condition_seconds = max_seconds_for_iteration,
                                                       start_in_curve = start_in_curve, end_in_curve = end_in_curve)
                        hx_success = hx[2].success
                        if hx_success == True:
                            pre_opt_res[ct,2] = hx[0]
                        else:
                            pre_opt_res[ct,2] = np.inf                            
                    else:
                        pre_opt_res[ct,2] = np.inf
                    pre_opt_res[ct,3] = find_optimization_initial_point(arr, c_type, find_start_point(np.copy(arr), c_type, start_in_curve, end_in_curve), 0, 0, 0, 0, 'SLSQP', maxiter=1000,
                                                                        cons = True, start_in_curve = start_in_curve, end_in_curve = end_in_curve)[1]
                    ct+=1   
                    
            pre_opt_res=pd.DataFrame(pre_opt_res)
            pre_opt_res.columns=['i','j','val', 'sq_diff']
            pre_opt_res = pre_opt_res.sort_values(by='sq_diff')
            print('Results of initial optimization:\n',pre_opt_res)            
            pre_opt_res=np.array(pre_opt_res)
            
            #print(pre_opt_res.shape[0], pre_opt_res[:,2])
            
            if pre_opt_res[0,2]<req_precision:
                print('---SUCCESS! SOLUTION FOUND!---')
                new_i = int(first_point_0 - pre_opt_res[0,0])
                new_j = int(last_point_0 + pre_opt_res[0, 1]) + 1
                arr = msv_rix[new_i : new_j]
                res_best_f, res_arr, res_of_opt = optimize_k(arr, c_type, k_start_point, ubound[new_i : new_j], lbound[new_i : new_j], 0, 0, 'SLSQP',
                                     gcons, tol=1e-2, maxiter=100, required_precision = req_precision, max_time_condition_seconds = max_seconds_for_iteration,
                                                       start_in_curve = start_in_curve, end_in_curve = end_in_curve)
                next_i=np.ceil((new_j-1)*L/d).astype(int)
                ws_list.append([c_type, [new_i, new_j], 0, res_arr, start_in_curve, end_in_curve, res_of_opt])
            else:
                if find_good_solution == False:
                    print('---SOLUTION NOT FOUND!---')                    
                    new_i = int(first_point_0 - pre_opt_res[0, 0])
                    new_j = int(last_point_0 + pre_opt_res[0, 1]) + 1
                    arr = msv_rix[new_i : new_j]   
                    next_i=np.ceil((new_j-1)*L/d).astype(int)                    
                    ws_list.append([c_type, [new_i, new_j], 2, [new_i, new_j], start_in_curve, end_in_curve, -1])  
                else:
                    for c in tqdm(range(pre_opt_res.shape[0])):
                        token.check()
                        #if c==1:
                        #    continue
                        print("Try with first point = ", first_point_0 - pre_opt_res[c, 0], "and last point = ", last_point_0 + pre_opt_res[c, 1])
                        rs = optimize_msv(msv_rix, c_type, int(first_point_0 - pre_opt_res[c, 0]), int(last_point_0 + pre_opt_res[c, 1]), 0, 0, ubound, lbound, gcons, req_precision,
                                          start_in_curve=start_in_curve, end_in_curve=end_in_curve)
                        res = rs.best_trial['result'] 

                        if (res['loss'] < req_precision) & (res['success'] == True):
                            print('---SUCCESS! SOLUTION FOUND!---')
                            new_i = int(first_point_0 - pre_opt_res[c, 0])                          
                            new_j = int(last_point_0 + pre_opt_res[c, 1]) +1
                            next_i=np.ceil((new_j-1+res['edx'])*L/d).astype(int)
                            ws_list.append([c_type, [new_i, new_j], 1, rs, start_in_curve, end_in_curve, res['opt_results']])
                            break

                    if (res['loss'] > req_precision) | (res['success'] == False):
                        print('---SOLUTION NOT FOUND!---')
                        new_i = int(first_point_0 - pre_opt_res[0, 0])                   
                        new_j = int(last_point_0 + pre_opt_res[0, 1]) + 1
                        arr = msv_rix[new_i : new_j]    
                        next_i=np.ceil((new_j-1)*L/d).astype(int)
                        ws_list.append([c_type, [new_i, new_j], 2, [new_i, new_j], start_in_curve, end_in_curve, -1])
                                                    
            if j-ii<5:
                i=j
                continue    
            i=next_i
            last_curve_end_point=new_j-1
    print('-------------END OF CALCUCATION---------------')        
    return ws_list


#Нахождение значения заданной кусочно-линейной функции в произвольной точке для прямого участка
def straight_pattern(x, x_vector, s_vector, k0, k1):   
    
    if x<x_vector[0]:
        return k0  
    
    for i in range(len(x_vector)-1):
        if (x >= x_vector[i]) & (x < x_vector[i+1]):
            return s_vector[i]
        
    if x>=x_vector[-1]:
        return k1   

#Подбор плана прямого участка с учетом ограничений   
def build_straight_plan(msv, x0_point, xx_vector, k0, k1, ubound, lbound, tol=1e-2, maxiter=100, required_precision=1e-6, max_time_condition_seconds = 3):  
    #L-curve type
    Lx=len(xx_vector)-1
    N=len(msv)

    class Trigger(Exception):
        pass

    class ObjectiveFunctionWrapper:
        def __init__(self, fun, cons_1, cons_2, fun_tol=None, time_start = None, max_time=None):
            self.fun = fun
            self.cons_1 = cons_1   
            self.cons_2 = cons_2              
            self.best_x = None
            self.time_start = time_start or None
            self.best_f = np.inf
            self.fun_tol = fun_tol or -np.inf
            self.max_time = max_time or np.inf        
            self.number_of_f_evals = 0
            self.success = False
            
        def __call__(self, x):
            _f = self.fun(x)

            self.number_of_f_evals += 1

            if _f < self.best_f:
                self.best_x, self.best_f = x, _f

            return _f

        def stop(self, *args):
            u = (datetime.datetime.now()-self.time_start).seconds
            if (self.best_f < self.fun_tol) & (np.min(self.cons_1(self.best_x)) >= 0) & (np.min(self.cons_2(self.best_x)) >= 0):
                print(f"Found f value below tolerance of {fun_tol} in {self.number_of_f_evals} f-evals and {u} seconds: k = {self.best_x}, f(x) = {self.best_f}") 
                self.success = True
                raise Trigger               
            if u > self.max_time:
                #print(f"Time exceeded. Found f value in {self.number_of_f_evals} f-evals and {u} seconds: nx = {self.best_x}, nf(x) = {self.best_f}")   
                raise Trigger     
    
    def sq_linear_n(kk_vector):   
        sm=0
        evm=0
        for js in range(N):
            sm+=(straight_pattern(js,np.copy(xx_vector),np.copy(kk_vector),k0,k1)-msv[js])
            evm+=(N-js-1)*(straight_pattern(js,np.copy(xx_vector),np.copy(kk_vector),k0,k1)-msv[js])
        return sm**2+evm**2 

    
    A=np.zeros((2*Lx,Lx)) 
    l_c=np.zeros((2*Lx,))
    u_c=np.zeros((2*Lx,))    
    
    A[0, 0] = 1 
    l_c[0]= k0 - 5
    u_c[0]= k0 + 5         

    A[2*Lx-1, Lx-1] = 1 
    l_c[2*Lx-1]= k1 - 5
    u_c[2*Lx-1]= k1 + 5     
    
    for i in range(1, Lx):
        A[2*i-1,i-1]=-1
        A[2*i-1,i]=1                
        l_c[2*i-1]=-5
        u_c[2*i-1]=5    
        
        A[2*i,i-1]=1
        A[2*i,i]=-1                
        l_c[2*i]=-5
        u_c[2*i]=5          
    #print(A, l_c, u_c)
        
    linear_constraint = LinearConstraint(A, l_c, u_c)  
    
    def eq_cons(kk_vector):
        cons_f=list()
        evm=0
        sm=0        
        for js in range(N):         
            sm+=(straight_pattern(js,np.copy(xx_vector),np.copy(kk_vector),k0,k1)-msv[js])            
            evm+=(N-js-1)*(straight_pattern(js,np.copy(xx_vector),np.copy(kk_vector),k0,k1)-msv[js])  
        cons_f.append(sm)
        cons_f.append(evm)
        return cons_f        
        
    def cons_f(kk_vector):
        cons_l=list()
        for j in range(N):
            evl=0
            for i in range(j):
                x_proekt = straight_pattern(i, np.copy(xx_vector), np.copy(kk_vector),k0,k1) 
                diff_strel = msv[i] - x_proekt
                val = (j-i)*diff_strel
                evl = evl + val
            cons_l.append(ubound[j]/2-evl)
            cons_l.append(evl-lbound[j]/2)  
        return np.array(cons_l)

    def cons_k(kk_vector):
        cons_l=list()
        cons_l.append(kk_vector[0]-k0+5)
        cons_l.append(k0-kk_vector[0]+5)        
        for i in range(1,len(kk_vector)):
            cons_l.append(kk_vector[i]-kk_vector[i-1]+5)
            cons_l.append(kk_vector[i-1]-kk_vector[i]+5)
        cons_l.append(k1-kk_vector[-1]+5)    
        cons_l.append(kk_vector[-1]-k1+5)       
        return np.array(cons_l)    
    
    non_linear_constraint_0 = {'type': 'ineq', 'fun': lambda x: cons_f(x)}
    non_linear_constraint_1 = {'type': 'eq', 'fun': lambda x: eq_cons(x)}
    non_linear_constraint_2 = {'type': 'ineq', 'fun': lambda x: cons_k(x)}

    fun_tol = required_precision
    max_time = max_time_condition_seconds #in seconds
    f_wrapped = ObjectiveFunctionWrapper(sq_linear_n, cons_f, cons_k, fun_tol, datetime.datetime.now(), max_time)    
    
    try: 
        p = optimize.minimize(
            f_wrapped, 
            x0=x0_point, 
            method='SLSQP', 
            tol=tol,        
            #constraints=[linear_constraint, non_linear_constraint_0, non_linear_constraint_1],
            #bounds=(x0_point - 3, x0_point + 3),
            constraints=[non_linear_constraint_0, non_linear_constraint_1, non_linear_constraint_2],        
            options={'maxiter': maxiter},
            callback=f_wrapped.stop            
            )
    except Trigger:
        pass
    except Exception as e:  # catch other errors
        raise e  
    if f_wrapped.success == True:
        return f_wrapped.best_f, f_wrapped.best_x, f_wrapped.success
    else:
        return np.inf, x0_point, f_wrapped.success    
    
# Функция, оптимизирующая длины участков "прямой"
def optimize_straight(msv_rix, str_type, k0, k1, ubound, lbound, mx_evals, req_precision, token = SimpleToken()):
    
    def objective(search_space):
        token.check()
        z=np.zeros((str_type+1,))       
        for i in range(str_type+1):
            z[i]=search_space[f"x{i+1}"]            
        z=np.sort(z)
        print(z)
        
        x0_point = np.zeros((str_type, )) 
        p = build_straight_plan(msv_rix, x0_point, z, k0, k1, ubound, lbound, tol=1e-2, maxiter=100)
        
        #azy.append(straight_pattern(i, hyp_opt.results[-1]['z'], hyp_opt.results[-1]['p'].x, k0, k1))
        #return f_wrapped.best_f, f_wrapped.best_x, f_wrapped.success
        
        #print(search_space, loss)
        
        return {'loss': p[0], 'success': p[2], 'k': p[1], 'z' : z.astype(int), 'status': STATUS_OK}
        #return {'loss': p.fun, 'success': p.success, 'p': p, 'z' : z.astype(int), 'status': STATUS_OK}
        
    def stop_func(*args):
        losses = args[0].losses()
        if (losses[-1] < req_precision) & (args[0].results[-1]['success'] == True):
            return True, args
        return False, args
    
    trials = Trials()
    search_space=dict()
    for i in range(str_type+1):
        search_space[f'x{i+1}']=hp.randint(f'x{i+1}', 1, len(msv_rix) - 1)
    
    best_params = fmin(
        fn=objective, space=search_space, algo=hyperopt.anneal.suggest,#algo=tpe.suggest,
        max_evals=mx_evals, trials=trials, rstate=np.random.default_rng(42), verbose=False,
        early_stop_fn=stop_func
    )
    
    return trials

def count_curve_parametres(curve_data, curve_urov, curve_v, curve_type, p_points, start_point, a_np_max, calculation_for_profile, start_in_curve = False, end_in_curve=False): 
    # print(p_points, curve_type)
    points=np.copy(p_points)
    points[0] = 0
    points[-1] = curve_data.shape[0] -1     
    points = points.astype(int)
    #Записываем значения уровня на участке
    curve_data[:,16]=curve_urov
    #Записываем значения максимальной скорости на участке    
    curve_data[:,17]=curve_v
    #Расчет радиуса
    curve_data[:,18]=np.abs(50000/curve_data[:,10])
    #Расчет непогашенного ускорения    
    curve_data[:,19]=curve_data[:,17]**2/13/curve_data[:,18]-0.0061*curve_data[:,16]
    #Расчет максимально допустимой скорости
    curve_data[:,20]=(13*curve_data[:,18]*(0.0061*curve_data[:,16]+a_np_max))**0.5
    #Расчет минимального расчетного возвышения наружного рельса
    curve_data[:,21]=12.5*curve_data[:,17]**2/curve_data[:,18]-115

    l_p=list()
    mean_urov=list()
    v_max_p=list()
    dnp=list()
    
    if (start_in_curve == False) & (end_in_curve == False):
        for i in range(curve_type+1):
        #Расчет длин переходных кривых
            l_p.append(p_points[2*i+1]-p_points[2*i])
            mean_urov.append(np.mean(curve_data[points[2*i]:points[2*i+1]+1,16]))   
            v_max_p.append(np.max(curve_data[points[2*i]:points[2*i+1]+1,17]))
            #Расчет разности непогашенных ускорений в начале и конце переходной кривой
            dnp.append(curve_data[points[2*i+1],19]-curve_data[points[2*i],19])       
        
    if (start_in_curve == True) & (end_in_curve == False):
        for i in range(curve_type):
        #Расчет длин переходных кривых
            l_p.append(p_points[2*i+2]-p_points[2*i+1])
            mean_urov.append(np.mean(curve_data[points[2*i+1]:points[2*i+2]+1,16]))   
            v_max_p.append(np.max(curve_data[points[2*i+1]:points[2*i+2]+1,17]))
            #Расчет разности непогашенных ускорений в начале и конце переходной кривой
            dnp.append(curve_data[points[2*i+2],19]-curve_data[points[2*i+1],19])       
            
    if (start_in_curve == False) & (end_in_curve == True):
        for i in range(curve_type):
        #Расчет длин переходных кривых
            l_p.append(p_points[2*i+1]-p_points[2*i])
            mean_urov.append(np.mean(curve_data[points[2*i]:points[2*i+1]+1,16]))   
            v_max_p.append(np.max(curve_data[points[2*i]:points[2*i+1]+1,17]))
            #Расчет разности непогашенных ускорений в начале и конце переходной кривой
            dnp.append(curve_data[points[2*i+1],19]-curve_data[points[2*i],19])       

    if (start_in_curve == True) & (end_in_curve == True):
        for i in range(curve_type-1):
        #Расчет длин переходных кривых
            l_p.append(p_points[2*i+2]-p_points[2*i+1])
            mean_urov.append(np.mean(curve_data[points[2*i+1]:points[2*i+2]+1,16]))   
            v_max_p.append(np.max(curve_data[points[2*i+1]:points[2*i+2]+1,17]))
            #Расчет разности непогашенных ускорений в начале и конце переходной кривой
            dnp.append(curve_data[points[2*i+2],19]-curve_data[points[2*i+1],19])                
            
    l_p=10*np.array(l_p)
    mean_urov=np.array(mean_urov)
    v_max_p=np.array(v_max_p)
    dnp=np.array(dnp)     
        
    for i in range(len(l_p)):
        curve_data[i,22]=l_p[i]
        curve_data[i,23]=mean_urov[i]  
    #Расчет уклона отвода возвышения
        curve_data[i,24]=mean_urov[i]/l_p[i]
    #Расчет нарастания непогашенного ускорения
        curve_data[i,25]=dnp[i]*v_max_p[i]/3.6/l_p[i]           
    
    ac_plan=pd.DataFrame()
    ac_urov=pd.DataFrame()

    if calculation_for_profile == False: 
        if (start_in_curve == False) & (end_in_curve == False):        
            for i in range(curve_type+1):      
                x=pd.DataFrame(["Место [м]", 10*(p_points[2*i]+start_point), 
                                "Положение в плане: геометрия", "линейный",
                                "Положение в плане: длина[м]/радиус[м]", 10*(p_points[2*i+1]-p_points[2*i])])
                ac_plan=pd.concat([ac_plan,x.T])
                x=pd.DataFrame(["Место [м]", 10*(p_points[2*i]+start_point), 
                                "Возвышение: геометрия", "линейный",
                                "Возвышение: длина[м]/возвыш[мм]", 10*(p_points[2*i+1]-p_points[2*i])])  
                ac_urov=pd.concat([ac_urov,x.T])

                if i<curve_type:
                    alc, u_urov=find_R_to_alc(curve_data[points[2*i+1] + 1 : points[2*i+2] + 1, 10], 
                                              curve_data[points[2*i+1] + 1 : points[2*i+2] + 1, 16],
                                              p_points[2*i+1] + start_point, calculation_for_profile)         
                    ac_plan=pd.concat([ac_plan,alc])                 
                    ac_urov=pd.concat([ac_urov,u_urov])  
                    
        if (start_in_curve == True) & (end_in_curve == False):               
            for i in range(curve_type):      
                alc, u_urov=find_R_to_alc(curve_data[points[2*i] + 1 : points[2*i+1] + 1, 10], 
                                            curve_data[points[2*i] + 1 : points[2*i+1] + 1, 16],
                                            p_points[2*i] + start_point, calculation_for_profile)         
                ac_plan=pd.concat([ac_plan,alc])                 
                ac_urov=pd.concat([ac_urov,u_urov])  
                    
                x=pd.DataFrame(["Место [м]", 10*(p_points[2*i+1]+start_point), 
                                "Положение в плане: геометрия", "линейный",
                                "Положение в плане: длина[м]/радиус[м]", 10*(p_points[2*i+2]-p_points[2*i+1])])
                ac_plan=pd.concat([ac_plan,x.T])
                x=pd.DataFrame(["Место [м]", 10*(p_points[2*i+1]+start_point), 
                                "Возвышение: геометрия", "линейный",
                                "Возвышение: длина[м]/возвыш[мм]", 10*(p_points[2*i+2]-p_points[2*i+1])])  
                ac_urov=pd.concat([ac_urov,x.T])                    

        if (start_in_curve == False) & (end_in_curve == True):        
            for i in range(curve_type):      
                x=pd.DataFrame(["Место [м]", 10*(p_points[2*i]+start_point), 
                                "Положение в плане: геометрия", "линейный",
                                "Положение в плане: длина[м]/радиус[м]", 10*(p_points[2*i+1]-p_points[2*i])])
                ac_plan=pd.concat([ac_plan,x.T])
                x=pd.DataFrame(["Место [м]", 10*(p_points[2*i]+start_point), 
                                "Возвышение: геометрия", "линейный",
                                "Возвышение: длина[м]/возвыш[мм]", 10*(p_points[2*i+1]-p_points[2*i])])  
                ac_urov=pd.concat([ac_urov,x.T])

                if i<curve_type:
                    alc, u_urov=find_R_to_alc(curve_data[points[2*i+1] + 1 : points[2*i+2] + 1, 10], 
                                              curve_data[points[2*i+1] + 1 : points[2*i+2] + 1, 16],
                                              p_points[2*i+1] + start_point, calculation_for_profile)         
                    ac_plan=pd.concat([ac_plan,alc])                 
                    ac_urov=pd.concat([ac_urov,u_urov])                     

        if (start_in_curve == True) & (end_in_curve == True):        
            for i in range(curve_type):      
                alc, u_urov=find_R_to_alc(curve_data[points[2*i] + 1 : points[2*i+1] + 1, 10], 
                                            curve_data[points[2*i] + 1 : points[2*i+1] + 1, 16],
                                            p_points[2*i] + start_point, calculation_for_profile)         
                ac_plan=pd.concat([ac_plan,alc])                 
                ac_urov=pd.concat([ac_urov,u_urov])  

                if i<curve_type-1:
                    x=pd.DataFrame(["Место [м]", 10*(p_points[2*i+1]+start_point), 
                                    "Положение в плане: геометрия", "линейный",
                                    "Положение в плане: длина[м]/радиус[м]", 10*(p_points[2*i+2]-p_points[2*i+1])])
                    ac_plan=pd.concat([ac_plan,x.T])
                    x=pd.DataFrame(["Место [м]", 10*(p_points[2*i+1]+start_point), 
                                    "Возвышение: геометрия", "линейный",
                                    "Возвышение: длина[м]/возвыш[мм]", 10*(p_points[2*i+2]-p_points[2*i+1])])  
                    ac_urov=pd.concat([ac_urov,x.T])                      
                    
    if calculation_for_profile == True:            
        x=pd.DataFrame(["Место [м]", 10*(p_points[0]+start_point), 
                        "Уровень: геометрия", "Перелом профиля/R",
                        "Радиус сопряжения",  50000/np.mean(curve_data[points[0]:points[-1]+1,10]),
                        "Длина (м)", 10*(p_points[-1]-p_points[0]),
                        "Уклон (ppt)", "-"])    
        ac_plan=x.T
        ac_urov=pd.DataFrame()
            
    return curve_data, ac_plan, ac_urov
 
def find_R_to_alc(straight, urov, start, calculation_for_profile):
    alc=pd.DataFrame()    
    alc_urov=pd.DataFrame()      
    u=10**100
    
    if calculation_for_profile == False:
        for i in range(len(straight)):
            if np.abs(straight[i]-u)>10**-4: 
                h=pd.DataFrame(["Место [м]", 10*(start+i), 
                            "Положение в плане: геометрия", "радиус",
                            "Положение в плане: длина[м]/радиус[м]", 50000/straight[i]])
                alc=pd.concat([alc,h.T]) 
                u=straight[i]

        straight=straight.tolist()
        straight.append(10**100)

        ui=0  
        u=straight[0]    
        for i in range(1,len(straight)):   
            if np.abs(straight[i]-u)>10**-4:             
                hx=pd.DataFrame(["Место [м]", 10*(start+ui), 
                            "Возвышение: геометрия", "возвышение",
                            "Возвышение: длина[м]/возвыш[мм]", np.mean(urov[ui:i])])               
                alc_urov=pd.concat([alc_urov,hx.T])                         
                ui=i
                u=straight[i]     
                
    if calculation_for_profile == True:
        ui=0  
        u=straight[0]         
        for i in range(1,len(straight)):
            if np.abs(straight[i]-u)>10**-4: 
                h=pd.DataFrame(["Место [м]", 10*(start+ui), 
                            "Уровень: геометрия", "Перелом профиля/R",
                            "Радиус сопряжения", 50000/u,
                            "Длина (м)", 10*(i-ui),
                            "Уклон (ppt)", "-"])    
                alc=pd.concat([alc,h.T]) 
                ui=i
                u=straight[i]

        straight=straight.tolist()
        straight.append(10**100)
                
    return alc, alc_urov   

def change_plan(f, p, popravki_value, upper_bound, lower_bound, min_length_from_start_end, koeff, kfv):
    n=len(f)  
    EV_table=np.zeros((n,42))
    EV_table[:,0]=f
    EV_table[:,1]=p
    EV_table[:,2]=f-p
    EV_table[0,3]=EV_table[0,2]
    for i in range(1,n):
        EV_table[i,3]=EV_table[i-1,3]+EV_table[i,2]
    EV_table[0,4]=0
    EV_table[1,4]=EV_table[0,3]
    for i in range(2,n):
        EV_table[i,4]=EV_table[i-1,4]+EV_table[i-1,3]    
    ub=EV_table[:,4]+upper_bound/2
    lb=EV_table[:,4]+lower_bound/2
    EV_table[:,14]=ub
    EV_table[:,15]=lb

    if kfv == -1:
        fv = EV_table[:,4]
    else:
        fv = kfv*ub + (1-kfv)*lb    
    
    s_point_1=min_length_from_start_end
    e_point_1=n-min_length_from_start_end-1  
    s_point_2=0
    e_point_2=n-1 
    
    M_coord_2=0      
    K_coord_2=EV_table[n-1,4]     
    
    for i in range(n):
        if (ub[i]<0) | (lb[i]>0):
            break  
    sp=i-1    
               
    for i in range(n-1,0,-1):
        if (ub[i] < EV_table[n-1,4]) | (lb[i] > EV_table[n-1,4]):
            break 
    ep=i+1
    
    kf=0
   
    
    if (sp>=n-3) & (ep<=2):
        start_point=int(n/3)
        end_point=int(2*n/3)
        M_coord_1=start_point-1
        K_coord_1=end_point+1     
        
    elif sp>=ep:
        if ep<=2: 
            start_point=int(sp/2)
            end_point=sp        
            
        elif sp>=n-3:   
            start_point=ep
            end_point=ep+int((n-1-ep)/2)   
            
        else:
            start_point=sp
            end_point=start_point+1

        M_coord_1=start_point-1        
        K_coord_1=end_point+1      
    
    else:   
        kf=koeff
        for j in range(sp,0,-1):
            if fv[j]*fv[j-1]<0:
                s_point_2=j
                break
        print(sp, s_point_1, s_point_2)    
        
        if s_point_1 >= sp:
            start_point = s_point_1
        else:
            if s_point_1 >= s_point_2:
                start_point = sp
            else:
                start_point = s_point_2
        M_coord_1=start_point-1


        for j in range(ep,n-1):
            if (fv[j]-fv[n-1])*(fv[j+1]-fv[n-1])<0:
                e_point_2=j    
                break
                           
                
        if e_point_1 <= ep:
            end_point = e_point_1
        else:
            if e_point_1 <= e_point_2:
                end_point = ep
            else:
                end_point = e_point_2   
        #end_point = end_point-1    
        
        if start_point > end_point-1:
            start_point = end_point-1
            
        K_coord_1=end_point+1  
 
    print(start_point, end_point)
    
    dimG=end_point-start_point+1
    G=calculate_Graph(fv, ub, lb, start_point, end_point, M_coord_1, M_coord_2, K_coord_1, K_coord_2, dimG, kf)
  
    #G=calculate_Graph((ub+lb)/2,EV_table[:,4],ub,lb,start_point,end_point,M_coord_1,M_coord_2,K_coord_1,K_coord_2,dimG,kf)    
    H,p_num=Dijkstra(G)

    VH=np.zeros((len(H),))
    VH_label=np.zeros((len(H),))
    V_Coord=np.zeros((len(H),))
    #print(start_point,end_point,EV_table.shape[0],dimG,H,p_num)
    for i in range(len(H)):
        VH[i]=H[i]  
    V=np.flip(VH.astype(int))+start_point-1

    for i in range(len(V)):
        V_Coord[i]=fv[V[i]]
        #V_Coord[i]=EV_table[V[i],4]
           
    V_Coord[0]=M_coord_2
    V_Coord[-1]=K_coord_2                
    for i in range(len(V)):
        EV_table[V[i],5]=V_Coord[i]
        EV_table[V[0],6]=0
    EV_table[start_point-1,5]=0.000001
    for i in range(1,len(V)):
        EV_table[V[i],6]=(V_Coord[i]-V_Coord[i-1])/(V[i]-V[i-1])
    for i in range(len(V)-1):
        EV_table[V[i],7]=EV_table[V[i+1],6]-EV_table[V[i],6]
    EV_table[V[-1],7]=-EV_table[V[-1],6]

    if popravki_value == 0:
        EV_table[:,9]=EV_table[:,7]
    else:
        EV_table[:,9]=distr_popravki(EV_table[:,7],popravki_value)

    EV_table[:,10]=EV_table[:,1]+EV_table[:,9]
    EV_table[:,11]=f-EV_table[:,10]
    EV_table[0,12]=EV_table[0,11]
    for i in range(1,n):
        EV_table[i,12]=EV_table[i-1,12]+EV_table[i,11]
    EV_table[0,13]=0
    EV_table[1,13]=EV_table[0,12]
    for i in range(2,n):
        EV_table[i,13]=EV_table[i-1,13]+EV_table[i-1,12] 
    EV_table[:,13]=2*EV_table[:,13]
    return EV_table

def G_elements_calculate(x1,y1,x2,y2,evmx,ub,lb,kf):

    mx=np.zeros((len(evmx),))
    k=(y2-y1)/(x2-x1)
    b=y1-k*x1
    for i in range(x1,x2+1):
        mx[i]=k*i+b
    dmx=np.abs(mx-evmx)/(ub-evmx)    

    x=1+kf*np.sum(dmx[x1:x2+1])#/(x2-x1)+kf3*(x2-x1)
  
    #x=1
    #x=((x1-x2)**2+(y1-y2)**2)**0.5    
    return x

def calculate_Graph(Evl,ub,lb,start_point,end_point,M_coord_1,M_coord_2,K_coord_1,K_coord_2,dimG,kf):
    G=100*np.ones((dimG+2,dimG+2))
    GG=np.zeros((dimG,dimG))
    GM=np.zeros((dimG,))
    GK=np.zeros((dimG,))
    GMK=0
    
    #GG calculating
    for i in range(start_point,end_point+1):
        for j in range(i+1,end_point+1):
            cross=0
            for k in range(i+1,j):
                a=(Evl[i]-Evl[j])/(i-j)
                b=(i*Evl[j]-j*Evl[i])/(i-j)
                z=a*k+b
                if (z>ub[k]) | (z<lb[k]):
                    cross=1
                    break
            if cross==0:
                GG[i-start_point,j-start_point]=G_elements_calculate(i,Evl[i],j,Evl[j],Evl,ub,lb,kf)
                GG[j-start_point,i-start_point]=GG[i-start_point,j-start_point]

    #GM calculating
    for i in range(start_point,end_point+1):
        cross=0
        for k in range(start_point,i):
            a=(Evl[i]-M_coord_2)/(i-M_coord_1)
            b=(i*M_coord_2-M_coord_1*Evl[i])/(i-M_coord_1)
            z=a*k+b
            if (z>ub[k]) | (z<lb[k]):
                cross=1
                break
        if cross==0:
            GM[i-start_point]=G_elements_calculate(M_coord_1,M_coord_2,i,Evl[i],Evl,ub,lb,kf)

    #GK calculating
    for i in range(start_point,end_point+1):
        cross=0
        for k in range(i+1,end_point+1):
            a=(Evl[i]-K_coord_2)/(i-K_coord_1)
            b=(i*K_coord_2-K_coord_1*Evl[i])/(i-K_coord_1)
            z=a*k+b
            if (z>ub[k]) | (z<lb[k]):
                cross=1
                break
        if cross==0:
            GK[i-start_point]=G_elements_calculate(i,Evl[i],K_coord_1,K_coord_2,Evl,ub,lb,kf)        
      
    #GMK calculating
    cross=0
    for k in range(start_point,end_point+1):
        a=(M_coord_2-K_coord_2)/(M_coord_1-K_coord_1)
        b=(M_coord_1*K_coord_2-K_coord_1*M_coord_2)/(M_coord_1-K_coord_1)
        z=a*k+b
        if (z>ub[k]) | (z<lb[k]):
            cross=1
            break
    if cross==0:
        GMK=G_elements_calculate(M_coord_1,M_coord_2,K_coord_1,K_coord_2,Evl,ub,lb,kf)     

    #fill G  
    G[0,0]=0
    G[dimG+1,dimG+1]=0  
    G[0,dimG+1]=GMK
    G[dimG+1,0]=GMK  

    G[1:dimG+1,0]=GM
    G[0,1:dimG+1]=GM    
    G[1:dimG+1,dimG+1]=GK
    G[dimG+1,1:dimG+1]=GK

    G[1:dimG+1,1:dimG+1]=GG
    #print(G)
    return G

def Dijkstra(Graph):
    L=len(Graph)
    GL=10**10*np.ones((L,))
    GL_Visited=np.zeros((L,))  
    GP=np.ones((L,))
    GL[0]=0
    while np.sum(GL_Visited)<L:
        minWeight=10**11
        minWeight_NUM=0
        for i in range(L):
            if (GL_Visited[i]==0) & (GL[i]<minWeight):
                minWeight=GL[i]
                minWeight_NUM=i
        GL_Visited[minWeight_NUM]=1
        for i in range(L):
            if Graph[minWeight_NUM,i]>0:
                if GL[minWeight_NUM]+Graph[minWeight_NUM,i]<GL[i]:
                    GL[i]=GL[minWeight_NUM]+Graph[minWeight_NUM,i]
                    GP[i]=minWeight_NUM
                    

    Path=(L-1)*np.ones((L,))
    w=0
    i=L-1
    while i>0:
        i=int(GP[i])
        w=w+1
        Path[w]=i
    result=GL[L-1]
    
#    print(Path[:np.argmin(Path)+1],int(result))
    return Path[:np.argmin(Path)+1],int(result)  

def distr_popravki(popravki,max_val):
    dp=np.zeros((len(popravki),))
    for i in range(len(popravki)):
        if np.abs(popravki[i])>0:
            kf=int(np.ceil(np.abs(popravki[i])/max_val/2))  
            
            if (i-kf>=0) & (i+kf<len(popravki)):
                for j in range(i-kf,i+kf+1):
                    dp[j]=dp[j]+popravki[i]/(2*kf+1)
            
            elif (i-kf<0) & (i+kf>=len(popravki)): 
                if 2*i>len(popravki)-1:
                    for j in range(2*i+1-len(popravki),len(popravki)):
                        dp[j]=dp[j]+popravki[i]/(2*len(popravki)-2*i-1)                       
                else:
                    for j in range(2*i+1):
                        dp[j]=dp[j]+popravki[i]/(2*i+1)                   
            
            elif i-kf<0: 
                for j in range(2*i+1):
                    dp[j]=dp[j]+popravki[i]/(2*i+1)    
            
            elif i+kf>=len(popravki): 
                for j in range(2*i+1-len(popravki),len(popravki)):
                    dp[j]=dp[j]+popravki[i]/(2*len(popravki)-2*i-1)                 
    return dp


# Обработка данных, полученных после разбиения участка на прямые и кривые
def track_calculation(initial_array, initial_urov, initial_v, ax, ubound, lbound, count_urov = -1, curve_urov = -1, kfv = -1, calc_type = [1], mx_evals = 1, min_iterations_straight = 3, max_iterations_straight = 6, save_to_csv = False, token = SimpleToken()):
    EV=pd.DataFrame()
    alc_plan = pd.DataFrame()
    alc_urov = pd.DataFrame()
    track_split = list()
    new_track_split = list()
    
    last_j = 0
    last_edx = 0
    last_k1 = 0
    if len(ax) == 0:
        EV_straight, ac_plan, ac_urov = straight_processing(initial_array, initial_urov, initial_v, 0, 0, 0, 0, ubound, lbound, 0, 0, kfv, req_precision = 1e-6, count_urov=count_urov,
                                                            min_iterations = min_iterations_straight, max_iterations = max_iterations_straight,
                                                            calc_type = calc_type[0], mx_evals = mx_evals, save_to_csv = save_to_csv)
        #track_split.append(['прямая', 0, 10*len(initial_array) - 10])
        new_track_split.append(['прямая', 0, 10*len(initial_array) - 10, 0, 0])        
        return EV_straight, ac_plan, ac_urov, pd.DataFrame(new_track_split)
    
    for curve_num in tqdm(range(len(ax))):
        token.check()
        curve_type=ax[curve_num][0]
        new_i=ax[curve_num][1][0]
        new_j=ax[curve_num][1][1]
        msv=initial_array[new_i : new_j]
        urov_msv=initial_urov[new_i : new_j]
        v_msv=initial_v[new_i : new_j]  
        start_in_curve = ax[curve_num][4]
        end_in_curve = ax[curve_num][5]
        
        #Решение найдено функцией optimize_k (алгоритм SLSQP)
        if ax[curve_num][2] == 0:    
            if (start_in_curve == False) & (end_in_curve == False):
                k0 = ax[curve_num][3][0]
                k1 = ax[curve_num][3][1] 
            if (start_in_curve == False) & (end_in_curve == True):
                k0 = ax[curve_num][3][0]
                k1 = 0
            if (start_in_curve == True) & (end_in_curve == False):
                k0 = 0
                k1 = ax[curve_num][3][0]
            if (start_in_curve == True) & (end_in_curve == True):
                k0 = 0
                k1 = 0
            sdx=0
            edx=0
            
        #Решение найдено функцией optimize_msv(алгоритм hyperopt)    
        if ax[curve_num][2] == 1:
            res=ax[curve_num][3].best_trial['result']
            if (start_in_curve == False) & (end_in_curve == False):
                k0 = res['k_vals'][0]
                k1 = res['k_vals'][1]
            if (start_in_curve == False) & (end_in_curve == True):
                k0 = res['k_vals'][0]
                k1 = 0
            if (start_in_curve == True) & (end_in_curve == False):
                k0 = 0
                k1 = res['k_vals'][0]
            if (start_in_curve == True) & (end_in_curve == True):
                k0 = 0
                k1 = 0

            sdx=res['sdx']
            edx=res['edx']  
            
        #Решение не найдено
        if ax[curve_num][2] == 2:
            k0=0
            k1=0
            sdx=0
            edx=0    

        if curve_num >= len(calc_type):
            calc_type_value = -1
        else:
            calc_type_value = curve_num     
                     
        if curve_num == 0:
            stp = 0
            track_split.append(['прямая', 0, 10*(new_i + sdx)])     
            new_track_split.append(['прямая', 0, 10*(new_i + sdx), last_k1, k0])              
        else:
            stp = last_j + edx - 1
            track_split.append(['прямая', 10*(last_j + edx - 1), 10*(new_i + sdx)])
            new_track_split.append(['прямая', 10*(last_j + edx - 1), 10*(new_i + sdx), last_k1, k0])            
            
        EV_straight, ac_plan, ac_urov = straight_processing(initial_array[last_j : new_i], initial_urov[last_j : new_i], initial_v[last_j : new_i], last_k1, k0, last_edx - 1, 1 + sdx, 
                                                            ubound[last_j : new_i], lbound[last_j : new_i], stp, curve_num, kfv, req_precision = 1e-6, count_urov=count_urov,
                                                            min_iterations = min_iterations_straight, max_iterations = max_iterations_straight,
                                                            calc_type = calc_type[calc_type_value], mx_evals = mx_evals, save_to_csv = save_to_csv)
        
#        EV_straight, ac_plan, ac_urov = straight_processing(initial_array[last_j : new_i], initial_urov[last_j : new_i], initial_v[last_j : new_i], last_k1, k0, last_edx - 1, 1 + sdx, 
#                                                            ubound[last_j : new_i], lbound[last_j : new_i], last_j, curve_num, kfv, req_precision = 1e-6, count_urov=count_urov,
#                                                            calc_type = calc_type[calc_type_value], mx_evals = mx_evals, save_to_csv = save_to_csv)      

        EV=pd.concat([EV, EV_straight])   
        alc_plan=pd.concat([alc_plan, ac_plan]) 
        alc_urov=pd.concat([alc_urov, ac_urov])
        
        EV_curve, ac_plan, ac_urov = curve_processing(msv, urov_msv, v_msv, curve_type, ax[curve_num][2], ax[curve_num][6], k0, k1, sdx, edx, ubound[new_i : new_j], lbound[new_i : new_j], new_i, curve_num, kfv,
                                                      save_to_csv = save_to_csv, start_in_curve = start_in_curve, end_in_curve = end_in_curve)
        
        new_track_split.append(['кривая', 10*(new_i + sdx), 10*(new_j + edx - 1), k0, k1]) 
        
        first_per_index = 0
        for i in range(ac_plan.shape[0]):
            if ac_plan[ac_plan.columns[3]].iloc[i] == 'линейный':
                first_per_index = i    
                break
                
        last_per_index = 0
        #last_per_value = 0
        for i in range(ac_plan.shape[0]):
            if ac_plan[ac_plan.columns[3]].iloc[i] == 'линейный':
                last_per_index = i
                
        last_per_value = None
        for i in range(ac_plan.shape[0]):
            if ac_plan[ac_plan.columns[3]].iloc[i] == 'линейный':
                if i == first_per_index:
                    if first_per_index > 0:
                        track_split.append(['круговая кривая', ac_plan[ac_plan.columns[1]].iloc[0], ac_plan[ac_plan.columns[1]].iloc[i]])
                else:
                    track_split.append(['круговая кривая', last_per_value, ac_plan[ac_plan.columns[1]].iloc[i]])
                    
                last_per_value = ac_plan[ac_plan.columns[1]].iloc[i] + ac_plan[ac_plan.columns[5]].iloc[i]
                track_split.append(['переходная кривая', ac_plan[ac_plan.columns[1]].iloc[i], last_per_value])
                
            if (i == last_per_index) & (last_per_index < ac_plan.shape[0] - 1):
                track_split.append(['круговая кривая', ac_plan[ac_plan.columns[1]].iloc[i+1], new_j - 1 + edx])             
        #track_split.append(['кривая', new_i + sdx, new_j - 1 + edx])
        
        if curve_urov != -1:
            ac_urov[ac_urov.columns[5]][ac_urov[ac_urov.columns[3]] == 'возвышение'] = curve_urov[curve_num]
            #print(ac_plan)
        EV=pd.concat([EV, EV_curve]) 
        alc_plan=pd.concat([alc_plan, ac_plan]) 
        alc_urov=pd.concat([alc_urov, ac_urov])
        last_j = new_j
        last_edx = edx
        last_k1 = k1     
        
    if curve_num + 1 >= len(calc_type):
        calc_type_value = -1
    else:
        calc_type_value = curve_num + 1
        
    EV_straight, ac_plan, ac_urov = straight_processing(initial_array[new_j : ], initial_urov[new_j : ], initial_v[new_j : ], k1, 0, edx - 1, 0,
                                                        ubound[new_j : ], lbound[new_j : ], new_j + edx - 1, curve_num + 1, kfv, req_precision = 1e-6, count_urov=count_urov,
                                                        min_iterations = min_iterations_straight, max_iterations = max_iterations_straight,
                                                        calc_type = calc_type[calc_type_value], mx_evals = mx_evals, save_to_csv = save_to_csv)
#    EV_straight, ac_plan, ac_urov = straight_processing(initial_array[new_j : ], initial_urov[new_j : ], initial_v[new_j : ], k1, 0, edx - 1, 0,
#                                                        ubound[new_j : ], lbound[new_j : ], new_j, curve_num + 1, kfv, req_precision = 1e-6, count_urov=count_urov,
#                                                        calc_type = calc_type[calc_type_value], mx_evals = mx_evals, save_to_csv = save_to_csv)

    track_split.append(['прямая', 10*(new_j + edx - 1), 10*(len(initial_array) - 1)])
    new_track_split.append(['прямая', 10*(new_j + edx - 1), 10*(len(initial_array) - 1), k1, 0])    
    EV=pd.concat([EV, EV_straight])
    alc_plan=pd.concat([alc_plan, ac_plan]) 
    alc_urov=pd.concat([alc_urov, ac_urov]) 
      
    EV = count_new_params(EV.copy(), alc_urov.copy())
    
    return EV, alc_plan, alc_urov, pd.DataFrame(new_track_split)


def count_new_params(EV_msv, alc_uroven=None):
    EV_msv = np.array(EV_msv)
    
    #Записываем значения возвышения наружного рельса из ALC-формата
    if alc_uroven is not None:
        EV_msv[:, 29] = alc_urov_to_10(alc_uroven, EV_msv.shape[0])
    
    for i in range(EV_msv.shape[0]):
        #Изменение длины рельса
        EV_msv[i, 26] = 0.00002*EV_msv[i, 13]*10*EV_msv[i, 10]
        
        #Изменение температуры закрепления
        EV_msv[i, 27] = EV_msv[i, 13]*EV_msv[i, 10]/0.0118/50000
        
        #Потребность в балласте
        #EV_msv[i, 28] =
        
        #Половина длины хорды 10+10
        a_str = 10
        #Непогашенное ускорение для натурных стрел
        EV_msv[i, 30] = EV_msv[i, 17]**2/6480/a_str**2*EV_msv[i, 0] - EV_msv[i, 16]/163

        #Непогашенное ускорение для проектных стрел 
        EV_msv[i, 33] = EV_msv[i, 17]**2/6480/a_str**2*EV_msv[i, 10] - EV_msv[i, 29]/163               
            
        
        if i>0:
            #Скорость нарастания непогашенного ускорения для натурных стрел
            EV_msv[i, 31] = EV_msv[i, 17]/3.6/a_str*(EV_msv[i, 30] - EV_msv[i-1, 30])
            #Скорость подъема колеса на возвышение наружного рельса для натурных стрел
            EV_msv[i, 32] = EV_msv[i, 17]/3.6/a_str*(EV_msv[i, 16] - EV_msv[i-1, 16])
            #Скорость нарастания непогашенного ускорения для проектных стрел
            EV_msv[i, 34] = EV_msv[i, 17]/3.6/a_str*(EV_msv[i, 33] - EV_msv[i-1, 33])  
            #Скорость подъема колеса на возвышение наружного рельса для проектных стрел
            EV_msv[i, 35] = EV_msv[i, 17]/3.6/a_str*(EV_msv[i, 29] - EV_msv[i-1, 29])            
        else:    
            EV_msv[i, 31] = EV_msv[i, 17]/3.6/a_str*EV_msv[i, 30]
            EV_msv[i, 32] = EV_msv[i, 17]/3.6/a_str*EV_msv[i, 16]
            EV_msv[i, 34] = EV_msv[i, 17]/3.6/a_str*EV_msv[i, 33] 
            EV_msv[i, 35] = EV_msv[i, 17]/3.6/a_str*EV_msv[i, 29]
        
    return pd.DataFrame(EV_msv)

#Функция расчета прямых
# msv -- натурные данные в плане
# urov_msv -- уровень 
# v_msv -- скорость
# k0 -- стрела в конце предыдущей кривой (из track_split)
# k1 -- стрела в начале следующей кривой (из track_split)
# sdx = 0
# edx = 0
# ubound, lbound -- ограничения 
# start_point -- началj прямого участка / 10
# straight_num -- номер прямого участка
# kfv = -1
def straight_processing(msv, urov_msv, v_msv, k0, k1, sdx, edx, ubound, lbound, start_point, straight_num, kfv, req_precision = 1e-6, count_urov = -1, min_iterations = 3, max_iterations = 6, calc_type = 1, mx_evals = 1, save_to_csv = False):
    print("---------------РАСЧЕТ ПРЯМОГО УЧАСТКА №", straight_num, 'ДЛИНА УЧАСТКА', len(msv))    
    res_found = False
    print(msv, k0, k1, sdx, edx)
    

    if len(msv)==0: 
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame() 
    
    if calc_type == 1:
        if len(msv)>5:            
            for straight_type in tqdm(range(min_iterations, np.min([max_iterations, len(msv) - 3]))):
                #print(msv.shape[0], ubound.shape[0], lbound.shape[0])
                hyp_opt = optimize_straight(np.copy(msv), straight_type, k0, k1, ubound, lbound, mx_evals, 1e-6)
                #print(hyp_opt.results[-1]['p'], hyp_opt.results[-1]['p'].success, )

                #if (hyp_opt.results[-1]['p'].success == True) & (hyp_opt.results[-1]['p'].fun < req_precision):
                if (hyp_opt.results[-1]['success'] == True) & (hyp_opt.results[-1]['loss'] < req_precision):                
                    res_found = True             
                    break   

            if res_found == True:
                #print("___________________________________SUCCESS_________________________, x=", hyp_opt.results[-1]['z'], ', k=', k0, hyp_opt.results[-1]['p'].x, k1)
                print("___________________________________SUCCESS_________________________, x=", hyp_opt.results[-1]['z'], ', k=', k0, hyp_opt.results[-1]['k'], k1)            
                azy=list()
                for i in range(len(msv)):
                    azy.append(straight_pattern(i, hyp_opt.results[-1]['z'], hyp_opt.results[-1]['k'], k0, k1))
                    #azy.append(straight_pattern(i, hyp_opt.results[-1]['z'], hyp_opt.results[-1]['p'].x, k0, k1))
                azy=np.array(azy)

                EV_table=np.zeros((len(msv),42))

                EV_table[:,0]=msv
                EV_table[:,1]=azy
                EV_table[:,2]=EV_table[:,0]-EV_table[:,1]
                EV_table[0,3]=EV_table[0,2]
                for i in range(1,len(msv)):
                    EV_table[i,3]=EV_table[i-1,3]+EV_table[i,2]
                EV_table[0,4]=0
                EV_table[1,4]=EV_table[0,3]
                for i in range(2,len(msv)):
                    EV_table[i,4]=EV_table[i-1,4]+EV_table[i-1,3] 
                EV_table[:,4]=2*EV_table[:,4]

                EV_table[:,10]=EV_table[:,1]  
                EV_table[:,13]=EV_table[:,4] 

            else:
                #Здесь классический метод эвольвент
                EV_table=change_plan(msv, np.mean(msv)*np.ones((len(msv),)), popravki_value=1.25, upper_bound=ubound, lower_bound=lbound, min_length_from_start_end=3, koeff=0, kfv = kfv)

        else: 
            EV_table=np.zeros((len(msv),42))
            EV_table[:,0]=msv
            EV_table[:,1]=msv  
            EV_table[:,10]=EV_table[:,1]  

    if calc_type == 2:
        nf = len(msv) - 1
        if nf > 0:
            EV_table=np.zeros((len(msv),42))
            Ef = 0
            for i in range(nf):
                Ef += (nf - i)*msv[i]
            EV_table[:,0]=msv
            EV_table[:,1]=2*Ef/nf/(nf+1)
            EV_table[:,2]=EV_table[:,0]-EV_table[:,1]
            EV_table[0,3]=EV_table[0,2]
            for i in range(1,len(msv)):
                EV_table[i,3]=EV_table[i-1,3]+EV_table[i,2]
            EV_table[0,4]=0
            EV_table[1,4]=EV_table[0,3]
            for i in range(2,len(msv)):
                EV_table[i,4]=EV_table[i-1,4]+EV_table[i-1,3] 
            EV_table[:,4]=2*EV_table[:,4]

            EV_table[:,10]=EV_table[:,1]  
            EV_table[:,13]=EV_table[:,4] 
        else:
            EV_table=np.zeros((len(msv),42))
            EV_table[:,0]=msv
            EV_table[:,1]=msv  
            EV_table[:,10]=EV_table[:,1]              
        print("ЭВОЛЬВЕНТА В ПОСЛЕДНЕЙ ТОЧКЕ:", EV_table[-1,13])    
            
    #Записываем значения уровня на участке
    EV_table[:,16]=urov_msv
    #Записываем значения максимальной скорости на участке    
    EV_table[:,17]=v_msv
  
    ac_plan, ac_urov = find_R_to_alc(np.copy(EV_table[:,10]), np.copy(EV_table[:,16]), start_point, False)                               
    
    if count_urov != -1:
        ac_urov[ac_urov.columns[-1]] = count_urov
    
    EV_table=pd.DataFrame(EV_table)                  
    if save_to_csv == True:
        EV_table.to_csv(f'results/straights/straight_{straight_num}.csv',index=False)
    return EV_table, ac_plan, ac_urov
#Функция расчета кривых
def curve_processing(msv, urov_msv, v_msv, curve_type, optimization_result, opt_result, k0, k1, sdx, edx, ubound, lbound, start_point, curve_num, kfv, save_to_csv = False, start_in_curve = False, end_in_curve=False):        
    print("---------------РАСЧЕТ КРИВОГО УЧАСТКА №", curve_num, 'ДЛИНА УЧАСТКА', len(msv))
    SLSQP_initial_point,_ = find_optimization_initial_point(msv, curve_type, find_start_point(np.copy(msv), curve_type, start_in_curve, end_in_curve), k0, k1, sdx, edx, 'SLSQP',
                                                            maxiter=1000, start_in_curve = start_in_curve, end_in_curve = end_in_curve) 
    if optimization_result < 2:
        #q, xf_vector, kf_vector, sf_vector, bf_vector, xxf_vector, sq = build_project_plan_track(np.copy(msv), curve_type, SLSQP_initial_point, k0, k1, sdx, edx, 0, ubound, lbound,
        #                                                                                         tol=10e-5, maxiter=100, start_in_curve = start_in_curve, end_in_curve = end_in_curve)     
        #x_points=q.x
        x_points=opt_result.x
    else:
        x_points,_ = find_optimization_initial_point(msv, curve_type, find_start_point(np.copy(msv), curve_type, start_in_curve, end_in_curve), k0, k1, sdx, edx, 'SLSQP',
                                                     maxiter=1000, cons = True, start_in_curve = start_in_curve, end_in_curve = end_in_curve)
    
    
    azy=list()
    y_val = int(start_in_curve) + int(end_in_curve)
    for i in range(len(msv)):
        azy.append(curve_pattern(i, x_points[:2*curve_type-y_val], x_points[2*curve_type-y_val:], len(msv), k0, k1, sdx, edx, start_in_curve, end_in_curve))
    azy=np.array(azy)

    if optimization_result < 2:
        EV_table=np.zeros((len(msv), 42))

        EV_table[:,0]=msv
        EV_table[:,1]=azy
        EV_table[:,2]=EV_table[:,0]-EV_table[:,1]
        EV_table[0,3]=EV_table[0,2]
        for i in range(1,len(msv)):
            EV_table[i,3]=EV_table[i-1,3]+EV_table[i,2]
        EV_table[0,4]=0
        EV_table[1,4]=EV_table[0,3]
        for i in range(2,len(msv)):
            EV_table[i,4]=EV_table[i-1,4]+EV_table[i-1,3] 
        EV_table[:,4]=2*EV_table[:,4]

        EV_table[:,10]=EV_table[:,1]  
        EV_table[:,13]=EV_table[:,4] 

    else:
        #Здесь классический метод эвольвент
        EV_table=change_plan(msv,azy,popravki_value=0.5,upper_bound=ubound,lower_bound=lbound,min_length_from_start_end=3,koeff=0, kfv = kfv)
    
    points = np.concatenate([np.array([sdx]), x_points[:2*curve_type - int(start_in_curve) - int(end_in_curve)]])
    points = np.concatenate([points, np.array([edx+len(msv)-1])])
    points = points + start_point
    print(points)    
                           
    EV_table, ac_plan, ac_urov = count_curve_parametres(np.copy(EV_table), urov_msv, v_msv, curve_type, points-start_point, start_point, 0.7, False, start_in_curve, end_in_curve)    
        
    EV_table=pd.DataFrame(EV_table)
    
    if save_to_csv == True:
        EV_table.to_csv(f'results/curves/curve_{curve_num}.csv',index=False)  
    return EV_table, ac_plan, ac_urov

def straight_split(msv, N, mlfse = 3, condition_start = 'None', condition_end = 'None'):
    if N == -1:
        return np.mean(msv)*np.ones((len(msv),))
    res = np.zeros((len(msv), ))
        
    m0 = msv[:mlfse + 1]
    m1 = msv[len(msv) - mlfse - 1:]    
    
    if condition_start == 'up':
        k0 = np.min(m0)   
    elif condition_start == 'down':
        k0 = np.max(m0) 
    elif condition_start == 'equal':
        k0 = m0[0]         
    else:
        k0 = np.mean(m0)
        
    if condition_end == 'up':
        k1 = np.min(m1)
    elif condition_end == 'down':
        k1 = np.max(m1)  
    elif condition_end == 'equal':
        k1 = m1[-1]        
    else:
        k1 = np.mean(m1)
    
    if (condition_start == 'equal') & (condition_end == 'equal'):
        xx_vector = list()
        for i in range(1, mlfse + 1):
            xx_vector.append(i)
        
        for i in range(1, N):
            xx_vector.append(len(m0) + int((len(msv) - len(m0) - len(m1))*i/N))
            
        for i in range(len(msv) - mlfse - 1, len(msv)):
            xx_vector.append(i)
            
        xx_vector = np.array(xx_vector)    

        kk_vector = np.zeros((len(xx_vector)-1, ))        
        for i in range(len(xx_vector)-1):
            kk_vector[i] = np.mean(msv[int(xx_vector[i]) : int(xx_vector[i+1])])    
            
    else:
        g1 = (np.sum(m0 - k0))
        g2 = (np.sum(m1 - k1))

        xx_vector = list()
        xx_vector.append(len(m0))
        for i in range(1, N + 1):
            xx_vector.append(len(m0) + int((len(msv) - len(m0) - len(m1))*i/N))
        xx_vector = np.array(xx_vector)    

        kk_vector = np.zeros((len(xx_vector)-1, ))        
        for i in range(len(xx_vector)-1):
            kk_vector[i] = np.mean(msv[int(xx_vector[i]) : int(xx_vector[i+1])])  

        kk_vector[0] += g1/len(msv[int(xx_vector[0]) : int(xx_vector[1])])
        kk_vector[-1] += g2/len(msv[int(xx_vector[-2]) : int(xx_vector[-1])])    
    
    for i in range(len(msv)):
        res[i] = straight_pattern(i, np.copy(xx_vector.astype(int)), np.copy(kk_vector), k0, k1)        
    return res

def project_profile(msv, lbound, ubound, popravki_value, min_length_from_start_end, koeff, kfv = 0.5, N_split = -1, condition_start = 'None', condition_end = 'None'):    
    lbound, ubound = restrictions_otvod(np.copy(lbound), np.copy(ubound))
    res = straight_split(msv, N_split, mlfse = min_length_from_start_end, condition_start = condition_start, condition_end = condition_end)
    EV=change_plan(msv, res, popravki_value, -lbound, -ubound, min_length_from_start_end, koeff, kfv)      
    
    alc=find_R_to_alc(EV[:,10], np.zeros((len(msv),)), 0, True)  
    alc=alc[0]
    ppt=np.zeros((alc.shape[0]+1,))
    R=np.abs(np.array(alc[alc.columns[5]]))
    R_sign=np.sign(np.array(alc[alc.columns[5]]))
    l=np.array(alc[alc.columns[7]])
    for i in range(1,ppt.shape[0]):
        y3=np.sin(l[i-1]/2/R[i-1])
        x3=(2*R[i-1]*y3-y3**2)**0.5
        x2=R[i-1]*y3/(x3+y3*ppt[i-1]/1000)
        y2=x2*ppt[i-1]/1000
        ppt[i]=R_sign[i-1]*np.abs((y3-y2)/(x3-x2)*1000)
    alc[alc.columns[9]]=ppt[:-1]
    
    res_alc=np.array(alc)
    
    res_alc[:,3]="Перелом профиля/N"
    res_alc[0,3]="Начальный уклон"    
    res_alc[:,5]=0    
    #l=res_alc[:,7]#np.array(res_alc[res_alc.columns[7]])
    l_prev=np.array(alc[alc.columns[7]])    
    #m=res_alc[:,1]#=np.array(res_alc[res_alc.columns[1]]) 
    res_alc[0,7]=res_alc[0,7]/2
    for i in range(1,l.shape[0]):
        res_alc[i,1]=res_alc[i-1,1]+res_alc[i-1,7]        
        res_alc[i,7]=l_prev[i]/2+l_prev[i-1]/2
    
    h=pd.DataFrame(["Место [м]", res_alc[-1,1]+res_alc[-1,7], 
                    "Уровень: геометрия", "Перелом профиля/N",
                    "Радиус сопряжения", 0,
                    "Длина (м)", alc[alc.columns[7]].iloc[-1]/2,
                    "Уклон (ppt)", ppt[-1]])    

    res_alc=pd.DataFrame(res_alc)    
    res_alc=pd.concat([res_alc,h.T])
    return pd.DataFrame(EV), res_alc 

def restrictions_otvod(lbound, ubound):  
    l_bound_max = np.max(lbound)
    ubound_max = np.max(ubound)       
    
    lbound[0] = 0
    lbound[-1] = 0    
    
    for i in range(1, int(1+np.floor(l_bound_max/10))):
        lbound[i] = (i-1)*10
        
    for i in range(1, int(1+np.floor(l_bound_max/10))):
        lbound[-i-1] = (i-1)*10
        
    for i in range(0, int(np.floor(ubound_max/10))):
        ubound[i] = (i+1)*10

    for i in range(0, int(np.floor(ubound_max/10))):
        ubound[-i-1] = (i+1)*10        
        
    return lbound, ubound

#====================================================================================================================#
def find_plan_xs(x_vector, f_vector):
    plan = list()
    i = 0
    while i <= x_vector[-1]:
        for j in range(1, len(x_vector)):
            if i <= x_vector[j]:
                a = (f_vector[j] - f_vector[j-1])/(x_vector[j] - x_vector[j-1])
                b = f_vector[j] - a*x_vector[j]
                plan.append(a*i+b)
                break
        i = i + 1
    return np.array(plan)

def minimize_evl_with_r_and_l(msv, y_vals, params_l, params_k,  mx_evals= 1000, req_precision = 10**-4, rand_state = 42):
    L = params_l.shape[0] - 1
    
    def objective(search_space):
        tsum = 0
        for i in range(len(search_space)-1):
            tsum += search_space[f'x{i+1}']
        #print(tsum - (len(msv) - np.sum(params_l) - 1))
        if tsum > len(msv) - np.sum(params_l) - 1:
            return {'loss': np.inf, 'plan': 0, 'status': STATUS_OK}

        xx_vector = list()
        xx_vector.append(0)
        for i in range(len(search_space)-1):
            xx_vector.append(xx_vector[-1] + params_l[i])
            xx_vector.append(xx_vector[-1] + search_space[f'x{i+1}'])
        xx_vector.append(xx_vector[-1] + params_l[-1])
        xx_vector = np.array(xx_vector)
        
        plan_xs = find_plan_xs(xx_vector, y_vals)
        plan = search_space[f'x{len(search_space)}'] * np.ones((len(msv), ))
        plan[:len(plan_xs)] = plan_xs
        
        evm=0
        for js in range(len(plan)):
            evm += (len(plan) - js - 1)*(plan[js] - msv[js])        
        
        evolvents = list()
        for j in range(len(plan)):
            evl=0
            for i in range(j):
                diff_strel = msv[i] - plan[i]
                val = (j-i)*diff_strel
                evl = evl + val
            evolvents.append(evl)
        
        max_evl = 2*np.max(np.abs(np.array(evolvents)))

        return {'loss': 10*np.abs(evm) + max_evl, 'plan': plan, 'len_radius': xx_vector, 'curve_len': len(plan_xs), 'status': STATUS_OK}
        #return {'loss': evm**2, 'plan': plan, 'curve_len': len(plan_xs), 'status': STATUS_OK}
        
    def stop_func(*args):
        losses = args[0].losses()
        
        if losses[-1] < req_precision:
            return True, args
        return False, args
    
    trials = Trials()
    search_space=dict()
    for i in range(L):
        search_space[f'x{i+1}']=hp.uniform(f'x{i+1}', 0, len(msv) - np.sum(params_l) - 2)
    search_space[f'x{L+1}']=hp.uniform(f'x{L+1}', params_k[-1] - 5, params_k[-1] + 5)
    
    best_params = fmin(
        fn=objective, space=search_space, algo=tpe.suggest, #algo=hyperopt.anneal.suggest
        max_evals=mx_evals, trials=trials, rstate=np.random.default_rng(rand_state), verbose=False,
        early_stop_fn=stop_func
    )
    
    return trials

"""
# Меняет длины переходных и радиусы
# params_l - длины переходных
# params_r - радиусы
# params_k - значение стрелы в начале и конце участка (к которому хотим привести)
# mx_evals - лучше 100 ставить

Вызов:
hmsv = msv_rix[64:87]
h_urov_msv=msv_urov[64:87]
h_v_msv=msv_v_max[64:87]

EV_table, alc_plan, alc_urov = calculate_plan_with_r_and_l(hmsv, h_urov_msv, h_v_msv,
                                                        params_l = [52, 55, 20], params_r = [450, 3000], params_k = [0, 0],
                                                        curve_urov = [25, 10], straight_urov = 0,
                                                        mx_evals= 10, req_precision = 10**-4, rand_state_min = 0, rand_state_max = 42)
"""
def calculate_plan_with_r_and_l(msv, urov, vmax, params_l, params_r, params_k, curve_urov = -1, straight_urov = -1, mx_evals= 1000, req_precision = 10**-4, rand_state_min = 0, rand_state_max = 42):
    params_l = np.array(params_l)/10
    params_r = np.array(params_r)
    params_k = np.array(params_k)
    params_f = 50000/params_r

    x_vals = list()
    y_vals = list()
    x_vals.append(0)
    y_vals.append(params_k[0])

    for i in range(len(params_l)):
        x_vals.append(x_vals[-1] + params_l[i])

    for i in range(len(params_f)):
        y_vals.append(params_f[i])
        y_vals.append(params_f[i])

    y_vals.append(params_k[-1])
    
    res_loss = np.inf
    for i in tqdm(range(rand_state_min, rand_state_max+1)):
        res = minimize_evl_with_r_and_l(msv, y_vals, params_l, params_k,  mx_evals = mx_evals, req_precision = req_precision, rand_state = i)
        # print(i, res_loss, res.best_trial['result']['loss'])
        if res.best_trial['result']['loss'] < res_loss:
            res_loss = res.best_trial['result']['loss']
            res_plan = res.best_trial['result']['plan']
            res_curve_len = res.best_trial['result']['curve_len']
            len_radius = res.best_trial['result']['len_radius']
            
    EV_table=np.zeros((len(msv),32))
    
    nf = len(msv) - 1    
    Ef = 0
    for i in range(nf):
        Ef += (nf - i)*msv[i]
        
    for i in range(res_curve_len):
        Ef -= (nf - i)*res_plan[i]    
    
    m = len(msv) - res_curve_len - 1
    y = 2*Ef/m/(m+1)
    
    EV_table[:,0]=msv
    EV_table[:,1]=res_plan  
    for i in range(res_curve_len, len(msv)):
        EV_table[i,1]=y
    EV_table[:,2]=EV_table[:,0]-EV_table[:,1]
    EV_table[0,3]=EV_table[0,2]
    for i in range(1,len(msv)):
        EV_table[i,3]=EV_table[i-1,3]+EV_table[i,2]
    EV_table[0,4]=0
    EV_table[1,4]=EV_table[0,3]
    for i in range(2,len(msv)):
        EV_table[i,4]=EV_table[i-1,4]+EV_table[i-1,3] 
    EV_table[:,4]=2*EV_table[:,4]

    EV_table[:,10]=EV_table[:,1]  
    EV_table[:,13]=EV_table[:,4] 

    #Записываем значения уровня на участке
    EV_table[:,16]=urov
    #Записываем значения максимальной скорости на участке    
    EV_table[:,17]=vmax    
    
    str_start = int(np.ceil(len_radius[-1]))
    E_table, alc_plan, alc_urov = count_curve_parametres(np.copy(EV_table[:str_start]), urov[:str_start], vmax[:str_start], len(params_r), len_radius, 0, 0.7, False, False, False) 
    EV_table[:str_start] = E_table
    
    if curve_urov != -1:
        alc_urov[alc_urov.columns[5]][alc_urov[alc_urov.columns[3]] == 'возвышение'] = curve_urov
    
    ac_plan, ac_urov = find_R_to_alc(np.copy(EV_table[str_start:,10]), np.copy(EV_table[str_start:,16]), len_radius[-1], False)   
    
    if straight_urov != -1:
        ac_urov[ac_urov.columns[-1]] = straight_urov    
        
    alc_plan = pd.concat([alc_plan, ac_plan])
    alc_urov = pd.concat([alc_urov, ac_urov])
    
    return EV_table, alc_plan, alc_urov


def minimize_evl_with_l_points(msv, l_points, params_k, x0_point, mx_evals= 1000, kf_search = 0.2, req_precision = 10**-4, rand_state = 42):
    L = int(len(l_points)/2 - 1)
    
    def objective(search_space):

        y_vals = list()
        y_vals.append(params_k[0])

        for i in range(L):
            y_vals.append(search_space[f'x{i+1}'])
            y_vals.append(search_space[f'x{i+1}'])

        y_vals.append(params_k[-1])
        
        plan_xs = find_plan_xs(l_points, y_vals)
        plan = search_space[f'x{len(search_space)}'] * np.ones((len(msv), ))
        plan[:len(plan_xs)] = plan_xs
        
        evm=0
        for js in range(len(plan)):
            evm += (len(plan) - js - 1)*(plan[js] - msv[js])        
        
        evolvents = list()
        for j in range(len(plan)):
            evl=0
            for i in range(j):
                diff_strel = msv[i] - plan[i]
                val = (j-i)*diff_strel
                evl = evl + val
            evolvents.append(evl)
        
        max_evl = 2*np.max(np.abs(np.array(evolvents)))

        return {'loss': 10*np.abs(evm) + max_evl, 'plan': plan, 'len_radius': y_vals, 'curve_len': len(plan_xs), 'status': STATUS_OK}
        #return {'loss': evm**2, 'plan': plan, 'curve_len': len(plan_xs), 'status': STATUS_OK}
        
    def stop_func(*args):
        losses = args[0].losses()
        
        if losses[-1] < req_precision:
            return True, args
        return False, args
    
    trials = Trials()
    
    search_space=dict()
    for i in range(L):
        f_diff = np.max([20, kf_search*np.abs(x0_point[i])])
        search_space[f'x{i+1}']=hp.uniform(f'x{i+1}', x0_point[i] - f_diff, x0_point[i] + f_diff)
    search_space[f'x{L+1}']=hp.uniform(f'x{L+1}', params_k[-1] - 5, params_k[-1] + 5)
    
    best_params = fmin(
        fn=objective, space=search_space, algo=tpe.suggest, #algo=hyperopt.anneal.suggest
        max_evals=mx_evals, trials=trials, rstate=np.random.default_rng(rand_state), verbose=False,
        early_stop_fn=stop_func
    )
    
    return trials

"""
# Меняет длины переходных и длины круговых
# params_k - значение стрелы в начале и конце участка (к которому хотим привести)
# msv - круговая кривая с началом в переходной и концом на прямой
# l_points - точки начала и окончания переходных и круговых кривых

EV_table, alc_plan, alc_urov = calculate_plan_with_l_points(hmsv, h_urov_msv, h_v_msv,
                                                        l_points = [0, 52, 65.7, 121, 151, 172], params_k = [0, 0],
                                                        curve_urov = [25, 10], straight_urov = 0,
                                                        mx_evals= 100, kf_search = 0.2, req_precision = 10**-4, rand_state_min = 0, rand_state_max = 42)
"""
def calculate_plan_with_l_points(msv, urov, vmax, l_points, params_k, curve_urov = -1, straight_urov = -1, mx_evals= 1000, kf_search = 0.2, req_precision = 10**-4, rand_state_min = 0, rand_state_max = 42):
    l_points = np.array(l_points)/10
    Lx = int(len(l_points)/2 - 1)    
    params_k = np.array(params_k)
    
    x0_point = list()
    for i in range(Lx):
        sp = np.ceil(l_points[2*i+1]).astype(int)
        ep = np.floor(l_points[2*i+2]).astype(int)
        new_p =  np.mean(msv[sp : ep+1])
        x0_point.append(new_p)
    x0_point = np.array(x0_point)
    
    res_loss = np.inf
    for i in tqdm(range(rand_state_min, rand_state_max+1)):
        res = minimize_evl_with_l_points(msv, l_points, params_k, x0_point, mx_evals = mx_evals, kf_search = kf_search, req_precision = req_precision, rand_state = i)
        # print(i, res_loss, res.best_trial['result']['loss'])
        if res.best_trial['result']['loss'] < res_loss:
            res_loss = res.best_trial['result']['loss']
            res_plan = res.best_trial['result']['plan']
            res_curve_len = res.best_trial['result']['curve_len']
            y_vals = res.best_trial['result']['len_radius']
            len_radius = l_points
            
    EV_table=np.zeros((len(msv),32))
    
    nf = len(msv) - 1    
    Ef = 0
    for i in range(nf):
        Ef += (nf - i)*msv[i]
        
    for i in range(res_curve_len):
        Ef -= (nf - i)*res_plan[i]    
    
    m = len(msv) - res_curve_len - 1
    y = 2*Ef/m/(m+1)
    
    EV_table[:,0]=msv
    EV_table[:,1]=res_plan  
    for i in range(res_curve_len, len(msv)):
        EV_table[i,1]=y
    EV_table[:,2]=EV_table[:,0]-EV_table[:,1]
    EV_table[0,3]=EV_table[0,2]
    for i in range(1,len(msv)):
        EV_table[i,3]=EV_table[i-1,3]+EV_table[i,2]
    EV_table[0,4]=0
    EV_table[1,4]=EV_table[0,3]
    for i in range(2,len(msv)):
        EV_table[i,4]=EV_table[i-1,4]+EV_table[i-1,3] 
    EV_table[:,4]=2*EV_table[:,4]

    EV_table[:,10]=EV_table[:,1]  
    EV_table[:,13]=EV_table[:,4] 

    #Записываем значения уровня на участке
    EV_table[:,16]=urov
    #Записываем значения максимальной скорости на участке    
    EV_table[:,17]=vmax    
    
    str_start = int(np.ceil(len_radius[-1]))
    E_table, alc_plan, alc_urov = count_curve_parametres(np.copy(EV_table[:str_start]), urov[:str_start], vmax[:str_start], Lx, len_radius, 0, 0.7, False, False, False) 
    EV_table[:str_start] = E_table
    
    if curve_urov != -1:
        alc_urov[alc_urov.columns[5]][alc_urov[alc_urov.columns[3]] == 'возвышение'] = curve_urov
    
    ac_plan, ac_urov = find_R_to_alc(np.copy(EV_table[str_start:,10]), np.copy(EV_table[str_start:,16]), len_radius[-1], False)   
    
    if straight_urov != -1:
        ac_urov[ac_urov.columns[-1]] = straight_urov    
        
    alc_plan = pd.concat([alc_plan, ac_plan])
    alc_urov = pd.concat([alc_urov, ac_urov])
    
    return EV_table, alc_plan, alc_urov

"""
Вызов:
podjemki = np.array(EV_profile[EV_profile.columns[13]])
urov_naturn = np.array(EV_plan[EV_plan.columns[16]])
urov_project = np.array(EV_plan[EV_plan.columns[23]])
podjemka_l, podjemka_r = calc_podjemki(urov_naturn, urov_project, podjemki)
"""
def calc_podjemki(urov_naturn, urov_project, podjemki):
    podjemka_l = np.copy(podjemki)
    podjemka_r = np.copy(podjemki)
    urov_popravka = urov_naturn - urov_project
    for i in range(urov_popravka.shape[0]):
        if urov_popravka[i] >= 0:
            podjemka_l[i] = podjemka_l[i] + urov_popravka[i]
        else:
            podjemka_r[i] = podjemka_r[i] - urov_popravka[i]  
    return podjemka_l, podjemka_r
