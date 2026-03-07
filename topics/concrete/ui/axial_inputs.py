import streamlit as st
import numpy as np

def input_strength_basis(prefix: str):
    return st.radio(
        "Strength Basis",
        ["Design Values (fcd, fyd)", "Characteristic Values (fck, fyk)"],
        horizontal=True,
        key=f"{prefix}_strength_basis",
    )

def input_materials_basic(prefix: str, steel_label: str = "Steel (fyk) [MPa]"):
    c1, c2 = st.columns(2)
    with c1:
        fc = st.number_input("Concrete (fck) [MPa]", value=20.0, key=f"{prefix}_fc")
    with c2:
        fy = st.number_input(steel_label, value=420.0, key=f"{prefix}_fy")
    return fc, fy

def input_geometry_config(prefix: str, allow_plain: bool = False, ties_only: bool = False):
    c1, c2 = st.columns(2)

    with c1:
        shape = st.selectbox("Column Shape", ["Rectangular", "Circular"], key=f"{prefix}_shape")

    with c2:
        if ties_only:
            st.selectbox("Confinement Type", ["Tied (Standard Hoops)"], key=f"{prefix}_conf_label")
            reinf_style = "Standard Ties (Match Shape)"
        else:
            options = {
                "Spiral (Continuous Helix)": "Spiral / Circular",
                "Tied (Standard Hoops)": "Standard Ties (Match Shape)",
            }
            if allow_plain:
                options["Plain Concrete (No Reinforcement)"] = "None (Plain Concrete)"

            selected_label = st.selectbox("Confinement Type", list(options.keys()), key=f"{prefix}_conf_label")
            reinf_style = options[selected_label]

    return shape, reinf_style

def input_section_dimensions(prefix: str, shape: str):
    c1, c2 = st.columns(2)

    if shape == "Rectangular":
        with c1:
            b = st.number_input("Width (b) [mm]", value=500.0, key=f"{prefix}_b")
        with c2:
            h = st.number_input("Depth (h) [mm]", value=500.0, key=f"{prefix}_h")
        dims = (b, h)
        Ag = b * h
    else:
        with c1:
            D = st.number_input("Diameter (D) [mm]", value=300.0, key=f"{prefix}_D")
        dims = (D,)
        Ag = np.pi * D**2 / 4

    return dims, Ag

def input_longitudinal_steel(prefix: str, reinf_style: str, min_bars: int = 4):
    # Defaults so nothing crashes
    bar_dia = 0.0
    num_bars = 0
    Ast = 0.0

    if "None" not in reinf_style:
        c1, c2 = st.columns(2)
        with c1:
            bar_dia = st.number_input("Bar Diameter [mm]", value=20.0, key=f"{prefix}_bar_dia")
        with c2:
            num_bars = st.number_input("Number of Bars", value=8, min_value=min_bars, key=f"{prefix}_num_bars")

        Ast = num_bars * np.pi * (bar_dia / 2) ** 2

    return bar_dia, num_bars, Ast

def input_spiral_details(prefix: str, shape: str, reinf_style: str):
    # Defaults so nothing crashes
    spiral_dia = 0.0
    spiral_spacing = 0.0
    fywk = 0.0
    Dk = 0.0

    if "Spiral" in reinf_style:
        c1, c2 = st.columns(2)
        with c1:
            spiral_dia = st.number_input("Spiral Bar φ [mm]", value=10.0, key=f"{prefix}_spiral_dia")
            fywk = st.number_input("Spiral Steel ($f_{ywk}$) [MPa]", value=220.0, key=f"{prefix}_fywk")
        with c2:
            spiral_spacing = st.number_input("Spiral Spacing s [mm]", value=50.0, key=f"{prefix}_spiral_s")
            if shape == "Circular":
                Dk = st.number_input("Core Diameter $D_k$ [mm]", value=250.0, key=f"{prefix}_Dk")

    return spiral_dia, spiral_spacing, fywk, Dk
