from flask import Flask, request, jsonify, render_template
import sqlite3
import json
import os
import logging

app = Flask(__name__, static_folder='static')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database file path


# Get the directory of the current script (app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, 'data', 'mcq_database.db')
print(f"Attempting to connect to database at: {DATABASE_FILE}")

#
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    # ... rest of the function

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    question_number = request.args.get('question_number', type=int, default=1)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question_id, question_text, option_a, option_b, option_c, option_d, option_e FROM questions WHERE question_id >= ? LIMIT 1", (question_number,))
        row = cursor.fetchone()
        conn.close()

        if row:
            question_data = dict(row)
            question_data['options'] = [question_data['option_a'], question_data['option_b'], question_data['option_c'], question_data['option_d'], question_data['option_e']]
            return jsonify([question_data])  # Return as a list for consistency with frontend
        else:
            return jsonify([]) # Return empty list if no questions found
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch questions from the database."}), 500

@app.route('/update_question', methods=['POST'])
def update_question():
    data = request.get_json()
    question_id = data.get('question_id')
    correct_answer = data.get('correct_answer')
    flagged = data.get('flagged')
    try:
        print(f"Updating question {question_id}: Correct Answer = {correct_answer}, Flagged = {flagged}") # Added print statement
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE questions SET correct_answer = ?, flagged = ? WHERE question_id = ?", (correct_answer, 'yes' if flagged else 'no', question_id))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Question {question_id} updated successfully."})
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Failed to update the question in the database."}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)