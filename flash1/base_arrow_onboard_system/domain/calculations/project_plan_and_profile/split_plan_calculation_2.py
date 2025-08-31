from .calculate_path import CalculatePath
from .bounded_pwlf import PWLF
from .del_points_plan_pwlf import del_PWLF
import numpy as np
import pandas as pd
from tqdm import tqdm
from copy import deepcopy


class PlanCalculation:

    def __init__(self, pkt, initial_rix, recalculated_rix, initial_ur, v_max, add_evl, lower_bound, upper_bound, token,
                 length_start=250, min_value=5, min_curve_value=5, max_curve_value=0):

        # Пикетаж
        self.pkt = pkt
        # Значения натурных стрел на участке
        self.recalculated_rix = recalculated_rix
        # Значение уровня на участке
        self.ur = initial_ur
        # Скорости на участке
        self.v_max = v_max

        # добавка к эвольвенте для возможности приведения сдвижек к целевому значению
        # (т.е. мы будем минимизировать отклонение сдвижки относительно целевого значения, а не относительно нуля)
        self.add_evl = add_evl

        # Ограничения по сдвижкам на участке
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        # Токен
        self.token = token

        # Находим значение шага
        self.d = self.pkt[1] - self.pkt[0]

        # Ограничение на минимальный тип кривой для поиска функцией find_project
        self.min_radius_number_value = 2
        # Ограничение на максимальный тип кривой для поиска функцией find_project
        self.max_curve_type = 7
        # Ограничение на минимальную длину радиуса
        self.min_element_length = 15
        # Ограничение на минимальную длину переходной на прямом участке
        self.min_per_length = 15
        # Ограничение на максимальную длину переходной на прямом участке
        self.max_per_length = 50

        # Максимальное количество точек при расчете количества изломов
        self.max_points_in_straight = 200
        self.kf = 0
        # Количество изломов в одном участке
        self.step_const = 2

        self.msv = initial_rix
        self.length_start = length_start
        self.min_value = min_value
        self.Rvalue = min_curve_value
        self.Rvalue2 = max_curve_value
        self.max_add_length = 500
        # Минимальное значение радиуса, при котором участок считаем прямым
        self.min_straight_radius = 7000
        self.min_number_of_critical_points_in_straight = 4

        # Значения точек излома
        self.breaks = None
        # Значения проектных стрел в точках излома
        self.y_vals = None
        # Перечень элементов (1 - переходная кривая, 0 - прямая/радиус)
        self.degree_list = None
        # Минимальное количество точек между кривыми 
        self.min_points_between_curves = 200

    def __get_params(self, curve_type, first_f_value, last_f_value, constr_to_first_point, constr_to_length_per, x_str):

        sum_evl_to_zero = False

        degree_list = (np.arange(2*curve_type + 1) % 2).astype(int)

        f = list()
        for i in range(curve_type + 1):
            f.append(None)
        f[0] = first_f_value
        f[-1] = last_f_value

        lc_lbound = self.min_element_length * np.ones(len(degree_list))
        lc_lbound[0] = x_str[0] + self.min_element_length
        lc_ubound = np.inf * np.ones(len(degree_list))
        lc_ubound[-1] = x_str[-1] - self.min_element_length

        if constr_to_length_per:
            for i in range(0, len(lc_ubound) - 1):
                if i % 2 == 1:
                    lc_lbound[i] = self.min_per_length
                    lc_ubound[i] = self.max_per_length

        if constr_to_first_point:
            lc_lbound[0] = x_str[0]
        constr = (lc_lbound, lc_ubound)

        return f, degree_list, sum_evl_to_zero, constr

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

    def __get_bounds_coords(self, x, y, lb, ub):
        lb_x = x + lb/1000
        lb_y = y + lb/1000
        ub_x = x + ub/1000
        ub_y = y + ub/1000
        return lb_x, lb_y, ub_x, ub_y

    def __track_split(self):
        n = len(self.msv)
        curve_list_with_params = list()

        i = -1
        while i < n - self.length_start:
            i = i + 1
            # Проверяем начало кривой
            if np.min(np.abs(self.msv[i: i + self.length_start])) >= self.min_value:
                # Нашли кривую
                sic = False
                eic = False
                znak = np.sign(np.mean(self.msv[i: i + self.length_start]))

            # Ищем минимальное значение для конца кривой
                j = i
                for j in range(i + 1, n):
                    if (znak > 0) & (self.msv[j] < self.Rvalue):
                        break
                    if (znak <= 0) & (self.msv[j] > -self.Rvalue):
                        break

            # Ищем максимальное значение для конца кривой
                s = j
                for s in range(j + 1, n):
                    if (znak > 0) & (self.msv[s] < -self.Rvalue2):
                        break
                    if (znak <= 0) & (self.msv[s] > self.Rvalue2):
                        break

            # Ищем максимальное значение для начала кривой
                hvalue = self.msv[i + self.length_start - 1]
                ii = i
                for ii in range(i + self.length_start - 1, -1, -1):
                    if (hvalue > 0) & (self.msv[ii] < self.Rvalue):
                        break
                    if (hvalue <= 0) & (self.msv[ii] > -self.Rvalue):
                        break

            # Ищем минимальное значение для начала кривой
                r = ii
                for r in range(ii - 1, -1, -1):
                    if (hvalue > 0) & (self.msv[r] < -self.Rvalue2):
                        break
                    if (hvalue <= 0) & (self.msv[r] > self.Rvalue2):
                        break

                if (ii == 0) & (np.abs(self.msv[ii]) > self.min_value):
                    sic = True

                if (j == n - 1) & (np.abs(self.msv[j]) > self.min_value):
                    eic = True

                curve_list_with_params.append([r, ii, j - 1, s - 1, sic, eic])
                i = j

        idx_to_del = list()
        for i in range(len(curve_list_with_params) - 1):
            if curve_list_with_params[i + 1][0] - curve_list_with_params[i][3] < self.min_points_between_curves:
                idx_to_del.append(i)
                curve_list_with_params[i + 1][0] = curve_list_with_params[i][0]
                curve_list_with_params[i + 1][1] = curve_list_with_params[i][0]

        for i in sorted(idx_to_del, reverse=True):
            del curve_list_with_params[i]

        return curve_list_with_params

    def __correct_curves(self, curve_list_with_params):

        curve_list = deepcopy(curve_list_with_params)

        curve_list[0][0] = np.max([0, curve_list[0][0] - self.max_add_length])
        curve_list[-1][3] = np.min([len(self.msv) - 1, curve_list[-1][3] + self.max_add_length])
        for i in range(1, len(curve_list)):

            w = curve_list[i][0] - curve_list[i - 1][3]

            if w > 2*self.max_add_length:
                curve_list[i][0] -= self.max_add_length
                curve_list[i - 1][3] += self.max_add_length
            else:
                curve_list[i][0] -= int(np.ceil(w/2))
                curve_list[i - 1][3] += int(np.floor(w/2))

        self.curve_list = curve_list
        return curve_list

    def __calc_curve_type(self, curve_list_with_params, curve_list_corrected):

        curve_list = list()
        for i in range(len(curve_list_corrected)):
            start_point = curve_list_corrected[i][0]
            end_point = curve_list_corrected[i][3]

            if i == 0:
                if curve_list_with_params[i][0] > 0:
                        first_value = np.mean(self.recalculated_rix[:curve_list_with_params[i][0]])
                else:
                    first_value = 0
            else:
                if curve_list_with_params[i][0] - curve_list_with_params[i - 1][3] > 0:
                    first_value = np.mean(self.recalculated_rix[curve_list_with_params[i - 1][3]:curve_list_with_params[i][0]])
                else:
                    first_value = 0

            if i == len(curve_list_corrected) - 1:
                if curve_list_with_params[i][3] < len(self.pkt) - 1:
                    last_value = np.mean(self.recalculated_rix[curve_list_with_params[i][3]:])
                else:
                    last_value = 0
            else:
                if curve_list_with_params[i + 1][0] - curve_list_with_params[i][3] > 0:
                    last_value = np.mean(self.recalculated_rix[curve_list_with_params[i][3]: curve_list_with_params[i + 1][0]])
                else:
                    last_value = 0

            curve_type, start_of_curve, end_of_curve = self.__get_curve(*self. __get_parts_of_track(start_point, end_point),
                                                                        max_start_of_curve=curve_list_corrected[i][1],
                                                                        min_end_of_curve=curve_list_corrected[i][2],
                                                                        first_value=first_value, last_value=last_value,
                                                                        sic=curve_list_corrected[i][4],
                                                                        eic=curve_list_corrected[i][5])
            curve_list.append([curve_type, start_of_curve, end_of_curve])

        return curve_list

    def __get_curve(self, x_str, y_str, add_evl, ub, lb, max_start_of_curve, min_end_of_curve, first_value, last_value, sic, eic):

        for curve_type in range(2, self.max_curve_type + 1):

            sum_evl_to_zero = False

            degree_list = list(np.arange(2 * curve_type + 1) % 2)

            f = list()
            for j in range(curve_type + 1):
                f.append(None)

            f[0] = first_value
            f[-1] = last_value

            pwlf = del_PWLF(x_str, y_str, ubound=ub, lbound=lb,
                            max_start_of_curve=self.pkt[max_start_of_curve], min_end_of_curve=self.pkt[min_end_of_curve],
                            add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                            end_evl_to_zero=False, summ_evl_to_zero=sum_evl_to_zero,
                            de_workers=1, min_element_length=self.min_element_length, disp_res=True,
                            lapack_driver='gelsd', degree=degree_list, evl_minimize=True, constr=None)

            pwlf.fit(len(degree_list))

            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)

            boolarr = (x_str >= breaks[0]) & (x_str <= breaks[-1])
            x = x_str[boolarr]
            y = y_str[boolarr]

            y_pred = pwlf.predict(x, f)
            sdv = self.__get_sdv(y, y_pred)

            if self.__check_inside_bounds(sdv, lb[boolarr], ub[boolarr]):

                start_of_curve = int(breaks[0] / self.d)
                end_of_curve = int(breaks[-1] / self.d) + 1
                return curve_type, start_of_curve, end_of_curve

        return self.max_curve_type + 1, max_start_of_curve, min_end_of_curve

    def __initial_split_with_params(self, curve_list):

        track_list = list()

        for i in range(len(curve_list)):
            if i == 0:
                if curve_list[0][1] == 0:
                    number_of_izlom_first = 0
                else:
                    critical_points, _ = self.__find_critical_points(0, curve_list[0][1])
                    number_of_izlom_first = len(critical_points) - 2
            else:
                critical_points, _ = self.__find_critical_points(curve_list[i - 1][2], curve_list[i][1])
                number_of_izlom_first = len(critical_points) - 2
                track_list[-1][-1] = len(critical_points) - 2
            track_list.append(curve_list[i] + [number_of_izlom_first] + [None])

        if curve_list[-1][2] < len(self.pkt) - 1:
            critical_points, _ = self.__find_critical_points(curve_list[i][2], len(self.pkt) - 1)
            track_list[-1][-1] = len(critical_points) - 2
        return track_list

    def __final_curve_calculation(self, length_start, length_end, start_curve_type, sic=False, eic=False):

        x_str, y_str, add_evl, ub, lb = self. __get_parts_of_track(length_start, length_end)

        for curve_type in range(start_curve_type, self.max_curve_type + 1):

            sum_evl_to_zero = False

            degree_list = list(np.arange(2 * curve_type + 1) % 2)

            f = list()
            for j in range(curve_type + 1):
                f.append(None)

            constr = None

            pwlf = PWLF(x_str, y_str, ubound=ub, lbound=lb,
                        add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                        end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                        de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
                        degree=degree_list, evl_minimize=True, constr=constr)

            pwlf.fit(len(degree_list))

            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)
            y_pred = pwlf.predict(x_str, f)
            sdv = self.__get_sdv(y_str, y_pred)

            if self.__check_inside_bounds(sdv, lb, ub):
                return degree_list, breaks, y_vals, y_pred, sdv

        return None, None, None, None, None

    def __get_final_split(self, track_list):

        final_list = list()
        for i in range(len(track_list)):
            if (track_list[i][3] < 2) & (track_list[i][4] < 2):
                if i == 0:
                    sp = 0
                else:
                    sp = int((track_list[i - 1][2] + track_list[i][1])/2)
                if i < len(track_list) - 1:
                    ep = int((track_list[i][2] + track_list[i + 1][1])/2)
                else:
                    ep = len(self.pkt)

            elif (track_list[i][3] >= 2) & (track_list[i][4] < 2):
                sp = track_list[i][1]
                if i < len(track_list) - 1:
                    ep = int((track_list[i][2] + track_list[i + 1][1])/2)
                else:
                    ep = len(self.pkt)

            elif (track_list[i][3] < 2) & (track_list[i][4] >= 2):
                if i == 0:
                    sp = 0
                else:
                    sp = int((track_list[i - 1][2] + track_list[i][1])/2)
                if i < len(track_list) - 1:
                    ep = track_list[i][2]

            else:
                sp = track_list[i][1]
                ep = track_list[i][2]

            result = self.__final_curve_calculation(sp, ep, track_list[i][0])
            final_list.append([sp, ep, result])
        return final_list

    def calc_with_split(self):

        curve_list_with_params = self.__track_split()
        if len(curve_list_with_params) == 0:
            final_result = self.split_project(0, len(self.pkt), None, None)
            self.degree_list = final_result[0]
            self.breaks = final_result[1]
            self.y_vals = final_result[2]
            return final_result

        curve_list_corrected = self.__correct_curves(curve_list_with_params)
        curve_list = self.__calc_curve_type(curve_list_with_params, curve_list_corrected)
        track_list = self.__initial_split_with_params(curve_list)
        print(track_list)
        final_list = self.__get_final_split(track_list)
        final_result = (np.array([]), np.array([]), np.array([]), np.array([]), np.array([]))

        if final_list[0][0] > 0:
            final_result = self.__concat_data(final_result, self.split_project(0, final_list[0][0], None, None))
        final_result = self.__concat_data(final_result, final_list[0][2])

        for i in range(1, len(final_list)):
            if final_list[i][0] - final_list[i - 1][1] > 1:
                final_result = self.__concat_data(final_result, self.split_project(final_list[i - 1][1], final_list[i][0], None, None))
            final_result = self.__concat_data(final_result, final_list[i][2])

        if final_list[-1][1] < len(self.pkt) - 1:
            final_result = self.__concat_data(final_result, self.split_project(final_list[-1][1], len(self.pkt), None, None))

        print(final_result[0], final_result[1], final_result[2])
        self.degree_list = final_result[0]
        self.breaks = final_result[1]
        self.y_vals = final_result[2]
        return final_result

    def __get_parts_of_track(self, length_start, length_end):
        pkt = self.pkt[length_start:length_end]
        recalculated_rix = self.recalculated_rix[length_start:length_end]
        add_evl = self.add_evl[length_start:length_end]
        upper_bound = self.upper_bound[length_start:length_end]
        lower_bound = self.lower_bound[length_start:length_end]
        return pkt, recalculated_rix, add_evl, upper_bound, lower_bound

    def __concat_data(self, result1, result2, del_last_element=False):

        degree_list, breaks, y_vals, y_pred, sdv = result1
        degree_list2, breaks2, y_vals2, y_pred2, sdv2 = result2

        if del_last_element:
            degree_list = np.concatenate([degree_list[: -1], degree_list2])
            breaks = np.concatenate([breaks, breaks2[1: -1]])
            y_vals = np.concatenate([y_vals, y_vals2[1: -1]])
        else:
            if len(result1[0]) > 0:
                degree_list = np.concatenate([degree_list, np.array([1])])
            degree_list = np.concatenate([degree_list, degree_list2])
            breaks = np.concatenate([breaks, breaks2])
            y_vals = np.concatenate([y_vals, y_vals2])
            # breaks = np.concatenate([breaks, breaks2[1:]])
            # y_vals = np.concatenate([y_vals, y_vals2[1:]])
        y_pred = np.concatenate([y_pred, y_pred2])
        sdv = np.concatenate([sdv, sdv2])

        return degree_list, breaks, y_vals, y_pred, sdv

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

    def __find_critical_points(self, length_start, length_end):

        x_str, y_str, add_evl, ub, lb = self.__get_parts_of_track(length_start, length_end)

        y_modified = y_str - np.mean(y_str)
        phi = self.__find_fi(y_modified/1000, self.d, self.d)
        psi = self.__find_psi(phi, self.d)
        x, y = self.__find_coord(psi, 0, 0, self.d, self.d, self.d)
        lb_x, lb_y, ub_x, ub_y = self.__get_bounds_coords(x, y, lb, ub)

        del_points_from_straight = self.__del_points_from_straight(length_start, length_end, x, y, lb_x, lb_y, ub_x, ub_y)
        idx = del_points_from_straight[-1]
        calc_path = CalculatePath(self.pkt[length_start: length_end], x, y, *del_points_from_straight[:-1], self.kf)
        critical_points = calc_path.calculate_straight_path()
        return critical_points, idx

    def split_project(self, length_start, length_end, first_value, last_value):
        x_str, y_str, add_evl, ub, lb = self.__get_parts_of_track(length_start, length_end)
        critical_points, idx = self.__find_critical_points(length_start, length_end)
        if len(critical_points) < self.step_const + 2:
            return self.find_project(x_str, y_str, add_evl, ub, lb, first_f_value=first_value, last_f_value=last_value)

        start_index = 0
        final_degree_list = np.array([])
        final_breaks = np.array([])
        final_y_vals = np.array([])
        final_y_pred = np.array([])
        final_sdv = np.array([])
        for i in tqdm(range(self.step_const, len(critical_points), self.step_const)):
            if i == self.step_const:
                first_f_value = first_value
                ctfp = False
            else:
                first_f_value = y_vals[-1]
                ctfp = True

            if len(critical_points) - i <= self.step_const:
                degree_list, breaks, y_vals, y_pred, sdv = self.find_project(x_str[start_index:],
                                                                             y_str[start_index:],
                                                                             add_evl[start_index:],
                                                                             ub[start_index:],
                                                                             lb[start_index:],
                                                                             first_f_value=first_f_value,
                                                                             last_f_value=last_value,
                                                                             constr_to_first_point=ctfp)
            else:
                end_point = int((idx[critical_points[i + 1]] + idx[critical_points[i]])/2)
                degree_list, breaks, y_vals, y_pred, sdv = self.find_project(x_str[start_index:end_point],
                                                                             y_str[start_index:end_point],
                                                                             add_evl[start_index:end_point],
                                                                             ub[start_index:end_point],
                                                                             lb[start_index:end_point],
                                                                             first_f_value=first_f_value,
                                                                             last_f_value=None,
                                                                             constr_to_first_point=ctfp)
                start_index = end_point

            final_degree_list = np.concatenate([final_degree_list, degree_list[:-1]])

            if i == self.step_const:
                final_breaks = np.concatenate([final_breaks, np.array([breaks[0]])])
                final_y_vals = np.concatenate([final_y_vals, np.array([y_vals[0]])])

            if len(critical_points) - i <= self.step_const:
                final_breaks = np.concatenate([final_breaks, breaks[1:]])
                final_y_vals = np.concatenate([final_y_vals, y_vals[1:]])
            else:
                final_breaks = np.concatenate([final_breaks, breaks[1: -1]])
                final_y_vals = np.concatenate([final_y_vals, y_vals[1: -1]])

            final_y_pred = np.concatenate([final_y_pred, y_pred])
            final_sdv = np.concatenate([final_sdv, sdv])

        final_degree_list = np.concatenate([final_degree_list, np.array([0])])
        return final_degree_list, final_breaks, final_y_vals, final_y_pred, final_sdv

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

    def find_project(self, x_str, y_str, add_evl, ub, lb, first_f_value, last_f_value, constr_to_first_point=False, constr_to_length_per=True):

        for i in range(self.min_radius_number_value, self.max_curve_type + 1):
            f, degree_list, sum_evl_to_zero, constr = self.__get_params(i, first_f_value, last_f_value, constr_to_first_point, constr_to_length_per, x_str)

            pwlf = PWLF(x_str, y_str, ubound=ub, lbound=lb,
                        add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                        end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                        de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
                        degree=degree_list, evl_minimize=True, constr=constr)

            pwlf.fit(len(degree_list))
            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)
            y_pred = pwlf.predict(x_str, f)
            sdv = self.__get_sdv(y_str, y_pred)

            if self.__check_inside_bounds(sdv, lb, ub):
                return degree_list, breaks, y_vals, y_pred, sdv

        return None, None

    def custom_calculation(self, degree_list, f, add_evl=0, sum_evl_to_zero=False, constr=None, disp_res=False):

        pwlf = PWLF(self.pkt, self.recalculated_rix, ubound=self.upper_bound, lbound=self.lower_bound,
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
        pwlf = PWLF(self.pkt, self.recalculated_rix, ubound=self.upper_bound, lbound=self.lower_bound,
                    add_evl=add_evl, f=f, token=self.token, maxiter=10**6,
                    end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                    de_workers=1, min_element_length=self.min_element_length, disp_res=False, lapack_driver='gelsd',
                    degree=degree_list, evl_minimize=True, constr=None, gen_solution=False)
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

    def __get_vozv_prj(self, f_urov, track_split):

        urov_prj = np.zeros(len(self.pkt))
        urov_values = np.zeros(len(self.breaks))

        if f_urov is None:
            for i in range(1, len(self.breaks)):
                if self.degree_list[i - 1] == 0:
                    if np.abs(track_split.radius.iloc[i - 1]) < self.min_straight_radius:
                        bool_arr = (self.pkt >= self.breaks[i - 1]) & (self.pkt <= self.breaks[i])
                        urov_values[i - 1] = np.mean(self.ur[bool_arr])
                        urov_values[i] = urov_values[i - 1]
                    else:
                        urov_values[i - 1] = 0
                        urov_values[i] = 0
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
        ev_table[:, 14] = self.upper_bound
        ev_table[:, 15] = self.lower_bound
        ev_table[:, 16] = self.ur
        ev_table[:, 17] = self.v_max

        ev_table[:, 29] = self.__get_vozv_prj(f_urov, track_split)

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
        return ["plan_fact", "First_plan", "Fact_Plan", "plan_prj_0185", "EV", "Coord", "tangens", "Popravka", "8",
                "Popravka_razn", "plan_prj", "Fact_Plan_corr", "Sum_Fact_Plan_corr", "plan_delta", "ubound", "lbound",
                "vozv_fact", "V_max", "R", "a_nepog", "Max_v_dop", "Min_vozv", "l_perex", "mean_vozv", "Uklon_otvoda",
                "narast_a_nepog", "rail_length", "fastening_tmp", "ballast_need", "vozv_prj", "a_nepog_fact",
                "psi_fact", "v_wheel_fact", "a_nepog_prj", "psi_prj", "v_wheel_prj", "36", "37", "38", "39", "40", "41"]

class PlanCalculationV2:

    def __init__(self, pkt, initial_rix, recalculated_rix, initial_ur, v_max, add_evl, lower_bound, upper_bound, token,
                 length_start=250, min_value=5, min_curve_value=5, max_curve_value=0):

        # Пикетаж
        self.pkt = pkt
        # Значения натурных стрел на участке
        self.recalculated_rix = recalculated_rix
        # Значение уровня на участке
        self.ur = initial_ur
        # Скорости на участке
        self.v_max = v_max

        # добавка к эвольвенте для возможности приведения сдвижек к целевому значению
        # (т.е. мы будем минимизировать отклонение сдвижки относительно целевого значения, а не относительно нуля)
        self.add_evl = add_evl

        # Ограничения по сдвижкам на участке
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        # Токен
        self.token = token

        # Находим значение шага
        self.d = self.pkt[1] - self.pkt[0]

        # Ограничение на минимальный тип кривой для поиска функцией find_project
        self.min_radius_number_value = 2
        # Ограничение на максимальный тип кривой для поиска функцией find_project
        self.max_curve_type = 7
        # Ограничение на минимальную длину радиуса
        self.min_element_length = 15
        # Ограничение на минимальную длину переходной на прямом участке
        self.min_per_length = 15
        # Ограничение на максимальную длину переходной на прямом участке
        self.max_per_length = 50

        # Максимальное количество точек при расчете количества изломов
        self.max_points_in_straight = 200
        self.kf = 0
        # Количество изломов в одном участке
        self.step_const = 2

        self.msv = initial_rix
        self.length_start = length_start
        self.min_value = min_value
        self.Rvalue = min_curve_value
        self.Rvalue2 = max_curve_value
        self.max_add_length = 500
        # Минимальное значение радиуса, при котором участок считаем прямым
        self.min_straight_radius = 7000
        self.min_number_of_critical_points_in_straight = 4

        # Значения точек излома
        self.breaks = None
        # Значения проектных стрел в точках излома
        self.y_vals = None
        # Перечень элементов (1 - переходная кривая, 0 - прямая/радиус)
        self.degree_list = None
        # Минимальное количество точек между кривыми 
        self.min_points_between_curves = 200

    def __get_params(self, curve_type, first_f_value, last_f_value, constr_to_first_point, constr_to_length_per, x_str):

        sum_evl_to_zero = False

        degree_list = (np.arange(2*curve_type + 1) % 2).astype(int)

        f = list()
        for i in range(curve_type + 1):
            f.append(None)
        f[0] = first_f_value
        f[-1] = last_f_value

        lc_lbound = self.min_element_length * np.ones(len(degree_list))
        lc_lbound[0] = x_str[0] + self.min_element_length
        lc_ubound = np.inf * np.ones(len(degree_list))
        lc_ubound[-1] = x_str[-1] - self.min_element_length

        if constr_to_length_per:
            for i in range(0, len(lc_ubound) - 1):
                if i % 2 == 1:
                    lc_lbound[i] = self.min_per_length
                    lc_ubound[i] = self.max_per_length

        if constr_to_first_point:
            lc_lbound[0] = x_str[0]
        constr = (lc_lbound, lc_ubound)

        return f, degree_list, sum_evl_to_zero, constr

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

    def __get_bounds_coords(self, x, y, lb, ub):
        lb_x = x + lb/1000
        lb_y = y + lb/1000
        ub_x = x + ub/1000
        ub_y = y + ub/1000
        return lb_x, lb_y, ub_x, ub_y

    def __track_split(self):
        n = len(self.msv)
        curve_list_with_params = list()

        i = -1
        while i < n - self.length_start:
            i = i + 1
            # Проверяем начало кривой
            if np.min(np.abs(self.msv[i: i + self.length_start])) >= self.min_value:
                # Нашли кривую
                sic = False
                eic = False
                znak = np.sign(np.mean(self.msv[i: i + self.length_start]))

            # Ищем минимальное значение для конца кривой
                j = i
                for j in range(i + 1, n):
                    if (znak > 0) & (self.msv[j] < self.Rvalue):
                        break
                    if (znak <= 0) & (self.msv[j] > -self.Rvalue):
                        break

            # Ищем максимальное значение для конца кривой
                s = j
                for s in range(j + 1, n):
                    if (znak > 0) & (self.msv[s] < -self.Rvalue2):
                        break
                    if (znak <= 0) & (self.msv[s] > self.Rvalue2):
                        break

            # Ищем максимальное значение для начала кривой
                hvalue = self.msv[i + self.length_start - 1]
                ii = i
                for ii in range(i + self.length_start - 1, -1, -1):
                    if (hvalue > 0) & (self.msv[ii] < self.Rvalue):
                        break
                    if (hvalue <= 0) & (self.msv[ii] > -self.Rvalue):
                        break

            # Ищем минимальное значение для начала кривой
                r = ii
                for r in range(ii - 1, -1, -1):
                    if (hvalue > 0) & (self.msv[r] < -self.Rvalue2):
                        break
                    if (hvalue <= 0) & (self.msv[r] > self.Rvalue2):
                        break

                if (ii == 0) & (np.abs(self.msv[ii]) > self.min_value):
                    sic = True

                if (j == n - 1) & (np.abs(self.msv[j]) > self.min_value):
                    eic = True

                curve_list_with_params.append([r, ii, j - 1, s - 1, sic, eic])
                i = j

        idx_to_del = list()
        for i in range(len(curve_list_with_params) - 1):
            if curve_list_with_params[i + 1][0] - curve_list_with_params[i][3] < self.min_points_between_curves:
                idx_to_del.append(i)
                curve_list_with_params[i + 1][0] = curve_list_with_params[i][0]
                curve_list_with_params[i + 1][1] = curve_list_with_params[i][0]

        for i in sorted(idx_to_del, reverse=True):
            del curve_list_with_params[i]

        return curve_list_with_params
    
    def __correct_curves(self, curve_list_with_params):

        curve_list = deepcopy(curve_list_with_params)

        curve_list[0][0] = np.max([0, curve_list[0][0] - self.max_add_length])
        curve_list[-1][3] = np.min([len(self.msv) - 1, curve_list[-1][3] + self.max_add_length])
        for i in range(1, len(curve_list)):

            w = curve_list[i][0] - curve_list[i - 1][3]

            if w > 2*self.max_add_length:
                curve_list[i][0] -= self.max_add_length
                curve_list[i - 1][3] += self.max_add_length
            else:
                curve_list[i][0] -= int(np.ceil(w/2))
                curve_list[i - 1][3] += int(np.floor(w/2))

        self.curve_list = curve_list
        return curve_list

    def __calc_curve_type(self, curve_list_with_params, curve_list_corrected):

        curve_list = list()
        for i in range(len(curve_list_corrected)):
            start_point = curve_list_corrected[i][0]
            end_point = curve_list_corrected[i][3]

            if i == 0:
                if curve_list_with_params[i][0] > 0:
                        first_value = np.mean(self.recalculated_rix[:curve_list_with_params[i][0]])
                else:
                    first_value = 0
            else:
                if curve_list_with_params[i][0] - curve_list_with_params[i - 1][3] > 0:
                    first_value = np.mean(self.recalculated_rix[curve_list_with_params[i - 1][3]:curve_list_with_params[i][0]])
                else:
                    first_value = 0

            if i == len(curve_list_corrected) - 1:
                if curve_list_with_params[i][3] < len(self.pkt) - 1:
                    last_value = np.mean(self.recalculated_rix[curve_list_with_params[i][3]:])
                else:
                    last_value = 0
            else:
                if curve_list_with_params[i + 1][0] - curve_list_with_params[i][3] > 0:
                    last_value = np.mean(self.recalculated_rix[curve_list_with_params[i][3]: curve_list_with_params[i + 1][0]])
                else:
                    last_value = 0

            curve_type, start_of_curve, end_of_curve = self.__get_curve(*self. __get_parts_of_track(start_point, end_point),
                                                                        max_start_of_curve=curve_list_corrected[i][1],
                                                                        min_end_of_curve=curve_list_corrected[i][2],
                                                                        # first_value=0, last_value=0,
                                                                        first_value=first_value, last_value=last_value,
                                                                        sic=curve_list_corrected[i][4],
                                                                        eic=curve_list_corrected[i][5])
            curve_list.append([curve_type, start_of_curve, end_of_curve])

        return curve_list

    def __get_curve(self, x_str, y_str, add_evl, ub, lb, max_start_of_curve, min_end_of_curve, first_value, last_value, sic, eic):

        for curve_type in range(2, self.max_curve_type + 1):

            sum_evl_to_zero = False

            degree_list = list(np.arange(2 * curve_type + 1) % 2)

            f = list()
            for j in range(curve_type + 1):
                f.append(None)

            f[0] = first_value
            f[-1] = last_value

            pwlf = del_PWLF(x_str, y_str, ubound=ub, lbound=lb,
                            max_start_of_curve=self.pkt[max_start_of_curve], min_end_of_curve=self.pkt[min_end_of_curve],
                            add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                            end_evl_to_zero=False, summ_evl_to_zero=sum_evl_to_zero,
                            de_workers=1, min_element_length=self.min_element_length, disp_res=True,
                            lapack_driver='gelsd', degree=degree_list, evl_minimize=True, constr=None)

            pwlf.fit(len(degree_list))

            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)

            boolarr = (x_str >= breaks[0]) & (x_str <= breaks[-1])
            x = x_str[boolarr]
            y = y_str[boolarr]

            y_pred = pwlf.predict(x, f)
            sdv = self.__get_sdv(y, y_pred)

            if self.__check_inside_bounds(sdv, lb[boolarr], ub[boolarr]):

                start_of_curve = int(breaks[0] / self.d)
                end_of_curve = int(breaks[-1] / self.d) + 1
                return curve_type, start_of_curve, end_of_curve

        return self.max_curve_type + 1, max_start_of_curve, min_end_of_curve

    def __get_correct_point_index(self, idx, critical_points, start_point_index, end_point_index):
        sp = None
        ep = None
        if len(critical_points) > 2:
            sp = int(idx[critical_points[1]]/2) + start_point_index
            ep = int((idx[critical_points[-2]] + idx[critical_points[-1]])/2) + start_point_index
        return sp, ep

    def __initial_split_with_params(self, curve_list):

        track_list = list()

        for i in range(len(curve_list)):
            if i == 0:
                if curve_list[0][1] == 0:
                    number_of_izlom_first = 0
                    sp = None
                    ep = None
                else:
                    critical_points, idx = self.__find_critical_points(0, curve_list[0][1])
                    number_of_izlom_first = len(critical_points) - 2
                    sp, ep = self.__get_correct_point_index(idx, critical_points, 0, curve_list[0][1])
            else:
                critical_points, idx = self.__find_critical_points(curve_list[i - 1][2], curve_list[i][1])
                number_of_izlom_first = len(critical_points) - 2
                sp, ep = self.__get_correct_point_index(idx, critical_points, curve_list[i - 1][2], curve_list[i][1])
                track_list[-1][-3] = len(critical_points) - 2
                track_list[-1][-1] = sp
            track_list.append(curve_list[i] + [number_of_izlom_first] + [None] + [ep] + [None])

        if curve_list[-1][2] < len(self.pkt) - 1:
            critical_points, idx = self.__find_critical_points(curve_list[i][2], len(self.pkt) - 1)
            track_list[-1][-3] = len(critical_points) - 2
            if len(critical_points) - 2 > 0:
                sp, ep = self.__get_correct_point_index(idx, critical_points, curve_list[i][2], len(self.pkt) - 1)
            track_list[-1][-1] = sp
        else:
            track_list[-1][-3] = 0
        return track_list

    def __final_curve_calculation(self, length_start, length_end, start_curve_type, sic=False, eic=False):

        x_str, y_str, add_evl, ub, lb = self. __get_parts_of_track(length_start, length_end)

        for curve_type in tqdm(range(start_curve_type, self.max_curve_type + 1)):

            sum_evl_to_zero = False

            degree_list = list(np.arange(2 * curve_type + 1) % 2)

            f = list()
            for j in range(curve_type + 1):
                f.append(None)

            lc_lbound = self.min_element_length*np.ones(len(degree_list))
            lc_lbound[0] = x_str[0]
            lc_ubound = np.inf*np.ones(len(degree_list))
            lc_ubound[-1] = x_str[-1]
            constr = (lc_lbound, lc_ubound)

            pwlf = PWLF(x_str, y_str, ubound=ub, lbound=lb,
                        add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                        end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                        de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
                        degree=degree_list, evl_minimize=True, constr=constr)

            pwlf.fit(len(degree_list))

            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)
            y_pred = pwlf.predict(x_str, f)
            sdv = self.__get_sdv(y_str, y_pred)

            if self.__check_inside_bounds(sdv, lb, ub):
                return degree_list, breaks, y_vals, y_pred, sdv

        return None, None, None, None, None

    def __get_final_split(self, track_list):

        final_list = list()
        for i in range(len(track_list)):
            if (track_list[i][3] < 2) & (track_list[i][4] < 2):
                if i == 0:
                    sp = 0
                else:
                    sp = int((track_list[i - 1][2] + track_list[i][1])/2)
                if i < len(track_list) - 1:
                    ep = int((track_list[i][2] + track_list[i + 1][1])/2)
                else:
                    ep = len(self.pkt)

            elif (track_list[i][3] >= 2) & (track_list[i][4] < 2):
                sp = track_list[i][5]
                if i < len(track_list) - 1:
                    ep = int((track_list[i][2] + track_list[i + 1][1])/2)
                else:
                    ep = len(self.pkt)

            elif (track_list[i][3] < 2) & (track_list[i][4] >= 2):
                if i == 0:
                    sp = 0
                else:
                    sp = int((track_list[i - 1][2] + track_list[i][1])/2)
                if i < len(track_list) - 1:
                    ep = track_list[i][6]

            else:
                sp = track_list[i][5]
                ep = track_list[i][6]

            result = self.__final_curve_calculation(sp, ep, track_list[i][0])
            final_list.append([sp, ep, result])
        return final_list

    def calc_with_split(self):

        curve_list_with_params = self.__track_split()
        if len(curve_list_with_params) == 0:
            final_result = self.split_project(0, len(self.pkt), None, None)
            self.degree_list = final_result[0]
            self.breaks = final_result[1]
            self.y_vals = final_result[2]
            return final_result

        curve_list_corrected = self.__correct_curves(curve_list_with_params)
        curve_list = self.__calc_curve_type(curve_list_with_params, curve_list_corrected)
        track_list = self.__initial_split_with_params(curve_list)
        final_list = self.__get_final_split(track_list)
        final_result = (np.array([]), np.array([]), np.array([]), np.array([]), np.array([]))

        if final_list[0][0] > 0:
            final_result = self.__concat_data(final_result, self.split_project(0, final_list[0][0], None, None))
            final_result = self.__concat_data(final_result, final_list[0][2])
        else:
            final_result = self.__concat_data(final_result, final_list[0][2])
            rs = list(final_result)
            rs[0] = rs[0][1:]
            final_result = tuple(rs)

        for i in range(1, len(final_list)):
            if final_list[i][0] - final_list[i - 1][1] > 1:
                final_result = self.__concat_data(final_result, self.split_project(final_list[i - 1][1], final_list[i][0], None, None))
            final_result = self.__concat_data(final_result, final_list[i][2])

        if final_list[-1][1] < len(self.pkt) - 1:
            final_result = self.__concat_data(final_result, self.split_project(final_list[-1][1], len(self.pkt), None, None))

        self.degree_list = final_result[0]
        self.breaks = final_result[1]
        self.y_vals = final_result[2]
        return final_result

    def __get_parts_of_track(self, length_start, length_end):
        pkt = self.pkt[length_start:length_end]
        recalculated_rix = self.recalculated_rix[length_start:length_end]
        add_evl = self.add_evl[length_start:length_end]
        upper_bound = self.upper_bound[length_start:length_end]
        lower_bound = self.lower_bound[length_start:length_end]
        return pkt, recalculated_rix, add_evl, upper_bound, lower_bound

    def __concat_data(self, result1, result2, del_last_element=False):

        degree_list, breaks, y_vals, y_pred, sdv = result1
        degree_list2, breaks2, y_vals2, y_pred2, sdv2 = result2

        if del_last_element:
            degree_list = np.concatenate([degree_list[: -1], degree_list2])
            breaks = np.concatenate([breaks, breaks2[1: -1]])
            y_vals = np.concatenate([y_vals, y_vals2[1: -1]])
        else:
            degree_list = np.concatenate([degree_list, np.array([1])])
            degree_list = np.concatenate([degree_list, degree_list2])
            breaks = np.concatenate([breaks, breaks2])
            y_vals = np.concatenate([y_vals, y_vals2])

        y_pred = np.concatenate([y_pred, y_pred2])
        sdv = np.concatenate([sdv, sdv2])

        return degree_list, breaks, y_vals, y_pred, sdv

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

    def __find_critical_points(self, length_start, length_end):

        x_str, y_str, add_evl, ub, lb = self.__get_parts_of_track(length_start, length_end)

        y_modified = y_str - np.mean(y_str)
        phi = self.__find_fi(y_modified/1000, self.d, self.d)
        psi = self.__find_psi(phi, self.d)
        x, y = self.__find_coord(psi, 0, 0, self.d, self.d, self.d)
        lb_x, lb_y, ub_x, ub_y = self.__get_bounds_coords(x, y, lb, ub)

        del_points_from_straight = self.__del_points_from_straight(length_start, length_end, x, y, lb_x, lb_y, ub_x, ub_y)
        idx = del_points_from_straight[-1]
        calc_path = CalculatePath(self.pkt[length_start: length_end], x, y, *del_points_from_straight[:-1], self.kf)
        critical_points = calc_path.calculate_straight_path()
        return critical_points, idx

    def split_project(self, length_start, length_end, first_value, last_value):
        x_str, y_str, add_evl, ub, lb = self.__get_parts_of_track(length_start, length_end)
        critical_points, idx = self.__find_critical_points(length_start, length_end)
        if len(critical_points) < self.step_const + 2:
            return self.find_project(x_str, y_str, add_evl, ub, lb, first_f_value=first_value, last_f_value=last_value)

        start_index = 0
        final_degree_list = np.array([])
        final_breaks = np.array([])
        final_y_vals = np.array([])
        final_y_pred = np.array([])
        final_sdv = np.array([])
        for i in tqdm(range(self.step_const, len(critical_points), self.step_const)):
            if i == self.step_const:
                first_f_value = first_value
                ctfp = False
            else:
                first_f_value = y_vals[-1]
                ctfp = True

            if len(critical_points) - i <= self.step_const:
                degree_list, breaks, y_vals, y_pred, sdv = self.find_project(x_str[start_index:],
                                                                             y_str[start_index:],
                                                                             add_evl[start_index:],
                                                                             ub[start_index:],
                                                                             lb[start_index:],
                                                                             first_f_value=first_f_value,
                                                                             last_f_value=last_value,
                                                                             constr_to_first_point=ctfp)
            else:
                end_point = int((idx[critical_points[i + 1]] + idx[critical_points[i]])/2)
                degree_list, breaks, y_vals, y_pred, sdv = self.find_project(x_str[start_index:end_point],
                                                                             y_str[start_index:end_point],
                                                                             add_evl[start_index:end_point],
                                                                             ub[start_index:end_point],
                                                                             lb[start_index:end_point],
                                                                             first_f_value=first_f_value,
                                                                             last_f_value=None,
                                                                             constr_to_first_point=ctfp)
                start_index = end_point

            final_degree_list = np.concatenate([final_degree_list, degree_list[:-1]])

            if i == self.step_const:
                final_breaks = np.concatenate([final_breaks, np.array([breaks[0]])])
                final_y_vals = np.concatenate([final_y_vals, np.array([y_vals[0]])])

            if len(critical_points) - i <= self.step_const:
                final_breaks = np.concatenate([final_breaks, breaks[1:]])
                final_y_vals = np.concatenate([final_y_vals, y_vals[1:]])
            else:
                final_breaks = np.concatenate([final_breaks, breaks[1: -1]])
                final_y_vals = np.concatenate([final_y_vals, y_vals[1: -1]])

            final_y_pred = np.concatenate([final_y_pred, y_pred])
            final_sdv = np.concatenate([final_sdv, sdv])

        final_degree_list = np.concatenate([final_degree_list, np.array([0])])
        return final_degree_list, final_breaks, final_y_vals, final_y_pred, final_sdv

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

    def find_project(self, x_str, y_str, add_evl, ub, lb, first_f_value, last_f_value, constr_to_first_point=False, constr_to_length_per=True):

        for i in tqdm(range(self.min_radius_number_value, self.max_curve_type + 1)):
            f, degree_list, sum_evl_to_zero, constr = self.__get_params(i, first_f_value, last_f_value, constr_to_first_point, constr_to_length_per, x_str)

            pwlf = PWLF(x_str, y_str, ubound=ub, lbound=lb,
                        add_evl=add_evl, f=f, token=self.token, count_with_weights=True, maxiter=10**6,
                        end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                        de_workers=1, min_element_length=self.min_element_length, disp_res=True, lapack_driver='gelsd',
                        degree=degree_list, evl_minimize=True, constr=constr)

            pwlf.fit(len(degree_list))
            breaks = pwlf.fit_breaks
            y_vals = pwlf.predict(breaks, f)
            y_pred = pwlf.predict(x_str, f)
            sdv = self.__get_sdv(y_str, y_pred)

            if self.__check_inside_bounds(sdv, lb, ub):
                return degree_list, breaks, y_vals, y_pred, sdv

        return None, None

    def custom_calculation(self, degree_list, f, add_evl=0, sum_evl_to_zero=False, constr=None, disp_res=False):

        pwlf = PWLF(self.pkt, self.recalculated_rix, ubound=self.upper_bound, lbound=self.lower_bound,
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
        pwlf = PWLF(self.pkt, self.recalculated_rix, ubound=self.upper_bound, lbound=self.lower_bound,
                    add_evl=add_evl, f=f, token=self.token, maxiter=10**6,
                    end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                    de_workers=1, min_element_length=self.min_element_length, disp_res=False, lapack_driver='gelsd',
                    degree=degree_list, evl_minimize=True, constr=None, gen_solution=False)
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

            # track_split.append([geom_type, breaks[i - 1], breaks[i], breaks[i] - breaks[i - 1], radius, np.nan])
            track_split.append([geom_type, breaks[i - 1], breaks[i], breaks[i] - breaks[i - 1], radius, np.nan, y_vals[i - 1], y_vals[i]])
        track_split = pd.DataFrame(track_split)
        track_split.columns = ["geom", "start", "end", "length", "radius", "level", "y_vals_start", "y_vals_end"]
        return track_split

    def __get_vozv_prj(self, f_urov, track_split):

        urov_prj = np.zeros(len(self.pkt))
        urov_values = np.zeros(len(self.breaks))

        if f_urov is None:
            for i in range(1, len(self.breaks)):
                if self.degree_list[i - 1] == 0:
                    if np.abs(track_split.radius.iloc[i - 1]) < self.min_straight_radius:
                        urov_values[i - 1] = self.__get_params_for_count_vozv(i, track_split, urov_values)
                        urov_values[i] = urov_values[i - 1]
                    else:
                        urov_values[i - 1] = 0
                        urov_values[i] = 0
        else:
            count = 0
            for i in range(1, len(self.breaks)):
                if self.degree_list[i - 1] == 0:
                    if f_urov[count] is not None:
                        urov_values[i - 1] = f_urov[count]
                    else:
                        if np.abs(track_split.radius.iloc[i - 1]) < self.min_straight_radius:
                            urov_values[i - 1] = self.__get_params_for_count_vozv(i, track_split, urov_values)
                        else:
                            urov_values[i - 1] = 0

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
        ev_table[:, 14] = self.upper_bound
        ev_table[:, 15] = self.lower_bound
        ev_table[:, 16] = self.ur
        ev_table[:, 17] = self.v_max

        ev_table[:, 29] = self.__get_vozv_prj(f_urov, track_split)

        # Изменение длины рельса
        ev_table[:, 26] = 0.00002 * ev_table[:, 13] * ev_table[:, 10] * self.d
        # Изменение температуры закрепления
        ev_table[:, 27] = 0.00002 * ev_table[:, 13] * ev_table[:, 10] / 0.0118

        # Потребность в балласте
        # ev_table[:, 28] =

        # Непогашенное ускорение для натурных стрел
        ev_table[:, 30] = ev_table[:, 17] ** 2 * ev_table[:, 0] / 13 / 50000 - 0.0061 * ev_table[:, 16]
        # Непогашенное ускорение для проектных стрел
        ev_table[:, 33] = ev_table[:, 17] ** 2 * ev_table[:, 10] / 13 / 50000 - 0.0061 * ev_table[:, 29]

        # Скорость нарастания непогашенного ускорения для натурных стрел
        ev_table[1:, 31] = ev_table[1:, 17] * (ev_table[1:, 30] - ev_table[: -1, 30]) / 3.6 / self.d
        # Скорость подъема колеса на возвышение наружного рельса для натурных стрел
        ev_table[1:, 32] = ev_table[1:, 17] * (ev_table[1:, 16] - ev_table[: -1, 16]) / 3.6 / self.d
        # Скорость нарастания непогашенного ускорения для проектных стрел
        ev_table[1:, 34] = ev_table[1:, 17] * (ev_table[1:, 33] - ev_table[: -1, 33]) / 3.6 / self.d
        # Скорость подъема колеса на возвышение наружного рельса для проектных стрел
        ev_table[1:, 35] = ev_table[1:, 17] * (ev_table[1:, 29] - ev_table[: -1, 29]) / 3.6 / self.d

        ev_table[:, 31] = np.abs(ev_table[:, 31])
        ev_table[:, 32] = np.abs(ev_table[:, 32])
        ev_table[:, 34] = np.abs(ev_table[:, 34])
        ev_table[:, 35] = np.abs(ev_table[:, 35])

        ev_table = pd.DataFrame(ev_table)
        ev_table.columns = self.__plan_column_names()
        return track_split, ev_table

    def __plan_column_names(self):
        return ["plan_fact", "First_plan", "Fact_Plan", "plan_prj_0185", "EV", "Coord", "tangens", "Popravka", "8",
                "Popravka_razn", "plan_prj", "Fact_Plan_corr", "Sum_Fact_Plan_corr", "plan_delta", "ubound", "lbound",
                "vozv_fact", "V_max", "R", "a_nepog", "Max_v_dop", "Min_vozv", "l_perex", "mean_vozv", "Uklon_otvoda",
                "narast_a_nepog", "rail_length", "fastening_tmp", "ballast_need", "vozv_prj", "a_nepog_fact",
                "psi_fact", "v_wheel_fact", "a_nepog_prj", "psi_prj", "v_wheel_prj", "36", "37", "38", "39", "40", "41"]

    def __get_i_max(self, v):
        if v > 220:
            i_max = 0.7
        elif v > 200:
            i_max = 0.8
        elif v > 180:
            i_max = 0.9
        elif v > 160:
            i_max = 1.0
        elif v > 140:
            i_max = 1.1
        elif v > 120:
            i_max = 1.2
        elif v > 110:
            i_max = 1.4
        elif v > 100:
            i_max = 1.5
        elif v > 95:
            i_max = 1.6
        elif v > 90:
            i_max = 1.7
        elif v > 85:
            i_max = 1.8
        elif v > 80:
            i_max = 1.9
        elif v > 75:
            i_max = 2.1
        elif v > 70:
            i_max = 2.3
        elif v > 65:
            i_max = 2.5
        elif v > 55:
            i_max = 2.7
        elif v > 50:
            i_max = 2.9
        elif v > 40:
            i_max = 3.0
        elif v > 25:
            i_max = 3.1
        else:
            i_max = 3.2
        return i_max

    def __check_urov_conditions(self, urov_to_check, h_left, h_right, v, v_left, v_right,
                                l_left, l_right, r, r_left, r_right):
        # print(f'urov_to_check = {urov_to_check}')
        a_np_left = v_left**2/13/r_left - 0.0061*h_left
        a_np_right = v_right**2/13/r_right - 0.0061*h_right
        i_max = self.__get_i_max(v)

        urov_i_max_left = l_left*i_max + h_left
        urov_i_max_left_low = -l_left * i_max + h_left
        urov_i_max_right = l_right*i_max + h_right
        urov_i_max_right_low = -l_right * i_max + h_right
        urov_i_max = np.min([urov_i_max_left, urov_i_max_right])
        urov_i_min = np.max([urov_i_max_left_low, urov_i_max_right_low])

        a_np_psi_left = 0.6 * 3.6 * l_left/v + a_np_left
        a_np_psi_left_low = -0.6 * 3.6 * l_left/v + a_np_left

        a_np_psi_right = 0.6 * 3.6 * l_right/v + a_np_right
        a_np_psi_right_low = -0.6 * 3.6 * l_right/v + a_np_right

        a_np_max = np.min([0.7, a_np_psi_left, a_np_psi_right])
        a_np_min = np.max([-0.7, a_np_psi_left_low, a_np_psi_right_low])
        urov_a_np = (v**2/13/r - a_np_max)/0.0061
        urov_a_np_low = (v**2/13/r - a_np_min)/0.0061

        urov_fv_left = 36 * 3.6 * l_left/v + h_left
        urov_fv_left_high = -36 * 3.6 * l_left/v + h_left
        urov_fv_right = 36 * 3.6 * l_right/v + h_right
        urov_fv_right_high = -36 * 3.6 * l_right/v + h_right
        urov_fv_high = np.max([urov_fv_left_high, urov_fv_right_high])
        urov_fv = np.min([urov_fv_left, urov_fv_right])

        urov_max_value = np.min([urov_i_max, urov_fv, urov_a_np_low])
        urov_min_value = np.max([urov_i_min, urov_a_np, urov_fv_high])
        # print(f'urov_max_value, urov_min_value = {urov_max_value, urov_min_value}')

        if urov_max_value < urov_min_value:
            mean_ur_diap = (urov_min_value + urov_max_value) / 2
            if np.abs(mean_ur_diap - urov_i_max) < np.abs(mean_ur_diap - urov_i_min):
                return urov_i_max
            return urov_i_min

        if (urov_to_check <= urov_max_value) & (urov_to_check >= urov_min_value):
            return urov_to_check

        if urov_max_value > 150:
            return urov_min_value

        if urov_min_value < -150:
            return urov_max_value

        if np.abs(urov_max_value - urov_to_check) < np.abs(urov_to_check - urov_min_value):
            return urov_max_value

        return urov_min_value

    def __get_params_for_count_vozv(self, i, track_split, urov_values):
        bool_arr = (self.pkt >= self.breaks[i - 1]) & (self.pkt <= self.breaks[i])
        urov_to_check = np.mean(self.ur[bool_arr])
        v_to_check = np.max(self.v_max[bool_arr])

        if i == 1:
            l_left = np.inf
        else:
            l_left = track_split.length.iloc[i - 2]
        if i == len(self.breaks) - 1:
            l_right = np.inf
        else:
            l_right = track_split.length.iloc[i]

        if i <= 2:
            ur_left = 0
            v_left = 0
            r_left = np.inf
        else:
            bool_arr_left = (self.pkt >= self.breaks[i - 3]) & (self.pkt <= self.breaks[i - 2])
            ur_left = urov_values[i - 3]
            v_left = np.max(self.v_max[bool_arr_left])
            r_left = track_split.radius.iloc[i - 3]

        if i >= len(self.breaks) - 2:
            ur_right = 0
            v_right = 0
            r_right = np.inf
        else:
            bool_arr_right = (self.pkt >= self.breaks[i + 1]) & (self.pkt <= self.breaks[i + 2])
            ur_right = np.mean(self.ur[bool_arr_right])
            v_right = np.max(self.v_max[bool_arr_right])
            r_right = track_split.radius.iloc[i + 1]

        r = track_split.radius.iloc[i - 1]
        res_urov_values = self.__check_urov_conditions(urov_to_check, ur_left, ur_right, v_to_check, v_left, v_right,
                                                       l_left, l_right, r, r_left, r_right)
        return res_urov_values
    
