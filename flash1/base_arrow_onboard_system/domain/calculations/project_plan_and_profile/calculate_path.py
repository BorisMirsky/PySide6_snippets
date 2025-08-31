import numpy as np
from tqdm import tqdm


class CalculatePath:

    def __init__(self, init_d, init_x, init_y, d_num, x_coord, y_coord, lb_x, lb_y, ub_x, ub_y, kf):

        self.initial_d = init_d
        self.initial_x = init_x
        self.initial_y = init_y

        self.d_num = d_num
        self.x = x_coord
        self.y = y_coord
        
        self.dimg = x_coord.shape[0]
        self.ub_x = ub_x
        self.ub_y = ub_y        
        self.lb_x = lb_x
        self.lb_y = lb_y  
        self.kf = kf
        self.a_bound, self.b_bound, self.c_bound, self.max_x_bound, self.min_x_bound, self.max_y_bound, self.min_y_bound = self.__prepare_bound_values()
        
    def __prepare_bound_values(self):
        a_bound = self.lb_y - self.ub_y
        b_bound = self.lb_x - self.ub_x
        c_bound = self.lb_x*self.ub_y - self.ub_x*self.lb_y    
        max_x_bound = np.max([self.lb_x, self.ub_x], axis=0)
        min_x_bound = np.min([self.lb_x, self.ub_x], axis=0)
        max_y_bound = np.max([self.lb_y, self.ub_y], axis=0)
        min_y_bound = np.min([self.lb_y, self.ub_y], axis=0)
        return a_bound, b_bound, c_bound, max_x_bound, min_x_bound, max_y_bound, min_y_bound
        
    def __G_elements_calculate(self, i, j):

        mx = np.ones(self.dimg)
        hx = np.ones(self.dimg)
        
        a = self.y[j] - self.y[i]
        b = self.x[j] - self.x[i]
        c = self.x[j]*self.y[i] - self.y[j]*self.x[i]
        l = (a**2 + b**2)**0.5  
        
        for s in range(i, j + 1):            
            mx[s] = np.abs(a*self.x[s] - b*self.y[s] + c)/l
            hx[s] = ((self.x[s] - self.ub_x[s])**2 + (self.y[s] - self.ub_y[s])**2)**0.5
        rx = mx/hx
        
        result_score = 1 + self.kf*np.sum(rx[i: j + 1])

        return result_score

    def __calculate_Graph(self):

        GG = np.zeros((self.dimg, self.dimg))

        for i in tqdm(range(self.dimg)):
            for j in range(i + 1, self.dimg):
                cross = 0
                a = self.y[i] - self.y[j]
                b = self.x[i] - self.x[j]
                c = self.x[i]*self.y[j] - self.x[j]*self.y[i]                 
                max_x = np.max([self.x[i], self.x[j]])
                min_x = np.min([self.x[i], self.x[j]])
                max_y = np.max([self.y[i], self.y[j]])
                min_y = np.min([self.y[i], self.y[j]])
                #print("prepare:--- %s seconds ---" % (time.time() - t))

                """
                t = time.time()
                p_x = (c * self.b_bound[i + 1: j + 1] - b * self.c_bound[i + 1: j + 1]) / (b * self.a_bound[i + 1: j + 1] - a * self.b_bound[i + 1: j + 1])
                p_y = (c * self.a_bound[i + 1: j + 1] - a * self.c_bound[i + 1: j + 1]) / (b * self.a_bound[i + 1: j + 1] - a * self.b_bound[i + 1: j + 1])
                hx = np.prod((p_x <= self.max_x_bound[i + 1: j + 1])*(p_x >= self.min_x_bound[i + 1: j + 1]))
                if hx == 1:
                    hy = np.prod((p_y <= self.max_y_bound[i + 1: j + 1])*(p_y >= self.min_y_bound[i + 1: j + 1]))
                    if hy == 1:
                        mx = np.prod((p_x <= max_x)*(p_x >= min_x))
                        if mx == 1:
                            my = np.prod((p_y <= max_y)*(p_y >= min_y))
                            if my == 1:
                                GG[i, j] = self.__G_elements_calculate(i, j)
                                GG[j, i] = GG[i, j]
                print("arrow:--- %s seconds ---" % (time.time() - t))
                """

                for k in range(i + 1, j):

                    p_x = (c*self.b_bound[k] - b*self.c_bound[k])/(b*self.a_bound[k] - a*self.b_bound[k])
                    p_y = (c*self.a_bound[k] - a*self.c_bound[k])/(b*self.a_bound[k] - a*self.b_bound[k])
                    if (p_x > self.max_x_bound[k]) | (p_x < self.min_x_bound[k]) | (p_y > self.max_y_bound[k]) | (p_y < self.min_y_bound[k]) | (p_x > max_x) | (p_x < min_x) | (p_y > max_y) | (p_y < min_y):
                        cross = 1
                        break
                #print("for:--- %s seconds ---" % (time.time() - t))

                if cross == 0:
                    GG[i, j] = self.__G_elements_calculate(i, j)
                    GG[j, i] = GG[i, j]
        
        return GG    

    def Dijkstra(self, Graph):
        
        L = len(Graph)
        GL = 10**10*np.ones(L)
        GL_Visited = np.zeros(L)  
        GP = np.ones(L)
        GL[0] = 0
        
        while np.sum(GL_Visited) < L:
            minWeight = 10**11
            minWeight_NUM = 0
            
            for i in range(L):
                if (GL_Visited[i] == 0) & (GL[i] < minWeight):
                    minWeight = GL[i]
                    minWeight_NUM = i
            GL_Visited[minWeight_NUM] = 1
            
            for i in range(L):
                if Graph[minWeight_NUM, i] > 0:
                    if GL[minWeight_NUM] + Graph[minWeight_NUM, i] < GL[i]:
                        GL[i] = GL[minWeight_NUM] + Graph[minWeight_NUM, i]
                        GP[i] = minWeight_NUM

        Path = (L - 1)*np.ones(L)
        w = 0
        i = L - 1
        while i > 0:
            i = int(GP[i])
            w = w + 1
            Path[w] = i
        result = GL[L - 1]

        return Path[: np.argmin(Path) + 1], int(result)       
    
    def calculate_straight_path(self):
  
        EV_table = np.zeros((self.dimg, 42))
        EV_table[:, 0] = self.x
        EV_table[:, 1] = self.y
        EV_table[:, 2] = self.ub_x
        EV_table[:, 3] = self.ub_y        
        EV_table[:, 4] = self.lb_x
        EV_table[:, 5] = self.lb_y

        G = self.__calculate_Graph()
        
        H, p_num = self.Dijkstra(G)
        print(H, p_num)

        VH = np.zeros(len(H))
        v_coord_x = np.zeros(len(H))
        v_coord_y = np.zeros(len(H))
        
        for i in range(len(H)):
            VH[i] = H[i]  
        V = np.flip(VH.astype(int))

        for i in range(len(V)):
            v_coord_x[i] = self.x[V[i]]            
            v_coord_y[i] = self.y[V[i]]
                
        for i in range(len(V) - 1):
            a = (v_coord_y[i + 1] - v_coord_y[i])/(v_coord_x[i + 1] - v_coord_x[i])
            b = v_coord_y[i] - a*v_coord_x[i]            
            for j in range(V[i], V[i + 1] + 1):                
                EV_table[j, 6] = v_coord_x[i] + (j - V[i])*(v_coord_x[i + 1] - v_coord_x[i])/(V[i + 1] - V[i])
                EV_table[j, 7] = v_coord_y[i] + (j - V[i])*(v_coord_y[i + 1] - v_coord_y[i])/(V[i + 1] - V[i])
                EV_table[j, 8] = np.sign(a*EV_table[j, 0] + b - EV_table[j, 1])

        # Расчет проектных стрел
        # import matplotlib.pyplot as plt
        #
        # plt.plot(EV_table[:, 0], EV_table[:, 1])
        # plt.plot(EV_table[:, 6], EV_table[:, 7])
        # plt.plot(EV_table[:, 2], EV_table[:, 3])
        # plt.plot(EV_table[:, 4], EV_table[:, 5])
        # plt.show()

        return V

