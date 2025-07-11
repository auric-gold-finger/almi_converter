import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import io
import base64

# Set matplotlib style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

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

def create_recomp_visualization(recomp_data, unit_system):
    """Create body recomposition visualization"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Body Recomposition Analysis', fontsize=16, fontweight='bold')
    
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
    
    # 1. Body composition pie charts
    current_data = [current_lean, current_fat]
    new_data = [new_lean, new_fat]
    labels = ['Lean Mass', 'Fat Mass']
    colors = ['#66A3FF', '#F3817D']
    
    ax1.pie(current_data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title(f'Current Body Composition\n{current_weight:.1f} {weight_unit}')
    
    ax2.pie(new_data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title(f'Target Body Composition\n{new_weight:.1f} {weight_unit}')
    
    # 3. Before/After comparison bar chart
    categories = ['Lean Mass', 'Fat Mass', 'Total Weight']
    current_values = [current_lean, current_fat, current_weight]
    new_values = [new_lean, new_fat, new_weight]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, current_values, width, label='Current', color='#757575', alpha=0.7)
    bars2 = ax3.bar(x + width/2, new_values, width, label='Target', color='#267DFF', alpha=0.8)
    
    ax3.set_xlabel('Component')
    ax3.set_ylabel(f'Mass ({weight_unit})')
    ax3.set_title('Current vs Target Comparison')
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories)
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax3.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
    
    # 4. Changes visualization
    changes = [new_lean - current_lean, new_fat - current_fat, new_weight - current_weight]
    change_colors = ['green' if x >= 0 else 'red' for x in changes]
    
    bars = ax4.bar(categories, changes, color=change_colors, alpha=0.7)
    ax4.set_xlabel('Component')
    ax4.set_ylabel(f'Change ({weight_unit})')
    ax4.set_title('Net Changes')
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax4.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, change in zip(bars, changes):
        height = bar.get_height()
        ax4.annotate(f'{change:+.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height >= 0 else -15),
                    textcoords="offset points",
                    ha='center', va='bottom' if height >= 0 else 'top', 
                    fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_limb_composition_chart(left_arm, right_arm, left_leg, right_leg, unit_system):
    """Create limb-specific lean mass visualization"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Appendicular Lean Mass Distribution', fontsize=16, fontweight='bold')
    
    weight_unit = "lbs" if unit_system == "English" else "kg"
    
    # Convert to display units if needed
    if unit_system == "English":
        limb_masses = [kg_to_lbs(left_arm), kg_to_lbs(right_arm), kg_to_lbs(left_leg), kg_to_lbs(right_leg)]
    else:
        limb_masses = [left_arm, right_arm, left_leg, right_leg]
    
    # 1. Pie chart of limb distribution
    labels = ['Left Arm', 'Right Arm', 'Left Leg', 'Right Leg']
    colors = ['#267DFF', '#66A3FF', '#F3817D', '#DA5955']
    
    ax1.pie(limb_masses, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Limb Mass Distribution')
    
    # 2. Bar chart comparison
    bars = ax2.bar(labels, limb_masses, color=colors, alpha=0.8)
    ax2.set_ylabel(f'Lean Mass ({weight_unit})')
    ax2.set_title('Lean Mass by Limb')
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, mass in zip(bars, limb_masses):
        height = bar.get_height()
        ax2.annotate(f'{mass:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold')
    
    # Calculate symmetry
    arm_symmetry = abs(limb_masses[0] - limb_masses[1]) / max(limb_masses[0], limb_masses[1]) * 100
    leg_symmetry = abs(limb_masses[2] - limb_masses[3]) / max(limb_masses[2], limb_masses[3]) * 100
    
    ax2.text(0.02, 0.98, f'Arm Asymmetry: {arm_symmetry:.1f}%\nLeg Asymmetry: {leg_symmetry:.1f}%', 
             transform=ax2.transAxes, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig

def create_percentile_visualization(current_metric, target_metric, gender, metric_type):
    """Create percentile goal visualization"""
    percentiles = get_percentile_targets(gender, metric_type)
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    percentile_names = list(percentiles.keys())
    percentile_values = list(percentiles.values())
    
    # Create bar chart
    bars = ax.bar(range(len(percentile_names)), percentile_values, 
                  color=['#DA5955', '#F3817D', '#757575', '#66A3FF', '#267DFF'], alpha=0.7)
    
    # Add current value line
    ax.axhline(y=current_metric, color='red', linestyle='--', linewidth=2, label=f'Current: {current_metric:.1f}')
    ax.axhline(y=target_metric, color='green', linestyle='--', linewidth=2, label=f'Target: {target_metric:.1f}')
    
    ax.set_xlabel('Percentile')
    ax.set_ylabel(f'{metric_type} (kg/m²)')
    ax.set_title(f'{metric_type} Percentile Goals for {gender}s')
    ax.set_xticks(range(len(percentile_names)))
    ax.set_xticklabels(percentile_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, percentile_values):
        height = bar.get_height()
        ax.annotate(f'{value:.1f}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    return fig

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
    
    # Read the HTML template from the document
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
            <p>&copy; 2025 Body Composition Analysis. All Rights Reserved.</p>
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

def main():
    st.title("Advanced Body Composition & Recomposition Calculator")
    st.write("Calculate lean mass gains with limb-specific inputs, visual analysis, and DEXA-style reports")
    
    # Input method selection
    input_method = st.radio("Analysis type:", 
                           ["Limb-Specific Analysis", "Body Recomposition Planning", "CSV Upload"], 
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
            
            if st.button("Process CSV"):
                st.success("CSV processing functionality available - implement batch analysis here")
    
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
        
        # Display summary
        weight_unit = "lbs" if unit_system == "English" else "kg"
        if recomp['net_weight_change'] > 0:
            change_direction = "gain"
        elif recomp['net_weight_change'] < 0:
            change_direction = "lose"
        else:
            change_direction = "maintain"
        
        weight_change = kg_to_lbs(abs(recomp['net_weight_change'])) if unit_system == "English" else abs(recomp['net_weight_change'])
        
        st.success(f"**Summary: {change_direction.title()} {weight_change:.1f} {weight_unit} total while gaining muscle and losing fat**")
        
        # Create and display visualization
        if st.button("Generate Recomposition Analysis"):
            fig = create_recomp_visualization(recomp, unit_system)
            st.pyplot(fig)
            plt.close()
    
    else:  # Limb-Specific Analysis
        # Unit system
        unit_system = st.radio("Units:", ["Metric", "English"], horizontal=True)
        
        # Basic inputs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if unit_system == "Metric":
                height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, 
                                           value=170.0, step=0.5)
                height_m = height_cm / 100
                height_display = f"{height_cm:.1f} cm"
            else:
                height_in = st.number_input("Height (inches):", min_value=48.0, max_value=96.0, 
                                           value=68.0, step=0.5)
                height_m = inches_to_m(height_in)
                height_display = f"{height_in:.1f} in"
        
        with col2:
            gender = st.selectbox("Gender:", ["Male", "Female"])
        
        with col3:
            calc_type = st.radio("Calculate:", ["ALMI", "FFMI"])
        
        # Input method selection
        st.subheader("Current Body Composition Input")
        
        input_type = st.radio("Input method:", 
                             ["Direct ALMI/FFMI", "Individual Limb Masses", "From Weight & Body Fat"])
        
        current_metric = None
        limb_data = None
        scan_data = {}
        
        if input_type == "Direct ALMI/FFMI":
            if calc_type == "ALMI":
                current_metric = st.number_input(f"Current ALMI (kg/m²):", 
                                               min_value=3.0, max_value=15.0, 
                                               value=6.5, step=0.1)
                # Estimate limb masses for visualization
                total_alm = calculate_alm_from_almi(current_metric, height_m)
                limb_data = {
                    'left_arm': total_alm * 0.23,   # Typical proportions
                    'right_arm': total_alm * 0.25,
                    'left_leg': total_alm * 0.25,
                    'right_leg': total_alm * 0.27
                }
            else:
                current_metric = st.number_input(f"Current FFMI (kg/m²):", 
                                               min_value=10.0, max_value=30.0, 
                                               value=18.0, step=0.1)
        
        elif input_type == "Individual Limb Masses":
            st.write("**Enter lean mass for each limb:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if unit_system == "Metric":
                    left_arm = st.number_input("Left Arm (kg):", min_value=1.0, max_value=15.0, value=3.2, step=0.1)
                else:
                    left_arm_lbs = st.number_input("Left Arm (lbs):", min_value=2.2, max_value=33.0, value=7.0, step=0.2)
                    left_arm = lbs_to_kg(left_arm_lbs)
            
            with col2:
                if unit_system == "Metric":
                    right_arm = st.number_input("Right Arm (kg):", min_value=1.0, max_value=15.0, value=3.4, step=0.1)
                else:
                    right_arm_lbs = st.number_input("Right Arm (lbs):", min_value=2.2, max_value=33.0, value=7.5, step=0.2)
                    right_arm = lbs_to_kg(right_arm_lbs)
            
            with col3:
                if unit_system == "Metric":
                    left_leg = st.number_input("Left Leg (kg):", min_value=3.0, max_value=25.0, value=8.2, step=0.1)
                else:
                    left_leg_lbs = st.number_input("Left Leg (lbs):", min_value=6.6, max_value=55.0, value=18.0, step=0.2)
                    left_leg = lbs_to_kg(left_leg_lbs)
            
            with col4:
                if unit_system == "Metric":
                    right_leg = st.number_input("Right Leg (kg):", min_value=3.0, max_value=25.0, value=8.5, step=0.1)
                else:
                    right_leg_lbs = st.number_input("Right Leg (lbs):", min_value=6.6, max_value=55.0, value=18.7, step=0.2)
                    right_leg = lbs_to_kg(right_leg_lbs)
            
            # Calculate total ALM and ALMI
            total_alm = calculate_alm_from_limbs(left_arm, right_arm, left_leg, right_leg)
            current_metric = calculate_almi_from_alm(total_alm, height_m)
            
            limb_data = {
                'left_arm': left_arm,
                'right_arm': right_arm,
                'left_leg': left_leg,
                'right_leg': right_leg
            }
            
            st.info(f"Calculated ALMI: {current_metric:.2f} kg/m² (Total ALM: {total_alm:.1f} kg)")
        
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
                estimated_alm = ffm * 0.75  # ALM is ~75% of FFM
                current_metric = calculate_almi_from_alm(estimated_alm, height_m)
                
                # Estimate limb distribution
                limb_data = {
                    'left_arm': estimated_alm * 0.23,
                    'right_arm': estimated_alm * 0.25,
                    'left_leg': estimated_alm * 0.25,
                    'right_leg': estimated_alm * 0.27
                }
                st.info(f"Estimated ALMI: {current_metric:.2f} kg/m² (ALM ≈ 75% of FFM)")
            else:
                current_metric = calculate_ffmi_from_weight_bf(weight_kg, body_fat_pct, height_m)
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
        
        target_method = st.radio("Analysis type:", ["Specific Target", "Percentile Goals", "Visual Analysis"])
        
        if target_method == "Specific Target":
            if calc_type == "ALMI":
                target_metric = st.number_input(f"Target ALMI (kg/m²):", 
                                              min_value=3.0, max_value=15.0, 
                                              value=7.5, step=0.1)
            else:
                target_metric = st.number_input(f"Target FFMI (kg/m²):", 
                                              min_value=10.0, max_value=30.0, 
                                              value=20.0, step=0.1)
            
            # Calculate mass needed
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
        
        elif target_method == "Percentile Goals":
            percentiles = get_percentile_targets(gender, calc_type)
            
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
                
                # Create percentile visualization
                if st.button("Generate Percentile Chart"):
                    target_value = percentiles["75th percentile"]  # Default to 75th percentile
                    fig = create_percentile_visualization(current_metric, target_value, gender, calc_type)
                    st.pyplot(fig)
                    plt.close()
        
        elif target_method == "Visual Analysis":
            if limb_data and st.button("Generate Limb Analysis"):
                fig = create_limb_composition_chart(
                    limb_data['left_arm'], limb_data['right_arm'], 
                    limb_data['left_leg'], limb_data['right_leg'], 
                    unit_system
                )
                st.pyplot(fig)
                plt.close()
        
        # DEXA Report Generation
        st.subheader("Generate DEXA-Style Report")
        
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Patient Name:", value="John Doe")
            patient_dob = st.date_input("Date of Birth:", value=datetime(1990, 1, 1))
        
        with col2:
            if st.button("Generate DEXA Report"):
                if current_metric and limb_data:
                    # Prepare patient data
                    patient_data = {
                        'name': patient_name,
                        'dob': patient_dob.strftime("%m/%d/%Y"),
                        'height_m': height_m,
                        'height_cm': height_cm if unit_system == "Metric" else height_in * 2.54,
                        'height_in': height_in if unit_system == "English" else height_cm / 2.54
                    }
                    
                    # Prepare scan data
                    if not scan_data:  # If not from weight/BF input
                        scan_data = {
                            'weight': 70.0,  # Default values
                            'body_fat': 15.0,
                            'alm': sum(limb_data.values()) if limb_data else calculate_alm_from_almi(current_metric, height_m),
                            'left_arm': limb_data['left_arm'],
                            'right_arm': limb_data['right_arm'],
                            'left_leg': limb_data['left_leg'],
                            'right_leg': limb_data['right_leg']
                        }
                    
                    # Generate HTML report
                    html_report = generate_dexa_report_html(patient_data, scan_data, unit_system)
                    
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
            if gender == "Male":
                st.caption("Male ALMI reference: Normal ≥ 7.0 kg/m², Low < 7.0 kg/m²")
            else:
                st.caption("Female ALMI reference: Normal ≥ 5.5 kg/m², Low < 5.5 kg/m²")
        else:
            if gender == "Male":
                st.caption("Male FFMI reference: Average 16.7-19.8 kg/m², Athletic >20 kg/m², Elite 22-25 kg/m²")
            else:
                st.caption("Female FFMI reference: Average 14.6-16.8 kg/m², Athletic >17 kg/m²")

if __name__ == "__main__":
    main()