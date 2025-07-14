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

def estimate_gain_rate(experience_level):
    """Estimate monthly lean mass gain rate in lbs (for ALM, approximate)"""
    if experience_level == "Beginner":
        return 1.5
    elif experience_level == "Intermediate":
        return 0.75
    else:  # Advanced
        return 0.375

def create_percentile_visualization(current_metric, target_metric, gender):
    """Create percentile goal visualization using Plotly"""
    percentiles = get_percentile_targets(gender)
    
    percentile_names = list(percentiles.keys())
    percentile_values = list(percentiles.values())
    
    # Create bar chart
    fig = go.Figure()
    
    # Add percentile bars with nicer colors
    colors = px.colors.sequential.Viridis[:5]
    
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
            text=f'ALMI Percentile Goals for {gender}s',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#1f2937')
        ),
        xaxis_title="Percentile",
        yaxis_title="ALMI (kg/m²)",
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
    
    percentiles = get_percentile_targets(gender)
    suggested_almi = find_next_percentile(current_almi, percentiles)
    target_almi = st.sidebar.number_input("Target ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=suggested_almi, step=0.1)
    
    st.title("DEXA ALMI Goal Calculator")
    st.write("Analyze your ALMI from DEXA scans, set goals, and get realistic timelines. Disclaimer: Consult a healthcare provider for personalized advice.")
    
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
        fig_percentile = create_percentile_visualization(current_almi, target_almi, gender)
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

if __name__ == "__main__":
    main()