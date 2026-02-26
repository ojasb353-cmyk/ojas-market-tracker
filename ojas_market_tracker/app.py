from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

symbols = {
    "S&P 500": "^GSPC",
    "NIFTY 50": "^NSEI",
    "Gold (INR per 10g)": "GC=F",
    "Bitcoin": "BTC-USD",
    "US 10Y Yield": "^TNX",
}

def get_usd_inr():
    try:
        usd = yf.Ticker("USDINR=X")
        data = usd.history(period="1d")
        return float(data["Close"].iloc[-1])
    except:
        return 83.0

def get_data():
    data = {}
    usd_inr = get_usd_inr()

    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")

            if len(hist) < 2:
                continue

            current = float(hist["Close"].iloc[-1])
            previous = float(hist["Close"].iloc[-2])
            change = ((current - previous) / previous) * 100

            # Gold conversion
            if "Gold" in name:
                current = current * usd_inr
                current = (current / 31.1035) * 10
                price = f"₹ {current:,.2f}"
            elif name == "NIFTY 50":
                price = f"₹ {current:,.2f}"
            elif name == "US 10Y Yield":
                price = f"{current:.2f}%"
            else:
                price = f"$ {current:,.2f}"

            data[name] = {
                "price": price,
                "change": round(change, 2),
                "sentiment": "Bullish 📈" if change > 0 else "Bearish 📉"
            }

        except:
            data[name] = {
                "price": "Data Error",
                "change": 0,
                "sentiment": "Unavailable"
            }

    return data


@app.route("/")
def home():
    market_data = get_data()
    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")

    return render_template(
        "index.html",
        data=market_data,
        time=now
    )