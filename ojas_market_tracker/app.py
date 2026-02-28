from flask import Flask, render_template
import yfinance as yf
import datetime
import pandas as pd
import numpy as np

app = Flask(__name__)

# -----------------------------
# SYMBOL GROUPING
# -----------------------------

RISK_ASSETS = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "NIFTY 50": "^NSEI",
    "Bitcoin": "BTC-USD"
}

DEFENSIVE_ASSETS = {
    "Gold": "GC=F",
    "US 10Y Yield": "^TNX",
    "USD Index (DXY)": "DX-Y.NYB",
    "VIX": "^VIX"
}

COMMODITIES = {
    "Crude Oil": "CL=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F"
}

FX = {
    "USD/INR": "USDINR=X",
    "EUR/INR": "EURINR=X",
    "AED/INR": "AEDINR=X"
}

# -----------------------------
# TREND MODEL (MA 20/50)
# -----------------------------

def trend_signal(df):
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    latest = df.iloc[-1]

    if latest["MA20"] > latest["MA50"] and latest["Close"] > latest["MA20"]:
        return "Bullish", 1, "green"
    elif latest["MA20"] < latest["MA50"] and latest["Close"] < latest["MA20"]:
        return "Bearish", -1, "red"
    else:
        return "Neutral", 0, "orange"

# -----------------------------
# VOLATILITY (21D)
# -----------------------------

def volatility(df):
    df["Returns"] = df["Close"].pct_change()
    vol = df["Returns"].rolling(21).std().iloc[-1] * np.sqrt(252)

    if pd.isna(vol):
        return "N/A", "orange"

    vol_pct = vol * 100

    if vol_pct < 15:
        return f"{vol_pct:.2f}%", "green"
    elif vol_pct < 30:
        return f"{vol_pct:.2f}%", "orange"
    else:
        return f"{vol_pct:.2f}%", "red"

# -----------------------------
# DATA ENGINE
# -----------------------------

def process_assets(asset_dict):
    output = {}
    scores = []

    for name, ticker in asset_dict.items():
        try:
            hist = yf.Ticker(ticker).history(period="120d")
            if len(hist) < 60:
                continue

            trend, score, color = trend_signal(hist)
            vol, vol_color = volatility(hist)
            price = hist["Close"].iloc[-1]

            output[name] = {
                "price": f"{price:,.2f}",
                "trend": trend,
                "color": color,
                "vol": vol,
                "vol_color": vol_color
            }

            scores.append(score)

        except:
            continue

    avg_score = round(sum(scores) / len(scores), 2) if scores else 0
    return output, avg_score

# -----------------------------
# MAIN ROUTE
# -----------------------------

@app.route("/")
def home():

    risk_data, risk_score = process_assets(RISK_ASSETS)
    defensive_data, defensive_score = process_assets(DEFENSIVE_ASSETS)
    commodity_data, _ = process_assets(COMMODITIES)
    fx_data, _ = process_assets(FX)

    liquidity_score = round((-defensive_score + risk_score) / 2, 2)

    if risk_score > defensive_score:
        regime = "RISK ON"
        regime_color = "green"
    elif defensive_score > risk_score:
        regime = "RISK OFF"
        regime_color = "red"
    else:
        regime = "TRANSITION"
        regime_color = "orange"

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")

    return render_template("index.html",
                           risk_data=risk_data,
                           defensive_data=defensive_data,
                           commodity_data=commodity_data,
                           fx_data=fx_data,
                           risk_score=risk_score,
                           defensive_score=defensive_score,
                           liquidity_score=liquidity_score,
                           regime=regime,
                           regime_color=regime_color,
                           time=now)

if __name__ == "__main__":
    app.run(debug=True)