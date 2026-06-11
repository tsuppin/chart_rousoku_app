#!/usr/bin/env python3
"""インデックス・為替・コモディティ・暗号資産データ取得"""
import yfinance as yf
import json
import os
from datetime import datetime, timedelta

INDICES = {
    'INDEX_N225':   {'name': '日経225',       'ticker': '^N225'},
    'INDEX_TOPX':   {'name': 'TOPIX ETF',       'ticker': '1306.T'},
    'INDEX_DJI':    {'name': 'NYダウ',         'ticker': '^DJI'},
    'INDEX_IXIC':   {'name': 'ナスダック',     'ticker': '^IXIC'},
    'INDEX_GSPC':   {'name': 'S&P500',         'ticker': '^GSPC'},
    'INDEX_WTI':    {'name': 'WTI原油',        'ticker': 'CL=F'},
    'INDEX_GOLD':   {'name': '金(ゴールド)',   'ticker': 'GC=F'},
    'INDEX_USDJPY': {'name': '米ドル/円',      'ticker': 'JPY=X'},
    'INDEX_EURJPY': {'name': 'ユーロ/円',      'ticker': 'EURJPY=X'},
    'INDEX_BTC':    {'name': 'ビットコイン',   'ticker': 'BTC-USD'},
    'INDEX_ETH':    {'name': 'イーサリアム',   'ticker': 'ETH-USD'},
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
            candles.append({
                'time': str(date_idx)[:10],
                'open': round(o, 2),
                'high': round(h, 2),
                'low': round(l, 2),
                'close': round(c, 2),
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
