#!/usr/bin/env python
import os
import subprocess


for file in os.listdir('./tests'):
    if len(file.split('.')) == 2 and file.split('.')[1] == 'py' and file.split('.')[0]:
        abs_path = os.path.abspath('/tests/' + file)
        my_script = 'python3 tests/{}'.format(file)
        #print(my_script)
        subprocess.run(my_script, shell=True)


#subprocess.run("python3 tests/testfile1.py & python3 tests/testfile2.py & python3 tests/testfile3.py", shell=True)