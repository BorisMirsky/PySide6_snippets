"""
Утилита для экспорта данных из nav-файла в формат amt - измерительную поездку  ПАК Стрелы ДС.
Для запуска утилиты или генерации exe-файла, этот файл надо скопировать корневую папку проекта 
(arrow_onboard_sytem) c именем nav_exporter.py. 
"""

import argparse
import zipfile
from dataclasses import dataclass

import pandas as pd
from os.path import isfile, dirname, basename, splitext
from domain.dto.Workflow import MeasuringTripResultDto, MeasuringTripOptionsDto, SteppedData
from domain.dto.Travelling import BaseRail, PicketDirection, MovingDirection, LocationVector1D
from presentation.utils.store.workflow.zip.Dto import MeasuringTripResultDto_to_archive

from nav_parser.navparser import NAVFile


class kwargs_append_action(argparse.Action):
    """
    argparse action to split an argument into KEY=VALUE form
    on append to a dictionary.
    """

    def __call__(self, parser, args, values, option_string=None):
        try:
            d = dict(map(lambda x: x.split('='),values))
        except ValueError as ex:
            raise argparse.ArgumentError(self, f"Could not parse argument \"{values}\" as k1=v1 k2=v2 ... format")
        setattr(args, self.dest, d)


@dataclass
class Args:
    """ Класс аргументов для данных из ui """
    srcfile: str
    start_step: int
    end_step: int
    step_picket: tuple[int, int] = None


def export_nav_to_amt(args: argparse.Namespace) -> tuple[MeasuringTripResultDto, pd.DataFrame]:
    # Парсер
    navfile = NAVFile(args.srcfile)

    measuring_step = 0.185
    start_step = 0 if not args.start_step else args.start_step
    end_step = len(navfile.data) if not args.end_step else args.end_step

    # Параметры машины
    machine_parameters = {
        "description": navfile.header.machine_description,
        "measures_step": measuring_step,
        "back_horde_plan": navfile.header.back_chord_plan,
        "front_horde_plan": navfile.header.front_chord_plan,
        "back_horde_prof": navfile.header.back_chord_prof,
        "front_horde_prof": navfile.header.front_chord_prof,
        "ticks_number": 0,
        "ticks_distance": 0,
        "lining_system_movable": True,
        "levelling_system_movable": True
    }

    # Расчет пикета начала
    start_picket = 0
    picket_direction = PicketDirection.Forward if navfile.picket_direction[0] == 0 else PicketDirection.Backward

    if args.step_picket is None:
        start_picket = start_step * measuring_step
    else:
        picket_step = int(args.step_picket[0])
        picket_position = float(args.step_picket[1])
        start_picket = picket_position - (picket_step - start_step) * measuring_step * picket_direction.multiplier()
    print(f'start_picket = {start_picket} m')

    # Опции
    options = MeasuringTripOptionsDto(
                track_title= navfile.name, 
                base_rail= BaseRail.Left if navfile.machine_press[0] == 0 else BaseRail.Right, 
                start_picket= LocationVector1D(meters=start_picket), 
                picket_direction= picket_direction, 
                moving_direction= MovingDirection.Forward if navfile.machine_direction[0] == 0 else MovingDirection.Backward)

    # Данные измерений
    # Дублируем рабочий маятник для маятника переднего и контрольного
    navfile.data['pendulum_front'] = navfile.data.pendulum_work
    navfile.data['pendulum_control'] = navfile.data.pendulum_work
    
    df_range = navfile.data.loc[start_step:end_step]
    df_range = df_range.reset_index(drop=True)
    df_range.index.name = 'step'
    measurements = SteppedData(data= df_range, step= LocationVector1D(meters=measuring_step))

    # RFID-метки
    tags = navfile.rfids_as_dataframe
    tags = tags[(tags.Step >= start_step) & (tags.Step <= end_step)]
    return MeasuringTripResultDto(options=options, measurements=measurements, tags=[], machine_parameters=machine_parameters), tags


def parse_args():    
    ap = argparse.ArgumentParser()
    ap.add_argument('srcfile', type=str, help='Входящий nav-файл')
    ap.add_argument("start_step", type=int, nargs='?', help="Номер шага начала участка")    
    ap.add_argument("end_step", type=int, nargs='?', help="Номер шага конца участка")
    ap.add_argument('-s', '--set-picket', dest='step_picket', nargs=2, type=float, required=False, help="Привязка пикета к степу. Первым идет значение степа, затем значение пикета в метрах (float).")

    return ap.parse_args()


def main(args: argparse.Namespace | Args):
    # print(f'--set-picket = {args.picket_step}')
    if not isfile(args.srcfile):
        raise ValueError(f'Файл "{args.srcfile}" не найден.')

    trip_dto, rfids = export_nav_to_amt(args)
    
    # Экспорт rfid-меток в csv-файл
    rfid_file = dirname(args.srcfile) + '/' + splitext(basename(args.srcfile))[0] + '_rfids.csv'
    print(f'Saving rfids to {rfid_file}')
    rfids.to_csv(rfid_file, sep=';', index=False)

    # Экспорт в amt
    amt_file = dirname(args.srcfile) + '/' + splitext(basename(args.srcfile))[0] + '.amt'
    print(f'Saving measuring trip to {amt_file}')
    MeasuringTripResultDto_to_archive(zipfile.ZipFile(amt_file, 'w'), trip_dto)
    
    print('Export done.')
    # exit(0)


if __name__ == "__main__":
    args = parse_args()
    main(args)
