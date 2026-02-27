from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time

app = Flask(__name__)

FED_FUNDS = 5.50
RBI_REPO = 6.50

CACHE = {}
CACHE_TIME = 300  # 5 minutes


tickers = {
    "SPX": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "VIX": "^VIX",
    "US10Y": "^TNX",
    "US2Y": "^IRX",
    "GOLD": "GC=F",
    "OIL": "CL=F",
    "USDINR": "USDINR=X",
    "BTC": "BTC-USD"
}


def fetch_data():
    global CACHE

    if "data" in CACHE and time.time() - CACHE["timestamp"] < CACHE_TIME:
        return CACHE["data"]

    df = yf.download(list(tickers.values()), period="3mo", interval="1d")["Close"]
    df.columns = tickers.keys()

    CACHE["data"] = df
    CACHE["timestamp"] = time.time()

    return df


def compute_regime(df):

    risk_assets = ["SPX", "NASDAQ", "BTC"]
    safe_assets = ["GOLD", "US10Y"]

    risk_score = df[risk_assets].pct_change().tail(5).mean().mean()
    safe_score = df[safe_assets].pct_change().tail(5).mean().mean()

    if risk_score > 0 and safe_score < 0:
        return "RISK ON"
    elif risk_score < 0 and safe_score > 0:
        return "RISK OFF"
    else:
        return "MIXED"


def yield_curve_slope(df):
    return round(df["US10Y"].iloc[-1] - df["US2Y"].iloc[-1], 2)


def liquidity_proxy(df):
    spx = df["SPX"].pct_change().tail(10).mean()
    vix = df["VIX"].pct_change().tail(10).mean()
    return round(spx - vix, 4)


def correlation_matrix(df):
    returns = df.pct_change().dropna()
    corr = returns.corr().round(2)
    return corr.to_dict()


def portfolio_overlay(df):
    weights = {"SPX":0.4, "NASDAQ":0.3, "GOLD":0.2, "BTC":0.1}
    returns = df.pct_change().dropna()
    portfolio_return = sum(weights[k] * returns[k] for k in weights)
    return round(portfolio_return.tail(5).mean(), 4)


@app.route("/")
def home():

    df = fetch_data()

    regime = compute_regime(df)
    slope = yield_curve_slope(df)
    liquidity = liquidity_proxy(df)
    corr = correlation_matrix(df)
    portfolio = portfolio_overlay(df)

    latest = df.iloc[-1].to_dict()

    spark = df.tail(30).pct_change().cumsum().round(3).to_dict()

    now = datetime.datetime.now().strftime("%d %b %Y | %H:%M")

    return render_template(
        "index.html",
        data=latest,
        regime=regime,
        slope=slope,
        liquidity=liquidity,
        corr=corr,
        portfolio=portfolio,
        spark=spark,
        fed=FED_FUNDS,
        rbi=RBI_REPO,
        time=now
    )