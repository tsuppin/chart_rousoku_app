#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOPIX 出来高60万株以上かつアプリ未保有の銘柄について、
5年分の株価データをyfinanceで取得し、data/ ディレクトリにJSファイルとして保存する。
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import json
import time
from datetime import datetime, timedelta
import yfinance as yf

# ============================================================
# 設定
# ============================================================
JSON_PATH   = r"c:\Users\tsuyoshi_tsuchiya\.gemini\antigravity\brain\60228439-d72d-4f39-8775-4bc82eea9e12\topix_missing_high_volume.json"
OUTPUT_DIR  = r"c:\Users\tsuyoshi_tsuchiya\.gemini\antigravity\scratch\chart_rousoku_app\data"
YEARS       = 5
BATCH_SIZE  = 40  # バッチ処理サイズ

def fetch_all():
    if not os.path.exists(JSON_PATH):
        print(f"[ERROR] JSONファイルが見つかりません: {JSON_PATH}")
        sys.exit(1)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    stocks = data.get("stocks", [])
    total_stocks = len(stocks)
    print(f"[INFO] 取得対象の銘柄数: {total_stocks} 銘柄")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 取得期間
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=int(365.25 * YEARS))
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str   = end_dt.strftime("%Y-%m-%d")

    print(f"[INFO] データ期間: {start_str} ~ {end_str}")

    success_count = 0
    fail_count = 0
    fail_list = []

    # バッチに分割してダウンロード
    for idx in range(0, total_stocks, BATCH_SIZE):
        batch = stocks[idx:idx+BATCH_SIZE]
        tickers = [f"{s['code']}.T" for s in batch]
        print(f"\n[INFO] バッチ [{idx+1}-{min(idx+BATCH_SIZE, total_stocks)}/{total_stocks}] ダウンロード中...")

        try:
            df = yf.download(
                tickers,
                start=start_str,
                end=end_str,
                auto_adjust=True,
                progress=False,
                group_by="ticker"
            )
        except Exception as e:
            print(f"[ERROR] バッチのダウンロードに失敗しました: {e}")
            fail_count += len(batch)
            fail_list.extend([s['code'] for s in batch])
            continue

        if df.empty:
            print("[WARN] データが空です")
            fail_count += len(batch)
            fail_list.extend([s['code'] for s in batch])
            continue

        # 各銘柄のデータを処理
        for s in batch:
            code = s["code"]
            name = s["name"]
            ticker_str = f"{code}.T"

            try:
                if len(tickers) == 1:
                    stock_df = df
                else:
                    if ticker_str not in df.columns.levels[0]:
                        print(f"  {code} {name} ... データなし（スキップ）")
                        fail_count += 1
                        fail_list.append(code)
                        continue
                    stock_df = df[ticker_str]

                stock_df = stock_df.dropna(subset=["Open", "High", "Low", "Close"])
                if stock_df.empty:
                    print(f"  {code} {name} ... 有効データなし（スキップ）")
                    fail_count += 1
                    fail_list.append(code)
                    continue

                stock_df = stock_df.sort_index()
                candles = []

                for date_idx, row in stock_df.iterrows():
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
                    print(f"  {code} {name} ... 有効キャンドル数 0（スキップ）")
                    fail_count += 1
                    fail_list.append(code)
                    continue

                # JS形式で保存
                output = {
                    "code":       code,
                    "name":       name,
                    "ticker":     ticker_str,
                    "fetched_at": datetime.now().isoformat(),
                    "count":      len(candles),
                    "candles":    candles,
                }

                out_path = os.path.join(OUTPUT_DIR, f"{code}.js")
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(f"window.STOCK_DATA_{code} = ")
                    json.dump(output, out_f, ensure_ascii=False, indent=2)
                    out_f.write(";")

                print(f"  {code} {name} ... OK ({len(candles):,} 件)")
                success_count += 1

            except Exception as e:
                print(f"  {code} {name} ... エラー: {e}")
                fail_count += 1
                fail_list.append(code)

        time.sleep(1.0)

    print("\n" + "="*60)
    print(f"[SUMMARY] 処理完了")
    print(f" 成功: {success_count} 銘柄")
    print(f" 失敗: {fail_count} 銘柄")
    if fail_list:
        print(f" 失敗リスト: {', '.join(fail_list)}")
    print("="*60)

if __name__ == "__main__":
    fetch_all()
