import numpy as np
import pandas as pd
from string import ascii_uppercase
from numpy.random import default_rng

round_precision = 3
nrows = 500
rand = default_rng()


df = pd.DataFrame({
    'picket': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'plan_mes': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'plan_prj': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'plan_d': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'prof_mes': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'prof_prj': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'prof_d': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'vozv_mes': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'vozv_prj': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'col10': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'col11': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'col12': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'col13': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
    'col14': rand.uniform(low=-100.0, high=100.0, size=nrows).round(decimals=round_precision),
})
df.to_csv('example_csv_file.csv', index=None)
