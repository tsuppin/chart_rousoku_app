#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平均出来高60万株以上 かつ chart_rousoku_app未保有の JPX400銘柄
27銘柄の株価データをyfinanceで取得して data/ に保存する
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import yfinance as yf
import json
import os
import time
from datetime import datetime, timedelta

# ============================================================
# 対象27銘柄（業種別）
# ============================================================
TARGET_STOCKS = {
    # 電気機器
    "6723": {"name": "ルネサスエレクトロニクス", "ticker": "6723.T"},
    "6920": {"name": "レーザーテック",           "ticker": "6920.T"},
    "6479": {"name": "ミネベアミツミ",           "ticker": "6479.T"},
    # 輸送用機器
    "7012": {"name": "川崎重工業",               "ticker": "7012.T"},
    # 情報通信・IT
    "4755": {"name": "楽天グループ",             "ticker": "4755.T"},
    "3697": {"name": "SHIFT",                    "ticker": "3697.T"},
    "2413": {"name": "エムスリー",               "ticker": "2413.T"},
    "3659": {"name": "ネクソン",                 "ticker": "3659.T"},
    "4385": {"name": "メルカリ",                 "ticker": "4385.T"},
    "4180": {"name": "Appier Group",             "ticker": "4180.T"},
    "4704": {"name": "トレンドマイクロ",         "ticker": "4704.T"},
    "4478": {"name": "フリー",                   "ticker": "4478.T"},
    # 小売
    "7532": {"name": "パン・パシフィックHD",     "ticker": "7532.T"},
    "3382": {"name": "セブン＆アイHD",           "ticker": "3382.T"},
    "3563": {"name": "FOOD & LIFE COMPANIES",    "ticker": "3563.T"},
    # サービス
    "2181": {"name": "パーソルHD",               "ticker": "2181.T"},
    "4661": {"name": "オリエンタルランド",       "ticker": "4661.T"},
    "6532": {"name": "ベイカレント・C",          "ticker": "6532.T"},
    # 金融
    "6178": {"name": "日本郵政",                 "ticker": "6178.T"},
    "8591": {"name": "オリックス",               "ticker": "8591.T"},
    # 化学
    "4901": {"name": "富士フイルムHD",           "ticker": "4901.T"},
    # 証券
    "8473": {"name": "SBI HD",                   "ticker": "8473.T"},
    # 建設
    "1963": {"name": "日揮HD",                   "ticker": "1963.T"},
    "1721": {"name": "コムシスHD",               "ticker": "1721.T"},
    # 医薬品
    "4565": {"name": "そーせいグループ",         "ticker": "4565.T"},
    # ガラス・土石
    "5334": {"name": "日本特殊陶業",             "ticker": "5334.T"},
    # 銀行
    "8354": {"name": "ふくおかFG",               "ticker": "8354.T"},
}

YEARS      = 5
OUTPUT_DIR = "data"

def fetch_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    end_dt   = datetime.now()
    start_dt = end_dt - timedelta(days=int(365.25 * YEARS))
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str   = end_dt.strftime("%Y-%m-%d")

    print(f"\n[INFO] データ取得: {start_str} ~ {end_str}")
    print(f"[INFO] 対象銘柄: {len(TARGET_STOCKS)} 銘柄\n")

    success_codes = []
    fail_codes    = []
    total = len(TARGET_STOCKS)

    for i, (code, info) in enumerate(TARGET_STOCKS.items(), 1):
        ticker_str = info["ticker"]
        print(f"  [{i:2d}/{total}] {code} {info['name']} ({ticker_str}) ...", end=" ", flush=True)

        try:
            ticker_obj = yf.Ticker(ticker_str)
            df = ticker_obj.history(
                start=start_str,
                end=end_str,
                auto_adjust=True,
            )
        except Exception as e:
            print(f"ERROR: {e}")
            fail_codes.append(code)
            continue

        if df.empty:
            print("WARN: データなし")
            fail_codes.append(code)
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
            except (TypeError, ValueError, KeyError):
                continue

            if any(x != x for x in [o, h, l, c]):
                continue

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
            print("WARN: 有効データ0件")
            fail_codes.append(code)
            continue

        output = {
            "code":       code,
            "name":       info["name"],
            "ticker":     ticker_str,
            "fetched_at": datetime.now().isoformat(),
            "count":      len(candles),
            "candles":    candles,
        }

        out_path = os.path.join(OUTPUT_DIR, f"{code}.js")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"window.STOCK_DATA_{code} = ")
            json.dump(output, f, ensure_ascii=False, indent=2)
            f.write(";")

        print(f"OK ({len(candles):,} 件)  →  {out_path}")
        success_codes.append(code)

        # レート制限対策
        if i % 5 == 0:
            time.sleep(1)

    print()
    print("=" * 60)
    print(f"[DONE] 成功: {len(success_codes)} 件  失敗: {len(fail_codes)} 件")
    if fail_codes:
        print(f"[FAIL] 失敗銘柄: {', '.join(fail_codes)}")
    print("=" * 60)

if __name__ == "__main__":
    fetch_all()
