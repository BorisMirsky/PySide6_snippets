from .straight_pwlf import PWLF
import numpy as np
import pandas as pd
from tqdm import tqdm


class TrackCalculation:

    def __init__(self, pkt, recalculated_rix, initial_ur, v_max, lower_bound, upper_bound, token,
                 add_evl, start_in_curve=True, end_in_curve=True):

        # Пикетаж
        self.pkt = pkt
        # Значения натурных стрел на участке
        self.recalculated_rix = recalculated_rix
        # Значение уровня на участке
        self.ur = initial_ur

        # Скорости на участке
        self.v_max = v_max
        # Ограничения по сдвижкам на участке
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        # Токен
        self.token = token

        # добавка к эвольвенте для возможности приведения сдвижек к целевому значению
        # (т.е. мы будем минимизировать отклонение сдвижки относительно целевого значения, а не относительно нуля)
        self.add_evl = add_evl
        # Установка начала/конца участка (True - начало/конец с прямой или радиуса, False - начало/конец с переходной)
        self.start_in_curve = start_in_curve
        self.end_in_curve = end_in_curve

        # Ограничение на максимальный тип кривой для поиска функцией find_project
        self.max_curve_type = 7
        # Ограничение на минимальную длину элемента
        self.min_element_length = 20

        # Находим значение шага
        self.d = self.pkt[1] - self.pkt[0]
        # Значения точек излома
        self.breaks = None
        # Значения проектных стрел в точках излома
        self.y_vals = None
        # Перечень элементов (1 - переходная кривая, 0 - прямая/радиус)
        self.degree_list = None
        self.pwlf = None

    def __get_params(self, curve_type):

        sum_evl_to_zero = False
        if curve_type >= 14:
            sum_evl_to_zero = True

        degree_list = list((np.arange(2 * curve_type + 1)) % 2)
        if not self.start_in_curve:
            degree_list.pop(0)
        if not self.end_in_curve:
            degree_list.pop(-1)

        f = list()
        for i in range(curve_type + 1):
            f.append(None)

        return f, degree_list, sum_evl_to_zero

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

    def find_project(self):

        for i in tqdm(range(2, self.max_curve_type + 1)):
            f, degree_list, sum_evl_to_zero = self.__get_params(i)
            print("f:", f, "degree_list:", degree_list)

            pwlf = PWLF(self.pkt, self.recalculated_rix, add_evl=self.add_evl, f=f, token=self.token, maxiter=10**6,
                        end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                        de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
                        degree=degree_list, evl_minimize=True, constr=None)

            pwlf.fit(len(degree_list))
            breaks = pwlf.fit_breaks
            y_pred = pwlf.predict(self.pkt, f)
            sdv = self.__get_sdv(self.recalculated_rix, y_pred)

            if self.__check_inside_bounds(sdv, self.lower_bound, self.upper_bound):
                self.pwlf = pwlf
                self.breaks = breaks
                self.y_vals = pwlf.predict(self.breaks, f)
                self.degree_list = degree_list
                return y_pred, sdv

        return None, None

    def custom_calculation(self, degree_list, f, add_evl=0, sum_evl_to_zero=False, constr=None, disp_res=False):

        pwlf = PWLF(self.pkt, self.recalculated_rix, add_evl=add_evl, f=f, token=self.token, maxiter=10**6,
                    end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                    de_workers=1, min_element_length=self.min_element_length, disp_res=disp_res, lapack_driver='gelsd',
                    degree=degree_list, evl_minimize=True, constr=constr)
        pwlf.fit(len(degree_list))
        breaks = pwlf.fit_breaks
        y_vals = pwlf.predict(breaks, f)
        y_pred = pwlf.predict(self.pkt, f)
        sdv = self.__get_sdv(self.recalculated_rix, y_pred)
        return pwlf, breaks, y_vals, y_pred, sdv

    def fixed_points_calculation(self, pwlf, breaks, f):

        pwlf.fit_with_breaks(breaks, f)
        y_pred = pwlf.predict(self.pkt, f)
        new_y_vals = pwlf.predict(breaks, f)
        sdv = self.__get_sdv(self.recalculated_rix, y_pred)
        return breaks, new_y_vals, y_pred, sdv

    def pwlf_init(self, degree_list, f, add_evl, sum_evl_to_zero):
        pwlf = PWLF(self.pkt, self.recalculated_rix, add_evl=add_evl, f=f, token=self.token, maxiter=10**6,
                    end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                    de_workers=1, min_element_length=self.min_element_length, disp_res=False, lapack_driver='gelsd',
                    degree=degree_list, evl_minimize=True, constr=None)
        return pwlf

    def get_track_split(self, breaks, y_vals):
        track_split = list()
        for i in range(1, len(breaks)):
            radius = np.nan
            geom_type = "переходная кривая"
            if self.degree_list[i - 1] == 0:
                if y_vals[i] == 0:
                    geom_type = "прямая"
                    radius = np.inf
                else:
                    radius = 500*self.d**2/y_vals[i]
                    geom_type = "круговая кривая"

            track_split.append([geom_type, breaks[i - 1], breaks[i], breaks[i] - breaks[i - 1], radius, np.nan])
        track_split = pd.DataFrame(track_split)
        track_split.columns = ["geom", "start", "end", "length", "radius", "level"]
        return track_split

    def __get_vozv_prj(self, f_urov):

        urov_prj = np.zeros(len(self.pkt))
        urov_values = np.zeros(len(self.breaks))

        if f_urov is None:
            for i in range(1, len(self.breaks)):
                if self.degree_list[i - 1] == 0:
                    bool_arr = (self.pkt >= self.breaks[i - 1]) & (self.pkt <= self.breaks[i])
                    urov_values[i - 1] = np.mean(self.ur[bool_arr])
                    urov_values[i] = urov_values[i - 1]
        else:
            count = 0
            for i in range(1, len(self.breaks)):
                if self.degree_list[i - 1] == 0:
                    if f_urov[count] is not None:
                        urov_values[i - 1] = f_urov[count]
                    else:
                        bool_arr = (self.pkt >= self.breaks[i - 1]) & (self.pkt <= self.breaks[i])
                        urov_values[i - 1] = np.mean(self.ur[bool_arr])
                    urov_values[i] = urov_values[i - 1]
                    count += 1

        for i in range(1, len(self.breaks)):
            bool_arr = (self.pkt >= self.breaks[i - 1]) & (self.pkt <= self.breaks[i])
            if self.degree_list[i - 1] == 0:
                urov_prj[bool_arr] = urov_values[i]
            elif self.degree_list[i - 1] == 1:
                alpha = (urov_values[i] - urov_values[i - 1]) / (self.breaks[i] - self.breaks[i - 1])
                beta = urov_values[i] - alpha*self.breaks[i]
                urov_prj[bool_arr] = alpha*self.pkt[bool_arr] + beta

        return urov_prj

    def change_horde(self, data, init_horde, horde_to_change):
        ih = 1000 * init_horde
        ch = 1000 * horde_to_change
        z = (data**2 + ih**2)/data/2
        new_data = z - np.sign(z)*(z**2 - ch**2)**0.5
        return new_data

    def calculate_track_parameters(self, breaks, y_vals, plan_prj, sdv, f_urov=None):

        track_split = self.get_track_split(breaks, y_vals)

        n = len(self.recalculated_rix)
        ev_table = np.zeros((n, 42))
        ev_table[:, 0] = self.change_horde(self.recalculated_rix, init_horde=0.185, horde_to_change=10)

        # Дублируем расчет сдвижки для проверки
        ev_table[:, 2] = self.recalculated_rix
        ev_table[:, 3] = plan_prj
        ev_table[:, 4] = ev_table[:, 2] - ev_table[:, 3]
        ev_table[:, 5] = np.cumsum(ev_table[:, 4])
        ev_table[0, 6] = ev_table[0, 5]
        ev_table[1:, 6] = np.cumsum(ev_table[:-1, 5])

        ev_table[:, 10] = self.change_horde(plan_prj, init_horde=0.185, horde_to_change=10)
        ev_table[:, 13] = sdv
        ev_table[:, 16] = self.ur
        ev_table[:, 17] = self.v_max

        ev_table[:, 29] = self.__get_vozv_prj(f_urov)

        # Изменение длины рельса
        ev_table[:, 26] = 0.00002 * ev_table[:, 13] * ev_table[:, 10] * self.d
        # Изменение температуры закрепления
        ev_table[:, 27] = 0.00002 * ev_table[:, 13] * ev_table[:, 10] / 0.0118

        # Потребность в балласте
        # ev_table[:, 28] =

        # Непогашенное ускорение для натурных стрел
        ev_table[:, 30] = ev_table[:, 17] ** 2 * np.abs(ev_table[:, 0]) / 13 / 50000 - 0.0061 * ev_table[:, 16]
        # Непогашенное ускорение для проектных стрел
        ev_table[:, 33] = ev_table[:, 17] ** 2 * np.abs(ev_table[:, 10]) / 13 / 50000 - 0.0061 * ev_table[:, 29]

        # Скорость нарастания непогашенного ускорения для натурных стрел
        ev_table[1:, 31] = ev_table[1:, 17] * (ev_table[1:, 30] - ev_table[: -1, 30]) / 3.6 / self.d
        # Скорость подъема колеса на возвышение наружного рельса для натурных стрел
        ev_table[1:, 32] = ev_table[1:, 17] * (ev_table[1:, 16] - ev_table[: -1, 16]) / 3.6 / self.d
        # Скорость нарастания непогашенного ускорения для проектных стрел
        ev_table[1:, 34] = ev_table[1:, 17] * (ev_table[1:, 33] - ev_table[: -1, 33]) / 3.6 / self.d
        # Скорость подъема колеса на возвышение наружного рельса для проектных стрел
        ev_table[1:, 35] = ev_table[1:, 17] * (ev_table[1:, 29] - ev_table[: -1, 29]) / 3.6 / self.d

        ev_table = pd.DataFrame(ev_table)
        ev_table.columns = self.__plan_column_names()
        return track_split, ev_table

    def __plan_column_names(self):
        return ["plan_fact", "First_plan", "Fact_Plan", "Sum_Fact_Plan", "EV", "Coord", "tangens", "Popravka", "8",
                "Popravka_razn", "plan_prj", "Fact_Plan_corr", "Sum_Fact_Plan_corr", "plan_delta", "ubound", "lbound",
                "vozv_fact", "V_max", "R", "a_nepog", "Max_v_dop", "Min_vozv", "l_perex", "mean_vozv", "Uklon_otvoda",
                "narast_a_nepog", "rail_length", "fastening_tmp", "ballast_need", "vozv_prj", "a_nepog_fact",
                "psi_fact", "v_wheel_fact", "a_nepog_prj", "psi_prj", "v_wheel_prj", "36", "37", "38", "39", "40", "41"]
