import streamlit as st
import pandas as pd

def calculate_alm_from_almi(almi, height_m):
    """Calculate appendicular lean mass from ALMI"""
    return almi * (height_m ** 2)

def calculate_ffm_from_ffmi(ffmi, height_m):
    """Calculate fat-free mass from FFMI"""
    return ffmi * (height_m ** 2)

def calculate_ffmi_from_weight_bf(weight_kg, body_fat_pct, height_m):
    """Calculate FFMI from weight and body fat percentage"""
    fat_free_mass = weight_kg * (1 - body_fat_pct / 100)
    return fat_free_mass / (height_m ** 2)

def main():
    st.title("Body Composition Calculator")
    st.write("Calculate lean mass gains needed to reach target ALMI or FFMI values")
    
    # Metric selection
    st.subheader("Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Unit system
        unit_system = st.radio("Unit system:", ["Metric", "English"])
        
        # Height input
        if unit_system == "Metric":
            height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, 
                                       value=170.0, step=0.5)
            height_m = height_cm / 100
        else:
            feet = st.number_input("Feet:", min_value=4, max_value=8, value=5, step=1)
            inches = st.number_input("Inches:", min_value=0, max_value=11, value=8, step=1)
            height_m = (feet * 12 + inches) * 0.0254
            height_cm = height_m * 100
        
        st.write(f"Height: {height_cm:.1f} cm ({height_m:.2f} m)")
    
    with col2:
        # Gender and calculation type
        gender = st.selectbox("Gender:", ["Male", "Female"])
        calc_type = st.radio("Calculate:", ["ALMI (Appendicular Lean Mass Index)", "FFMI (Fat-Free Mass Index)"])
    
    # Input section based on calculation type
    st.subheader("Current Metrics")
    
    if calc_type.startswith("ALMI"):
        col1, col2 = st.columns(2)
        
        with col1:
            current_almi = st.number_input("Current ALMI (kg/m²):", 
                                          min_value=3.0, max_value=15.0, 
                                          value=6.5, step=0.1)
        
        with col2:
            target_almi = st.number_input("Target ALMI (kg/m²):", 
                                         min_value=3.0, max_value=15.0, 
                                         value=7.5, step=0.1)
        
        # Reference ranges for ALMI
        if gender == "Male":
            ref_text = "Male reference: Normal ≥ 7.0 kg/m², Low < 7.0 kg/m²"
        else:
            ref_text = "Female reference: Normal ≥ 5.5 kg/m², Low < 5.5 kg/m²"
        
        st.write(ref_text)
        
        # Calculate lean mass values
        current_alm = calculate_alm_from_almi(current_almi, height_m)
        target_alm = calculate_alm_from_almi(target_almi, height_m)
        mass_needed = target_alm - current_alm
        
        metric_name = "ALMI"
        current_metric = current_almi
        target_metric = target_almi
        current_mass = current_alm
        target_mass = target_alm
        mass_unit = "ALM"
        
    else:  # FFMI
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_ffmi = st.number_input("Current FFMI (kg/m²):", 
                                          min_value=10.0, max_value=30.0, 
                                          value=18.0, step=0.1)
        
        with col2:
            target_ffmi = st.number_input("Target FFMI (kg/m²):", 
                                         min_value=10.0, max_value=30.0, 
                                         value=20.0, step=0.1)
        
        with col3:
            body_fat_pct = st.number_input("Current body fat (%):", 
                                          min_value=5.0, max_value=40.0, 
                                          value=15.0, step=0.5)
        
        # Reference ranges for FFMI
        if gender == "Male":
            ref_text = "Male reference: Average 16.7-19.8 kg/m², Athletic >20 kg/m², Elite 22-25 kg/m²"
        else:
            ref_text = "Female reference: Average 14.6-16.8 kg/m², Athletic >17 kg/m²"
        
        st.write(ref_text)
        
        # Calculate fat-free mass values
        current_ffm = calculate_ffm_from_ffmi(current_ffmi, height_m)
        target_ffm = calculate_ffm_from_ffmi(target_ffmi, height_m)
        mass_needed = target_ffm - current_ffm
        
        metric_name = "FFMI"
        current_metric = current_ffmi
        target_metric = target_ffmi
        current_mass = current_ffm
        target_mass = target_ffm
        mass_unit = "FFM"
    
    # Results
    st.subheader("Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Current:**")
        st.write(f"{metric_name}: {current_metric:.2f} kg/m²")
        st.write(f"{mass_unit}: {current_mass:.1f} kg")
    
    with col2:
        st.write("**Target:**")
        st.write(f"{metric_name}: {target_metric:.2f} kg/m²")
        st.write(f"{mass_unit}: {target_mass:.1f} kg")
    
    with col3:
        st.write("**To Gain:**")
        if mass_needed > 0:
            st.write(f"Lean Mass: **{mass_needed:.1f} kg**")
            st.write(f"{metric_name} Increase: {target_metric - current_metric:.2f} kg/m²")
        else:
            st.write("Target already reached!")
    
    # Timeline estimates (only if mass needs to be gained)
    if mass_needed > 0:
        st.subheader("Timeline Estimates")
        
        # Gender-specific gain rates (kg per month)
        if gender == "Male":
            rates = {
                "Beginner (Year 1)": 0.68,  # 1.5 lbs/month average
                "Intermediate (Year 2-3)": 0.34,  # 0.75 lbs/month
                "Advanced (Year 4+)": 0.11  # 0.25 lbs/month
            }
        else:  # Female
            rates = {
                "Beginner (Year 1)": 0.34,  # 0.75 lbs/month average
                "Intermediate (Year 2-3)": 0.17,  # 0.375 lbs/month
                "Advanced (Year 4+)": 0.06  # 0.125 lbs/month
            }
        
        st.write(f"**Realistic lean mass gain rates for {gender.lower()}s:**")
        
        timeline_data = []
        for level, monthly_gain in rates.items():
            months = mass_needed / monthly_gain
            years = months / 12
            timeline_data.append({
                "Experience Level": level,
                "Monthly Rate (kg)": f"{monthly_gain:.2f}",
                "Timeline": f"{months:.1f} months ({years:.1f} years)"
            })
        
        df = pd.DataFrame(timeline_data)
        st.dataframe(df, use_container_width=True)
    
    # Goal nomogram
    st.subheader("Goal Setting Nomogram")
    
    if calc_type.startswith("ALMI"):
        if gender == "Male":
            goals = {
                "Minimum Health": 7.0,
                "Good": 8.0,
                "Very Good": 9.0,
                "Excellent": 10.0
            }
        else:
            goals = {
                "Minimum Health": 5.5,
                "Good": 6.5,
                "Very Good": 7.5,
                "Excellent": 8.5
            }
        
        st.write("**ALMI Goal Targets:**")
        for goal, value in goals.items():
            mass_for_goal = calculate_alm_from_almi(value, height_m)
            gain_needed = max(0, mass_for_goal - current_mass)
            
            if gain_needed > 0:
                st.write(f"- {goal}: {value:.1f} kg/m² (need +{gain_needed:.1f} kg)")
            else:
                st.write(f"- {goal}: {value:.1f} kg/m² ✓")
    
    else:  # FFMI
        if gender == "Male":
            goals = {
                "Average": 18.0,
                "Above Average": 20.0,
                "Athletic": 22.0,
                "Elite Natural": 24.5
            }
        else:
            goals = {
                "Average": 16.0,
                "Above Average": 17.0,
                "Athletic": 18.5,
                "Elite Natural": 20.0
            }
        
        st.write("**FFMI Goal Targets:**")
        for goal, value in goals.items():
            mass_for_goal = calculate_ffm_from_ffmi(value, height_m)
            gain_needed = max(0, mass_for_goal - current_mass)
            
            if gain_needed > 0:
                st.write(f"- {goal}: {value:.1f} kg/m² (need +{gain_needed:.1f} kg)")
            else:
                st.write(f"- {goal}: {value:.1f} kg/m² ✓")
    
    # Notes
    st.subheader("Important Notes")
    st.write("""
    - These estimates assume consistent training, proper nutrition, and adequate recovery
    - Individual results vary based on genetics, age, training history, and lifestyle factors
    - Beginner rates apply to first year of serious training
    - ALMI focuses on appendicular (arms/legs) lean mass, while FFMI includes total body fat-free mass
    - Regular DEXA scans provide the most accurate progress tracking
    """)

if __name__ == "__main__":
    main()