import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from grimore_test import predict_weight_loss, calculate_lean_mass_preservation_scores, get_body_fat_info, estimate_tef, estimate_neat, calculate_metabolic_adaptation
from fpdf import FPDF

# Function to calculate age
def calculate_age(dob, current_date):
    return current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))

# Set page configuration
st.set_page_config(page_title="Weight Loss Predictor", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    body {
        color: #FFFF00;
        background-color: #000000;
    }
    .stButton > button {
        color: #000000;
        background-color: #FFFF00;
    }
    .stSelectbox > div > div {
        color: #FFFF00;
        background-color: #1A1A1A;
    }
    .stTextInput > div > div > input {
        color: #FFFF00;
        background-color: #1A1A1A;
    }
    .stNumberInput > div > div > input {
        color: #FFFF00;
        background-color: #1A1A1A;
    }
    .stDateInput > div > div > input {
        color: #FFFF00;
        background-color: #1A1A1A;
    }
    </style>
    """, unsafe_allow_html=True)

# PDF generation function
class PDF(FPDF):
    def header(self):
        self.set_font('Times', 'B', 15)
        self.set_text_color(0, 0, 0)  # Black
        self.cell(0, 10, 'Weight Loss Plan Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.set_text_color(0, 0, 0)  # Black
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(progression, initial_data, gender, client_name):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 10, "YOUR PERSONALIZED WEIGHT LOSS JOURNEY REPORT", 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Dear {client_name},", 0, 1, "L")
    pdf.cell(0, 10, "We've analyzed your data using our advanced weight loss prediction model.", 0, 1, "L")
    pdf.cell(0, 10, "Here's a comprehensive breakdown of your journey:", 0, 1, "L")
    pdf.ln(5)

    # Personal Profile
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "1. PERSONAL PROFILE", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Start Date: {progression[0]['date']}", 0, 1)
    pdf.cell(0, 10, f"End Date: {progression[-1]['date']}", 0, 1)
    pdf.cell(0, 10, f"Age: {calculate_age(initial_data['dob'], datetime.strptime(progression[0]['date'], '%m%d%y'))} years", 0, 1)
    pdf.cell(0, 10, f"Gender: {gender.upper()}", 0, 1)
    pdf.cell(0, 10, f"Height: {initial_data['height_feet']}'{initial_data['height_inches']}\" ({initial_data['height_cm']:.1f} cm)", 0, 1)
    pdf.cell(0, 10, f"Initial Weight: {progression[0]['weight']:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Goal Weight: {initial_data['goal_weight']:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Initial Body Fat: {progression[0]['body_fat_percentage']:.1f}%", 0, 1)
    pdf.cell(0, 10, f"Goal Body Fat: {initial_data['goal_bf']:.1f}%", 0, 1)
    pdf.cell(0, 10, f"Activity Level: {initial_data['activity_level_description']}", 0, 1)
    pdf.cell(0, 10, f"Experience Level: {initial_data['experience_level']}", 0, 1)
    pdf.ln(5)

    # Metabolic Calculations
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "2. METABOLIC CALCULATIONS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Initial Resting Metabolic Rate (RMR): {progression[0]['rmr']:.0f} calories/day", 0, 1)
    pdf.cell(0, 10, f"Initial Total Daily Energy Expenditure (TDEE): {progression[0]['tdee']:.0f} calories/day", 0, 1)
    pdf.cell(0, 10, f"Thermic Effect of Food (TEF): {estimate_tef(initial_data['protein_intake']):.0f} calories/day", 0, 1)
    pdf.cell(0, 10, f"Non-Exercise Activity Thermogenesis (NEAT): {estimate_neat(initial_data['job_activity'], initial_data['leisure_activity']):.0f} calories/day", 0, 1)
    pdf.cell(0, 10, f"Initial Daily Calorie Intake: {progression[0]['daily_calorie_intake']:.0f} calories/day", 0, 1)
    pdf.ln(5)

    # Workout Analysis
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "3. WORKOUT ANALYSIS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Workout Type: {initial_data['workout_type']}", 0, 1)
    pdf.cell(0, 10, f"Workout Frequency: {initial_data['workout_days']} days/week", 0, 1)
    pdf.cell(0, 10, f"Volume Score: {initial_data['volume_score']:.2f}", 0, 1)
    pdf.cell(0, 10, f"Intensity Score: {initial_data['intensity_score']:.2f}", 0, 1)
    pdf.cell(0, 10, f"Frequency Score: {initial_data['frequency_score']:.2f}", 0, 1)
    pdf.cell(0, 10, f"Resistance Training: {'Yes' if initial_data['resistance_training'] else 'No'}", 0, 1)
    pdf.cell(0, 10, f"Athlete Status: {'Yes' if initial_data['is_athlete'] else 'No'}", 0, 1)
    pdf.ln(5)

    # Body Composition Adjustments
    initial_lean_mass = progression[0]['weight'] * (1 - progression[0]['body_fat_percentage'] / 100)
    initial_fat_mass = progression[0]['weight'] * (progression[0]['body_fat_percentage'] / 100)
    estimated_muscle_gain = sum(entry['muscle_gain'] for entry in progression) / len(progression)

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "4. BODY COMPOSITION ADJUSTMENTS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Initial Lean Mass: {initial_lean_mass:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Initial Fat Mass: {initial_fat_mass:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Estimated Weekly Muscle Gain: {estimated_muscle_gain:.2f} lbs", 0, 1)
    pdf.ln(5)

    # Weekly Progress Summary
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "5. WEEKLY PROGRESS SUMMARY", 0, 1, "L")
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 10, "Week | Date | Weight (lbs) | Body Fat % | Daily Calories | TDEE | Weekly Cal Output | Total Weight Lost", 0, 1)
    pdf.cell(0, 10, "-" * 120, 0, 1)

    for i, entry in enumerate(progression):
        pdf.cell(0, 10, f"{i} | {entry['date']} | {entry['weight']:.1f} | {entry['body_fat_percentage']:.1f} | "
                         f"{entry['daily_calorie_intake']:.0f} | {entry['tdee']:.0f} | "
                         f"{entry['weekly_caloric_output']:.1f} | {entry['total_weight_lost']:.1f}", 0, 1)

    pdf.ln(5)

    # Metabolic Adaptation
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "6. METABOLIC ADAPTATION", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Week 1 Metabolic Adaptation: {calculate_metabolic_adaptation(1, progression[0]['body_fat_percentage'], initial_data['is_bodybuilder']):.2f}", 0, 1)
    pdf.cell(0, 10, f"Final Week Metabolic Adaptation: {calculate_metabolic_adaptation(len(progression) - 1, progression[-1]['body_fat_percentage'], initial_data['is_bodybuilder']):.2f}", 0, 1)
    pdf.ln(5)

    # Final Results
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "7. FINAL RESULTS", 0, 1, "L")
    pdf.set_font("Times", "", 12)

    total_weeks = len(progression) - 1
    total_weight_loss = progression[0]['weight'] - progression[-1]['weight']
    total_bf_loss = progression[0]['body_fat_percentage'] - progression[-1]['body_fat_percentage']
    total_muscle_gain = sum(entry['muscle_gain'] for entry in progression)

    pdf.cell(0, 10, f"Duration: {total_weeks} weeks", 0, 1)
    pdf.cell(0, 10, f"Total Weight Loss: {total_weight_loss:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Total Body Fat Reduction: {total_bf_loss:.1f}%", 0, 1)
    pdf.cell(0, 10, f"Final Weight: {progression[-1]['weight']:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Final Body Fat: {progression[-1]['body_fat_percentage']:.1f}%", 0, 1)
    pdf.cell(0, 10, f"Average Weekly Weight Loss: {total_weight_loss / total_weeks:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Total Muscle Gain: {total_muscle_gain:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Final Daily Calorie Intake: {progression[-1]['daily_calorie_intake']:.0f} calories", 0, 1)
    pdf.cell(0, 10, f"Final TDEE: {progression[-1]['tdee']:.0f} calories", 0, 1)
    pdf.cell(0, 10, f"Final Weekly Caloric Output: {progression[-1]['weekly_caloric_output']:.1f} calories", 0, 1)
    pdf.ln(5)

    # Body Fat Category Progression
    initial_category, initial_time, initial_description = get_body_fat_info(gender, progression[0]['body_fat_percentage'])
    final_category, final_time, final_description = get_body_fat_info(gender, progression[-1]['body_fat_percentage'])

    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "8. BODY FAT CATEGORY PROGRESSION", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Initial Category: {initial_category}", 0, 1)
    pdf.cell(0, 10, f"   Description: {initial_description}", 0, 1)
    pdf.cell(0, 10, f"   Estimated Time to Six-Pack: {initial_time}", 0, 1)
    pdf.cell(0, 10, "", 0, 1)  # Empty line
    pdf.cell(0, 10, f"Final Category: {final_category}", 0, 1)
    pdf.cell(0, 10, f"   Description: {final_description}", 0, 1)
    pdf.cell(0, 10, f"   Estimated Time to Six-Pack: {final_time}", 0, 1)
    pdf.ln(5)

    # Insights and Recommendations
    adaptation_percentage = ((progression[0]['tdee'] - progression[-1]['tdee']) / progression[0]['tdee']) * 100
    lean_mass_preserved = (progression[-1]['lean_mass'] / progression[0]['lean_mass']) * 100
    avg_muscle_gain = total_muscle_gain / total_weeks
    
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "9. INSIGHTS AND RECOMMENDATIONS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"• Your metabolic rate adapted by {adaptation_percentage:.1f}% over the course of your journey.", 0, 1)
    pdf.cell(0, 10, f"• You maintained an impressive {lean_mass_preserved:.1f}% of your initial lean mass.", 0, 1)
    pdf.cell(0, 10, f"• Your muscle gain rate averaged {avg_muscle_gain:.3f} lbs per week.", 0, 1)
    pdf.cell(0, 10, f"• Based on your final body fat percentage, you're now in the {final_category} category.", 0, 1)
    pdf.cell(0, 10, f"• To maintain your results, consider a daily calorie intake of {progression[-1]['tdee']:.0f} calories.", 0, 1)
    pdf.ln(5)

    # Next Steps
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "10. NEXT STEPS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, "• Continue to monitor your progress daily and adjust your nutrition as needed.", 0, 1)
    pdf.cell(0, 10, "• Consider adjusting your protein intake to meet your increased caloric expenditure.", 0, 1)
    pdf.cell(0, 10, "• Set new goals as you meet your targets!", 0, 1)
    pdf.ln(5)

    pdf.cell(0, 10, "Remember, this journey is a marathon, not a sprint. Celebrate your progress and stay committed to your health and fitness goals!", 0, 1, "C")

    pdf.cell(0, 10, "======================================================", 0, 1, "C")
    pdf.cell(0, 10, "                 Powered by Advanced AI Analytics", 0, 1, "C")
    pdf.cell(0, 10, "======================================================", 0, 1, "C")

    return pdf.output(dest='S').encode('latin-1')

# Main app
st.title("Weight Loss Predictor")

# Personal Information Section
st.header("Personal Information")
col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    gender = st.selectbox("Gender", ["M", "F"])
with col2:
    dob = st.date_input("Date of Birth", min_value=datetime.now().date() - timedelta(days=36500), max_value=datetime.now().date())
    feet = st.number_input("Height (feet)", min_value=0, max_value=8)
    inches = st.number_input("Height (inches)", min_value=0, max_value=11)
    height_cm = (feet * 12 + inches) * 2.54

# Current Stats and Goals Section
st.header("Current Stats and Goals")
col1, col2 = st.columns(2)
with col1:
    current_weight = st.number_input("Current Weight (lbs)", min_value=0.0)
    current_bf = st.number_input("Current Body Fat %", min_value=0.0, max_value=100.0)
    start_date = st.date_input("Start Date", min_value=datetime.now().date())
with col2:
    goal_weight = st.number_input("Goal Weight (lbs)", min_value=0.0)
    goal_bf = st.number_input("Goal Body Fat %", min_value=0.0, max_value=100.0)