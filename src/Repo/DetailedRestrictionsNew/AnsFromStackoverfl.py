
def line_equation(x1, y1, x2, y2):
    if x1 == x2:
        return f"x = {x1}" # Вертикальная линия
    elif y1 == y2:
        return (0, y1)  #f"y = {y1}" # Горизонтальная линия
    else:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
    return (slope, intercept)  


print(line_equation(100, 30, 200, 30))
