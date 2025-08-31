import numpy as np
from scipy.interpolate import CubicSpline
import scipy as sc

# Нахождение координат по стрелам
def find_coord_by_psi(msv, x0, y0, d, machine_horde_1, machine_horde_2):   
    x=np.zeros((len(msv),))
    y=np.zeros((len(msv),))

    x[0]=x0
    y[0]=y0
    for i in range(1,len(msv)):
        x[i]=x[i-1]+d*np.cos(msv[i])
        y[i]=y[i-1]+d*np.sin(msv[i])          
    return x, y

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

def find_coord(msv, x0, y0, d, machine_horde_1, machine_horde_2):   
    phi = find_fi(msv/1000, machine_horde_1, machine_horde_2)
    psi = find_psi(phi, d)
    x, y = find_coord_by_psi(psi, x0, y0, d, machine_horde_1, machine_horde_2)  
    return x, y

def int3(x,y):
    return CubicSpline(x,y)

def scalar_prod(x1,y1,x2,y2):
    return(x1*x2+y1*y2)

def equations_for_chord(vars,x0,y0,R,f1):
    x,y=vars
    eq1=(x-x0)**2+(y-y0)**2-R**2
    eq2=f1(x)-y
    return[eq1,eq2]

def find_chord_ends(x0,y0,R,f1,x_prev,y_prev):
    initial_guess1=[[x0+R,f1(x0+R)]]
    initial_guess2=[[x0-R,f1(x0-R)]]
    c1,d1=sc.optimize.fsolve(equations_for_chord,initial_guess1,args=(x0,y0,R,f1))
    c2,d2=sc.optimize.fsolve(equations_for_chord,initial_guess2,args=(x0,y0,R,f1))
    if np.sign(scalar_prod(x0-x_prev,y0-y_prev,c1-x0,d1-y0))>=0:
        c=c1;d=d1
    else:
        c=c2;d=d2
    return(c,d)

def line_2dots(x1,y1,x2,y2):
    k= (y2-y1)/(x2-x1)
    b=-x1*k+y1
    return(k,b)

def normal(x1,y1,k):
    k1=-1/k
    b1=-k1*x1+y1
    return(k1,b1)

def equations_for_arrow(p,k,b,f1):
    x,y=p
    eq1=k*x+b-y
    eq2=f1(x)-y
    return[eq1,eq2]

def find_arrow(a1,a2,k1,b1,f1):
    initial_guess1=[[a1,f1(a1)]]
    c1,d1=sc.optimize.fsolve(equations_for_arrow,initial_guess1,args=(k1,b1,f1))
    arr=((a1-c1)**2+(a2-d1)**2)**0.5
    return(c1,d1,arr)

def coords_to_arrows_sim_mono(x_coords:np.array,
                         y_coords:np.array,
                         l=0.185
):
    """
    Функция для случая монотонно возрастающей координаты х
    x_coords: (n x 1) - x-координата пути
    y_coords: (n x 1) - y-координата пути
    l:int - половина длины симметричной хорды 

    return:
        np.array: (mx2)
    """
    f1=int3(x_coords,y_coords)
    x_h=-l
    y_h=f1(-l)
    x_prev=x_h;y_prev=y_h
    x_a=0;y_a=0;i=0
    R=2*l
    arrow=[]
    while(x_a!=x_coords[len(x_coords)-1] and y_a!=y_coords[len(y_coords)-1]):
        x_e,y_e=find_chord_ends(x_h,y_h,R,f1,x_prev,y_prev)#конечная точка хорды
        k1,b1=line_2dots(x_h,y_h,x_e,y_e)
        cx=(x_h+x_e)/2#середина хорды(начало стрелы)
        cy=(y_h+y_e)/2
        k2,b2=normal(cx,cy,k1)
        x_a,y_a,arr=find_arrow(cx,cy,k2,b2,f1)#конец стрелы на пути
        direct=scalar_prod(1,0,x_e-x_h,y_e-y_h)
        arrow.append(arr*np.sign(cy-y_a)*np.sign(direct))
        x_prev=x_h;y_prev=y_h
        x_h=x_a
        y_h=y_a
        i+=1
        if i > len(x_coords)+1:
            break
    return np.array(arrow)

def next_point_equations(t, x1, y1, intrp, d_len):
    h = sc.interpolate.splev(t, intrp)
    return (h[0] - x1)**2 + (h[1] - y1)**2 - d_len**2

def arrow_end_equation(t,intrp,k,b):
    h = sc.interpolate.splev(t, intrp)
    return k*h[0]+b-h[1]

def find_next_point(hC_prev,lng,tck,x0,y0,x_prev,y_prev,R):
    initial_guess1=[hC_prev+1/lng]
    hC1 = sc.optimize.fsolve(next_point_equations, initial_guess1, args=(x0, y0, tck, R))
    X1,Y1=sc.interpolate.splev(hC1, tck)
    return(X1,Y1,hC1)

def find_arrow_end(hC,tck,k,b,x0,y0,lng):
    initial_guess1=[hC-1/(2*lng)]
    hC1 = sc.optimize.fsolve(arrow_end_equation, initial_guess1, args=( tck, k,b))
    X,Y=sc.interpolate.splev(hC1, tck)
    arr=((x0-X)**2+(y0-Y)**2)**0.5
    return(X,Y,arr)

def coords_to_arrows_sim_NOTmono(x_coords:np.array,
                         y_coords:np.array,
                         l=0.185
):
    """
    Функция для немонотонной координаты х
    x_coords: (n x 1) - x-координата пути
    y_coords: (n x 1) - y-координата пути
    scale_rail: l - половина длины симметричной хорды

    return:
        np.array: (mx2)
    """
    tck,_ = sc.interpolate.splprep([x_coords, y_coords], s=0, per=False)
    x_h=-l
    y_h=y_coords[0]
    x_prev=x_h;y_prev=y_h;h_prev=0
    x_a=0;y_a=0;i=0
    R=2*l
    lng=len(x_coords)
    arrow=[]
    #L=curve_length(x_coords,y_coords,0,x_coords[-1])
    while(x_a!=x_coords[-1] and y_a!=y_coords[-1]):
        x_e,y_e,h=find_next_point(h_prev,lng,tck,x_h,y_h,x_prev,y_prev,R)#конечная точка хорды
        k1,b1=line_2dots(x_h,y_h,x_e,y_e)
        cx=(x_h+x_e)/2#середина хорды(начало стрелы)
        cy=(y_h+y_e)/2
        k2,b2=normal(cx,cy,k1)
        x_a,y_a,arr=find_arrow_end(h,tck,k2,b2,cx,cy,lng)#конец стрелы на пути
        direct=scalar_prod(1,0,x_e-x_h,y_e-y_h)
        arrow.append(float(arr*np.sign(cy-y_a)*np.sign(direct)))
        h_prev=h
        x_prev=x_h;y_prev=y_h
        x_h=x_a
        y_h=y_a
        i+=1
        if i > lng+1:
            break
    return np.array(arrow)

def coords_to_arrows_sim(x_coords,y_coords,l=0.185):
    try:
        arrow=coords_to_arrows_sim_mono(x_coords,y_coords)
    except:
        arrow=coords_to_arrows_sim_NOTmono(x_coords,y_coords)
    return 1000*arrow[:len(x_coords)]

#Пересчет из несимметричной хорды в симметричную
def new_horde_to_horde(data, machine_horde_1, machine_horde_2, d, mh1, mh2):
    # print('new_horde_to_horde')
    x, y = find_coord(data, 0, 0, d, machine_horde_1, machine_horde_2)  
    res_to_strela = coords_to_arrows_sim(x, y, d)      
    return res_to_strela
