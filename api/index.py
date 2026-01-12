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

@app.route('/')
def home():
    gold_data = {}
    error_message = None
    today_date = datetime.now().strftime("%d-%b-%Y")

    try:
        # 1. Fetch Gold Price (USD per Ounce) and USD/INR Rate
        # GC=F is Gold Futures, INR=X is USD to INR exchange rate
        tickers = yf.Tickers("GC=F INR=X")
        
        # Get the latest data
        gold_info = tickers.tickers['GC=F'].history(period="1d")
        usd_inr_info = tickers.tickers['INR=X'].history(period="1d")

        if not gold_info.empty and not usd_inr_info.empty:
            # Extract the latest closing prices
            price_ounce_usd = gold_info['Close'].iloc[-1]
            usd_to_inr = usd_inr_info['Close'].iloc[-1]
            
            # 2. Convert USD/Ounce to INR/10g
            # 1 Troy Ounce = 31.1035 grams
            price_ounce_inr = price_ounce_usd * usd_to_inr
            base_price_24k = (price_ounce_inr / 31.1035) * 10.6
            
            # 3. Calculate Purities
            base_22k = base_price_24k * (22/24)
            base_18k = base_price_24k * (18/24)
            
            # 4. Add 3% GST Tax
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
                'trend': 'up'
            }
        else:
            error_message = "Market data currently unavailable (Exchange Closed?)"

    except Exception as e:
        error_message = f"Internal Error: {str(e)}"

    return render_template('index.html', data=gold_data, error=error_message)

# Important for Vercel
app = app








