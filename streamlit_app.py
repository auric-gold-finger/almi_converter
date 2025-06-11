import streamlit as st
import numpy as np

# Streamlit app
st.title("ALMI Lean Mass Goal Calculator")
st.write("Calculate the lean body mass gain needed to achieve your target ALMI.")

# Input section
st.header("Input Your Metrics")
unit_system = st.radio("Unit System", ["Metric", "Imperial"])

if unit_system == "Metric":
    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
    height_m = height_cm / 100
else:
    height_in = st.number_input("Height (inches)", min_value=40.0, max_value=100.0, value=67.0, step=0.1)
    # Convert imperial to metric
    height_m = height_in * 0.0254

# ALMI inputs
st.header("Set Your ALMI Values")
col1, col2 = st.columns(2)
with col1:
    current_almi = st.number_input("Current ALMI (kg/m²)", min_value=3.0, max_value=15.0, value=6.0, step=0.1)
with col2:
    target_almi = st.number_input("Target ALMI (kg/m²)", min_value=3.0, max_value=15.0, value=7.0, step=0.1)

# Calculate required lean mass
if st.button("Calculate"):
    # Current and target appendicular lean mass (ALM)
    current_alm = current_almi * height_m ** 2
    target_alm = target_almi * height_m ** 2

    # Total lean mass (assuming ALM is ~75% of total lean mass)
    current_lean_mass = current_alm / 0.75
    target_lean_mass = target_alm / 0.75

    # Lean mass gain required
    lean_mass_gain = target_lean_mass - current_lean_mass

    st.header("Results")
    st.write(f"**Current ALMI**: {current_almi:.1f} kg/m²")
    st.write(f"**Target ALMI**: {target_almi:.1f} kg/m²")
    st.write(f"**Current Lean Body Mass**: {current_lean_mass:.1f} kg ({current_lean_mass / 0.453592:.1f} lb)")
    st.write(f"**Target Lean Body Mass**: {target_lean_mass:.1f} kg ({target_lean_mass / 0.453592:.1f} lb)")
    if lean_mass_gain > 0:
        st.write(f"**Lean Mass to Gain**: {lean_mass_gain:.1f} kg ({lean_mass_gain / 0.453592:.1f} lb)")
    elif lean_mass_gain < 0:
        st.write(f"**Lean Mass to Lose**: {abs(lean_mass_gain):.1f} kg ({abs(lean_mass_gain) / 0.453592:.1f} lb)")
    else:
        st.write("You are already at your target ALMI!")

# Notes
st.write("---")
st.write("""
**Notes**:
- ALMI (Appendicular Lean Mass Index) is based on lean mass in limbs, estimated here as ~75% of total lean mass.
- Calculations use height to convert ALMI to lean mass (ALM = ALMI * height²).
- Imperial height inputs are converted to metric (1 inch = 0.0254 m).
""")