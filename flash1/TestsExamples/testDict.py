a = {}
a['q'] = 11
a['w'] = 12
a['e'] = 13
b = {}
b['q'] =21
b['w'] = 22
b['e'] = 23
c = {}
c['q'] = 44
c['w'] = 45
c['e'] = 55

u = []
u.append(a)
u.append(b)
u.append(c)


def get_summary_column(file, column_name):
    column = []
    for every_dict in file:
        column.append(every_dict[column_name])
    print(column)

get_summary_column(u, 'w')