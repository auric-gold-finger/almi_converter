import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import base64

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

def calculate_alm_from_almi(almi, height_m):
    """Calculate appendicular lean mass from ALMI"""
    return almi * (height_m ** 2)

def calculate_almi_from_alm(alm_kg, height_m):
    """Calculate ALMI from appendicular lean mass"""
    return alm_kg / (height_m ** 2)

def get_percentile_targets(gender):
    """Get percentile-based targets for ALMI"""
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

def get_annual_alm_gain_range(gender, experience_level):
    """Get annual ALM gain range in pounds based on gender and experience"""
    gain_data = {
        "Male": {
            "Beginner (< 1 year)": (4, 9),
            "Intermediate (1-2 years)": (2, 4),
            "Experienced (2+ years)": (1, 2.5)
        },
        "Female": {
            "Beginner (< 1 year)": (2, 5),
            "Intermediate (1-2 years)": (1, 3),
            "Experienced (2+ years)": (0.5, 2)
        }
    }
    return gain_data.get(gender, {}).get(experience_level, (0, 0))

def estimate_timeline_range(mass_needed_lbs, gender, experience_level):
    """Estimate timeline range in months based on annual gain rates"""
    min_annual, max_annual = get_annual_alm_gain_range(gender, experience_level)
    
    if mass_needed_lbs <= 0:
        return 0, 0, "Achieved"
    
    if max_annual <= 0:
        return 0, 0, "No gains expected"
    
    # Calculate timeline in years, then convert to months
    # Minimum time uses maximum gain rate (best case scenario)
    min_years = mass_needed_lbs / max_annual  
    # Maximum time uses minimum gain rate (conservative scenario)
    max_years = mass_needed_lbs / min_annual if min_annual > 0 else float('inf')
    
    min_months = min_years * 12
    max_months = max_years * 12 if max_years != float('inf') else 999
    
    # Cap at reasonable maximum
    max_months = min(max_months, 120)  # 10 years max
    
    return min_months, max_months, f"{min_months:.1f} - {max_months:.1f}"

def create_asymmetry_chart(limb_data, unit_system):
    """Create visualization for limb asymmetries"""
    if not any(limb_data.values()):
        return None
    
    # Filter out None/zero values
    valid_limbs = {k: v for k, v in limb_data.items() if v and v > 0}
    
    if len(valid_limbs) < 2:
        return None
    
    limb_names = list(valid_limbs.keys())
    limb_values = list(valid_limbs.values())
    
    # Calculate asymmetries (difference from mean)
    mean_value = np.mean(limb_values)
    asymmetries = [(v - mean_value) / mean_value * 100 for v in limb_values]
    
    # Create bar chart
    fig = go.Figure()
    
    # Color bars based on asymmetry magnitude
    colors = ['#FF6B6B' if abs(asym) > 10 else '#FFA500' if abs(asym) > 5 else '#4CAF50' 
              for asym in asymmetries]
    
    unit_label = "kg" if unit_system == "Metric" else "lbs"
    
    fig.add_trace(go.Bar(
        x=limb_names,
        y=limb_values,
        name='Lean Mass',
        marker=dict(
            color=colors,
            opacity=0.85,
            line=dict(width=1, color='rgba(0,0,0,0.1)')
        ),
        text=[f'{val:.1f} {unit_label}<br>({asym:+.1f}%)' for val, asym in zip(limb_values, asymmetries)],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.1f} ' + unit_label + '<br>Asymmetry: %{customdata:+.1f}%<extra></extra>',
        customdata=asymmetries
    ))
    
    # Add mean line
    fig.add_hline(
        y=mean_value,
        line_dash="dash",
        line_color="#1E90FF",
        line_width=2,
        annotation_text=f"Mean: {mean_value:.1f} {unit_label}",
        annotation_position="top right",
        annotation_font=dict(color="#1E90FF", size=12)
    )
    
    fig.update_layout(
        title=dict(
            text='Limb Lean Mass Asymmetry Analysis',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#2C3E50', family='Roboto')
        ),
        xaxis_title="Limb",
        yaxis_title=f"Lean Mass ({unit_label})",
        height=500,
        font=dict(family="Roboto", color="#2C3E50"),
        plot_bgcolor='rgba(245, 245, 245, 1)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
        showlegend=False,
        bargap=0.3,
        template='plotly_white',
        margin=dict(l=60, r=60, t=80, b=60),
        xaxis=dict(
            tickfont=dict(size=12),
            title_font=dict(size=14),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            tickfont=dict(size=12),
            title_font=dict(size=14),
            gridcolor='rgba(0,0,0,0.05)'
        )
    )
    
    return fig, asymmetries, mean_value

def create_percentile_visualization(current_metric, target_metric, gender):
    """Create percentile goal visualization using Plotly"""
    percentiles = get_percentile_targets(gender)
    
    percentile_names = list(percentiles.keys())
    percentile_values = list(percentiles.values())
    
    # Create bar chart
    fig = go.Figure()
    
    # Add percentile bars with gender-appropriate colors
    if gender == "Female":
        colors = px.colors.sequential.Purples
    else:
        colors = px.colors.sequential.Tealgrn
    
    fig.add_trace(go.Bar(
        x=percentile_names,
        y=percentile_values,
        name='Percentiles',
        marker=dict(
            color=colors,
            opacity=0.85,
            line=dict(width=1, color='rgba(0,0,0,0.1)')
        ),
        text=[f'{val:.1f}' for val in percentile_values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.1f} kg/m²<extra></extra>'
    ))
    
    # Add current value line
    fig.add_hline(
        y=current_metric,
        line_dash="dash",
        line_color="#FF6B6B",
        line_width=2.5,
        annotation_text=f"Current: {current_metric:.1f}",
        annotation_position="top right",
        annotation_font=dict(color="#FF6B6B", size=14)
    )
    
    # Add target value line
    fig.add_hline(
        y=target_metric,
        line_dash="dash",
        line_color="#4CAF50",
        line_width=2.5,
        annotation_text=f"Target: {target_metric:.1f}",
        annotation_position="bottom right",
        annotation_font=dict(color="#4CAF50", size=14)
    )
    
    # Update layout for a sleek, modern design
    fig.update_layout(
        title=dict(
            text=f'ALMI Percentile Goals for {gender}s',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#2C3E50', family='Roboto')
        ),
        xaxis_title="Percentile",
        yaxis_title="ALMI (kg/m²)",
        height=600,
        font=dict(family="Roboto", color="#2C3E50"),
        plot_bgcolor='rgba(245, 245, 245, 1)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
        showlegend=False,
        bargap=0.15,
        template='plotly_white',
        margin=dict(l=60, r=60, t=80, b=60),
        xaxis=dict(
            tickfont=dict(size=12),
            title_font=dict(size=16),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            tickfont=dict(size=12),
            title_font=dict(size=16),
            gridcolor='rgba(0,0,0,0.05)'
        )
    )
    
    return fig

def create_progress_timeline_chart(mass_needed_lbs, gender, experience_level):
    """Create timeline visualization for lean mass gain progress with ranges"""
    min_months, max_months, timeline_str = estimate_timeline_range(mass_needed_lbs, gender, experience_level)
    
    fig = go.Figure()
    
    if mass_needed_lbs <= 0:
        # Already achieved
        fig.add_trace(go.Bar(
            y=[experience_level],
            x=[0],
            orientation='h',
            name='Achieved',
            marker=dict(
                color='#4CAF50',
                line=dict(color='#4CAF50', width=2),
                opacity=0.9
            ),
            text=['Achieved'],
            textposition='inside',
            insidetextfont=dict(color='#FFFFFF', size=14),
            hovertemplate='<b>%{y}</b><br>Status: Achieved<extra></extra>'
        ))
    else:
        # Choose colors based on gender
        primary_color = '#9C27B0' if gender == "Female" else '#1E90FF'
        secondary_color = '#E1BEE7' if gender == "Female" else '#87CEEB'
        
        # Show range as stacked bars
        fig.add_trace(go.Bar(
            y=[experience_level],
            x=[min_months],
            orientation='h',
            name='Minimum Timeline',
            marker=dict(
                color=primary_color,
                opacity=0.9
            ),
            text=[f'{min_months:.1f}'],
            textposition='inside',
            insidetextfont=dict(color='#FFFFFF', size=12),
            hovertemplate='<b>%{y}</b><br>Minimum: %{x:.1f} months<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=[experience_level],
            x=[max_months - min_months],
            orientation='h',
            name='Maximum Timeline',
            marker=dict(
                color=secondary_color,
                opacity=0.7
            ),
            text=[f'{max_months:.1f}'],
            textposition='inside',
            insidetextfont=dict(color='#2C3E50', size=12),
            hovertemplate='<b>%{y}</b><br>Maximum: %{x:.1f} additional months<extra></extra>'
        ))
    
    # Update layout for modern, dimensional look
    fig.update_layout(
        title=dict(
            text='Estimated Timeline to Goal',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#2C3E50', family='Roboto')
        ),
        yaxis_title="Experience Level",
        xaxis_title="Months to Goal",
        height=350,
        font=dict(family="Roboto", color="#2C3E50"),
        plot_bgcolor='rgba(245, 245, 245, 1)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
        showlegend=True,
        bargap=0.2,
        barmode='stack',
        template='plotly_white',
        margin=dict(l=60, r=60, t=60, b=60),
        xaxis=dict(
            tickfont=dict(size=12),
            title_font=dict(size=16),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            tickfont=dict(size=12),
            title_font=dict(size=16),
        )
    )
    
    return fig, (min_months, max_months)

def find_next_percentile(current_almi, percentiles):
    """Find the next reasonable percentile cut point"""
    if current_almi <= 0:
        return min(percentiles.values())  # Return lowest percentile for invalid ALMI
    sorted_percentiles = sorted(percentiles.items(), key=lambda x: x[1])
    for perc, value in sorted_percentiles:
        if current_almi < value:
            return value
    return max(percentiles.values())  # If above all, suggest the highest

def style_dataframe(df):
    """Apply styling to DataFrame for display"""
    return df.style.set_properties(**{
        'background-color': '#FFFFFF',
        'color': '#2C3E50',
        'border-color': '#E0E0E0',
        'font-family': 'Roboto, sans-serif',
        'font-size': '14px',
        'text-align': 'left',
        'padding': '12px'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#F8F9FA'),
            ('color', '#1E90FF'),
            ('font-weight', 'bold'),
            ('padding', '12px'),
            ('text-align', 'left')
        ]},
        {'selector': 'tr:nth-child(even)', 'props': [
            ('background-color', '#F9FAFB')
        ]},
        {'selector': 'tr:hover', 'props': [
            ('background-color', '#F1F5F9')
        ]},
        {'selector': 'table', 'props': [
            ('border-collapse', 'collapse'),
            ('box-shadow', '0 4px 8px rgba(0,0,0,0.05)'),
            ('margin', '20px 0')
        ]}
    ])

def main():
    st.set_page_config(layout="wide", page_title="DEXA ALMI Goal Calculator")
    
    st.sidebar.title("Input Parameters")
    unit_system = st.sidebar.radio("Units:", ["English", "Metric"], index=0, key="unit_system")
    gender = st.sidebar.selectbox("Gender:", ["Male", "Female"], key="gender")
    
    # Input validation for height
    try:
        if unit_system == "Metric":
            height_cm = st.sidebar.number_input("Height (cm):", min_value=100.0, max_value=250.0, value=165.0 if gender == "Female" else 175.0, step=0.5, key="height_cm")
            if height_cm <= 0:
                st.sidebar.error("Height must be positive.")
                return
            height_m = height_cm / 100
        else:
            height_in = st.sidebar.number_input("Height (in):", min_value=48.0, max_value=96.0, value=65.0 if gender == "Female" else 70.0, step=0.5, key="height_in")
            if height_in <= 0:
                st.sidebar.error("Height must be positive.")
                return
            height_m = inches_to_m(height_in)
    except ValueError:
        st.sidebar.error("Invalid height input.")
        return
    
    # Input validation for ALMI
    try:
        default_almi = 6.5 if gender == "Female" else 8.0
        current_almi = st.sidebar.number_input("Current ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=default_almi, step=0.1, key="current_almi")
        if current_almi <= 0:
            st.sidebar.error("Current ALMI must be positive.")
            return
    except ValueError:
        st.sidebar.error("Invalid ALMI input.")
        return
    
    experience_level = st.sidebar.selectbox("Training Experience:", 
                                          ["Beginner (< 1 year)", "Intermediate (1-2 years)", "Experienced (2+ years)"], 
                                          key="experience_level")
    
    percentiles = get_percentile_targets(gender)
    suggested_almi = find_next_percentile(current_almi, percentiles)
    
    # Input validation for target ALMI
    try:
        target_almi = st.sidebar.number_input("Target ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=suggested_almi, step=0.1, key="target_almi")
        if target_almi <= 0:
            st.sidebar.error("Target ALMI must be positive.")
            return
    except ValueError:
        st.sidebar.error("Invalid target ALMI input.")
        return
    
    # Display gain rate information
    min_gain, max_gain = get_annual_alm_gain_range(gender, experience_level)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Expected Annual ALM Gain:**")
    st.sidebar.markdown(f"{min_gain} - {max_gain} lbs/year")
    
    # Optional limb lean mass inputs
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Optional: Individual Limb Analysis**")
    enable_limb_analysis = st.sidebar.checkbox("Enable limb asymmetry analysis", key="enable_limb")
    
    limb_data = {}
    if enable_limb_analysis:
        unit_label = "kg" if unit_system == "Metric" else "lbs"
        
        st.sidebar.markdown(f"*Enter lean mass for each limb ({unit_label}):*")
        limb_data = {
            "Right Arm": st.sidebar.number_input(f"Right Arm ({unit_label}):", min_value=0.0, value=0.0, step=0.1, key="right_arm"),
            "Left Arm": st.sidebar.number_input(f"Left Arm ({unit_label}):", min_value=0.0, value=0.0, step=0.1, key="left_arm"),
            "Right Leg": st.sidebar.number_input(f"Right Leg ({unit_label}):", min_value=0.0, value=0.0, step=0.1, key="right_leg"),
            "Left Leg": st.sidebar.number_input(f"Left Leg ({unit_label}):", min_value=0.0, value=0.0, step=0.1, key="left_leg")
        }
    
    # Main content
    st.title("DEXA ALMI Goal Calculator")
    with st.container():
        st.markdown("Analyze your ALMI from DEXA scans, set goals, and get realistic timelines based on research-backed gain rates. Now with limb asymmetry analysis! *Disclaimer: Consult a healthcare provider for personalized advice.*")
    
    try:
        current_alm_kg = calculate_alm_from_almi(current_almi, height_m)
        results_data = []
        
        short_term_target = percentiles["75th percentile"]
        long_term_target = percentiles["95th percentile"]
        fig_timeline_short = None
        fig_timeline_long = None
        
        for perc, percentile_almi in percentiles.items():
            percentile_alm_kg = calculate_alm_from_almi(percentile_almi, height_m)
            mass_needed_kg = max(0, percentile_alm_kg - current_alm_kg)
            mass_needed_lbs = kg_to_lbs(mass_needed_kg)
            
            fig_timeline, (min_months, max_months) = create_progress_timeline_chart(mass_needed_lbs, gender, experience_level)
            
            if mass_needed_lbs <= 0:
                mass_str = "Achieved"
                months_str = "Achieved"
            else:
                mass_str = f"{mass_needed_lbs:.1f}"
                if max_months >= 120:
                    months_str = f"{min_months:.1f} - 120+"
                else:
                    months_str = f"{min_months:.1f} - {max_months:.1f}"
            
            if perc == "75th percentile":
                fig_timeline_short = fig_timeline
            elif perc == "95th percentile":
                fig_timeline_long = fig_timeline
            
            results_data.append({
                "Percentile": perc,
                "Target ALMI": f"{percentile_almi:.1f} kg/m²",
                "ALM Needed (lbs)": mass_str,
                "Timeline (months)": months_str
            })
        
        results_df = pd.DataFrame(results_data)
        
        # Layout: Main results in columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Percentile Targets")
            st.dataframe(style_dataframe(results_df), use_container_width=True)
        
        with col2:
            # Current stats summary
            st.subheader("Current Stats")
            current_alm_lbs = kg_to_lbs(current_alm_kg)
            st.metric("Current ALMI", f"{current_almi:.1f} kg/m²")
            st.metric("Current ALM", f"{current_alm_lbs:.1f} lbs")
            
            # Find current percentile
            current_percentile = "Below 5th"
            for perc, value in sorted(percentiles.items(), key=lambda x: x[1]):
                if current_almi >= value:
                    current_percentile = perc
            st.metric("Current Percentile", current_percentile)
        
        # Custom target calculation
        target_alm_kg = calculate_alm_from_almi(target_almi, height_m)
        mass_needed_kg = max(0, target_alm_kg - current_alm_kg)
        mass_needed_lbs = kg_to_lbs(mass_needed_kg)
        fig_custom, (min_months_custom, max_months_custom) = create_progress_timeline_chart(mass_needed_lbs, gender, experience_level)
        
        with st.container():
            st.subheader("Custom Target")
            if mass_needed_lbs <= 0:
                st.success("Target Achieved!")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Target ALM Needed", f"{mass_needed_lbs:.1f} lbs")
                with col2:
                    if max_months_custom >= 120:
                        timeline_display = f"{min_months_custom:.1f} - 120+ months"
                    else:
                        timeline_display = f"{min_months_custom:.1f} - {max_months_custom:.1f} months"
                    st.metric("Estimated Timeline", timeline_display)
                st.plotly_chart(fig_custom, use_container_width=True)
        
        # Limb asymmetry analysis
        if enable_limb_analysis and any(limb_data.values()):
            st.subheader("Limb Asymmetry Analysis")
            
            asymmetry_result = create_asymmetry_chart(limb_data, unit_system)
            if asymmetry_result:
                fig_asymmetry, asymmetries, mean_value = asymmetry_result
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.plotly_chart(fig_asymmetry, use_container_width=True)
                
                with col2:
                    st.markdown("**Asymmetry Guidelines:**")
                    st.markdown("🟢 **<5%**: Normal variation")
                    st.markdown("🟡 **5-10%**: Moderate asymmetry")  
                    st.markdown("🔴 **>10%**: Significant asymmetry")
                    
                    max_asymmetry = max(abs(a) for a in asymmetries)
                    if max_asymmetry > 10:
                        st.warning("⚠️ Significant asymmetry detected. Consider targeted training.")
                    elif max_asymmetry > 5:
                        st.info("ℹ️ Moderate asymmetry. Monitor and consider corrective exercises.")
                    else:
                        st.success("✅ Normal limb symmetry.")
                
                # Calculate total from limbs if all 4 are provided
                valid_limbs = [v for v in limb_data.values() if v > 0]
                if len(valid_limbs) == 4:
                    total_limb_mass = sum(valid_limbs)
                    unit_label = "kg" if unit_system == "Metric" else "lbs"
                    
                    # Convert to kg for ALMI calculation if needed
                    if unit_system == "English":
                        total_limb_mass_kg = lbs_to_kg(total_limb_mass)
                    else:
                        total_limb_mass_kg = total_limb_mass
                    
                    calculated_almi = calculate_almi_from_alm(total_limb_mass_kg, height_m)
                    
                    st.info(f"**Calculated from limbs:** Total ALM = {total_limb_mass:.1f} {unit_label}, ALMI = {calculated_almi:.1f} kg/m²")
                    
                    if abs(calculated_almi - current_almi) > 0.5:
                        st.warning("⚠️ Significant difference between entered ALMI and calculated from limbs. Please verify your inputs.")
        
        # Display percentile chart
        with st.container():
            st.subheader("ALMI Percentile Chart")
            fig_percentile = create_percentile_visualization(current_almi, target_almi, gender)
            st.plotly_chart(fig_percentile, use_container_width=True)
        
        # Display timelines for short and long term
        st.subheader("Percentile Timelines")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            with st.container():
                st.markdown("**Short-term Goal (75th percentile)**")
                if fig_timeline_short:
                    st.plotly_chart(fig_timeline_short, use_container_width=True)
        with col_t2:
            with st.container():
                st.markdown("**Long-term Goal (95th percentile)**")
                if fig_timeline_long:
                    st.plotly_chart(fig_timeline_long, use_container_width=True)
        
        with st.container():
            st.markdown("---")
            st.markdown("**Annual ALM Gain Rates by Experience Level:**")
            
            # Create a table showing the gain rates
            gain_table_data = []
            for level in ["Beginner (< 1 year)", "Intermediate (1-2 years)", "Experienced (2+ years)"]:
                male_min, male_max = get_annual_alm_gain_range("Male", level)
                female_min, female_max = get_annual_alm_gain_range("Female", level)
                gain_table_data.append({
                    "Experience Level": level,
                    "Male ALM (lbs/year)": f"{male_min} - {male_max}",
                    "Female ALM (lbs/year)": f"{female_min} - {female_max}"
                })
            
            gain_df = pd.DataFrame(gain_table_data)
            st.dataframe(style_dataframe(gain_df), use_container_width=True)
            
            st.markdown("*Rates assume progressive overload, 0.75-1g protein/lb body weight, and slight caloric surplus. Males typically gain more due to higher testosterone; progress slows with experience. ALMI may decline ~1% per decade after 30. Limb asymmetries >10% may indicate need for targeted training.*")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}. Please check your inputs and try again.")

if __name__ == "__main__":
    main()