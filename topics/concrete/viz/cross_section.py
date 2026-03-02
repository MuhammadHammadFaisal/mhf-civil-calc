import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_cross_section(inputs):

    fig, ax = plt.subplots(figsize=(4,4))

    ax.add_patch(
        patches.Rectangle(
            (0,0),
            inputs.width,
            inputs.height,
            fill=False,
            linewidth=2
        )
    )

    x_positions = np.linspace(
        inputs.cover,
        inputs.width - inputs.cover,
        inputs.num_bars
    )

    for x in x_positions:
        ax.add_patch(
            patches.Circle(
                (x, inputs.cover),
                inputs.bar_diameter/2,
                fill=True
            )
        )

    ax.set_xlim(-20, inputs.width + 20)
    ax.set_ylim(-20, inputs.height + 20)
    ax.set_aspect('equal')
    ax.set_title("Cross Section")

    return fig
