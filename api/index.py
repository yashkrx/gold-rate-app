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

# Cache storage
last_known_data = {}

# Manual fallback data
MANUAL_FALLBACK_DATA = {
    'date': 'Saturday, Sunday',
    'price_24k': '1,58,212',
    'price_22k': '1,44,165',
    'price_18k': '1,18,433',
    'silver_price': '1,850',  # per 10g
    'currency': '₹',
    'trend': 'none'
}

@app.route('/')
def home():
    global last_known_data

    gold_data = {}
    error_message = None
    today_date = datetime.now().strftime("%d-%b-%Y")

    try:
        # Fetch Gold, Silver, USD/INR
        tickers = yf.Tickers("GC=F SI=F INR=X")

        gold_info = tickers.tickers['GC=F'].history(period="1d")
        silver_info = tickers.tickers['SI=F'].history(period="1d")
        usd_inr_info = tickers.tickers['INR=X'].history(period="1d")

        if not gold_info.empty and not usd_inr_info.empty:

            # ---------- GOLD ----------
            price_ounce_usd = gold_info['Close'].iloc[-1]
            usd_to_inr = usd_inr_info['Close'].iloc[-1]

            price_ounce_inr = price_ounce_usd * usd_to_inr

            base_price_24k = (price_ounce_inr / 31.1035) * 10.67
            base_22k = base_price_24k * (22 / 24)
            base_18k = base_price_24k * (18 / 24)

            tax_multiplier = 1.03

            final_24k = base_price_24k * tax_multiplier
            final_22k = base_22k * tax_multiplier
            final_18k = base_18k * tax_multiplier

            # ---------- SILVER ----------
            if not silver_info.empty:
                silver_price_ounce_usd = silver_info['Close'].iloc[-1]
                silver_price_ounce_inr = silver_price_ounce_usd * usd_to_inr

                silver_price_10g = (silver_price_ounce_inr / 31.1035) * 11.2
                silver_final = silver_price_10g * tax_multiplier

                silver_price = "{:,.0f}".format(silver_final)
            else:
                silver_price = MANUAL_FALLBACK_DATA['silver_price']

            # Final response
            gold_data = {
                'date': today_date,
                'price_24k': "{:,.0f}".format(final_24k),
                'price_22k': "{:,.0f}".format(final_22k),
                'price_18k': "{:,.0f}".format(final_18k),
                'silver_price': silver_price,
                'currency': '₹',
                'trend': 'up'
            }

            # Save cache
            last_known_data = gold_data.copy()

        else:
            if last_known_data:
                gold_data = last_known_data
                error_message = "Market data currently unavailable. Showing last fetched rates."
            else:
                gold_data = MANUAL_FALLBACK_DATA.copy()
                error_message = "Market data unavailable. Showing backup rates."

    except Exception:
        if last_known_data:
            gold_data = last_known_data
            error_message = "Live fetch failed. Showing last known rates."
        else:
            gold_data = MANUAL_FALLBACK_DATA.copy()
            error_message = "Live fetch failed. Showing manual backup rates."

    return render_template('index.html', data=gold_data, error=error_message)

# Important for Vercel
app = app
