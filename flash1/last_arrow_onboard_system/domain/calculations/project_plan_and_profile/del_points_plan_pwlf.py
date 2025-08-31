from __future__ import print_function
from .functions.generate_lincond_matrix_2 import generate_lincond_matrix
import numpy as np
import datetime
from scipy import linalg
from scipy.optimize import differential_evolution
from scipy.optimize import LinearConstraint
from scipy.linalg import lapack

def get_evl(a):

    b = np.zeros_like(a)
    b[1:] = np.cumsum(np.cumsum(a, axis=0), axis=0)[:-1]
    return b


class del_PWLF(object):

    def __init__(self, x, y, max_start_of_curve, min_end_of_curve,
                 ubound, lbound, add_evl, degree, f, token, count_with_weights=True,
                 end_evl_to_zero=False, summ_evl_to_zero=False, maxiter=1000,
                 de_workers=1, min_element_length=20, disp_res=False, lapack_driver='gelsd',
                 evl_minimize=False, constr=None, gen_solution=True):

        self.token = token
        self.print = disp_res
        self.lapack_driver = lapack_driver
        self.constr = constr

        # x and y should be numpy arrays
        # if they are not convert to numpy array
        if isinstance(x, np.ndarray) is False:
            x = np.array(x)
        if isinstance(y, np.ndarray) is False:
            y = np.array(y)

        self.degree = degree
        self.f_vector = f
        self.f_without_none = self.__get_f_without_none(self.f_vector)
        self.x_data = x
        self.y_data = y
        self.ubound = ubound/2
        self.lbound = lbound/2
        self.add_evl = add_evl/2
        self.w = self.__get_w()
        self.wt = self.w[np.newaxis, :].T

        self.max_start_of_curve = max_start_of_curve
        self.min_end_of_curve = min_end_of_curve

        self.count_with_weights = count_with_weights
        self.end_evl_to_zero = end_evl_to_zero
        self.summ_evl_to_zero = summ_evl_to_zero

        self.seed = 42
        self.min_element_length = min_element_length

        self.EVL_minimize = evl_minimize        
        self.de_workers = de_workers

        if self.EVL_minimize:
            self.Gy = get_evl(self.y_data) - self.add_evl
        else:
            self.Gy = np.copy(self.y_data)

        # calculate the number of data points
        self.n_data = x.size

        # set the first and last break x values to be the min and max of x
        self.break_0 = np.min(self.x_data)
        self.break_n = np.max(self.x_data)

        self.maxiter = maxiter
        self.gen_solution = gen_solution

        self.Ax_gen = None
        self.Ay_gen = None
        if self.gen_solution:
            self.Ax_gen, self.Ay_gen = generate_lincond_matrix(self.f_vector, self.degree, self.end_evl_to_zero, self.summ_evl_to_zero)

        self.index_to_drop = self.get_index_to_drop()

        self.beta = None
        self.all_beta_values = None
        self.fit_breaks = None
        self.n_segments = None
        self.n_parameters = None
        self.ssr = None
        self.slopes = None
        self.intercepts = None
        self.nVar = None

    def __get_w(self):
        w = 50/np.min([self.ubound - self.add_evl, self.add_evl - self.lbound], axis=0)
        return w

    def __get_f_without_none(self, f):
        f_without_none = list()
        for i in range(len(f)):
            if f[i] is not None:
                f_without_none.append(f[i])
        return f_without_none

    def get_index_to_drop(self):
        
        get_index_to_drop = list()
        
        for i in range(len(self.f_vector)):
            if self.f_vector[i] is not None:
                get_index_to_drop.append(i)

        condition_number = 1 + int(self.end_evl_to_zero) + int(self.summ_evl_to_zero)      
        conditions_counter = 0

        for i in range(len(self.f_vector) - 1, -1, -1):
            if conditions_counter >= condition_number:
                break     
            if self.f_vector[i] is None:       
                get_index_to_drop.append(i)
                conditions_counter += 1                

        get_index_to_drop = np.sort(np.array(get_index_to_drop))

        return get_index_to_drop        
    
    def assemble_regression_matrix(self, breaks, x, y, add_evl, f, calc_for_predict=False):
        self.token.check()
        
        # Check if breaks in ndarray, if not convert to np.array
        if isinstance(breaks, np.ndarray) is False:
            breaks = np.array(breaks)

        # Sort the breaks, then store them
        breaks_order = np.argsort(breaks)
        self.fit_breaks = breaks[breaks_order]
        # store the number of parameters and line segments
        self.n_segments = len(breaks) - 1

        # Assemble the regression matrix
        a_list = [np.ones_like(x)]
            
        for i in range(self.n_segments):
            degree = self.degree[i]
            if i == 0:
                a_list = [np.ones_like(x)]
                        
                if degree == 1:
                    w = np.where(x >= self.fit_breaks[i + 1], self.fit_breaks[i + 1] - self.fit_breaks[0], 0)
                    w2 = np.where((x < self.fit_breaks[i + 1]) & (x > self.fit_breaks[i]), x - self.fit_breaks[i], 0)
                    a_list.append(w + w2)
                        
            if i > 0:
                if degree == 0:
                    continue
                        
                elif degree == 1:
                    w = np.where(x >= self.fit_breaks[i + 1], self.fit_breaks[i + 1] - self.fit_breaks[i], 0)
                    w2 = np.where((x < self.fit_breaks[i + 1]) & (x > self.fit_breaks[i]), x - self.fit_breaks[i], 0)
                    a_list.append(w + w2)

        matrix_a = np.vstack(a_list).T  

        if calc_for_predict:
            return matrix_a, None, None, None   
        
        # print("A Forming:", datetime.datetime.now() - t)
                       
        if self.EVL_minimize:
            ga = get_evl(matrix_a)
            gy = get_evl(y) - add_evl
        else:
            ga = np.copy(matrix_a)
            gy = np.copy(y)
               
        wa = np.delete(ga, self.index_to_drop, 1)
        a_drop = ga[:, self.index_to_drop]
        
        var = list(np.sum(matrix_a, axis=0)) + [np.sum(y)] + list(ga[-1]) + [gy[-1]] + list(np.sum(ga, axis=0)) + \
              [np.sum(gy)] + list(self.fit_breaks) + list(np.zeros(matrix_a.shape[1])) + list(f)
        
        d = self.Ax_gen(*var)
        phi = self.Ay_gen(*var)
        
        new_a = wa + np.dot(a_drop, d)
        
        if self.EVL_minimize:
            new_y_data = gy - np.dot(a_drop, phi)
        else:
            new_y_data = y - np.dot(a_drop, phi)
            
        self.n_parameters = ga.shape[1]
        return new_a, new_y_data, d, phi

    def recalculate_index(self, index):
        
        idx = 0
        if index == 0:
            return idx
        
        ct = 0
        for idx in range(len(self.degree)):
            if self.degree[idx] == 1:
                ct += 1
            if ct == index:
                break
        return idx + 1

    def fit_with_breaks(self, breaks, f):

        # Check if breaks in ndarray, if not convert to np.array
        if isinstance(breaks, np.ndarray) is False:
            breaks = np.array(breaks)

        f_without_none = self.__get_f_without_none(f)

        boolarr = (self.x_data >= breaks[1]) & (self.x_data <= breaks[-2])
        x = self.x_data[boolarr]
        y = self.y_data[boolarr]
        wt = self.wt[boolarr]
        w = self.w[boolarr]
        lb = self.lbound[boolarr]
        ub = self.ubound[boolarr]
        add_evl = self.add_evl[boolarr]

        A, new_y_data, _, _ = self.assemble_regression_matrix(breaks[1: -1], x, y, add_evl, f_without_none)

        if (np.isnan(A).any()) | (np.isnan(new_y_data).any()):
            return np.inf
        
        # try to solve the regression problem
        try:
            # least squares solver
            if self.count_with_weights:
                beta, ssr, rank, s = linalg.lstsq(wt*A, w*new_y_data, lapack_driver=self.lapack_driver)
            else:
                beta, ssr, rank, s = linalg.lstsq(A, new_y_data, lapack_driver=self.lapack_driver)
            # save the beta parameters
            self.beta = beta

            # save the slopes
            self.calc_slopes()

            if self.count_with_weights:
                y_hat = np.dot(wt*A, beta)
                e = y_hat - w*new_y_data
            else:
                y_hat = np.dot(A, beta)
                e = y_hat - new_y_data

            # ssr is only calculated if self.n_data > self.n_parameters
            # in this case I'll need to calculate ssr manually
            # where ssr = sum of square of residuals
            if self.n_data <= self.n_parameters:
                y_hat = np.dot(A, beta)
                e = y_hat - new_y_data
                ssr = np.dot(e, e)
            if type(ssr) == list:
                ssr = ssr[0]
            elif type(ssr) == np.ndarray:
                if ssr.size == 0:
                    y_hat = np.dot(A, beta)
                    e = y_hat - new_y_data
                    ssr = np.dot(e, e)
                else:
                    ssr = ssr[0]

        except linalg.LinAlgError:
            # the computation could not converge!
            # on an error, return ssr = np.print_function
            # You might have a singular Matrix!!!
            ssr = np.inf
            e = np.inf * np.ones(A.shape[0])
        if ssr is None:
            ssr = np.inf
            e = np.inf * np.ones(A.shape[0])
            # something went wrong...
        self.ssr = ssr

        return self.calc_reward(e, ssr)

    def calc_reward(self, e, ssr):
        # if self.count_with_weights:
        #    we = w*e
        #    return np.dot(we, we)
        return ssr / len(e)
        # return 10**10*self.check_inside_bounds(e) + ssr

    def check_inside_bounds(self, e):
        if self.count_with_weights:
            w = self.w
        else:
            w = np.ones(len(self.w))

        for i in range(len(e)):
            if (e[i] / w[i] < -self.ubound[i]) | (e[i] / w[i] > -self.lbound[i]):
                return 1
        return 0

    def predict(self, x, f, beta=None, breaks=None):

        if beta is not None and breaks is not None:
            self.beta = beta
            # Sort the breaks, then store them
            breaks_order = np.argsort(breaks)
            self.fit_breaks = breaks[breaks_order]
            self.n_parameters = len(self.fit_breaks)
            self.n_segments = self.n_parameters - 1

        f_without_none = self.__get_f_without_none(f)

        boolarr = (self.x_data >= self.fit_breaks[0]) & (self.x_data <= self.fit_breaks[-1])
        new_x = self.x_data[boolarr]
        new_y = self.y_data[boolarr]
        add_evl = self.add_evl[boolarr]

        # check if x is numpy array, if not convert to numpy array
        if isinstance(x, np.ndarray) is False:
            x = np.array(x)

        _, _, D, phi = self.assemble_regression_matrix(self.fit_breaks, new_x, new_y, add_evl, f_without_none)
        
        add_beta = np.dot(D, self.beta) + phi        
        self.all_beta_values = self.get_beta(add_beta)
        
        # solve the regression problem        
        A, _, _, _ = self.assemble_regression_matrix(self.fit_breaks, x, y=None, add_evl=add_evl,
                                                     f=f_without_none, calc_for_predict=True)
        y_hat = np.dot(A, self.all_beta_values)
        
        return y_hat

    def get_beta(self, add_beta):
        
        ind_list = self.get_index_to_drop()
        new_beta = np.zeros(len(self.beta) + len(add_beta))
        
        ct = 0
        gt = 0
        for i in range(len(new_beta)):
            if i in ind_list:
                new_beta[i] = add_beta[ct]
                ct += 1
            else:
                new_beta[i] = self.beta[gt]
                gt += 1     

        return new_beta
    
    def fit_with_breaks_opt(self, var):

        var = np.sort(var)

        breaks = np.zeros(len(var) + 2)
        breaks[1:-1] = var.copy()
        breaks[0] = self.break_0
        breaks[-1] = self.break_n

        boolarr = (self.x_data >= var[0]) & (self.x_data <= var[-1])
        x = self.x_data[boolarr]
        y = self.y_data[boolarr]
        wt = self.wt[boolarr]
        w = self.w[boolarr]
        lb = self.lbound[boolarr]
        ub = self.ubound[boolarr]
        add_evl = self.add_evl[boolarr]

        A, new_y_data, _, _ = self.assemble_regression_matrix(var, x, y, add_evl, self.f_without_none)
        
        if (np.isnan(A).any()) | (np.isnan(new_y_data).any()):
            return np.inf

        # try to solve the regression problem
        try:
            # least squares solver
            if self.count_with_weights:
                beta, ssr, rank, s = linalg.lstsq(wt*A, w*new_y_data, lapack_driver=self.lapack_driver)
                y_hat = np.dot(wt*A, beta)
                e = y_hat - w*new_y_data
            else:
                beta, ssr, rank, s = linalg.lstsq(A, new_y_data, lapack_driver=self.lapack_driver)
                y_hat = np.dot(A, beta)
                e = y_hat - new_y_data

            # ssr is only calculated if self.n_data > self.n_parameters
            # in all other cases I'll need to calculate ssr manually
            # where ssr = sum of square of residuals
            if self.n_data <= self.n_parameters:
                y_hat = np.dot(A, beta)
                e = y_hat - new_y_data
                ssr = np.dot(e, e)
            if type(ssr) == list:
                ssr = ssr[0]
            elif type(ssr) == np.ndarray:
                if ssr.size == 0:
                    y_hat = np.dot(A, beta)
                    e = y_hat - new_y_data
                    ssr = np.dot(e, e)
                else:
                    ssr = ssr[0]

        except linalg.LinAlgError:
            # the computation could not converge!
            # on an error, return ssr = np.inf
            # You might have a singular Matrix!!!
            ssr = np.inf
            e = np.inf * np.ones(A.shape[0])
        if ssr is None:
            ssr = np.inf
            e = np.inf * np.ones(A.shape[0])
            # something went wrong...
        return self.calc_reward(e, ssr)
    
    def get_linear_constraints_matrix(self, n):
        
        lca = np.zeros((n + 1, n))
        lca[0, 0] = 1
        for i in range(1, n):
            lca[i, i - 1] = -1
            lca[i, i] = 1
        lca[-1, -1] = 1
        return lca
    
    def fit(self, n_segments, bounds=None, **kwargs):

        # set the function to minimize
        min_function = self.fit_with_breaks_opt

        # store the number of line segments and number of parameters
        self.n_segments = int(n_segments)
        self.n_parameters = self.n_segments + 1

        # calculate the number of variables I have to solve for
        self.nVar = self.n_segments + 1
        
        # initiate the bounds of the optimization
        if bounds is None:
            
            bounds = np.zeros([self.nVar, 2])
            # bounds[:, 0] = self.max_start_of_curve
            # bounds[:, 1] = self.min_end_of_curve
            bounds[:, 0] = self.break_0
            bounds[:, 1] = self.break_n

            bounds[0, 0] = self.break_0
            bounds[0, 1] = self.max_start_of_curve
            bounds[-1, 0] = self.min_end_of_curve
            bounds[-1, 1] = self.break_n

        lca_matrix = self.get_linear_constraints_matrix(self.nVar)
        if self.constr is None:
            lc_lbound = self.min_element_length * np.ones(self.nVar + 1)
            lc_ubound = np.inf * np.ones(self.nVar + 1)
            lc_lbound[0] = self.break_0 #self.break_0 + self.min_element_length
            lc_ubound[0] = self.max_start_of_curve
            lc_lbound[-1] = self.min_end_of_curve
            lc_ubound[-1] = self.break_n #self.break_n - self.min_element_length
            lc_lbound[1] = 0
            lc_lbound[-2] = 0
            # lc_ubound[1] = 0
            # lc_ubound[-2] = 0
        else:
            lc_lbound, lc_ubound = self.constr

        # print(lca_matrix, lc_lbound, lc_ubound)
        lc = LinearConstraint(lca_matrix, lc_lbound, lc_ubound)

        # run the optimization
        if len(kwargs) == 0:
            res = differential_evolution(min_function, bounds, constraints=lc,
                                         strategy='best1bin', maxiter=self.maxiter,
                                         popsize=50, tol=1e-3,
                                         mutation=(0.5, 1), recombination=0.7,
                                         seed=self.seed, callback=None, disp=False,
                                         polish=True, init='latinhypercube',
                                         atol=1e-4, workers=self.de_workers)
        else:
            res = differential_evolution(min_function,
                                         bounds, **kwargs)
        if self.print is True:
            print(res)

        self.ssr = res.fun
        
        # pull the breaks out of the result
        var = np.sort(res.x)
        breaks = np.zeros(len(var) + 2)
        breaks[1:-1] = var.copy()
        breaks[0] = self.break_0
        breaks[-1] = self.break_n

        # assign values
        self.fit_with_breaks(breaks, self.f_vector)

        return self.fit_breaks

    def calc_slopes(self):
        
        y_hat = self.predict(self.fit_breaks, self.f_vector)
        self.slopes = np.zeros(self.n_segments)
        for i in range(self.n_segments):
            self.slopes[i] = (y_hat[i+1]-y_hat[i]) / \
                        (self.fit_breaks[i+1]-self.fit_breaks[i])
        self.intercepts = y_hat[0:-1] - self.slopes*self.fit_breaks[0:-1]
        return self.slopes
