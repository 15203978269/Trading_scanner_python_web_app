import pandas as pd
import numpy as np
import yfinance as yf
from ..config import PSX_STOCKS

psx_stocks = PSX_STOCKS

def get_hammer_head_patterns(days: int, interval: str) -> pd.DataFrame:
    data = []
    for stock in psx_stocks:
        try:
            ticker = yf.Ticker(stock)
            period = f"{days}d"
            df = ticker.history(period=period, interval=interval, actions=False)
        except Exception:
            continue
        if df is None or df.empty:
            continue

        df = df.rename(columns=lambda c: c.capitalize() if isinstance(c, str) else c)
        if not {'Open', 'High', 'Low', 'Close', 'Volume'}.issubset(df.columns):
            continue

        df['Stock'] = stock
        df['length_of_candle'] = df['High'] - df['Low']
        df['candle_body'] = (df['Open'] - df['Close']).abs()
        df['upper_wick'] = (df[['Open', 'Close']].max(axis=1) - df['High']).abs()
        df['lower_wick'] = (df[['Open', 'Close']].min(axis=1) - df['Low']).abs()
        df['lower_wick_to_total_length_ratio'] = np.where(df['length_of_candle'] > 0, df['lower_wick'] / df['length_of_candle'], 0)
        df['best_entry'] = df[['Open', 'Close']].min(axis=1)
        df['date'] = df.index
        df['pair'] = stock
        df['Result'] = np.where(df['lower_wick_to_total_length_ratio'] > 0.5, 'hammer head', 'not hammer')
        data.append(df[['Stock', 'Open', 'High', 'Low', 'Close', 'Volume',
                        'length_of_candle', 'candle_body', 'upper_wick',
                        'lower_wick', 'lower_wick_to_total_length_ratio',
                        'best_entry', 'date', 'pair', 'Result']])
    if data:
        df_psx = pd.concat(data, ignore_index=True)
        df_hammer_head = df_psx[df_psx['Result'] == 'hammer head']
        return df_hammer_head.sort_values(['Volume'], ascending=False)
    return pd.DataFrame()

def find_bullish_fvg(symbol, period: str, interval: str):
    try:
        data = yf.download(symbol, period=period, interval=interval, actions=False, progress=False)
    except Exception:
        return None
    if data is None or len(data) < 3:
        return None

    data_sorted = data.sort_index(ascending=True)
    arr = data_sorted[['Open', 'High', 'Low', 'Close']].to_numpy()
    timestamps = data_sorted.index
    current_price = arr[-1][3]

    fvg_data = []
    for i in range(2, len(arr)-1):
        candle_c = arr[i-2]
        candle_a = arr[i]
        if candle_a[2] > candle_c[1]:
            OB_low = candle_c[2]
            fvg_start = candle_a[2]
            fvg_end = candle_c[1]
            unfilled = True
            for j in range(i+1, len(arr)):
                if arr[j][2] <= OB_low:
                    unfilled = False
                    break
            if unfilled:
                pct_diff_start = ((current_price - fvg_start) / fvg_start) * 100
                pct_diff_end = ((current_price - fvg_end) / fvg_end) * 100
                fvg_data.append({
                    "Symbol": symbol,
                    "Date": timestamps[i],
                    "OB LOW": OB_low,
                    "FVG START": fvg_start,
                    "FVG END": fvg_end,
                    "Current Price": current_price,
                    "% FVG start": pct_diff_start,
                    "% FVG end": pct_diff_end
                })
    if fvg_data:
        return pd.DataFrame(fvg_data)
    return None

def get_bullish_fvg_for_symbols(symbols=None, period: str = "7d", interval: str = "1d"):
    if symbols is None:
        symbols = psx_stocks
    results = []
    for s in symbols:
        r = find_bullish_fvg(s, period, interval)
        if r is not None:
            results.append(r)
    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()
