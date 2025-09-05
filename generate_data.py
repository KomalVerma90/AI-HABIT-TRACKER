import sqlite3
import random
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('habits.db')
c = conn.cursor()

# Sample habits and dates
habits = ['Morning Walk', 'Drink Water', 'Read Book', 'Meditate', 'Exercise']
start_date = datetime(2025, 4, 1)
for i in range(50):  # Add 50 fake habits
    habit_name = random.choice(habits)
    date = (start_date + timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
    success = random.randint(0, 1)
    c.execute("INSERT INTO habits (user_id, habit_name, date, success) VALUES (?, ?, ?, ?)",
              (1, habit_name, date, success))
conn.commit()
conn.close()
print("Added 50 fake habits!")