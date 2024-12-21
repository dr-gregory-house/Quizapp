from flask import Flask, request, jsonify, render_template
import csv
import json
import os
import pandas as pd

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    csv_file = request.args.get('csv_file')
    question_number = request.args.get('question_number', type = int, default=1)
    if not csv_file:
        return jsonify({"error": "CSV file name not provided"}), 400
    try:
        data = read_csv_data(csv_file, question_number)
        print(data) # check the output here
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def read_csv_data(csv_file, question_number):
    data = []
    try:
         # Construct the full path to the CSV file
        csv_path = "C:\\Users\\anubh\\Desktop\\Project PSM\\Quiz\\mcq_csv_final.csv"
        print(f"CSV file path: {csv_path}") #check for correct file path.
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if int(row.get('Question Number')) >= int(question_number):
                    print(f"Processing row: {row}")  # Print for debugging.
                    question_id = row.get('Question Number')
                    question = row.get('Question')
                    options = [row.get('Option A'), row.get('Option B'), row.get('Option C'), row.get('Option D'), row.get('Option E')]
                    data.append({
                        "question_id": question_id,
                        "question": question,
                        "options": options,
                    })
                if len(data) >0:
                     break;
        print("Data after processing:")  # Print for debugging.
        print(data)
        return data
    except Exception as e:
        print(f"Error reading CSV: {e}")  # Print the error message
        return []  # Return an empty list to avoid further errors

@app.route('/update_question', methods=['POST'])
def update_question():
    data = request.get_json()
    csv_file = data.get('csv_file')
    if not csv_file:
        return jsonify({"error": "CSV file name not provided"}), 400
    question_id = data.get('question_id')
    correct_answer = data.get('correct_answer')
    flagged = data.get('flagged')
    try:
        update_csv_data(csv_file, question_id, correct_answer, flagged)
        return jsonify({"message": "CSV updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_csv_data(csv_file, question_id, correct_answer, flagged):
    try:
        csv_path = "C:\\Users\\anubh\\Desktop\\Project PSM\\Quiz\\mcq_csv_final.csv"  # Use the full file path
        df = pd.read_csv(csv_path)
        question_id_str = str(question_id)
        df.loc[df['Question Number'].astype(str) == question_id_str, 'Correct Answer'] = correct_answer
        print(f"Correct answer being written: {correct_answer}")  # Debugging print statement
        if flagged:
            df.loc[df['Question Number'].astype(str) == question_id_str, 'Flag'] = 'yes'
        else:
            df.loc[df['Question Number'].astype(str) == question_id_str, 'Flag'] = 'no'
        # Added quoting to handle commas in the 'Correct Answer' field
        df.to_csv(csv_path, index=False, quoting=csv.QUOTE_MINIMAL, quotechar='"')
        print("CSV file updated successfully")  # print for debugging
    except Exception as e:
        print(f"Error updating CSV: {e}")  # Print the error message

if __name__ == '__main__':
     app.run(host='0.0.0.0', debug=True)