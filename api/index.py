from flask import Flask, render_template
import os
import requests
from datetime import datetime

app = Flask(__name__)

# CONFIGURATION
API_KEY = os.environ.get('GOLD_API_KEY')
BASE_URL = 'https://www.goldapi.io/api/XAU/INR'

@app.route('/')
def home():
    gold_data = {}
    error_message = None
    today_date = datetime.now().strftime("%d-%b-%Y") # e.g., 08-Jan-2026

    if not API_KEY:
        return render_template('index.html', error="API Key missing.")

    try:
        headers = {
            "x-access-token": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(BASE_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Base calculation: Price per 10 grams 24K
            price_ounce = data.get('price')
            price_24k_10g = (price_ounce / 31.1035) * 10
            
            # Calculate other purities commonly shown on jewelry sites
            price_22k_10g = price_24k_10g * (22/24)
            price_18k_10g = price_24k_10g * (18/24)
            
            gold_data = {
                'date': today_date,
                'price_24k': "{:,.0f}".format(price_24k_10g),
                'price_22k': "{:,.0f}".format(price_22k_10g),
                'price_18k': "{:,.0f}".format(price_18k_10g),
                'currency': '₹',
                # Mock trend for design purposes (up/down arrow)
                'trend': 'up' if data.get('price_change_24h', 0) > 0 else 'down'
            }
        else:
            error_message = f"Error fetching data: {response.status_code}"

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"

    return render_template('index.html', data=gold_data, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)