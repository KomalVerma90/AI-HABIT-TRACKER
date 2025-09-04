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
@app.route('/view_habits')
def view_habits():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT * FROM habits")
    habits = c.fetchall()
    conn.close()
    return str(habits)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)