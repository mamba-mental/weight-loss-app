import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from grimore_test import predict_weight_loss, calculate_lean_mass_preservation_scores, get_body_fat_info
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
        self.cell(0, 10, '======================================================', 0, 1, 'C')
        self.cell(0, 10, 'YOUR PERSONALIZED', 0, 1, 'C')
        self.cell(0, 10, 'WEIGHT LOSS JOURNEY REPORT', 0, 1, 'C')
        self.cell(0, 10, '======================================================', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.set_text_color(0, 0, 0)  # Black
        self.cell(0, 10, '======================================================', 0, 1, 'C')
        self.cell(0, 10, 'Powered by Advanced AI Analytics', 0, 1, 'C')
        self.cell(0, 10, '======================================================', 0, 1, 'C')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(progression, initial_data, gender, client_name):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Times", "", 12)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 10, f"Dear {client_name},", 0, 1)
    pdf.ln(5)
    pdf.multi_cell(0, 10, "We've analyzed your data using our advanced weight loss prediction model. Here's a comprehensive breakdown of your journey:")
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

    # Metabolic Calculations
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "2. METABOLIC CALCULATIONS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Initial Resting Metabolic Rate (RMR): {initial_data['initial_rmr']} calories/day", 0, 1)
    pdf.cell(0, 10, f"Initial Total Daily Energy Expenditure (TDEE): {initial_data['initial_tdee']} calories/day", 0, 1)
    pdf.cell(0, 10, f"Thermic Effect of Food (TEF): {initial_data['tef']} calories/day", 0, 1)
    pdf.cell(0, 10, f"Non-Exercise Activity Thermogenesis (NEAT): {initial_data['neat']} calories/day", 0, 1)
    pdf.cell(0, 10, f"Initial Daily Calorie Intake: {initial_data['initial_daily_calories']} calories/day", 0, 1)

    # Workout Analysis
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "3. WORKOUT ANALYSIS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Workout Type: {initial_data['workout_type']}", 0, 1)
    pdf.cell(0, 10, f"Workout Frequency: {initial_data['workout_days']} days/week", 0, 1)
    pdf.cell(0, 10, f"Volume Score: {initial_data['volume_score']}", 0, 1)
    pdf.cell(0, 10, f"Intensity Score: {initial_data['intensity_score']}", 0, 1)
    pdf.cell(0, 10, f"Frequency Score: {initial_data['frequency_score']}", 0, 1)
    pdf.cell(0, 10, f"Resistance Training: {'Yes' if initial_data['resistance_training'] else 'No'}", 0, 1)
    pdf.cell(0, 10, f"Athlete Status: {'Yes' if initial_data['is_athlete'] else 'No'}", 0, 1)

    # Body Composition Adjustments
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "4. BODY COMPOSITION ADJUSTMENTS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Initial Lean Mass: {initial_data['initial_lean_mass']} lbs", 0, 1)
    pdf.cell(0, 10, f"Initial Fat Mass: {initial_data['initial_fat_mass']} lbs", 0, 1)
    pdf.cell(0, 10, f"Estimated Weekly Muscle Gain: {initial_data['estimated_muscle_gain']} lbs", 0, 1)

    # Weekly Progress Summary
    pdf.add_page()
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "5. WEEKLY PROGRESS SUMMARY", 0, 1, "C")
    pdf.set_font("Times", "", 10)

    col_widths = [10, 20, 25, 25, 25, 25, 30, 30]
    headers = ["Week", "Date", "Weight (lbs)", "Body Fat %", "Daily Calories", "TDEE", "Weekly Cal Output", "Total Weight Lost"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1)
    pdf.ln()

    for i, entry in enumerate(progression):
        pdf.cell(col_widths[0], 10, str(i), 1)
        pdf.cell(col_widths[1], 10, entry['date'], 1)
        pdf.cell(col_widths[2], 10, f"{entry['weight']:.1f}", 1)
        pdf.cell(col_widths[3], 10, f"{entry['body_fat_percentage']:.1f}", 1)
        pdf.cell(col_widths[4], 10, f"{entry['daily_calorie_intake']:.0f}", 1)
        pdf.cell(col_widths[5], 10, f"{entry['tdee']:.0f}", 1)
        pdf.cell(col_widths[6], 10, f"{entry['weekly_caloric_output']:.1f}", 1)
        pdf.cell(col_widths[7], 10, f"{entry['total_weight_lost']:.1f}", 1)
        pdf.ln()

    # Metabolic Adaptation
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "6. METABOLIC ADAPTATION", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Week 1 Metabolic Adaptation: {initial_data['week1_adaptation']}", 0, 1)
    pdf.cell(0, 10, f"Final Week Metabolic Adaptation: {initial_data['final_week_adaptation']}", 0, 1)

    # Final Results
    pdf.add_page()
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "7. FINAL RESULTS", 0, 1, "C")
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

    # Body Fat Category Progression
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "8. BODY FAT CATEGORY PROGRESSION", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"Initial Category: {initial_data['initial_bf_category']}", 0, 1)
    pdf.cell(0, 10, f"Description: {initial_data['initial_bf_description']}", 0, 1)
    pdf.cell(0, 10, f"Estimated Time to Six-Pack: {initial_data['initial_sixpack_time']}", 0, 1)
    pdf.cell(0, 10, f"Final Category: {initial_data['final_bf_category']}", 0, 1)
    pdf.cell(0, 10, f"Description: {initial_data['final_bf_description']}", 0, 1)
    pdf.cell(0, 10, f"Estimated Time to Six-Pack: {initial_data['final_sixpack_time']}", 0, 1)

    # Insights and Recommendations
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "9. INSIGHTS AND RECOMMENDATIONS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 10, f"• Your metabolic rate adapted by {initial_data['adaptation_percentage']}% over the course of your journey.\n"
                           f"• You maintained an impressive {initial_data['lean_mass_preserved']}% of your initial lean mass.\n"
                           f"• Your muscle gain rate averaged {initial_data['avg_muscle_gain']} lbs per week, which is {initial_data['muscle_gain_assessment']}.\n"
                           f"• Based on your final body fat percentage, you're now in the {initial_data['final_bf_category']} category.\n"
                           f"• To maintain your results, consider a daily calorie intake of {initial_data['maintenance_calories']} calories.")

    # Next Steps
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "10. NEXT STEPS", 0, 1, "L")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 10, f"• {initial_data['personalized_recommendation']}\n"
                           f"• Consider adjusting your protein intake to {initial_data['recommended_protein']} g/day to support lean mass.\n"
                           f"• Your next ideal body composition goal could be {initial_data['next_goal_suggestion']}.")

    pdf.ln(10)
    pdf.multi_cell(0, 10, "Remember, this journey is a marathon, not a sprint. Celebrate your progress and stay committed to your health and fitness goals!")

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
    end_date = st.date_input("End Date", min_value=start_date)

# Activity and Training Section
st.header("Activity and Training")
col1, col2 = st.columns(2)
with col1:
    activity_level = st.selectbox("Activity Level", [
        "Little To No Exercise",
        "Light Exercise/Sports 1-3 Days/Week",
        "Moderate Exercise/Sports 3-5 Days/Week",
        "Hard Exercise/Sports 6-7 Days A Week",
        "Very Hard Exercise/Sports & A Physical Job"
    ])
    resistance_training = st.checkbox("Doing Resistance Training")
    is_athlete = st.checkbox("Are You An Athlete")
with col2:
    workout_type = st.selectbox("Workout Type", [
        "Bodybuilding - Focused on muscle building and strength training",
        "Cardio - Primarily cardiovascular exercises like running or cycling",
        "General Fitness - A mix of resistance training and cardio"
    ])
    workout_days = st.number_input("Workout Days Per Week", min_value=0, max_value=7)
    protein_intake = st.number_input("Daily Protein Intake (Grams)", min_value=0.0)

# Additional Information Section
st.header("Additional Information")
col1, col2 = st.columns(2)
with col1:
    job_activity = st.selectbox("Job Activity Level", [
        "Sedentary - Mostly sitting (e.g., desk job)",
        "Light - Standing or walking for significant periods (e.g., teacher)",
        "Moderate - Regular physical activity (e.g., retail worker)",
        "Active - Constant physical activity (e.g., construction worker)"
    ])
with col2:
    leisure_activity = st.selectbox("Leisure Activity Level", [
        "Sedentary - Little to no physical activity outside of work",
        "Light - Occasional light activities (e.g., casual walking)",
        "Moderate - Regular moderate activities (e.g., recreational sports)",
        "Active - Frequent intense activities (e.g., competitive sports)"
    ])
    experience_level = st.selectbox("Experience Level", [
        "Beginner (0-1 Year)",
        "Novice (1-2 Years)",
        "Intermediate (2-4 Years)",
        "Advanced (4-10 Years)",
        "Elite (10+ Years)"
    ])

if st.button("Calculate"):
    # Convert activity level to numeric
    activity_level_map = {
        "Little To No Exercise": 1,
        "Light Exercise/Sports 1-3 Days/Week": 2,
        "Moderate Exercise/Sports 3-5 Days/Week": 3,
        "Hard Exercise/Sports 6-7 Days A Week": 4,
        "Very Hard Exercise/Sports & A Physical Job": 5
    }
    activity_level_num = activity_level_map[activity_level]

    # Convert job and leisure activity to lowercase
    job_activity_lower = job_activity.split('-')[0].strip().lower()
    leisure_activity_lower = leisure_activity.split('-')[0].strip().lower()

    # Extract workout type
    workout_type_simple = workout_type.split('-')[0].strip()

    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type_simple)
    is_bodybuilder = workout_type_simple == "Bodybuilding" and experience_level in ['Intermediate (2-4 Years)', 'Advanced (4-10 Years)', 'Elite (10+ Years)']

    progression = predict_weight_loss(
        current_weight, current_bf, goal_weight, goal_bf, start_date, end_date,
        dob, gender.lower(), activity_level_num, height_cm, is_athlete,
        resistance_training, protein_intake, volume_score, intensity_score,
        frequency_score, job_activity_lower, leisure_activity_lower,
        experience_level, is_bodybuilder
    )

    # Generate PDF
    client_name = f"{first_name} {last_name}"
    pdf_bytes = generate_pdf(progression, {
        'dob': dob,
        'height_feet': feet,
        'height_inches': inches,
        'height_cm': height_cm,
        'goal_weight': goal_weight,
        'goal_bf': goal_bf,
        'activity_level_description': activity_level,
        'experience_level': experience_level,
        'initial_rmr': 1500,  # Placeholder
        'initial_tdee': 2000,  # Placeholder
        'tef': 200,  # Placeholder
        'neat': 300,  # Placeholder
        'initial_daily_calories': 2500,  # Placeholder
        'workout_type': workout_type,
        'workout_days': workout_days,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'resistance_training': resistance_training,
        'is_athlete': is_athlete,
        'initial_lean_mass': 130,  # Placeholder
        'initial_fat_mass': 30,  # Placeholder
        'estimated_muscle_gain': 1,  # Placeholder
        'week1_adaptation': 'Minimal',  # Placeholder
        'final_week_adaptation': 'Moderate',  # Placeholder
        'initial_bf_category': 'Overweight',  # Placeholder
        'initial_bf_description': 'Above average body fat.',  # Placeholder
        'initial_sixpack_time': '12 weeks',  # Placeholder
        'final_bf_category': 'Fit',  # Placeholder
        'final_bf_description': 'In the fit range.',  # Placeholder
        'final_sixpack_time': '8 weeks',  # Placeholder
        'adaptation_percentage': 15,  # Placeholder
        'lean_mass_preserved': 95,  # Placeholder
        'avg_muscle_gain': 0.5,  # Placeholder
        'muscle_gain_assessment': 'Excellent',  # Placeholder
        'maintenance_calories': 2500,  # Placeholder
        'personalized_recommendation': 'Increase resistance training to maximize muscle gain.',  # Placeholder
        'recommended_protein': 150,  # Placeholder
        'next_goal_suggestion': 'Reduce body fat to 10%',  # Placeholder
    }, gender.lower(), client_name)

    # Create download button
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"{client_name}_weight_loss_plan.pdf",
        mime="application/pdf"
    )

    # Final stats
    st.subheader("Final Stats and Results Summary")
    total_weeks = len(progression) - 1
    total_weight_loss = progression[0]['weight'] - progression[-1]['weight']
    total_bf_loss = progression[0]['body_fat_percentage'] - progression[-1]['body_fat_percentage']
    total_muscle_gain = sum(entry['muscle_gain'] for entry in progression)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Duration: {total_weeks} weeks")
        st.write(f"Total Weight Loss: {total_weight_loss:.1f} lbs")
        st.write(f"Total Body Fat Reduction: {total_bf_loss:.1f}%")
        st.write(f"Final Weight: {progression[-1]['weight']:.1f} lbs")
        st.write(f"Final Body Fat: {progression[-1]['body_fat_percentage']:.1f}%")
    with col2:
        st.write(f"Average Weekly Weight Loss: {total_weight_loss / total_weeks:.1f} lbs")
        st.write(f"Total Muscle Gain: {total_muscle_gain:.1f} lbs")
        st.write(f"Final Daily Calorie Intake: {progression[-1]['daily_calorie_intake']:.0f} calories")
        st.write(f"Final TDEE: {progression[-1]['tdee']:.0f} calories")
        st.write(f"Final Weekly Caloric Output: {progression[-1]['weekly_caloric_output']:.1f} calories")
