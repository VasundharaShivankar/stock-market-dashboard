# test_data.py — run once to verify data fetching works, then delete
from src.data_fetcher import (
    fetch_stock_history,
    fetch_stock_info,
    fetch_live_price,
    format_market_cap,
    format_volume,
)

print("Testing fetch_stock_history (AAPL, 1mo)...")
df = fetch_stock_history("AAPL", "1mo")
print(df.tail(3))
print(f"Shape: {df.shape}\n")

print("Testing fetch_stock_info (AAPL)...")
info = fetch_stock_info("AAPL")
print(f"  Name:       {info['name']}")
print(f"  Sector:     {info['sector']}")
print(f"  Market Cap: {format_market_cap(info['market_cap'])}\n")

print("Testing fetch_live_price (AAPL)...")
price = fetch_live_price("AAPL")
print(f"  Price:  ${price['price']}")
print(f"  Change: {price['change']} ({price['pct']}%)")
print(f"  Volume: {format_volume(price['volume'])}\n")

print("All data layer tests passed!")