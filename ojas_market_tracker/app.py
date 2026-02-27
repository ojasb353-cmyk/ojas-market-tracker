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


def fetch_all():
    global CACHE

    if "data" in CACHE and time.time() - CACHE["timestamp"] < CACHE_TIME:
        return CACHE["data"]

    data = yf.download(
        list(ASSETS.values()),
        period="5d",
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=False
    )

    results = {}

    for name, ticker in ASSETS.items():
        try:
            df = data[ticker]
            close = df["Close"].dropna()

            if len(close) < 2:
                continue

            today = float(close.iloc[-1])
            prev = float(close.iloc[-2])

            if name == "US 10Y Yield":
                today = today / 10
                prev = prev / 10

            change = ((today - prev) / prev) * 100

            results[name] = {
                "price": round(today, 2),
                "change": round(change, 2)
            }

        except Exception:
            continue

    CACHE["data"] = results
    CACHE["timestamp"] = time.time()

    return results


@app.route("/")
def home():

    assets = fetch_all()

    regime_list = ["S&P 500", "NASDAQ", "Dow Jones"]
    valid = [assets[x]["change"] for x in regime_list if x in assets]

    regime = "RISK ON" if sum(valid)/len(valid) > 0 else "RISK OFF"

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