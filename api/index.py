from flask import Flask, render_template
import yfinance as yf
import os
from datetime import datetime

# --- PATH FIX FOR VERCEL ---
base_dir = os.path.abspath(os.path.dirname(__file__))
if os.path.exists(os.path.join(base_dir, 'templates')):
    template_dir = os.path.join(base_dir, 'templates')
else:
    template_dir = os.path.abspath(os.path.join(base_dir, '..', 'templates'))

app = Flask(__name__, template_folder=template_dir)
# ---------------------------

# 1. Initialize a global variable to hold the cached data
last_known_data = {}

@app.route('/')
def home():
    # 2. Tell Python we are using the global variable
    global last_known_data 
    
    gold_data = {}
    error_message = None
    today_date = datetime.now().strftime("%d-%b-%Y")

    try:
        tickers = yf.Tickers("GC=F INR=X")
        
        gold_info = tickers.tickers['GC=F'].history(period="1d")
        usd_inr_info = tickers.tickers['INR=X'].history(period="1d")

        if not gold_info.empty and not usd_inr_info.empty:
            price_ounce_usd = gold_info['Close'].iloc[-1]
            usd_to_inr = usd_inr_info['Close'].iloc[-1]
            
            price_ounce_inr = price_ounce_usd * usd_to_inr
            base_price_24k = (price_ounce_inr / 31.1035) * 10.60
            
            base_22k = base_price_24k * (22/24)
            base_18k = base_price_24k * (18/24)
            
            tax_multiplier = 1.03
            final_24k = base_price_24k * tax_multiplier
            final_22k = base_22k * tax_multiplier
            final_18k = base_18k * tax_multiplier
            
            gold_data = {
                'date': today_date,
                'price_24k': "{:,.0f}".format(final_24k),
                'price_22k': "{:,.0f}".format(final_22k),
                'price_18k': "{:,.0f}".format(final_18k),
                'currency': '₹',
                'trend': 'up' # You might want to calculate this dynamically later!
            }
            
            # 3. Save the successful fetch to our global cache
            last_known_data = gold_data.copy()
            
        else:
            # 4. If yfinance is empty, try to use the cache
            if last_known_data:
                gold_data = last_known_data
                error_message = "Market data currently unavailable. Showing last known rates."
            else:
                error_message = "Market data unavailable and no previous data to show."

    except Exception as e:
        # 5. If an error occurs (like network failure), try to use the cache
        if last_known_data:
            gold_data = last_known_data
            error_message = f"Live fetch failed. Showing last known rates."
        else:
            error_message = f"Internal Error: {str(e)}"

    return render_template('index.html', data=gold_data, error=error_message)

# Important for Vercel
app = app

















