import csv
import pandas as pd
import random
from random import uniform

filename = "example_csv_file.csv"


def read_csv_file(file, n):
    df = pd.read_csv(file)    # index_col=False, header=None,
    #print(df.shape)    # (100,1)
    print(df.loc[:, 'prof_prj'])    #df.iloc[:, n] )


    #col = df.iloc[:, number_]  # df.iloc[:, number]       df.loc['prof_prj']
    #print(col.tolist())
    # return col.tolist()

read_csv_file(filename, 1)