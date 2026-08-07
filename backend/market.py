import os
from dotenv import load_dotenv
from massive import RESTClient

load_dotenv(override=True)

massive_api_key = os.getenv("MASSIVE_API_KEY")
client = RESTClient(api_key=massive_api_key)

def _last_trade(client: RESTClient, symbol: str) -> float:
    return float(client.get_last_trade(symbol).price)


def _snapshot(client: RESTClient, symbol: str) -> float:
    snapshot = client.get_snapshot_ticker("stocks", symbol)
    return float(snapshot.min.close or snapshot.prev_day.close)


def _previous_close(client: RESTClient, symbol: str) -> float:
    return float(client.get_previous_close_agg(symbol)[0].close)

price_methods = [_last_trade, _snapshot, _previous_close]
plan_tier = 0

def get_share_price(symbol: str) -> float:
    """Return the current price for a symbol, from Massive or the simulator."""
    if massive_api_key:
        try:
            return get_share_price_massive(symbol)
        except Exception as e:
            print(f"Massive API unavailable ({e}); using a simulated price")
    return None  # Placeholder for simulated price logic, if needed


def get_share_price_massive(symbol: str) -> float:
    """Get the current share price of a stock using the Massive API."""
    global plan_tier
    client = RESTClient(massive_api_key)
    for tier in range(plan_tier, len(price_methods)):
        try:
            price = price_methods[tier](client, symbol)
            plan_tier = tier
            return price
        except Exception:
            continue
    raise RuntimeError(f"No Massive price available for {symbol}")
    