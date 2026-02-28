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

    # FX
    "USD/INR": "USDINR=X",
    "EUR/INR": "EURINR=X",
    "AED/INR": "AEDINR=X"
}

# ---------------- SAFE MA TREND ----------------

def moving_average_signal(df):
    if len(df) < 60:
        return "Neutral", "orange"

    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    latest = df.iloc[-1]

    if pd.isna(latest["MA20"]) or pd.isna(latest["MA50"]):
        return "Neutral", "orange"

    if latest["MA20"] > latest["MA50"] and latest["Close"] > latest["MA20"]:
        return "▲ Bullish Trend", "green"
    elif latest["MA20"] < latest["MA50"] and latest["Close"] < latest["MA20"]:
        return "▼ Bearish Trend", "red"
    else:
        return "► Neutral Structure", "orange"

# ---------------- SAFE VOLATILITY ----------------

def calculate_volatility(df):
    if len(df) < 30:
        return "N/A", "orange", "Insufficient Data"

    returns = df["Close"].pct_change()
    rolling_std = returns.rolling(30).std()

    if pd.isna(rolling_std.iloc[-1]):
        return "N/A", "orange", "Insufficient Data"

    vol = rolling_std.iloc[-1] * np.sqrt(252)
    vol_pct = vol * 100

    if vol_pct < 15:
        return f"{vol_pct:.2f}%", "green", "Low Volatility"
    elif vol_pct < 30:
        return f"{vol_pct:.2f}%", "orange", "Moderate Volatility"
    else:
        return f"{vol_pct:.2f}%", "red", "High Volatility"

# ---------------- MAIN DATA ENGINE ----------------

def get_data():
    data = {}

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="120d")

            if hist.empty:
                continue

            hist = hist.dropna()

            if len(hist) < 2:
                continue

            current = hist["Close"].iloc[-1]
            previous = hist["Close"].iloc[-2]
            change = ((current - previous) / previous) * 100

            # Default formatting
            display_price = f"{current:,.2f}"
            unit = ""

            # FX formatting
            if name in ["USD/INR", "EUR/INR", "AED/INR"]:
                display_price = f"{current:.4f}"
                unit = "FX Rate"

            # Crypto
            elif name in ["Bitcoin", "Ethereum"]:
                display_price = f"$ {current:,.2f}"
                unit = "USD"

            # Yields
            elif name == "US 10Y Yield":
                display_price = f"{current:.2f}%"
                unit = "Yield"

            # VIX
            elif name == "VIX":
                display_price = f"{current:.2f}"
                unit = "Volatility Index"

            # Indices
            elif name in [
                "S&P 500", "Dow Jones", "NASDAQ",
                "Shanghai Composite", "Hang Seng",
                "NIFTY 50", "Sensex", "USD Index (DXY)"
            ]:
                display_price = f"{current:,.2f}"
                unit = "Index"

            # Commodities (no conversion now for stability)
            else:
                display_price = f"{current:,.2f}"

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

        except Exception:
            continue

    return data

# ---------------- RISK MODE ----------------

def get_risk_mode(data):
    try:
        sp = data.get("S&P 500", {}).get("change", 0)
        btc = data.get("Bitcoin", {}).get("change", 0)

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