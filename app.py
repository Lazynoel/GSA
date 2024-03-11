from flask import Flask, request, jsonify, render_template
import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import random
import datetime


app = Flask(__name__)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
QUIZ_SPREADSHEET_ID = '1r2SedejaixElPsnKf5EDycHdnYeUmHC5mMYJAg1TkjI'
SCORES_SPREADSHEET_ID =  '1Ub7netOHTXfjIuSuNIri7DDq4vYTmaD3hjf9amq-lxw'
SERVICE_ACCOUNT_FILE = r'C:\Users\lazyn\my_flask_project\keys\mythic-byway-415505-8e23a1e224f7.json'

credentials_base64 = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json), scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-quiz', methods=['GET'])
def get_quiz():
    try:
        range_name = 'Sheet1!B2:C16'  # Adjusted for 15 questions
        result = service.spreadsheets().values().get(spreadsheetId=QUIZ_SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            return jsonify({'error': 'No quiz data found.'}), 404

        words = [row[0] for row in values]
        sentences = [row[1] for row in values]

        random.shuffle(words)
        random.shuffle(sentences)

        quiz_data = {'words': words, 'sentences': sentences}
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
        
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time

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
