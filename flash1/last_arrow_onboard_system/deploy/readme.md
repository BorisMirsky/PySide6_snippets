Сборка проекта под Ubuntu 22.04

Устанавливаем pyinstaller
pip install pyinstaller


Запускаем сборку демо-проекта:
pyinstaller mock_run.spec

Запускаем сборку проекта для машины:
pyinstaller release_run.spec

Запускаем сборку утилиты:
pyinstaller machine_settings.spec

В папке dist находится сборка для запуска необходимо рядом положить папку resources
