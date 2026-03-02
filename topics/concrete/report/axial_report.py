import streamlit as st

def render_report(inputs, results):

    st.subheader("Step-by-Step Calculation Report")

    st.markdown("#### Design Strengths")
    st.metric("fcd", f"{results.fcd:.2f} MPa")
    st.metric("fyd", f"{results.fyd:.2f} MPa")

    st.markdown("#### Reinforcement Ratio")
    st.write(f"ρ = {results.rho_percent:.2f}%")

    st.markdown("#### Unconfined Capacity")
    st.write(f"N_or = {results.Nor1/1000:.0f} kN")

    if results.Nor2 > 0:
        st.markdown("#### Confined Capacity")
        st.write(f"N_or2 = {results.Nor2/1000:.0f} kN")
