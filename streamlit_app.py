import streamlit as st
import pandas as pd
import numpy as np

def lbs_to_kg(lbs):
    """Convert pounds to kilograms"""
    return lbs / 2.20462

def kg_to_lbs(kg):
    """Convert kilograms to pounds"""
    return kg * 2.20462

def inches_to_m(inches):
    """Convert inches to meters"""
    return inches * 0.0254

def m_to_inches(m):
    """Convert meters to inches"""
    return m / 0.0254

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

def calculate_body_recomp(current_weight, current_bf_pct, target_lean_gain, target_fat_loss, target_vat_loss=0):
    """Calculate comprehensive body recomposition changes"""
    current_fat_mass = current_weight * (current_bf_pct / 100)
    current_lean_mass = current_weight - current_fat_mass
    
    # Future composition
    new_lean_mass = current_lean_mass + target_lean_gain
    new_fat_mass = current_fat_mass - target_fat_loss - target_vat_loss
    new_weight = new_lean_mass + new_fat_mass
    new_bf_pct = (new_fat_mass / new_weight) * 100
    
    net_weight_change = new_weight - current_weight
    
    return {
        'current_lean': current_lean_mass,
        'current_fat': current_fat_mass,
        'new_lean': new_lean_mass,
        'new_fat': new_fat_mass,
        'new_weight': new_weight,
        'new_bf_pct': new_bf_pct,
        'net_weight_change': net_weight_change,
        'total_fat_loss': target_fat_loss + target_vat_loss
    }

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

def process_csv_data(df, height_col, gender_col, calc_type, unit_system):
    """Process CSV data and calculate lean mass needs"""
    results = []
    
    for idx, row in df.iterrows():
        try:
            if unit_system == "English":
                height_m = inches_to_m(row[height_col])
            else:
                height_m = row[height_col] / 100 if row[height_col] > 3 else row[height_col]
            
            gender = row[gender_col]
            
            # Calculate current metric based on available columns
            current_metric = None
            if calc_type == "ALMI":
                if 'ALMI' in df.columns:
                    current_metric = row['ALMI']
                elif 'ALM' in df.columns:
                    alm = lbs_to_kg(row['ALM']) if unit_system == "English" else row['ALM']
                    current_metric = calculate_almi_from_alm(alm, height_m)
                elif all(col in df.columns for col in ['Weight', 'BodyFat']):
                    weight = lbs_to_kg(row['Weight']) if unit_system == "English" else row['Weight']
                    ffm = weight * (1 - row['BodyFat'] / 100)
                    estimated_alm = ffm * 0.75
                    current_metric = calculate_almi_from_alm(estimated_alm, height_m)
            else:  # FFMI
                if 'FFMI' in df.columns:
                    current_metric = row['FFMI']
                elif 'FFM' in df.columns:
                    ffm = lbs_to_kg(row['FFM']) if unit_system == "English" else row['FFM']
                    current_metric = calculate_ffmi_from_ffm(ffm, height_m)
                elif all(col in df.columns for col in ['Weight', 'BodyFat']):
                    weight = lbs_to_kg(row['Weight']) if unit_system == "English" else row['Weight']
                    current_metric = calculate_ffmi_from_weight_bf(weight, row['BodyFat'], height_m)
            
            if current_metric:
                percentiles = get_percentile_targets(gender, calc_type)
                
                result = {
                    'ID': idx + 1,
                    'Gender': gender,
                    'Height': f"{row[height_col]:.1f} {'in' if unit_system == 'English' else 'cm'}",
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
                    
                    if unit_system == "English":
                        result[f'{percentile}_lbs'] = round(kg_to_lbs(mass_needed), 1)
                    else:
                        result[f'{percentile}_kg'] = round(mass_needed, 1)
                
                results.append(result)
        except Exception as e:
            st.warning(f"Error processing row {idx + 1}: {e}")
    
    return pd.DataFrame(results)

def main():
    st.title("Enhanced Body Composition & Recomposition Calculator")
    st.write("Calculate lean mass gains, fat loss, and complete body recomposition")
    
    # Input method selection
    input_method = st.radio("Input method:", 
                           ["Manual Entry", "Body Recomposition Planning", "CSV Upload"], 
                           horizontal=True)
    
    if input_method == "CSV Upload":
        st.subheader("CSV Upload")
        st.write("Upload a CSV with columns for height, gender, and body composition data")
        
        unit_system = st.radio("CSV data units:", ["Metric", "English"], horizontal=True)
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("**Data preview:**")
            st.dataframe(df.head())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                height_col = st.selectbox("Height column:", df.columns)
                st.caption("English: inches, Metric: cm")
            with col2:
                gender_col = st.selectbox("Gender column:", df.columns)
            with col3:
                calc_type = st.selectbox("Calculate:", ["ALMI", "FFMI"])
            
            st.write("**Available columns for calculation:**")
            st.write(f"Detected: {', '.join(df.columns)}")
            
            if st.button("Process CSV"):
                results_df = process_csv_data(df, height_col, gender_col, calc_type, unit_system)
                
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
    
    elif input_method == "Body Recomposition Planning":
        st.subheader("Complete Body Recomposition Calculator")
        
        # Unit system
        unit_system = st.radio("Units:", ["Metric", "English"], horizontal=True)
        
        # Basic inputs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if unit_system == "Metric":
                height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, 
                                           value=170.0, step=0.5)
                height_m = height_cm / 100
            else:
                height_in = st.number_input("Height (inches):", min_value=48.0, max_value=96.0, 
                                           value=68.0, step=0.5)
                height_m = inches_to_m(height_in)
        
        with col2:
            if unit_system == "Metric":
                current_weight = st.number_input("Current Weight (kg):", min_value=30.0, max_value=200.0, value=70.0)
            else:
                current_weight_lbs = st.number_input("Current Weight (lbs):", min_value=66.0, max_value=440.0, value=154.0)
                current_weight = lbs_to_kg(current_weight_lbs)
        
        with col3:
            current_bf_pct = st.number_input("Current Body Fat (%):", min_value=5.0, max_value=40.0, value=20.0)
        
        with col4:
            gender = st.selectbox("Gender:", ["Male", "Female"])
        
        # Recomposition targets
        st.write("**Recomposition Goals:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if unit_system == "Metric":
                target_lean_gain = st.number_input("Lean Mass Gain (kg):", min_value=0.0, max_value=30.0, value=5.0, step=0.5)
            else:
                target_lean_gain_lbs = st.number_input("Lean Mass Gain (lbs):", min_value=0.0, max_value=66.0, value=11.0, step=1.0)
                target_lean_gain = lbs_to_kg(target_lean_gain_lbs)
        
        with col2:
            if unit_system == "Metric":
                target_fat_loss = st.number_input("Subcutaneous Fat Loss (kg):", min_value=0.0, max_value=50.0, value=8.0, step=0.5)
            else:
                target_fat_loss_lbs = st.number_input("Subcutaneous Fat Loss (lbs):", min_value=0.0, max_value=110.0, value=17.6, step=1.0)
                target_fat_loss = lbs_to_kg(target_fat_loss_lbs)
        
        with col3:
            if unit_system == "Metric":
                target_vat_loss = st.number_input("Visceral Fat Loss (kg):", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
            else:
                target_vat_loss_lbs = st.number_input("Visceral Fat Loss (lbs):", min_value=0.0, max_value=22.0, value=2.2, step=0.2)
                target_vat_loss = lbs_to_kg(target_vat_loss_lbs)
        
        # Calculate recomposition
        recomp = calculate_body_recomp(current_weight, current_bf_pct, target_lean_gain, target_fat_loss, target_vat_loss)
        
        # Current FFMI calculation
        current_ffmi = calculate_ffmi_from_weight_bf(current_weight, current_bf_pct, height_m)
        new_ffmi = calculate_ffmi_from_ffm(recomp['new_lean'], height_m)
        
        # Results
        st.subheader("Recomposition Results")
        
        # Current vs Target comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Current:**")
            if unit_system == "English":
                st.write(f"Weight: {kg_to_lbs(current_weight):.1f} lbs")
                st.write(f"Lean Mass: {kg_to_lbs(recomp['current_lean']):.1f} lbs")
                st.write(f"Fat Mass: {kg_to_lbs(recomp['current_fat']):.1f} lbs")
            else:
                st.write(f"Weight: {current_weight:.1f} kg")
                st.write(f"Lean Mass: {recomp['current_lean']:.1f} kg")
                st.write(f"Fat Mass: {recomp['current_fat']:.1f} kg")
            st.write(f"Body Fat: {current_bf_pct:.1f}%")
            st.write(f"FFMI: {current_ffmi:.1f} kg/m²")
        
        with col2:
            st.write("**Target:**")
            if unit_system == "English":
                st.write(f"Weight: {kg_to_lbs(recomp['new_weight']):.1f} lbs")
                st.write(f"Lean Mass: {kg_to_lbs(recomp['new_lean']):.1f} lbs")
                st.write(f"Fat Mass: {kg_to_lbs(recomp['new_fat']):.1f} lbs")
            else:
                st.write(f"Weight: {recomp['new_weight']:.1f} kg")
                st.write(f"Lean Mass: {recomp['new_lean']:.1f} kg")
                st.write(f"Fat Mass: {recomp['new_fat']:.1f} kg")
            st.write(f"Body Fat: {recomp['new_bf_pct']:.1f}%")
            st.write(f"FFMI: {new_ffmi:.1f} kg/m²")
        
        with col3:
            st.write("**Net Changes:**")
            if unit_system == "English":
                st.write(f"Weight: {kg_to_lbs(recomp['net_weight_change']):+.1f} lbs")
                st.write(f"Lean Mass: {kg_to_lbs(target_lean_gain):+.1f} lbs")
                st.write(f"Total Fat: {-kg_to_lbs(recomp['total_fat_loss']):.1f} lbs")
            else:
                st.write(f"Weight: {recomp['net_weight_change']:+.1f} kg")
                st.write(f"Lean Mass: {target_lean_gain:+.1f} kg")
                st.write(f"Total Fat: {-recomp['total_fat_loss']:.1f} kg")
            st.write(f"Body Fat: {recomp['new_bf_pct'] - current_bf_pct:+.1f}%")
            st.write(f"FFMI: {new_ffmi - current_ffmi:+.1f} kg/m²")
        
        # Summary
        if recomp['net_weight_change'] > 0:
            change_direction = "gain"
        elif recomp['net_weight_change'] < 0:
            change_direction = "lose"
        else:
            change_direction = "maintain"
        
        weight_unit = "lbs" if unit_system == "English" else "kg"
        weight_change = kg_to_lbs(abs(recomp['net_weight_change'])) if unit_system == "English" else abs(recomp['net_weight_change'])
        
        st.success(f"**Summary: {change_direction.title()} {weight_change:.1f} {weight_unit} total while gaining muscle and losing fat**")
    
    else:  # Manual Entry (original functionality)
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
                height_in = st.number_input("Height (inches):", min_value=48.0, max_value=96.0, 
                                           value=68.0, step=0.5)
                height_m = inches_to_m(height_in)
        
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
                if unit_system == "Metric":
                    weight_kg = st.number_input("Weight (kg):", min_value=30.0, max_value=200.0, value=70.0)
                else:
                    weight_lbs = st.number_input("Weight (lbs):", min_value=66.0, max_value=440.0, value=154.0)
                    weight_kg = lbs_to_kg(weight_lbs)
            with col2:
                body_fat_pct = st.number_input("Body Fat (%):", min_value=5.0, max_value=40.0, value=15.0)
            
            if calc_type == "ALMI":
                ffm = weight_kg * (1 - body_fat_pct / 100)
                estimated_alm = ffm * 0.75
                current_metric = calculate_almi_from_alm(estimated_alm, height_m)
                st.info(f"Estimated ALMI: {current_metric:.2f} kg/m² (ALM ≈ 75% of FFM)")
            else:
                current_metric = calculate_ffmi_from_weight_bf(weight_kg, body_fat_pct, height_m)
                st.info(f"Calculated FFMI: {current_metric:.2f} kg/m²")
        
        elif input_type == "From DEXA Scan":
            if calc_type == "ALMI":
                if unit_system == "Metric":
                    alm_kg = st.number_input("Appendicular Lean Mass (kg):", min_value=5.0, max_value=50.0, value=20.0)
                else:
                    alm_lbs = st.number_input("Appendicular Lean Mass (lbs):", min_value=11.0, max_value=110.0, value=44.0)
                    alm_kg = lbs_to_kg(alm_lbs)
                current_metric = calculate_almi_from_alm(alm_kg, height_m)
                st.info(f"Calculated ALMI: {current_metric:.2f} kg/m²")
            else:
                if unit_system == "Metric":
                    total_lean_kg = st.number_input("Total Lean Mass (kg):", min_value=20.0, max_value=80.0, value=50.0)
                else:
                    total_lean_lbs = st.number_input("Total Lean Mass (lbs):", min_value=44.0, max_value=176.0, value=110.0)
                    total_lean_kg = lbs_to_kg(total_lean_lbs)
                current_metric = calculate_ffmi_from_ffm(total_lean_kg, height_m)
                st.info(f"Calculated FFMI: {current_metric:.2f} kg/m²")
        
        elif input_type == "From Lean Mass":
            if calc_type == "ALMI":
                if unit_system == "Metric":
                    total_lean_kg = st.number_input("Total Lean Mass (kg):", min_value=20.0, max_value=80.0, value=50.0)
                else:
                    total_lean_lbs = st.number_input("Total Lean Mass (lbs):", min_value=44.0, max_value=176.0, value=110.0)
                    total_lean_kg = lbs_to_kg(total_lean_lbs)
                current_metric = calculate_almi_from_dexa(total_lean_kg, height_m)
                st.info(f"Estimated ALMI: {current_metric:.2f} kg/m² (assuming ALM = 75% of total lean)")
            else:
                if unit_system == "Metric":
                    lean_mass_kg = st.number_input("Fat-Free Mass (kg):", min_value=20.0, max_value=80.0, value=50.0)
                else:
                    lean_mass_lbs = st.number_input("Fat-Free Mass (lbs):", min_value=44.0, max_value=176.0, value=110.0)
                    lean_mass_kg = lbs_to_kg(lean_mass_lbs)
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
                    if unit_system == "English":
                        st.success(f"**To reach {target_metric:.1f} kg/m² {calc_type}: Gain {kg_to_lbs(mass_needed):.1f} lbs lean mass**")
                    else:
                        st.success(f"**To reach {target_metric:.1f} kg/m² {calc_type}: Gain {mass_needed:.1f} kg lean mass**")
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
                    
                    if mass_needed == 0:
                        status = "✅ Achieved"
                    else:
                        if unit_system == "English":
                            status = f"Need +{kg_to_lbs(mass_needed):.1f} lbs"
                        else:
                            status = f"Need +{mass_needed:.1f} kg"
                    
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