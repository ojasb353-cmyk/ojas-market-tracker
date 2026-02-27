from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import datetime
import time

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

CACHE = {}
CACHE_TIME = 180

TICKERS = {
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "USD/INR": "USDINR=X",
    "EUR/INR": "EURINR=X",
    "AED/INR": "AEDINR=X",
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Shanghai Composite": "000001.SS",
    "Hang Seng": "^HSI",
    "NIFTY 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "US 10Y Yield": "^TNX"
}


def fetch_data():
    global CACHE

    if "data" in CACHE and time.time() - CACHE["timestamp"] < CACHE_TIME:
        return CACHE["data"]

    try:
        df = yf.download(
            list(TICKERS.values()),
            period="5d",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False
        )

        if df.empty:
            return {}

        close = df["Close"]
        close.columns = TICKERS.keys()

        assets = {}

        for col in close.columns:
            series = close[col].dropna()
            if len(series) < 2:
                continue

            today = float(series.iloc[-1])
            prev = float(series.iloc[-2])
            change = ((today - prev) / prev) * 100

            if col == "US 10Y Yield":
                today = today / 10
                prev = prev / 10
                change = ((today - prev) / prev) * 100

            assets[col] = {
                "price": round(today, 2),
                "change": round(change, 2)
            }

        CACHE["data"] = assets
        CACHE["timestamp"] = time.time()

        return assets

    except Exception:
        return {}


@app.route("/")
def home():

    assets = fetch_data()

    try:
        regime_assets = ["S&P 500", "NASDAQ", "Dow Jones"]
        valid = [assets[x]["change"] for x in regime_assets if x in assets]
        regime_score = sum(valid) / len(valid) if valid else 0
        regime = "RISK ON" if regime_score > 0 else "RISK OFF"
    except:
        regime = "N/A"

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")

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