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
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",
    "USD/INR": "USDINR=X",
    "EUR/INR": "EURINR=X",
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
    "VIX": "^VIX"
}


def fetch_data():
    global CACHE

    if "data" in CACHE and time.time() - CACHE["timestamp"] < CACHE_TIME:
        return CACHE["data"]

    df = yf.download(list(TICKERS.values()), period="5d", interval="1d", progress=False)["Close"]
    df.columns = TICKERS.keys()

    df = df.dropna(axis=1, how="all")

    CACHE["data"] = df
    CACHE["timestamp"] = time.time()

    return df


def format_asset(name, today, yesterday):
    if pd.isna(today) or pd.isna(yesterday):
        return None

    change = today - yesterday
    pct = (change / yesterday) * 100 if yesterday != 0 else 0

    arrow = "▲" if change > 0 else "▼" if change < 0 else "■"
    color = "green" if change > 0 else "red" if change < 0 else "gray"

    return {
        "name": name,
        "price": round(float(today), 2),
        "change": round(float(pct), 2),
        "arrow": arrow,
        "color": color
    }


def compute_regime(assets):
    eq = []
    for index in ["S&P 500", "NASDAQ", "Dow Jones"]:
        if index in assets:
            eq.append(assets[index]["change"])

    if not eq:
        return "UNKNOWN"

    avg = np.mean(eq)

    if avg > 0.3:
        return "RISK ON"
    elif avg < -0.3:
        return "RISK OFF"
    else:
        return "MIXED"


@app.route("/")
def home():
    df = fetch_data()

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    assets = {}

    for col in df.columns:
        formatted = format_asset(col, latest[col], previous[col])
        if formatted:
            assets[col] = formatted

    regime = compute_regime(assets)

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