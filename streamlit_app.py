import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import base64
from fpdf import FPDF
import json

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

def calculate_bmi(weight_kg, height_m):
    """Calculate BMI"""
    return weight_kg / (height_m ** 2)

def calculate_body_fat_percentage(weight_kg, lean_mass_kg):
    """Calculate body fat percentage from total weight and lean mass"""
    fat_mass_kg = weight_kg - lean_mass_kg
    return (fat_mass_kg / weight_kg) * 100

def calculate_ideal_body_fat_ranges(gender, age):
    """Get ideal body fat ranges based on gender and age"""
    if gender == "Male":
        if age < 30:
            return {"Essential": (2, 5), "Athletes": (6, 13), "Fitness": (14, 17), "Average": (18, 24), "Obese": (25, 100)}
        elif age < 40:
            return {"Essential": (2, 5), "Athletes": (7, 14), "Fitness": (15, 18), "Average": (19, 25), "Obese": (26, 100)}
        elif age < 50:
            return {"Essential": (2, 5), "Athletes": (8, 15), "Fitness": (16, 19), "Average": (20, 26), "Obese": (27, 100)}
        else:
            return {"Essential": (2, 5), "Athletes": (9, 16), "Fitness": (17, 20), "Average": (21, 27), "Obese": (28, 100)}
    else:  # Female
        if age < 30:
            return {"Essential": (10, 13), "Athletes": (14, 20), "Fitness": (21, 24), "Average": (25, 31), "Obese": (32, 100)}
        elif age < 40:
            return {"Essential": (10, 13), "Athletes": (15, 21), "Fitness": (22, 25), "Average": (26, 32), "Obese": (33, 100)}
        elif age < 50:
            return {"Essential": (10, 13), "Athletes": (16, 22), "Fitness": (23, 26), "Average": (27, 33), "Obese": (34, 100)}
        else:
            return {"Essential": (10, 13), "Athletes": (17, 23), "Fitness": (24, 27), "Average": (28, 34), "Obese": (35, 100)}

def get_age_adjusted_percentiles(gender, age):
    """Get age-adjusted percentile targets for ALMI"""
    base_percentiles = get_percentile_targets(gender)
    
    # Age-related decline: ~1% per decade after 30
    if age > 30:
        decline_factor = 1 - (0.01 * (age - 30) / 10)
        return {k: v * decline_factor for k, v in base_percentiles.items()}
    
    return base_percentiles

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

def get_annual_alm_gain_range(gender, experience_level, age):
    """Get annual ALM gain range in pounds based on gender, experience, and age"""
    base_gains = {
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
    
    min_gain, max_gain = base_gains.get(gender, {}).get(experience_level, (0, 0))
    
    # Age adjustment: reduce gains after 30
    if age > 30:
        age_factor = max(0.3, 1 - (age - 30) * 0.015)  # Gradual decline, minimum 30% of base
        min_gain *= age_factor
        max_gain *= age_factor
    
    return min_gain, max_gain

def calculate_protein_needs(weight_kg, goal_type, activity_level):
    """Calculate daily protein needs based on goals and activity"""
    base_protein = {
        "Muscle Building": 1.6,
        "Maintenance": 1.2,
        "Fat Loss": 1.8
    }
    
    activity_multiplier = {
        "Sedentary": 1.0,
        "Light Activity": 1.1,
        "Moderate Activity": 1.2,
        "High Activity": 1.3,
        "Very High Activity": 1.4
    }
    
    protein_per_kg = base_protein.get(goal_type, 1.2) * activity_multiplier.get(activity_level, 1.0)
    total_protein_g = weight_kg * protein_per_kg
    
    return total_protein_g, protein_per_kg

def estimate_timeline_range(mass_needed_lbs, gender, experience_level, age):
    """Estimate timeline range in months based on annual gain rates"""
    min_annual, max_annual = get_annual_alm_gain_range(gender, experience_level, age)
    
    if mass_needed_lbs <= 0:
        return 0, 0, "Achieved"
    
    if max_annual <= 0:
        return 0, 0, "No gains expected"
    
    # Calculate timeline in years, then convert to months
    min_years = mass_needed_lbs / max_annual  
    max_years = mass_needed_lbs / min_annual if min_annual > 0 else float('inf')
    
    min_months = min_years * 12
    max_months = max_years * 12 if max_years != float('inf') else 999
    
    # Cap at reasonable maximum
    max_months = min(max_months, 120)  # 10 years max
    
    return min_months, max_months, f"{min_months:.1f} - {max_months:.1f}"

def create_progress_tracking_chart(progress_data):
    """Create progress tracking visualization"""
    if not progress_data:
        return None
    
    df = pd.DataFrame(progress_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('ALMI Progress', 'Body Fat %', 'Total Weight', 'Lean Mass'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # ALMI Progress
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['ALMI'], mode='lines+markers', name='ALMI',
                  line=dict(color='#1E90FF', width=3)),
        row=1, col=1
    )
    
    # Body Fat %
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Body_Fat_Percent'], mode='lines+markers', name='Body Fat %',
                  line=dict(color='#FF6B6B', width=3)),
        row=1, col=2
    )
    
    # Total Weight
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Total_Weight'], mode='lines+markers', name='Weight',
                  line=dict(color='#4CAF50', width=3)),
        row=2, col=1
    )
    
    # Lean Mass
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Lean_Mass'], mode='lines+markers', name='Lean Mass',
                  line=dict(color='#9C27B0', width=3)),
        row=2, col=2
    )
    
    fig.update_layout(
        title='Progress Tracking Dashboard',
        height=600,
        showlegend=False,
        font=dict(family="Roboto", color="#2C3E50"),
        plot_bgcolor='rgba(245, 245, 245, 1)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
    )
    
    return fig

def create_body_fat_analysis_chart(current_bf, ideal_ranges, gender, age):
    """Create body fat analysis visualization"""
    fig = go.Figure()
    
    # Create color-coded ranges
    colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#FF5722']
    y_pos = 0
    
    for i, (category, (min_val, max_val)) in enumerate(ideal_ranges.items()):
        if max_val == 100:
            max_val = 50  # Cap for display
        
        fig.add_trace(go.Bar(
            x=[max_val - min_val],
            y=[category],
            base=min_val,
            orientation='h',
            marker_color=colors[i % len(colors)],
            opacity=0.7,
            name=category,
            text=f"{min_val}-{max_val}%",
            textposition='inside'
        ))
    
    # Add current value line
    fig.add_vline(
        x=current_bf,
        line_dash="dash",
        line_color="#000000",
        line_width=3,
        annotation_text=f"Current: {current_bf:.1f}%",
        annotation_position="top"
    )
    
    fig.update_layout(
        title=f'Body Fat Analysis for {gender} (Age {age})',
        xaxis_title="Body Fat Percentage (%)",
        yaxis_title="Category",
        height=400,
        font=dict(family="Roboto", color="#2C3E50"),
        plot_bgcolor='rgba(245, 245, 245, 1)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
        showlegend=False,
        bargap=0.2
    )
    
    return fig

def create_nutrition_chart(protein_needs, weight_kg):
    """Create nutrition recommendations chart"""
    protein_g, protein_per_kg = protein_needs
    
    # Meal distribution (assuming 4 meals)
    meals = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
    meal_distribution = [0.25, 0.30, 0.30, 0.15]  # Typical distribution
    meal_protein = [protein_g * dist for dist in meal_distribution]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=meals,
        y=meal_protein,
        marker_color=['#FF6B6B', '#4CAF50', '#2196F3', '#FF9800'],
        text=[f'{p:.0f}g' for p in meal_protein],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f'Daily Protein Distribution ({protein_g:.0f}g total)',
        xaxis_title="Meal",
        yaxis_title="Protein (g)",
        height=400,
        font=dict(family="Roboto", color="#2C3E50"),
        plot_bgcolor='rgba(245, 245, 245, 1)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
        showlegend=False
    )
    
    return fig

def generate_pdf_report(user_data, results_data, progress_data=None):
    """Generate PDF report"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    
    # Title
    pdf.cell(200, 10, txt="DEXA ALMI Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    # User Information
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Personal Information", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.cell(200, 8, txt=f"Gender: {user_data['gender']}", ln=True)
    pdf.cell(200, 8, txt=f"Age: {user_data['age']}", ln=True)
    pdf.cell(200, 8, txt=f"Height: {user_data['height']}", ln=True)
    pdf.cell(200, 8, txt=f"Weight: {user_data['weight']}", ln=True)
    pdf.cell(200, 8, txt=f"Current ALMI: {user_data['current_almi']:.1f} kg/m²", ln=True)
    pdf.cell(200, 8, txt=f"Body Fat: {user_data['body_fat']:.1f}%", ln=True)
    pdf.ln(10)
    
    # Results
    pdf.cell(200, 10, txt="Analysis Results", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    for result in results_data:
        pdf.cell(200, 8, txt=f"{result['Percentile']}: {result['Target ALMI']} | Need: {result['ALM Needed (lbs)']} lbs | Timeline: {result['Timeline (months)']} months", ln=True)
    
    pdf.ln(10)
    
    # Recommendations
    pdf.cell(200, 10, txt="Recommendations", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.cell(200, 8, txt=f"Daily Protein: {user_data['protein_needs']:.0f}g", ln=True)
    pdf.cell(200, 8, txt="Focus on progressive resistance training", ln=True)
    pdf.cell(200, 8, txt="Maintain slight caloric surplus for muscle building", ln=True)
    pdf.cell(200, 8, txt="Track progress with regular DEXA scans", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

def export_data_to_csv(results_data, progress_data=None):
    """Export results and progress data to CSV"""
    results_df = pd.DataFrame(results_data)
    
    if progress_data:
        progress_df = pd.DataFrame(progress_data)
        # Combine both datasets
        output = io.StringIO()
        results_df.to_csv(output, index=False)
        output.write('\n\nProgress Data:\n')
        progress_df.to_csv(output, index=False)
        return output.getvalue()
    else:
        return results_df.to_csv(index=False)

def save_progress_data(data):
    """Save progress data to session state"""
    if 'progress_history' not in st.session_state:
        st.session_state.progress_history = []
    
    st.session_state.progress_history.append(data)

def load_progress_data():
    """Load progress data from session state"""
    return st.session_state.get('progress_history', [])

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

def create_progress_timeline_chart(mass_needed_lbs, gender, experience_level, age):
    """Create timeline visualization for lean mass gain progress with ranges"""
    min_months, max_months, timeline_str = estimate_timeline_range(mass_needed_lbs, gender, experience_level, age)
    
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
    
    fig.update_layout(
        title=dict(
            text='Estimated Timeline to Goal (Age-Adjusted)',
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
        return min(percentiles.values())
    sorted_percentiles = sorted(percentiles.items(), key=lambda x: x[1])
    for perc, value in sorted_percentiles:
        if current_almi < value:
            return value
    return max(percentiles.values())

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
    st.set_page_config(layout="wide", page_title="Enhanced DEXA ALMI Calculator")
    
    # Initialize session state
    if 'progress_history' not in st.session_state:
        st.session_state.progress_history = []
    
    st.sidebar.title("Input Parameters")
    
    # Basic Information
    st.sidebar.subheader("Basic Information")
    unit_system = st.sidebar.radio("Units:", ["English", "Metric"], index=0, key="unit_system")
    gender = st.sidebar.selectbox("Gender:", ["Male", "Female"], key="gender")
    age = st.sidebar.number_input("Age:", min_value=18, max_value=100, value=30, key="age")
    
    # Physical Measurements
    st.sidebar.subheader("Physical Measurements")
    try:
        if unit_system == "Metric":
            height_cm = st.sidebar.number_input("Height (cm):", min_value=100.0, max_value=250.0, value=165.0 if gender == "Female" else 175.0, step=0.5, key="height_cm")
            if height_cm <= 0:
                st.sidebar.error("Height must be positive.")
                return
            height_m = height_cm / 100
            height_display = f"{height_cm:.1f} cm"
            
            weight_kg = st.sidebar.number_input("Total Weight (kg):", min_value=30.0, max_value=300.0, value=70.0 if gender == "Female" else 80.0, step=0.1, key="weight_kg")
            weight_display = f"{weight_kg:.1f} kg"
            
            total_lean_mass_kg = st.sidebar.number_input("Total Lean Mass (kg):", min_value=20.0, max_value=150.0, value=50.0 if gender == "Female" else 60.0, step=0.1, key="lean_mass_kg")
        else:
            height_in = st.sidebar.number_input("Height (in):", min_value=48.0, max_value=96.0, value=65.0 if gender == "Female" else 70.0, step=0.5, key="height_in")
            if height_in <= 0:
                st.sidebar.error("Height must be positive.")
                return
            height_m = inches_to_m(height_in)
            height_display = f"{height_in:.1f} in"
            
            weight_lbs = st.sidebar.number_input("Total Weight (lbs):", min_value=66.0, max_value=660.0, value=154.0 if gender == "Female" else 176.0, step=0.1, key="weight_lbs")
            weight_kg = lbs_to_kg(weight_lbs)
            weight_display = f"{weight_lbs:.1f} lbs"
            
            total_lean_mass_lbs = st.sidebar.number_input("Total Lean Mass (lbs):", min_value=44.0, max_value=330.0, value=110.0 if gender == "Female" else 132.0, step=0.1, key="lean_mass_lbs")
            total_lean_mass_kg = lbs_to_kg(total_lean_mass_lbs)
    except ValueError:
        st.sidebar.error("Invalid input values.")
        return
    
    # DEXA Measurements
    st.sidebar.subheader("DEXA Measurements")
    try:
        default_almi = 6.5 if gender == "Female" else 8.0
        current_almi = st.sidebar.number_input("Current ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=default_almi, step=0.1, key="current_almi")
        if current_almi <= 0:
            st.sidebar.error("Current ALMI must be positive.")
            return
    except ValueError:
        st.sidebar.error("Invalid ALMI input.")
        return
    
    # Calculate body fat percentage
    body_fat_percent = calculate_body_fat_percentage(weight_kg, total_lean_mass_kg)
    
    # Training Information
    st.sidebar.subheader("Training Information")
    experience_level = st.sidebar.selectbox("Training Experience:", 
                                          ["Beginner (< 1 year)", "Intermediate (1-2 years)", "Experienced (2+ years)"], 
                                          key="experience_level")
    
    activity_level = st.sidebar.selectbox("Activity Level:",
                                        ["Sedentary", "Light Activity", "Moderate Activity", "High Activity", "Very High Activity"],
                                        index=2, key="activity_level")
    
    goal_type = st.sidebar.selectbox("Primary Goal:",
                                   ["Muscle Building", "Maintenance", "Fat Loss"],
                                   key="goal_type")
    
    # Age-adjusted percentiles
    percentiles = get_age_adjusted_percentiles(gender, age)
    suggested_almi = find_next_percentile(current_almi, percentiles)
    
    try:
        target_almi = st.sidebar.number_input("Target ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=suggested_almi, step=0.1, key="target_almi")
        if target_almi <= 0:
            st.sidebar.error("Target ALMI must be positive.")
            return
    except ValueError:
        st.sidebar.error("Invalid target ALMI input.")
        return
    
    # Display gain rate information (age-adjusted)
    min_gain, max_gain = get_annual_alm_gain_range(gender, experience_level, age)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Expected Annual ALM Gain (Age {age}):**")
    st.sidebar.markdown(f"{min_gain:.1f} - {max_gain:.1f} lbs/year")
    
    # Calculate nutrition needs
    protein_needs = calculate_protein_needs(weight_kg, goal_type, activity_level)
    st.sidebar.markdown(f"**Daily Protein Needs:**")
    st.sidebar.markdown(f"{protein_needs[0]:.0f}g ({protein_needs[1]:.1f}g/kg)")
    
    # Progress Tracking Section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Progress Tracking")
    
    # Add current data to progress
    if st.sidebar.button("Save Current Data", key="save_progress"):
        current_data = {
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'ALMI': current_almi,
            'Body_Fat_Percent': body_fat_percent,
            'Total_Weight': weight_kg if unit_system == "Metric" else kg_to_lbs(weight_kg),
            'Lean_Mass': total_lean_mass_kg if unit_system == "Metric" else kg_to_lbs(total_lean_mass_kg),
            'Notes': f"Goal: {goal_type}, Activity: {activity_level}"
        }
        save_progress_data(current_data)
        st.sidebar.success("Data saved!")
    
    # Clear progress data
    if st.sidebar.button("Clear Progress History", key="clear_progress"):
        st.session_state.progress_history = []
        st.sidebar.success("Progress history cleared!")
    
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
    st.title("Enhanced DEXA ALMI Calculator")
    with st.container():
        st.markdown("**Comprehensive DEXA analysis with progress tracking, body fat analysis, nutrition recommendations, and age adjustments.** *Disclaimer: Consult a healthcare provider for personalized advice.*")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analysis", "📈 Progress", "🍽️ Nutrition", "📁 Export", "ℹ️ Info"])
    
    with tab1:
        try:
            current_alm_kg = calculate_alm_from_almi(current_almi, height_m)
            results_data = []
            
            # Calculate results for all percentiles
            for perc, percentile_almi in percentiles.items():
                percentile_alm_kg = calculate_alm_from_almi(percentile_almi, height_m)
                mass_needed_kg = max(0, percentile_alm_kg - current_alm_kg)
                mass_needed_lbs = kg_to_lbs(mass_needed_kg)
                
                fig_timeline, (min_months, max_months) = create_progress_timeline_chart(mass_needed_lbs, gender, experience_level, age)
                
                if mass_needed_lbs <= 0:
                    mass_str = "Achieved"
                    months_str = "Achieved"
                else:
                    mass_str = f"{mass_needed_lbs:.1f}"
                    if max_months >= 120:
                        months_str = f"{min_months:.1f} - 120+"
                    else:
                        months_str = f"{min_months:.1f} - {max_months:.1f}"
                
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
                st.subheader("Age-Adjusted Percentile Targets")
                st.dataframe(style_dataframe(results_df), use_container_width=True)
            
            with col2:
                # Current stats summary
                st.subheader("Current Stats")
                current_alm_lbs = kg_to_lbs(current_alm_kg)
                bmi = calculate_bmi(weight_kg, height_m)
                
                st.metric("Current ALMI", f"{current_almi:.1f} kg/m²")
                st.metric("Current ALM", f"{current_alm_lbs:.1f} lbs")
                st.metric("Body Fat %", f"{body_fat_percent:.1f}%")
                st.metric("BMI", f"{bmi:.1f}")
                
                # Find current percentile
                current_percentile = "Below 5th"
                for perc, value in sorted(percentiles.items(), key=lambda x: x[1]):
                    if current_almi >= value:
                        current_percentile = perc
                st.metric("Current Percentile", current_percentile)
            
            # Body Fat Analysis
            st.subheader("Body Fat Analysis")
            bf_ranges = calculate_ideal_body_fat_ranges(gender, age)
            fig_bf = create_body_fat_analysis_chart(body_fat_percent, bf_ranges, gender, age)
            st.plotly_chart(fig_bf, use_container_width=True)
            
            # Current category
            current_bf_category = "Unknown"
            for category, (min_val, max_val) in bf_ranges.items():
                if min_val <= body_fat_percent <= max_val:
                    current_bf_category = category
                    break
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Current Category:** {current_bf_category}")
            with col2:
                if current_bf_category in ["Athletes", "Fitness"]:
                    st.success("✅ Excellent body composition!")
                elif current_bf_category == "Average":
                    st.warning("⚠️ Room for improvement in body composition")
                elif current_bf_category == "Obese":
                    st.error("🔴 Consider focusing on fat loss")
            
            # Custom target calculation
            target_alm_kg = calculate_alm_from_almi(target_almi, height_m)
            mass_needed_kg = max(0, target_alm_kg - current_alm_kg)
            mass_needed_lbs = kg_to_lbs(mass_needed_kg)
            fig_custom, (min_months_custom, max_months_custom) = create_progress_timeline_chart(mass_needed_lbs, gender, experience_level, age)
            
            with st.container():
                st.subheader("Custom Target Analysis")
                if mass_needed_lbs <= 0:
                    st.success("🎉 Target Achieved!")
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Target ALM Needed", f"{mass_needed_lbs:.1f} lbs")
                    with col2:
                        if max_months_custom >= 120:
                            timeline_display = f"{min_months_custom:.1f} - 120+ months"
                        else:
                            timeline_display = f"{min_months_custom:.1f} - {max_months_custom:.1f} months"
                        st.metric("Estimated Timeline", timeline_display)
                    with col3:
                        weekly_gain = mass_needed_lbs / (min_months_custom * 4.33) if min_months_custom > 0 else 0
                        st.metric("Weekly ALM Target", f"{weekly_gain:.2f} lbs")
                    
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
        
        except Exception as e:
            st.error(f"An error occurred in analysis: {str(e)}. Please check your inputs and try again.")
    
    with tab2:
        st.subheader("Progress Tracking Dashboard")
        
        progress_data = load_progress_data()
        
        if progress_data:
            # Create progress chart
            fig_progress = create_progress_tracking_chart(progress_data)
            if fig_progress:
                st.plotly_chart(fig_progress, use_container_width=True)
            
            # Progress statistics
            if len(progress_data) > 1:
                df_progress = pd.DataFrame(progress_data)
                df_progress['Date'] = pd.to_datetime(df_progress['Date'])
                df_progress = df_progress.sort_values('Date')
                
                # Calculate changes
                almi_change = df_progress['ALMI'].iloc[-1] - df_progress['ALMI'].iloc[0]
                bf_change = df_progress['Body_Fat_Percent'].iloc[-1] - df_progress['Body_Fat_Percent'].iloc[0]
                weight_change = df_progress['Total_Weight'].iloc[-1] - df_progress['Total_Weight'].iloc[0]
                lean_change = df_progress['Lean_Mass'].iloc[-1] - df_progress['Lean_Mass'].iloc[0]
                
                days_diff = (df_progress['Date'].iloc[-1] - df_progress['Date'].iloc[0]).days
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("ALMI Change", f"{almi_change:+.2f} kg/m²", delta=f"{almi_change:+.2f}")
                with col2:
                    st.metric("Body Fat Change", f"{bf_change:+.1f}%", delta=f"{bf_change:+.1f}")
                with col3:
                    unit_label = "kg" if unit_system == "Metric" else "lbs"
                    st.metric(f"Weight Change ({unit_label})", f"{weight_change:+.1f}", delta=f"{weight_change:+.1f}")
                with col4:
                    st.metric(f"Lean Mass Change ({unit_label})", f"{lean_change:+.1f}", delta=f"{lean_change:+.1f}")
                
                st.info(f"**Tracking Period:** {days_diff} days ({days_diff/30.44:.1f} months)")
            
            # Progress data table
            st.subheader("Progress History")
            progress_df = pd.DataFrame(progress_data)
            st.dataframe(style_dataframe(progress_df), use_container_width=True)
            
        else:
            st.info("No progress data available. Use 'Save Current Data' in the sidebar to start tracking your progress!")
            
            # Sample data explanation
            st.markdown("### How to Use Progress Tracking:")
            st.markdown("1. **Save Current Data**: Click the button in the sidebar to save your current measurements")
            st.markdown("2. **Regular Updates**: Update your measurements after each DEXA scan (recommended every 3-6 months)")
            st.markdown("3. **Track Trends**: Monitor your ALMI, body fat %, weight, and lean mass changes over time")
            st.markdown("4. **Set Reminders**: Consider setting calendar reminders for regular DEXA scans")
    
    with tab3:
        st.subheader("Nutrition Recommendations")
        
        # Protein analysis
        protein_total, protein_per_kg = protein_needs
        fig_nutrition = create_nutrition_chart(protein_needs, weight_kg)
        st.plotly_chart(fig_nutrition, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Daily Protein Targets")
            st.metric("Total Daily Protein", f"{protein_total:.0f}g")
            st.metric("Protein per kg", f"{protein_per_kg:.1f}g/kg")
            st.metric("Protein per meal", f"{protein_total/4:.0f}g")
            
            # Protein sources
            st.markdown("### High-Quality Protein Sources")
            protein_sources = {
                "Chicken Breast (100g)": "31g",
                "Lean Beef (100g)": "26g", 
                "Salmon (100g)": "25g",
                "Greek Yogurt (170g)": "20g",
                "Eggs (2 large)": "12g",
                "Whey Protein (1 scoop)": "25g",
                "Tofu (100g)": "8g",
                "Lentils (100g cooked)": "9g"
            }
            
            for source, amount in protein_sources.items():
                st.markdown(f"• **{source}**: {amount}")
        
        with col2:
            st.markdown("### Additional Recommendations")
            
            # Caloric needs estimation
            if goal_type == "Muscle Building":
                calorie_adjustment = "+300-500"
                st.success("🍽️ **Caloric Surplus**: Eat 300-500 calories above maintenance")
            elif goal_type == "Fat Loss":
                calorie_adjustment = "-300-500"
                st.info("🥗 **Caloric Deficit**: Eat 300-500 calories below maintenance")
            else:
                calorie_adjustment = "Maintenance"
                st.info("⚖️ **Maintenance**: Eat at your maintenance calorie level")
            
            st.markdown(f"**Caloric Target**: {calorie_adjustment} calories")
            
            # Meal timing
            st.markdown("### Optimal Timing")
            st.markdown("• **Pre-workout**: 20-30g protein + carbs")
            st.markdown("• **Post-workout**: 25-40g protein within 2 hours")
            st.markdown("• **Before bed**: 20-30g casein protein")
            st.markdown("• **Spread intake**: Every 3-4 hours throughout the day")
            
            # Hydration
            water_needs = weight_kg * 35  # 35ml per kg
            st.markdown(f"### Hydration")
            st.markdown(f"**Daily Water Target**: {water_needs/1000:.1f} liters")
            st.markdown("• Add 500-750ml per hour of training")
            st.markdown("• Monitor urine color (pale yellow is ideal)")
        
        # Supplement recommendations
        st.markdown("---")
        st.subheader("Evidence-Based Supplement Recommendations")
        
        supplement_col1, supplement_col2 = st.columns(2)
        
        with supplement_col1:
            st.markdown("### Core Supplements")
            st.markdown("🥤 **Creatine Monohydrate**: 3-5g daily")
            st.markdown("🥛 **Whey Protein**: If needed to meet protein targets")
            st.markdown("💊 **Vitamin D3**: 1000-2000 IU daily")
            st.markdown("🐟 **Omega-3**: 1-2g EPA/DHA daily")
        
        with supplement_col2:
            st.markdown("### Performance Supplements")
            st.markdown("☕ **Caffeine**: 3-6mg/kg pre-workout")
            st.markdown("🔋 **Beta-Alanine**: 3-5g daily (for endurance)")
            st.markdown("🍒 **Tart Cherry**: For recovery (if needed)")
            st.markdown("🧬 **HMB**: 3g daily (for experienced trainees)")
        
        st.warning("⚠️ **Note**: Supplements are not magic bullets. Focus on whole foods first and consult a healthcare provider before starting any supplement regimen.")
    
    with tab4:
        st.subheader("Export Your Data")
        
        # Prepare user data for export
        user_data = {
            'gender': gender,
            'age': age,
            'height': height_display,
            'weight': weight_display,
            'current_almi': current_almi,
            'body_fat': body_fat_percent,
            'protein_needs': protein_total,
            'goal_type': goal_type,
            'activity_level': activity_level,
            'experience_level': experience_level
        }
        
        progress_data = load_progress_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 PDF Report")
            st.markdown("Generate a comprehensive PDF report with all your analysis results.")
            
            if st.button("Generate PDF Report", key="generate_pdf"):
                try:
                    pdf_bytes = generate_pdf_report(user_data, results_data, progress_data)
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"DEXA_Analysis_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF report generated successfully!")
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
        
        with col2:
            st.markdown("### 📊 CSV Data Export")
            st.markdown("Export your results and progress data to CSV format for further analysis.")
            
            if st.button("Generate CSV Export", key="generate_csv"):
                try:
                    csv_data = export_data_to_csv(results_data, progress_data)
                    
                    st.download_button(
                        label="📥 Download CSV Data",
                        data=csv_data,
                        file_name=f"DEXA_Data_Export_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    st.success("CSV data exported successfully!")
                except Exception as e:
                    st.error(f"Error generating CSV: {str(e)}")
        
        # Data summary
        st.markdown("---")
        st.subheader("Export Summary")
        
        export_summary_col1, export_summary_col2 = st.columns(2)
        
        with export_summary_col1:
            st.markdown("### PDF Report Includes:")
            st.markdown("• Personal information and measurements")
            st.markdown("• ALMI analysis and percentile targets")
            st.markdown("• Timeline estimates (age-adjusted)")
            st.markdown("• Body fat analysis")
            st.markdown("• Nutrition recommendations")
            st.markdown("• Training suggestions")
        
        with export_summary_col2:
            st.markdown("### CSV Export Includes:")
            st.markdown("• Complete percentile analysis table")
            st.markdown("• Progress tracking data (if available)")
            st.markdown("• Timestamps and measurements")
            st.markdown("• Compatible with Excel and Google Sheets")
            st.markdown("• Easy data manipulation and charting")
        
        # Progress data backup/restore
        if progress_data:
            st.markdown("---")
            st.subheader("Progress Data Backup")
            
            progress_json = json.dumps(progress_data, indent=2)
            st.download_button(
                label="📥 Backup Progress Data (JSON)",
                data=progress_json,
                file_name=f"progress_backup_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with tab5:
        st.subheader("Information & Guidelines")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown("### 📏 About ALMI")
            st.markdown("""
            **Appendicular Lean Mass Index (ALMI)** is calculated as:
            
            ALMI = ALM (kg) ÷ Height² (m²)
            
            Where ALM is the sum of lean mass in arms and legs from DEXA scan.
            
            **Percentile Ranges:**
            - **5th-25th**: Below average muscle mass
            - **25th-75th**: Average range
            - **75th-95th**: Above average
            - **95th+**: Excellent muscle mass
            """)
            
            st.markdown("### 🎯 Goal Setting")
            st.markdown("""
            **Realistic Targets:**
            - Beginners: Focus on 50th-75th percentile initially
            - Intermediate: Target 75th percentile
            - Advanced: Aim for 95th percentile
            
            **Age Considerations:**
            - Muscle mass naturally declines ~1% per decade after 30
            - Targets are automatically adjusted for your age
            - Resistance training can slow/reverse this decline
            """)
        
        with info_col2:
            st.markdown("### 💪 Training Guidelines")
            st.markdown("""
            **For Muscle Building:**
            - Progressive resistance training 3-4x/week
            - Compound movements (squats, deadlifts, presses)
            - 6-20 rep range across different exercises
            - Focus on progressive overload
            
            **Recovery:**
            - 7-9 hours sleep per night
            - 48-72 hours rest between training same muscles
            - Manage stress levels
            - Stay hydrated
            """)
            
            st.markdown("### 🧬 Body Fat Guidelines")
            st.markdown("""
            **Optimal Ranges by Category:**
            - **Athletes**: Lower body fat, higher muscle
            - **Fitness**: Balanced composition
            - **Average**: Normal health ranges
            
            **Factors Affecting Body Fat:**
            - Age (increases with age)
            - Gender (females naturally higher)
            - Genetics and metabolism
            - Training and nutrition
            """)
        
        st.markdown("---")
        st.subheader("Important Disclaimers")
        
        disclaimer_col1, disclaimer_col2 = st.columns(2)
        
        with disclaimer_col1:
            st.warning("""
            **Medical Disclaimer:**
            - This tool is for educational purposes only
            - Not a substitute for professional medical advice
            - Consult healthcare providers for personalized guidance
            - Individual results may vary significantly
            """)
        
        with disclaimer_col2:
            st.info("""
            **Data Accuracy:**
            - Based on research averages and population data
            - DEXA scan accuracy can vary between machines
            - Progress tracking requires consistent measurement conditions
            - Genetic factors significantly influence potential
            """)
        
        # Annual gain rates table
        st.markdown("---")
        st.subheader("Research-Based Annual Gain Rates")
        
        gain_table_data = []
        for level in ["Beginner (< 1 year)", "Intermediate (1-2 years)", "Experienced (2+ years)"]:
            male_min, male_max = get_annual_alm_gain_range("Male", level, 25)  # Base rates at age 25
            female_min, female_max = get_annual_alm_gain_range("Female", level, 25)
            
            # Age-adjusted rates for current user
            male_min_adj, male_max_adj = get_annual_alm_gain_range("Male", level, age)
            female_min_adj, female_max_adj = get_annual_alm_gain_range("Female", level, age)
            
            gain_table_data.append({
                "Experience Level": level,
                "Male ALM (lbs/year)": f"{male_min} - {male_max}",
                "Female ALM (lbs/year)": f"{female_min} - {female_max}",
                f"Male (Age {age})": f"{male_min_adj:.1f} - {male_max_adj:.1f}",
                f"Female (Age {age})": f"{female_min_adj:.1f} - {female_max_adj:.1f}"
            })
        
        gain_df = pd.DataFrame(gain_table_data)
        st.dataframe(style_dataframe(gain_df), use_container_width=True)
        
        st.markdown("""
        **Notes on Gain Rates:**
        - Base rates shown for optimal conditions at age 25
        - Age-adjusted rates account for natural decline after 30
        - Rates assume progressive training, adequate protein, and slight caloric surplus
        - Individual genetics can cause significant variation (±50%)
        - Rates may be lower with suboptimal training, nutrition, or recovery
        """)
        
        # Citations and references
        st.markdown("---")
        st.subheader("Scientific References")
        st.markdown("""
        **Key Research Sources:**
        - Baumgartner et al. (1998): ALMI reference values and sarcopenia cutpoints
        - Mitchell et al. (2012): Resistance training for muscle hypertrophy
        - Helms et al. (2014): Evidence-based recommendations for bodybuilding
        - Aragon & Schoenfeld (2013): Nutrient timing and muscle protein synthesis
        - Moore et al. (2009): Ingested protein dose response of muscle synthesis
        
        **Population Data:**
        - NHANES (National Health and Nutrition Examination Survey)
        - UK Biobank body composition reference data
        - International sarcopenia working group guidelines
        """)

if __name__ == "__main__":
    main()