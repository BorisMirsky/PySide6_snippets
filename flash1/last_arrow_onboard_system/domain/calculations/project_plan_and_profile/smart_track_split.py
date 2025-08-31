from .plan_optimization import PlanOptimization
from .smart_bounded_pwlf import PWLF as smart_PWLF
from .bounded_pwlf import PWLF
import numpy as np
import pandas as pd
from cantok import SimpleToken


class SmartSplitPlanCalculation:

    def __init__(self, pkt, recalculated_rix, initial_ur, v_max, lower_bound, upper_bound,
                 shift=2, min_radius_length=20, min_per_length=20, max_per_length=None, 
                 degree_template=[0, 1, 0, 1, 0], 
                 f=[None, None, None], 
                 tol=10,
                 differential_evolution_tol = 1e-3,
                 differential_evolution_updating = 'immediate',
                 token=SimpleToken(), 
                 add_evl=None):
        
        self.differential_evolution_tol = differential_evolution_tol
        self.differential_evolution_updating = differential_evolution_updating

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

        # Количество точек, которые мы считаем уже рассчитанными по итогам предыдущй итерации
        self.shift = shift
        # Точность нахождения максимальной длины, до куда возможно дотянуть участок, укладываясь в ограничения
        self.tol = tol
        # Параметры вычислительного алгоритма
        self.f = f
        self.degree_template = degree_template

        # Ограничение на минимальную длину радиуса
        self.min_radius_length = min_radius_length
        # Ограничение на минимальную длину переходной на прямом участке
        self.min_per_length = min_per_length
        # Ограничение на максимальную длину переходной на прямом участке
        self.max_per_length = max_per_length
        # Минимальная длина элемента (с меньшим значением расчет не имеет смысла)
        self.abs_min_length_elem = 3
        # Минимальное значение ограничения (по модулю), при котором используется функция add_evl
        self.min_value_to_add_evl = 19.5

        # Добавка к эвольвенте для возможности приведения сдвижек к целевому значению
        # (т.е. Мы будем минимизировать отклонение сдвижки относительно целевого значения, а не относительно нуля)
        if add_evl is None:
            self.add_evl = self.__get_add_evl()
        else:
            self.add_evl = add_evl

        # Минимальное значение радиуса, при котором участок считаем прямым
        self.min_straight_radius = 7000

        # Находим значение шага
        self.d = self.pkt[1] - self.pkt[0]
        # Значения точек излома
        self.breaks = None
        # Значения проектных стрел в точках излома
        self.y_vals = None
        # Перечень элементов (1 - переходная кривая, 0 - прямая/радиус)
        self.degree_list = None

    def __get_add_evl(self):
        add_evl = np.zeros(len(self.lower_bound))
        for i in range(len(self.lower_bound)):
            if (np.abs(self.lower_bound[i]) < self.min_value_to_add_evl) |\
                    (np.abs(self.upper_bound[i]) < self.min_value_to_add_evl):
                add_evl[i] = (self.lower_bound[i] + self.upper_bound[i])/2
        add_evl[0] = 0
        add_evl[-1] = 0
        return add_evl

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

    def track_split_calculation(self, init_summ_str=0, init_last_evl=0, init_summ_sdv=0, new_summ_str=0, new_evl=0,
                                last_f=None, start_point=None, init_prj=np.array([])):

        calculation_complete = False
        if start_point is None:
            x_opt = self.pkt[0]
        else:
            x_opt = start_point

        summ_str = init_summ_str
        last_evl = init_last_evl
        summ_sdv = init_summ_sdv
        delta_str_prev = -summ_str

        final_degree_list = np.array([0])
        final_breaks = np.array([x_opt])
        final_y_vals = np.array([])
        plan_prj = init_prj
        f = self.f

        while not calculation_complete:

            ba = (self.pkt >= x_opt)
            x = self.pkt[ba]
            y = self.recalculated_rix[ba]
            lb = self.lower_bound[ba]
            ub = self.upper_bound[ba]
            a_evl = self.add_evl[ba]

            smart_plan_split = PlanOptimization(x, y, lb, ub, self.recalculated_rix[self.pkt < x_opt], plan_prj,
                                                self.lower_bound[self.pkt < x_opt], self.upper_bound[self.pkt < x_opt],
                                                delta_str_prev=delta_str_prev, summ_str=summ_str, last_evl=last_evl,
                                                summ_sdv=summ_sdv, min_radius_length=self.min_radius_length,
                                                min_per_length=self.min_per_length, max_per_length=self.max_per_length,
                                                degree_list=self.degree_template, f=self.f, tol=self.tol,
                                                token=self.token, add_evl=a_evl,
                                                new_summ_str=new_summ_str, new_evl=new_evl, 
                                                differential_evolution_tol=self.differential_evolution_tol,
                                                differential_evolution_updating=self.differential_evolution_updating,
                                                last_f=last_f)

            degree_list, breaks, y_vals, y_pred_full, sdv_full, calculation_complete = smart_plan_split.find_project()

            if calculation_complete is None:
                # TODO избавиться от ошибки в этом случае - если calculation_complete is None, то считаем стандартным методом эвольвент
                return None

            if not calculation_complete:
                delta_rasst = breaks[self.shift + 1] - breaks[self.shift] - self.d
                # x_opt = breaks[self.shift] + np.min([self.min_radius_length, delta_rasst])
                x_opt = breaks[self.shift + 1] - self.abs_min_length_elem
                x_num_in_arr = int((x_opt - self.pkt[0]) / self.d)
                final_degree_list = np.concatenate([final_degree_list, degree_list[1: self.shift + 1]])
                final_breaks = np.concatenate([final_breaks, breaks[1: self.shift + 1]])
                final_y_vals = np.concatenate([final_y_vals, y_vals[1: self.shift + 1]])
                plan_prj = np.concatenate([plan_prj, y_pred_full])
                plan_prj = plan_prj[: x_num_in_arr + 1]
                print(f"Calculated {x_opt} from {self.pkt[-1]}")
            else:
                final_degree_list = np.concatenate([final_degree_list, degree_list[1:]])
                final_breaks = np.concatenate([final_breaks, breaks[1:]])
                final_y_vals = np.concatenate([final_y_vals, y_vals[1:]])
                plan_prj = np.concatenate([plan_prj, y_pred_full])
                print(f"Calculation complete!")

            # TODO по окончании расчета добавить попытку сделать polish при помощи fixed_points calculation и проверить,
            #  если укладывается в сдвижки, то брать это решение
            z = len(plan_prj)
            ev_table = np.zeros((z, 5))
            ev_table[:, 0] = self.recalculated_rix[: z]
            ev_table[:, 1] = plan_prj
            ev_table[:, 2] = ev_table[:, 0] - ev_table[:, 1]
            ev_table[:, 3] = np.cumsum(ev_table[:, 2])
            ev_table[1:, 4] = 2 * np.cumsum(ev_table[:-1, 3])

            # plt.plot(self.pkt[:ev_table.shape[0]],ev_table[:, 0])
            # plt.plot(self.pkt[:ev_table.shape[0]],ev_table[:, 1])
            # plt.show()
            #
            # plt.plot(self.pkt[:ev_table.shape[0]], ev_table[:, 4])
            # plt.show()

            f[0] = plan_prj[-1]
            summ_str = np.sum(ev_table[:, 2])
            last_evl = ev_table[-1, 4] / 2
            delta_str_prev = -summ_str

        # Добавляем в массив самое первое значение, т.к. оно пропущено (объединяли [1:])
        final_y_vals = np.concatenate([np.array([ev_table[0, 1]]), final_y_vals])
        self.degree_list = final_degree_list
        self.breaks = final_breaks
        self.y_vals = final_y_vals

        return final_degree_list, final_breaks, final_y_vals, ev_table[:, 1], ev_table[:, 4]

    def fixed_points_calculation(self, degree_list, breaks, f):
        pwlf = self.pwlf_init(degree_list, f, self.add_evl, sum_evl_to_zero=False)
        breaks, new_y_vals, y_pred = pwlf.solve_lsq_equal_constr(breaks, f)
        sdv = self.__get_sdv(self.recalculated_rix, y_pred)
        return breaks, new_y_vals, y_pred, sdv

    def pwlf_init(self, degree_list, f, add_evl, sum_evl_to_zero):
        pwlf = PWLF(self.pkt, self.recalculated_rix, ubound=self.upper_bound, lbound=self.lower_bound,
                    add_evl=add_evl, f=f, token=self.token, maxiter=10**6,
                    end_evl_to_zero=True, summ_evl_to_zero=sum_evl_to_zero,
                    de_workers=1, min_element_length=self.min_radius_length, disp_res=False, lapack_driver='gelsd',
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

            track_split.append([geom_type, breaks[i - 1], breaks[i], breaks[i] - breaks[i - 1], radius, np.nan,
                                y_vals[i - 1], y_vals[i]])
        track_split = pd.DataFrame(track_split)
        track_split.columns = ["geom", "start", "end", "length", "radius", "level", "y_vals_start", "y_vals_end"]
        return track_split

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

    def __get_params_for_count_vozv(self, i, track_split, urov_values, breaks):
        bool_arr = (self.pkt >= breaks[i - 1]) & (self.pkt <= breaks[i])
        urov_to_check = np.mean(self.ur[bool_arr])
        v_to_check = np.max(self.v_max[bool_arr])

        if i == 1:
            l_left = np.inf
        else:
            l_left = track_split.length.iloc[i - 2]
        if i == len(breaks) - 1:
            l_right = np.inf
        else:
            l_right = track_split.length.iloc[i]

        if i <= 2:
            ur_left = 0
            v_left = 0
            r_left = np.inf
        else:
            bool_arr_left = (self.pkt >= breaks[i - 3]) & (self.pkt <= breaks[i - 2])
            ur_left = urov_values[i - 3]
            v_left = np.max(self.v_max[bool_arr_left])
            r_left = track_split.radius.iloc[i - 3]

        if i >= len(breaks) - 2:
            ur_right = 0
            v_right = 0
            r_right = np.inf
        else:
            bool_arr_right = (self.pkt >= breaks[i + 1]) & (self.pkt <= breaks[i + 2])
            ur_right = np.mean(self.ur[bool_arr_right])
            v_right = np.max(self.v_max[bool_arr_right])
            r_right = track_split.radius.iloc[i + 1]

        r = track_split.radius.iloc[i - 1]
        res_urov_values = self.__check_urov_conditions(urov_to_check, ur_left, ur_right, v_to_check, v_left, v_right,
                                                       l_left, l_right, r, r_left, r_right)
        return res_urov_values

    def __get_vozv_prj(self, f_urov, track_split, breaks):

        urov_prj = np.zeros(len(self.pkt))
        urov_values = np.zeros(len(breaks))

        if f_urov is None:
            for i in range(1, len(breaks)):
                if self.degree_list[i - 1] == 0:
                    if np.abs(track_split.radius.iloc[i - 1]) < self.min_straight_radius:
                        urov_values[i - 1] = self.__get_params_for_count_vozv(i, track_split, urov_values, breaks)
                        urov_values[i] = urov_values[i - 1]
                    else:
                        urov_values[i - 1] = 0
                        urov_values[i] = 0
        else:
            count = 0
            for i in range(1, len(breaks)):
                if self.degree_list[i - 1] == 0:
                    if f_urov[count] is not None:
                        urov_values[i - 1] = f_urov[count]
                    else:
                        if np.abs(track_split.radius.iloc[i - 1]) < self.min_straight_radius:
                            urov_values[i - 1] = self.__get_params_for_count_vozv(i, track_split, urov_values, breaks)
                        else:
                            urov_values[i - 1] = 0

                    urov_values[i] = urov_values[i - 1]
                    count += 1

        for i in range(1, len(breaks)):
            bool_arr = (self.pkt >= breaks[i - 1]) & (self.pkt <= breaks[i])
            if self.degree_list[i - 1] == 0:
                urov_prj[bool_arr] = urov_values[i]
            elif self.degree_list[i - 1] == 1:
                alpha = (urov_values[i] - urov_values[i - 1]) / (breaks[i] - breaks[i - 1])
                beta = urov_values[i] - alpha * breaks[i]
                urov_prj[bool_arr] = alpha * self.pkt[bool_arr] + beta

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

        ev_table[:, 29] = self.__get_vozv_prj(f_urov, track_split, breaks)

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

    def __get_change_points(self, degree_list_values, f_values, y_vals, lc_lbound, lc_ubound, custom_points):

        lng_const = 6

        if custom_points is not None:
            return custom_points

        first_change_value = int(len(degree_list_values)/2)
        if degree_list_values[first_change_value] == 1:
            first_change_value += 1
        last_change_value = first_change_value

        for i in range(len(f_values)):
            if f_values[i] is not None:
                first_change_value = i
                break

        for i in range(len(f_values) - 1, -1, -1):
            if f_values[i] is not None:
                last_change_value = i
                break
        # TODO обсудить формат входных данных и расчет откуда до куда пересчитывать (в degree_list)
        nscp = np.max([0, first_change_value - lng_const])
        necp = np.min([len(f_values) - 1, last_change_value + lng_const + 1])
        degree_list = degree_list_values[nscp: necp]
        lc_lb = lc_lbound[nscp: necp]
        lc_ub = lc_ubound[nscp: necp]

        f = list()
        f.append(y_vals[nscp])
        for i in range(nscp + 1, necp - 1):
            if degree_list_values[i] == 0:
                f.append(f_values[i])

        f.append(y_vals[necp - 1])

        return nscp, necp, degree_list, np.array(f), lc_lb, lc_ub

    def custom_calculation(self, degree_list_values, f_values, constraints, breaks, y_vals, plan_prj, sdv, custom_points=None):

        lc, uc = constraints
        # Учитываем ограничения на длины круговых и переходных кривых
        lc_lbound = self.min_radius_length * np.ones(len(degree_list_values))
        lc_ubound = np.inf * np.ones(len(degree_list_values))

        for i in range(len(degree_list_values)):
            if i % 2 == 1:
                lc_lbound[i] = self.min_per_length

        for i in range(len(degree_list_values)):
            if lc[i] is not None:
                lc_lbound[i] = lc[i]
            if uc[i] is not None:
                lc_ubound[i] = uc[i]

        nscp, necp, degree_list, f, lc_lb, lc_ub = self.__get_change_points(degree_list_values, f_values, y_vals, lc_lbound, lc_ubound, custom_points)

        ba = (self.pkt >= breaks[nscp]) & (self.pkt <= breaks[necp])
        summ_str = np.sum(self.recalculated_rix[self.pkt < breaks[nscp]] - plan_prj[self.pkt < breaks[nscp]])
        new_summ_str = np.sum(self.recalculated_rix[self.pkt > breaks[necp]] - plan_prj[self.pkt > breaks[necp]])

        s1 = sdv[self.pkt < breaks[nscp]]
        last_evl = 0
        if len(s1) > 0:
            last_evl = s1[-1] / 2

        s2 = sdv[self.pkt <= breaks[necp]]
        new_evl = 0
        if len(s2) > 0:
            new_evl = s2[-1] / 2
        summ_sdv = 0

        x = self.pkt[ba]
        y = self.recalculated_rix[ba]

        lb = self.lower_bound[ba]
        ub = self.upper_bound[ba]
        new_add_evl = self.add_evl[ba] - 2 * last_evl
        new_add_evl[-1] = 0  # new_evl

        lc_lb[0] = x[0] + lc_lb[0]
        lc_ub[-1] = x[-1] - lc_lb[-1]
        constr = (lc_lb, lc_ub)

        pwlf = smart_PWLF(x, y, ubound=ub, lbound=lb, add_evl=new_add_evl, degree=degree_list, f=f, token=self.token,
                          count_with_weights=True, delta_str_prev=-summ_str,
                          delta_str_to_zero=True, end_evl_to_zero=True, summ_evl_to_zero=False,
                          summ_str=summ_str, summ_str_last_point=new_summ_str, last_evl=last_evl - new_evl,
                          summ_sdv=summ_sdv, maxiter=10 ** 6, de_workers=1, min_element_length=self.min_radius_length,
                          disp_res=False, lapack_driver='gelsd', evl_minimize=True, constr=constr, gen_solution=True,
                          differential_evolution_tol=self.differential_evolution_tol,
                          differential_evolution_updating=self.differential_evolution_updating)

        pwlf.fit(len(degree_list))

        new_breaks = pwlf.fit_breaks
        new_custom_breaks = np.concatenate([breaks[:nscp + 1], new_breaks[1: -1]])
        new_custom_breaks = np.concatenate([new_custom_breaks, breaks[necp:]])
        boolarr = (x >= new_breaks[0]) & (x <= new_breaks[-1])
        new_y_vals = pwlf.predict(new_breaks, f)
        new_custom_y_vals = np.concatenate([y_vals[:nscp + 1], new_y_vals[1: -1]])
        new_custom_y_vals = np.concatenate([new_custom_y_vals, y_vals[necp:]])
        new_y_pred = pwlf.predict(x[boolarr], f)
        prev_y_data = self.recalculated_rix[self.pkt < breaks[nscp]]
        prev_prj = plan_prj[self.pkt < breaks[nscp]]
        new_y_full = np.concatenate([prev_y_data, y[boolarr]])
        new_y_pred_full = np.concatenate([prev_prj, new_y_pred])
        sdv_full = self.__get_sdv(new_y_full, new_y_pred_full)

        new_plan_prj = np.concatenate([new_y_pred_full, plan_prj[self.pkt > breaks[necp]]])
        new_sdv = self.__get_sdv(self.recalculated_rix, new_plan_prj)
        return degree_list, new_custom_breaks, new_custom_y_vals, new_plan_prj, new_sdv
