def generate_bmd_report_html(patient_data, bmd_data, unit_system):
    """Generate a BMD-focused DEXA report HTML"""
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMD Analysis Report - {patient_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Lato', sans-serif; background-color: #f7f7f5; }}
        h1, h2, h3, h4 {{ font-family: 'Cormorant Garamond', serif; color: #06121B; }}
        .chart-line {{ stroke-dasharray: 1000; stroke-dashoffset: 1000; animation: dash 2s ease-out forwards; }}
        @keyframes dash {{ to {{ stroke-dashoffset: 0; }} }}
    </style>
</head>
<body class="p-4 sm:p-6 lg:p-8">
    <div class="max-w-7xl mx-auto space-y-8 bg-white rounded-2xl p-6 shadow-lg">
        <header class="text-center border-b border-gray-200 pb-6">
            <h1 class="text-4xl font-bold text-gray-800 tracking-wide">Bone Mineral Density Analysis</h1>
            <p class="text-xl text-gray-600 mt-2">{patient_name}</p>
            <div class="flex justify-center flex-wrap gap-x-6 gap-y-2 mt-2 text-gray-500">
                <span>DOB: {dob}</span>
                <span>Age: {age} years</span>
                <span>Height: {height}</span>
                <span>Exam Date: {exam_date}</span>
            </div>
        </header>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-3xl font-bold mb-6 text-center">Current BMD T-Scores</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="bmd-charts">
                <div class="bg-white rounded-xl shadow-md p-4">
                    <h4 class="text-xl font-semibold text-center mb-4">Left Femur BMD (T-score)</h4>
                    <div class="flex items-center justify-center space-x-4">
                        <div class="flex flex-col justify-between text-right text-xs text-gray-500 h-80">
                            <div>4</div><div>3</div><div>2</div><div>1</div><div>0</div>
                            <div>-1</div><div>-2</div><div>-3</div><div>-4</div>
                        </div>
                        <div class="relative w-20 rounded-lg overflow-hidden border-2 border-gray-300 h-80">
                            <div class="absolute w-full bg-red-400 opacity-70" style="bottom: 0%; height: 12.5%;"></div>
                            <div class="absolute w-full bg-orange-400 opacity-70" style="bottom: 12.5%; height: 18.75%;"></div>
                            <div class="absolute w-full bg-blue-400 opacity-70" style="bottom: 31.25%; height: 37.5%;"></div>
                            <div class="absolute w-full bg-blue-600 opacity-70" style="bottom: 68.75%; height: 31.25%;"></div>
                            <div class="absolute w-full h-1 bg-slate-800 border-t-2 border-b-2 border-white" 
                                 style="bottom: {left_femur_position}%; transform: translateY(50%);">
                                <div class="absolute right-full top-1/2 -translate-y-1/2 mr-2 px-2 py-0.5 bg-slate-800 text-white text-xs font-bold rounded">
                                    {left_femur_t:.1f}
                                </div>
                            </div>
                        </div>
                        <div class="flex flex-col justify-around h-80">
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-blue-600 opacity-70"></div>
                                <span class="text-xs text-gray-600">High Density</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-blue-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Normal</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-orange-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Osteopenia</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-red-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Osteoporosis</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-xl shadow-md p-4">
                    <h4 class="text-xl font-semibold text-center mb-4">Right Femur BMD (T-score)</h4>
                    <div class="flex items-center justify-center space-x-4">
                        <div class="flex flex-col justify-between text-right text-xs text-gray-500 h-80">
                            <div>4</div><div>3</div><div>2</div><div>1</div><div>0</div>
                            <div>-1</div><div>-2</div><div>-3</div><div>-4</div>
                        </div>
                        <div class="relative w-20 rounded-lg overflow-hidden border-2 border-gray-300 h-80">
                            <div class="absolute w-full bg-red-400 opacity-70" style="bottom: 0%; height: 12.5%;"></div>
                            <div class="absolute w-full bg-orange-400 opacity-70" style="bottom: 12.5%; height: 18.75%;"></div>
                            <div class="absolute w-full bg-blue-400 opacity-70" style="bottom: 31.25%; height: 37.5%;"></div>
                            <div class="absolute w-full bg-blue-600 opacity-70" style="bottom: 68.75%; height: 31.25%;"></div>
                            <div class="absolute w-full h-1 bg-slate-800 border-t-2 border-b-2 border-white" 
                                 style="bottom: {right_femur_position}%; transform: translateY(50%);">
                                <div class="absolute right-full top-1/2 -translate-y-1/2 mr-2 px-2 py-0.5 bg-slate-800 text-white text-xs font-bold rounded">
                                    {right_femur_t:.1f}
                                </div>
                            </div>
                        </div>
                        <div class="flex flex-col justify-around h-80">
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-blue-600 opacity-70"></div>
                                <span class="text-xs text-gray-600">High Density</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-blue-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Normal</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-orange-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Osteopenia</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-red-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Osteoporosis</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-xl shadow-md p-4">
                    <h4 class="text-xl font-semibold text-center mb-4">Lumbar Spine BMD (T-score)</h4>
                    <div class="flex items-center justify-center space-x-4">
                        <div class="flex flex-col justify-between text-right text-xs text-gray-500 h-80">
                            <div>4</div><div>3</div><div>2</div><div>1</div><div>0</div>
                            <div>-1</div><div>-2</div><div>-3</div><div>-4</div>
                        </div>
                        <div class="relative w-20 rounded-lg overflow-hidden border-2 border-gray-300 h-80">
                            <div class="absolute w-full bg-red-400 opacity-70" style="bottom: 0%; height: 12.5%;"></div>
                            <div class="absolute w-full bg-orange-400 opacity-70" style="bottom: 12.5%; height: 18.75%;"></div>
                            <div class="absolute w-full bg-blue-400 opacity-70" style="bottom: 31.25%; height: 37.5%;"></div>
                            <div class="absolute w-full bg-blue-600 opacity-70" style="bottom: 68.75%; height: 31.25%;"></div>
                            <div class="absolute w-full h-1 bg-slate-800 border-t-2 border-b-2 border-white" 
                                 style="bottom: {spine_position}%; transform: translateY(50%);">
                                <div class="absolute right-full top-1/2 -translate-y-1/2 mr-2 px-2 py-0.5 bg-slate-800 text-white text-xs font-bold rounded">
                                    {spine_t:.1f}
                                </div>
                            </div>
                        </div>
                        <div class="flex flex-col justify-around h-80">
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-blue-600 opacity-70"></div>
                                <span class="text-xs text-gray-600">High Density</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-blue-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Normal</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-orange-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Osteopenia</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 rounded-full bg-red-400 opacity-70"></div>
                                <span class="text-xs text-gray-600">Osteoporosis</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-3xl font-bold mb-6 text-center">BMD Summary & Interpretation</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div class="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">Left Femur</h3>
                    <p class="text-3xl font-bold text-blue-600">{left_femur_t:.1f}</p>
                    <p class="text-sm text-gray-600">{left_femur_status}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">Right Femur</h3>
                    <p class="text-3xl font-bold text-green-600">{right_femur_t:.1f}</p>
                    <p class="text-sm text-gray-600">{right_femur_status}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">Lumbar Spine</h3>
                    <p class="text-3xl font-bold text-purple-600">{spine_t:.1f}</p>
                    <p class="text-sm text-gray-600">{spine_status}</p>
                </div>
            </div>
            
            <div class="bg-gray-50 rounded-lg p-6">
                <h3 class="text-xl font-semibold mb-4">Clinical Interpretation</h3>
                <div class="space-y-3 text-gray-700">
                    <p><strong>Overall Assessment:</strong> {overall_assessment}</p>
                    <p><strong>T-Score Interpretation:</strong></p>
                    <ul class="list-disc list-inside ml-4 space-y-1">
                        <li><strong>Normal:</strong> T-score of -1.0 or above</li>
                        <li><strong>Osteopenia (Low bone mass):</strong> T-score between -1.0 and -2.5</li>
                        <li><strong>Osteoporosis:</strong> T-score of -2.5 or below</li>
                    </ul>
                    <p><strong>Recommendations:</strong> {recommendations}</p>
                </div>
            </div>
        </section>

        <footer class="text-center text-sm text-gray-500 pt-8 mt-8 border-t border-gray-200">
            <p>&copy; 2025 BMD Analysis Report. All Rights Reserved.</p>
            <p class="text-xs mt-1">Disclaimer: This is a visualization of BMD data and not a medical diagnosis. Consult with your healthcare provider.</p>
        </footer>
    </div>
</body>
</html>"""
    
    # Calculate positions for BMD indicators (T-score range -4 to 4)
    def calc_position(t_score):
        return ((t_score + 4) / 8) * 100
    
    # Determine status based on T-score
    def get_bmd_status(t_score):
        if t_score >= -1.0:
            return "Normal"
        elif t_score >= -2.5:
            return "Osteopenia"
        else:
            return "Osteoporosis"
    
    # Calculate overall assessment
    scores = [bmd_data['left_femur_t'], bmd_data['right_femur_t'], bmd_data['spine_t']]
    min_score = min(scores)
    avg_score = sum(scores) / len(scores)
    
    if min_score >= -1.0:
        overall_assessment = "Excellent bone health with normal bone density at all measured sites."
        recommendations = "Continue current lifestyle with adequate calcium, vitamin D, and weight-bearing exercise."
    elif min_score >= -2.5:
        overall_assessment = "Mild bone loss (osteopenia) detected. Early intervention recommended."
        recommendations = "Increase weight-bearing exercise, ensure adequate calcium/vitamin D intake, consider lifestyle modifications."
    else:
        overall_assessment = "Osteoporosis detected. Medical evaluation and treatment planning recommended."
        recommendations = "Consult with physician for comprehensive osteoporosis management including medication evaluation."
    
    # Format the HTML
    formatted_html = html_template.format(
        patient_name=patient_data['name'],
        dob=patient_data['dob'],
        age=patient_data['age'],
        height=patient_data['height_display'],
        exam_date=datetime.now().strftime("%m/%d/%Y"),
        left_femur_t=bmd_data['left_femur_t'],
        right_femur_t=bmd_data['right_femur_t'],
        spine_t=bmd_data['spine_t'],
        left_femur_position=calc_position(bmd_data['left_femur_t']),
        right_femur_position=calc_position(bmd_data['right_femur_t']),
        spine_position=calc_position(bmd_data['spine_t']),
        left_femur_status=get_bmd_status(bmd_data['left_femur_t']),
        right_femur_status=get_bmd_status(bmd_data['right_femur_t']),
        spine_status=get_bmd_status(bmd_data['spine_t']),
        overall_assessment=overall_assessment,
        recommendations=recommendations
    )
    
    return formatted_html

def generate_body_comp_report_html(patient_data, body_comp_data, goals_data, unit_system):
    """Generate a comprehensive body composition report HTML"""
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Body Composition Analysis - {patient_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Lato', sans-serif; background-color: #f7f7f5; }}
        h1, h2, h3, h4 {{ font-family: 'Cormorant Garamond', serif; color: #06121B; }}
    </style>
</head>
<body class="p-4 sm:p-6 lg:p-8">
    <div class="max-w-7xl mx-auto space-y-8 bg-white rounded-2xl p-6 shadow-lg">
        <header class="text-center border-b border-gray-200 pb-6">
            <h1 class="text-4xl font-bold text-gray-800 tracking-wide">Body Composition Analysis</h1>
            <p class="text-xl text-gray-600 mt-2">{patient_name}</p>
            <div class="flex justify-center flex-wrap gap-x-6 gap-y-2 mt-2 text-gray-500">
                <span>DOB: {dob}</span>
                <span>Age: {age} years</span>
                <span>Gender: {gender}</span>
                <span>Exam Date: {exam_date}</span>
            </div>
        </header>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-3xl font-bold mb-6 text-center">Current Body Composition</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                <div class="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">Height</h3>
                    <p class="text-2xl font-bold text-blue-600">{height}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">Weight</h3>
                    <p class="text-2xl font-bold text-green-600">{weight}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">BMI</h3>
                    <p class="text-2xl font-bold text-purple-600">{bmi:.1f}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-red-50 to-red-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">Total Body Fat</h3>
                    <p class="text-2xl font-bold text-red-600">{body_fat:.1f}%</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="text-center p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">VAT Mass</h3>
                    <p class="text-2xl font-bold text-indigo-600">{vat_mass:.0f}g</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-teal-50 to-teal-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">Total ALM</h3>
                    <p class="text-2xl font-bold text-teal-600">{alm:.1f} {weight_unit}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">ALMI</h3>
                    <p class="text-2xl font-bold text-yellow-600">{almi:.2f}</p>
                    <p class="text-xs text-gray-500">kg/m²</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg">
                    <h3 class="text-lg font-semibold text-gray-700">FFMI</h3>
                    <p class="text-2xl font-bold text-pink-600">{ffmi:.1f}</p>
                    <p class="text-xs text-gray-500">kg/m²</p>
                </div>
            </div>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-3xl font-bold mb-6 text-center">Limb-Specific Lean Mass</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Left Arm</h4>
                    <p class="text-xl font-bold text-blue-600">{left_arm:.1f} {weight_unit}</p>
                    <p class="text-sm text-gray-500">{left_arm_pct:.1f}% of ALM</p>
                </div>
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Right Arm</h4>
                    <p class="text-xl font-bold text-blue-600">{right_arm:.1f} {weight_unit}</p>
                    <p class="text-sm text-gray-500">{right_arm_pct:.1f}% of ALM</p>
                </div>
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Left Leg</h4>
                    <p class="text-xl font-bold text-green-600">{left_leg:.1f} {weight_unit}</p>
                    <p class="text-sm text-gray-500">{left_leg_pct:.1f}% of ALM</p>
                </div>
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-700">Right Leg</h4>
                    <p class="text-xl font-bold text-green-600">{right_leg:.1f} {weight_unit}</p>
                    <p class="text-sm text-gray-500">{right_leg_pct:.1f}% of ALM</p>
                </div>
            </div>
            
            <div class="mt-6 bg-gray-50 rounded-lg p-4">
                <h4 class="font-semibold text-gray-700 mb-2">Symmetry Analysis</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="text-center">
                        <p class="text-sm text-gray-600">Arm Asymmetry</p>
                        <p class="text-lg font-bold {arm_color}">{arm_asymmetry:.1f}%</p>
                    </div>
                    <div class="text-center">
                        <p class="text-sm text-gray-600">Leg Asymmetry</p>
                        <p class="text-lg font-bold {leg_color}">{leg_asymmetry:.1f}%</p>
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-2">*Asymmetry >10% may indicate muscle imbalance</p>
            </div>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-3xl font-bold mb-6 text-center">Percentile Analysis & Goals</h2>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6">
                    <h3 class="text-xl font-semibold mb-4 text-center">ALMI Goals</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-sm font-medium">Current ALMI:</span>
                            <span class="font-bold text-blue-600">{almi:.2f} kg/m²</span>
                        </div>
                        <div class="space-y-2">
                            {almi_goals}
                        </div>
                    </div>
                </div>
                
                <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6">
                    <h3 class="text-xl font-semibold mb-4 text-center">FFMI Goals</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-sm font-medium">Current FFMI:</span>
                            <span class="font-bold text-green-600">{ffmi:.1f} kg/m²</span>
                        </div>
                        <div class="space-y-2">
                            {ffmi_goals}
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-3xl font-bold mb-6 text-center">Recommended Actions</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-yellow-50 rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4 text-yellow-800">Priority Goals</h3>
                    <ul class="space-y-2 text-sm text-yellow-700">
                        {priority_goals}
                    </ul>
                </div>
                <div class="bg-green-50 rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4 text-green-800">Recommendations</h3>
                    <ul class="space-y-2 text-sm text-green-700">
                        {recommendations}
                    </ul>
                </div>
            </div>
        </section>

        <footer class="text-center text-sm text-gray-500 pt-8 mt-8 border-t border-gray-200">
            <p>&copy; 2025 Body Composition Analysis. All Rights Reserved.</p>
            <p class="text-xs mt-1">Disclaimer: This analysis is for informational purposes and not a substitute for medical advice.</p>
        </footer>
    </div>
</body>
</html>"""
    
    # Calculate derived metrics
    weight_unit = "lbs" if unit_system == "English" else "kg"
    heightimport streamlit as st
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
    colors = ['#267DFF', '#66A3FF', '#F3817D', '#DA5955']
    
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
    arm_symmetry = abs(limb_masses[0] - limb_masses[1]) / max(limb_masses[0], limb_masses[1]) * 100
    leg_symmetry = abs(limb_masses[2] - limb_masses[3]) / max(limb_masses[2], limb_masses[3]) * 100
    
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
    
    # Add percentile bars
    colors = ['#DA5955', '#F3817D', '#757575', '#66A3FF', '#267DFF']
    
    fig.add_trace(go.Bar(
        x=percentile_names,
        y=percentile_values,
        name='Percentiles',
        marker_color=colors,
        text=[f'{val:.1f}' for val in percentile_values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>%{y:.1f} kg/m²<extra></extra>'
    ))
    
    # Add current value line
    fig.add_hline(
        y=current_metric,
        line_dash="dash",
        line_color="red",
        line_width=3,
        annotation_text=f"Current: {current_metric:.1f}",
        annotation_position="top right"
    )
    
    # Add target value line
    fig.add_hline(
        y=target_metric,
        line_dash="dash",
        line_color="green",
        line_width=3,
        annotation_text=f"Target: {target_metric:.1f}",
        annotation_position="bottom right"
    )
    
    # Update layout
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
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    
    # Update axes
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.1)')
    
    return fig

def create_progress_timeline_chart(timeline_data, unit_system):
    """Create timeline visualization for lean mass gain progress"""
    
    weight_unit = "lbs" if unit_system == "English" else "kg"
    
    fig = go.Figure()
    
    # Extract data
    experience_levels = [item['experience'] for item in timeline_data]
    monthly_rates = [item['monthly_rate_kg'] for item in timeline_data]
    timelines_months = [item['timeline_months'] for item in timeline_data]
    
    # Convert to display units if needed
    if unit_system == "English":
        monthly_rates_display = [kg_to_lbs(rate) for rate in monthly_rates]
    else:
        monthly_rates_display = monthly_rates
    
    # Create bar chart for monthly rates
    fig.add_trace(go.Bar(
        x=experience_levels,
        y=monthly_rates_display,
        name=f'Monthly Rate ({weight_unit})',
        marker_color=['#267DFF', '#66A3FF', '#F3817D'],
        text=[f'{rate:.2f}' for rate in monthly_rates_display],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>%{y:.2f} ' + weight_unit + '/month<br>Timeline: %{customdata:.1f} months<extra></extra>',
        customdata=timelines_months
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='Realistic Lean Mass Gain Timeline',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#1f2937')
        ),
        xaxis_title="Experience Level",
        yaxis_title=f"Monthly Gain Rate ({weight_unit})",
        height=400,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    
    # Update axes
    fig.update_xaxes(tickangle=0)
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.1)')
    
    return fig

    # Calculate derived metrics
    weight_unit = "lbs" if unit_system == "English" else "kg"
    height_m = patient_data['height_m']
    
    # Display values in appropriate units
    if unit_system == "English":
        weight_display = f"{kg_to_lbs(body_comp_data['weight']):.1f} lbs"
        height_display = f"{m_to_inches(height_m):.1f} in"
        alm_display = kg_to_lbs(body_comp_data['alm'])
        left_arm_display = kg_to_lbs(body_comp_data['left_arm'])
        right_arm_display = kg_to_lbs(body_comp_data['right_arm'])
        left_leg_display = kg_to_lbs(body_comp_data['left_leg'])
        right_leg_display = kg_to_lbs(body_comp_data['right_leg'])
    else:
        weight_display = f"{body_comp_data['weight']:.1f} kg"
        height_display = f"{height_m * 100:.1f} cm"
        alm_display = body_comp_data['alm']
        left_arm_display = body_comp_data['left_arm']
        right_arm_display = body_comp_data['right_arm']
        left_leg_display = body_comp_data['left_leg']
        right_leg_display = body_comp_data['right_leg']
    
    # Calculate BMI
    bmi = body_comp_data['weight'] / (height_m ** 2)
    
    # Calculate percentages of ALM
    total_alm = body_comp_data['alm']
    left_arm_pct = (body_comp_data['left_arm'] / total_alm) * 100
    right_arm_pct = (body_comp_data['right_arm'] / total_alm) * 100
    left_leg_pct = (body_comp_data['left_leg'] / total_alm) * 100
    right_leg_pct = (body_comp_data['right_leg'] / total_alm) * 100
    
    # Calculate asymmetries
    arm_asymmetry = abs(body_comp_data['left_arm'] - body_comp_data['right_arm']) / max(body_comp_data['left_arm'], body_comp_data['right_arm']) * 100
    leg_asymmetry = abs(body_comp_data['left_leg'] - body_comp_data['right_leg']) / max(body_comp_data['left_leg'], body_comp_data['right_leg']) * 100
    
    # Color coding for asymmetries
    arm_color = "text-red-600" if arm_asymmetry > 10 else "text-green-600"
    leg_color = "text-red-600" if leg_asymmetry > 10 else "text-green-600"
    
    # Generate ALMI goals
    almi_goals_html = ""
    current_almi = body_comp_data['almi']
    for percentile, target_almi in goals_data['almi_targets'].items():
        current_mass = calculate_alm_from_almi(current_almi, height_m)
        target_mass = calculate_alm_from_almi(target_almi, height_m)
        mass_needed = max(0, target_mass - current_mass)
        
        if mass_needed == 0:
            status = "✅ Achieved"
            status_color = "text-green-600"
        else:
            if unit_system == "English":
                status = f"Need +{kg_to_lbs(mass_needed):.1f} lbs"
            else:
                status = f"Need +{mass_needed:.1f} kg"
            status_color = "text-orange-600"
        
        almi_goals_html += f"""
        <div class="flex justify-between items-center py-1">
            <span class="text-sm">{percentile}:</span>
            <div class="text-right">
                <span class="text-sm font-medium">{target_almi:.1f} kg/m²</span>
                <span class="block text-xs {status_color}">{status}</span>
            </div>
        </div>"""
    
    # Generate FFMI goals
    ffmi_goals_html = ""
    current_ffmi = body_comp_data['ffmi']
    for percentile, target_ffmi in goals_data['ffmi_targets'].items():
        current_mass = calculate_ffm_from_ffmi(current_ffmi, height_m)
        target_mass = calculate_ffm_from_ffmi(target_ffmi, height_m)
        mass_needed = max(0, target_mass - current_mass)
        
        if mass_needed == 0:
            status = "✅ Achieved"
            status_color = "text-green-600"
        else:
            if unit_system == "English":
                status = f"Need +{kg_to_lbs(mass_needed):.1f} lbs"
            else:
                status = f"Need +{mass_needed:.1f} kg"
            status_color = "text-orange-600"
        
        ffmi_goals_html += f"""
        <div class="flex justify-between items-center py-1">
            <span class="text-sm">{percentile}:</span>
            <div class="text-right">
                <span class="text-sm font-medium">{target_ffmi:.1f} kg/m²</span>
                <span class="block text-xs {status_color}">{status}</span>
            </div>
        </div>"""
    
    # Generate priority goals
    priority_goals_html = ""
    recommendations_html = ""
    
    # Determine priorities based on current metrics
    if current_almi < goals_data['almi_targets']['25th percentile']:
        priority_goals_html += "<li>• Increase appendicular lean mass to reach 25th percentile minimum</li>"
        recommendations_html += "<li>• Implement progressive resistance training 3-4x/week</li>"
        recommendations_html += "<li>• Ensure adequate protein intake (1.6-2.2g/kg body weight)</li>"
    
    if current_ffmi < goals_data['ffmi_targets']['50th percentile']:
        priority_goals_html += "<li>• Build total lean mass to reach median population levels</li>"
        recommendations_html += "<li>• Focus on compound movements (squats, deadlifts, presses)</li>"
    
    if body_comp_data['body_fat'] > 20 and patient_data['gender'] == 'Male':
        priority_goals_html += "<li>• Reduce body fat percentage for improved health</li>"
        recommendations_html += "<li>• Implement moderate caloric deficit with cardio</li>"
    elif body_comp_data['body_fat'] > 25 and patient_data['gender'] == 'Female':
        priority_goals_html += "<li>• Reduce body fat percentage for improved health</li>"
        recommendations_html += "<li>• Implement moderate caloric deficit with cardio</li>"
    
    if arm_asymmetry > 10 or leg_asymmetry > 10:
        priority_goals_html += "<li>• Address muscle imbalances between limbs</li>"
        recommendations_html += "<li>• Include unilateral exercises and corrective work</li>"
    
    if body_comp_data.get('vat_mass', 500) > 1000:
        priority_goals_html += "<li>• Reduce visceral adipose tissue for metabolic health</li>"
        recommendations_html += "<li>• Prioritize cardiovascular exercise and stress management</li>"
    
    # Default recommendations
    recommendations_html += "<li>• Schedule follow-up DEXA scan in 6-12 months</li>"
    recommendations_html += "<li>• Consider working with qualified fitness professional</li>"
    
    # Format the HTML
    formatted_html = html_template.format(
        patient_name=patient_data['name'],
        dob=patient_data['dob'],
        age=patient_data['age'],
        gender=patient_data['gender'],
        exam_date=datetime.now().strftime("%m/%d/%Y"),
        height=height_display,
        weight=weight_display,
        bmi=bmi,
        body_fat=body_comp_data['body_fat'],
        vat_mass=body_comp_data.get('vat_mass', 450),
        alm=alm_display,
        almi=current_almi,
        ffmi=current_ffmi,
        weight_unit=weight_unit,
        left_arm=left_arm_display,
        right_arm=right_arm_display,
        left_leg=left_leg_display,
        right_leg=right_leg_display,
        left_arm_pct=left_arm_pct,
        right_arm_pct=right_arm_pct,
        left_leg_pct=left_leg_pct,
        right_leg_pct=right_leg_pct,
        arm_asymmetry=arm_asymmetry,
        leg_asymmetry=leg_asymmetry,
        arm_color=arm_color,
        leg_color=leg_color,
        almi_goals=almi_goals_html,
        ffmi_goals=ffmi_goals_html,
        priority_goals=priority_goals_html,
        recommendations=recommendations_html
    )
    
    return formatted_html
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
            st.plotly_chart(fig, use_container_width=True)
            
            # Create timeline visualization
            if gender == "Male":
                rates_kg = [0.68, 0.34, 0.11]  # kg per month
            else:
                rates_kg = [0.34, 0.17, 0.06]  # kg per month
            
            timeline_data = []
            for i, (level, rate) in enumerate(zip(["Beginner (Year 1)", "Intermediate (Year 2-3)", "Advanced (Year 4+)"], rates_kg)):
                months = target_lean_gain / rate
                timeline_data.append({
                    'experience': level,
                    'monthly_rate_kg': rate,
                    'timeline_months': months
                })
            
            timeline_fig = create_progress_timeline_chart(timeline_data, unit_system)
            st.plotly_chart(timeline_fig, use_container_width=True)
    
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
                    st.plotly_chart(fig, use_container_width=True)
        
        elif target_method == "Visual Analysis":
            if limb_data and st.button("Generate Limb Analysis"):
                fig = create_limb_composition_chart(
                    limb_data['left_arm'], limb_data['right_arm'], 
                    limb_data['left_leg'], limb_data['right_leg'], 
                    unit_system
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # DEXA Report Generation
        st.subheader("Generate Professional Reports")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            patient_name = st.text_input("Patient Name:", value="John Doe")
        with col2:
            patient_dob = st.date_input("Date of Birth:", value=datetime(1990, 1, 1))
        with col3:
            report_type = st.selectbox("Report Type:", ["Body Composition Report", "BMD Analysis Report"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Report"):
                if current_metric and limb_data:
                    # Calculate age
                    age = (datetime.now() - datetime.combine(patient_dob, datetime.min.time())).days // 365
                    
                    # Prepare patient data
                    patient_data = {
                        'name': patient_name,
                        'dob': patient_dob.strftime("%m/%d/%Y"),
                        'age': age,
                        'gender': gender,
                        'height_m': height_m,
                        'height_display': height_display
                    }
                    
                    if report_type == "Body Composition Report":
                        # Prepare body composition data
                        if not scan_data:  # If not from weight/BF input
                            scan_data = {
                                'weight': 70.0,  # Default values - could be enhanced
                                'body_fat': 15.0,
                                'alm': sum(limb_data.values()) if limb_data else calculate_alm_from_almi(current_metric, height_m),
                                'almi': current_metric if calc_type == "ALMI" else calculate_almi_from_alm(sum(limb_data.values()), height_m),
                                'ffmi': current_metric if calc_type == "FFMI" else calculate_ffmi_from_weight_bf(70.0, 15.0, height_m),
                                'left_arm': limb_data['left_arm'],
                                'right_arm': limb_data['right_arm'],
                                'left_leg': limb_data['left_leg'],
                                'right_leg': limb_data['right_leg'],
                                'vat_mass': 450  # Default VAT mass
                            }
                        
                        # Prepare goals data
                        almi_targets = get_percentile_targets(gender, "ALMI")
                        ffmi_targets = get_percentile_targets(gender, "FFMI")
                        goals_data = {
                            'almi_targets': almi_targets,
                            'ffmi_targets': ffmi_targets
                        }
                        
                        # Generate body composition report
                        html_report = generate_body_comp_report_html(patient_data, scan_data, goals_data, unit_system)
                        
                    else:  # BMD Analysis Report
                        # Prepare BMD data (mock data for demonstration)
                        bmd_data = {
                            'left_femur_t': 1.2,   # Mock T-scores
                            'right_femur_t': 1.4,
                            'spine_t': 0.8
                        }
                        
                        # Generate BMD report
                        html_report = generate_bmd_report_html(patient_data, bmd_data, unit_system)
                    
                    # Store report in session state for download
                    st.session_state['generated_report'] = html_report
                    st.session_state['report_filename'] = f"{report_type.lower().replace(' ', '_')}_{patient_name.replace(' ', '_')}.html"
                    
                    st.success(f"{report_type} generated successfully!")
                else:
                    st.error("Please complete the body composition analysis first.")
        
        with col2:
            # Download button - only show if report exists
            if 'generated_report' in st.session_state:
                b64 = base64.b64encode(st.session_state['generated_report'].encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" download="{st.session_state["report_filename"]}">Download {report_type}</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # Preview button
                if st.button("Preview Report"):
                    with st.expander("Report Preview", expanded=True):
                        st.components.v1.html(st.session_state['generated_report'], height=600, scrolling=True)
        
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