import os
import re
import json
import time
from datetime import datetime, timedelta
import yfinance as yf

# 設定
DATA_DIR = "data"
INDEX_HTML = "index.html"
YEARS = 5

INDICES_TICKER = {
    "INDEX_N225": "^N225",
    "INDEX_TOPX": "1306.T",
    "INDEX_DJI": "^DJI",
    "INDEX_IXIC": "^IXIC",
    "INDEX_GSPC": "^GSPC",
    "INDEX_WTI": "CL=F",
    "INDEX_GOLD": "GC=F",
    "INDEX_USDJPY": "JPY=X",
    "INDEX_EURJPY": "EURJPY=X",
    "INDEX_BTC": "BTC-USD",
    "INDEX_ETH": "ETH-USD",
}

def get_ticker_str(code):
    if code in INDICES_TICKER:
        return INDICES_TICKER[code]
    return f"{code}.T"

def update_all():
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} not found.")
        return

    # get all codes from data dir
    codes = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".js"):
            code = f.replace(".js", "")
            codes.append(code)

    codes.sort()
    
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=int(365.25 * YEARS))
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")

    failed_codes = []
    
    total = len(codes)
    for i, code in enumerate(codes, 1):
        ticker_str = get_ticker_str(code)
        print(f"[{i}/{total}] Fetching {code} ({ticker_str})...", end=" ")
        
        try:
            ticker_obj = yf.Ticker(ticker_str)
            df = ticker_obj.history(start=start_str, end=end_str, auto_adjust=True)
            
            if df.empty:
                print("Empty data.")
                failed_codes.append(code)
                continue
                
            df = df.sort_index()
            candles = []
            for date_idx, row in df.iterrows():
                try:
                    o = float(row["Open"])
                    h = float(row["High"])
                    l = float(row["Low"])
                    c = float(row["Close"])
                    v = int(row.get("Volume", 0))
                except Exception:
                    continue
                    
                if any(x != x for x in [o, h, l, c]):
                    continue
                    
                decimals = 2 if code.startswith("INDEX_") else 1
                candles.append({
                    "time": str(date_idx)[:10],
                    "open": round(o, decimals),
                    "high": round(h, decimals),
                    "low": round(l, decimals),
                    "close": round(c, decimals),
                    "volume": v,
                })
                
            if not candles:
                print("No valid candle data.")
                failed_codes.append(code)
                continue
                
            # Update data file
            # To get name we read existing name if possible, or just use code temporarily
            name = code
            file_path = os.path.join(DATA_DIR, f"{code}.js")
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # try to extract name
                        m = re.search(r'"name"\s*:\s*"([^"]+)"', content)
                        if m:
                            name = m.group(1)
                except:
                    pass
            
            output = {
                "code": code,
                "name": name,
                "ticker": ticker_str,
                "fetched_at": datetime.now().isoformat(),
                "count": len(candles),
                "candles": candles,
            }
            
            var_name = code.replace("-", "_").replace("=", "_").replace("^", "")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"window.STOCK_DATA_{var_name} = ")
                json.dump(output, f, ensure_ascii=False, indent=2)
                f.write(";")
                
            print(f"OK ({len(candles)} candles)")
            
        except Exception as e:
            print(f"Error: {e}")
            failed_codes.append(code)
            
        if i % 10 == 0:
            time.sleep(1)

    print("\n--- Failed Codes ---")
    print(failed_codes)
    
    if failed_codes:
        print("Cleaning up failed codes...")
        # 1. Delete data files
        for code in failed_codes:
            file_path = os.path.join(DATA_DIR, f"{code}.js")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")
                
        # 2. Remove from index.html
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        new_html_content = html_content
        for code in failed_codes:
            # Match formats like: '1234':{'name':'Name'}, or '1234': {'name': 'Name'}
            pattern1 = rf"'{code}'\s*:\s*{{[^}}]+}}(?:,\s*)?"
            pattern2 = rf"\"{code}\"\s*:\s*{{[^}}]+}}(?:,\s*)?"
            new_html_content = re.sub(pattern1, "", new_html_content)
            new_html_content = re.sub(pattern2, "", new_html_content)
            
        with open(INDEX_HTML, "w", encoding="utf-8") as f:
            f.write(new_html_content)
            
        print("Removed failed codes from index.html")
    
    print("All done!")

if __name__ == "__main__":
    update_all()
