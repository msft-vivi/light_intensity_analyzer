class FilmThickness():
    def __init__(self):
        pass

    @staticmethod
    def get_thickness(index, x):
        if index == 0:
            return -18.79*x**3 + 4.364*x**2 - 22.5*x + 13.41
        elif index == 1:
            return 19.28*x**3 - 2.738*x**2 + 36.44*x + 125.1
        elif index == 2:
            return -18.53*x**3 + 0.667*x**2 - 23.13*x + 225.7
        elif index == 3:
            return 12.39*x**3 - 0.638*x**2 + 40.4*x + 336.1
        elif index == 4:
            return -17.91*x**3 - 0.651*x**2 - 23*x + 437.8
        elif index == 5:
            return 14.91*x**3 + 0.082*x**2 + 38.74*x + 547.4
        elif index == 6:
            return -32.83*x**3 + 1.809*x**2 - 22.05*x + 649.7
        elif index == 7:
            return 14.12*x**3 - 2.533*x**2 - 40.46*x + 759.9
        else:
            return 1000