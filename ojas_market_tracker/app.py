from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

tickers = {
    # Commodities
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",

    # FX
    "USD/INR": "USDINR=X",
    "EUR/INR": "EURINR=X",
    "AED/INR": "AEDINR=X",

    # Global Equity
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Shanghai Composite": "000001.SS",
    "Hang Seng": "^HSI",

    # India Equity
    "NIFTY 50": "^NSEI",
    "Sensex": "^BSESN",

    # Crypto
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",

    # Bonds
    "US 10Y Yield": "^TNX",
    "India 10Y": "^IN10Y"
}


def fetch_all():
    data = {}

    for name, symbol in tickers.items():
        try:
            asset = yf.Ticker(symbol)
            hist = asset.history(period="2d")

            if len(hist) < 2:
                continue

            current = float(hist["Close"].iloc[-1])
            previous = float(hist["Close"].iloc[-2])
            change = ((current - previous) / previous) * 100

            data[name] = {
                "price_raw": current,
                "change": round(change, 2)
            }

        except:
            data[name] = {
                "price_raw": None,
                "change": 0
            }

    return data


def format_prices(data):
    formatted = {}

    usd_inr = data.get("USD/INR", {}).get("price_raw", 83)

    for name, values in data.items():

        price = values["price_raw"]
        change = values["change"]

        if price is None:
            continue

        # Commodities formatting
        if name == "Crude Oil":
            display = f"$ {price:,.2f} /bbl"

        elif name == "Natural Gas":
            display = f"$ {price:,.2f}"

        elif name == "Gold":
            gold_inr = price * usd_inr
            gold_10g = (gold_inr / 31.1035) * 10
            display = f"₹ {gold_10g:,.2f} /10g"

        elif name == "Silver":
            silver_inr = price * usd_inr
            silver_kg = (silver_inr / 31.1035) * 1000
            display = f"₹ {silver_kg:,.2f} /kg"

        elif name in ["Copper", "Wheat"]:
            display = f"$ {price:,.2f}"

        # FX
        elif "INR" in name:
            display = f"{price:,.2f}"

        # Crypto
        elif name in ["Bitcoin", "Ethereum"]:
            display = f"$ {price:,.2f}"

        # Bonds
        elif "Yield" in name or "10Y" in name:
            display = f"{price:.2f}%"

        # Equity indices (no currency)
        else:
            display = f"{price:,.2f}"

        formatted[name] = {
            "price": display,
            "change": change
        }

    return formatted


@app.route("/")
def home():

    raw = fetch_all()
    data = format_prices(raw)

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")

    return render_template(
        "index.html",
        data=data,
        fed=FED_FUNDS,
        rbi=RBI_REPO,
        time=now
    )


if __name__ == "__main__":
    app.run(debug=True)