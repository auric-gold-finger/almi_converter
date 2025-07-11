import streamlit as st
import pandas as pd
import numpy as np

def calculate_almi_from_alm(alm, height_m):
    """Calculate ALMI from appendicular lean mass"""
    return alm / (height_m ** 2)

def calculate_alm_from_almi(almi, height_m):
    """Calculate appendicular lean mass from ALMI"""
    return almi * (height_m ** 2)

def calculate_ffmi_from_ffm(ffm, height_m):
    """Calculate FFMI from fat-free mass"""
    return ffm / (height_m ** 2)

def calculate_ffm_from_ffmi(ffmi, height_m):
    """Calculate fat-free mass from FFMI"""
    return ffmi * (height_m ** 2)

def calculate_ffmi_from_weight_bf(weight_kg, body_fat_pct, height_m):
    """Calculate FFMI from weight and body fat percentage"""
    fat_free_mass = weight_kg * (1 - body_fat_pct / 100)
    return fat_free_mass / (height_m ** 2)

def calculate_almi_from_dexa(total_lean_kg, height_m, alm_ratio=0.75):
    """Estimate ALMI from total lean mass (DEXA). ALM is typically ~75% of total lean mass"""
    estimated_alm = total_lean_kg * alm_ratio
    return calculate_almi_from_alm(estimated_alm, height_m)

def kg_to_lbs(kg):
    """Convert kilograms to pounds"""
    return kg * 2.20462

def get_percentile_targets(gender, metric_type):
    """Get percentile-based targets"""
    if metric_type == "ALMI":
        if gender == "Male":
            return {
                "5th percentile": 6.8,
                "25th percentile": 7.8,
                "50th percentile (median)": 8.5,
                "75th percentile": 9.4,
                "95th percentile": 10.8
            }
        else:  # Female
            return {
                "5th percentile": 5.2,
                "25th percentile": 6.0,
                "50th percentile (median)": 6.8,
                "75th percentile": 7.6,
                "95th percentile": 8.8
            }
    else:  # FFMI
        if gender == "Male":
            return {
                "5th percentile": 16.5,
                "25th percentile": 18.0,
                "50th percentile (median)": 19.5,
                "75th percentile": 21.0,
                "95th percentile": 23.5
            }
        else:  # Female
            return {
                "5th percentile": 14.5,
                "25th percentile": 15.5,
                "50th percentile (median)": 16.5,
                "75th percentile": 17.5,
                "95th percentile": 19.0
            }

def process_csv_data(df, height_col, gender_col, calc_type):
    """Process CSV data and calculate lean mass needs"""
    results = []
    
    for idx, row in df.iterrows():
        try:
            height_m = row[height_col] / 100 if row[height_col] > 3 else row[height_col]  # Handle cm vs m
            gender = row[gender_col]
            
            # Calculate current metric based on available columns
            current_metric = None
            if calc_type == "ALMI":
                if 'ALMI' in df.columns:
                    current_metric = row['ALMI']
                elif 'ALM' in df.columns:
                    current_metric = calculate_almi_from_alm(row['ALM'], height_m)
                elif all(col in df.columns for col in ['Weight', 'BodyFat']):
                    # Estimate from weight/BF (rough approximation)
                    ffm = row['Weight'] * (1 - row['BodyFat'] / 100)
                    estimated_alm = ffm * 0.75  # ALM is ~75% of FFM
                    current_metric = calculate_almi_from_alm(estimated_alm, height_m)
            else:  # FFMI
                if 'FFMI' in df.columns:
                    current_metric = row['FFMI']
                elif 'FFM' in df.columns:
                    current_metric = calculate_ffmi_from_ffm(row['FFM'], height_m)
                elif all(col in df.columns for col in ['Weight', 'BodyFat']):
                    current_metric = calculate_ffmi_from_weight_bf(row['Weight'], row['BodyFat'], height_m)
            
            if current_metric:
                percentiles = get_percentile_targets(gender, calc_type)
                
                result = {
                    'ID': idx + 1,
                    'Gender': gender,
                    'Height_m': height_m,
                    f'Current_{calc_type}': current_metric
                }
                
                # Calculate mass needed for each percentile
                for percentile, target_value in percentiles.items():
                    if calc_type == "ALMI":
                        current_mass = calculate_alm_from_almi(current_metric, height_m)
                        target_mass = calculate_alm_from_almi(target_value, height_m)
                    else:  # FFMI
                        current_mass = calculate_ffm_from_ffmi(current_metric, height_m)
                        target_mass = calculate_ffm_from_ffmi(target_value, height_m)
                    
                    mass_needed = max(0, target_mass - current_mass)
                    result[f'{percentile}_kg'] = round(mass_needed, 1)
                    result[f'{percentile}_lbs'] = round(kg_to_lbs(mass_needed), 1)
                
                results.append(result)
        except Exception as e:
            st.warning(f"Error processing row {idx + 1}: {e}")
    
    return pd.DataFrame(results)

def main():
    st.title("Enhanced Body Composition Calculator")
    st.write("Calculate lean mass gains with multiple input methods and percentile targets")
    
    # Input method selection
    input_method = st.radio("Input method:", 
                           ["Manual Entry", "CSV Upload"], 
                           horizontal=True)
    
    if input_method == "CSV Upload":
        st.subheader("CSV Upload")
        st.write("Upload a CSV with columns for height, gender, and body composition data")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("**Data preview:**")
            st.dataframe(df.head())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                height_col = st.selectbox("Height column:", df.columns)
            with col2:
                gender_col = st.selectbox("Gender column:", df.columns)
            with col3:
                calc_type = st.selectbox("Calculate:", ["ALMI", "FFMI"])
            
            st.write("**Available columns for calculation:**")
            st.write(f"Detected: {', '.join(df.columns)}")
            
            if st.button("Process CSV"):
                results_df = process_csv_data(df, height_col, gender_col, calc_type)
                
                if not results_df.empty:
                    st.subheader("Results")
                    st.dataframe(results_df)
                    
                    # Download button
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download results as CSV",
                        data=csv,
                        file_name=f'{calc_type}_analysis_results.csv',
                        mime='text/csv'
                    )
                else:
                    st.error("No valid data could be processed")
    
    else:  # Manual Entry
        # Single line setup
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            unit_system = st.radio("Units:", ["Metric", "English"])
        
        with col2:
            if unit_system == "Metric":
                height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, 
                                           value=170.0, step=0.5)
                height_m = height_cm / 100
            else:
                feet = st.number_input("Feet:", min_value=4, max_value=8, value=5, step=1)
                inches = st.number_input("Inches:", min_value=0, max_value=11, value=8, step=1)
                height_m = (feet * 12 + inches) * 0.0254
                height_cm = height_m * 100
        
        with col3:
            gender = st.selectbox("Gender:", ["Male", "Female"])
        
        with col4:
            calc_type = st.radio("Calculate:", ["ALMI", "FFMI"])
        
        # Input method for current values
        st.subheader("Current Body Composition")
        
        input_type = st.radio("How do you want to enter current data?", 
                             ["Direct Entry", "From Weight & Body Fat", "From DEXA Scan", "From Lean Mass"])
        
        current_metric = None
        
        if input_type == "Direct Entry":
            if calc_type == "ALMI":
                current_metric = st.number_input(f"Current ALMI (kg/m²):", 
                                               min_value=3.0, max_value=15.0, 
                                               value=6.5, step=0.1)
            else:
                current_metric = st.number_input(f"Current FFMI (kg/m²):", 
                                               min_value=10.0, max_value=30.0, 
                                               value=18.0, step=0.1)
        
        elif input_type == "From Weight & Body Fat":
            col1, col2 = st.columns(2)
            with col1:
                weight_kg = st.number_input("Weight (kg):", min_value=30.0, max_value=200.0, value=70.0)
            with col2:
                body_fat_pct = st.number_input("Body Fat (%):", min_value=5.0, max_value=40.0, value=15.0)
            
            if calc_type == "ALMI":
                # Estimate ALM from FFM (ALM ≈ 75% of FFM)
                ffm = weight_kg * (1 - body_fat_pct / 100)
                estimated_alm = ffm * 0.75
                current_metric = calculate_almi_from_alm(estimated_alm, height_m)
                st.info(f"Estimated ALMI: {current_metric:.2f} kg/m² (ALM ≈ 75% of FFM)")
            else:
                current_metric = calculate_ffmi_from_weight_bf(weight_kg, body_fat_pct, height_m)
                st.info(f"Calculated FFMI: {current_metric:.2f} kg/m²")
        
        elif input_type == "From DEXA Scan":
            if calc_type == "ALMI":
                alm_kg = st.number_input("Appendicular Lean Mass (kg):", min_value=5.0, max_value=50.0, value=20.0)
                current_metric = calculate_almi_from_alm(alm_kg, height_m)
                st.info(f"Calculated ALMI: {current_metric:.2f} kg/m²")
            else:
                total_lean_kg = st.number_input("Total Lean Mass (kg):", min_value=20.0, max_value=80.0, value=50.0)
                current_metric = calculate_ffmi_from_ffm(total_lean_kg, height_m)
                st.info(f"Calculated FFMI: {current_metric:.2f} kg/m²")
        
        elif input_type == "From Lean Mass":
            if calc_type == "ALMI":
                total_lean_kg = st.number_input("Total Lean Mass (kg):", min_value=20.0, max_value=80.0, value=50.0)
                current_metric = calculate_almi_from_dexa(total_lean_kg, height_m)
                st.info(f"Estimated ALMI: {current_metric:.2f} kg/m² (assuming ALM = 75% of total lean)")
            else:
                lean_mass_kg = st.number_input("Fat-Free Mass (kg):", min_value=20.0, max_value=80.0, value=50.0)
                current_metric = calculate_ffmi_from_ffm(lean_mass_kg, height_m)
                st.info(f"Calculated FFMI: {current_metric:.2f} kg/m²")
        
        # Target selection
        st.subheader("Target Selection")
        
        target_method = st.radio("Choose target:", ["Specific Value", "Percentile Goal"])
        
        if target_method == "Specific Value":
            if calc_type == "ALMI":
                target_metric = st.number_input(f"Target ALMI (kg/m²):", 
                                              min_value=3.0, max_value=15.0, 
                                              value=7.5, step=0.1)
            else:
                target_metric = st.number_input(f"Target FFMI (kg/m²):", 
                                              min_value=10.0, max_value=30.0, 
                                              value=20.0, step=0.1)
            
            # Calculate and display result
            if current_metric:
                if calc_type == "ALMI":
                    current_mass = calculate_alm_from_almi(current_metric, height_m)
                    target_mass = calculate_alm_from_almi(target_metric, height_m)
                else:
                    current_mass = calculate_ffm_from_ffmi(current_metric, height_m)
                    target_mass = calculate_ffm_from_ffmi(target_metric, height_m)
                
                mass_needed = target_mass - current_mass
                
                if mass_needed > 0:
                    st.success(f"**To reach {target_metric:.1f} kg/m² {calc_type}: Gain {mass_needed:.1f} kg ({kg_to_lbs(mass_needed):.1f} lbs) lean mass**")
                else:
                    st.success("**Target already reached!**")
        
        else:  # Percentile Goal
            percentiles = get_percentile_targets(gender, calc_type)
            
            st.write("**Percentile targets:**")
            
            if current_metric:
                results_data = []
                
                for percentile, target_value in percentiles.items():
                    if calc_type == "ALMI":
                        current_mass = calculate_alm_from_almi(current_metric, height_m)
                        target_mass = calculate_alm_from_almi(target_value, height_m)
                    else:
                        current_mass = calculate_ffm_from_ffmi(current_metric, height_m)
                        target_mass = calculate_ffm_from_ffmi(target_value, height_m)
                    
                    mass_needed = max(0, target_mass - current_mass)
                    
                    status = "✅ Achieved" if mass_needed == 0 else f"Need +{mass_needed:.1f} kg ({kg_to_lbs(mass_needed):.1f} lbs)"
                    
                    results_data.append({
                        "Percentile": percentile,
                        f"Target {calc_type}": f"{target_value:.1f} kg/m²",
                        "Lean Mass Needed": status
                    })
                
                results_df = pd.DataFrame(results_data)
                st.dataframe(results_df, use_container_width=True)
        
        # Reference ranges
        if calc_type == "ALMI":
            if gender == "Male":
                st.caption("Male reference: Normal ≥ 7.0 kg/m², Low < 7.0 kg/m²")
            else:
                st.caption("Female reference: Normal ≥ 5.5 kg/m², Low < 5.5 kg/m²")
        else:
            if gender == "Male":
                st.caption("Male reference: Average 16.7-19.8 kg/m², Athletic >20 kg/m², Elite 22-25 kg/m²")
            else:
                st.caption("Female reference: Average 14.6-16.8 kg/m², Athletic >17 kg/m²")

if __name__ == "__main__":
    main()