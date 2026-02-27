from flask import Flask, render_template
import yfinance as yf
import datetime
import time

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

CACHE = {}
CACHE_TIME = 180


ASSETS = {
    "Crude Oil (WTI)": "CL=F",
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


def fetch_price(ticker):
    try:
        data = yf.download(
            ticker,
            period="5d",
            interval="1d",
            progress=False,
            threads=False
        )

        if data.empty:
            return None, None

        close = data["Close"]
        today = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if len(close) > 1 else today

        return today, prev

    except Exception:
        return None, None


@app.route("/")
def home():

    global CACHE

    if "data" in CACHE and time.time() - CACHE["timestamp"] < CACHE_TIME:
        assets = CACHE["data"]
    else:
        assets = {}

        for name, ticker in ASSETS.items():

            today, prev = fetch_price(ticker)

            if today is None:
                continue

            change = ((today - prev) / prev) * 100 if prev else 0

            if name == "US 10Y Yield":
                today = today / 10
                prev = prev / 10
                change = ((today - prev) / prev) * 100 if prev else 0

            assets[name] = {
                "price": round(today, 2),
                "change": round(change, 2)
            }

        CACHE["data"] = assets
        CACHE["timestamp"] = time.time()

    try:
        regime_assets = ["S&P 500", "NASDAQ", "Dow Jones"]
        regime_score = sum(
            assets[x]["change"] for x in regime_assets if x in assets
        ) / max(len(regime_assets), 1)

        regime = "RISK ON" if regime_score > 0 else "RISK OFF"

    except Exception:
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