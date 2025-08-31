import numpy as np

def servo_piecewise_linear_interpolation(x: float, start_value: int, zero_value: int, zero_range: tuple, modbus_range: tuple, value_range: tuple) -> float:
    """
    """
    k = -1 if modbus_range[0] > modbus_range[1] else 1
    if x < value_range[0]:
        return modbus_range[0]
    if x > value_range[1]:
        return modbus_range[1]    
    if zero_range[0] <= x <= zero_range[1]:
        return zero_value
    if value_range[0] <= x < zero_range[0]:
        return np.interp(x, (value_range[0], zero_range[0]), (modbus_range[0], zero_value-k*start_value))
    if zero_range[1] < x <= value_range[1]:
        return np.interp(x, (zero_range[1], value_range[1]), (zero_value+k*start_value, modbus_range[1]))
    return zero_value


# SERVO_START_VALUE = 10

# def servo_interpolation(x: float, start_value: int, zero_value: int, zero_range: tuple, modbus_range: tuple, value_range: tuple) -> float:
#     """
#     """
#     k = -1 if modbus_range[0] > modbus_range[1] else 1
#     if x < value_range[0]:
#         return modbus_range[0]
#     if x > value_range[1]:
#         return modbus_range[1]    
#     if zero_range[0] <= x <= zero_range[1]:
#         return zero_value
#     if value_range[0] <= x < zero_range[0]:
#         return np.interp(x, (value_range[0], zero_range[0]), (modbus_range[0], zero_value-k*start_value))
#     if zero_range[1] < x <= value_range[1]:
#         return np.interp(x, (zero_range[1], value_range[1]), (zero_value+k*start_value, modbus_range[1]))
#     return zero_value

# def servo_lining_interpolation(x: float, 
#                                start_value: int = SERVO_START_VALUE, 
#                                zero_value: int = -15,
#                                zero_range: tuple = (-0.5,0.5),
#                                modbus_range: tuple = (-150,120),
#                                value_range: tuple = (-30,30)    ) -> float:
#     """
#     "lining": {
#         "interpolation_type": "linear",
#         "projection_range": {
#             "start_value": 10,
#             "zero": -15,
#             "min": -150,
#             "max": 120                    
#         },
#         "value_range": {
#             "zero_range": [-0.5,0.5],
#             "min": -30,
#             "max": 30
#         }
#     }
#     1.	[-0.5, 0.5] -> -15
#     2.	[-30, -0.5] -> [-150, -45]
#     3.	[0.5, 30]   -> [15, 120]
#     """
#     return servo_interpolation(x, start_value=start_value, zero_value=zero_value, zero_range=zero_range, modbus_range=modbus_range, value_range=value_range)

# def servo_left_interpolation(x: float,                              
#                              start_value: int = SERVO_START_VALUE, 
#                              zero_value: int = 0,
#                              zero_range: tuple = (-0.5,0.5),
#                              modbus_range: tuple = (150,-150),
#                              value_range: tuple = (-30,30)) -> float:
#     """
#     "lifting_left": {
#         "projection_range": {
#             "zero": 0,
#             "start_value": 30,
#             "min": 150,
#             "max": -150
#         },
#         "value_range": {
#             "min": -30,
#             "max": 30
#         }
#     }
#     1.	[-0.5, 0.5] -> 0
#     2.	[-30, -0.5] -> [150, 30]
#     3.	[0.5, 30]   -> [-30, -150]
#     """
#     return servo_interpolation(x, start_value=start_value, zero_value=zero_value, zero_range=zero_range, modbus_range=modbus_range, value_range=value_range)

# def servo_right_interpolation(x: float,                              
#                              start_value: int = 20, 
#                              zero_value: int = 60,
#                              zero_range: tuple = (-0.5,0.5),
#                              modbus_range: tuple = (150,-30),
#                              value_range: tuple = (-30,30)) -> float:
#     """
#     "lifting_right": {
#         "projection_range": {
#             "zero": 60,
#             "min": 150,
#             "max": -30
#         },
#         "value_range": {
#             "min": -30,
#             "max": 30
#         }
#     1.	[-0.5, 0.5] -> 60
#     2.	[-30, -0.5] -> [150, 30]
#     3.	[0.5, 30]   -> [90, -30]
#     """
#     return servo_interpolation(x, start_value=start_value, zero_value=zero_value, zero_range=zero_range, modbus_range=modbus_range, value_range=value_range)