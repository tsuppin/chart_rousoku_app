#!/usr/bin/env python3
"""インデックス・為替・コモディティ・暗号資産データ取得"""
import yfinance as yf
import json
import os
from datetime import datetime, timedelta

INDICES = {
    'INDEX_N225':    {'name': '日経225',             'ticker': '^N225'},
    'INDEX_TOPX':    {'name': 'TOPIX ETF',           'ticker': '1306.T'},
    'INDEX_JPX400':  {'name': 'JPX日経400 ETF',      'ticker': '1591.T'},
    'INDEX_GR250':   {'name': '東証グロース250 ETF', 'ticker': '2516.T'},
    'INDEX_REIT':    {'name': '東証REIT指数 ETF',    'ticker': '1343.T'},
    'INDEX_DJI':     {'name': 'NYダウ',              'ticker': '^DJI'},
    'INDEX_IXIC':    {'name': 'ナスダック',          'ticker': '^IXIC'},
    'INDEX_NDX':     {'name': 'ナスダック100',       'ticker': '^NDX'},
    'INDEX_GSPC':    {'name': 'S&P500',              'ticker': '^GSPC'},
    'INDEX_RUT':     {'name': 'ラッセル2000',        'ticker': '^RUT'},
    'INDEX_DAX':     {'name': 'ドイツDAX',           'ticker': '^GDAXI'},
    'INDEX_FTSE':    {'name': 'イギリスFTSE100',     'ticker': '^FTSE'},
    'INDEX_CAC':     {'name': 'フランスCAC40',       'ticker': '^FCHI'},
    'INDEX_STOXX50': {'name': 'ユーロ・ストックス50','ticker': '^STOXX50E'},
    'INDEX_NIFTY':   {'name': 'インドNifty50',       'ticker': '^NSEI'},
    'INDEX_SENSEX':  {'name': 'インドSENSEX',        'ticker': '^BSESN'},
    'INDEX_TWII':    {'name': '台湾加権指数',        'ticker': '^TWII'},
    'INDEX_HSI':     {'name': '香港ハンセン指数',    'ticker': '^HSI'},
    'INDEX_SSEC':    {'name': '中国上海総合指数',    'ticker': '000001.SS'},
    'INDEX_KOSPI':   {'name': '韓国KOSPI',           'ticker': '^KS11'},
    'INDEX_ASX200':  {'name': '豪ASX200',            'ticker': '^AXJO'},
    'INDEX_WTI':       {'name': 'WTI原油',                   'ticker': 'CL=F'},
    'INDEX_BRENT':     {'name': 'ブレント原油',              'ticker': 'BZ=F'},
    'INDEX_NATGAS':    {'name': '天然ガス',                  'ticker': 'NG=F'},
    'INDEX_GOLD':      {'name': '金(ゴールド)',              'ticker': 'GC=F'},
    'INDEX_SILVER':    {'name': '銀(シルバー)',              'ticker': 'SI=F'},
    'INDEX_PLATINUM':  {'name': 'プラチナ(白金)',            'ticker': 'PL=F'},
    'INDEX_PALLADIUM': {'name': 'パラジウム',                'ticker': 'PA=F'},
    'INDEX_COPPER':    {'name': '銅(カッパー)',              'ticker': 'HG=F'},
    'INDEX_CORN':      {'name': 'トウモロコシ',              'ticker': 'ZC=F'},
    'INDEX_SOYBEAN':   {'name': '大豆',                      'ticker': 'ZS=F'},
    'INDEX_WHEAT':     {'name': '小麦',                      'ticker': 'ZW=F'},
    'INDEX_COFFEE':    {'name': 'コーヒー',                  'ticker': 'KC=F'},
    'INDEX_SUGAR':     {'name': '砂糖',                      'ticker': 'SB=F'},
    'INDEX_USDJPY':    {'name': '米ドル/円',                 'ticker': 'JPY=X'},
    'INDEX_EURJPY':    {'name': 'ユーロ/円',                 'ticker': 'EURJPY=X'},
    'INDEX_GBPJPY':    {'name': '英ポンド/円',               'ticker': 'GBPJPY=X'},
    'INDEX_AUDJPY':    {'name': '豪ドル/円',                 'ticker': 'AUDJPY=X'},
    'INDEX_NZDJPY':    {'name': 'NZドル/円',                 'ticker': 'NZDJPY=X'},
    'INDEX_CADJPY':    {'name': 'カナダドル/円',             'ticker': 'CADJPY=X'},
    'INDEX_CHFJPY':    {'name': 'スイスフラン/円',           'ticker': 'CHFJPY=X'},
    'INDEX_EURUSD':    {'name': 'ユーロ/米ドル',             'ticker': 'EURUSD=X'},
    'INDEX_GBPUSD':    {'name': '英ポンド/米ドル',           'ticker': 'GBPUSD=X'},
    'INDEX_AUDUSD':    {'name': '豪ドル/米ドル',             'ticker': 'AUDUSD=X'},
    'INDEX_NZDUSD':    {'name': 'NZドル/米ドル',             'ticker': 'NZDUSD=X'},
    'INDEX_USDCHF':    {'name': '米ドル/スイスフラン',       'ticker': 'USDCHF=X'},
    'INDEX_USDCAD':    {'name': '米ドル/カナダドル',         'ticker': 'USDCAD=X'},
    'INDEX_EURGBP':    {'name': 'ユーロ/英ポンド',           'ticker': 'EURGBP=X'},
    'INDEX_BTC':       {'name': 'ビットコイン',              'ticker': 'BTC-USD'},
    'INDEX_ETH':       {'name': 'イーサリアム',              'ticker': 'ETH-USD'},
    'INDEX_XRP':       {'name': 'リップル(XRP)',             'ticker': 'XRP-USD'},
    'INDEX_SOL':       {'name': 'ソラナ(SOL)',               'ticker': 'SOL-USD'},
    'INDEX_BNB':       {'name': 'バイナンスコイン(BNB)',     'ticker': 'BNB-USD'},
    'INDEX_DOGE':      {'name': 'ドージコイン(DOGE)',        'ticker': 'DOGE-USD'},
    'INDEX_ADA':       {'name': 'カルダノ(ADA)',             'ticker': 'ADA-USD'},
    'INDEX_AVAX':      {'name': 'アバランチ(AVAX)',          'ticker': 'AVAX-USD'},
    'INDEX_LINK':      {'name': 'チェーンリンク(LINK)',      'ticker': 'LINK-USD'},
    'INDEX_LTC':       {'name': 'ライトコイン(LTC)',         'ticker': 'LTC-USD'},
    'INDEX_BCH':       {'name': 'ビットコインキャッシュ(BCH)','ticker': 'BCH-USD'},
    'INDEX_DOT':       {'name': 'ポルカドット(DOT)',         'ticker': 'DOT-USD'},
    'INDEX_XLM':       {'name': 'ステラルーメン(XLM)',       'ticker': 'XLM-USD'},
}

end_dt = datetime.now()
start_dt = end_dt - timedelta(days=int(365.25 * 5))
start_str = start_dt.strftime('%Y-%m-%d')
end_str = end_dt.strftime('%Y-%m-%d')

os.makedirs('data', exist_ok=True)

for code, info in INDICES.items():
    print(f'Fetching {code} ({info["ticker"]})...', end=' ')
    try:
        df = yf.Ticker(info['ticker']).history(start=start_str, end=end_str, auto_adjust=True)
        if df.empty:
            print('NO DATA')
            continue
        df = df.sort_index()
        candles = []
        for date_idx, row in df.iterrows():
            try:
                o = float(row['Open'])
                h = float(row['High'])
                l = float(row['Low'])
                c = float(row['Close'])
                v = int(row.get('Volume', 0))
            except Exception:
                continue
            if any(x != x for x in [o, h, l, c]):
                continue
            decimals = 4 if c < 10 else 2
            candles.append({
                'time': str(date_idx)[:10],
                'open': round(o, decimals),
                'high': round(h, decimals),
                'low': round(l, decimals),
                'close': round(c, decimals),
                'volume': v,
            })
        if not candles:
            print('NO CANDLES')
            continue
        output = {
            'code': code,
            'name': info['name'],
            'ticker': info['ticker'],
            'fetched_at': datetime.now().isoformat(),
            'count': len(candles),
            'candles': candles,
        }
        var_name = code.replace('-', '_').replace('=', '_').replace('^', '')
        with open(f'data/{code}.js', 'w', encoding='utf-8') as f:
            f.write(f'window.STOCK_DATA_{var_name} = ')
            json.dump(output, f, ensure_ascii=False, indent=2)
            f.write(';')
        print(f'OK ({len(candles)} candles)')
    except Exception as e:
        print(f'ERROR: {e}')

print('Done!')
