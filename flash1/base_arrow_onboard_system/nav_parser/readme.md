### Генерация exe-файла:

`pyinstaller .\nav_exporter.py --onefile --clean -n nav_parser`

### Запуск утилиты:

`navparser.exe <имя_файла> <степ_начала> <степ_конца> --set-picket <значение_степа> <значение_пикета_метры>`

### Пример:

`navparser.exe D:\Navigator.DB\20231128_074539_Аф-Сев.nav 1500 1800`
