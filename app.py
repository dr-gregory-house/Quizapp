from flask import Flask, request, jsonify, render_template
import sqlite3
import json
import os
import logging
from datetime import datetime
import random
from waitress import serve

class ApplicationLogger(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(fmt='{message}', style='{')
        
        # Color codes
        self.BLUE = '\033[38;5;39m'    # Server info
        self.GREEN = '\033[38;5;82m'    # Success/Normal operations
        self.YELLOW = '\033[38;5;226m'  # Warnings/Debug
        self.RED = '\033[38;5;196m'     # Errors
        self.PURPLE = '\033[38;5;171m'  # Database operations
        self.CYAN = '\033[38;5;51m'     # Client requests
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
        self.DIM = '\033[2m'

    def _format_server_start(self, msg):
        border = f"{self.BLUE}{'═' * 50}{self.RESET}"
        return f"\n{border}\n{self.BLUE}{self.BOLD}✧ {msg}{self.RESET}\n{border}\n"

    def _format_request(self, record):
        ip = getattr(record, 'ip', 'unknown')
        endpoint = getattr(record, 'endpoint', '')
        return f"{self.CYAN}► [{ip}] {endpoint}{self.RESET}"

    def _format_database(self, msg):
        return f"{self.PURPLE}⌬ DB: {msg}{self.RESET}"

    def _format_error(self, msg):
        return f"{self.RED}{self.BOLD}✖ ERROR: {msg}{self.RESET}"

    def format(self, record):
        timestamp = self.formatTime(record, datefmt='%H:%M:%S')
        
        # Get the log message
        msg = record.getMessage()
        
        # Format based on log type (using custom record attributes)
        log_type = getattr(record, 'log_type', '')
        
        if log_type == 'server_start':
            formatted_msg = self._format_server_start(msg)
        elif log_type == 'request':
            formatted_msg = self._format_request(record)
        elif log_type == 'database':
            formatted_msg = self._format_database(msg)
        elif record.levelno >= logging.ERROR:
            formatted_msg = self._format_error(msg)
        else:
            formatted_msg = f"{self.GREEN}→ {msg}{self.RESET}"

        return f"{self.DIM}[{timestamp}]{self.RESET} {formatted_msg}"

# Create filter to add custom attributes
class RequestFilter(logging.Filter):
    def filter(self, record):
        record.ip = request.remote_addr if request else 'localhost'
        record.endpoint = request.endpoint if request else ''
        return True

app = Flask(__name__, static_folder='static')

# Setup logging
logger = logging.getLogger(__name__)
formatter = ApplicationLogger()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.addFilter(RequestFilter())

# Database file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, 'data', 'mcq_database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    logger.info("New client connection", extra={'log_type': 'request'})
    return render_template('index.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    question_number = request.args.get('question_number', type=int, default=1)
    logger.info(f"Fetching question #{question_number}", extra={'log_type': 'request'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE question_id >= ? LIMIT 1", (question_number,))
        row = cursor.fetchone()
        conn.close()

        if row:
            question_data = dict(row)
            logger.info(f"Retrieved question {question_number}", extra={'log_type': 'database'})
            return jsonify([question_data])
        else:
            logger.warning(f"No question found with ID {question_number}", extra={'log_type': 'database'})
            return jsonify([])
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/update_question', methods=['POST'])
def update_question():
    data = request.get_json()
    question_id = data.get('question_id')
    correct_answer = data.get('correct_answer')
    flagged = data.get('flagged')
    
    logger.info(
        f"Question {question_id} update: Answer={correct_answer}, Flagged={flagged}",
        extra={'log_type': 'request'}
    )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE questions SET correct_answer = ?, flagged = ? WHERE question_id = ?",
            (correct_answer, 'yes' if flagged else 'no', question_id)
        )
        conn.commit()
        conn.close()
        logger.info(f"Question {question_id} updated successfully", extra={'log_type': 'database'})
        return jsonify({"message": "Update successful"})
    except sqlite3.Error as e:
        logger.error(f"Failed to update question {question_id}: {str(e)}")
        return jsonify({"error": "Update failed"}), 500

if __name__ == '__main__':
    logger.info("Starting MCQ Review Server", extra={'log_type': 'server_start'})
    logger.info(f"Database location: {DATABASE_FILE}", extra={'log_type': 'server_start'})
    serve(app, host='0.0.0.0', port=5000)