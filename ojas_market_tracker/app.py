from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

# -------------------------------
# SYMBOLS
# -------------------------------

symbols = {
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",

    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Shanghai Composite": "000001.SS",
    "Hang Seng": "^HSI",
    "NIFTY 50": "^NSEI",
    "Sensex": "^BSESN",

    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",

    "US 10Y Yield": "^TNX",
    "VIX": "^VIX",
    "USD Index (DXY)": "DX-Y.NYB",
}

# -------------------------------
# Helpers
# -------------------------------

def get_usd_inr():
    usd = yf.Ticker("USDINR=X")
    data = usd.history(period="1d")
    return data["Close"].iloc[-1]

def format_currency(value, currency):
    if currency == "INR":
        return f"₹ {value:,.2f}"
    elif currency == "USD":
        return f"$ {value:,.2f}"
    elif currency == "HKD":
        return f"HK$ {value:,.2f}"
    elif currency == "CNY":
        return f"¥ {value:,.2f}"
    elif currency == "%":
        return f"{value:.2f}%"
    else:
        return f"{value:,.2f}"

# -------------------------------
# AI LOGIC
# -------------------------------

def ai_prediction(change):
    if change > 1:
        return "▲ Bullish Momentum", "green"
    elif change < -1:
        return "▼ Bearish Pressure", "red"
    else:
        return "► Sideways / Neutral", "orange"

# -------------------------------
# Core Data
# -------------------------------

def get_data():
    data = {}
    usd_inr = get_usd_inr()

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="7d")

            if len(hist) < 2:
                continue

            current = hist["Close"].iloc[-1]
            previous = hist["Close"].iloc[-2]
            change = ((current - previous) / previous) * 100

            currency = "USD"

            if name in ["NIFTY 50", "Sensex"]:
                currency = "INR"
            elif name == "Hang Seng":
                currency = "HKD"
            elif name == "Shanghai Composite":
                currency = "CNY"
            elif name in ["US 10Y Yield", "VIX"]:
                currency = "%"
            elif name in ["Crude Oil", "Natural Gas", "Gold", "Silver", "Copper", "Wheat"]:
                current *= usd_inr
                currency = "INR"

            short_ai, color = ai_prediction(change)

            data[name] = {
                "price": format_currency(current, currency),
                "change": round(change, 2),
                "ai_5d": short_ai,
                "ai_1m": short_ai,
                "color": color
            }

        except:
            continue

    return data

# -------------------------------
# Risk Mode
# -------------------------------

def get_risk_mode(data):
    try:
        sp = data["S&P 500"]["change"]
        btc = data["Bitcoin"]["change"]
        gold = data["Gold"]["change"]
        vix = data["VIX"]["change"]

        if sp > 0 and btc > 0:
            return "RISK ON"
        elif gold > 0 and vix > 0:
            return "RISK OFF"
        else:
            return "NEUTRAL"
    except:
        return "NEUTRAL"

# -------------------------------
# ROUTE
# -------------------------------

@app.route("/")
def home():
    market_data = get_data()
    risk_mode = get_risk_mode(market_data)
    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")

    return render_template("index.html",
                           data=market_data,
                           time=now,
                           risk=risk_mode)

if __name__ == "__main__":
    app.run(debug=True)