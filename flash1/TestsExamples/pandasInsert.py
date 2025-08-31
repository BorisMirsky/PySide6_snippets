import pandas as pd

# Create a sample DataFrame
data = {'age': [21, 22, 27, 28, 34, 67, 88],
        'name': ['sss', 'ddd', 'Suww', 'xzs', 'qqq', 'www', 'eee'],
        'address': ['MP', 'jhy', 'UP', 'jytr', 'dfg', 'vbn', 'nmnm']}



print(data['age'][1:-1].max())