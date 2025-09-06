from flask import Flask, request
import sqlite3
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <link rel="stylesheet" href="/static/style.css">
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
        username = request.form['username']
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        conn.close()
        return '''
            <link rel="stylesheet" href="/static/style.css">
            <div class="container">
                <h1>Success</h1>
                <p>User signed up!</p>
                <a href="/">Home</a>
            </div>
        '''
    return '''
        <link rel="stylesheet" href="/static/style.css">
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
        habit_name = request.form['habit_name']
        date_val = request.form['date']
        success = int(request.form['success'])
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("INSERT INTO habits (user_id, habit_name, date, success) VALUES (?, ?, ?, ?)",
                  (1, habit_name, date_val, success))
        conn.commit()
        conn.close()
        return '''
            <link rel="stylesheet" href="/static/style.css">
            <div class="container">
                <h1>Success</h1>
                <p>Habit added!</p>
                <a href="/add_habit">Add Another</a> | <a href="/">Home</a>
            </div>
        '''
    return '''
        <link rel="stylesheet" href="/static/style.css">
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
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT * FROM habits WHERE user_id = 1")
    habits = c.fetchall()
    conn.close()
    table_rows = ''.join(f'<tr><td>{h[2]}</td><td>{h[3]}</td><td>{"Success" if h[4] else "Failed"}</td></tr>' for h in habits)
    return f'''
        <link rel="stylesheet" href="/static/style.css">
        <div class="container">
            <h1>Your Habits</h1>
            <table>
                <tr><th>Habit</th><th>Date</th><th>Status</th></tr>
                {table_rows if habits else "<tr><td colspan='3'>No habits found.</td></tr>"}
            </table>
            <a href="/">Home</a>
        </div>
    '''

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        habit_name = request.form['habit_name']
        date_val = request.form['date']
        try:
            with open('model.pkl', 'rb') as f:
                model = pickle.load(f)
            with open('label_encoder.pkl', 'rb') as f:
                le = pickle.load(f)
            day_of_week = pd.to_datetime(date_val).dayofweek
            habit_encoded = le.transform([habit_name])[0]
            X_new = [[habit_encoded, day_of_week]]
            prob = model.predict_proba(X_new)[0][1] * 100
            return f'''
                <link rel="stylesheet" href="/static/style.css">
                <div class="container">
                    <h1>Prediction Result</h1>
                    <p>Predicted success for {habit_name} on {date_val}: {prob:.1f}%</p>
                    <a href="/predict">Back</a> | <a href="/">Home</a>
                </div>
            '''
        except Exception as e:
            return f'''
                <link rel="stylesheet" href="/static/style.css">
                <div class="container">
                    <h1>Error</h1>
                    <p>Error: {str(e)}</p>
                    <a href="/predict">Back</a> | <a href="/">Home</a>
                </div>
            '''
    return '''
        <link rel="stylesheet" href="/static/style.css">
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
    conn = sqlite3.connect('habits.db')
    df = pd.read_sql_query("SELECT habit_name, AVG(success) as success_rate FROM habits WHERE user_id = 1 GROUP BY habit_name", conn)
    conn.close()

    plt.figure(figsize=(8, 4))
    plt.bar(df['habit_name'], df['success_rate'], color='#ff6f61')
    plt.xlabel('Habit')
    plt.ylabel('Success Rate')
    plt.title('Habit Success Rates')
    plt.xticks(rotation=45)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return f'''
        <link rel="stylesheet" href="/static/style.css">
        <div class="container">
            <h1>Habit Success Chart</h1>
            <img src="data:image/png;base64,{img_str}" alt="Habit Chart">
            <p><a href="/">Home</a></p>
        </div>
    '''

@app.route('/reminders')
def reminders():
    today = date.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT habit_name, date FROM habits WHERE date = ? AND user_id = 1", (today,))
    habits = c.fetchall()
    conn.close()
    table_rows = ''.join(f'<tr><td>{h[0]}</td><td>{h[1]}</td></tr>' for h in habits)
    return f'''
        <link rel="stylesheet" href="/static/style.css">
        <div class="container">
            <h1>Reminders for {today}</h1>
            <table>
                <tr><th>Habit</th><th>Date</th></tr>
                {table_rows if habits else "<tr><td colspan='2'>No habits due today.</td></tr>"}
            </table>
            <a href="/">Home</a>
        </div>
    '''

if __name__ == '__main__':
    app.run(debug=True)
