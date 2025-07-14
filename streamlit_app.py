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

def calculate_alm_from_limbs(left_arm, right_arm, left_leg, right_leg):
    """Calculate total appendicular lean mass from individual limbs"""
    return left_arm + right_arm + left_leg + right_leg

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

def estimate_gain_rate(experience_level):
    """Estimate monthly lean mass gain rate in lbs (for ALM, approximate)"""
    if experience_level == "Beginner":
        return 1.5  # Adjusted for ALM (~75% of total lean gain)
    elif experience_level == "Intermediate":
        return 0.75
    else:  # Advanced
        return 0.375

def create_recomp_visualization(recomp_data, unit_system):
    """Create body recomposition visualization using Plotly"""
    
    # Weight unit for display
    weight_unit = "lbs" if unit_system == "English" else "kg"
    
    # Convert to display units if needed
    if unit_system == "English":
        current_weight = kg_to_lbs(recomp_data['current_lean'] + recomp_data['current_fat'])
        new_weight = kg_to_lbs(recomp_data['new_weight'])
        current_lean = kg_to_lbs(recomp_data['current_lean'])
        new_lean = kg_to_lbs(recomp_data['new_lean'])
        current_fat = kg_to_lbs(recomp_data['current_fat'])
        new_fat = kg_to_lbs(recomp_data['new_fat'])
    else:
        current_weight = recomp_data['current_lean'] + recomp_data['current_fat']
        new_weight = recomp_data['new_weight']
        current_lean = recomp_data['current_lean']
        new_lean = recomp_data['new_lean']
        current_fat = recomp_data['current_fat']
        new_fat = recomp_data['new_fat']
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Current Body Composition', 'Target Body Composition', 
                       'Current vs Target Comparison', 'Net Changes'),
        specs=[[{"type": "pie"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Colors
    colors = ['#66A3FF', '#F3817D']
    
    # 1. Current composition pie chart
    fig.add_trace(go.Pie(
        labels=['Lean Mass', 'Fat Mass'],
        values=[current_lean, current_fat],
        name="Current",
        marker_colors=colors,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.1f} ' + weight_unit + '<br>%{percent}<extra></extra>'
    ), row=1, col=1)
    
    # 2. Target composition pie chart
    fig.add_trace(go.Pie(
        labels=['Lean Mass', 'Fat Mass'],
        values=[new_lean, new_fat],
        name="Target",
        marker_colors=colors,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.1f} ' + weight_unit + '<br>%{percent}<extra></extra>'
    ), row=1, col=2)
    
    # 3. Comparison bar chart
    categories = ['Lean Mass', 'Fat Mass', 'Total Weight']
    current_values = [current_lean, current_fat, current_weight]
    new_values = [new_lean, new_fat, new_weight]
    
    fig.add_trace(go.Bar(
        x=categories,
        y=current_values,
        name='Current',
        marker_color='rgba(117, 117, 117, 0.7)',
        text=[f'{val:.1f}' for val in current_values],
        textposition='auto',
        hovertemplate='<b>Current %{x}</b><br>%{y:.1f} ' + weight_unit + '<extra></extra>'
    ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=categories,
        y=new_values,
        name='Target',
        marker_color='rgba(38, 125, 255, 0.8)',
        text=[f'{val:.1f}' for val in new_values],
        textposition='auto',
        hovertemplate='<b>Target %{x}</b><br>%{y:.1f} ' + weight_unit + '<extra></extra>'
    ), row=2, col=1)
    
    # 4. Changes bar chart
    changes = [new_lean - current_lean, new_fat - current_fat, new_weight - current_weight]
    change_colors = ['green' if x >= 0 else 'red' for x in changes]
    
    fig.add_trace(go.Bar(
        x=categories,
        y=changes,
        name='Changes',
        marker_color=change_colors,
        text=[f'{change:+.1f}' for change in changes],
        textposition='auto',
        hovertemplate='<b>%{x} Change</b><br>%{y:+.1f} ' + weight_unit + '<extra></extra>',
        showlegend=False
    ), row=2, col=2)
    
    # Add horizontal line at y=0 for changes chart
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='Body Recomposition Analysis',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#1f2937')
        ),
        height=700,
        showlegend=True,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text=f"Mass ({weight_unit})", row=2, col=1)
    fig.update_yaxes(title_text=f"Change ({weight_unit})", row=2, col=2)
    
    return fig

def create_limb_composition_chart(left_arm, right_arm, left_leg, right_leg, unit_system):
    """Create limb-specific lean mass visualization using Plotly"""
    
    weight_unit = "lbs" if unit_system == "English" else "kg"
    
    # Convert to display units if needed
    if unit_system == "English":
        limb_masses = [kg_to_lbs(left_arm), kg_to_lbs(right_arm), kg_to_lbs(left_leg), kg_to_lbs(right_leg)]
    else:
        limb_masses = [left_arm, right_arm, left_leg, right_leg]
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Limb Mass Distribution', 'Lean Mass by Limb'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Data
    labels = ['Left Arm', 'Right Arm', 'Left Leg', 'Right Leg']
    colors = px.colors.qualitative.Pastel[:4]  # Nicer colors
    
    # 1. Pie chart
    fig.add_trace(go.Pie(
        labels=labels,
        values=limb_masses,
        name="Distribution",
        marker_colors=colors,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.1f} ' + weight_unit + '<br>%{percent}<extra></extra>'
    ), row=1, col=1)
    
    # 2. Bar chart
    fig.add_trace(go.Bar(
        x=labels,
        y=limb_masses,
        name='Lean Mass',
        marker_color=colors,
        text=[f'{mass:.1f}' for mass in limb_masses],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>%{y:.1f} ' + weight_unit + '<extra></extra>',
        showlegend=False
    ), row=1, col=2)
    
    # Calculate symmetry
    arm_symmetry = abs(limb_masses[0] - limb_masses[1]) / max(limb_masses[0], limb_masses[1]) * 100 if max(limb_masses[0], limb_masses[1]) > 0 else 0
    leg_symmetry = abs(limb_masses[2] - limb_masses[3]) / max(limb_masses[2], limb_masses[3]) * 100 if max(limb_masses[2], limb_masses[3]) > 0 else 0
    
    # Add symmetry annotation
    fig.add_annotation(
        x=0.05, y=0.95,
        xref="paper", yref="paper",
        text=f"Arm Asymmetry: {arm_symmetry:.1f}%<br>Leg Asymmetry: {leg_symmetry:.1f}%",
        showarrow=False,
        align="left",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 0, 0, 0.2)",
        borderwidth=1
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='Appendicular Lean Mass Distribution',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#1f2937')
        ),
        height=500,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update y-axis
    fig.update_yaxes(title_text=f"Lean Mass ({weight_unit})", row=1, col=2)
    
    return fig

def create_percentile_visualization(current_metric, target_metric, gender, metric_type):
    """Create percentile goal visualization using Plotly"""
    percentiles = get_percentile_targets(gender, metric_type)
    
    percentile_names = list(percentiles.keys())
    percentile_values = list(percentiles.values())
    
    # Create bar chart
    fig = go.Figure()
    
    # Add percentile bars with nicer colors
    colors = px.colors.sequential.Blues[:5]
    
    fig.add_trace(go.Bar(
        x=percentile_names,
        y=percentile_values,
        name='Percentiles',
        marker_color=colors,
        text=[f'{val:.1f}' for val in percentile_values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.1f} kg/m²<extra></extra>'
    ))
    
    # Add current value line
    fig.add_hline(
        y=current_metric,
        line_dash="dash",
        line_color="red",
        line_width=3,
        annotation_text=f"Current: {current_metric:.1f}",
        annotation_position="top right",
        annotation_font=dict(color="red", size=14)
    )
    
    # Add target value line
    fig.add_hline(
        y=target_metric,
        line_dash="dash",
        line_color="green",
        line_width=3,
        annotation_text=f"Target: {target_metric:.1f}",
        annotation_position="bottom right",
        annotation_font=dict(color="green", size=14)
    )
    
    # Update layout for nicer look
    fig.update_layout(
        title=dict(
            text=f'{metric_type} Percentile Goals for {gender}s',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#1f2937')
        ),
        xaxis_title="Percentile",
        yaxis_title=f"{metric_type} (kg/m²)",
        height=500,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='white',
        showlegend=False,
        bargap=0.2
    )
    
    # Update axes
    fig.update_xaxes(tickangle=45, gridcolor='white')
    fig.update_yaxes(gridcolor='white')
    
    return fig

def create_progress_timeline_chart(mass_needed_lbs, experience_level):
    """Create timeline visualization for lean mass gain progress"""
    
    monthly_rate = estimate_gain_rate(experience_level)
    if mass_needed_lbs > 0 and monthly_rate > 0:
        timeline_months = max(1, mass_needed_lbs / monthly_rate)
    else:
        timeline_months = 0
    
    fig = go.Figure()
    
    # Horizontal bar with gloss (gradient)
    fig.add_trace(go.Bar(
        y=[experience_level],
        x=[timeline_months],
        orientation='h',
        name='Estimated Months',
        marker=dict(
            color='rgba(0, 200, 255, 0.8)',
            line=dict(color='rgba(0, 150, 255, 1)', width=2),
            colorscale='Blues'  # Gradient for gloss
        ),
        text=[f'{timeline_months:.1f} months' if timeline_months > 0 else 'Achieved'],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Est. Time: %{x:.1f} months<extra></extra>'
    ))
    
    # Update layout for modern look
    fig.update_layout(
        title=dict(
            text='Estimated Timeline to Goal',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#1f2937')
        ),
        yaxis_title="Experience Level",
        xaxis_title="Months to Goal",
        height=300,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='white',
        showlegend=False,
        bargap=0.2
    )
    
    fig.update_xaxes(gridcolor='white')
    
    return fig, timeline_months

def generate_dexa_report_html(patient_data, scan_data, unit_system):
    """Generate a DEXA-style report HTML"""
    
    # Calculate derived metrics
    height_m = patient_data['height_m']
    current_almi = calculate_almi_from_alm(scan_data['alm'], height_m)
    current_ffmi = calculate_ffmi_from_weight_bf(scan_data['weight'], scan_data['body_fat'], height_m)
    
    # Generate mock historical data for trends
    base_date = datetime.now()
    scan_dates = [(base_date - timedelta(days=365*i)).strftime("%m/%d/%Y") for i in range(2, -1, -1)]
    
    # Create trend data with some realistic variation
    trend_data = [
        {
            "metric": "Total Body Fat (%)",
            "values": [f"{scan_data['body_fat']:.1f}", f"{scan_data['body_fat']+1.2:.1f}", f"{scan_data['body_fat']+2.1:.1f}"]
        },
        {
            "metric": "Visceral Adipose Tissue (VAT) Mass (grams)",
            "values": [f"{scan_data.get('vat_mass', 450):.0f}", f"{scan_data.get('vat_mass', 450)+50:.0f}", f"{scan_data.get('vat_mass', 450)+80:.0f}"]
        },
        {
            "metric": "Appendicular Lean Mass Index (ALMI) (kg/m²)",
            "values": [f"{current_almi:.2f}", f"{current_almi-0.1:.2f}", f"{current_almi-0.3:.2f}"]
        },
        {
            "metric": "Fat-Free Mass Index (FFMI) (kg/m²)",
            "values": [f"{current_ffmi:.1f}", f"{current_ffmi-0.2:.1f}", f"{current_ffmi-0.5:.1f}"]
        }
    ]
    
    # HTML template (same as before, assuming it's the same)
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEXA Analysis Report - {patient_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Lato', sans-serif; background-color: #f7f7f5; }}
        h1, h2, h3, h4 {{ font-family: 'Cormorant Garamond', serif; color: #06121B; }}
        .metrics-table th, .metrics-table td {{ white-space: nowrap; }}
        .metrics-table th {{ text-transform: uppercase; letter-spacing: 0.05em; }}
        .chart-line {{ stroke-dasharray: 1000; stroke-dashoffset: 1000; animation: dash 2s ease-out forwards; }}
        @keyframes dash {{ to {{ stroke-dashoffset: 0; }} }}
    </style>
</head>
<body class="p-4 sm:p-6 lg:p-8 bg-brand-light">
    <div class="max-w-7xl mx-auto space-y-8 bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
        <header class="text-center border-b border-gray-200 pb-6">
            <h1 class="text-4xl font-bold text-gray-800 tracking-wide">DEXA Analysis Report</h1>
            <p class="text-xl text-brand-dark mt-2">{patient_name}</p>
            <div class="flex justify-center flex-wrap gap-x-6 gap-y-2 mt-2 text-brand-gray">
                <span>DOB: {dob}</span>
                <span>Height: {height}</span>
                <span>Exam Date: {exam_date}</span>
            </div>
        </header>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-3xl font-bold mb-6 text-center">Current Body Composition Summary</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 text-center">
                    <h3 class="text-lg font-semibold text-gray-700">Total Body Fat</h3>
                    <p class="text-3xl font-bold text-blue-600">{body_fat:.1f}%</p>
                </div>
                <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 text-center">
                    <h3 class="text-lg font-semibold text-gray-700">ALMI</h3>
                    <p class="text-3xl font-bold text-green-600">{almi:.2f} kg/m²</p>
                </div>
                <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 text-center">
                    <h3 class="text-lg font-semibold text-gray-700">FFMI</h3>
                    <p class="text-3xl font-bold text-purple-600">{ffmi:.1f} kg/m²</p>
                </div>
                <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 text-center">
                    <h3 class="text-lg font-semibold text-gray-700">ALM Total</h3>
                    <p class="text-3xl font-bold text-red-600">{alm:.1f} kg</p>
                </div>
            </div>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h3 class="text-2xl font-semibold mb-4">Limb-Specific Lean Mass Distribution</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Left Arm</h4>
                    <p class="text-xl font-bold text-blue-600">{left_arm:.1f} kg</p>
                </div>
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Right Arm</h4>
                    <p class="text-xl font-bold text-blue-600">{right_arm:.1f} kg</p>
                </div>
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Left Leg</h4>
                    <p class="text-xl font-bold text-green-600">{left_leg:.1f} kg</p>
                </div>
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Right Leg</h4>
                    <p class="text-xl font-bold text-green-600">{right_leg:.1f} kg</p>
                </div>
            </div>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h3 class="text-2xl font-semibold mb-4">Understanding Your Metrics</h3>
            <div class="space-y-4 text-gray-700 leading-relaxed">
                <p><strong>Appendicular Lean Mass Index (ALMI):</strong> This measures muscle mass in your limbs, crucial for strength and metabolic health. For optimal health, the target is to be above the 75th percentile. Your ALMI is <strong>{almi:.2f} kg/m²</strong>.</p>
                <p><strong>Fat-Free Mass Index (FFMI):</strong> This reflects your overall muscularity. The goal is to be in the upper quartile, above the 75th percentile. Your FFMI is <strong>{ffmi:.1f} kg/m²</strong>.</p>
                <p><strong>Total Body Fat %:</strong> While a key health marker, this is also influenced by aesthetic goals. Your value of <strong>{body_fat:.1f}%</strong> places you in the athlete category based on common classifications.</p>
                <p><strong>Limb Symmetry:</strong> Balance between limbs is important for injury prevention and optimal performance. Monitor asymmetries greater than 10%.</p>
            </div>
        </section>

        <footer class="text-center text-sm text-gray-500 pt-8 mt-8 border-t border-gray-200">
            <p>© 2025 Body Composition Analysis. All Rights Reserved.</p>
            <p class="text-xs mt-1">Disclaimer: This is a visualization of your body composition data and not a medical diagnosis. Consult with your healthcare provider.</p>
        </footer>
    </div>
</body>
</html>"""
    
    # Format the HTML with actual data
    formatted_html = html_template.format(
        patient_name=patient_data['name'],
        dob=patient_data['dob'],
        height=f"{patient_data['height_cm']:.1f} cm" if unit_system == "Metric" else f"{patient_data['height_in']:.1f} in",
        exam_date=datetime.now().strftime("%m/%d/%Y"),
        body_fat=scan_data['body_fat'],
        almi=current_almi,
        ffmi=current_ffmi,
        alm=scan_data['alm'],
        left_arm=scan_data['left_arm'],
        right_arm=scan_data['right_arm'],
        left_leg=scan_data['left_leg'],
        right_leg=scan_data['right_leg']
    )
    
    return formatted_html

def find_next_percentile(current_almi, percentiles):
    """Find the next reasonable percentile cut point"""
    sorted_percentiles = sorted(percentiles.items(), key=lambda x: x[1])
    for perc, value in sorted_percentiles:
        if current_almi < value:
            return value
    return max(percentiles.values())  # If above all, suggest the highest

def main():
    st.sidebar.title("Input Parameters")
    unit_system = st.sidebar.radio("Units:", ["English", "Metric"], index=0)  # Default English for lbs
    gender = st.sidebar.selectbox("Gender:", ["Male", "Female"])
    if unit_system == "Metric":
        height_cm = st.sidebar.number_input("Height (cm):", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
        height_m = height_cm / 100
    else:
        height_in = st.sidebar.number_input("Height (in):", min_value=48.0, max_value=96.0, value=68.0, step=0.5)
        height_m = inches_to_m(height_in)
    current_almi = st.sidebar.number_input("Current ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=7.0, step=0.1)
    experience_level = st.sidebar.selectbox("Training Experience:", ["Beginner", "Intermediate", "Advanced"])
    
    percentiles = get_percentile_targets(gender, "ALMI")
    suggested_almi = find_next_percentile(current_almi, percentiles)
    target_almi = st.sidebar.number_input("Target ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=suggested_almi, step=0.1)
    
    st.title("Advanced Body Composition & Recomposition Calculator")
    st.write("Calculate lean mass gains with limb-specific inputs, visual analysis, and DEXA-style reports. Disclaimer: Consult a healthcare provider for personalized advice.")
    
    # Quick DEXA ALMI Calculator (results in main area)
    st.subheader("Quick DEXA ALMI Goal Calculator")
    
    if current_almi:
        current_alm_kg = calculate_alm_from_almi(current_almi, height_m)
        results_data = []
        
        short_term_target = percentiles["75th percentile"]  # Short-term: health baseline
        long_term_target = percentiles["95th percentile"]  # Long-term: elite/longevity
        fig_timeline_short = None
        fig_timeline_long = None
        
        for perc, percentile_almi in percentiles.items():
            percentile_alm_kg = calculate_alm_from_almi(percentile_almi, height_m)
            mass_needed_kg = max(0, percentile_alm_kg - current_alm_kg)
            mass_needed_lbs = kg_to_lbs(mass_needed_kg)
            
            fig_timeline, months = create_progress_timeline_chart(mass_needed_lbs, experience_level)
            
            if mass_needed_lbs <= 0:
                mass_str = "Achieved"
                months_str = "Achieved"
            else:
                mass_str = f"{mass_needed_lbs:.1f}"
                months_str = f"{months:.1f}"
            
            if perc == "75th percentile":
                fig_timeline_short = fig_timeline
            elif perc == "95th percentile":
                fig_timeline_long = fig_timeline
            
            results_data.append({
                "Percentile": perc,
                "Target ALMI": f"{percentile_almi:.1f} kg/m²",
                "Lean Mass Needed (lbs)": mass_str,
                "Est. Time (months)": months_str
            })
        
        results_df = pd.DataFrame(results_data)
        st.dataframe(results_df, use_container_width=True)
        
        # Custom target calculation
        target_alm_kg = calculate_alm_from_almi(target_almi, height_m)
        mass_needed_kg = max(0, target_alm_kg - current_alm_kg)
        mass_needed_lbs = kg_to_lbs(mass_needed_kg)
        fig_custom, months_custom = create_progress_timeline_chart(mass_needed_lbs, experience_level)
        
        if mass_needed_lbs <= 0:
            st.success("Target Achieved!")
        else:
            st.write(f"Target Lean Mass Needed: {mass_needed_lbs:.1f} lbs")
            st.write(f"Estimated Time to Target: {months_custom:.1f} months")
            st.plotly_chart(fig_custom, use_container_width=True)
        
        # Display percentile chart
        fig_percentile = create_percentile_visualization(current_almi, target_almi, gender, "ALMI")
        st.plotly_chart(fig_percentile, use_container_width=True)
        
        # Display timelines for short and long term
        st.subheader("Percentile Timelines")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.write("Short-term Timeline (75th percentile)")
            if fig_timeline_short:
                st.plotly_chart(fig_timeline_short, use_container_width=True)
        with col_t2:
            st.write("Long-term Timeline (95th percentile)")
            if fig_timeline_long:
                st.plotly_chart(fig_timeline_long, use_container_width=True)
        
        st.caption("Note: Gain rates are approximate (Beginner: 1.5 lbs/month ALM, Intermediate: 0.75, Advanced: 0.375). Adjust for age/diet/training. ALMI declines ~1% per decade after 30; consider age in goals.")
    
    # Rest of the app (existing features)
    st.subheader("Advanced Analysis")
    input_method = st.radio("Analysis type:", 
                           ["Limb-Specific Analysis", "Body Recomposition Planning", "CSV Upload"], 
                           horizontal=True, key="advanced_input_method")
    
    if input_method == "CSV Upload":
        st.subheader("CSV Upload")
        st.write("Upload a CSV with columns for height, gender, and body composition data")
        
        csv_unit_system = st.radio("CSV data units:", ["Metric", "English"], horizontal=True, key="csv_units")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="csv_uploader")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("**Data preview:**")
            st.dataframe(df.head())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                height_col = st.selectbox("Height column:", df.columns, key="csv_height_col")
                st.caption("English: inches, Metric: cm")
            with col2:
                gender_col = st.selectbox("Gender column:", df.columns, key="csv_gender_col")
            with col3:
                calc_type = st.selectbox("Calculate:", ["ALMI", "FFMI"], key="csv_calc_type")
            
            if st.button("Process CSV", key="csv_process_button"):
                st.success("CSV processing functionality available - implement batch analysis here")
    
    elif input_method == "Body Recomposition Planning":
        st.subheader("Complete Body Recomposition Calculator")
        
        # Unit system
        recomp_unit_system = st.radio("Units:", ["Metric", "English"], horizontal=True, key="recomp_units")
        
        # Basic inputs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if recomp_unit_system == "Metric":
                recomp_height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, 
                                           value=170.0, step=0.5, key="recomp_height_cm")
                recomp_height_m = recomp_height_cm / 100
            else:
                recomp_height_in = st.number_input("Height (inches):", min_value=48.0, max_value=96.0, 
                                           value=68.0, step=0.5, key="recomp_height_in")
                recomp_height_m = inches_to_m(recomp_height_in)
        
        with col2:
            if recomp_unit_system == "Metric":
                current_weight = st.number_input("Current Weight (kg):", min_value=30.0, max_value=200.0, value=70.0, key="recomp_current_weight_kg")
            else:
                current_weight_lbs = st.number_input("Current Weight (lbs):", min_value=66.0, max_value=440.0, value=154.0, key="recomp_current_weight_lbs")
                current_weight = lbs_to_kg(current_weight_lbs)
        
        with col3:
            current_bf_pct = st.number_input("Current Body Fat (%):", min_value=5.0, max_value=40.0, value=20.0, key="recomp_bf_pct")
        
        with col4:
            recomp_gender = st.selectbox("Gender:", ["Male", "Female"], key="recomp_gender")
        
        # Recomposition targets
        st.write("**Recomposition Goals:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if recomp_unit_system == "Metric":
                target_lean_gain = st.number_input("Lean Mass Gain (kg):", min_value=0.0, max_value=30.0, value=5.0, step=0.5, key="recomp_lean_gain_kg")
            else:
                target_lean_gain_lbs = st.number_input("Lean Mass Gain (lbs):", min_value=0.0, max_value=66.0, value=11.0, step=1.0, key="recomp_lean_gain_lbs")
                target_lean_gain = lbs_to_kg(target_lean_gain_lbs)
        
        with col2:
            if recomp_unit_system == "Metric":
                target_fat_loss = st.number_input("Subcutaneous Fat Loss (kg):", min_value=0.0, max_value=50.0, value=8.0, step=0.5, key="recomp_fat_loss_kg")
            else:
                target_fat_loss_lbs = st.number_input("Subcutaneous Fat Loss (lbs):", min_value=0.0, max_value=110.0, value=17.6, step=1.0, key="recomp_fat_loss_lbs")
                target_fat_loss = lbs_to_kg(target_fat_loss_lbs)
        
        with col3:
            if recomp_unit_system == "Metric":
                target_vat_loss = st.number_input("Visceral Fat Loss (kg):", min_value=0.0, max_value=10.0, value=1.0, step=0.1, key="recomp_vat_loss_kg")
            else:
                target_vat_loss_lbs = st.number_input("Visceral Fat Loss (lbs):", min_value=0.0, max_value=22.0, value=2.2, step=0.2, key="recomp_vat_loss_lbs")
                target_vat_loss = lbs_to_kg(target_vat_loss_lbs)
        
        # Calculate recomposition
        recomp = calculate_body_recomp(current_weight, current_bf_pct, target_lean_gain, target_fat_loss, target_vat_loss)
        
        # Display summary
        weight_unit = "lbs" if recomp_unit_system == "English" else "kg"
        if recomp['net_weight_change'] > 0:
            change_direction = "gain"
        elif recomp['net_weight_change'] < 0:
            change_direction = "lose"
        else:
            change_direction = "maintain"
        
        weight_change = kg_to_lbs(abs(recomp['net_weight_change'])) if recomp_unit_system == "English" else abs(recomp['net_weight_change'])
        
        st.success(f"**Summary: {change_direction.title()} {weight_change:.1f} {weight_unit} total while gaining muscle and losing fat**")
        
        # Create and display visualization
        if st.button("Generate Recomposition Analysis", key="recomp_generate_button"):
            fig = create_recomp_visualization(recomp, recomp_unit_system)
            st.plotly_chart(fig, use_container_width=True)
    
    elif input_method == "Limb-Specific Analysis":
        # Unit system
        limb_unit_system = st.radio("Units:", ["Metric", "English"], horizontal=True, key="limb_units")
        
        # Basic inputs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if limb_unit_system == "Metric":
                limb_height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, 
                                           value=170.0, step=0.5, key="limb_height_cm")
                limb_height_m = limb_height_cm / 100
                height_display = f"{limb_height_cm:.1f} cm"
            else:
                limb_height_in = st.number_input("Height (inches):", min_value=48.0, max_value=96.0, 
                                           value=68.0, step=0.5, key="limb_height_in")
                limb_height_m = inches_to_m(limb_height_in)
                height_display = f"{limb_height_in:.1f} in"
        
        with col2:
            limb_gender = st.selectbox("Gender:", ["Male", "Female"], key="limb_gender")
        
        with col3:
            calc_type = st.radio("Calculate:", ["ALMI", "FFMI"], key="limb_calc_type")
        
        # Input method selection
        st.subheader("Current Body Composition Input")
        
        limb_input_type = st.radio("Input method:", 
                             ["Direct ALMI/FFMI", "Individual Limb Masses", "From Weight & Body Fat"], key="limb_input_type")
        
        current_metric = None
        limb_data = None
        scan_data = {}
        
        if limb_input_type == "Direct ALMI/FFMI":
            if calc_type == "ALMI":
                current_metric = st.number_input(f"Current ALMI (kg/m²):", 
                                               min_value=3.0, max_value=15.0, 
                                               value=6.5, step=0.1, key="limb_direct_almi")
                # Estimate limb masses for visualization
                total_alm = calculate_alm_from_almi(current_metric, limb_height_m)
                limb_data = {
                    'left_arm': total_alm * 0.23,   # Typical proportions
                    'right_arm': total_alm * 0.25,
                    'left_leg': total_alm * 0.25,
                    'right_leg': total_alm * 0.27
                }
            else:
                current_metric = st.number_input(f"Current FFMI (kg/m²):", 
                                               min_value=10.0, max_value=30.0, 
                                               value=18.0, step=0.1, key="limb_direct_ffmi")
        
        elif limb_input_type == "Individual Limb Masses":
            st.write("**Enter lean mass for each limb:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if limb_unit_system == "Metric":
                    left_arm = st.number_input("Left Arm (kg):", min_value=1.0, max_value=15.0, value=3.2, step=0.1, key="limb_left_arm_kg")
                else:
                    left_arm_lbs = st.number_input("Left Arm (lbs):", min_value=2.2, max_value=33.0, value=7.0, step=0.2, key="limb_left_arm_lbs")
                    left_arm = lbs_to_kg(left_arm_lbs)
            
            with col2:
                if limb_unit_system == "Metric":
                    right_arm = st.number_input("Right Arm (kg):", min_value=1.0, max_value=15.0, value=3.4, step=0.1, key="limb_right_arm_kg")
                else:
                    right_arm_lbs = st.number_input("Right Arm (lbs):", min_value=2.2, max_value=33.0, value=7.5, step=0.2, key="limb_right_arm_lbs")
                    right_arm = lbs_to_kg(right_arm_lbs)
            
            with col3:
                if limb_unit_system == "Metric":
                    left_leg = st.number_input("Left Leg (kg):", min_value=3.0, max_value=25.0, value=8.2, step=0.1, key="limb_left_leg_kg")
                else:
                    left_leg_lbs = st.number_input("Left Leg (lbs):", min_value=6.6, max_value=55.0, value=18.0, step=0.2, key="limb_left_leg_lbs")
                    left_leg = lbs_to_kg(left_leg_lbs)
            
            with col4:
                if limb_unit_system == "Metric":
                    right_leg = st.number_input("Right Leg (kg):", min_value=3.0, max_value=25.0, value=8.5, step=0.1, key="limb_right_leg_kg")
                else:
                    right_leg_lbs = st.number_input("Right Leg (lbs):", min_value=6.6, max_value=55.0, value=18.7, step=0.2, key="limb_right_leg_lbs")
                    right_leg = lbs_to_kg(right_leg_lbs)
            
            # Calculate total ALM and ALMI
            total_alm = calculate_alm_from_limbs(left_arm, right_arm, left_leg, right_leg)
            current_metric = calculate_almi_from_alm(total_alm, limb_height_m)
            
            limb_data = {
                'left_arm': left_arm,
                'right_arm': right_arm,
                'left_leg': left_leg,
                'right_leg': right_leg
            }
            
            st.info(f"Calculated ALMI: {current_metric:.2f} kg/m² (Total ALM: {total_alm:.1f} kg)")
        
        elif limb_input_type == "From Weight & Body Fat":
            col1, col2 = st.columns(2)
            with col1:
                if limb_unit_system == "Metric":
                    weight_kg = st.number_input("Weight (kg):", min_value=30.0, max_value=200.0, value=70.0, key="limb_weight_kg")
                else:
                    weight_lbs = st.number_input("Weight (lbs):", min_value=66.0, max_value=440.0, value=154.0, key="limb_weight_lbs")
                    weight_kg = lbs_to_kg(weight_lbs)
            with col2:
                body_fat_pct = st.number_input("Body Fat (%):", min_value=5.0, max_value=40.0, value=15.0, key="limb_bf_pct")
            
            if calc_type == "ALMI":
                ffm = weight_kg * (1 - body_fat_pct / 100)
                estimated_alm = ffm * 0.75  # ALM is ~75% of FFM
                current_metric = calculate_almi_from_alm(estimated_alm, limb_height_m)
                
                # Estimate limb distribution
                limb_data = {
                    'left_arm': estimated_alm * 0.23,
                    'right_arm': estimated_alm * 0.25,
                    'left_leg': estimated_alm * 0.25,
                    'right_leg': estimated_alm * 0.27
                }
                st.info(f"Estimated ALMI: {current_metric:.2f} kg/m² (ALM ≈ 75% of FFM)")
            else:
                current_metric = calculate_ffmi_from_weight_bf(weight_kg, body_fat_pct, limb_height_m)
                st.info(f"Calculated FFMI: {current_metric:.2f} kg/m²")
            
            # Store data for DEXA report
            scan_data.update({
                'weight': weight_kg,
                'body_fat': body_fat_pct,
                'alm': estimated_alm if calc_type == "ALMI" else ffm,
                'left_arm': limb_data['left_arm'] if calc_type == "ALMI" else ffm * 0.23,
                'right_arm': limb_data['right_arm'] if calc_type == "ALMI" else ffm * 0.25,
                'left_leg': limb_data['left_leg'] if calc_type == "ALMI" else ffm * 0.25,
                'right_leg': limb_data['right_leg'] if calc_type == "ALMI" else ffm * 0.27
            })
        
        # Target selection
        st.subheader("Target Analysis")
        
        target_method = st.radio("Analysis type:", ["Specific Target", "Percentile Goals", "Visual Analysis"], key="limb_target_method")
        
        if target_method == "Specific Target":
            if calc_type == "ALMI":
                target_metric = st.number_input(f"Target ALMI (kg/m²):", 
                                              min_value=3.0, max_value=15.0, 
                                              value=7.5, step=0.1, key="limb_specific_almi")
            else:
                target_metric = st.number_input(f"Target FFMI (kg/m²):", 
                                              min_value=10.0, max_value=30.0, 
                                              value=20.0, step=0.1, key="limb_specific_ffmi")
            
            # Calculate mass needed
            if current_metric:
                if calc_type == "ALMI":
                    current_mass = calculate_alm_from_almi(current_metric, limb_height_m)
                    target_mass = calculate_alm_from_almi(target_metric, limb_height_m)
                else:
                    current_mass = calculate_ffm_from_ffmi(current_metric, limb_height_m)
                    target_mass = calculate_ffm_from_ffmi(target_metric, limb_height_m)
                
                mass_needed = target_mass - current_mass
                
                if mass_needed > 0:
                    if limb_unit_system == "English":
                        st.success(f"**To reach {target_metric:.1f} kg/m² {calc_type}: Gain {kg_to_lbs(mass_needed):.1f} lbs lean mass**")
                    else:
                        st.success(f"**To reach {target_metric:.1f} kg/m² {calc_type}: Gain {mass_needed:.1f} kg lean mass**")
                else:
                    st.success("**Target already reached!**")
        
        elif target_method == "Percentile Goals":
            percentiles = get_percentile_targets(limb_gender, calc_type)
            
            if current_metric:
                results_data = []
                
                for percentile, target_value in percentiles.items():
                    if calc_type == "ALMI":
                        current_mass = calculate_alm_from_almi(current_metric, limb_height_m)
                        target_mass = calculate_alm_from_almi(target_value, limb_height_m)
                    else:
                        current_mass = calculate_ffm_from_ffmi(current_metric, limb_height_m)
                        target_mass = calculate_ffm_from_ffmi(target_value, limb_height_m)
                    
                    mass_needed = max(0, target_mass - current_mass)
                    
                    if mass_needed == 0:
                        status = "✅ Achieved"
                    else:
                        if limb_unit_system == "English":
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
                
                # Create percentile visualization
                if st.button("Generate Percentile Chart", key="limb_percentile_button"):
                    target_value = percentiles["75th percentile"]  # Default to 75th percentile
                    fig = create_percentile_visualization(current_metric, target_value, limb_gender, calc_type)
                    st.plotly_chart(fig, use_container_width=True)
        
        elif target_method == "Visual Analysis":
            if limb_data and st.button("Generate Limb Analysis", key="limb_generate_button"):
                fig = create_limb_composition_chart(
                    limb_data['left_arm'], limb_data['right_arm'], 
                    limb_data['left_leg'], limb_data['right_leg'], 
                    limb_unit_system
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # DEXA Report Generation
        st.subheader("Generate DEXA-Style Report")
        
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Patient Name:", value="John Doe", key="limb_patient_name")
            patient_dob = st.date_input("Date of Birth:", value=datetime(1990, 1, 1), key="limb_dob")
        
        with col2:
            if st.button("Generate DEXA Report", key="limb_report_button"):
                if current_metric and limb_data:
                    # Prepare patient data
                    patient_data = {
                        'name': patient_name,
                        'dob': patient_dob.strftime("%m/%d/%Y"),
                        'height_m': limb_height_m,
                        'height_cm': limb_height_cm if limb_unit_system == "Metric" else limb_height_in * 2.54,
                        'height_in': limb_height_in if limb_unit_system == "English" else limb_height_cm / 2.54
                    }
                    
                    # Prepare scan data
                    if not scan_data:  # If not from weight/BF input
                        scan_data = {
                            'weight': 70.0,  # Default values
                            'body_fat': 15.0,
                            'alm': sum(limb_data.values()) if limb_data else calculate_alm_from_almi(current_metric, limb_height_m),
                            'left_arm': limb_data['left_arm'],
                            'right_arm': limb_data['right_arm'],
                            'left_leg': limb_data['left_leg'],
                            'right_leg': limb_data['right_leg']
                        }
                    
                    # Generate HTML report
                    html_report = generate_dexa_report_html(patient_data, scan_data, limb_unit_system)
                    
                    # Provide download link
                    b64 = base64.b64encode(html_report.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="dexa_report_{patient_name.replace(" ", "_")}.html">Download DEXA Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    st.success("DEXA report generated! Click the link above to download.")
                else:
                    st.error("Please complete the body composition analysis first.")
        
        # Reference ranges
        st.subheader("Reference Information")
        if calc_type == "ALMI":
            if limb_gender == "Male":
                st.caption("Male ALMI reference: Normal ≥ 7.0 kg/m², Low < 7.0 kg/m²")
            else:
                st.caption("Female ALMI reference: Normal ≥ 5.5 kg/m², Low < 5.5 kg/m²")
        else:
            if limb_gender == "Male":
                st.caption("Male FFMI reference: Average 16.7-19.8 kg/m², Athletic >20 kg/m², Elite 22-25 kg/m²")
            else:
                st.caption("Female FFMI reference: Average 14.6-16.8 kg/m², Athletic >17 kg/m²")

if __name__ == "__main__":
    main()