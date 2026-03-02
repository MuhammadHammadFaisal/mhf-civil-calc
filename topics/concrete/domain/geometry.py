import numpy as np

def gross_area(shape, dims):
    if shape == "Circular":
        return np.pi * dims[0]**2 / 4
    elif shape == "Square":
        return dims[0]**2
    else:
        return dims[0] * dims[1]

def steel_area(num_bars, bar_dia):
    return num_bars * np.pi * (bar_dia / 2)**2

def core_area(core_diameter):
    return np.pi * core_diameter**2 / 4

def spiral_area(spiral_dia):
    return np.pi * spiral_dia**2 / 4
