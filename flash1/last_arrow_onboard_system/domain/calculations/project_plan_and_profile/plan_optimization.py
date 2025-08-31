from .smart_bounded_pwlf import PWLF
import numpy as np
# import matplotlib.pyplot as plt


class PlanOptimization:

    def __init__(self, pkt, recalculated_rix, lower_bound, upper_bound,
                 prev_y_data, prev_prj, prev_lb, prev_ub, delta_str_prev, summ_str, last_evl, summ_sdv,
                 min_radius_length, min_per_length, max_per_length,
                 degree_list, f, tol, token, add_evl, new_summ_str, new_evl, 
                 differential_evolution_tol,
                 differential_evolution_updating,
                 last_f=None):

        self.differential_evolution_tol = differential_evolution_tol
        self.differential_evolution_updating = differential_evolution_updating

        # Пикетаж
        self.pkt = pkt
        # Значения натурных стрел на участке
        self.recalculated_rix = recalculated_rix

        self.prev_y_data = prev_y_data
        self.prev_prj = prev_prj
        self.prev_lb = prev_lb
        self.prev_ub = prev_ub

        # Ограничения по сдвижкам на участке
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        # Токен
        self.token = token

        # Добавка к эвольвенте для возможности приведения сдвижек к целевому значению
        # (т.е. Мы будем минимизировать отклонение сдвижки относительно целевого значения, а не относительно нуля)
        self.add_evl = add_evl

        # Условие на равенство разности сумм натурных и проектных стрел заданному числу
        self.delta_str_to_zero = False
        # Условие на равенство эвольвенты заданному числу на конце участка
        self.evl_to_zero = False
        # Условие на равенство суммы сдвигов на участке заданному числу
        self.summ_evl_to_zero = False

        self.delta_str_prev = delta_str_prev
        self.summ_str = summ_str
        self.last_evl = last_evl
        self.summ_sdv = summ_sdv
        self.new_summ_str = new_summ_str
        self.new_evl = new_evl
        self.last_f = last_f

        # Ограничение на минимальную длину радиуса
        self.min_radius_length = min_radius_length
        # Ограничение на минимальную длину переходной на прямом участке
        self.min_per_length = min_per_length
        # Константы для поиска наличия кривой на участке
        self.length_start = 150
        self.min_delta_value = 0.003
        # Максимальная длина переходной для прямых участков
        self.max_per_length_for_straight = 50
        # Ограничение на максимальную длину переходной на прямом участке
        if max_per_length is None:
            self.max_per_length = self.__get_max_per_length()
        else:
            self.max_per_length = max_per_length
        # print(self.max_per_length)
        # Шаг уменьшения минимальной длины элемента в случае, если не получается провести расчет с текущим значением
        self.step_element_length_minimize = 5
        # Минимальная длина элемента (с меньшим значением расчет не имеет смысла)
        self.abs_min_length_elem = 3

        # Перечень элементов (1 - переходная кривая, 0 - прямая/радиус)
        self.degree_list = degree_list
        self.f = f
        self.tol = tol

    def __get_max_per_length(self):
        # Определяем, есть ли на участке хотя бы одна кривая, если нет, то ограничиваем
        # длину переходной заданным значением для прямой
        if len(self.pkt) <= self.length_start:
            return np.inf

        for i in range(1, len(self.pkt) - self.length_start):
            prev_mean_str_value = np.mean(self.recalculated_rix[:i])
            next_values = self.recalculated_rix[i: i + self.length_start]
            if np.min(np.abs(next_values - prev_mean_str_value)) >= self.min_delta_value:
                return np.inf
        return self.max_per_length_for_straight

    def __get_sdv(self, f, p):

        n = len(f)

        ev_table = np.zeros((n, 5))
        ev_table[:, 0] = f
        ev_table[:, 1] = p
        ev_table[:, 2] = ev_table[:, 0] - ev_table[:, 1]
        ev_table[0, 3] = ev_table[0, 2]

        for i in range(1, n):
            ev_table[i, 3] = ev_table[i - 1, 3] + ev_table[i, 2]

        ev_table[0, 4] = 0
        ev_table[1, 4] = ev_table[0, 3]

        for i in range(2, n):
            ev_table[i, 4] = ev_table[i - 1, 4] + ev_table[i - 1, 3]

        return 2*np.array(ev_table[:, 4])

    def __check_inside_bounds(self, evl, lb, ub):
        is_inside = True
        for i in range(len(evl)):
            if (evl[i] < lb[i]) | (evl[i] > ub[i]):
                is_inside = False
                break
        return is_inside

    def f_to_minimize(self, number_of_pkt, min_radius_length, min_per_length, delta_str_to_zero=False, end_evl_to_zero=False):
        ba = (self.pkt <= number_of_pkt)
        x = self.pkt[ba]
        y = self.recalculated_rix[ba]
        lb = self.lower_bound[ba]
        ub = self.upper_bound[ba]
        add_evl = self.add_evl[ba] - 2*self.last_evl

        f_value = np.copy(self.f)
        dgr_list = np.copy(self.degree_list)

        if int(delta_str_to_zero) + int(end_evl_to_zero) == 2:
            add_evl[-1] = 0
            if self.last_f is not None:
                dgr_list = list(np.concatenate([np.array(self.degree_list), np.array([1, 0])]))
                f_value = np.concatenate([np.array(f_value), np.array([self.last_f])])

        # Учитываем ограничения на длины круговых и переходных кривых
        lc_lbound = min_radius_length * np.ones(len(dgr_list))
        if f_value[0] is None:
            lc_lbound[0] = x[0] + min_radius_length
        else:
            lc_lbound[0] = x[0]

        # Учитываем ограничения на максимальную длину переходной (для прямых участков)
        lc_ubound = np.inf * np.ones(len(dgr_list))
        if int(delta_str_to_zero) + int(end_evl_to_zero) == 2:
            lc_ubound[-1] = x[-1] - min_radius_length
        else:
            lc_ubound[-1] = x[-1]

        for i in range(0, len(lc_ubound) - 1):
            if i % 2 == 1:
                lc_lbound[i] = min_per_length
                lc_ubound[i] = self.max_per_length

        constr = (lc_lbound, lc_ubound)

        if len(dgr_list) > len(self.degree_list):

            number_of_perex = np.sum(dgr_list)
            number_of_radius = len(dgr_list) - number_of_perex

            if x[-1] - x[0] <= min_radius_length * number_of_radius + min_per_length * number_of_perex:
                return 0, (None, None, None, None, None)

        pwlf = PWLF(x, y, ubound=ub, lbound=lb, add_evl=add_evl, degree=dgr_list, f=f_value, token=self.token,
                    count_with_weights=True, delta_str_prev=self.delta_str_prev,
                    differential_evolution_tol=self.differential_evolution_tol,
                    differential_evolution_updating=self.differential_evolution_updating,
                    delta_str_to_zero=delta_str_to_zero, end_evl_to_zero=end_evl_to_zero, summ_evl_to_zero=False,
                    summ_str=self.summ_str, summ_str_last_point=self.new_summ_str,
                    last_evl=self.last_evl - self.new_evl, summ_sdv=self.summ_sdv, maxiter=10 ** 6,
                    de_workers=1, min_element_length=min_radius_length, disp_res=False, lapack_driver='gelsd',
                    evl_minimize=True, constr=constr, gen_solution=True)

        pwlf.fit(len(dgr_list))

        breaks = pwlf.fit_breaks
        boolarr = (x >= breaks[0]) & (x <= breaks[-1])
        y_vals = pwlf.predict(breaks, f_value)
        y_pred = pwlf.predict(x[boolarr], f_value)
        y_full = np.concatenate([self.prev_y_data, y[boolarr]])
        y_pred_full = np.concatenate([self.prev_prj, y_pred])
        sdv_full = self.__get_sdv(y_full, y_pred_full)

        lb_full = np.concatenate([self.prev_lb, lb[boolarr]])
        ub_full = np.concatenate([self.prev_ub, ub[boolarr]])

        reward = int(self.__check_inside_bounds(sdv_full, lb_full, ub_full))

        # plt.plot(y_full)
        # plt.plot(y_pred_full)
        # plt.show()
        #
        # plt.plot(sdv_full)
        # plt.show()

        # n = 2*int(self.last_evl/self.summ_str) + 1
        # xx = -self.summ_str/n
        # h = np.concatenate([np.zeros(n), y])
        # h2 = np.concatenate([xx*np.ones(n), y_pred_full])
        # sdv_to_check = np.zeros_like(h)
        # sdv_to_check[1:] = np.cumsum(np.cumsum(h - h2, axis=0), axis=0)[:-1]

        result = (dgr_list, breaks, y_vals, y_pred, sdv_full)

        return reward, result

    def opt_algo(self, lb, ub, tol, min_radius_length, min_per_length):

        # TODO При сдвиге точки влево результат может внезапно получиться хуже в плане максимальной сдвижки.
        #  Суть в том, что мы минимизируем сумму квадратов сдвигов, но не максимальный сдвиг

        # TODO В идеале - ограничения на сдвижки должны задаваться при решении задачи регрессии,аналогично lsqlin MATLAB
        reward, res = self.f_to_minimize(ub, min_radius_length, min_per_length, delta_str_to_zero=True, end_evl_to_zero=True)
        if reward > 0.5:
            return ub, res, True

        x = (lb + ub) / 2
        result = None
        while (x - lb > tol) & (ub - x > tol):
            reward, res = self.f_to_minimize(x, min_radius_length, min_per_length)
            # print("x:", x, "reward:", reward)
            if reward < 0.5:
                ub = x
                x = (x + lb)/2
            else:
                lb = x
                x = (x + ub) / 2
                result = res
        return lb, result, False

    def find_project(self):

        number_of_perex = np.sum(self.degree_list)
        # Вычитаем 1, т.к. длина первого радиуса у нас может быть любой, не зависит от min_radius_length,
        # а последнего на последнем участке должна быть не меньше min_radius_length
        number_of_radius = len(self.degree_list) - number_of_perex - 1

        min_radius_length = self.min_radius_length + self.step_element_length_minimize
        min_per_length = self.min_per_length + self.step_element_length_minimize
        result = None

        while result is None:

            min_radius_length = np.max([min_radius_length - self.step_element_length_minimize, self.abs_min_length_elem])
            min_per_length = np.max([min_per_length - self.step_element_length_minimize, self.abs_min_length_elem])

            lb = self.pkt[0] + min_radius_length * number_of_radius + min_per_length * number_of_perex
            ub = self.pkt[-1]

            if ub > lb:
                x_opt, result, calculation_complete = self.opt_algo(lb, ub, self.tol, min_radius_length, min_per_length)
                if result is None:
                    print(f"try with min_radius_length={min_radius_length} and min_per_length={min_per_length}. Result is None")
                else:
                    print(f"try with min_radius_length={min_radius_length} and min_per_length={min_per_length}. Result breaks are {result[1]}")
            else:
                print(f"try with min_radius_length={min_radius_length} and min_per_length={min_per_length}. Length is too much!")

            if min_radius_length < self.abs_min_length_elem + 0.5:
                break

        if result is None:
            return None, None, None, None, None, None

        degree_list, breaks, y_vals, y_pred_full, sdv_full = result

        return degree_list, breaks, y_vals, y_pred_full, sdv_full, calculation_complete
