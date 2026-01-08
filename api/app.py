from flask import Flask, render_template
import requests
import os

# Point to the 'templates' folder in the parent directory
app = Flask(__name__, template_folder='../templates')

# Get API Key from Environment Variable (Secure way)
API_KEY = os.environ.get('goldapi-424wtsmk4gjonm-io')
BASE_URL = 'https://www.goldapi.io/api/XAU/USD'

@app.route('/')
def home():
    gold_data = {}
    error_message = None

    if not API_KEY:
        return render_template('index.html', error="API Key missing in configuration.")

    try:
        headers = {
            "x-access-token": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(BASE_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            gold_data = {
                'price': round(data.get('price'), 2),
                'currency': 'USD',
                'symbol': 'XAU',
                'low_price': round(data.get('low_price'), 2),
                'high_price': round(data.get('high_price'), 2)
            }
        else:
            error_message = f"Error fetching data: {response.status_code}"

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"

    return render_template('index.html', data=gold_data, error=error_message)

# Vercel requires this for the serverless function to work
app = app