from flask import Blueprint, render_template, request
from ..services.psx import get_hammer_head_patterns, get_bullish_fvg_for_symbols
from ..config import PSX_STOCKS

psx_bp = Blueprint("psx", __name__, url_prefix="/psx")

@psx_bp.route("/")
def psx_home():
    return render_template("psx_home.html", psx_count=len(PSX_STOCKS))

@psx_bp.route("/hammer_head_psx", methods=["GET"])
def hammer_form_psx():
    return render_template("hammer_head_psx.html")

@psx_bp.route("/hammer_head_result_psx", methods=["POST"])
def hammer_result_psx():
    limit = int(request.form.get("limit", 7))
    timeframe = request.form.get("timeframe", "1d")
    df = get_hammer_head_patterns(limit, timeframe)
    if df.empty:
        return render_template("hammer_head_result_psx.html", tables=None, message="No hammer head patterns found.")
    table_html = df[['Stock', 'date', 'Open', 'High', 'Low', 'Close', 'Volume',
                     'length_of_candle', 'candle_body', 'upper_wick',
                     'lower_wick', 'lower_wick_to_total_length_ratio',
                     'best_entry', 'Result']].to_html(classes='data', index=False)
    return render_template("hammer_head_result_psx.html", tables=table_html, message=None)

@psx_bp.route("/bullish_fvg_psx", methods=["GET"])
def bullish_fvg_psx():
    return render_template("bullish_fvg_psx.html")

@psx_bp.route("/bullish_fvg_psx_results", methods=["POST"])
def bullish_fvg_psx_result():
    limit = int(request.form.get("limit", 7))
    timeframe = request.form.get("timeframe", "1d")
    final_limit = f"{limit}d"
    df = get_bullish_fvg_for_symbols(PSX_STOCKS, final_limit, timeframe)
    if df is None or df.empty:
        return render_template("bullish_fvg_psx_results.html", tables=None, message="No FVG found")
    table_html = df[['Symbol', 'Date', 'FVG START', 'FVG END', 'OB LOW', '% FVG start', '% FVG end']].to_html(classes='data', index=False)
    return render_template('bullish_fvg_psx_results.html', tables=table_html, message=None)
