import time
import sys
import json
# import bidict
import argparse
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, 
    QPushButton, QSpinBox, QWidget, QDoubleSpinBox, QLabel, QGroupBox)

from presentation.machine.units.com_port.ComPortUnitProvider import SerialPortUnitProvider

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

# def reload_config() -> None:
#     global units
#     if units is not None:
#         units.close()
#     time.sleep(5)
#     units = SerialPortUnitProvider(json.load(open('./resources/config.json')))

if __name__ == '__main__':    
    config = json.load(open('./resources/config.json'))
    # receive_count = config['models']['connection']['receive_items_count']
    # send_count = config['models']['connection']['send_items_count']
    sensors_config = config['models']['sensors'].copy()
    controls_config = config['models']['controls'].copy()
    controls_config['enable_register'] = {'register_id': 0}

    app = QApplication(sys.argv)
    units = SerialPortUnitProvider(config)    

    # ===========================================================================================
    # Датчики
    # ===========================================================================================
    receive_code_widgets: dict[str, QSpinBox] = dict()
    receive_value_widgets: dict[str, QDoubleSpinBox] = dict()

    receive_elements_layout = QGridLayout()
    receive_elements_layout.addWidget(QLabel('Код'), 0, 1)
    receive_elements_layout.addWidget(QLabel('Значение (мм)'), 0, 2)
    
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

    def read_elements_from_controller() ->None:
        # print('read_elements_from_controller')
        for name, params in sensors_config.items():
            receive_code_widgets[name].setValue(as_signed_value(units.controller().receive_get(params['register_id'])))
            if params.get('projection_range', False):
                receive_value_widgets[name].setValue(units.sensors().get(name).read())
    
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

    write_elements_button = QPushButton('Записать значения')
    write_elements_button.clicked.connect(write_elements_to_controller)


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
    # mainLayout.addWidget(reload_config_button, 1, 0)
    mainLayout.addWidget(controls_groupbox, 0, 1)
    mainLayout.addWidget(write_elements_button, 1, 1)
    # mainLayout.setHorizontalSpacing(10)

    window.show()
    sys.exit(app.exec())
