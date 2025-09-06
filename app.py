from flask import Flask, request
import sqlite3
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle
from datetime import datetime, date
import json

app = Flask(__name__)


@app.route('/')
def home():
    return '''
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/js/app.js"></script>
        <div class="container">
            <h1>Welcome to AI Habit Tracker!</h1>
            <div class="nav-links">
                <a href="/signup">Sign Up</a> |
                <a href="/add_habit">Add Habit</a> |
                <a href="/view_habits">View Habits</a> |
                <a href="/predict">Predict Success</a> |
                <a href="/chart">View Chart</a> |
                <a href="/reminders">Reminders</a>
            </div>
        </div>
    '''


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Error</h1>
                    <p>Please enter a username.</p>
                    <a href="/signup">Back</a> | <a href="/">Home</a>
                </div>
            '''
        try:
            conn = sqlite3.connect('habits.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            conn.close()
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Success</h1>
                    <p>User signed up!</p>
                    <a href="/">Home</a>
                </div>
            '''
        except Exception as e:
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Error</h1>
                    <p>Database error: {}.</p>
                    <a href="/signup">Back</a> | <a href="/">Home</a>
                </div>
            '''.format(str(e))
    return '''
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/js/app.js"></script>
        <div class="container">
            <h1>Sign Up</h1>
            <form method="post">
                Username: <input type="text" name="username"><br>
                <input type="submit" value="Sign Up">
            </form>
        </div>
    '''


@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        habit_name = request.form.get('habit_name', '').strip()
        date_str = request.form.get('date', '').strip()
        success = request.form.get('success', '').strip()
        if not all([habit_name, date_str, success]):
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Error</h1>
                    <p>Please fill all fields.</p>
                    <a href="/add_habit">Back</a> | <a href="/">Home</a>
                </div>
            '''
        try:
            success = int(success)
            if success not in [0, 1]:
                raise ValueError("Success must be 0 or 1")
            conn = sqlite3.connect('habits.db')
            c = conn.cursor()
            c.execute(
                "INSERT INTO habits (user_id, habit_name, date, success) VALUES (?, ?, ?, ?)",
                (1, habit_name, date_str, success)
            )
            conn.commit()
            conn.close()
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Success</h1>
                    <p>Habit added!</p>
                    <a href="/add_habit">Add Another</a> | <a href="/">Home</a>
                </div>
            '''
        except Exception as e:
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Error</h1>
                    <p>Error: {}.</p>
                    <a href="/add_habit">Back</a> | <a href="/">Home</a>
                </div>
            '''.format(str(e))
    return '''
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/js/app.js"></script>
        <div class="container">
            <h1>Add Habit</h1>
            <form method="post">
                Habit Name: <input type="text" name="habit_name"><br>
                Date (YYYY-MM-DD): <input type="text" name="date"><br>
                Success (0 or 1): <input type="text" name="success"><br>
                <input type="submit" value="Add Habit">
            </form>
        </div>
    '''


@app.route('/view_habits')
def view_habits():
    try:
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute(
            "SELECT habit_name, COUNT(*) as total, SUM(success) as successes "
            "FROM habits WHERE user_id = 1 GROUP BY habit_name"
        )
        habits = c.fetchall()
        conn.close()
        if not habits:
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Your Habits</h1>
                    <p>No habits found. Add some via <a href='/add_habit'>Add Habit</a>.</p>
                    <a href="/">Home</a>
                </div>
            '''
        cards_and_progress = ''
        for habit in habits:
            habit_name, total, successes = habit
            success_rate = (successes / total * 100) if total > 0 else 0
            cards_and_progress += f'''
                <div class="card">
                    <div class="card-inner">
                        <div class="card-front">
                            <p>{habit_name} (Total: {total})</p>
                        </div>
                        <div class="card-back">
                            <p>Success Rate: {success_rate:.1f}%</p>
                        </div>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress" style="--progress-width: {success_rate}%;" data-label="{success_rate:.1f}%"></div>
                </div>
            '''
        return f'''
            <link rel="stylesheet" href="/static/style.css">
            <script src="/static/js/app.js"></script>
            <div class="container">
                <h1>Your Habits</h1>
                {cards_and_progress}
                <a href="/">Home</a>
            </div>
            <script>
                document.querySelectorAll('.progress').forEach(bar => {{
                    bar.classList.add('animate');
                }});
            </script>
        '''
    except Exception as e:
        return '''
            <link rel="stylesheet" href="/static/style.css">
            <script src="/static/js/app.js"></script>
            <div class="container">
                <h1>Error</h1>
                <p>Database error: {}.</p>
                <a href="/">Home</a>
            </div>
        '''.format(str(e))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        habit_name = request.form.get('habit_name', '').strip()
        date_str = request.form.get('date', '').strip()
        if not all([habit_name, date_str]):
            return '''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Error</h1>
                    <p>Please fill all fields.</p>
                    <a href="/predict">Back</a> | <a href="/">Home</a>
                </div>
            '''
        try:
            with open('model.pkl', 'rb') as f:
                model = pickle.load(f)
            with open('label_encoder.pkl', 'rb') as f:
                le = pickle.load(f)
            day_of_week = pd.to_datetime(date_str).dayofweek
            habit_encoded = le.transform([habit_name])[0]
            X_new = [[habit_encoded, day_of_week]]
            prob = model.predict_proba(X_new)[0][1] * 100
            return f'''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Prediction Result</h1>
                    <p>Predicted success for {habit_name} on {date_str}: {prob:.1f}%</p>
                    <a href="/predict">Back</a> | <a href="/">Home</a>
                </div>
            '''
        except Exception as e:
            return f'''
                <link rel="stylesheet" href="/static/style.css">
                <script src="/static/js/app.js"></script>
                <div class="container">
                    <h1>Error</h1>
                    <p>Error: {str(e)}</p>
                    <a href="/predict">Back</a> | <a href="/">Home</a>
                </div>
            '''
    return '''
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/js/app.js"></script>
        <div class="container">
            <h1>Predict Habit Success</h1>
            <form method="post">
                Habit Name: <input type="text" name="habit_name"><br>
                Date (YYYY-MM-DD): <input type="text" name="date"><br>
                <input type="submit" value="Predict">
            </form>
        </div>
    '''


@app.route('/chart')
def chart():
    return '''
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/js/app.js"></script>
        <div class="container">
            <h1>Chart (Placeholder)</h1>
            <p>Chart feature is temporarily replaced with progress bars in View Habits.</p>
            <a href="/">Home</a>
        </div>
    '''


@app.route('/reminders')
def reminders():
    try:
        today = date.today().strftime('%Y-%m-%d')
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute(
            "SELECT habit_name, date FROM habits WHERE date = ? AND user_id = 1",
            (today,)
        )
        habits = c.fetchall()
        conn.close()
        table_rows = ''.join(f'<tr><td>{h[0]}</td><td>{h[1]}</td></tr>' for h in habits)
        return f'''
            <link rel="stylesheet" href="/static/style.css">
            <script src="/static/js/app.js"></script>
            <div class="container">
                <h1>Reminders for {today}</h1>
                <table>
                    <tr><th>Habit</th><th>Date</th></tr>
                    {table_rows if habits else "<tr><td colspan='2'>No habits due today.</td></tr>"}
                </table>
                <a href="/">Home</a>
            </div>
        '''
    except Exception as e:
        return f'''
            <link rel="stylesheet" href="/static/style.css">
            <script src="/static/js/app.js"></script>
            <div class="container">
                <h1>Error</h1>
                <p>Database error: {str(e)}</p>
                <a href="/">Home</a>
            </div>
        '''


if __name__ == '__main__':
    app.run(debug=True)
