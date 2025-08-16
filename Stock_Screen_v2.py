import streamlit as st
import yfinance as yf
import requests
import os

def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
    except Exception:
        return None
    data = {
        "PE": info.get("trailingPE", 0),
        "PB": info.get("priceToBook", 0),
        "Debt/Equity": info.get("debtToEquity", None),  # Now returns None if not available
        "Free Cashflow yield": (info.get("freeCashflow", 0) / info.get("marketCap", 1)) * 100,
        "Current ratio": info.get("currentRatio", 0),
        "P/S": info.get("priceToSalesTrailing12Months", 0),
        "ROE": info.get("returnOnEquity", 0) * 100,
        "ROIC": 0,  # Placeholder
        "Earning Growth": info.get("earningsQuarterlyGrowth", 0) * 100,
        "Revenue Growth YOY": info.get("revenueGrowth", 0) * 100,
        "EPS Growth YOY": info.get("earningsGrowth", 0) * 100,
        "Gross margin": info.get("grossMargins", 0) * 100,
        "Revenue Growth + Cash flow Margin": 0,  # Placeholder
        "TAM": 20_000_000_000,  # Placeholder
        "Retention Rate": 120,  # Placeholder
        "Moat": True,  # Placeholder
        "Cashflow 5 Years": True,  # Placeholder
        "Insider Buying": False  # Placeholder
    }
    return data

def evaluate(data):
    criteria = {
        "PE": {"Deep Value": lambda x: x < 8, "Value": lambda x: x < 20},
        "PB": {"Deep Value": lambda x: x < 1},
        "Debt/Equity": {
            "Deep Value": lambda x: x is not None and x < 0.5,
            "Value": lambda x: x is not None and x < 1.5,
            "Growth": lambda x: x is not None and x < 2
        },
        "Free Cashflow yield": {"Deep Value": lambda x: x > 8},
        "Current ratio": {"Deep Value": lambda x: x > 1.5},
        "P/S": {"Deep Value": lambda x: x < 1},
        "ROE": {"Value": lambda x: x > 15},
        "ROIC": {"Value": lambda x: x > 12},
        "Earning Growth": {"Value": lambda x: 5 <= x <= 10},
        "Revenue Growth YOY": {"Growth": lambda x: x > 20},
        "EPS Growth YOY": {"Growth": lambda x: x > 20},
        "Gross margin": {"Growth": lambda x: x > 60},
        "Revenue Growth + Cash flow Margin": {"Growth": lambda x: x > 40},
        "TAM": {"Growth": lambda x: x > 10_000_000_000},
        "Retention Rate": {"Growth": lambda x: x > 110},
        "Moat": {"Growth": lambda x: x is True},
        "Cashflow 5 Years": {"Growth": lambda x: x is True},
        "Insider Buying": {"Deep Value": lambda x: x is True}
    }
    result = []
    for metric, value in data.items():
        show_value = "N/A" if value is None else (round(value, 2) if isinstance(value, (float, int)) else value)
        row = {"Metric": metric, "Value": show_value}
        for category in ["Deep Value", "Value", "Growth"]:
            rule = criteria.get(metric, {}).get(category)
            if rule:
                if value is not None and rule(value):
                    row[category] = "✔️"
                elif value is not None:
                    row[category] = "❌"
                else:
                    row[category] = ""
            else:
                row[category] = ""
        result.append(row)
    return result

def main():
    # --- Set page config
    st.set_page_config(page_title="Stock Classification", layout="wide")

    st.title("📊 Stock Classification: Deep Value vs Growth vs Value")

    # --- Input for ticker symbol
    ticker = st.text_input("Enter stock ticker symbol:", value="AAPL")

    if ticker:
        data = fetch_data(ticker)
        if data:
            results = evaluate(data)
            st.write(f"### Evaluation for {ticker}")
            st.table(results)
        else:
            st.write("Failed to fetch data. Please check the ticker symbol.")

if __name__ == "__main__":
    main()
