import os
import base64
import json
from flask import Flask, request, jsonify, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
import random
import datetime
import pytz


app = Flask(__name__)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
QUIZ_SPREADSHEET_ID = '1r2SedejaixElPsnKf5EDycHdnYeUmHC5mMYJAg1TkjI'
SCORES_SPREADSHEET_ID =  '1Ub7netOHTXfjIuSuNIri7DDq4vYTmaD3hjf9amq-lxw'

# Check if the environment variable is set
if 'GOOGLE_APPLICATION_CREDENTIALS_BASE64' in os.environ:
    credentials_base64 = os.environ['GOOGLE_APPLICATION_CREDENTIALS_BASE64']
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json), scopes=SCOPES)
else:
    raise ValueError("The GOOGLE_APPLICATION_CREDENTIALS_BASE64 environment variable is not set.")


service = build('sheets', 'v4', credentials=credentials)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/quiz1')
def quiz1():
    return render_template('quiz1.html')
    
@app.route('/quiz2')
def quiz2():
    return render_template('quiz2.html')
    
@app.route('/get-quiz/<quiz_id>', methods=['GET'])  # Added the route parameter quiz_id
def get_quiz(quiz_id):  # Added the function parameter quiz_id
    try:
        # Adjust the range or spreadsheet based on the quiz_id
        if quiz_id == 'quiz1':
            range_name = 'Sheet1!B2:D16'  # Quiz 1 range
        elif quiz_id == 'quiz2':
            range_name = 'Sheet2!B2:D16'  # Quiz 2 range
        else:
            return jsonify({'error': 'Invalid quiz ID.'}), 400

        result = service.spreadsheets().values().get(spreadsheetId=QUIZ_SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            return jsonify({'error': 'No quiz data found.'}), 404

        words = [row[0] for row in values]
        sentences = [row[1] for row in values]
        answers = [row[2] for row in values]

        random.shuffle(words)

        quiz_data = {'words': words, 'sentences': sentences, 'answers': answers}
        return jsonify(quiz_data), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch quiz data.'}), 500


@app.route('/submit-score', methods=['POST'])
def submit_score():
    try:
        content = request.get_json()
        name = content['name']
        score = content['score']
        seoul_timezone = pytz.timezone('Asia/Seoul')
        
        time_now = datetime.datetime.now(seoul_timezone).strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the data to be inputted: [Name, Score, Timestamp]
        values = [[name, score, time_now]]
        body = {'values': values}
        result = service.spreadsheets().values().append(
            spreadsheetId=SCORES_SPREADSHEET_ID,
            range='sheet1!A:C',  # Adjust the range based on your sheet's layout
            valueInputOption='USER_ENTERED',
            body=body).execute()

        return jsonify({'result': 'Score submitted successfully.'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to submit score.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
