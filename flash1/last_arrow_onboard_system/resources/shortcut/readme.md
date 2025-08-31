# Автоматическое копирование:
1. sudo chmod +x deploy_shortcut.sh
2. ./deploy_shortcut.sh

# Ручное копирование:
1. Копируем файл strela_release.desktop в папку Desktop (Рабочий стол) в домашнем каталоге:
`cp strela_release.desktop ~/Рабочий\ стол/`

2. Делаем его исполняемым:
`chmod ugo+x ~/Рабочий\ стол/strela_release.desktop`

3. Делаем его доверенным:
`gio set ~/Рабочий\ стол/strela_release.desktop metadata::trusted true`