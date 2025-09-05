import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pickle

# Load data from database
conn = sqlite3.connect('habits.db')
df = pd.read_sql_query("SELECT habit_name, date, success FROM habits WHERE user_id = 1", conn)
conn.close()

# Create features
df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek  # 0=Monday, 6=Sunday
le = LabelEncoder()
df['habit_encoded'] = le.fit_transform(df['habit_name'])

# Prepare data for model
X = df[['habit_encoded', 'day_of_week']]
y = df['success']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save model and encoder
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

print("Model trained and saved!")