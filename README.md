
# Weight Loss Predictor

## Project Overview

The Weight Loss Predictor is a comprehensive tool designed to simulate and predict weight loss progression over time. It takes into account various factors such as daily caloric intake, exercise regimen, metabolic adaptation, and body composition changes. The application provides users with personalized insights and recommendations to help them achieve their weight loss goals more effectively.

## Key Features

- **Detailed Weight Loss Prediction**: Simulates weight loss over a specified period based on personalized user inputs.
- **Comprehensive Reports**: Generates detailed reports that include metabolic calculations, workout analysis, body composition adjustments, and weekly progress summaries.
- **Customizable Workouts and Diet**: Adjusts predictions based on workout type, frequency, intensity, and daily protein intake.
- **Metabolic Adaptation Tracking**: Monitors changes in metabolic rate over time to ensure realistic predictions.
- **PDF Report Generation**: Allows users to generate and download a PDF report summarizing their weight loss journey.

## Directory Structure

```plaintext
.
├── .gitignore
├── app.py
├── capacitor.config.json
├── grimore_test.py
├── package.json
├── package-lock.json
├── requirements.txt
├── styles.css
└── README.md
```

## File Descriptions

### `.gitignore`

Specifies files and directories to be ignored by Git, including Python cache files and environment variables.

### `app.py`

The main entry point for the application. It uses Streamlit for the frontend interface and integrates functions from `grimore_test.py` to handle weight loss predictions and report generation. It also includes a PDF generation feature using ReportLab.

### `capacitor.config.json`

Configuration file for the Capacitor, detailing the app's ID, name, and web directory. This file is crucial for the mobile deployment of the application.

### `grimore_test.py`

Contains all the core functions and algorithms used in the weight loss prediction model. This includes calculations for resting metabolic rate (RMR), total daily energy expenditure (TDEE), lean mass preservation, and more. The file also includes unit tests to verify the accuracy of these functions.

### `package.json`

Defines the project's metadata and dependencies required for running the application in a Node.js environment. This includes Capacitor dependencies for building mobile apps.

### `package-lock.json`

Locks the versions of dependencies specified in `package.json`, ensuring consistent builds across different environments.

### `requirements.txt`

Lists all Python dependencies required to run the application, such as `streamlit`, `pandas`, and `reportlab`.

### `styles.css`

Custom CSS file used to style the Streamlit frontend, ensuring a consistent look and feel across the application.

## Installation

### Prerequisites

- **Python 3.8+**: Ensure you have Python installed on your system.
- **pip**: Python's package manager.

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/username/weight-loss-app.git
   cd weight-loss-app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

2. **Input Personal Information**:
   Enter your weight, body fat percentage, goal weight, and other personal details.

3. **Generate Predictions**:
   The application will simulate your weight loss journey and display a detailed report.

4. **Download PDF Report**:
   Use the "Download Report" button to get a PDF summary of your weight loss prediction.

## Detailed Functionality

### Core Prediction Functions

The core prediction functions are housed in `grimore_test.py` and include:

- **`calculate_age(dob, current_date)`**: Calculates the age based on the date of birth.
- **`calculate_rmr(weight, age, gender, height_cm, is_athlete)`**: Calculates the resting metabolic rate using the Mifflin-St Jeor equation.
- **`calculate_tdee(weight, age, gender, activity_level, height_cm, is_athlete, protein_intake, job_activity, leisure_activity)`**: Computes the total daily energy expenditure.
- **`predict_weight_loss(...)`**: Simulates the weight loss journey based on the user's inputs and returns a progression over time.

### PDF Generation

The PDF report generation is handled in `app.py` using the `generate_pdf` function, which formats and compiles the user's weight loss journey into a structured PDF document.

## Testing

Unit tests are included in `grimore_test.py` to ensure the accuracy of core functions. To run the tests, execute:

```bash
python -m unittest discover -s tests
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the repository**.
2. **Create a new branch** (`git checkout -b feature-branch-name`).
3. **Make your changes** and commit them (`git commit -m 'Add some feature'`).
4. **Push to the branch** (`git push origin feature-branch-name`).
5. **Open a Pull Request**.

## License

This project is licensed under the ISC License. See the `LICENSE` file for more details.

## Acknowledgments

Special thanks to the contributors and open-source libraries that made this project possible.

