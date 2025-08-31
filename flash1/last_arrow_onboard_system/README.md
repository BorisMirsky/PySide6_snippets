# Стрела ДС
## Клонирование репозитория
```
git clone --recurse-submodules -b dev/main git@gitlab.vniizht.lan:strela-ds/arrow_machine_manager/arrow_onboard_system.git 
```

## Настройка среды разработки
```
Создаем виртуальное окружение:
python -m vevn strela

Активируем его:
source strela/bin/activate

Переходим в корень проекта:
cd arrow_onboard_system

Устанавливаем библиотеки:
pip install -r requiments.txt
```

## Запуск приложения
Запуск для разработки и тестирования:
```
python3 mock_run.py
```
### Настройки для разработки:

**Выбор направления движения машины для тестов**:

Тестовые данные данные изменяются (движение вперед / назад)
в файле:
`mock_run.py`

`строка 109:    units = MockUnitProvider(config)`

**перейти в метод и изменить значение `MovingDirection` в соответствии с описанием**:

Движение вперед: `register = TickCounterMockProvider(25, ticks_direction=MovingDirection.Backward, parent=QApplication.instance())`\
Движение назад: `register = TickCounterMockProvider(25, ticks_direction=MovingDirection.Forward, parent=QApplication.instance())`


**Запуск при наличии блока управления:**
```
python3 release_run.py
```

## Перевод приложения
Генерация файла перевода выполняется с помощью утилиты `pylupdate6` из корня проекта. Утилита содержится в библиотеке PyQt6 (`pip install pyqt6`).
Утилита, которая идет с библиотекой PySide6 (pyside6-lupdate) почему-то не работает, поэтому для генерации перевода прийдется поставить PyQt6.
```
pylupdate6 ./ --no-obsolete -ts resources/translations/ru.ts
```
Для перевода полученного файла запускаем утилиту `pyside6-linguist`, которая имеет пользовательский интерфейс. В ней выбираем сгенерированный файл ru.ts. Лежит в виртуальном окружении, там куда поставили `pip install PySide6`. 


## Перевод приложения вариант2
Установить `Qt6` -> перейти в директорию с файлом и  выполнить команду 
```
lrelease ru.ts
```


## Сборка приложения
```
Устанавливаем pyinstaller
pip install pyinstaller

Запускаем сборку демо-проекта:
pyinstaller mock_run.spec

Запускаем сборку проекта для машины:
pyinstaller release_run.spec

Запускаем сборку утилиты:
pyinstaller machine_settings.spec
```
В папке dist находится сборка. Для запуска необходимо рядом положить папку resources.

## Утилиты
### Тарировка машины
Запуск утилиты без привязки к **config.json**, т.е. просмотр пришедшего массива (receive-count=15) и отправка массива (send-count=10). 
```
python ./arrow_com_port_view_panel.py --port=/dev/ttyUSB0 --baud-rate=115200 --receive-count=15 --send-count=10 --send-message-timeout=30
```
Запуск утилиты с привязкой к файлу **config.json**. Количество получаемых и отправляемых элементов берется из файла, также как и конвертация кодов в миллиметры.
```
python ./com_port_view_panel.py
```

Запуск новой версии утилиты (пока в разработке): 
```
python -m tools.machine_adjustment
```
