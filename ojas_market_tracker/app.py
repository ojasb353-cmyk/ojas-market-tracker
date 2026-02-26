from flask import Flask, render_template
import yfinance as yf
import datetime

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

commodities = {
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Wheat": "ZW=F",
}

fx = {
    "USD/INR": "USDINR=X",
    "EUR/INR": "EURINR=X",
    "AED/INR": "AEDINR=X",
}

equities_global = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Shanghai Composite": "000001.SS",
    "Hang Seng": "^HSI",
}

equities_india = {
    "NIFTY 50": "^NSEI",
    "Sensex": "^BSESN",
}

crypto = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
}

bonds = {
    "US 10Y Yield": "^TNX",
}

def fetch_data(symbol_dict):
    result = {}
    for name, ticker in symbol_dict.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")

            if len(hist) < 2:
                continue

            current = float(hist["Close"].iloc[-1])
            previous = float(hist["Close"].iloc[-2])
            change = ((current - previous) / previous) * 100

            result[name] = {
                "price": current,
                "change": round(change, 2),
            }
        except:
            result[name] = {
                "price": None,
                "change": 0,
            }

    return result


@app.route("/")
def home():
    usd_inr = 83
    try:
        usd = yf.Ticker("USDINR=X")
        usd_data = usd.history(period="1d")
        usd_inr = float(usd_data["Close"].iloc[-1])
    except:
        pass

    comm_data = fetch_data(commodities)
    fx_data = fetch_data(fx)
    global_eq = fetch_data(equities_global)
    india_eq = fetch_data(equities_india)
    crypto_data = fetch_data(crypto)
    bond_data = fetch_data(bonds)

    # Format commodities
    formatted_comm = {}

    for name, data in comm_data.items():
        if data["price"] is None:
            continue

        price = data["price"]

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

        else:
            display = f"$ {price:,.2f}"

        formatted_comm[name] = {
            "price": display,
            "change": data["change"]
        }

    # Equity Top Bull & Bear
    def top_movers(eq_data):
        sorted_data = sorted(eq_data.items(), key=lambda x: x[1]["change"])
        bear = sorted_data[0]
        bull = sorted_data[-1]
        return bull, bear

    global_bull, global_bear = top_movers(global_eq)
    india_bull, india_bear = top_movers(india_eq)

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M:%S")

    return render_template(
        "index.html",
        commodities=formatted_comm,
        fx=fx_data,
        global_eq=global_eq,
        india_eq=india_eq,
        crypto=crypto_data,
        bonds=bond_data,
        fed=FED_FUNDS,
        rbi=RBI_REPO,
        global_bull=global_bull,
        global_bear=global_bear,
        india_bull=india_bull,
        india_bear=india_bear,
        time=now
    )