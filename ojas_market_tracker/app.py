from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

# ---------------------------------
# SYMBOLS
# ---------------------------------

symbols = {
    # Commodities (convert to INR)
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",

    # Equity Indices (native currency)
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Shanghai Composite": "000001.SS",
    "Hang Seng": "^HSI",
    "NIFTY 50": "^NSEI",
    "Sensex": "^BSESN",

    # Crypto
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",

    # Macro
    "US 10Y Yield": "^TNX",
    "VIX": "^VIX",
    "USD Index (DXY)": "DX-Y.NYB"
}


# ---------------------------------
# SAFE USDINR FETCH
# ---------------------------------

def get_usd_inr():
    try:
        usd = yf.Ticker("USDINR=X")
        data = usd.history(period="1d")
        return float(data["Close"].iloc[-1])
    except:
        return 83.0  # fallback safe rate


# ---------------------------------
# FORMATTER
# ---------------------------------

def format_price(value, currency):
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


# ---------------------------------
# CORE DATA
# ---------------------------------

def get_data():
    data = {}
    usd_inr = get_usd_inr()

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")

            if len(hist) < 2:
                continue

            current = float(hist["Close"].iloc[-1])
            previous = float(hist["Close"].iloc[-2])
            change = ((current - previous) / previous) * 100

            sentiment = "Bullish 📈" if change > 0 else "Bearish 📉"

            currency = "USD"

            # Native currencies
            if name in ["NIFTY 50", "Sensex"]:
                currency = "INR"

            elif name == "Hang Seng":
                currency = "HKD"

            elif name == "Shanghai Composite":
                currency = "CNY"

            elif name in ["US 10Y Yield", "VIX"]:
                currency = "%"

            # Convert commodities to INR
            if name in ["Crude Oil", "Natural Gas", "Gold", "Silver", "Copper", "Wheat"]:
                current = current * usd_inr
                currency = "INR"

            # Gold per 10g
            if name == "Gold":
                current = (current / 31.1035) * 10

            # Silver per kg
            if name == "Silver":
                current = (current / 31.1035) * 1000

            data[name] = {
                "price": format_price(current, currency),
                "change": round(change, 2),
                "sentiment": sentiment
            }

        except:
            data[name] = {
                "price": "N/A",
                "change": 0,
                "sentiment": "Data Error"
            }

    # Add RBI Repo (static reference)
    data["RBI Repo Rate"] = {
        "price": "6.50%",
        "change": 0,
        "sentiment": "Stable"
    }

    return data


# ---------------------------------
# RISK MODE
# ---------------------------------

def get_risk_mode(data):
    try:
        sp = data["S&P 500"]["change"]
        btc = data["Bitcoin"]["change"]
        gold = data["Gold"]["change"]
        vix = data["VIX"]["change"]

        if sp > 0 and btc > 0:
            return "RISK ON 🟢"
        elif gold > 0 and vix > 0:
            return "RISK OFF 🔴"
        else:
            return "NEUTRAL 🟡"
    except:
        return "NEUTRAL 🟡"


# ---------------------------------
# ROUTE
# ---------------------------------

@app.route("/")
def home():
    try:
        market_data = get_data()
        risk_mode = get_risk_mode(market_data)
    except:
        market_data = {}
        risk_mode = "DATA TEMPORARILY UNAVAILABLE"

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")

    return render_template(
        "index.html",
        data=market_data,
        time=now,
        risk=risk_mode
    )