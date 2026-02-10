import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ======================================
# 1. DRAW CROSS SECTION
# ======================================

def draw_cross_section(shape, dims, num_bars, bar_dia, cover):
    fig, ax = plt.subplots(figsize=(4,4))
    bar_r = bar_dia / 2

    if shape in ["Rectangular", "Square"]:
        b, h = dims
        ax.add_patch(patches.Rectangle((0,0), b, h,
                                       facecolor="#e0e0e0",
                                       edgecolor="black"))

        # Circular confined core visualization
        D_core = min(b,h) - 2*cover
        cx, cy = b/2, h/2
        ax.add_patch(patches.Circle((cx,cy), D_core/2,
                                   fill=False,
                                   linestyle="--",
                                   edgecolor="blue"))

        # Bar placement (simple corner + uniform)
        positions = []
        spacing_x = (b-2*(cover+bar_r))/(num_bars/2)
        for i in range(num_bars//2):
            positions.append((cover+bar_r+i*spacing_x, cover+bar_r))
            positions.append((cover+bar_r+i*spacing_x, h-cover-bar_r))

        for x,y in positions:
            ax.add_patch(patches.Circle((x,y), bar_r, color="red"))

        ax.set_xlim(-50,b+50)
        ax.set_ylim(-50,h+50)

    else:
        D = dims[0]
        cx, cy = D/2, D/2

        ax.add_patch(patches.Circle((cx,cy), D/2,
                                   facecolor="#e0e0e0",
                                   edgecolor="black"))

        D_core = D - 2*cover
        ax.add_patch(patches.Circle((cx,cy), D_core/2,
                                   fill=False,
                                   linestyle="--",
                                   edgecolor="blue"))

        angles = np.linspace(0,2*np.pi,num_bars,endpoint=False)
        r = D/2 - cover - bar_r

        for a in angles:
            x = cx + r*np.cos(a)
            y = cy + r*np.sin(a)
            ax.add_patch(patches.Circle((x,y), bar_r, color="red"))

        ax.set_xlim(-50,D+50)
        ax.set_ylim(-50,D+50)

    ax.set_aspect("equal")
    ax.axis("off")
    return fig


# ======================================
# 2. MAIN APP
# ======================================

def app():

    st.title("TS500 Spiral Confined Column Capacity")

    # -------- Inputs --------
    shape = st.selectbox("Column Shape",
                         ["Rectangular","Square","Circular"])

    fc = st.number_input("Concrete Strength fc [MPa]", value=25.0)
    fy = st.number_input("Steel Strength fy [MPa]", value=420.0)
    cover = st.number_input("Cover [mm]", value=30.0)

    # Geometry
    if shape == "Rectangular":
        b = st.number_input("Width b [mm]", value=300.0)
        h = st.number_input("Depth h [mm]", value=400.0)
        Ag = b*h
        dims = (b,h)

    elif shape == "Square":
        a = st.number_input("Side a [mm]", value=350.0)
        Ag = a*a
        dims = (a,a)

    else:
        D = st.number_input("Diameter D [mm]", value=300.0)
        Ag = np.pi*D**2/4
        dims = (D,)

    # Longitudinal steel
    bar_dia = st.number_input("Bar Diameter [mm]", value=16.0)
    num_bars = st.number_input("Number of Bars", value=8)

    Ast = num_bars * np.pi * (bar_dia/2)**2

    # Spiral reinforcement
    st.subheader("Spiral Reinforcement")

    spiral_dia = st.number_input("Spiral Diameter [mm]", value=8.0)
    spiral_spacing = st.number_input("Spiral Spacing s [mm]", value=80.0)

    # -------- Visualization --------
    fig = draw_cross_section(shape, dims, num_bars, bar_dia, cover)
    st.pyplot(fig)

    # -------- TS500 Calculations --------
    if st.button("Analyze Capacity"):

        gamma_c = 1.5
        gamma_s = 1.15

        fcd = fc/gamma_c
        fyd = fy/gamma_s

        # -------- Unconfined Capacity --------
        Nor1 = 0.85*fcd*(Ag-Ast) + Ast*fyd

        st.subheader("Peak 1: Unconfined Capacity")
        st.latex(r"N_{or} = 0.85 f_{cd}(A_g-A_{st}) + A_{st} f_{yd}")
        st.write(f"{Nor1/1000:.1f} kN")

        # -------- Confined Core --------
        if shape == "Circular":
            D_col = dims[0]
            D_core_outer = D_col - 2*cover
            D_core_center = D_col - 2*(cover + spiral_dia/2)

        else:
            D_core_outer = min(dims) - 2*cover
            D_core_center = min(dims) - 2*(cover + spiral_dia/2)

        Ack = np.pi * D_core_outer**2 / 4
        Asp = np.pi * spiral_dia**2 / 4

        rho_s = 4*Asp/(D_core_center*spiral_spacing)

        rho_min1 = 0.45*(fc/fy)*((Ag/Ack)-1)
        rho_min2 = 0.12*(fc/fy)
        rho_min = max(rho_min1, rho_min2)

        st.subheader("Spiral Ratio")
        st.write(f"ρs = {rho_s:.4f}")
        st.write(f"ρs(min) = {rho_min:.4f}")

        # -------- Confined Strength --------
        fcc = 0.85*fc + 2*rho_s*fy
        fccd = fcc/gamma_c

        # -------- Confined Capacity --------
        Nor2 = fccd*Ack + Ast*fyd

        st.subheader("Peak 2: Confined Capacity")
        st.latex(r"N_{or2} = f_{ccd}A_{ck} + A_{st}f_{yd}")
        st.write(f"{Nor2/1000:.1f} kN")

        if Nor2 > Nor1:
            st.success("Confined capacity governs")
        else:
            st.warning("Unconfined capacity governs")


if __name__ == "__main__":
    app()
