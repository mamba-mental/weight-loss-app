#grimore_test.py (Original Code File for Weight Loss Predictor)
import datetime
import math
from tabulate import tabulate
import unittest
import sys
import io
import logging

# Function to calculate age from date of birth
def calculate_age(dob, current_date):
    return current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))

# Function to calculate lean mass preservation scores based on workout frequency and type
def calculate_lean_mass_preservation_scores(workout_days, workout_type):
    workout_intensities = {
        "Bodybuilding": 0.8,
        "Cardio": 0.4,
        "General Fitness": 0.6
    }
    workout_volumes = {
        "Bodybuilding": 20,
        "Cardio": 10,
        "General Fitness": 15
    }
    if workout_type not in workout_intensities:
        raise ValueError("Invalid workout type.")
    volume_score = min(workout_volumes[workout_type] * workout_days / 7 / 20, 1)
    intensity_score = workout_intensities[workout_type]
    frequency_score = min(workout_days / 3, 1)
    return volume_score, intensity_score, frequency_score

# Estimate the thermic effect of food based on protein intake
def estimate_tef(protein_intake):
    return protein_intake * 0.3

# Estimate NEAT (Non-Exercise Activity Thermogenesis) based on job and leisure activity levels
def estimate_neat(job_activity, leisure_activity):
    job_factors = {'sedentary': 100, 'light': 300, 'moderate': 500, 'active': 700}
    leisure_factors = {'sedentary': 50, 'light': 150, 'moderate': 250, 'active': 350}
    return job_factors[job_activity] + leisure_factors[leisure_activity]

# Adjust body composition based on resistance training and protein intake
def adjust_body_composition(fat_loss, lean_loss, resistance_training, protein_intake, weight):
    if resistance_training:
        lean_loss *= 0.8 # Optimize protein and lean retention
    adjusted_fat_loss = fat_loss * 0.9
    adjusted_lean_loss = lean_loss * 0.1
    return adjusted_fat_loss, adjusted_lean_loss

# Calculate resting metabolic rate (RMR) using the Mifflin-St Jeor equation
def calculate_rmr(weight, age, gender, height_cm, is_athlete):
    if gender == 'm':
        rmr = 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        rmr = 10 * weight + 6.25 * height_cm - 5 * age - 161
    return rmr * 1.1 if is_athlete else rmr

# Calculate total daily energy expenditure (TDEE) based on activity level
def calculate_tdee(weight, age, gender, activity_level, height_cm, is_athlete, protein_intake, job_activity, leisure_activity):
    rmr = calculate_rmr(weight, age, gender, height_cm, is_athlete)
    activity_factors = [1.2, 1.375, 1.55, 1.725, 1.9]
    tdee = rmr * activity_factors[activity_level - 1]
    tdee += estimate_tef(protein_intake) # Add thermic effect of food
    tdee += estimate_neat(job_activity, leisure_activity) # Add NEAT
    return tdee

# Calculate the amount of fat loss required to reach the goal body fat percentage
def calculate_fat_loss_required(current_weight, current_bf, goal_bf):
    current_fat_mass = current_weight * (current_bf / 100)
    goal_fat_mass = current_weight * (goal_bf / 100)
    fat_loss_required = current_fat_mass - goal_fat_mass
    return fat_loss_required

# Calculate metabolic adaptation
def calculate_metabolic_adaptation(week, current_bf, is_bodybuilder):
    # Base adaptation calculation
    base_adaptation = max(0.85, 1 - (week / 300))

    # Adjust adaptation based on current body fat percentage
    bf_factor = max(0.9, 1 - (30 - current_bf) / 100)

    # More aggressive adaptation for bodybuilders
    if is_bodybuilder:
        base_adaptation = max(0.80, 1 - (week / 200))

    return base_adaptation * bf_factor

# Function to adjust caloric output based on TDEE and daily calorie intake
def calculate_weekly_caloric_output(tdee, daily_calorie_intake):
    return (tdee - daily_calorie_intake) * 7

# Distribute weight loss between fat and lean mass
def distribute_weight_loss(weekly_weight_loss, current_bf, resistance_training, daily_protein_intake, current_weight, goal_bf, is_bodybuilder):
    # Start with the base FFM rule: 75% fat loss, 25% lean mass loss
    fat_loss_ratio = 0.75

    # Adjust based on current body fat percentage
    if current_bf > 30:
        fat_loss_ratio += 0.05
    elif current_bf < 15:
        fat_loss_ratio -= 0.05

    # Adjust for resistance training
    if resistance_training:
        fat_loss_ratio += 0.05

    # Adjust for protein intake
    protein_factor = min(daily_protein_intake / (current_weight * 0.8), 1)
    fat_loss_ratio += protein_factor * 0.05

    # More aggressive fat loss for bodybuilders
    if is_bodybuilder:
        fat_loss_ratio = min(fat_loss_ratio + 0.1, 0.95)
    else:
        fat_loss_ratio = min(fat_loss_ratio, 0.9)

    fat_loss = weekly_weight_loss * fat_loss_ratio
    lean_loss = weekly_weight_loss * (1 - fat_loss_ratio)

    return fat_loss, lean_loss

def calculate_initial_daily_calories(tdee, rmr):
    # Set initial daily calorie intake to the lesser of 58% of RMR or 58% of adapted TDEE
    return min(rmr * 0.58, tdee * 0.58)

def estimate_muscle_gain(current_weight, training_frequency, training_volume, intensity, protein_intake, age, gender, experience_level, is_bodybuilder):
    gain_rates = {
        'Beginner (0-1 year)': 0.0125,
        'Novice (1-2 years)': 0.0100,
        'Intermediate (2-4 years)': 0.0075,
        'Advanced (4-10 years)': 0.0050,
        'Elite (10+ years)': 0.0025
    }

    base_rate = gain_rates.get(experience_level, 0.0075) # Default to intermediate if not specified

    # Adjust rate based on age, gender, etc.
    age_multiplier = 1.0 if age < 30 else (0.8 if age < 40 else 0.6)
    gender_multiplier = 1.0 if gender == 'm' else 0.8
    frequency_multiplier = min(training_frequency / 3, 1.25)
    volume_intensity_multiplier = min((training_volume * intensity) / (10 * 0.7), 1.25)
    protein_multiplier = min(protein_intake / (current_weight * 1.6), 1.25)

    monthly_gain_percentage = base_rate * age_multiplier * gender_multiplier * frequency_multiplier * volume_intensity_multiplier * protein_multiplier

    # Increase muscle gain for bodybuilders (simulating PED use)
    if is_bodybuilder and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']:
        monthly_gain_percentage *= 2.5

    weekly_muscle_gain = (monthly_gain_percentage * current_weight) / 4

    return weekly_muscle_gain

def get_body_fat_info(gender, body_fat_percentage):
    categories = [
        {"name": "Very Lean", "men": 10, "women": 18, "time": "3-4 weeks", "description": "Visible abs, vascularity, striations"},
        {"name": "Lean", "men": 14, "women": 22, "time": "2-3 months", "description": "Some muscle definition, less visible abs"},
        {"name": "Average", "men": 19, "women": 27, "time": "3-4 months", "description": "Little muscle definition, soft look"},
        {"name": "Above Average", "men": 24, "women": 32, "time": "4-6 months", "description": "No visible abs, excess fat"},
        {"name": "High Body Fat", "men": 29, "women": 37, "time": "6-12 months", "description": "Excess fat all around, round physique"},
        {"name": "Obese", "men": float('inf'), "women": float('inf'), "time": "12+ months", "description": "Significant excess fat all around"}
    ]

    threshold_key = "men" if gender.lower() == 'm' else "women"

    for category in categories:
        if body_fat_percentage < category[threshold_key]:
            return category["name"], category["time"], category["description"]

    return categories[-1]["name"], categories[-1]["time"], categories[-1]["description"]

# Predict weight loss progression over time based on initial parameters
def predict_weight_loss(current_weight, current_bf, goal_weight, goal_bf, start_date, end_date, dob, gender, activity_level, height_cm, is_athlete, resistance_training, daily_protein_intake, volume_score, intensity_score, frequency_score, job_activity, leisure_activity, experience_level, is_bodybuilder):
    weeks = (end_date - start_date).days // 7
    progression = []
    initial_weight = current_weight
    initial_bf = current_bf

    for week in range(weeks + 1):
        age = calculate_age(dob, start_date + datetime.timedelta(weeks=week))
        rmr = calculate_rmr(current_weight, age, gender, height_cm, is_athlete)  # Add this line
        tdee = calculate_tdee(current_weight, age, gender, activity_level, height_cm, is_athlete, daily_protein_intake, job_activity, leisure_activity)
        metabolic_adaptation = calculate_metabolic_adaptation(week, current_bf, is_bodybuilder)
        adapted_tdee = tdee * metabolic_adaptation

        if week == 0:
            daily_calorie_intake = calculate_initial_daily_calories(adapted_tdee, rmr)
        else:
            remaining_weeks = max(1, weeks - week)
            current_fat_mass = current_weight * (current_bf / 100)
            current_lean_mass = current_weight - current_fat_mass
            goal_fat_mass = (goal_bf / 100) * current_lean_mass / (1 - (goal_bf / 100))
            remaining_fat_to_lose = max(current_fat_mass - goal_fat_mass, 0)
            weekly_fat_loss_required = remaining_fat_to_lose / remaining_weeks
            weekly_deficit_required = weekly_fat_loss_required * 3500

            daily_deficit_required = weekly_deficit_required / 7
            min_calories = max(adapted_tdee / 3, 1000) # Ensure not below 1/3 of TDEE or 1000 calories
            daily_calorie_intake = max(adapted_tdee - daily_deficit_required, min_calories)

        weekly_caloric_output = calculate_weekly_caloric_output(adapted_tdee, daily_calorie_intake)
        weekly_weight_loss = weekly_caloric_output / 3500

        fat_loss, lean_loss = distribute_weight_loss(weekly_weight_loss, current_bf, resistance_training, daily_protein_intake, current_weight, goal_bf, is_bodybuilder)

        if resistance_training:
            muscle_gain = estimate_muscle_gain(current_weight, frequency_score * 3, volume_score * 20, intensity_score, daily_protein_intake, age, gender, experience_level, is_bodybuilder)
        else:
            muscle_gain = 0

        current_fat_mass = max(0, current_weight * (current_bf / 100) - fat_loss)
        current_lean_mass = max(current_weight * (1 - current_bf / 100) - lean_loss + muscle_gain, current_weight * 0.05)
        current_weight = current_fat_mass + current_lean_mass
        current_bf = (current_fat_mass / current_weight) * 100

        total_weight_lost = initial_weight - current_weight

        progression.append({
            'date': (start_date + datetime.timedelta(weeks=week)).strftime("%m%d%y"),
            'weight': current_weight,
            'body_fat_percentage': current_bf,
            'daily_calorie_intake': daily_calorie_intake,
            'tdee': adapted_tdee,
            'weekly_caloric_output': weekly_caloric_output,
            'total_weight_lost': total_weight_lost,
            'lean_mass': current_lean_mass,
            'fat_mass': current_fat_mass,
            'muscle_gain': muscle_gain,
            'rmr': rmr  # Add this line
        })
        
        if current_bf <= goal_bf and current_weight <= goal_weight:
            break

    return progression

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid float.")

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_experience_level_input(prompt):
    print(prompt)
    levels = [
        ("1", "Beginner (0-1 year)"),
        ("2", "Novice (1-2 years)"),
        ("3", "Intermediate (2-4 years)"),
        ("4", "Advanced (4-10 years)"),
        ("5", "Elite (10+ years)")
    ]
    for idx, (level, description) in enumerate(levels, 1):
        print(f"{idx}. {description}")
    while True:
        try:
            choice = int(input("Choose an option: ").strip())
            if 1 <= choice <= len(levels):
                return levels[choice - 1][1]
            else:
                print(f"Invalid input. Please enter a number between 1 and {len(levels)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(levels)}.")

# Function to generate a comprehensive report
def generate_comprehensive_report(progression, initial_data):
    initial_entry = progression[0]
    final_entry = progression[-1]
    total_weeks = len(progression) - 1

    # Calculate additional metrics
    total_weight_loss = initial_entry['weight'] - final_entry['weight']
    total_bf_loss = initial_entry['body_fat_percentage'] - final_entry['body_fat_percentage']
    avg_weekly_loss = total_weight_loss / total_weeks
    total_muscle_gain = sum(entry['muscle_gain'] for entry in progression)
    adaptation_percentage = (1 - final_entry['tdee'] / initial_entry['tdee']) * 100
    lean_mass_preserved = (final_entry['lean_mass'] / initial_entry['lean_mass']) * 100
    avg_muscle_gain = total_muscle_gain / total_weeks

    # Generate the report
    report = f"""
======================================================
                 YOUR PERSONALIZED 
           WEIGHT LOSS JOURNEY REPORT
======================================================

Dear Client,

We've analyzed your data using our advanced weight loss prediction model. Here's a comprehensive breakdown of your journey:

1. PERSONAL PROFILE
------------------------------------------------------
Start Date: {initial_entry['date']}
End Date: {final_entry['date']}
Age: {calculate_age(initial_data['dob'], datetime.datetime.strptime(initial_entry['date'], "%m%d%y"))} years
Gender: {initial_data['gender']}
Height: {initial_data['height_feet']}'{initial_data['height_inches']}" ({initial_data['height_cm']:.1f} cm)
Initial Weight: {initial_entry['weight']:.1f} lbs
Goal Weight: {initial_data['goal_weight']:.1f} lbs
Initial Body Fat: {initial_entry['body_fat_percentage']:.1f}%
Goal Body Fat: {initial_data['goal_bf']:.1f}%
Activity Level: {initial_data['activity_level_description']}
Experience Level: {initial_data['experience_level']}

2. METABOLIC CALCULATIONS
------------------------------------------------------
Initial Resting Metabolic Rate (RMR): {initial_entry['rmr']:.0f} calories/day
Initial Total Daily Energy Expenditure (TDEE): {initial_entry['tdee']:.0f} calories/day
Thermic Effect of Food (TEF): {estimate_tef(initial_data['protein_intake']):.0f} calories/day
Non-Exercise Activity Thermogenesis (NEAT): {estimate_neat(initial_data['job_activity'], initial_data['leisure_activity']):.0f} calories/day
Initial Daily Calorie Intake: {initial_entry['daily_calorie_intake']:.0f} calories/day

3. WORKOUT ANALYSIS
------------------------------------------------------
Workout Type: {initial_data['workout_type']}
Workout Frequency: {initial_data['workout_days']} days/week
Volume Score: {initial_data['volume_score']:.2f}
Intensity Score: {initial_data['intensity_score']:.2f}
Frequency Score: {initial_data['frequency_score']:.2f}
Resistance Training: {'Yes' if initial_data['resistance_training'] else 'No'}
Athlete Status: {'Yes' if initial_data['is_athlete'] else 'No'}

4. BODY COMPOSITION ADJUSTMENTS
------------------------------------------------------
Initial Lean Mass: {initial_entry['lean_mass']:.1f} lbs
Initial Fat Mass: {initial_entry['fat_mass']:.1f} lbs
Estimated Weekly Muscle Gain: {initial_entry['muscle_gain']:.3f} lbs

5. WEEKLY PROGRESS SUMMARY
------------------------------------------------------
{tabulate(progression, headers="keys", tablefmt="grid")}

6. METABOLIC ADAPTATION
------------------------------------------------------
Week 1 Metabolic Adaptation: {calculate_metabolic_adaptation(1, initial_entry['body_fat_percentage'], initial_data['is_bodybuilder']):.2f}
Final Week Metabolic Adaptation: {calculate_metabolic_adaptation(total_weeks, final_entry['body_fat_percentage'], initial_data['is_bodybuilder']):.2f}

7. FINAL RESULTS
------------------------------------------------------
Duration: {total_weeks} weeks
Total Weight Loss: {total_weight_loss:.1f} lbs
Total Body Fat Reduction: {total_bf_loss:.1f}%
Final Weight: {final_entry['weight']:.1f} lbs
Final Body Fat: {final_entry['body_fat_percentage']:.1f}%
Average Weekly Weight Loss: {avg_weekly_loss:.2f} lbs
Total Muscle Gain: {total_muscle_gain:.1f} lbs
Final Daily Calorie Intake: {final_entry['daily_calorie_intake']:.0f} calories
Final TDEE: {final_entry['tdee']:.0f} calories
Final Weekly Caloric Output: {final_entry['weekly_caloric_output']:.1f} calories

8. BODY FAT CATEGORY PROGRESSION
------------------------------------------------------
Initial Category: {get_body_fat_info(initial_data['gender'], initial_entry['body_fat_percentage'])[0]}
   Description: {get_body_fat_info(initial_data['gender'], initial_entry['body_fat_percentage'])[2]}
   Estimated Time to Six-Pack: {get_body_fat_info(initial_data['gender'], initial_entry['body_fat_percentage'])[1]}

Final Category: {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[0]}
   Description: {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[2]}
   Estimated Time to Six-Pack: {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[1]}

9. INSIGHTS AND RECOMMENDATIONS
------------------------------------------------------
• Your metabolic rate adapted by {adaptation_percentage:.1f}% over the course of your journey.
• You maintained an impressive {lean_mass_preserved:.1f}% of your initial lean mass.
• Your muscle gain rate averaged {avg_muscle_gain:.3f} lbs per week, which is {'excellent' if avg_muscle_gain > 0.5 else 'good' if avg_muscle_gain > 0.25 else 'moderate'}.
• Based on your final body fat percentage, you're now in the {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[0]} category.
• To maintain your results, consider a daily calorie intake of {final_entry['tdee']:.0f} calories.

10. NEXT STEPS
------------------------------------------------------
• {'Continue with your current plan.' if final_entry['body_fat_percentage'] > initial_data['goal_bf'] else 'Consider a muscle building phase to further improve body composition.'}
• Consider adjusting your protein intake to {final_entry['weight'] * 0.8:.0f} g/day to support lean mass.
• Your next ideal body composition goal could be {max(final_entry['body_fat_percentage'] - 2, 5):.1f}% body fat.

Remember, this journey is a marathon, not a sprint. Celebrate your progress and stay committed to your health and fitness goals!

======================================================
            Powered by Advanced AI Analytics
======================================================
"""
    return report

def run_user_interaction():
    def get_date_input(prompt):
        while True:
            try:
                return datetime.datetime.strptime(input(prompt), "%m%d%y")
            except ValueError:
                print("Invalid input. Please enter a valid date in the format MMDDYY (e.g., 091524 for September 15, 2024).")

    def get_yes_no_input(prompt):
        while True:
            response = input(prompt).strip().lower()
            if response in ['y', 'n']:
                return response == 'y'
            else:
                print("Invalid input. Please enter 'Y' for Yes or 'N' for No.")

    def get_choice_input(prompt, choices_descriptions):
        print(prompt)
        for idx, (choice, description) in enumerate(choices_descriptions, 1):
            print(f"{idx}. {choice} - {description}")
        while True:
            try:
                choice = int(input("Choose an option: ").strip())
                if 1 <= choice <= len(choices_descriptions):
                    return choices_descriptions[choice - 1][0]
                else:
                    print(f"Invalid input. Please enter a number between 1 and {len(choices_descriptions)}.")
            except ValueError:
                print(f"Invalid input. Please enter a number between 1 and {len(choices_descriptions)}.")

    print("Welcome to the Weight Loss Predictor!")
    current_weight = get_float_input("Enter your current weight in lbs: ")
    current_bf = get_float_input("Enter your current body fat percentage: ")
    goal_weight = get_float_input("Enter your goal weight in lbs: ")
    goal_bf = get_float_input("Enter your goal body fat percentage: ")
    start_date = get_date_input("Enter your start date (MMDDYY): ")
    end_date = get_date_input("Enter your end date (MMDDYY): ")
    dob = get_date_input("Enter your date of birth (MMDDYY): ")
    gender = input("Enter your gender (m/f): ").strip().lower()
    height_feet = get_int_input("Enter your height (feet): ")
    height_inches = get_int_input("Enter your height (inches): ")
    height_cm = (height_feet * 12 + height_inches) * 2.54
    protein_intake = get_float_input("Enter your daily protein intake in grams: ")

    activity_level = get_choice_input("Enter your activity level (1-5):", [
        ("1", "Little to no exercise"),
        ("2", "Light exercise/sports 1-3 days/week"),
        ("3", "Moderate exercise/sports 3-5 days/week"),
        ("4", "Hard exercise/sports 6-7 days a week"),
        ("5", "Very hard exercise/sports & a physical job")
    ])

    resistance_training = get_yes_no_input("Are you doing resistance training? (Y/N): ")
    is_athlete = get_yes_no_input("Are you an athlete? (Y/N): ")

    workout_type = get_choice_input("What type of workouts do you primarily do?", [
        ("Bodybuilding", "Strength training and muscle building"),
        ("Cardio", "Cardiovascular exercises like running or cycling"),
        ("General Fitness", "A mix of different exercises for overall health")
    ])
    workout_days = get_int_input("How many days per week do you work out? ")

    job_activity = get_choice_input("Select your job activity level:", [
        ("sedentary", "Mostly sitting (e.g., desk job)"),
        ("light", "Light activity (e.g., teacher, salesperson)"),
        ("moderate", "Moderate activity (e.g., construction worker)"),
        ("active", "Very active (e.g., courier, agriculture)")
    ])
    leisure_activity = get_choice_input("Select your leisure activity level:", [
        ("sedentary", "Little to no physical activity"),
        ("light", "Light physical activity (e.g., walking, gardening)"),
        ("moderate", "Moderate physical activity (e.g., hiking, dancing)"),
        ("active", "High physical activity (e.g., sports, intense exercise)")
    ])

    experience_level = get_experience_level_input("Enter your experience level (1-5):")

    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type)
    is_bodybuilder = workout_type == "Bodybuilding" and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    progression = predict_weight_loss(current_weight, current_bf, goal_weight, goal_bf, start_date, end_date, dob, gender, int(activity_level), height_cm, is_athlete, resistance_training, protein_intake, volume_score, intensity_score, frequency_score, job_activity, leisure_activity, experience_level, is_bodybuilder)

    initial_data = {
        'dob': dob,
        'gender': gender,
        'height_feet': height_feet,
        'height_inches': height_inches,
        'height_cm': height_cm,
        'goal_weight': goal_weight,
        'goal_bf': goal_bf,
        'activity_level_description': ["Little to no exercise", "Light exercise/sports 1-3 days/week", "Moderate exercise/sports 3-5 days/week", "Hard exercise/sports 6-7 days a week", "Very hard exercise/sports & a physical job"][int(activity_level) - 1],
        'experience_level': experience_level,
        'protein_intake': protein_intake,
        'workout_type': workout_type,
        'workout_days': workout_days,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'resistance_training': resistance_training,
        'is_athlete': is_athlete,
        'job_activity': job_activity,
        'leisure_activity': leisure_activity,
        'is_bodybuilder': is_bodybuilder
    }

    return progression, initial_data

# Function to print the progress summary
def print_summary(progression, initial_data):
    report = generate_comprehensive_report(progression, initial_data)
    print(report)

# Function to execute tests for the weight loss predictor
class TestWeightLossPredictor(unittest.TestCase):
    def setUp(self):
        self.start_date = datetime.datetime.strptime("010123", "%m%d%y")
        self.end_date = datetime.datetime.strptime("040123", "%m%d%y")
        self.dob = datetime.datetime.strptime("010190", "%m%d%y")
        self.gender = 'm'
        self.activity_level = 3
        self.height_cm = 180
        self.is_athlete = False
        self.current_weight = 240
        self.current_bf = 30
        self.goal_weight = 217
        self.goal_bf = 7
        self.resistance_training = True
        self.protein_intake = 150
        self.job_activity = "sedentary"
        self.leisure_activity = "light"
        self.volume_score = 0.5
        self.intensity_score = 0.6
        self.frequency_score = 0.7
        self.experience_level = "Intermediate (2-4 years)"
        self.is_bodybuilder = True

    def test_calculate_rmr(self):
        age = calculate_age(self.dob, self.start_date)
        rmr = calculate_rmr(self.current_weight, age, self.gender, self.height_cm, self.is_athlete)
        self.assertTrue(1800 <= rmr <= 2500, f"RMR {rmr} is out of expected range")

    def test_calculate_tdee(self):
        age = calculate_age(self.dob, self.start_date)
        tdee = calculate_tdee(self.current_weight, age, self.gender, self.activity_level, self.height_cm, self.is_athlete, self.protein_intake, self.job_activity, self.leisure_activity)
        self.assertTrue(2800 <= tdee <= 3800, f"TDEE {tdee} is out of expected range")

    def test_predict_weight_loss(self):
        progression = predict_weight_loss(
            self.current_weight, self.current_bf, self.goal_weight, self.goal_bf,
            self.start_date, self.end_date, self.dob, self.gender, self.activity_level,
            self.height_cm, self.is_athlete, self.resistance_training, self.protein_intake,
            self.volume_score, self.intensity_score, self.frequency_score,
            self.job_activity, self.leisure_activity, self.experience_level, self.is_bodybuilder
        )
        final_weight = progression[-1]['weight']
        final_bf = progression[-1]['body_fat_percentage']
        self.assertLessEqual(final_bf, self.goal_bf + 0.5, f"Final body fat {final_bf}% diverged from target {self.goal_bf}% intent")
        self.assertEqual(progression[-1]['date'], self.end_date.strftime("%m%d%y"), "Completion timeline failed")
        for i in range(1, len(progression)):
            self.assertLessEqual(progression[i]['weight'], progression[i-1]['weight'], f"Weight gain in week {i} unjustified")
            self.assertLessEqual(progression[i]['body_fat_percentage'], progression[i-1]['body_fat_percentage'], f"Non-decrement at week {i} questionable")

    def test_verified_minimum_calories(self):
        progression = predict_weight_loss(
            self.current_weight, self.current_bf, self.goal_weight, self.goal_bf,
            self.start_date, self.end_date, self.dob, self.gender, self.activity_level,
            self.height_cm, self.is_athlete, self.resistance_training, self.protein_intake,
            self.volume_score, self.intensity_score, self.frequency_score,
            self.job_activity, self.leisure_activity, self.experience_level, self.is_bodybuilder
        )
        for entry in progression:
            self.assertGreaterEqual(entry['daily_calorie_intake'], 1000)

if __name__ == "__main__":
    progression, initial_data = run_user_interaction()
    print_summary(progression, initial_data)