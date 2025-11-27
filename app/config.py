# path, adjust the import.
try:
    from src.config.psx_stocks import PSX_STOCKS
except Exception:
    PSX_STOCKS = []  

BINANCE_BASE = "https://api.binance.com/api/v3"
REQUEST_TIMEOUT = 10
