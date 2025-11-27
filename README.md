# Trading_Scanner_web_app_python (refactor)

This app scans for trading patterns (hammer heads, FVGs, etc.) across Binance (crypto) and PSX stocks.

Project layout:
- run.py
- app/
  - __init__.py
  - config.py
  - routes/
  - services/
  - templates/

How to run locally:
1. Create a virtualenv
2. pip install -r requirements.txt
3. Ensure PSX_STOCKS exists at src/config/psx_stocks.py or update app/config.py to point to the correct source.
4. python run.py
5. Visit http://localhost:5000

Notes:
- The code isolates Binance requests into services/binance.py and analysis into services/analysis.py.
- Add logging and request timeouts as needed (REQUEST_TIMEOUT is in app/config.py).
- For production, disable debug mode and use a WSGI server.
