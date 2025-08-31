
# [(49, 40), (49, 30), (119, 40), (119, 30), (215, 30), (215, 20), (277, 30), (277, 20), (315, 30), (315, 35), (386, 30), (386, 35)]
# list_ = [(49, 40), (49, 30), (119, 40), (119, 30), (215, 30), (215, 20), (277, 30), (277, 20), (315, 30), (315, 35), (386, 30), (386, 35)]
#
# if list_[0][0] > 0:
#     list_[0] = (0, 30)
# list_[-1] = (500, 30)

# [(0, 30), (49, 30), (119, 40), (119, 30), (215, 30), (215, 20), (277, 30), (277, 20), (315, 30), (315, 35), (386, 30), (500, 30)]

list_ = [(0, 10), (10, 55), (20, -15), (30, 5), (40, 15)]

def func(some_list): #, base_y):
    result = [[x] for x in range(0, 41, 1)]
    for i in range(0, 41, 1):
        for j in range(0, len(some_list) + 1, 1):
            try:
                if some_list[j][0] <= result[i][0] < some_list[j+1][0]:
                    result[i].append(some_list[j][1])
            except IndexError:
                pass
    print(result)


#func(list_)

def piecewise_linear_func ():
    sorted_list = [(0, 30), (54, 30), (54, 40), (237, 40), (237, 30)]    #sorted(self.edit_decision_list, key=lambda x: x[0])
    result = [[x] for x in range(0, 501, 1)]
    for i in range(0, 501, 1):
        for j in range(0, len(sorted_list) + 1, 1):
            try:
                if sorted_list[j][0] <= result[i][0] < sorted_list[j + 1][0]:
                    result[i].append(sorted_list[j][1])
            except IndexError:
                pass
    print(sorted_list, '\n')
    print(result)

piecewise_linear_func()
