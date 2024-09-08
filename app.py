import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from grimore_test import predict_weight_loss, calculate_lean_mass_preservation_scores, get_body_fat_info
from fpdf import FPDF

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

def generate_pdf(progression, gender, client_name, initial_data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 10, f"Weight Loss Plan for {client_name}", 0, 1, "C")
    pdf.ln(10)

    # Personal Profile
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, "Personal Profile", 0, 1, "L")
    pdf.cell(0, 10, f"Start Date: {progression[0]['date']}", 0, 1)
    pdf.cell(0, 10, f"End Date: {progression[-1]['date']}", 0, 1)
    pdf.cell(0, 10, f"Age: {calculate_age(initial_data['dob'], datetime.strptime(progression[0]['date'], '%m%d%y'))} years", 0, 1)
    pdf.cell(0, 10, f"Gender: {gender.upper()}", 0, 1)
    pdf.cell(0, 10, f"Height: {initial_data['height_cm']} cm", 0, 1)
    pdf.cell(0, 10, f"Initial Weight: {progression[0]['weight']:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Goal Weight: {progression[-1]['weight']:.1f} lbs", 0, 1)
    pdf.cell(0, 10, f"Initial Body Fat: {progression[0]['body_fat_percentage']:.1f}%", 0, 1)
    pdf.cell(0, 10, f"Goal Body Fat: {progression[-1]['body_fat_percentage']:.1f}%", 0, 1)

    # Weekly Progress Summary
    pdf.add_page()
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Weekly Progress Summary", 0, 1, "C")
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

    # Final Stats Summary
    pdf.add_page()
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Final Stats and Results Summary", 0, 1, "C")
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
        current_weight, current_bf, goal_weight, goal_bf,
        start_date, end_date, dob, gender.lower(), activity_level_num,
        height_cm, is_athlete, resistance_training, protein_intake,
        volume_score, intensity_score, frequency_score,
        job_activity_lower, leisure_activity_lower, experience_level, is_bodybuilder
    )

    # Display results
    st.subheader("Weight Loss Plan Input Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Start Date: {progression[0]['date']}")
        st.write(f"Initial Weight: {progression[0]['weight']:.1f} lbs")
        st.write(f"Initial Body Fat: {progression[0]['body_fat_percentage']:.1f}%")
    with col2:
        st.write(f"End Date: {progression[-1]['date']}")
        st.write(f"Goal Weight: {progression[-1]['weight']:.1f} lbs")
        st.write(f"Goal Body Fat: {progression[-1]['body_fat_percentage']:.1f}%")

    st.subheader("Weekly Progress Summary")
    df = pd.DataFrame(progression)
    st.dataframe(df.style.format({
        'weight': '{:.1f}',
        'body_fat_percentage': '{:.1f}',
        'daily_calorie_intake': '{:.0f}',
        'tdee': '{:.0f}',
        'weekly_caloric_output': '{:.1f}',
        'total_weight_lost': '{:.1f}',
        'lean_mass': '{:.1f}',
        'fat_mass': '{:.1f}',
        'muscle_gain': '{:.3f}'
    }))

    # Generate PDF
    client_name = f"{first_name} {last_name}"
    pdf_bytes = generate_pdf(progression, gender.lower(), client_name, {
        'dob': dob,
        'height_cm': height_cm
    })

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