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

    "US 10Y Yield": "^TNX",
    "India 10Y": "^IN10Y"
}


def fetch_data():
    data = {}

    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")

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
            continue

    return data


def ai_commentary(name, change):
    if change > 1:
        return "Strong upside momentum building."
    elif change > 0:
        return "Mild positive bias."
    elif change < -1:
        return "Heavy downside pressure visible."
    elif change < 0:
        return "Soft negative drift."
    else:
        return "Flat session. Await catalyst."


def ai_macro_summary(data):
    risk_assets = ["S&P 500", "NASDAQ", "Bitcoin"]
    safe_assets = ["Gold", "US 10Y Yield"]

    risk_score = sum(data.get(x, {}).get("change", 0) for x in risk_assets)
    safe_score = sum(data.get(x, {}).get("change", 0) for x in safe_assets)

    if risk_score > 0 and safe_score < 0:
        return "RISK-ON regime: equities firm, defensive assets soft."
    elif risk_score < 0 and safe_score > 0:
        return "RISK-OFF tone: capital rotating to safety."
    else:
        return "Mixed macro signals. No dominant regime detected."


@app.route("/")
def home():

    raw = fetch_data()

    formatted = {}
    usd_inr = raw.get("USD/INR", {}).get("price_raw", 83)

    for name, values in raw.items():
        price = values["price_raw"]
        change = values["change"]

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

        elif "Yield" in name or "10Y" in name:
            display = f"{price:.2f}%"

        else:
            display = f"{price:,.2f}"

        formatted[name] = {
            "price": display,
            "change": change,
            "ai": ai_commentary(name, change)
        }

    summary = ai_macro_summary(raw)
    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M")

    return render_template(
        "index.html",
        data=formatted,
        fed=FED_FUNDS,
        rbi=RBI_REPO,
        summary=summary,
        time=now
    )