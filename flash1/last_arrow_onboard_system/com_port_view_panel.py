import time
import sys
import json
# import bidict
import argparse
from pathlib import Path
from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (QMessageBox,
    QApplication, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, 
    QPushButton, QSpinBox, QWidget, QDoubleSpinBox, QLabel, QGroupBox)

from presentation.machine.units.com_port.ComPortUnitProvider import SerialPortUnitProvider
from presentation.machine.units.mock.MockUnitProvider import MockUnitProvider


def uint(argument: str) ->int:
    """ Type function for argparse - a uint value"""
    try:
        result = int(argument)
    except ValueError:    
        raise argparse.ArgumentTypeError("Must be a integer number")
    if result < 0:
        raise argparse.ArgumentTypeError('Argument must be non negative')
    return result
def uint16_t(argument: str) ->int:
    """ Type function for argparse - a uint16_t value"""
    result = uint(argument)
    if result < 0 or result > 65535:
        raise argparse.ArgumentTypeError('Argument must be in range [0; 65535]')
    return result

def as_signed_value(value: int) -> int:    
    return value if value <= 32767 else -1*(65536 - value)

def set_pendulum_to_zero(name: str, config: dict, units_provider: SerialPortUnitProvider):
    unit_params = config['models']['sensors'].get(name)
    inverse = -1 if unit_params.get('inverse', False) else 1

    cur_value = units_provider.sensors().get(name).read()
    unit_params['value_range']['min'] = round(unit_params['value_range']['min'] - cur_value*inverse)
    unit_params['value_range']['max'] = round(unit_params['value_range']['max'] - cur_value*inverse)
    new_unit = units_provider.create_read_unit(name, unit_params)
    # заменяем старый юнит на новый, с новым диаппазоном
    units_provider.sensors()[name] = new_unit

def shift_unit_value_range(name: str, shift: float, config: dict, units_provider: SerialPortUnitProvider):
    unit_params = config['models']['sensors'].get(name)
    inverse = -1 if unit_params.get('inverse', False) else 1

    # cur_value = units_provider.sensors().get(name).read()
    unit_params['value_range']['min'] = round(unit_params['value_range']['min'] - shift*inverse)
    unit_params['value_range']['max'] = round(unit_params['value_range']['max'] - shift*inverse)
    new_unit = units_provider.create_read_unit(name, unit_params)
    # заменяем старый юнит на новый, с новым диаппазоном
    units_provider.sensors()[name] = new_unit

def save_config(new_config: dict):
    if QMessageBox.question(window, 'Сохранение', 'Сохранить изменения?') == QMessageBox.StandardButton.No:
        return
    # делаем резервную копию config.json с именем backup_name
    backup_name = f'config__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.json.bak'
    config = json.load(open('./resources/config.json', encoding='utf-8'))
    with open(f'./resources/{backup_name}', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    # сохраняем новые настройки в config.json
    with open('./resources/config.json', 'w', encoding='utf-8') as f:
        json.dump(new_config, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':    
    config = json.load(open('./resources/config.json', encoding='utf-8'))
    # receive_count = config['models']['connection']['receive_items_count']
    # send_count = config['models']['connection']['send_items_count']
    sensors_config = config['models']['sensors'].copy()
    controls_config = config['models']['controls'].copy()
    controls_config['enable_register'] = {'register_id': 0}

    app = QApplication(sys.argv)
    units = SerialPortUnitProvider(config)
    # units = MockUnitProvider(config)

    # ===========================================================================================
    # Датчики
    # ===========================================================================================
    def read_elements_from_controller() ->None:
        # print('read_elements_from_controller')
        for name, params in sensors_config.items():
            # receive_code_widgets[name].setValue(as_signed_value(units.controller().receive_get(params['register_id'])))
            receive_code_widgets[name].setValue(units.controller().receive_get(params['register_id']))
            if params.get('projection_range', False):
                sensor_value = units.sensors().get(name).read()
                if sensor_value is not None:
                    receive_value_widgets[name].setValue(sensor_value)
                else:
                    # стрелограф возвращает None один раз после сдвига диаппазона
                    print(f'{name} returned the value {sensor_value}')

    receive_code_widgets: dict[str, QSpinBox] = dict()
    receive_value_widgets: dict[str, QDoubleSpinBox] = dict()
    receive_adjustment_widgets: dict[str, QPushButton] = dict()

    receive_elements_layout = QGridLayout()
    receive_elements_layout.addWidget(QLabel('Код'), 0, 1)
    receive_elements_layout.addWidget(QLabel('Значение (мм)'), 0, 2)
    receive_elements_layout.addWidget(QLabel('Тарировка'), 0, 3)
    
    # Формируем поля вывода показаний датчиков
    row  = 1
    for name, params in sensors_config.items():
        receive_elements_layout.addWidget(QLabel(name+f" ({str(params['register_id'])})"), row, 0)

        receive_code_spinbox = QSpinBox()
        receive_code_spinbox.setReadOnly(True)
        receive_code_spinbox.setRange(-65535, 65535)
        receive_code_widgets[name] = receive_code_spinbox
        receive_elements_layout.addWidget(receive_code_spinbox, row, 1)

        if params.get('projection_range', False):
            receive_value_spinbox = QDoubleSpinBox()
            receive_value_spinbox.setReadOnly(True)
            receive_value_spinbox.setRange(-65535, 65535)
            receive_value_widgets[name] = receive_value_spinbox        
            receive_elements_layout.addWidget(receive_value_spinbox, row, 2)
        row += 1

    # Формируем кнопки тарировки датчиков
    # strelograph_work
    strelograph_shift_layout = QHBoxLayout()
    btnStrelographShift = QPushButton('Сдвинуть')
    strelograph_shift_layout.addWidget(btnStrelographShift)
    spinboxStrelographShift = QDoubleSpinBox()
    spinboxStrelographShift.setRange(-100, 100)
    strelograph_shift_layout.addWidget(spinboxStrelographShift)
    btnStrelographShift.pressed.connect(
        lambda: shift_unit_value_range(name='strelograph_work', shift=spinboxStrelographShift.value(), config=config, units_provider=units))
    receive_adjustment_widgets['strelograph_work'] = strelograph_shift_layout
    idx = list(receive_code_widgets.keys()).index('strelograph_work') + 1
    receive_elements_layout.addLayout(receive_adjustment_widgets['strelograph_work'], idx, 3)
    # pendulum_work
    receive_adjustment_widgets['pendulum_work'] = QPushButton('-> 0')
    receive_adjustment_widgets['pendulum_work'].pressed.connect(
        lambda: set_pendulum_to_zero(name='pendulum_work', config=config, units_provider=units))
    idx = list(receive_code_widgets.keys()).index('pendulum_work') + 1
    receive_elements_layout.addWidget(receive_adjustment_widgets['pendulum_work'], idx, 3)
    # pendulum_control
    receive_adjustment_widgets['pendulum_control'] = QPushButton('-> 0')
    receive_adjustment_widgets['pendulum_control'].pressed.connect(
        lambda: set_pendulum_to_zero(name='pendulum_control', config=config, units_provider=units))
    idx = list(receive_code_widgets.keys()).index('pendulum_control') + 1
    receive_elements_layout.addWidget(receive_adjustment_widgets['pendulum_control'], idx, 3)
    # pendulum_front
    receive_adjustment_widgets['pendulum_front'] = QPushButton('-> 0')
    receive_adjustment_widgets['pendulum_front'].pressed.connect(
        lambda: set_pendulum_to_zero(name='pendulum_front', config=config, units_provider=units))
    idx = list(receive_code_widgets.keys()).index('pendulum_front') + 1
    receive_elements_layout.addWidget(receive_adjustment_widgets['pendulum_front'], idx, 3)

    units.controller().valueChanged.connect(read_elements_from_controller)
    # units.controller().valueChanged.connect(lambda: print('controller().valueChanged'))

    # ====================================================================================================================== #
    # Управляющие элементы                                                                                                   #
    # ====================================================================================================================== #
    send_code_widgets: dict[str, QSpinBox] = dict()
    send_value_widgets: dict[str, QDoubleSpinBox] = dict()

    send_elements_layout = QGridLayout()
    # send_elements_layout.addWidget(QLabel('Управляющие элементы'), 0, 0)
    send_elements_layout.addWidget(QLabel('Код'), 0, 1)
    # send_elements_layout.addWidget(QLabel('Значение (мм)'), 0, 2)
    
    row  = 1
    for name, params in controls_config.items():
        send_elements_layout.addWidget(QLabel(name+f" ({str(params['register_id'])})"), row, 0)
        send_element_spin_box = QSpinBox()
        send_element_spin_box.setRange(0, 65535)
        send_code_widgets[name] = send_element_spin_box
        send_elements_layout.addWidget(send_element_spin_box, row, 1)

        # if params.get('projection_range', False):
        #     send_value_spinbox = QDoubleSpinBox()
        #     send_value_spinbox.setReadOnly(True)
        #     send_value_spinbox.setRange(-65535, 65535)
        #     send_value_widgets[name] = send_value_spinbox        
        #     send_elements_layout.addWidget(send_value_spinbox, row, 2)
        row += 1

    def write_elements_to_controller() ->None:
        print('Write elements to controller...')
        for name, params in controls_config.items():       
            # units.controls().get(name).write(send_code_widgets[name].value())
            units.controller().send_set(params['register_id'], send_code_widgets[name].value())

    # units.controller_communication_allowed = True

    write_elements_button = QPushButton('Отослать значения на контроллер')
    write_elements_button.clicked.connect(write_elements_to_controller)
    save_config_button = QPushButton('Сохранить настройки')
    save_config_button.clicked.connect(lambda: save_config(config))

    # reload_config_button = QPushButton('Перечитать конфиг')
    # reload_config_button.clicked.connect(reload_config)

    sensors_groupbox = QGroupBox('Датчики')
    sensors_groupbox.setLayout(receive_elements_layout)
    controls_groupbox = QGroupBox('Управляющие элементы')
    controls_groupbox.setLayout(send_elements_layout)

    window = QWidget()
    
    mainLayout = QGridLayout()
    window.setLayout(mainLayout)
    mainLayout.addWidget(sensors_groupbox, 0, 0)
    mainLayout.addWidget(save_config_button, 1, 0)
    mainLayout.addWidget(controls_groupbox, 0, 1)
    mainLayout.addWidget(write_elements_button, 1, 1)
    mainLayout.setColumnStretch(0, 1)
    mainLayout.setColumnStretch(1, 0)
    
    window.show()
    sys.exit(app.exec())
