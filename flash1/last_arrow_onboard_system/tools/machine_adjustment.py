import sys
import json
# import bidict
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (QMessageBox, QTabWidget, QCheckBox,
    QApplication, QGridLayout, QHBoxLayout, QVBoxLayout, QFileDialog, 
    QPushButton, QSpinBox, QWidget, QDoubleSpinBox, QLabel, QGroupBox)

from presentation.machine.units.com_port.ComPortUnitProvider import SerialPortUnitProvider

class MachineAdjustmentWidget(QWidget):
    StyleSpinBoxWidth = 110

    @staticmethod
    def as_signed_value(value: int) -> int:    
        return value if value <= 32767 else -1*(65536 - value)
    
    def __init__(self, config: dict):
        super().__init__()
        self.__config = config
        self.__unit_provider = SerialPortUnitProvider(config)
        self.__unit_provider.controller().valueChanged.connect(self.update_sensor_data)

        self.__receive_code_widgets: dict[str, QSpinBox] = dict()
        self.__receive_value_widgets: dict[str, QDoubleSpinBox] = dict()
        self.__receive_adjustment_widgets: dict[str, QPushButton] = dict()

        self.__send_code_widgets: dict[str, QSpinBox] = dict()
        self.__send_value_widgets: dict[str, QDoubleSpinBox] = dict()
        
        mainLayout = QGridLayout()
        adjustmentTabWidget = QTabWidget()
        adjustmentTabLayout = QHBoxLayout()
        adjustmentTabLayout.addWidget(adjustmentTabWidget)        
        adjustmentTabWidget.addTab(self.__createReadUnitsWidget(config), 'Датчики')
        adjustmentTabWidget.addTab(self.__createWriteUnitsWidget(config), 'Управляющие элементы')

        self.__connectCheckBox = QCheckBox('Установить связь', parent=self)
        self.__connectCheckBox.checkStateChanged.connect(self.__connectionButtonHandler)
        
        save_config_button = QPushButton('Сохранить настройки')
        save_config_button.clicked.connect(self.save_config)

        # mainLayout.addWidget(self.__signedCheckBox, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        mainLayout.addWidget(self.__connectCheckBox, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        mainLayout.addItem(adjustmentTabLayout, 1, 0, columnSpan=2)
        mainLayout.addWidget(save_config_button, 2, 0)
        self.setLayout(mainLayout)

    def write_elements_to_controller(self) -> None:
        print('Write elements to controller...')
        for name, params in config['models']['controls'].items():       
            self.__unit_provider.controller().send_set(params['register_id'], self.__send_code_widgets[name].value())
            
    def update_sensor_data(self) ->None:
        # print('read_elements_from_controller')
        for name, params in self.__config['models']['sensors'].items():
            sensor_value = self.__unit_provider.controller().receive_get(params['register_id'])
            sensor_value = self.as_signed_value(sensor_value) if self.__signedCheckBox.isChecked() else sensor_value 
            self.__receive_code_widgets[name].setValue(sensor_value)
            if params.get('projection_range', False):
                sensor_value = self.__unit_provider.sensors().get(name).read()
                if sensor_value is not None:
                    self.__receive_value_widgets[name].setValue(sensor_value)
                else:
                    # стрелограф возвращает None один раз после сдвига диаппазона
                    print(f'{name} returned the value {sensor_value}')

    def __connectionButtonHandler(self):
        self.__unit_provider.controller_communication_allowed = self.__connectCheckBox.isChecked()
        print(f'communication_allowed = {self.__unit_provider.controller_communication_allowed}')

    def save_config(self):
        new_config = self.__config
        # if QMessageBox.question(window, 'Сохранение', 'Сохранить изменения?') == QMessageBox.StandardButton.No:
        #     return
        # делаем резервную копию config.json
        # backup_name = f'config__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.json.bak'
        # config = json.load(open('./resources/config.json', encoding='utf-8'))
        # with open(f'./resources/{backup_name}', 'w', encoding='utf-8') as f:
        #     json.dump(config, f, ensure_ascii=False, indent=4)
        # сохраняем новые настройки в config.json
        # with open('./resources/config.json', 'w', encoding='utf-8') as f:
        #     json.dump(new_config, f, ensure_ascii=False, indent=4)

        preffered_name: str = f'./resources/config__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.json'
        saveFile = QFileDialog.getSaveFileName(self, 'Сохранение настроек', preffered_name, '*.json')[0]
        if saveFile is None or len(saveFile) == 0:
            return
        elif not saveFile.endswith('.json'):
            saveFile += '.json'

        with open(saveFile, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, ensure_ascii=False, indent=4)
                    
    def __createReadUnitsWidget(self, config: dict):
        receive_elements_layout = QGridLayout()        
        qlabel = QLabel('Код')
        qlabel.setFixedHeight(20)
        receive_elements_layout.addWidget(qlabel, 0, 1)
        qlabel = QLabel('Значение (мм)')
        qlabel.setFixedHeight(20)
        receive_elements_layout.addWidget(qlabel, 0, 2)
        qlabel = QLabel('Тарировка')
        qlabel.setFixedHeight(20)
        receive_elements_layout.addWidget(qlabel, 0, 3)
        
        # Формируем поля вывода показаний датчиков
        row  = 1
        for name, params in config['models']['sensors'].items():
            receive_elements_layout.addWidget(QLabel(name+f" ({str(params['register_id'])})"), row, 0)

            receive_code_spinbox = QSpinBox()
            receive_code_spinbox.setReadOnly(True)
            receive_code_spinbox.setRange(-65535, 65535)
            receive_code_spinbox.setFixedWidth(self.StyleSpinBoxWidth)
            self.__receive_code_widgets[name] = receive_code_spinbox
            receive_elements_layout.addWidget(receive_code_spinbox, row, 1)

            if params.get('projection_range', False):
                receive_value_spinbox = QDoubleSpinBox()
                receive_value_spinbox.setReadOnly(True)
                receive_value_spinbox.setRange(-65535, 65535)
                receive_value_spinbox.setFixedWidth(self.StyleSpinBoxWidth)
                self.__receive_value_widgets[name] = receive_value_spinbox        
                receive_elements_layout.addWidget(receive_value_spinbox, row, 2)
            row += 1

        # Формируем кнопки тарировки датчиков
        # strelograph_work
        self.__receive_adjustment_widgets['strelograph_work'] = self.createAdjustmentWidget('strelograph_work')
        idx = list(self.__receive_code_widgets.keys()).index('strelograph_work') + 1
        receive_elements_layout.addLayout(self.__receive_adjustment_widgets['strelograph_work'], idx, 3)
        # pendulum_work
        self.__receive_adjustment_widgets['pendulum_work'] = self.createAdjustmentWidget('pendulum_work')
        idx = list(self.__receive_code_widgets.keys()).index('pendulum_work') + 1
        receive_elements_layout.addLayout(self.__receive_adjustment_widgets['pendulum_work'], idx, 3)
        # pendulum_control
        self.__receive_adjustment_widgets['pendulum_control'] = self.createAdjustmentWidget('pendulum_control')
        idx = list(self.__receive_code_widgets.keys()).index('pendulum_control') + 1
        receive_elements_layout.addLayout(self.__receive_adjustment_widgets['pendulum_control'], idx, 3)
        # pendulum_front
        self.__receive_adjustment_widgets['pendulum_front'] = self.createAdjustmentWidget('pendulum_front')
        idx = list(self.__receive_code_widgets.keys()).index('pendulum_front') + 1
        receive_elements_layout.addLayout(self.__receive_adjustment_widgets['pendulum_front'], idx, 3)
        # sagging_left
        self.__receive_adjustment_widgets['sagging_left'] = self.createAdjustmentWidget('sagging_left')
        idx = list(self.__receive_code_widgets.keys()).index('sagging_left') + 1
        receive_elements_layout.addLayout(self.__receive_adjustment_widgets['sagging_left'], idx, 3)
        # sagging_right
        self.__receive_adjustment_widgets['sagging_right'] = self.createAdjustmentWidget('sagging_right')
        idx = list(self.__receive_code_widgets.keys()).index('sagging_right') + 1
        receive_elements_layout.addLayout(self.__receive_adjustment_widgets['sagging_right'], idx, 3)
        
        sensors_groupbox = QGroupBox()
        sensorsVBoxLayout = QVBoxLayout()
        self.__signedCheckBox = QCheckBox('Значения со знаком', parent=self)
        sensorsVBoxLayout.addWidget(self.__signedCheckBox)
        sensorsVBoxLayout.addLayout(receive_elements_layout)
        sensors_groupbox.setLayout(sensorsVBoxLayout)
        return sensors_groupbox
    
    def __createWriteUnitsWidget(self, config: dict):
        send_elements_layout = QGridLayout()
        qlabel = QLabel('Код')
        qlabel.setFixedHeight(20)
        send_elements_layout.addWidget(qlabel, 0, 1)
        # send_elements_layout.addWidget(QLabel('Значение (мм)'), 0, 2)
        
        row  = 1
        for name, params in config['models']['controls'].items():
            send_elements_layout.addWidget(QLabel(name+f" ({str(params['register_id'])})"), row, 0)
            send_element_spin_box = QSpinBox()
            send_element_spin_box.setRange(0, 65535)
            if params.get('projection_range'):
                val = params['projection_range'].get('zero', None)
                val = round((params['projection_range']['max']+params['projection_range']['min'])/2) if val is None else val
            else: 
                val = 0
            send_element_spin_box.setValue(val)
            self.__send_code_widgets[name] = send_element_spin_box
            send_elements_layout.addWidget(send_element_spin_box, row, 1)
            row += 1

        write_elements_button = QPushButton('Отослать значения на контроллер')
        write_elements_button.clicked.connect(self.write_elements_to_controller)

        controls_groupbox = QGroupBox()
        controlsVBoxLayout = QVBoxLayout()
        controlsVBoxLayout.addLayout(send_elements_layout)
        controlsVBoxLayout.addWidget(write_elements_button)
        controls_groupbox.setLayout(controlsVBoxLayout)
        return controls_groupbox

    def createAdjustmentWidget(self, unit_name: str, operation: str = None):
        unitOperationLayout = QHBoxLayout()
        btnAdjustmentOperation = QPushButton('Сдвинуть к')
        unitOperationLayout.addWidget(btnAdjustmentOperation)
        spinboxOperationArg = QDoubleSpinBox()
        spinboxOperationArg.setRange(-200, 200)
        spinboxOperationArg.setFixedWidth(self.StyleSpinBoxWidth)
        unitOperationLayout.addWidget(spinboxOperationArg)
        btnAdjustmentOperation.pressed.connect(
            lambda: self.shift_unit_code_range_to_be_equal_to(name=unit_name, new_value=spinboxOperationArg.value(), config=config))
        return unitOperationLayout

    def set_pendulum_to_zero(self, name: str, config: dict):
        unit_params = config['models']['sensors'].get(name)
        inverse = -1 if unit_params.get('inverse', False) else 1

        cur_value = self.__unit_provider.sensors().get(name).read()
        unit_params['value_range']['min'] = round(unit_params['value_range']['min'] - cur_value*inverse)
        unit_params['value_range']['max'] = round(unit_params['value_range']['max'] - cur_value*inverse)
        new_unit = self.__unit_provider.create_read_unit(name, unit_params)
        # заменяем старый юнит на новый, с новым диаппазоном
        self.__unit_provider.sensors()[name] = new_unit

    def shift_unit_value_range(self, name: str, shift: float, config: dict):
        unit_params = config['models']['sensors'].get(name)
        inverse = -1 if unit_params.get('inverse', False) else 1

        # cur_value = self.__unit_provider.sensors().get(name).read()
        unit_params['value_range']['min'] = round(unit_params['value_range']['min'] - shift*inverse)
        unit_params['value_range']['max'] = round(unit_params['value_range']['max'] - shift*inverse)
        new_unit = self.__unit_provider.create_read_unit(name, unit_params)
        # заменяем старый юнит на новый, с новым диаппазоном
        self.__unit_provider.sensors()[name] = new_unit

    def shift_unit_code_range_to_be_equal_to(self, name: str, new_value: float, config: dict):
        print(f'shift unit {name} to {new_value}')        
        shift_value = self.__unit_provider.sensors().get(name).read() - new_value
        # 
        unit_params = config['models']['sensors'].get(name)
        inverse = -1 if unit_params.get('inverse', False) else 1
        if unit_params['value_range']['min'] > unit_params['value_range']['max']:
            inverse = inverse*-1
        
        units_per_mm = abs(unit_params['projection_range']['max'] - unit_params['projection_range']['min'])/abs(unit_params['value_range']['max'] - unit_params['value_range']['min'])
        units_shift = round(shift_value*units_per_mm ) 
        # обновляем диапазон кодов
        unit_params['projection_range']['min'] = round(unit_params['projection_range']['min'] + units_shift*inverse)
        unit_params['projection_range']['max'] = round(unit_params['projection_range']['max'] + units_shift*inverse)
        new_unit = self.__unit_provider.create_read_unit(name, unit_params)
        # заменяем старый юнит на новый, с новым диаппазоном
        self.__unit_provider.sensors()[name] = new_unit

if __name__ == '__main__':
    # print(f'__name__ = {__name__}')
    app = QApplication(sys.argv)

    config = json.load(open('./resources/config.json', encoding='utf-8'))
    window = MachineAdjustmentWidget(config)
    window.show()

    sys.exit(app.exec())


    