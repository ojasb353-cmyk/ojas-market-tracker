from flask import Flask, render_template
import yfinance as yf
import datetime
import time

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

CACHE = {}
CACHE_TIME = 120


ASSETS = {
    "Crude Oil (WTI)": "CL=F",          # USD per barrel
    "Natural Gas": "NG=F",              # USD per MMBtu
    "Copper": "HG=F",                   # USD per lb
    "Wheat": "ZW=F",                    # USD per bushel
    "Gold": "GC=F",                     # USD per oz
    "Silver": "SI=F",                   # USD per oz
    "USD/INR": "USDINR=X",              # INR
    "EUR/INR": "EURINR=X",
    "AED/INR": "AEDINR=X",
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Shanghai Composite": "000001.SS",
    "Hang Seng": "^HSI",
    "NIFTY 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bitcoin": "BTC-USD",               # USD
    "Ethereum": "ETH-USD",              # USD
    "US 10Y Yield": "^TNX"              # ÷10
}


def fetch_asset(ticker):
    data = yf.download(ticker, period="5d", interval="1d", progress=False)
    if data.empty:
        return None, None
    close = data["Close"]
    today = close.iloc[-1]
    prev = close.iloc[-2] if len(close) > 1 else close.iloc[-1]
    return today, prev


@app.route("/")
def home():

    global CACHE

    if "data" in CACHE and time.time() - CACHE["timestamp"] < CACHE_TIME:
        assets = CACHE["data"]
    else:
        assets = {}

        for name, ticker in ASSETS.items():
            today, prev = fetch_asset(ticker)

            if today is None:
                continue

            change = ((today - prev) / prev) * 100 if prev else 0

            # Fix US10Y scaling
            if name == "US 10Y Yield":
                today = today / 10
                prev = prev / 10
                change = ((today - prev) / prev) * 100 if prev else 0

            assets[name] = {
                "price": round(float(today), 2),
                "change": round(float(change), 2)
            }

        CACHE["data"] = assets
        CACHE["timestamp"] = time.time()

    regime_assets = ["S&P 500", "NASDAQ", "Dow Jones"]
    regime_score = sum(
        assets[x]["change"] for x in regime_assets if x in assets
    ) / len(regime_assets)

    regime = "RISK ON" if regime_score > 0 else "RISK OFF"

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