import streamlit as st
import numpy as np

def input_strength_basis(prefix: str) -> str:
    return st.radio(
        "Strength Basis",
        ["Design Values (fcd, fyd)", "Characteristic Values (fck, fyk)"],
        horizontal=True,
        key=f"{prefix}_strength_basis",
    )

def input_materials_concrete(prefix: str) -> float:
    fc = st.number_input("Concrete (fck) [MPa]", min_value=0.1, value=20.0, step=5.0, key=f"{prefix}_fc")
    return fc

def input_nu_requirment(prefix: str) -> float:
    Nu_kN_req = st.number_input(
        "Applied axial load Nu [kN]",
        value=2000.0,
        step=50.0,
        key=f"{prefix}_Nu"
    )
    return Nu_kN_req

def input_materials_steel_fyk(prefix: str) -> float:
    fy = st.number_input("Steel (fyk) [MPa]", min_value=0.1, value=420.0, step=10.0, key=f"{prefix}_fy")
    return fy

def input_materials_steel_fywk(prefix: str) -> float:
    fywk = st.number_input("Steel (fywk) [MPa]", min_value=0.1, value=220.0, step=10.0, key=f"{prefix}_fywk")
    return fywk

def input_column_geometry(prefix: str) -> str:
    shape = st.selectbox("Column Shape", ["Rectangular", "Circular"], key=f"{prefix}_shape")
    return shape

def input_confinement_type_capacity(prefix: str) -> str:
    reinf_style = st.selectbox("Confinement Type", ["Tied (Standard)", "Spiral / Circular", "Plain Concrete (No Reinforcement)"], key=f"{prefix}_conf_label")        
    return reinf_style

def input_confinement_type_ast(prefix: str) -> str:
    reinf_style = st.selectbox("Confinement Type", ["Tied (Standard)", "Spiral / Circular"], key=f"{prefix}_conf_label")        
    return reinf_style

def input_confinement_type_ao(prefix: str) -> str:
    reinf_style = st.selectbox("Confinement Type", ["Spiral / Circular"], key=f"{prefix}_conf_label")        
    return reinf_style

def input_confinement_type_ac(prefix: str) -> str:
    reinf_style = st.selectbox("Confinement Type", ["Tied (Standard)", "Spiral / Circular", "Plain Concrete (No Reinforcement)"], key=f"{prefix}_conf_label")        
    return reinf_style

def input_confinement_type_ack(prefix: str) -> str:
    reinf_style = st.selectbox("Confinement Type", ["Spiral / Circular"], key=f"{prefix}_conf_label")        
    return reinf_style

def input_section_dimensions(prefix: str, shape: str):
    c1, c2 = st.columns(2)

    if shape == "Rectangular":
        with c1:
            b = st.number_input("Width (b) [mm]", min_value=1.0, value=500.0, step=10.0, key=f"{prefix}_b")
        with c2:
            h = st.number_input("Depth (h) [mm]", min_value=1.0, value=500.0, step=10.0, key=f"{prefix}_h")
        dims = (b, h)
        Ag = b * h
    else:
        with c1:
            D = st.number_input("Diameter (D) [mm]", min_value=1.0, value=300.0, step=10.0, key=f"{prefix}_D")
        dims = (D,)
        Ag = np.pi * D**2 / 4

    return dims, Ag

def input_bar_diameter(prefix: str, default: float = 20.0) -> float:
    bar_dia = st.number_input(
        "Bar Diameter [mm]", min_value=1.0,
        value=default, step=2.00,
        key=f"{prefix}_bar_dia"
    )
    return bar_dia

def input_num_bars(prefix: str, default: int = 8, min_bars: int = 4) -> int:
    num_bars = st.number_input(
        "Number of Bars",
        value=default,
        min_value=min_bars,
        step=1,
        key=f"{prefix}_num_bars"
    )
    return int(num_bars)

def calc_Ast(num_bars: int, bar_dia: float) -> float:
    # Ast in mm^2
    return float(num_bars) * np.pi * (bar_dia / 2.0) ** 2

def input_spiral_bar_dia(prefix: str, default: float = 10.0) -> float:
    return st.number_input(
        "Spiral Bar φ [mm]", min_value=1.0,
        value=default, step=2.00,
        key=f"{prefix}_spiral_dia"
    )

def input_spiral_spacing(prefix: str, default: float = 50.0) -> float:
    return st.number_input(
        "Spiral Spacing s [mm]", min_value=1.0,
        value=default, step=1.00,
        key=f"{prefix}_spiral_s"
    )


def input_core_diameter(prefix: str, default: float = 250.0) -> float:
    return st.number_input(
        "Core Diameter Ack [mm]", min_value=1.0,
        value=default, step=10.0,
        key=f"{prefix}_Dk"
    )
