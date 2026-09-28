import os
import re
import sys
import json
import time
from datetime import datetime, timedelta
import yfinance as yf

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

    # 全銘柄コードと既存の名称を取得
    codes = []
    names = {}
    for f in os.listdir(DATA_DIR):
        if f.endswith(".js"):
            code = f.replace(".js", "")
            codes.append(code)
            file_path = os.path.join(DATA_DIR, f)
            try:
                with open(file_path, "r", encoding="utf-8") as fp:
                    m = re.search(r'"name"\s*:\s*"([^"]+)"', fp.read(500))
                    names[code] = m.group(1) if m else code
            except Exception:
                names[code] = code

    codes.sort()
    
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=int(365.25 * YEARS))
    start_str = start_dt.strftime("%Y-%m-%d")

    failed_codes = []
    updated_count = 0
    total = len(codes)
    
    print(f"=== 全 {total} 銘柄の株価データ更新開始 (期間: {start_str} 〜 最新) ===")

    for i, code in enumerate(codes, 1):
        ticker_str = get_ticker_str(code)
        stock_name = names.get(code, code)
        print(f"[{i}/{total}] {code} ({stock_name} / {ticker_str})...", end=" ", flush=True)
        
        success = False
        last_error = ""

        # リトライ含め最大3回試行
        for attempt in range(3):
            try:
                ticker_obj = yf.Ticker(ticker_str)
                # endパラメータを指定しないことで最新の取引データ（当日分）まで取得
                df = ticker_obj.history(start=start_str, auto_adjust=True)
                
                if df is None or df.empty:
                    last_error = "Empty data"
                    time.sleep(1.0)
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
                    last_error = "No valid candle data"
                    time.sleep(1.0)
                    continue

                # データ更新
                output = {
                    "code": code,
                    "name": stock_name,
                    "ticker": ticker_str,
                    "fetched_at": datetime.now().isoformat(),
                    "count": len(candles),
                    "candles": candles,
                }
                
                var_name = code.replace("-", "_").replace("=", "_").replace("^", "")
                file_path = os.path.join(DATA_DIR, f"{code}.js")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"window.STOCK_DATA_{var_name} = ")
                    json.dump(output, f, ensure_ascii=False, indent=2)
                    f.write(";")
                    
                print(f"OK ({len(candles)} candles, 最新: {candles[-1]['time']})")
                updated_count += 1
                success = True
                break

            except Exception as e:
                last_error = str(e)
                time.sleep(1.5)

        if not success:
            print(f"FAILED ({last_error})")
            failed_codes.append((code, stock_name, last_error))

        if i % 15 == 0:
            time.sleep(0.5)

    print("\n" + "=" * 50)
    print(f"更新完了サマリー:")
    print(f"  総銘柄数: {total}")
    print(f"  更新成功: {updated_count}")
    print(f"  取得失敗（削除対象）: {len(failed_codes)}")
    
    if failed_codes:
        print("\n--- 取得できなかった銘柄（削除処理実行） ---")
        for c, n, err in failed_codes:
            print(f"  {c} ({n}): {err}")

        # 1. data/ からファイル削除
        deleted_files = 0
        for c, n, _ in failed_codes:
            file_path = os.path.join(DATA_DIR, f"{c}.js")
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files += 1
                print(f"  削除: {file_path}")
        print(f"  データファイル削除完了: {deleted_files} 件")

        # 2. index.html から削除
        if os.path.exists(INDEX_HTML):
            with open(INDEX_HTML, "r", encoding="utf-8") as f:
                html_content = f.read()

            new_html_content = html_content
            removed_from_html = 0
            for c, n, _ in failed_codes:
                # '1234':{'name':'Name'}, or '1234': {'name': 'Name'} などのパターンにマッチ
                pattern = rf"\s*['\"]?{c}['\"]?\s*:\s*\{{[^}}]*\}}\s*,?"
                if re.search(pattern, new_html_content):
                    new_html_content = re.sub(pattern, "", new_html_content)
                    removed_from_html += 1

            if removed_from_html > 0:
                # 末尾の余計なカンマや空行の調整
                new_html_content = re.sub(r",\s*};", "\n};", new_html_content)
                with open(INDEX_HTML, "w", encoding="utf-8") as f:
                    f.write(new_html_content)
                print(f"  index.html から削除完了: {removed_from_html} 件")
            else:
                print("  index.html に対象銘柄は含まれていませんでした")

    print("\n全ての処理が完了しました。")

if __name__ == "__main__":
    update_all()
