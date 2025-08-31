import pandas as pd
import numpy as np

list1 = [7058, 7059, 7075, 7076]

list2 = [7058, 7059, 7012, 7075, 7076]

list11 = ["Sravan", "Jyothika", "Deepika", "Kyathi"]

list22 = ["Sravan", "Jyothika", "Salma", "Deepika", "Kyathi"]

dataframe1 = pd.DataFrame({"Student ID": list1, "Student Name": list11})
#print('First data frame:', dataframe1)

dataframe2 = pd.DataFrame({"Student ID": list2, "Student Name": list22})
#print('Second data frame:', dataframe2)


mergedf = dataframe2.merge(dataframe1, how='left')
print('Merged data frame:', mergedf)
