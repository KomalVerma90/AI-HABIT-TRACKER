import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle
from datetime import datetime
from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# Create database
conn = sqlite3.connect('habits.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY, user_id INTEGER, habit_name TEXT, date TEXT, success INTEGER)''')
conn.commit()
conn.close()

# Home page
@app.route('/')
def home():
    return "Welcome to AI Habit Tracker!"
# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return "User created!"
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Sign Up">
        </form>
    '''
# Add habit
@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        user_id = 1  # For now, hardcode user ID (change later)
        habit_name = request.form['habit_name']
        date = request.form['date']
        success = int(request.form['success'])
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("INSERT INTO habits (user_id, habit_name, date, success) VALUES (?, ?, ?, ?)", (user_id, habit_name, date, success))
        conn.commit()
        conn.close()
        return "Habit added!"
    return '''
        <form method="post">
            Habit Name: <input type="text" name="habit_name"><br>
            Date (YYYY-MM-DD): <input type="text" name="date"><br>
            Success (1 for yes, 0 for no): <input type="text" name="success"><br>
            <input type="submit" value="Add Habit">
        </form>
    '''
#view habbit
@app.route('/view_habits')
def view_habits():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT * FROM habits")
    habits = c.fetchall()
    conn.close()
    return str(habits)
#prediction
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        habit_name = request.form['habit_name']
        date = request.form['date']
        try:
            # Load model and encoder
            with open('model.pkl', 'rb') as f:
                model = pickle.load(f)
            with open('label_encoder.pkl', 'rb') as f:
                le = pickle.load(f)
            # Prepare input
            day_of_week = pd.to_datetime(date).dayofweek
            habit_encoded = le.transform([habit_name])[0]
            X_new = [[habit_encoded, day_of_week]]
            # Predict
            prob = model.predict_proba(X_new)[0][1] * 100
            return f"Predicted success for {habit_name} on {date}: {prob:.1f}%"
        except Exception as e:
            return f"Error: {str(e)}"
    return '''
        <form method="post">
            Habit Name: <input type="text" name="habit_name"><br>
            Date (YYYY-MM-DD): <input type="text" name="date"><br>
            <input type="submit" value="Predict">
        </form>
    '''
@app.route('/chart')
def chart():
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import sqlite3
    import pandas as pd
    import base64
    from io import BytesIO

    conn = sqlite3.connect('habits.db')
    df = pd.read_sql_query("SELECT habit_name, AVG(success) as success_rate FROM habits WHERE user_id = 1 GROUP BY habit_name", conn)
    conn.close()
    
    plt.figure(figsize=(8, 4))
    plt.bar(df['habit_name'], df['success_rate'], color='#1f77b4')
    plt.xlabel('Habit')
    plt.ylabel('Success Rate')
    plt.title('Habit Success Rates')
    plt.xticks(rotation=45)
    
    # Save plot to memory
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return f'<img src="data:image/png;base64,{img_str}" alt="Habit Chart">'


# Run the app
if __name__ == '__main__':
    app.run(debug=True)