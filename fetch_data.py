#!/usr/bin/env python3
"""
株価データ取得スクリプト
yfinance を使用して JPX 上場銘柄の日足データを JSON に保存します。

使用方法:
  pip install yfinance
  python fetch_data.py
"""

import yfinance as yf
import json
import os
import sys
from datetime import datetime, timedelta

# ============================================================
# 設定
# ============================================================
STOCKS = {
    "1801": {"name": "大成建設",               "ticker": "1801.T"},
    "3436": {"name": "SUMCO",                  "ticker": "3436.T"},
    "9684": {"name": "スクウェア・エニックス HD", "ticker": "9684.T"},
}

YEARS      = 11          # 余裕を持って 11 年分取得（10 年以上確保）
OUTPUT_DIR = "data"


# ============================================================
# メイン処理
# ============================================================
def fetch_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    end_dt   = datetime.now()
    start_dt = end_dt - timedelta(days=int(365.25 * YEARS))

    start_str = start_dt.strftime("%Y-%m-%d")
    end_str   = end_dt.strftime("%Y-%m-%d")

    print(f"\n[INFO] 株価データ取得開始: {start_str} ~ {end_str}\n")

    success_count = 0

    for code, info in STOCKS.items():
        ticker_str = info["ticker"]
        print(f"  >> {code}  {info['name']}  ({ticker_str}) ...")

        try:
            ticker_obj = yf.Ticker(ticker_str)
            df = ticker_obj.history(
                start=start_str,
                end=end_str,
                auto_adjust=True,
            )
        except Exception as e:
            print(f"    [ERROR] 取得エラー: {e}")
            continue

        if df.empty:
            print(f"    [WARN]  データが空でした（ティッカーを確認してください）")
            continue

        df = df.sort_index()

        candles = []
        for date_idx, row in df.iterrows():
            try:
                o = float(row["Open"])
                h = float(row["High"])
                l = float(row["Low"])
                c = float(row["Close"])
                v = int(row["Volume"])
            except (TypeError, ValueError, KeyError):
                continue

            # NaN チェック
            if any(x != x for x in [o, h, l, c]):  # NaN != NaN
                continue

            # 日付文字列 YYYY-MM-DD
            date_str = str(date_idx)[:10]

            candles.append({
                "time":   date_str,
                "open":   round(o, 1),
                "high":   round(h, 1),
                "low":    round(l, 1),
                "close":  round(c, 1),
                "volume": v,
            })

        if not candles:
            print(f"    [WARN]  有効なデータが 0 件でした")
            continue

        output = {
            "code":       code,
            "name":       info["name"],
            "ticker":     ticker_str,
            "fetched_at": datetime.now().isoformat(),
            "count":      len(candles),
            "candles":    candles,
        }

        out_path = os.path.join(OUTPUT_DIR, f"{code}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"    [OK]   {len(candles):,} 件  -> {out_path}")
        success_count += 1

    print()
    if success_count == 0:
        print("[ERROR] データを取得できませんでした。ネットワーク接続を確認してください。")
        sys.exit(1)

    print(f"[DONE] {success_count} 銘柄のデータ取得完了!")
    print("\n次のコマンドでサーバーを起動してください:")
    print("  python start_server.py")
    print("ブラウザで  http://localhost:8080  を開いてください\n")


if __name__ == "__main__":
    fetch_all()
