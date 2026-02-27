from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

symbols = {
    # Commodities
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",

    # Indices
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

    # Risk / Macro
    "US 10Y Yield": "^TNX",
    "VIX": "^VIX",
    "USD Index (DXY)": "DX-Y.NYB",
}

def get_usd_inr():
    usd = yf.Ticker("USDINR=X")
    data = usd.history(period="1d")
    return data["Close"].iloc[-1]

def ai_prediction(change):
    if change > 1:
        return "▲ Bullish Momentum", "green"
    elif change < -1:
        return "▼ Bearish Pressure", "red"
    else:
        return "► Sideways / Neutral", "orange"

def get_data():
    data = {}
    usd_inr = get_usd_inr()

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")

            if len(hist) < 2:
                continue

            current = hist["Close"].iloc[-1]
            previous = hist["Close"].iloc[-2]
            change = ((current - previous) / previous) * 100

            unit = ""
            display_price = ""

            # ---------------- COMMODITIES ----------------

            if name == "Gold":
                # USD per ounce → INR per 10g
                price_inr = current * usd_inr
                price_10g = (price_inr / 31.1035) * 10
                display_price = f"₹ {price_10g:,.2f}"
                unit = "per 10g"

            elif name == "Silver":
                # USD per ounce → INR per kg
                price_inr = current * usd_inr
                price_kg = (price_inr / 31.1035) * 1000
                display_price = f"₹ {price_kg:,.2f}"
                unit = "per kg"

            elif name == "Crude Oil":
                price_inr = current * usd_inr
                display_price = f"₹ {price_inr:,.2f}"
                unit = "per barrel"

            elif name == "Natural Gas":
                price_inr = current * usd_inr
                display_price = f"₹ {price_inr:,.2f}"
                unit = "per MMBtu"

            elif name == "Copper":
                price_inr = current * usd_inr
                display_price = f"₹ {price_inr:,.2f}"
                unit = "per pound"

            elif name == "Wheat":
                price_inr = current * usd_inr
                display_price = f"₹ {price_inr:,.2f}"
                unit = "per bushel"

            # ---------------- INDICES ----------------

            elif name in ["NIFTY 50", "Sensex"]:
                display_price = f"₹ {current:,.2f}"
                unit = "Index"

            elif name == "Hang Seng":
                display_price = f"HK$ {current:,.2f}"
                unit = "Index"

            elif name == "Shanghai Composite":
                display_price = f"¥ {current:,.2f}"
                unit = "Index"

            elif name in ["S&P 500", "Dow Jones", "NASDAQ"]:
                display_price = f"{current:,.2f}"
                unit = "Index"

            # ---------------- CRYPTO ----------------

            elif name in ["Bitcoin", "Ethereum"]:
                display_price = f"$ {current:,.2f}"
                unit = "USD"

            # ---------------- RATES ----------------

            elif name in ["US 10Y Yield", "VIX"]:
                display_price = f"{current:.2f}%"
                unit = "Percent"

            elif name == "USD Index (DXY)":
                display_price = f"{current:,.2f}"
                unit = "Index"

            short_ai, color = ai_prediction(change)

            data[name] = {
                "price": display_price,
                "unit": unit,
                "change": round(change, 2),
                "ai_5d": short_ai,
                "ai_1m": short_ai,
                "color": color
            }

        except:
            continue

    return data

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