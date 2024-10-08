import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from grimore_test import predict_weight_loss, calculate_lean_mass_preservation_scores, get_body_fat_info, estimate_tef, estimate_neat, calculate_metabolic_adaptation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

# Function to calculate age
def calculate_age(dob, current_date):
    return current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))

# Set page configuration
st.set_page_config(page_title="Weight Loss Predictor", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    body {
        color: #FFFFFF;
        background-color: #000000;
    }
    .stButton > button {
        color: #000000;
        background-color: #FFFFFF;
    }
    .stSelectbox > div > div {
        color: #FFFFFF;
        background-color: #1A1A1A;
    }
    .stTextInput > div > div > input {
        color: #FFFFFF;
        background-color: #1A1A1A;
    }
    .stNumberInput > div > div > input {
        color: #FFFFFF;
        background-color: #1A1A1A;
    }
    .stDateInput > div > div > input {
        color: #FFFFFF;
        background-color: #1A1A1A;
    }
    .streamlit-expanderHeader {
        color: #FFFFFF;
    }
    p, .stMarkdown {
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# PDF generation function using ReportLab
def generate_pdf(progression, report_data, gender, client_name):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=1))
    
    story = []
    
    # Title
    story.append(Paragraph("YOUR PERSONALIZED WEIGHT LOSS JOURNEY REPORT", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    # Personal Profile
    story.append(Paragraph("1. PERSONAL PROFILE", styles['Heading2']))
    data = [[key, value] for key, value in report_data['personal_profile'].items()]
    t = Table(data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('FONTSIZE', (0, 0), (-1, 0), 14),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                           ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                           ('FONTSIZE', (0, 0), (-1, -1), 12),
                           ('TOPPADDING', (0, 0), (-1, -1), 6),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Metabolic Calculations
    story.append(Paragraph("2. METABOLIC CALCULATIONS", styles['Heading2']))
    data = [[key, value] for key, value in report_data['metabolic_calculations'].items()]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Workout Analysis
    story.append(Paragraph("3. WORKOUT ANALYSIS", styles['Heading2']))
    data = [[key, value] for key, value in report_data['workout_analysis'].items()]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Body Composition Adjustments
    story.append(Paragraph("4. BODY COMPOSITION ADJUSTMENTS", styles['Heading2']))
    data = [[key, value] for key, value in report_data['body_composition'].items()]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Weekly Progress Summary
    story.append(Paragraph("5. WEEKLY PROGRESS SUMMARY", styles['Heading2']))
    data = [
        ["Week", "Date", "Weight (lbs)", "Body Fat %", "Daily Calories", "TDEE", "Weekly Caloric Output", "Total Weight Lost"]
    ]
    for i, entry in enumerate(progression):
        data.append([str(i), entry['date'], f"{entry['weight']:.1f}", f"{entry['body_fat_percentage']:.1f}", f"{entry['daily_calorie_intake']:.0f}", f"{entry['tdee']:.0f}", f"{entry['weekly_caloric_output']:.1f}", f"{entry['total_weight_lost']:.1f}"])
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Metabolic Adaptation
    story.append(Paragraph("6. METABOLIC ADAPTATION", styles['Heading2']))
    data = [[key, value] for key, value in report_data['metabolic_adaptation'].items()]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Final Results
    story.append(Paragraph("7. FINAL RESULTS", styles['Heading2']))
    data = [[key, value] for key, value in report_data['final_results'].items()]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Body Fat Category Progression
    story.append(Paragraph("8. BODY FAT CATEGORY PROGRESSION", styles['Heading2']))
    data = [[key, value] for key, value in report_data['body_fat_category'].items()]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Insights and Recommendations
    story.append(Paragraph("9. INSIGHTS AND RECOMMENDATIONS", styles['Heading2']))
    for recommendation in report_data['insights_recommendations']:
        story.append(Paragraph(recommendation, styles['Justify']))
    story.append(Spacer(1, 12))
    
    # Next Steps
    story.append(Paragraph("10. NEXT STEPS", styles['Heading2']))
    for step in report_data['next_steps']:
        story.append(Paragraph(step, styles['Justify']))
    
    story.append(Spacer(1, 12))
    story.append(Paragraph("Remember, this journey is a marathon, not a sprint. Celebrate your progress and stay committed to your health and fitness goals!", styles['Justify']))
    
    # Build the PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# Function to generate the comprehensive report data
def generate_report_data(progression, initial_data, gender):
    initial_entry = progression[0]
    final_entry = progression[-1]
    total_weeks = len(progression) - 1
    total_weight_loss = initial_entry['weight'] - final_entry['weight']
    total_bf_loss = initial_entry['body_fat_percentage'] - final_entry['body_fat_percentage']
    avg_weekly_loss = total_weight_loss / total_weeks
    total_muscle_gain = sum(entry['muscle_gain'] for entry in progression)
    adaptation_percentage = (1 - final_entry['tdee'] / initial_entry['tdee']) * 100
    lean_mass_preserved = (final_entry['lean_mass'] / initial_entry['lean_mass']) * 100
    avg_muscle_gain = total_muscle_gain / total_weeks

    report_data = {
        "personal_profile": {
            "Start Date": initial_entry['date'],
            "End Date": final_entry['date'],
            "Age": calculate_age(initial_data['dob'], datetime.strptime(initial_entry['date'], '%m%d%y')),
            "Gender": gender.upper(),
            "Height": f"{initial_data['height_feet']}'{initial_data['height_inches']}\" ({initial_data['height_cm']:.1f} cm)",
            "Initial Weight": f"{initial_entry['weight']:.1f} lbs",
            "Goal Weight": f"{initial_data['goal_weight']:.1f} lbs",
            "Initial Body Fat": f"{initial_entry['body_fat_percentage']:.1f}%",
            "Goal Body Fat": f"{initial_data['goal_bf']:.1f}%",
            "Activity Level": initial_data['activity_level_description'],
            "Experience Level": initial_data['experience_level']
        },
        "metabolic_calculations": {
            "Initial RMR": f"{initial_data['initial_rmr']:.0f} calories/day",
            "Initial TDEE": f"{initial_data['initial_tdee']:.0f} calories/day",
            "TEF": f"{initial_data['tef']:.0f} calories/day",
            "NEAT": f"{initial_data['neat']:.0f} calories/day",
            "Initial Daily Calorie Intake": f"{initial_data['initial_daily_calories']:.0f} calories/day"
        },
        "workout_analysis": {
            "Workout Type": initial_data['workout_type'],
            "Workout Frequency": f"{initial_data['workout_days']} days/week",
            "Volume Score": f"{initial_data['volume_score']:.2f}",
            "Intensity Score": f"{initial_data['intensity_score']:.2f}",
            "Frequency Score": f"{initial_data['frequency_score']:.2f}",
            "Resistance Training": "Yes" if initial_data['resistance_training'] else "No",
            "Athlete Status": "Yes" if initial_data['is_athlete'] else "No"
        },
        "body_composition": {
            "Initial Lean Mass": f"{initial_data['initial_lean_mass']:.1f} lbs",
            "Initial Fat Mass": f"{initial_data['initial_fat_mass']:.1f} lbs",
            "Estimated Weekly Muscle Gain": f"{initial_data['estimated_muscle_gain']:.3f} lbs"
        },
        "metabolic_adaptation": {
            "Week 1 Metabolic Adaptation": f"{initial_data['week1_adaptation']:.2f}",
            "Final Week Metabolic Adaptation": f"{initial_data['final_week_adaptation']:.2f}"
        },
        "final_results": {
            "Duration": f"{total_weeks} weeks",
            "Total Weight Loss": f"{total_weight_loss:.1f} lbs",
            "Total Body Fat Reduction": f"{total_bf_loss:.1f}%",
            "Final Weight": f"{final_entry['weight']:.1f} lbs",
            "Final Body Fat": f"{final_entry['body_fat_percentage']:.1f}%",
            "Average Weekly Weight Loss": f"{avg_weekly_loss:.2f} lbs",
            "Total Muscle Gain": f"{total_muscle_gain:.1f} lbs",
            "Final Daily Calorie Intake": f"{final_entry['daily_calorie_intake']:.0f} calories",
            "Final TDEE": f"{final_entry['tdee']:.0f} calories",
            "Final Weekly Caloric Output": f"{final_entry['weekly_caloric_output']:.1f} calories"
        },
        "body_fat_category": {
            "Initial Category": initial_data['initial_bf_category'],
            "Description": initial_data['initial_bf_description'],
            "Estimated Time to Six-Pack": initial_data['initial_sixpack_time'],
            "Final Category": initial_data['final_bf_category'],
            "Description": initial_data['final_bf_description'],
            "Estimated Time to Six-Pack": initial_data['final_sixpack_time']
        },
        "insights_recommendations": [
            f"Your metabolic rate adapted by {adaptation_percentage:.1f}% over the course of your journey.",
            f"You maintained an impressive {lean_mass_preserved:.1f}% of your initial lean mass.",
            f"Your muscle gain rate averaged {avg_muscle_gain:.3f} lbs per week, which is {'excellent' if avg_muscle_gain > 0.5 else 'good' if avg_muscle_gain > 0.25 else 'moderate'}.",
            f"Based on your final body fat percentage, you're now in the {initial_data['final_bf_category']} category.",
            f"To maintain your results, consider a daily calorie intake of {final_entry['tdee']:.0f} calories."
        ],
        "next_steps": [
            initial_data['personalized_recommendation'],
            f"Consider adjusting your protein intake to {final_entry['weight'] * 0.8:.0f} g/day to support lean mass.",
            f"Your next ideal body composition goal could be {max(final_entry['body_fat_percentage'] - 2, 5):.1f}% body fat."
        ]
    }
    return report_data

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

    # Calculate initial RMR and TDEE
    initial_rmr = progression[0]['rmr']
    initial_tdee = progression[0]['tdee']
    initial_daily_calories = progression[0]['daily_calorie_intake']

    # Generate report data
    report_data = generate_report_data(progression, {
        'dob': dob,
        'height_feet': feet,
        'height_inches': inches,
        'height_cm': height_cm,
        'goal_weight': goal_weight,
        'goal_bf': goal_bf,
        'activity_level_description': activity_level,
        'experience_level': experience_level,
        'initial_rmr': initial_rmr,
        'initial_tdee': initial_tdee,
        'tef': estimate_tef(protein_intake),
        'neat': estimate_neat(job_activity_lower, leisure_activity_lower),
        'initial_daily_calories': initial_daily_calories,
        'workout_type': workout_type,
        'workout_days': workout_days,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'resistance_training': resistance_training,
        'is_athlete': is_athlete,
        'initial_lean_mass': progression[0]['lean_mass'],
        'initial_fat_mass': progression[0]['fat_mass'],
        'estimated_muscle_gain': progression[0]['muscle_gain'],
        'week1_adaptation': calculate_metabolic_adaptation(1, progression[0]['body_fat_percentage'], is_bodybuilder),
        'final_week_adaptation': calculate_metabolic_adaptation(len(progression)-1, progression[-1]['body_fat_percentage'], is_bodybuilder),
        'initial_bf_category': get_body_fat_info(gender.lower(), progression[0]['body_fat_percentage'])[0],
        'initial_bf_description': get_body_fat_info(gender.lower(), progression[0]['body_fat_percentage'])[2],
        'initial_sixpack_time': get_body_fat_info(gender.lower(), progression[0]['body_fat_percentage'])[1],
        'final_bf_category': get_body_fat_info(gender.lower(), progression[-1]['body_fat_percentage'])[0],
        'final_bf_description': get_body_fat_info(gender.lower(), progression[-1]['body_fat_percentage'])[2],
        'final_sixpack_time': get_body_fat_info(gender.lower(), progression[-1]['body_fat_percentage'])[1],
        'personalized_recommendation': 'Increase resistance training to maximize muscle gain.' if not resistance_training else 'Continue with your current plan.',
    }, gender.lower())

    # Display results
    st.header("Your Personalized Weight Loss Journey Report")

    st.subheader("1. Personal Profile")
    for key, value in report_data['personal_profile'].items():
        st.write(f"{key}: {value}")

    st.subheader("2. Metabolic Calculations")
    for key, value in report_data['metabolic_calculations'].items():
        st.write(f"{key}: {value}")

    st.subheader("3. Workout Analysis")
    for key, value in report_data['workout_analysis'].items():
        st.write(f"{key}: {value}")

    st.subheader("4. Body Composition Adjustments")
    for key, value in report_data['body_composition'].items():
        st.write(f"{key}: {value}")

    st.subheader("5. Weekly Progress Summary")
    progress_df = pd.DataFrame(progression)
    st.dataframe(progress_df)

    st.subheader("6. Metabolic Adaptation")
    for key, value in report_data['metabolic_adaptation'].items():
        st.write(f"{key}: {value}")

    st.subheader("7. Final Results")
    for key, value in report_data['final_results'].items():
        st.write(f"{key}: {value}")

    st.subheader("8. Body Fat Category Progression")
    for key, value in report_data['body_fat_category'].items():
        st.write(f"{key}: {value}")

    st.subheader("9. Insights and Recommendations")
    for insight in report_data['insights_recommendations']:
        st.write(f"• {insight}")

    st.subheader("10. Next Steps")
    for step in report_data['next_steps']:
        st.write(f"• {step}")

    st.write("Remember, this journey is a marathon, not a sprint. Celebrate your progress and stay committed to your health and fitness goals!")

    # Generate PDF
    client_name = f"{first_name} {last_name}"
    pdf_bytes = generate_pdf(progression, report_data, gender.lower(), client_name)

    # Create download button
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"{client_name}_weight_loss_plan.pdf",
        mime="application/pdf"
    )
