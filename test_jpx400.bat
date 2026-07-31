@echo off
"C:\Program Files\QGIS 3.40.14\apps\Python312\python.exe" -c "import yfinance as yf; tickers = ['^JPXNK400', '1591.T', '1592.T', 'JPXN']; [print(t, ':', 'OK' if not yf.Ticker(t).history(period='5d').empty else 'NO DATA') for t in tickers]"
