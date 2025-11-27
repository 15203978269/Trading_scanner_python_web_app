import requests
from ..config import BINANCE_BASE, REQUEST_TIMEOUT

def get_usdt_symbols(timeout=REQUEST_TIMEOUT):
    url = f"{BINANCE_BASE}/exchangeInfo"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    exchange_info = r.json()
    return [
        s['symbol']
        for s in exchange_info.get('symbols', [])
        if s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING'
    ]

def get_klines(symbol, interval='4h', limit=1, timeout=REQUEST_TIMEOUT):
    url = f"{BINANCE_BASE}/klines"
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()
