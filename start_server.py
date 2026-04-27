#!/usr/bin/env python3
"""
簡易 HTTP サーバー起動スクリプト

使用方法:
  python start_server.py

ブラウザが自動で開きます。終了は Ctrl+C。
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os
import sys

PORT = 8080


def main():
    # スクリプトが置かれているディレクトリを静的ルートにする
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # data フォルダが存在するか確認
    if not os.path.isdir("data"):
        print("[WARN] data/ folder not found.")
        print("Run fetch_data.py first:\n")
        print("  python fetch_data.py\n")
        sys.exit(1)

    json_files = [f for f in os.listdir("data") if f.endswith(".json")]
    if not json_files:
        print("[WARN] No JSON files in data/ folder.")
        print("Run fetch_data.py first:\n")
        print("  python fetch_data.py\n")
        sys.exit(1)

    class Handler(http.server.SimpleHTTPRequestHandler):
        """ログを最小限にした静的ファイルサーバー"""
        def log_message(self, format, *args):
            # 2xx/3xx は無視
            if args and str(args[1]).startswith(('2', '3')):
                return
            pass  # エラーも無視（シンプルモード）

    print(f"\n{'=' * 50}")
    print(f"  [SERVER] Souba-Ryu Chart Viewer")
    print(f"  URL: http://localhost:{PORT}")
    print(f"  Stop: Ctrl+C")
    print(f"{'=' * 50}\n")

    # 1秒後にブラウザを自動で開く
    def open_browser():
        time.sleep(1.2)
        webbrowser.open(f"http://localhost:{PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[DONE] Server stopped.")
    except OSError as e:
        # ポートが使用中（Windows: errno 10048, Linux: errno 98）
        if e.errno in (10048, 98):
            print(f"\n[ERROR] Port {PORT} is already in use.")
            print("Stop another server process, or open http://localhost:8080 directly.")
        else:
            raise


if __name__ == "__main__":
    main()
