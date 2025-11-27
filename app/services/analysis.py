import pandas as pd
import numpy as np
from ..services.binance import get_usdt_symbols, get_klines

def analyze_candlesticks(current_candle=True, limit=1, timeframe='4h'):
    symbols = get_usdt_symbols()
    results = []
    req_limit = limit + (1 if current_candle else 0)

    for symbol in symbols:
        try:
            klines = get_klines(symbol, interval=timeframe, limit=req_limit)
        except Exception:
            continue
        if not klines or len(klines) < 1:
            continue

        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_vol', 'no_of_trades',
            'taker_buy_base_vol', 'taker_buy_base_quote_vol', 'ignore'
        ])

        # convert numeric columns
        num_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_vol',
                    'no_of_trades', 'taker_buy_base_quote_vol']
        for c in num_cols:
            if c in df.columns:
                df[c] = df[c].astype(float)

        df['length_of_candle'] = df['high'] - df['low']
        df['candle_body'] = (df['open'] - df['close']).abs()
        df['upper_wick'] = df[['open', 'close']].max(axis=1).rsub(df['high']).abs()
        df['lower_wick'] = df[['open', 'close']].min(axis=1).sub(df['low']).abs()
        df['lower_wick_to_total_length_ratio'] = np.where(
            df['length_of_candle'] > 0,
            df['lower_wick'] / df['length_of_candle'],
            0
        )
        df['best_entry'] = df[['open', 'close']].min(axis=1)
        df['date'] = pd.to_datetime(df['open_time'], unit='ms')
        df['pair'] = symbol
        df['period'] = timeframe
        df['momentum_score'] = (df.get('volume', 0) + df.get('quote_asset_vol', 0) + df.get('taker_buy_base_quote_vol', 0)) * df.get('no_of_trades', 0)

        df['Result'] = np.where(df['lower_wick_to_total_length_ratio'] > 0.5, 'hammer head', '')
        hammer_df = df[df['Result'] == 'hammer head']
        if not hammer_df.empty:
            results.append(hammer_df)

    if results:
        final = pd.concat(results, ignore_index=True)
        return final.sort_values(by='lower_wick', ascending=False)
    return pd.DataFrame()

def detect_fvg(symbol, timeframe, limit):
    try:
        klines = get_klines(symbol, interval=timeframe, limit=limit)
    except Exception:
        return None
    if not klines or len(klines) < 3:
        return None

    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume",
                                       "close_time", "quote_asset_volume", "number_of_trades",
                                       "taker_buy_base", "taker_buy_quote", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)

    fvg_info = []
    for i in range(2, len(df) - 1):
        current = df.iloc[i]
        two_back = df.iloc[i - 2]
        if current["low"] > two_back["high"]:
            fvg_low = two_back["high"]
            fvg_high = current["low"]
            ob_low = two_back["low"]

            unfilled = True
            for j in range(i + 1, len(df)):
                if df.iloc[j]["low"] <= ob_low:
                    unfilled = False
                    break

            if unfilled:
                current_price = df.iloc[-1]["close"]
                pct_diff_fvg_start = ((current_price - fvg_high) / fvg_high) * 100
                pct_diff_fvg_end = ((current_price - fvg_low) / fvg_low) * 100
                fvg_info.append({
                    "symbol": symbol,
                    "date": current["timestamp"],
                    "fvg_low": fvg_low,
                    "fvg_high": fvg_high,
                    "ob_low": ob_low,
                    "% diff fvg low": pct_diff_fvg_start,
                    "% diff fvg high": pct_diff_fvg_end
                })
    return fvg_info[-1] if fvg_info else None

def calculate_wick(symbol, timeframe):
    try:
        candle = get_klines(symbol, interval=timeframe, limit=1)[0]
        high = float(candle[2])
        low = float(candle[3])
        open_ = float(candle[1])
        close = float(candle[4])
        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low
        total_wick = upper_wick + lower_wick
        candle_range = high - low
        return (total_wick / candle_range) * 100 if candle_range > 0 else 0
    except Exception:
        return None

def analyze_nearest_ob(limit=100, timeframe='4h'):
    symbols = get_usdt_symbols()
    results = []
    for s in symbols:
        fvg = detect_fvg(s, timeframe, limit)
        if fvg:
            fvg["wick_percentage"] = calculate_wick(s, timeframe)
            results.append(fvg)
    df = pd.DataFrame(results)
    if df.empty:
        return df
    return df.sort_values(by="wick_percentage", ascending=False)
