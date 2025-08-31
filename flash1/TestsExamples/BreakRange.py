
# if 1 < chart_window_size < 5:
#     chart.y_axis.setTickInterval(1)
# elif 5 < chart_window_size < 10:
#     chart.y_axis.setTickInterval(2)
# elif 10 < chart_window_size < 50:
#     chart.y_axis.setTickInterval(10)
# elif 50 < chart_window_size < 100:
#     chart.y_axis.setTickInterval(20)
# elif 100 < chart_window_size < 500:
#     chart.y_axis.setTickInterval(100)
# elif 500 < chart_window_size < 1000:
#     chart.y_axis.setTickInterval(200)
# else:
#     chart.y_axis.setTickInterval(500)

def func(some_param):
    if 1 < some_param < 5:
        result = 1
    elif 5 < some_param < 10:
        result = 2
    elif 10 < some_param < 50:
        result = 10
    elif 50 < some_param < 100:
        result = 20
    elif 100 < some_param < 500:
        result = 100
    elif 500 < some_param < 1000:
        result = 200
    else:
        result = 500
    print(result)

func(32)
