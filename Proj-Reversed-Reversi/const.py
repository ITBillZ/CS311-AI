import numpy as np

COLOR_BLACK = -1
COLOR_WHITH = 1
COLOR_NONE = 0
INT_MIN = -10e5
INT_MAX = 10e5

WEIGHT_MAP = -np.array([[500, -25, 10, 5, 5, 10, -25, 500],
                        [-25, -45, 1, 1, 1, 1, -45, -25],
                        [10, 1, 3, 2, 2, 3, 1, 10],
                        [5, 1, 2, 1, 1, 2, 1, 5],
                        [5, 1, 2, 1, 1, 2, 1, 5],
                        [10, 1, 3, 2, 2, 3, 1, 10],
                        [-25, -45, 1, 1, 1, 1, -45, -25],
                        [500, -25, 10, 5, 5, 10, -25, 500]])