import streamlit as st
import yfinance as yf
import requests
import os

# Set your Finnhub API key here (or as an environment variable)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "YOUR_FINNHUB_API_KEY")

# Define criteria globally
criteria = {
    "PE": {"Deep Value": lambda x: x is not None and x < 8,
           "Value": lambda x: x is not None and x < 20},
    "PB": {"Deep Value": lambda x: x is not None and x < 1},
    "Debt/Equity": {
        "Deep Value": lambda x: x is not None and x < 0.5,
        "Value": lambda x: x is not None and x < 0.5,
        "Growth": lambda x: x is not None and x < 0.5
    },
    "Free Cashflow yield": {"Deep Value": lambda x: x is not None and x > 8},
    "Current ratio": {"Deep Value": lambda x: x is not None and x > 1.5},
    "P/S": {"Deep Value": lambda x: x is not None and x < 1},
    "ROE": {"Value": lambda x: x is not None and x > 15},
    "ROIC": {"Value": lambda x: x is not None and x > 12},
    "Earning Growth": {"Value": lambda x: x is not None and 5 <= x <= 10},
    "Revenue Growth YOY": {"Growth": lambda x: x is not None and x > 20},
    "EPS Growth YOY": {"Growth": lambda x: x is not None and x > 20},
    "Gross margin": {"Growth": lambda x: x is not None and x > 60},
    # The following criteria lack data in yFinance, left empty or as comments
    "Revenue Growth + Cash flow Margin": None,
    "TAM": None,
    "Retention Rate": None,
    "Moat": None,
    "Cashflow 5 Years": None,
    "Insider Buying": None
}

def fetch_yahoo_data(ticker):
    """Fetch data from Yahoo Finance."""
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        data = {
            "PE": info.get("trailingPE"),
            "PB": info.get("priceToBook"),
            "Debt/Equity": info.get("debtToEquity"),
            "Free Cashflow yield": (
                (info.get("freeCashflow") / info.get("marketCap") * 100)
                if info.get("marketCap") and info.get("freeCashflow") else None
            ),
            "Current ratio": info.get("currentRatio"),
            "P/S": info.get("priceToSalesTrailing12Months"),
            "ROE": info.get("returnOnEquity"),
            "ROIC": info.get("returnOnCapital"),
            "Earning Growth": info.get("earningsQuarterlyGrowth")
            * 100 if info.get("earningsQuarterlyGrowth") else None,
            "Revenue Growth YOY": info.get("revenueQuarterlyGrowth")
            * 100 if info.get("revenueQuarterlyGrowth") else None,
            "EPS Growth YOY": info.get("epsForward")
            * 100 if info.get("epsForward") else None,
            "Gross margin": info.get("grossMargins")
            * 100 if info.get("grossMargins") else None,
        }
        return data
    except Exception as e:
        st.error(f"Error fetching Yahoo data: {e}")
        return {}

def fetch_finnhub_data(ticker):
    """Fetch additional data from Finnhub API."""
    if FINNHUB_API_KEY == "YOUR_FINNHUB_API_KEY":
        return {}
    base_url = "https://finnhub.io/api/v1"
    headers = {"X-Finnhub-Token": FINNHUB_API_KEY}
    data = {}
    try:
        response = requests.get(f"{base_url}/stock/metric", params={"symbol": ticker}, headers=headers)
        if response.status_code != 200:
            return {}
        metrics = response.json().get("metric", {})
        data["debtToEqu
