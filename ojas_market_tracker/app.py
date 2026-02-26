from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

symbols = {
    "Crude Oil": {"ticker": "CL=F", "currency": "USD"},
    "Natural Gas": {"ticker": "NG=F", "currency": "USD"},
    "Gold": {"ticker": "GC=F", "currency": "USD"},
    "Silver": {"ticker": "SI=F", "currency": "USD"},
    "Copper": {"ticker": "HG=F", "currency": "USD"},
    "Wheat": {"ticker": "ZW=F", "currency": "USD"},
    "S&P 500": {"ticker": "^GSPC", "currency": "USD"},
    "Dow Jones": {"ticker": "^DJI", "currency": "USD"},
    "NASDAQ": {"ticker": "^IXIC", "currency": "USD"},
    "Shanghai Composite": {"ticker": "000001.SS", "currency": "CNY"},
    "Hang Seng": {"ticker": "^HSI", "currency": "HKD"},
    "NIFTY 50": {"ticker": "^NSEI", "currency": "INR"},
    "Sensex": {"ticker": "^BSESN", "currency": "INR"},
    "Bitcoin": {"ticker": "BTC-USD", "currency": "USD"},
    "Ethereum": {"ticker": "ETH-USD", "currency": "USD"},
    "US 10Y Yield": {"ticker": "^TNX", "currency": "%"},
}

def get_usd_inr():
    usd = yf.Ticker("INR=X")
    hist = usd.history(period="1d")
    return float(hist["Close"].iloc[-1])

def get_data():
    data = {}
    usd_inr = get_usd_inr()

    for name, info in symbols.items():
        try:
            stock = yf.Ticker(info["ticker"])
            hist = stock.history(period="2d")

            if len(hist) >= 2:
                current = float(hist["Close"].iloc[-1])
                previous = float(hist["Close"].iloc[-2])

                change = ((current - previous) / previous) * 100
                sentiment = "Bullish 📈" if change > 0 else "Bearish 📉"

                display_price = current
                currency_label = info["currency"]

                # Convert USD assets to INR
                if info["currency"] == "USD":
                    display_price = current * usd_inr
                    currency_label = "INR"

                data[name] = {
                    "price": round(display_price, 2),
                    "original": round(current, 2),
                    "currency": currency_label,
                    "change": round(change, 2),
                    "sentiment": sentiment
                }

        except Exception:
            data[name] = {
                "price": "N/A",
                "original": "N/A",
                "currency": "",
                "change": 0,
                "sentiment": "No Data"
            }

    return data

@app.route("/")
def home():
    market_data = get_data()
    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")
    return render_template("index.html", data=market_data, time=now)

if __name__ == "__main__":
    app.run(debug=True)