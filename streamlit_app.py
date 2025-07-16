import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ================================
# CONFIGURATION AND DATA
# ================================

# Research-based ALMI percentile cutpoints (kg/m²)
# Based on multiple studies including Ball State/UW-Milwaukee and Australian Body Composition studies
ALMI_PERCENTILES = {
    "Male": {
        "3rd": 6.2,
        "10th": 6.8,
        "25th": 7.4,
        "50th": 8.1,
        "75th": 8.8,
        "90th": 9.6,
        "97th": 10.4
    },
    "Female": {
        "3rd": 4.8,
        "10th": 5.2,
        "25th": 5.7,
        "50th": 6.2,
        "75th": 6.8,
        "90th": 7.4,
        "97th": 8.0
    }
}

# Sarcopenia cutpoints (EWGSOP2 and research-based)
SARCOPENIA_CUTPOINTS = {
    "Male": 7.0,
    "Female": 5.5
}

# Realistic muscle gain rates (lbs/year) based on research
MUSCLE_GAIN_RATES = {
    "Male": {
        "Beginner": (4, 8),
        "Intermediate": (2, 4),
        "Advanced": (0.5, 2)
    },
    "Female": {
        "Beginner": (2, 4),
        "Intermediate": (1, 2.5),
        "Advanced": (0.25, 1.5)
    }
}

# ================================
# UTILITY FUNCTIONS
# ================================

def lbs_to_kg(lbs):
    return lbs / 2.20462

def kg_to_lbs(kg):
    return kg * 2.20462

def inches_to_m(inches):
    return inches * 0.0254

def calculate_alm_from_almi(almi, height_m):
    return almi * (height_m ** 2)

def calculate_almi_from_alm(alm_kg, height_m):
    return alm_kg / (height_m ** 2)

def get_current_percentile(almi, gender):
    """Determine current percentile based on ALMI value"""
    percentiles = ALMI_PERCENTILES[gender]
    
    if almi <= percentiles["3rd"]:
        return "Below 3rd"
    elif almi <= percentiles["10th"]:
        return "3rd-10th"
    elif almi <= percentiles["25th"]:
        return "10th-25th"
    elif almi <= percentiles["50th"]:
        return "25th-50th"
    elif almi <= percentiles["75th"]:
        return "50th-75th"
    elif almi <= percentiles["90th"]:
        return "75th-90th"
    elif almi <= percentiles["97th"]:
        return "90th-97th"
    else:
        return "Above 97th"

def estimate_timeline(mass_needed_lbs, gender, experience):
    """Calculate realistic timeline for muscle gain"""
    if mass_needed_lbs <= 0:
        return 0, 0, "Achieved"
    
    min_rate, max_rate = MUSCLE_GAIN_RATES[gender][experience]
    
    # Calculate years, then convert to months
    min_years = mass_needed_lbs / max_rate
    max_years = mass_needed_lbs / min_rate if min_rate > 0 else float('inf')
    
    min_months = min_years * 12
    max_months = min(max_years * 12, 120)  # Cap at 10 years
    
    return min_months, max_months, f"{min_months:.1f}-{max_months:.1f}"

def get_health_status(almi, gender):
    """Determine health status based on ALMI"""
    sarcopenia_cutpoint = SARCOPENIA_CUTPOINTS[gender]
    percentiles = ALMI_PERCENTILES[gender]
    
    if almi < sarcopenia_cutpoint:
        return "⚠️ Low Muscle Mass", "red"
    elif almi < percentiles["25th"]:
        return "🟡 Below Average", "orange"
    elif almi < percentiles["75th"]:
        return "🟢 Average", "green"
    elif almi < percentiles["90th"]:
        return "💪 Above Average", "blue"
    else:
        return "🏆 Excellent", "purple"

# ================================
# VISUALIZATION FUNCTIONS
# ================================

def create_percentile_chart(current_almi, target_almi, gender):
    """Create modern percentile visualization"""
    percentiles = ALMI_PERCENTILES[gender]
    
    fig = go.Figure()
    
    # Create gradient colors
    colors = ['#FF6B6B', '#FFA500', '#FFD700', '#90EE90', '#4169E1', '#8A2BE2', '#FF1493']
    
    # Add percentile bars
    percentile_names = list(percentiles.keys())
    percentile_values = list(percentiles.values())
    
    fig.add_trace(go.Bar(
        x=percentile_names,
        y=percentile_values,
        marker=dict(
            color=colors,
            line=dict(width=1, color='rgba(0,0,0,0.1)'),
            opacity=0.8
        ),
        text=[f'{val:.1f}' for val in percentile_values],
        textposition='outside',
        name='Percentiles',
        hovertemplate='<b>%{x} Percentile</b><br>%{y:.1f} kg/m²<extra></extra>'
    ))
    
    # Add current ALMI line
    if current_almi > 0:
        fig.add_hline(
            y=current_almi,
            line=dict(color='#FF0000', width=3, dash='dash'),
            annotation_text=f"Current: {current_almi:.1f}",
            annotation_position="top right"
        )
    
    # Add target ALMI line
    if target_almi != current_almi:
        fig.add_hline(
            y=target_almi,
            line=dict(color='#00AA00', width=3, dash='dash'),
            annotation_text=f"Target: {target_almi:.1f}",
            annotation_position="bottom right"
        )
    
    # Add sarcopenia cutpoint
    sarcopenia_line = SARCOPENIA_CUTPOINTS[gender]
    fig.add_hline(
        y=sarcopenia_line,
        line=dict(color='#800080', width=2, dash='dot'),
        annotation_text=f"Sarcopenia Risk: {sarcopenia_line:.1f}",
        annotation_position="top left"
    )
    
    fig.update_layout(
        title=f'ALMI Percentiles for {gender}s',
        xaxis_title="Percentile",
        yaxis_title="ALMI (kg/m²)",
        template='plotly_white',
        height=500,
        showlegend=False,
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_progress_chart(almi_needed, gender, experience):
    """Create timeline visualization"""
    min_months, max_months, timeline_str = estimate_timeline(almi_needed, gender, experience)
    
    if min_months == 0:
        st.success("🎉 Target Already Achieved!")
        return None
    
    fig = go.Figure()
    
    # Color scheme based on gender
    primary_color = '#E91E63' if gender == "Female" else '#2196F3'
    secondary_color = '#FCE4EC' if gender == "Female" else '#E3F2FD'
    
    # Create timeline bar
    fig.add_trace(go.Bar(
        x=[min_months],
        y=[experience],
        orientation='h',
        name='Optimistic Timeline',
        marker_color=primary_color,
        text=f'{min_months:.1f} months',
        textposition='inside'
    ))
    
    if max_months > min_months:
        fig.add_trace(go.Bar(
            x=[max_months - min_months],
            y=[experience],
            orientation='h',
            name='Realistic Range',
            marker_color=secondary_color,
            text=f'+{max_months - min_months:.1f} months',
            textposition='inside'
        ))
    
    fig.update_layout(
        title='Estimated Timeline to Target',
        xaxis_title='Months',
        yaxis_title='Experience Level',
        template='plotly_white',
        height=300,
        barmode='stack',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_limb_analysis(limb_data, unit_system):
    """Enhanced limb asymmetry analysis"""
    if not any(v > 0 for v in limb_data.values()):
        return None
    
    valid_limbs = {k: v for k, v in limb_data.items() if v > 0}
    if len(valid_limbs) < 2:
        return None
    
    limb_names = list(valid_limbs.keys())
    limb_values = list(valid_limbs.values())
    mean_value = np.mean(limb_values)
    asymmetries = [(v - mean_value) / mean_value * 100 for v in limb_values]
    
    # Color code based on asymmetry
    colors = []
    for asym in asymmetries:
        if abs(asym) <= 5:
            colors.append('#4CAF50')  # Green - Normal
        elif abs(asym) <= 10:
            colors.append('#FF9800')  # Orange - Moderate
        else:
            colors.append('#F44336')  # Red - Significant
    
    fig = go.Figure()
    
    unit_label = "kg" if unit_system == "Metric" else "lbs"
    
    fig.add_trace(go.Bar(
        x=limb_names,
        y=limb_values,
        marker=dict(color=colors, opacity=0.8),
        text=[f'{val:.1f}<br>({asym:+.1f}%)' for val, asym in zip(limb_values, asymmetries)],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.1f} ' + unit_label + '<br>Asymmetry: %{customdata:+.1f}%<extra></extra>',
        customdata=asymmetries
    ))
    
    # Add mean line
    fig.add_hline(
        y=mean_value,
        line=dict(dash="dash", color="#666", width=2),
        annotation_text=f"Mean: {mean_value:.1f} {unit_label}"
    )
    
    fig.update_layout(
        title='Limb Lean Mass Distribution',
        xaxis_title='Limb',
        yaxis_title=f'Lean Mass ({unit_label})',
        template='plotly_white',
        height=400,
        showlegend=False,
        font=dict(family="Inter, sans-serif")
    )
    
    return fig, asymmetries, mean_value

# ================================
# MAIN APPLICATION
# ================================

def main():
    st.set_page_config(
        page_title="DEXA ALMI Calculator",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">💪 DEXA ALMI Calculator</div>', unsafe_allow_html=True)
    st.markdown("**Optimize your muscle health with research-based ALMI targets and realistic timelines**")
    
    # Sidebar inputs
    with st.sidebar:
        st.header("📊 Input Parameters")
        
        # Basic parameters
        gender = st.selectbox("👤 Gender", ["Male", "Female"])
        unit_system = st.radio("📏 Units", ["Metric", "Imperial"])
        
        # Height input
        if unit_system == "Metric":
            height_cm = st.number_input(
                "📐 Height (cm)", 
                min_value=120.0, max_value=220.0, 
                value=175.0 if gender == "Male" else 165.0, 
                step=0.5
            )
            height_m = height_cm / 100
        else:
            height_in = st.number_input(
                "📐 Height (inches)", 
                min_value=48.0, max_value=84.0, 
                value=70.0 if gender == "Male" else 65.0, 
                step=0.5
            )
            height_m = inches_to_m(height_in)
        
        # ALMI input
        current_almi = st.number_input(
            "🎯 Current ALMI (kg/m²)", 
            min_value=3.0, max_value=15.0, 
            value=8.0 if gender == "Male" else 6.0, 
            step=0.1,
            help="From your DEXA scan report"
        )
        
        # Training experience
        experience = st.selectbox(
            "🏋️ Training Experience", 
            ["Beginner", "Intermediate", "Advanced"]
        )
        
        st.divider()
        
        # Target selection
        st.subheader("🎯 Goal Setting")
        percentiles = ALMI_PERCENTILES[gender]
        
        goal_options = {
            "Health Maintenance (50th percentile)": percentiles["50th"],
            "Longevity Target (75th percentile)": percentiles["75th"],
            "Optimal Performance (90th percentile)": percentiles["90th"],
            "Elite Level (97th percentile)": percentiles["97th"],
            "Custom Target": "custom"
        }
        
        goal_selection = st.selectbox("Select Goal", list(goal_options.keys()))
        
        if goal_options[goal_selection] == "custom":
            target_almi = st.number_input(
                "Custom Target ALMI (kg/m²)", 
                min_value=current_almi, max_value=15.0, 
                value=current_almi + 0.5, 
                step=0.1
            )
        else:
            target_almi = goal_options[goal_selection]
        
        # Optional limb analysis
        st.divider()
        st.subheader("🦾 Limb Analysis (Optional)")
        enable_limb = st.toggle("Enable limb asymmetry analysis")
        
        limb_data = {}
        if enable_limb:
            unit_label = "kg" if unit_system == "Metric" else "lbs"
            
            col1, col2 = st.columns(2)
            with col1:
                limb_data["Right Arm"] = st.number_input(f"Right Arm ({unit_label})", min_value=0.0, step=0.1)
                limb_data["Right Leg"] = st.number_input(f"Right Leg ({unit_label})", min_value=0.0, step=0.1)
            with col2:
                limb_data["Left Arm"] = st.number_input(f"Left Arm ({unit_label})", min_value=0.0, step=0.1)
                limb_data["Left Leg"] = st.number_input(f"Left Leg ({unit_label})", min_value=0.0, step=0.1)
    
    # Main content
    if current_almi and height_m:
        # Calculate current stats
        current_alm_kg = calculate_alm_from_almi(current_almi, height_m)
        target_alm_kg = calculate_alm_from_almi(target_almi, height_m)
        alm_needed_kg = max(0, target_alm_kg - current_alm_kg)
        alm_needed_lbs = kg_to_lbs(alm_needed_kg)
        
        # Get health status
        health_status, status_color = get_health_status(current_almi, gender)
        current_percentile = get_current_percentile(current_almi, gender)
        
        # Display current status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current ALMI", f"{current_almi:.1f} kg/m²")
        
        with col2:
            st.metric("Current ALM", f"{kg_to_lbs(current_alm_kg):.1f} lbs")
        
        with col3:
            st.metric("Current Percentile", current_percentile)
        
        with col4:
            st.markdown(f"""
            <div class="status-card" style="border-left-color: {status_color};">
                <strong>{health_status}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Target analysis
        if alm_needed_lbs > 0:
            st.subheader(f"📈 Target Analysis: {target_almi:.1f} kg/m²")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("ALM Needed", f"{alm_needed_lbs:.1f} lbs")
                
                # Timeline estimation
                min_months, max_months, timeline_str = estimate_timeline(alm_needed_lbs, gender, experience)
                
                if min_months > 0:
                    if max_months >= 120:
                        timeline_display = f"{min_months:.1f}+ months"
                    else:
                        timeline_display = f"{min_months:.1f}-{max_months:.1f} months"
                    
                    st.metric("Estimated Timeline", timeline_display)
                    
                    # Progress visualization
                    progress_fig = create_progress_chart(alm_needed_lbs, gender, experience)
                    if progress_fig:
                        st.plotly_chart(progress_fig, use_container_width=True)
            
            with col2:
                # Key insights
                st.markdown("### 💡 Key Insights")
                
                gain_rates = MUSCLE_GAIN_RATES[gender][experience]
                st.markdown(f"• **Expected gain rate:** {gain_rates[0]}-{gain_rates[1]} lbs/year")
                
                if min_months > 24:
                    st.warning("⏰ This is a long-term goal. Consider intermediate targets.")
                
                if current_almi < SARCOPENIA_CUTPOINTS[gender]:
                    st.error("⚠️ Current ALMI indicates low muscle mass risk.")
                
                if target_almi >= ALMI_PERCENTILES[gender]["75th"]:
                    st.success("🎯 Target aligns with longevity research!")
        
        else:
            st.success("🎉 Congratulations! You've already achieved your target ALMI.")
        
        # Percentile visualization
        st.subheader("📊 ALMI Percentile Chart")
        percentile_fig = create_percentile_chart(current_almi, target_almi, gender)
        st.plotly_chart(percentile_fig, use_container_width=True)
        
        # Limb analysis
        if enable_limb and any(v > 0 for v in limb_data.values()):
            st.subheader("🦾 Limb Asymmetry Analysis")
            
            limb_result = create_limb_analysis(limb_data, unit_system)
            if limb_result:
                fig, asymmetries, mean_value = limb_result
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    max_asymmetry = max(abs(a) for a in asymmetries)
                    
                    st.markdown("**Assessment:**")
                    if max_asymmetry <= 5:
                        st.success("✅ Normal symmetry")
                    elif max_asymmetry <= 10:
                        st.warning("⚠️ Moderate asymmetry")
                    else:
                        st.error("🚨 Significant asymmetry")
                    
                    st.markdown(f"**Max asymmetry:** {max_asymmetry:.1f}%")
                    st.markdown("**Guidelines:**")
                    st.markdown("• <5%: Normal variation")
                    st.markdown("• 5-10%: Monitor closely")
                    st.markdown("• >10%: Consider targeted training")
        
        # Research references and methodology
        with st.expander("📚 Research References & Methodology"):
            st.markdown("""
            **ALMI Percentiles:** Based on research from Ball State University, University of Wisconsin-Milwaukee, 
            and Australian Body Composition studies using GE-Healthcare DXA systems.
            
            **Sarcopenia Cutpoints:** European Working Group on Sarcopenia in Older People 2 (EWGSOP2) guidelines.
            
            **Muscle Gain Rates:** Compiled from multiple longitudinal training studies accounting for gender, 
            training status, and realistic progression rates.
            
            **Longevity Connection:** Research by Dr. Peter Attia and others shows ALMI above 75th percentile 
            correlates with improved healthspan and longevity outcomes.
            
            **Disclaimer:** This tool is for educational purposes. Consult healthcare professionals for 
            personalized medical advice.
            """)

if __name__ == "__main__":
    main()