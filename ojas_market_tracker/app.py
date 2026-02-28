from flask import Flask, render_template
import yfinance as yf
import datetime
import pandas as pd
import numpy as np

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

    # Macro
    "US 10Y Yield": "^TNX",
    "VIX": "^VIX",
    "USD Index (DXY)": "DX-Y.NYB",
}

def get_usd_inr():
    usd = yf.Ticker("USDINR=X")
    data = usd.history(period="1d")
    return data["Close"].iloc[-1]

# -------- MOVING AVERAGE TREND --------

def moving_average_signal(df):
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    latest = df.iloc[-1]

    if latest["MA20"] > latest["MA50"] and latest["Close"] > latest["MA20"]:
        return "▲ Bullish Trend", "green"
    elif latest["MA20"] < latest["MA50"] and latest["Close"] < latest["MA20"]:
        return "▼ Bearish Trend", "red"
    else:
        return "► Neutral Structure", "orange"

# -------- VOLATILITY CALCULATION --------

def calculate_volatility(df):
    df["Returns"] = df["Close"].pct_change()
    vol = df["Returns"].rolling(window=30).std().iloc[-1] * np.sqrt(252)

    vol_percent = vol * 100

    if vol_percent < 15:
        return f"{vol_percent:.2f}%", "green", "Low Volatility"
    elif vol_percent < 30:
        return f"{vol_percent:.2f}%", "orange", "Moderate Volatility"
    else:
        return f"{vol_percent:.2f}%", "red", "High Volatility"

def get_data():
    data = {}
    usd_inr = get_usd_inr()

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="120d")

            if len(hist) < 60:
                continue

            current = hist["Close"].iloc[-1]
            previous = hist["Close"].iloc[-2]
            change = ((current - previous) / previous) * 100

            unit = ""
            display_price = ""

            # -------- COMMODITIES --------

            if name == "Gold":
                price_10g = (current / 31.1035) * 10 * usd_inr
                display_price = f"₹ {price_10g:,.2f}"
                unit = "per 10g"

            elif name == "Silver":
                price_kg = (current / 31.1035) * 1000 * usd_inr
                display_price = f"₹ {price_kg:,.2f}"
                unit = "per kg"

            elif name == "Crude Oil":
                display_price = f"₹ {current * usd_inr:,.2f}"
                unit = "per barrel"

            elif name == "Natural Gas":
                display_price = f"₹ {current * usd_inr:,.2f}"
                unit = "per MMBtu"

            elif name == "Copper":
                display_price = f"₹ {current * usd_inr:,.2f}"
                unit = "per pound"

            elif name == "Wheat":
                display_price = f"₹ {current * usd_inr:,.2f}"
                unit = "per bushel"

            # -------- INDICES --------

            elif name in [
                "S&P 500", "Dow Jones", "NASDAQ",
                "Shanghai Composite", "Hang Seng",
                "NIFTY 50", "Sensex", "USD Index (DXY)"
            ]:
                display_price = f"{current:,.2f}"
                unit = "Index"

            # -------- CRYPTO --------

            elif name in ["Bitcoin", "Ethereum"]:
                display_price = f"$ {current:,.2f}"
                unit = "USD"

            # -------- RATES --------

            elif name == "US 10Y Yield":
                display_price = f"{current:.2f}%"
                unit = "Yield"

            elif name == "VIX":
                display_price = f"{current:.2f}"
                unit = "Volatility Index"

            # -------- SIGNALS --------

            trend_signal, trend_color = moving_average_signal(hist)
            vol_value, vol_color, vol_label = calculate_volatility(hist)

            data[name] = {
                "price": display_price,
                "unit": unit,
                "change": round(change, 2),
                "trend": trend_signal,
                "trend_color": trend_color,
                "volatility": vol_value,
                "vol_color": vol_color,
                "vol_label": vol_label
            }

        except:
            continue

    return data

def get_risk_mode(data):
    try:
        sp = data["S&P 500"]["change"]
        btc = data["Bitcoin"]["change"]

        if sp > 1 and btc > 1:
            return "RISK ON"
        elif sp < -1 and btc < -1:
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