import matplotlib.pyplot as plt
import numpy as np

# ======================================
# 2. PLOT: LOAD vs DEFORMATION
# ======================================
def plot_load_deformation(N1, N2, trans_type):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    
    # --- STYLING FOR DARK MODE ---
    text_color = "white"
    ax.spines['bottom'].set_color(text_color)
    ax.spines['left'].set_color(text_color)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)
    ax.yaxis.label.set_color(text_color)
    ax.xaxis.label.set_color(text_color)

    if trans_type == "Spiral":
        if N2 > N1:
            x = np.array([0, 1.0, 2.0, 3.5, 5.5, 6.5]) 
            y = np.array([0, N1,  0.85*N1, N2, N2, N2*0.9]) 
            color = "#00BFFF" 
            ax.annotate('First Peak\n(Shell Spalls)', xy=(1.0, N1), xytext=(0.5, N1+N1*0.1),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
            ax.annotate('Second Peak\n(Confined Core)', xy=(3.5, N2), xytext=(3.5, N2+N2*0.1),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
            ax.annotate('Ductile Plateau', xy=(5.5, N2), xytext=(5.5, N2-N2*0.15),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
            ax.axhline(y=N1, color='gray', linestyle='--', alpha=0.5)
        else:
            x = np.array([0, 1.0, 2.0, 3.5, 5.0])
            y = np.array([0, N1,  0.80*N1, N2, N2*0.8]) 
            color = "#FF4B4B" 
            ax.annotate('First Peak\n(Governs)', xy=(1.0, N1), xytext=(1.5, N1+N1*0.15),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), color=text_color)
            ax.annotate('Spiral too weak', xy=(3.5, N2), xytext=(3.5, N2+N2*0.15),
                        arrowprops=dict(facecolor=text_color, arrowstyle='->'), ha='center', color=text_color)
    else: 
        x = np.array([0, 1.0, 2.5, 4.0])
        y = np.array([0, N1, 0.5*N1, 0.3*N1])
        color = "#FFA500" 
        ax.annotate('Failure ($N_{max}$)', xy=(1.0, N1), xytext=(1.5, N1),
                    arrowprops=dict(facecolor=text_color, arrowstyle='->'), color=text_color)

    if HAS_SCIPY:
        try:
            interpolator = PchipInterpolator(x, y)
            x_smooth = np.linspace(x.min(), x.max(), 300)
            y_smooth = interpolator(x_smooth)
            ax.plot(x_smooth, y_smooth, color=color, linewidth=3)
        except:
            ax.plot(x, y, color=color, linewidth=3)
    else:
        ax.plot(x, y, color=color, linewidth=3, linestyle='-')
    
    ax.set_xlabel(r"Axial Shortening ($\delta$)", fontsize=11)
    ax.set_ylabel("Axial Load (N)", fontsize=11)
    ax.set_ylim(bottom=0, top=max(N1, N2)*1.3)
    ax.set_xlim(left=0)
    return fig
