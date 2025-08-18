import streamlit as st
import yfinance as yf

def safe_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except (ValueError, TypeError):
        return None

# New helper function to standardize Debt/Equity ratio
def adjust_de_ratio(raw_ratio):
    if raw_ratio is None:
        return None
    try:
        val = float(raw_ratio)
        # If the value is suspiciously high, treat it as percent (e.g., 12.267 -> 0.12267)
        if val > 3:
            val = val / 100
        return val
    except Exception:
        return None

def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
    except Exception:
        return None

    st.write(f"{ticker} - debtToEquity raw:", info.get("debtToEquity"))

    keys_to_show = [
        "trailingPE", "priceToBook", "debtToEquity", "freeCashflow", "marketCap",
        "currentRatio", "priceToSalesTrailing12Months", "returnOnEquity",
        "earningsQuarterlyGrowth", "revenueGrowth", "earningsGrowth", "grossMargins"
    ]
    for key in keys_to_show:
        st.write(f"{ticker} - {key}:", info.get(key))

    data = {
        "PE": safe_float(info.get("trailingPE")),
        "PB": safe_float(info.get("priceToBook")),
        "Debt/Equity": adjust_de_ratio(info.get("debtToEquity")),
        "Free Cashflow yield": (
            safe_float(info.get("freeCashflow")) / safe_float(info.get("marketCap")) * 100
            if safe_float(info.get("freeCashflow")) is not None and safe_float(info.get("marketCap")) not in [None, 0]
            else None
        ),
        "Current ratio": safe_float(info.get("currentRatio")),
        "P/S": safe_float(info.get("priceToSalesTrailing12Months")),
        "ROE": safe_float(info.get("returnOnEquity")) * 100 if safe_float(info.get("returnOnEquity")) is not None else None,
        "ROIC": None,  # Placeholder
        "Earning Growth": safe_float(info.get("earningsQuarterlyGrowth")) * 100 if safe_float(info.get("earningsQuarterlyGrowth")) is not None else None,
        "Revenue Growth YOY": safe_float(info.get("revenueGrowth")) * 100 if safe_float(info.get("revenueGrowth")) is not None else None,
        "EPS Growth YOY": safe_float(info.get("earningsGrowth")) * 100 if safe_float(info.get("earningsGrowth")) is not None else None,
        "Gross margin": safe_float(info.get("grossMargins")) * 100 if safe_float(info.get("grossMargins")) is not None else None,
        "Revenue Growth + Cash flow Margin": None,  # Placeholder
        "TAM": 20_000_000_000,  # Placeholder
        "Retention Rate": 120,  # Placeholder
        "Moat": True,  # Placeholder
        "Cashflow 5 Years": True,  # Placeholder
        "Insider Buying": False  # Placeholder
    }
    return data

def evaluate(data):
    criteria = {
        "PE": {
            "Deep Value": lambda x: x is not None and x < 8,
            "Value": lambda x: x is not None and x < 20
        },
        "PB": {
            "Deep Value": lambda x: x is not None and x < 1,
             "Value": lambda x: x is not None and x < 1.5
        },
        "Debt/Equity": {
            "Deep Value": lambda x: x is not None and x < 0.5,
            "Value": lambda x: x is not None and x < 1.5,
            "Growth": lambda x: x is not None and x < 2.0
        },
        "Free Cashflow yield": {
            "Deep Value": lambda x: x is not None and x > 8
        },
        "Current ratio": {
            "Deep Value": lambda x: x is not None and x > 1.5
        },
        "P/S": {
            "Deep Value": lambda x: x is not None and x < 1
        },
        "ROE": {
            "Value": lambda x: x is not None and x > 15
        },
        "ROIC": {
            "Value": lambda x: x is not None and x > 12
        },
        "Earning Growth": {
            "Value": lambda x: x is not None and 5 <= x <= 10
        },
        "Revenue Growth YOY": {
            "Growth": lambda x: x is not None and x > 20
        },
        "EPS Growth YOY": {
            "Growth": lambda x: x is not None and x > 20,
            "Value": lambda x: x is not None and x > 5
        },
        "Gross margin": {
            "Growth": lambda x: x is not None and x > 60
        },
        "Revenue Growth + Cash flow Margin": {
            "Growth": lambda x: x is not None and x > 40
        },
        "TAM": {
            "Growth": lambda x: x is not None and x > 10_000_000_000
        },
        "Retention Rate": {
            "Growth": lambda x: x is not None and x > 110
        },
        "Moat": {
            "Growth": lambda x: x is True
        },
        "Cashflow 5 Years": {
            "Growth": lambda x: x is True
        },
        "Insider Buying": {
            "Deep Value": lambda x: x is True
        }
    }
    result = []
    for metric, value in data.items():
        show_value = (
            "N/A" if value is None else
            round(value, 2) if isinstance(value, (float, int)) else value
        )
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
    st.set_page_config(page_title="Stock Classification", layout="wide")
    st.title("📊 Stock Classification: Deep Value vs Growth vs Value")
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
