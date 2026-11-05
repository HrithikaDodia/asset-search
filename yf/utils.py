import yfinance as yf
import pandas as pd
from pathlib import Path
import json


def fetch_security(symbol: str) -> dict | None:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.get_info()

        security = {
            "symbol": info.get("symbol") or symbol,
            "exchange": (
                info.get("fullExchangeName")
                or info.get("exchange")
            ),
            "name": (
                info.get("longName")
                or info.get("shortName")
            ),
            "country": info.get("country"),
            "type": info.get("quoteType"),
            "industry": info.get("industry"),
            "description": info.get("longBusinessSummary")
        }

        return security

    except Exception as exc:
        print(f"Failed to fetch {symbol}: {exc}")
        return None

def fetch_securities(symbols: list[str]) -> list[dict]:
    securities = []

    for symbol in symbols:
        print(f"Fetching {symbol}...")

        security = fetch_security(symbol)

        if security:
            securities.append(security)

    return securities

def fetch_index_tickers():
    url = (
        "https://raw.githubusercontent.com/"
        "datasets/s-and-p-500-companies/"
        "main/data/constituents.csv"
    )

    df = pd.read_csv(url)

    symbols = (
        df["Symbol"]
        .str.replace(".", "-", regex=False)
        .tolist()
    )

    data = fetch_securities(symbols)

    return data

def save_securities_to_json(
    securities: list[dict],
    output_file: str = "data/securities.json",
):
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            securities,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved {len(securities)} securities "
        f"to {output_path}"
    )

def main():
    data = fetch_index_tickers()
    save_securities_to_json(data, "./../data/securities_data.json")

if '__main__' == __name__:
    main()