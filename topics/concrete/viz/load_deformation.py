import matplotlib.pyplot as plt
import numpy as np

def plot_load_deformation(results):

    fig, ax = plt.subplots()

    x = np.linspace(0,1,50)
    y = results.N1 * (1 - np.exp(-5*x))

    ax.plot(x, y, label="N1 Capacity")
    ax.axhline(results.N2, linestyle="--", label="N2 Capacity")

    ax.set_xlabel("Strain")
    ax.set_ylabel("Load (kN)")
    ax.legend()

    return fig
