from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

CACHE = {}
CACHE_TIME = 300


TICKERS = {
    # Commodities (USD)
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",

    # Metals
    "Gold": "GC=F",
    "Silver": "SI=F",

    # FX
    "USD/INR": "USDINR=X",
    "EUR/INR": "EURINR=X",
    "AED/INR": "AEDINR=X",

    # Index
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

    # Yield
    "US 10Y Yield": "^TNX"
}


def fetch_data():
    global CACHE

    if "data" in CACHE and time.time() - CACHE["timestamp"] < CACHE_TIME:
        return CACHE["data"]

    df = yf.download(
        list(TICKERS.values()),
        period="3mo",
        interval="1d",
        progress=False,
        auto_adjust=True
    )["Close"]

    df.columns = TICKERS.keys()
    df = df.dropna(axis=1, how="all")

    CACHE["data"] = df
    CACHE["timestamp"] = time.time()

    return df


def safe_usdinr(value):
    # If USDINR abnormal, fallback to realistic value
    if value < 50 or value > 120:
        return 85.0
    return value


def ai_bias(momentum, volatility):
    score = momentum - volatility

    if score > 0.02:
        return "Bullish", "▲", "green"
    elif score < -0.02:
        return "Bearish", "▼", "red"
    else:
        return "Neutral", "■", "orange"


@app.route("/")
def home():

    df = fetch_data()
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    assets = {}

    usdinr = latest.get("USD/INR", 85.0)
    usdinr = safe_usdinr(usdinr)

    for col in df.columns:

        today = latest[col]
        yesterday = prev[col]

        if pd.isna(today) or pd.isna(yesterday):
            continue

        change = ((today - yesterday) / yesterday) * 100
        momentum = df[col].pct_change().tail(5).mean()
        volatility = df[col].pct_change().tail(20).std()

        bias_text, arrow, color = ai_bias(momentum, volatility)

        confidence = round(abs(momentum) / (volatility + 1e-6) * 100, 1)
        confidence = min(confidence, 95)

        price_display = today

        # Gold USD/oz → INR per 10g
        if col == "Gold":
            price_display = (today * usdinr * 10) / 31.1035

        # Silver USD/oz → INR per kg
        if col == "Silver":
            price_display = (today * usdinr * 1000) / 31.1035

        assets[col] = {
            "price": round(float(price_display), 2),
            "change": round(float(change), 2),
            "momentum": round(momentum * 100, 2),
            "volatility": round(volatility * 100, 2),
            "bias": bias_text,
            "arrow": arrow,
            "color": color,
            "confidence": confidence
        }

    regime_score = np.mean([
        assets[x]["change"]
        for x in ["S&P 500", "NASDAQ", "Dow Jones"]
        if x in assets
    ])

    regime = "RISK ON" if regime_score > 0 else "RISK OFF"

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M")

    return render_template(
        "index.html",
        assets=assets,
        regime=regime,
        fed=FED_FUNDS,
        rbi=RBI_REPO,
        time=now
    )


if __name__ == "__main__":
    app.run(debug=True)