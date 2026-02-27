from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

tickers = {
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",

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

def safe_fetch(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            return None, 0
        current = float(hist["Close"].iloc[-1])
        previous = float(hist["Close"].iloc[-2])
        change = ((current - previous) / previous) * 100
        return current, round(change, 2)
    except:
        return None, 0


def ai_comment(change):
    if change > 1:
        return "Strong upside momentum."
    elif change > 0:
        return "Mild positive bias."
    elif change < -1:
        return "Heavy downside pressure."
    elif change < 0:
        return "Soft negative drift."
    return "Flat session."


@app.route("/")
def home():

    data = {}

    # Fetch USDINR first for conversion
    usd_price, _ = safe_fetch("USDINR=X")
    usd_inr = usd_price if usd_price else 83

    for name, symbol in tickers.items():

        price, change = safe_fetch(symbol)

        if price is None:
            continue

        # Formatting
        if name == "Crude Oil":
            display = f"$ {price:,.2f}/bbl"

        elif name == "Natural Gas":
            display = f"$ {price:,.2f}"

        elif name == "Gold":
            inr = price * usd_inr
            display = f"₹ {(inr/31.1035)*10:,.2f}/10g"

        elif name == "Silver":
            inr = price * usd_inr
            display = f"₹ {(inr/31.1035)*1000:,.2f}/kg"

        elif name in ["Copper", "Wheat", "Bitcoin", "Ethereum"]:
            display = f"$ {price:,.2f}"

        elif "Yield" in name:
            display = f"{price:.2f}%"

        else:
            display = f"{price:,.2f}"

        data[name] = {
            "price": display,
            "change": change,
            "ai": ai_comment(change)
        }

    summary = "Macro regime mixed. Monitor bond-equity divergence."

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M")

    return render_template(
        "index.html",
        data=data,
        fed=FED_FUNDS,
        rbi=RBI_REPO,
        summary=summary,
        time=now
    )