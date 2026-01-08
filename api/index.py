from flask import Flask, render_template
import os
import requests
from datetime import datetime

# --- MAGIC FIX FOR VERCEL TEMPLATE ERROR ---
# This tells Python: "Look for the templates folder in the main directory, not just the current folder"
base_dir = os.path.abspath(os.path.dirname(__file__))

# Check if 'templates' is in the current folder, or one level up
if os.path.exists(os.path.join(base_dir, 'templates')):
    template_dir = os.path.join(base_dir, 'templates')
else:
    # If we are in 'api/', go up one level to find 'templates'
    template_dir = os.path.abspath(os.path.join(base_dir, '..', 'templates'))

app = Flask(__name__, template_folder=template_dir)
# -------------------------------------------

# CONFIGURATION
API_KEY = os.environ.get('GOLD_API_KEY')
BASE_URL = 'https://www.goldapi.io/api/XAU/INR'

@app.route('/')
def home():
    gold_data = {}
    error_message = None
    today_date = datetime.now().strftime("%d-%b-%Y")

    if not API_KEY:
        # Pass empty data to prevent crash if key is missing
        return render_template('index.html', error="System Error: API Key missing.", data={})

    try:
        headers = {
            "x-access-token": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(BASE_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # SAFE CHECK: Ensure price exists
            if 'price' in data:
                price_ounce = data.get('price')
                price_24k_10g = (price_ounce / 31.1035) * 10
                
                price_22k_10g = price_24k_10g * (22/24)
                price_18k_10g = price_24k_10g * (18/24)
                
                gold_data = {
                    'date': today_date,
                    'price_24k': "{:,.0f}".format(price_24k_10g),
                    'price_22k': "{:,.0f}".format(price_22k_10g),
                    'price_18k': "{:,.0f}".format(price_18k_10g),
                    'currency': '₹',
                    'trend': 'up' 
                }
            else:
                error_message = "API returned data but price is missing."
        else:
            error_message = f"Error fetching data: {response.status_code}"

    except Exception as e:
        error_message = f"Internal Error: {str(e)}"

    return render_template('index.html', data=gold_data, error=error_message)

# Important for Vercel
app = app
