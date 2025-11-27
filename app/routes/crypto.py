from flask import Blueprint, render_template, request
from ..services.analysis import analyze_candlesticks, analyze_nearest_ob
import pandas as pd

crypto_bp = Blueprint("crypto", __name__)

@crypto_bp.route("/")
def home():
    return render_template("home.html")

@crypto_bp.route("/crypto")
def crypto():
    return render_template("crypto.html")

@crypto_bp.route("/hammer_head", methods=["GET"])
def hammer_form():
    return render_template("hammer_head.html")

@crypto_bp.route("/hammer_head_result", methods=["POST"])
def hammer_result():
    current_candle = request.form.get("current_candle") == "True"
    limit = int(request.form.get("limit", 1))
    timeframe = request.form.get("timeframe", "4h")

    df = analyze_candlesticks(current_candle=current_candle, limit=limit, timeframe=timeframe)

    if df.empty:
        return render_template("hammer_head_result.html", tables=None, message="No hammer head patterns found.")
    table_html = df[['date', 'pair', 'open', 'high', 'low', 'close',
                     'lower_wick', 'lower_wick_to_total_length_ratio', 'momentum_score']].to_html(classes='data', index=False)
    return render_template("hammer_head_result.html", tables=table_html, message=None)

@crypto_bp.route("/nearest_ob", methods=["GET"])
def nearest_ob_form():
    return render_template("nearest_ob.html")

@crypto_bp.route("/nearest_ob_result", methods=["POST"])
def nearest_ob_result():
    limit = int(request.form.get("limit", 100))
    timeframe = request.form.get("timeframe", "4h")
    from ..services.analysis import analyze_nearest_ob
    df = analyze_nearest_ob(limit=limit, timeframe=timeframe)
    if df.empty:
        return render_template("nearest_ob_result.html", tables=None, message="No valid OB detected.")
    table_html = df[['symbol', 'date', 'fvg_low', 'fvg_high', 'ob_low', '% diff fvg low','% diff fvg high', 'wick_percentage']].to_html(classes='data', index=False)
    return render_template("nearest_ob_result.html", tables=table_html, message=None)
