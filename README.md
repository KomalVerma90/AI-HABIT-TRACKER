# AI-HABIT-TRACKER
# AI Habit Tracker
![GitHub last commit](https://img.shields.io/github/last-commit/KomalVerma90/AI-HABIT-TRACKER)

A Flask-based web application designed to help users track habits, predict success rates using machine learning, and visualize progress with interactive UI elements. Built as a personal project to explore web development, UX design, and AI integration.

## Features
- **Habit Tracking**: Add and view habits with 3D flip cards showing success status.
- **Success Prediction**: Predict habit success probability with animated progress bars.
- **Progress Visualization**: Animated progress bars in habit view.
- **User Feedback**: Feedback form on the homepage.
- **Responsive Design**: Gradient background and clean layout.

### Installation
1. Clone the repository:
   git clone https://github.com/KomalVerma90/AI-HABIT-TRACKER.git
   cd AI-HABIT-TRACKER

## Screenshots
<img src="screenshots/home.png" alt="Home Page">
<img src="screenshots/view_habits.png" alt="View Habits">
<img src="screenshots/predict.png" alt="Predict Success">


## Development Journey
Day 1: Set up Flask app with basic routes (home, sign-up, add habit).

Day 2: Added 3D flip cards for habit viewing and a gradient background.

Day 3: Integrated 3D sphere visualization (later replaced due to issues) and introduced progress bars.

Day 4: Enhanced with progress bars for predictions, added feedback form, and fixed prediction errors for unseen labels.

## Technologies
Backend: Python, Flask

Data: SQLite, Pandas, Scikit-learn

Frontend: HTML, CSS (animations), JavaScript

Version Control: Git, GitHub

## Challenges & Solutions
3D Visualization: Faced issues with Three.js (404 errors, ReferenceError). Switched to progress bars for reliability.

Unseen Labels: Encountered prediction errors for new habits (e.g., 'meditate'). Implemented a fallback encoding.

## Future Improvements
Future Improvements
Retrain the model with more habit data for accurate predictions.
Add user authentication.
Implement Chart.js for advanced visualizations.
Deploy the app using Heroku or Render.
