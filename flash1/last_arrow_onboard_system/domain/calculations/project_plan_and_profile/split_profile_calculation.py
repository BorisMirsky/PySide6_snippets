from .calculate_path import CalculatePath
# from calculations.del_points_profile_pwlf import del_PWLF
from .profile_pwlf import PWLF
import numpy as np
import pandas as pd
from tqdm import tqdm
# from copy import deepcopy
# from shapely.geometry import LineString


class ProfileCalculation:

    def __init__(self, pkt, recalculated_rix, initial_ur, v_max, lower_bound, upper_bound, token):

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
        self.ds = np.mean(self.upper_bound + self.lower_bound)/2

        # Токен
        self.token = token

        # Находим значение шага
        self.d = self.pkt[1] - self.pkt[0]

        # Ограничение на максимальный тип кривой для поиска функцией find_project
        self.max_curve_type = 10
        # Ограничение на минимальную длину элемента
        self.min_element_length = 5
        # Ограничение на минимальную длину нулевых значений в отводе
        self.min_zero_points_in_metres = 15
        # Ограничение на допустимую погрешность при проверки выполнения ограничений на сдвижки/подъемки
        self.possible_bound_accuracy_error = 0.1

        # добавка к эвольвенте для возможности приведения сдвижек к целевому значению
        # (т.е. мы будем минимизировать отклонение сдвижки относительно целевого значения, а не относительно нуля)
        self.add_evl, self.otvod_length = self.__get_add_evl()

        # Находим значение минимальной подъемки с учетом отвода
        self.lbound_with_otvod, self.first_otvod_point, self.last_otvod_point = self.__get_lbound_with_otvod()

        # Максимальное количество точек при расчете количества изломов
        self.max_points_in_straight = 500
        self.kf = 0
        # Количество изломов в одном участке
        self.step_const = 3

        # Значения точек излома
        self.breaks = None
        # Значения проектных стрел в точках излома
        self.y_vals = None
        # Перечень элементов (1 - переходная кривая, 0 - прямая/радиус)
        self.degree_list = None

    def __get_add_evl(self):  # TODO разобраться с отводами
        mean_prof = (self.upper_bound + self.lower_bound)/2
        otvod_length = int(np.ceil(np.mean(mean_prof) / self.d))
        if 2*otvod_length < len(self.pkt):
            add_evl = mean_prof
            add_evl[:otvod_length] = self.d * np.arange(otvod_length)
            add_evl[-otvod_length:] = self.d * np.arange(otvod_length)[::-1]
        else:
            otvod_length = int(len(self.pkt)/2)
            add_evl = mean_prof
            add_evl[:otvod_length] = self.d * np.arange(otvod_length)
            add_evl[-otvod_length:] = self.d * np.arange(otvod_length)[::-1]
        return add_evl, otvod_length

    def __get_lbound_with_otvod(self):

        lbound_with_otvod = np.copy(self.lower_bound)
        zero_points_in_otvod = int(np.ceil(self.min_zero_points_in_metres/self.d))
        if len(lbound_with_otvod) < 2*zero_points_in_otvod:
            zero_points_in_otvod = int(len(lbound_with_otvod)/2)

        lbound_with_otvod[:zero_points_in_otvod] = 0
        lbound_with_otvod[-zero_points_in_otvod:] = 0
        first_otvod_point = 0
        last_otvod_point = len(lbound_with_otvod) - 1

        for i in range(zero_points_in_otvod, int(len(lbound_with_otvod)/2)):
            u = self.d*(i - zero_points_in_otvod)
            if u < self.lower_bound[i]:
                lbound_with_otvod[i] = u
            else:
                first_otvod_point = i + 1
                break

        for i in range(len(lbound_with_otvod) - zero_points_in_otvod - 1, int(len(lbound_with_otvod)/2) - 1, -1):
            u = self.d*(len(lbound_with_otvod) - zero_points_in_otvod - i)
            if u < self.lower_bound[i]:
                lbound_with_otvod[i] = u
            else:
                last_otvod_point = i - 1
                break

        return lbound_with_otvod, first_otvod_point, last_otvod_point

    def __get_params(self, curve_type):

        sum_evl_to_zero = False

        degree_list = np.zeros(curve_type).astype(int)

        f = list()
        for i in range(curve_type):
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
            if (evl[i] < lb[i] - self.possible_bound_accuracy_error) | (evl[i] > ub[i] + self.possible_bound_accuracy_error):
                is_inside = False
                break
        return is_inside

    def __get_bounds_coords(self, x, y, lb, ub):
        lb_x = x + lb/1000
        lb_y = y + lb/1000
        ub_x = x + ub/1000
        ub_y = y + ub/1000
        """
        for i in range(1, len(self.x)):
            a = (self.x[i - 1], self.y[i - 1])
            b = (self.x[i], self.y[i])
            ub = np.abs(self.upper_bound[i]/1000)
            lb = np.abs(self.lower_bound[i]/1000)

            ab = LineString([a, b])
            left = ab.parallel_offset(ub, 'left')
            right = ab.parallel_offset(lb, 'right')
            c = left.boundary.geoms[1]
            d = right.boundary.geoms[0]  # note the different orientation for right offset
            ub_x[i] = c.x
            ub_y[i] = c.y
            lb_x[i] = d.x
            lb_y[i] = d.y
        """
        return lb_x, lb_y, ub_x, ub_y

    def calc_with_split(self):

        length_start = np.max([self.first_otvod_point, self.otvod_length]) + 1
        length_end = np.min([self.last_otvod_point, len(self.pkt) - self.otvod_length]) - 1

        lng_start = length_start
        lng_end = length_end

        if lng_start >= lng_end:
            return self.find_project(self.pkt, self.recalculated_rix, self.upper_bound, self.lbound_with_otvod, self.add_evl)

        first_breaks, first_y_vals, first_y_pred, first_sdv = self.find_project_del(self.pkt[:lng_start],
                                                                                    self.recalculated_rix[:lng_start],
                                                                                    self.upper_bound[:lng_start],
                                                                                    self.lbound_with_otvod[:lng_start],
                                                                                    self.add_evl[:lng_start],
                                                                                    self.pkt[0], self.pkt[length_start])

        last_breaks, last_y_vals, last_y_pred, last_sdv = self.find_project_del(self.pkt[lng_end:],
                                                                                self.recalculated_rix[lng_end:],
                                                                                self.upper_bound[lng_end:] - self.ds,
                                                                                self.lbound_with_otvod[lng_end:] - self.ds,
                                                                                self.add_evl[lng_end:] - self.ds,
                                                                                self.pkt[length_end], self.pkt[-1])

        # s1 = int(np.ceil(first_breaks[-1]/self.d))
        # s2 = int(np.ceil(last_breaks[0]/self.d))
        s1 = lng_start
        s2 = lng_end

        main_breaks, main_y_vals, main_y_pred, main_sdv = self.split_project(self.pkt[s1: s2],
                                                                             self.recalculated_rix[s1: s2],
                                                                             self.upper_bound[s1: s2] - self.ds,
                                                                             self.lbound_with_otvod[s1: s2] - self.ds,
                                                                             s1, s2)

        breaks = np.concatenate([first_breaks[:-1], main_breaks, last_breaks])
        y_vals = np.concatenate([first_y_vals[:-1], main_y_vals, last_y_vals])
        y_pred = np.concatenate([first_y_pred, main_y_pred, last_y_pred])
        sdv = np.concatenate([first_sdv, main_sdv, last_sdv + self.ds])

        # f_new = list()
        # for i in range(len(breaks) - 1):
        #     f_new.append(None)
        # f_new[4] = 0
        # f_new[8] = 0
        # dgr = np.zeros(len(f_new))
        # new_breaks, new_y_vals, new_y_pred, new_sdv = self.fixed_points_calculation(dgr, breaks, f_new)
        #
        # import matplotlib.pyplot as plt
        # plt.plot(self.pkt, self.recalculated_rix)
        # plt.plot(self.pkt, new_y_pred)
        # plt.show()
        # plt.plot(self.pkt, new_sdv)
        return breaks, y_vals, y_pred, sdv

    # Нахождение координат по стрелам
    def __find_coord(self, msv, x0, y0, d, machine_horde_1, machine_horde_2):
        x = np.zeros(len(msv))
        y = np.zeros(len(msv))

        x[0] = x0
        y[0] = y0
        for i in range(1, len(msv)):
            x[i] = x[i - 1] + d * np.cos(msv[i])
            y[i] = y[i - 1] + d * np.sin(msv[i])
        return x, y

    def __find_fi(self, msv, l1, l2):
        phi = np.zeros(len(msv))

        for i in range(len(msv)):
            if msv[i] == 0:
                phi[i] = 0
            else:
                x0 = (l1 + l2) / 2
                y0 = (msv[i] ** 2 - l1 * l2) / 2 / msv[i]
                r = np.sign(msv[i]) * (x0 ** 2 + y0 ** 2) ** 0.5
                phi[i] = np.arctan(1 / r)
        return phi

    def __find_psi(self, msv, d):
        return d * np.cumsum(msv)

    def split_project(self, x_str, y_str, ub, lb, length_start, length_end):
        y_modified = y_str - np.mean(y_str)
        phi = self.__find_fi(y_modified/1000, self.d, self.d)
        psi = self.__find_psi(phi, self.d)
        x, y = self.__find_coord(psi, 0, 0, self.d, self.d, self.d)
        lb_x, lb_y, ub_x, ub_y = self.__get_bounds_coords(x, y, lb, ub)

        add_evl = np.zeros(len(x_str))
        del_points_from_straight = self.__del_points_from_straight(length_start, length_end, x, y, lb_x, lb_y, ub_x, ub_y)
        idx = del_points_from_straight[-1]
        calc_path = CalculatePath(self.pkt[length_start: length_end], x, y, *del_points_from_straight[:-1], self.kf)
        critical_points = calc_path.calculate_straight_path()

        start_index = 0
        final_breaks = np.array([])
        final_y_vals = np.array([])
        final_y_pred = np.array([])
        final_sdv = np.array([])

        if self.step_const >= len(critical_points):
            breaks, y_vals, y_pred, sdv = self.find_project(x_str, y_str, ub, lb, add_evl)
            return breaks[:-1], y_vals[:-1], y_pred, sdv + self.ds

        for i in tqdm(range(self.step_const, len(critical_points), self.step_const)):
            if len(critical_points) - i <= self.step_const:
                breaks, y_vals, y_pred, sdv = self.find_project(x_str[start_index:],
                                                        y_str[start_index:],
                                                        ub[start_index:],
                                                        lb[start_index:],
                                                        add_evl[start_index:])
            else:
                end_point = int((idx[critical_points[i + 1]] + idx[critical_points[i]])/2)
                breaks, y_vals, y_pred, sdv = self.find_project(x_str[start_index:end_point],
                                                                y_str[start_index:end_point],
                                                                ub[start_index:end_point],
                                                                lb[start_index:end_point],
                                                                add_evl[start_index:end_point])
                start_index = end_point



            final_breaks = np.concatenate([final_breaks, breaks[:-1]])
            final_y_vals = np.concatenate([final_y_vals, y_vals[:-1]])
            final_y_pred = np.concatenate([final_y_pred, y_pred])
            final_sdv = np.concatenate([final_sdv, sdv + self.ds])

        return final_breaks, final_y_vals, final_y_pred, final_sdv

    def __del_points_from_straight(self, length_start, length_end, x, y, lb_x, lb_y, ub_x, ub_y):

        pkt = self.pkt[length_start: length_end]

        if len(pkt) <= self.max_points_in_straight:
            return pkt, x, y, lb_x, lb_y, ub_x, ub_y, np.arange(len(pkt))

        step = (pkt[-1] - pkt[0])/self.max_points_in_straight
        idx = list()
        i = pkt[0]

        while i < pkt[-1]:
            idx.append(np.argmin(np.abs(pkt - i)))
            i += step
        idx.append(np.argmin(np.abs(pkt - pkt[-1])))
        if idx[-1] == idx[-2]:
            idx.pop(-1)
        return pkt[idx], x[idx], y[idx], lb_x[idx], lb_y[idx], ub_x[idx], ub_y[idx], idx

    def find_project(self, x_str, y_str, ub, lb, add_evl):

        for i in range(2, self.max_curve_type + 1):
            f, degree_list, sum_evl_to_zero = self.__get_params(i)

            pwlf = PWLF(x_str, y_str, ubound=ub, lbound=lb,
                        add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                        end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                        de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
                        degree=degree_list, evl_minimize=True, constr=None)

            pwlf.fit(len(degree_list))
            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)
            y_pred = pwlf.predict(x_str, f)
            sdv = self.__get_sdv(y_str, y_pred)

            # import matplotlib.pyplot as plt
            # plt.plot(x_str, y_str)
            # plt.plot(x_str, y_pred)
            # plt.show()
            # plt.plot(x_str, sdv)
            # plt.plot(x_str, add_evl)
            # plt.plot(x_str, lb)
            # plt.plot(x_str, ub)
            # plt.show()

            if self.__check_inside_bounds(sdv, lb, ub):
                return breaks, y_vals, y_pred, sdv

        return None, None

    def find_project_del(self, x_str, y_str, ub, lb, add_evl, max_start_of_curve, min_end_of_curve):

        for i in range(2, self.max_curve_type + 1):
            f, degree_list, sum_evl_to_zero = self.__get_params(i)
            print(f)
            # pwlf = del_PWLF(x_str, y_str, max_start_of_curve, min_end_of_curve, ubound=ub, lbound=lb,
            #             add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
            #             end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
            #             de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
            #             degree=degree_list, evl_minimize=True, constr=None)

            pwlf = PWLF(x_str, y_str, ubound=ub, lbound=lb,
                        add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                        end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                        de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
                        degree=degree_list, evl_minimize=True, constr=None)

            pwlf.fit(len(degree_list))
            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)

            boolarr = (x_str >= breaks[0]) & (x_str <= breaks[-1])
            x = x_str[boolarr]
            y = y_str[boolarr]

            y_pred = pwlf.predict(x, f)
            sdv = self.__get_sdv(y, y_pred)

            # import matplotlib.pyplot as plt
            # plt.plot(x, y)
            # plt.plot(x, y_pred)
            # plt.show()
            # plt.plot(x, sdv)
            # plt.plot(x, add_evl[boolarr])
            # plt.plot(x, lb[boolarr])
            # plt.plot(x, ub[boolarr])
            # plt.show()

            if self.__check_inside_bounds(sdv, lb[boolarr], ub[boolarr]):
                return breaks, y_vals, y_pred, sdv

        return None, None

    def custom_calculation(self, degree_list, f, add_evl=0, sum_evl_to_zero=False, constr=None, disp_res=False):

        pwlf = PWLF(self.pkt, self.recalculated_rix, ubound=self.upper_bound, lbound=self.lbound_with_otvod,
                    add_evl=add_evl, f=f, token=self.token, maxiter=10**6,
                    end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                    de_workers=1, min_element_length=self.min_element_length, disp_res=disp_res, lapack_driver='gelsd',
                    degree=degree_list, evl_minimize=True, constr=constr)
        pwlf.fit(len(degree_list))
        breaks = pwlf.fit_breaks
        y_vals = pwlf.predict(breaks, f)
        y_pred = pwlf.predict(self.pkt, f)
        sdv = self.__get_sdv(self.recalculated_rix, y_pred)
        return pwlf, breaks, y_vals, y_pred, sdv

    def fixed_points_calculation(self, degree_list, breaks, f):
        pwlf = self.pwlf_init(degree_list, f, self.add_evl, sum_evl_to_zero=False)
        breaks, new_y_vals, y_pred = pwlf.solve_lsq_equal_constr(breaks, f)
        sdv = self.__get_sdv(self.recalculated_rix, y_pred)
        return breaks, new_y_vals, y_pred, sdv

    def pwlf_init(self, degree_list, f, add_evl, sum_evl_to_zero):
        pwlf = PWLF(self.pkt, self.recalculated_rix, ubound=self.upper_bound, lbound=self.lbound_with_otvod,
                    add_evl=add_evl, f=f, token=self.token, maxiter=10**6,
                    end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                    de_workers=1, min_element_length=self.min_element_length, disp_res=False, lapack_driver='gelsd',
                    degree=degree_list, evl_minimize=True, constr=None, gen_solution=False)
        return pwlf

    def get_track_split(self, breaks, y_vals):
        track_split = list()
        for i in range(len(breaks) - 1):
            radius = 500 * self.d ** 2 / y_vals[i]
            geom_type = "круговая кривая"
            if y_vals[i] == 0:
                geom_type = "прямая"
                radius = np.inf

            track_split.append([geom_type, breaks[i], breaks[i + 1], breaks[i + 1] - breaks[i], radius, np.nan])
        track_split = pd.DataFrame(track_split)
        track_split.columns = ["geom", "start", "end", "length", "radius", "level"]
        return track_split

    def change_horde(self, data, init_horde, horde_to_change):
        ih = 1000 * init_horde
        ch = 1000 * horde_to_change
        z = (data**2 + ih**2)/data/2
        new_data = z - np.sign(z)*(z**2 - ch**2)**0.5
        return new_data

    def calculate_track_parameters(self, breaks, y_vals, plan_prj, sdv):

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
        ev_table[:, 14] = self.upper_bound
        ev_table[:, 15] = self.lbound_with_otvod

        ev_table = pd.DataFrame(ev_table)
        ev_table.columns = self.__profile_column_names()
        return track_split, ev_table

    def __profile_column_names(self):
        return ["prof_fact", "First_prof", "Fact_Prof", "Sum_Fact_Prof", "EV", "Coord", "tangens", "Popravka", "8",
                "Popravka_razn", "prof_prj", "Fact_Prof_corr",
                "Sum_Fact_Prof_corr", "prof_delta", "ubound", "lbound", "vozv_fact", "V_max", "R", "a_nepog",
                "Max_v_dop", "Min_vozv", "l_perex", "mean_vozv", "Uklon_otvoda",
                "narast_a_nepog", "rail_length", "fastening_tmp", "ballast_need", "vozv_prj", "a_nepog_fact",
                "psi_fact", "v_wheel_fact", "a_nepog_prj", "psi_prj",
                "v_wheel_prj", "36", "37", "38", "39", "40", "41"]
