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
    rates = {
        "Beginner": 1.5,
        "Intermediate": 0.75,
        "Advanced": 0.375
    }
    return rates.get(experience_level, 0.75)  # Default to Intermediate if invalid

def create_percentile_visualization(current_metric, target_metric, gender):
    """Create percentile goal visualization using Plotly"""
    percentiles = get_percentile_targets(gender)
    
    percentile_names = list(percentiles.keys())
    percentile_values = list(percentiles.values())
    
    # Create bar chart
    fig = go.Figure()
    
    # Add percentile bars with a modern color gradient
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

def create_progress_timeline_chart(mass_needed_lbs, experience_level):
    """Create timeline visualization for lean mass gain progress"""
    monthly_rate = estimate_gain_rate(experience_level)
    if mass_needed_lbs > 0 and monthly_rate > 0:
        timeline_months = max(1, mass_needed_lbs / monthly_rate)
    else:
        timeline_months = 0
    
    fig = go.Figure()
    
    # Horizontal bar with improved color contrast
    fig.add_trace(go.Bar(
        y=[experience_level],
        x=[timeline_months],
        orientation='h',
        name='Estimated Months',
        marker=dict(
            color='#1E90FF' if timeline_months > 0 else '#4CAF50',
            line=dict(color='#1E90FF', width=2),
            opacity=0.9
        ),
        text=[f'{timeline_months:.1f} months' if timeline_months > 0 else 'Achieved'],
        textposition='inside',
        insidetextfont=dict(color='#FFFFFF', size=14),
        hovertemplate='<b>%{y}</b><br>Est. Time: %{x:.1f} months<extra></extra>'
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
        showlegend=False,
        bargap=0.2,
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
    
    return fig, timeline_months

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
            height_cm = st.sidebar.number_input("Height (cm):", min_value=100.0, max_value=250.0, value=170.0, step=0.5, key="height_cm")
            if height_cm <= 0:
                st.sidebar.error("Height must be positive.")
                return
            height_m = height_cm / 100
        else:
            height_in = st.sidebar.number_input("Height (in):", min_value=48.0, max_value=96.0, value=68.0, step=0.5, key="height_in")
            if height_in <= 0:
                st.sidebar.error("Height must be positive.")
                return
            height_m = inches_to_m(height_in)
    except ValueError:
        st.sidebar.error("Invalid height input.")
        return
    
    # Input validation for ALMI
    try:
        current_almi = st.sidebar.number_input("Current ALMI (kg/m²):", min_value=3.0, max_value=15.0, value=7.0, step=0.1, key="current_almi")
        if current_almi <= 0:
            st.sidebar.error("Current ALMI must be positive.")
            return
    except ValueError:
        st.sidebar.error("Invalid ALMI input.")
        return
    
    experience_level = st.sidebar.selectbox("Training Experience:", ["Beginner", "Intermediate", "Advanced"], key="experience_level")
    
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
    
    st.title("DEXA ALMI Goal Calculator")
    with st.container():
        st.markdown("Analyze your ALMI from DEXA scans, set goals, and get realistic timelines. *Disclaimer: Consult a healthcare provider for personalized advice.*")
    
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
        with st.container():
            st.subheader("Percentile Targets")
            st.dataframe(style_dataframe(results_df), use_container_width=True)
        
        # Custom target calculation
        target_alm_kg = calculate_alm_from_almi(target_almi, height_m)
        mass_needed_kg = max(0, target_alm_kg - current_alm_kg)
        mass_needed_lbs = kg_to_lbs(mass_needed_kg)
        fig_custom, months_custom = create_progress_timeline_chart(mass_needed_lbs, experience_level)
        
        with st.container():
            st.subheader("Custom Target")
            if mass_needed_lbs <= 0:
                st.success("Target Achieved!")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Target Lean Mass Needed", f"{mass_needed_lbs:.1f} lbs")
                with col2:
                    st.metric("Estimated Time to Target", f"{months_custom:.1f} months")
                st.plotly_chart(fig_custom, use_container_width=True)
        
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
                st.markdown("**Short-term Timeline (75th percentile)**")
                if fig_timeline_short:
                    st.plotly_chart(fig_timeline_short, use_container_width=True)
        with col_t2:
            with st.container():
                st.markdown("**Long-term Timeline (95th percentile)**")
                if fig_timeline_long:
                    st.plotly_chart(fig_timeline_long, use_container_width=True)
        
        with st.container():
            st.markdown("*Note: Gain rates are approximate (Beginner: 1.5 lbs/month ALM, Intermediate: 0.75, Advanced: 0.375). Adjust for age/diet/training. ALMI declines ~1% per decade after 30; consider age in goals.*")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}. Please check your inputs and try again.")

if __name__ == "__main__":
    main()