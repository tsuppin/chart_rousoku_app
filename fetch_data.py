#!/usr/bin/env python3
"""
株価データ取得スクリプト
yfinance を使用して 日経225銘柄 + 各種インデックス・為替・コモディティ・暗号資産の
日足データを JSON に保存します。

使用方法:
  pip install yfinance
  python fetch_data.py
"""

import yfinance as yf
import json
import os
import sys
import time
from datetime import datetime, timedelta

# ============================================================
# 設定
# ============================================================
STOCKS = {
    # 食料品
    "1332": {"name": "マルハニチロ",          "ticker": "1332.T"},
    "1333": {"name": "ニッスイ",              "ticker": "1333.T"},
    "2002": {"name": "日清製粉GHD",           "ticker": "2002.T"},
    "2269": {"name": "明治HD",                "ticker": "2269.T"},
    "2282": {"name": "日本ハム",              "ticker": "2282.T"},
    "2501": {"name": "サッポロHD",            "ticker": "2501.T"},
    "2502": {"name": "アサヒGHD",             "ticker": "2502.T"},
    "2503": {"name": "キリンHD",              "ticker": "2503.T"},
    "2531": {"name": "宝HD",                  "ticker": "2531.T"},
    "2801": {"name": "キッコーマン",          "ticker": "2801.T"},
    "2802": {"name": "味の素",                "ticker": "2802.T"},
    "2871": {"name": "ニチレイ",              "ticker": "2871.T"},
    "2914": {"name": "JT",                    "ticker": "2914.T"},
    # 繊維
    "3401": {"name": "帝人",                  "ticker": "3401.T"},
    "3402": {"name": "東レ",                  "ticker": "3402.T"},
    # パルプ・紙
    "3861": {"name": "王子HD",                "ticker": "3861.T"},
    "3863": {"name": "日本製紙",              "ticker": "3863.T"},
    # 化学
    "4004": {"name": "レゾナック・HD",        "ticker": "4004.T"},
    "4005": {"name": "住友化学",              "ticker": "4005.T"},
    "4021": {"name": "日産化学",              "ticker": "4021.T"},
    "4042": {"name": "東ソー",                "ticker": "4042.T"},
    "4043": {"name": "トクヤマ",              "ticker": "4043.T"},
    "4061": {"name": "デンカ",                "ticker": "4061.T"},
    "4063": {"name": "信越化学工業",          "ticker": "4063.T"},
    "4151": {"name": "協和キリン",            "ticker": "4151.T"},
    "4183": {"name": "三井化学",              "ticker": "4183.T"},
    "4188": {"name": "三菱ケミカルG",         "ticker": "4188.T"},
    "4208": {"name": "UBE",                   "ticker": "4208.T"},
    "4307": {"name": "野村総研",              "ticker": "4307.T"},
    "4324": {"name": "電通グループ",          "ticker": "4324.T"},
    "4452": {"name": "花王",                  "ticker": "4452.T"},
    "4502": {"name": "武田薬品",              "ticker": "4502.T"},
    "4503": {"name": "アステラス製薬",        "ticker": "4503.T"},
    "4506": {"name": "住友ファーマ",          "ticker": "4506.T"},
    "4507": {"name": "塩野義製薬",            "ticker": "4507.T"},
    "4519": {"name": "中外製薬",              "ticker": "4519.T"},
    "4523": {"name": "エーザイ",              "ticker": "4523.T"},
    "4528": {"name": "小野薬品",              "ticker": "4528.T"},
    "4543": {"name": "テルモ",                "ticker": "4543.T"},
    "4568": {"name": "第一三共",              "ticker": "4568.T"},
    "4578": {"name": "大塚HD",                "ticker": "4578.T"},
    # 石油
    "5019": {"name": "出光興産",              "ticker": "5019.T"},
    "5020": {"name": "ENEOS HD",              "ticker": "5020.T"},
    # ゴム
    "5108": {"name": "ブリヂストン",          "ticker": "5108.T"},
    # ガラス・土石
    "5201": {"name": "AGC",                   "ticker": "5201.T"},
    "5214": {"name": "日本電気硝子",          "ticker": "5214.T"},
    "5232": {"name": "住友大阪セメント",      "ticker": "5232.T"},
    "5233": {"name": "太平洋セメント",        "ticker": "5233.T"},
    "5301": {"name": "東海カーボン",          "ticker": "5301.T"},
    "5332": {"name": "TOTO",                  "ticker": "5332.T"},
    "5333": {"name": "日本碍子",              "ticker": "5333.T"},
    # 鉄鋼
    "5401": {"name": "日本製鉄",              "ticker": "5401.T"},
    "5406": {"name": "神戸製鋼所",            "ticker": "5406.T"},
    "5411": {"name": "JFE HD",                "ticker": "5411.T"},
    "5541": {"name": "大平洋金属",            "ticker": "5541.T"},
    # 非鉄金属
    "5631": {"name": "日本製鋼所",            "ticker": "5631.T"},
    "5703": {"name": "日本軽金属HD",          "ticker": "5703.T"},
    "5706": {"name": "三井金属",              "ticker": "5706.T"},
    "5707": {"name": "東邦亜鉛",              "ticker": "5707.T"},
    "5711": {"name": "三菱マテリアル",        "ticker": "5711.T"},
    "5713": {"name": "住友金属鉱山",          "ticker": "5713.T"},
    "5714": {"name": "DOWA HD",               "ticker": "5714.T"},
    "5715": {"name": "古河機械金属",          "ticker": "5715.T"},
    "5801": {"name": "古河電工",              "ticker": "5801.T"},
    "5802": {"name": "住友電工",              "ticker": "5802.T"},
    "5803": {"name": "フジクラ",              "ticker": "5803.T"},
    # 機械
    "6098": {"name": "リクルートHD",          "ticker": "6098.T"},
    "6103": {"name": "オークマ",              "ticker": "6103.T"},
    "6113": {"name": "アマダ",                "ticker": "6113.T"},
    "6146": {"name": "ディスコ",              "ticker": "6146.T"},
    "6301": {"name": "コマツ",                "ticker": "6301.T"},
    "6302": {"name": "住友重機",              "ticker": "6302.T"},
    "6305": {"name": "日立建機",              "ticker": "6305.T"},
    "6326": {"name": "クボタ",                "ticker": "6326.T"},
    "6361": {"name": "荏原製作所",            "ticker": "6361.T"},
    "6367": {"name": "ダイキン工業",          "ticker": "6367.T"},
    # 電気機器
    "6501": {"name": "日立製作所",            "ticker": "6501.T"},
    "6503": {"name": "三菱電機",              "ticker": "6503.T"},
    "6504": {"name": "富士電機",              "ticker": "6504.T"},
    "6506": {"name": "安川電機",              "ticker": "6506.T"},
    "6508": {"name": "明電舎",                "ticker": "6508.T"},
    "6594": {"name": "ニデック",              "ticker": "6594.T"},
    "6645": {"name": "オムロン",              "ticker": "6645.T"},
    "6674": {"name": "GSユアサ",              "ticker": "6674.T"},
    "6701": {"name": "NEC",                   "ticker": "6701.T"},
    "6702": {"name": "富士通",                "ticker": "6702.T"},
    "6703": {"name": "沖電気工業",            "ticker": "6703.T"},
    "6706": {"name": "電気興業",              "ticker": "6706.T"},
    "6724": {"name": "セイコーエプソン",      "ticker": "6724.T"},
    "6752": {"name": "パナソニックHD",        "ticker": "6752.T"},
    "6753": {"name": "シャープ",              "ticker": "6753.T"},
    "6758": {"name": "ソニーグループ",        "ticker": "6758.T"},
    "6762": {"name": "TDK",                   "ticker": "6762.T"},
    "6770": {"name": "アルプスアルパイン",    "ticker": "6770.T"},
    "6857": {"name": "アドバンテスト",        "ticker": "6857.T"},
    "6861": {"name": "キーエンス",            "ticker": "6861.T"},
    "6902": {"name": "デンソー",              "ticker": "6902.T"},
    "6952": {"name": "カシオ計算機",          "ticker": "6952.T"},
    "6954": {"name": "ファナック",            "ticker": "6954.T"},
    "6971": {"name": "京セラ",                "ticker": "6971.T"},
    "6976": {"name": "太陽誘電",              "ticker": "6976.T"},
    "6981": {"name": "村田製作所",            "ticker": "6981.T"},
    # 輸送用機器
    "7011": {"name": "三菱重工",              "ticker": "7011.T"},
    "7013": {"name": "IHI",                   "ticker": "7013.T"},
    "7201": {"name": "日産自動車",            "ticker": "7201.T"},
    "7202": {"name": "いすゞ自動車",          "ticker": "7202.T"},
    "7203": {"name": "トヨタ自動車",          "ticker": "7203.T"},
    "7211": {"name": "三菱自動車",            "ticker": "7211.T"},
    "7261": {"name": "マツダ",                "ticker": "7261.T"},
    "7267": {"name": "ホンダ",                "ticker": "7267.T"},
    "7269": {"name": "スズキ",                "ticker": "7269.T"},
    "7270": {"name": "SUBARU",                "ticker": "7270.T"},
    "7272": {"name": "ヤマハ発動機",          "ticker": "7272.T"},
    # 精密機器
    "7309": {"name": "シマノ",                "ticker": "7309.T"},
    "7731": {"name": "ニコン",                "ticker": "7731.T"},
    "7733": {"name": "オリンパス",            "ticker": "7733.T"},
    "7735": {"name": "SCREENホールディングス","ticker": "7735.T"},
    "7741": {"name": "HOYA",                  "ticker": "7741.T"},
    "7751": {"name": "キヤノン",              "ticker": "7751.T"},
    "7752": {"name": "リコー",                "ticker": "7752.T"},
    "7762": {"name": "シチズン時計",          "ticker": "7762.T"},
    # その他製品
    "7832": {"name": "バンダイナムコHD",      "ticker": "7832.T"},
    "7912": {"name": "大日本印刷",            "ticker": "7912.T"},
    "7951": {"name": "ヤマハ",                "ticker": "7951.T"},
    "7974": {"name": "任天堂",                "ticker": "7974.T"},
    # 商業
    "3543": {"name": "コメダホールディングス",  "ticker": "3543.T"},
    "8001": {"name": "伊藤忠商事",            "ticker": "8001.T"},
    "8002": {"name": "丸紅",                  "ticker": "8002.T"},
    "8015": {"name": "豊田通商",              "ticker": "8015.T"},
    "8031": {"name": "三井物産",              "ticker": "8031.T"},
    "8053": {"name": "住友商事",              "ticker": "8053.T"},
    "8058": {"name": "三菱商事",              "ticker": "8058.T"},
    "8233": {"name": "高島屋",                "ticker": "8233.T"},
    "8252": {"name": "丸井グループ",          "ticker": "8252.T"},
    "8267": {"name": "イオン",                "ticker": "8267.T"},
    # 金融・保険
    "8304": {"name": "あおぞら銀行",          "ticker": "8304.T"},
    "8306": {"name": "三菱UFJ FG",            "ticker": "8306.T"},
    "8308": {"name": "りそなHD",              "ticker": "8308.T"},
    "8309": {"name": "三井住友トラストHD",    "ticker": "8309.T"},
    "8316": {"name": "三井住友FG",            "ticker": "8316.T"},
    "8411": {"name": "みずほFG",              "ticker": "8411.T"},
    "8601": {"name": "大和証券G本社",         "ticker": "8601.T"},
    "8604": {"name": "野村HD",                "ticker": "8604.T"},
    "8630": {"name": "SOMPOホールディングス", "ticker": "8630.T"},
    "8725": {"name": "MS&AD インシュアランス", "ticker": "8725.T"},
    "8750": {"name": "第一生命HD",            "ticker": "8750.T"},
    "8766": {"name": "東京海上HD",            "ticker": "8766.T"},
    "8795": {"name": "T&D HD",               "ticker": "8795.T"},
    # 不動産
    "8801": {"name": "三井不動産",            "ticker": "8801.T"},
    "8802": {"name": "三菱地所",              "ticker": "8802.T"},
    "8804": {"name": "東京建物",              "ticker": "8804.T"},
    "8830": {"name": "住友不動産",            "ticker": "8830.T"},
    # 陸運
    "9001": {"name": "東武鉄道",              "ticker": "9001.T"},
    "9005": {"name": "東急",                  "ticker": "9005.T"},
    "9007": {"name": "小田急電鉄",            "ticker": "9007.T"},
    "9008": {"name": "京王電鉄",              "ticker": "9008.T"},
    "9009": {"name": "京成電鉄",              "ticker": "9009.T"},
    "9020": {"name": "JR東日本",              "ticker": "9020.T"},
    "9022": {"name": "JR東海",                "ticker": "9022.T"},
    "9064": {"name": "ヤマトHD",              "ticker": "9064.T"},
    # 海運
    "9101": {"name": "日本郵船",              "ticker": "9101.T"},
    "9104": {"name": "商船三井",              "ticker": "9104.T"},
    "9107": {"name": "川崎汽船",              "ticker": "9107.T"},
    # 空運
    "9202": {"name": "ANA HD",               "ticker": "9202.T"},
    # 倉庫
    "9301": {"name": "三菱倉庫",              "ticker": "9301.T"},
    # 通信
    "9432": {"name": "NTT",                   "ticker": "9432.T"},
    "9433": {"name": "KDDI",                  "ticker": "9433.T"},
    "9434": {"name": "ソフトバンク",          "ticker": "9434.T"},

    # 電気・ガス
    "9501": {"name": "東京電力HD",            "ticker": "9501.T"},
    "9502": {"name": "中部電力",              "ticker": "9502.T"},
    "9503": {"name": "関西電力",              "ticker": "9503.T"},
    "9531": {"name": "東京ガス",              "ticker": "9531.T"},
    "9532": {"name": "大阪ガス",              "ticker": "9532.T"},
    # サービス
    "9602": {"name": "東宝",                  "ticker": "9602.T"},
    "9735": {"name": "セコム",                "ticker": "9735.T"},
    "9983": {"name": "ファーストリテイリング","ticker": "9983.T"},
    "9984": {"name": "ソフトバンクG",         "ticker": "9984.T"},
    # 鉱業
    "1605": {"name": "INPEX",                 "ticker": "1605.T"},
    # 建設
    "1801": {"name": "大成建設",              "ticker": "1801.T"},
    "1802": {"name": "大林組",                "ticker": "1802.T"},
    "1803": {"name": "清水建設",              "ticker": "1803.T"},
    "1808": {"name": "長谷工コーポレーション","ticker": "1808.T"},
    "1812": {"name": "鹿島建設",              "ticker": "1812.T"},
    "1925": {"name": "大和ハウス工業",        "ticker": "1925.T"},
    "1928": {"name": "積水ハウス",            "ticker": "1928.T"},
    # 半導体・ソフトウェア
    "3436": {"name": "SUMCO",                 "ticker": "3436.T"},
    "4689": {"name": "LINEヤフー",            "ticker": "4689.T"},
    "9684": {"name": "スクウェア・エニックスHD","ticker": "9684.T"},
}

# ============================================================
# インデックス・為替・コモディティ・暗号資産
# ============================================================
INDICES = {
    # キー = ファイルコード（INDEX_ プレフィックスでHTMLと対応）
    "INDEX_N225":   {"name": "日経225",          "ticker": "^N225"},
    "INDEX_TOPX":   {"name": "TOPIX ETF",       "ticker": "1306.T"},
    "INDEX_DJI":    {"name": "NYダウ",           "ticker": "^DJI"},
    "INDEX_IXIC":   {"name": "ナスダック",       "ticker": "^IXIC"},
    "INDEX_GSPC":   {"name": "S&P500",           "ticker": "^GSPC"},
    "INDEX_WTI":    {"name": "WTI原油",          "ticker": "CL=F"},
    "INDEX_GOLD":   {"name": "金（ゴールド）",   "ticker": "GC=F"},
    "INDEX_USDJPY": {"name": "米ドル/円",        "ticker": "JPY=X"},
    "INDEX_EURJPY": {"name": "ユーロ/円",        "ticker": "EURJPY=X"},
    "INDEX_BTC":    {"name": "ビットコイン",     "ticker": "BTC-USD"},
    "INDEX_ETH":    {"name": "イーサリアム",     "ticker": "ETH-USD"},
}

YEARS      = 5           # データ期間（225銘柄でもVercel制限内に収まるよう5年）
OUTPUT_DIR = "data"


# ============================================================
# メイン処理
# ============================================================
def fetch_items(items_dict, start_str, end_str, label="銘柄"):
    """汎用データ取得関数。STOCKS / INDICES どちらにも使用。"""
    total = len(items_dict)
    success_count = 0
    fail_codes = []

    for i, (code, info) in enumerate(items_dict.items(), 1):
        ticker_str = info["ticker"]
        print(f"  [{i:3d}/{total}] {code} {info['name']} ({ticker_str}) ...", end=" ")

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

            # 小数点以下の桁数をデータ種別に応じて調整
            is_index_or_fx = code.startswith("INDEX_")
            decimals = 2 if is_index_or_fx else 1

            date_str = str(date_idx)[:10]
            candles.append({
                "time":   date_str,
                "open":   round(o, decimals),
                "high":   round(h, decimals),
                "low":    round(l, decimals),
                "close":  round(c, decimals),
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

        # ファイル名は code をそのまま使用（INDEX_N225.js など）
        safe_code = code.replace("/", "_").replace("=", "_").replace("^", "")
        out_path = os.path.join(OUTPUT_DIR, f"{code}.js")
        with open(out_path, "w", encoding="utf-8") as f:
            # JS変数名はアンダースコア等で安全に
            var_name = code.replace("-", "_").replace("=", "_").replace("^", "")
            f.write(f"window.STOCK_DATA_{var_name} = ")
            json.dump(output, f, ensure_ascii=False, indent=2)
            f.write(";")

        print(f"OK ({len(candles):,} 件)")
        success_count += 1

        # レート制限対策: 5件ごとに少し待つ
        if i % 5 == 0:
            time.sleep(1)

    return success_count, fail_codes


def fetch_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    end_dt   = datetime.now()
    start_dt = end_dt - timedelta(days=int(365.25 * YEARS))

    start_str = start_dt.strftime("%Y-%m-%d")
    end_str   = end_dt.strftime("%Y-%m-%d")

    print(f"\n[INFO] データ取得開始: {start_str} ~ {end_str}")

    # ── 1. インデックス・為替・コモディティ・暗号資産 ──────────────────
    print(f"\n[STEP 1] インデックス等 ({len(INDICES)} 件)")
    ok1, fail1 = fetch_items(INDICES, start_str, end_str, label="インデックス")

    # ── 2. 個別銘柄 ────────────────────────────────────────────────────
    print(f"\n[STEP 2] 個別銘柄 ({len(STOCKS)} 銘柄)")
    ok2, fail2 = fetch_items(STOCKS, start_str, end_str, label="銘柄")

    # ── 完了サマリー ───────────────────────────────────────────────────
    total_ok   = ok1 + ok2
    total_fail = fail1 + fail2
    print()
    print(f"[DONE] 成功: {total_ok} 件  失敗: {len(total_fail)} 件")
    if total_fail:
        print(f"[FAIL] 失敗: {', '.join(total_fail)}")
    print("\n次のコマンドでサーバーを起動してください:")
    print("  python start_server.py")
    print("ブラウザで  http://localhost:8080  を開いてください\n")


if __name__ == "__main__":
    fetch_all()
