#!/bin/bash

cp strela_mock.desktop /home/arrow/Рабочий\ стол/
chmod ugo+x /home/arrow/Рабочий\ стол/strela_mock.desktop
gio set /home/arrow/Рабочий\ стол/strela_mock.desktop metadata::trusted true

cp strela_release.desktop /home/arrow/Рабочий\ стол/
chmod ugo+x /home/arrow/Рабочий\ стол/strela_release.desktop
gio set /home/arrow/Рабочий\ стол/strela_release.desktop metadata::trusted true

cp machine_settings.desktop /home/arrow/Рабочий\ стол/
chmod ugo+x /home/arrow/Рабочий\ стол/machine_settings.desktop
gio set /home/arrow/Рабочий\ стол/machine_settings.desktop metadata::trusted true