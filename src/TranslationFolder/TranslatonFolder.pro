TRANSLATIONS += \
    Translations/TranslatonFolder_ru.ts
 
system(lrelease \"$$_PRO_FILE_\")
 
tr.commands = lupdate \"$$_PRO_FILE_\" && lrelease \"$$_PRO_FILE_\"
    PRE_TARGETDEPS += tr
    QMAKE_EXTRA_TARGETS += tr