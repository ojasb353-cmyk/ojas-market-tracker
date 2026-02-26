from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

# Static rates
FED_FUNDS = 5.50
RBI_REPO = 6.50

symbols = {
    # Commodities (convert to INR)
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

    # India
    "NIFTY 50": "^NSEI",
    "Sensex": "^BSESN",

    # Crypto
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",

    # Bonds
    "US 10Y Yield": "^TNX",
    "India 10Y": "^INDI10Y"
}

def get_data():
    data = {}
    usd_inr = 83.0

    try:
        usd = yf.Ticker("USDINR=X")
        usd_data = usd.history(period="1d")
        usd_inr = float(usd_data["Close"].iloc[-1])
    except:
        pass

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")

            if len(hist) < 2:
                continue

            current = float(hist["Close"].iloc[-1])
            previous = float(hist["Close"].iloc[-2])
            change = ((current - previous) / previous) * 100

            # Commodities conversion
            if name in ["Crude Oil", "Natural Gas", "Gold", "Silver", "Copper", "Wheat"]:
                current = current * usd_inr
                price = f"₹ {current:,.2f}"

            elif name in ["USD/INR", "EUR/INR", "AED/INR"]:
                price = f"₹ {current:,.2f}"

            elif name in ["NIFTY 50", "Sensex"]:
                price = f"₹ {current:,.2f}"

            elif name in ["US 10Y Yield", "India 10Y"]:
                price = f"{current:.2f}%"

            else:
                price = f"$ {current:,.2f}"

            data[name] = {
                "price": price,
                "change": round(change, 2),
                "sentiment": "Bullish" if change > 0 else "Bearish"
            }

        except:
            data[name] = {
                "price": "N/A",
                "change": 0,
                "sentiment": "Unavailable"
            }

    # Add policy rates
    data["Fed Funds Rate"] = {
        "price": f"{FED_FUNDS:.2f}%",
        "change": 0,
        "sentiment": "Stable"
    }

    data["RBI Repo Rate"] = {
        "price": f"{RBI_REPO:.2f}%",
        "change": 0,
        "sentiment": "Stable"
    }

    return data


@app.route("/")
def home():
    market_data = get_data()
    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")
    return render_template("index.html", data=market_data, time=now)