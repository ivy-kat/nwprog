#!/usr/bin/env python3
"""1行CSVテキストを受信し、ログファイルへ追記する。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from threading import Lock
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request

app = Flask(__name__)
LOG_FILE = Path("received.log")
LOG_LOCK = Lock()


@app.post("/report")
def report() -> tuple[str, int]:
    body = request.get_data(as_text=True)

    # 1リクエスト=1行になるよう、改行文字は除去する。
    safe_line = body.replace("\r", "").replace("\n", "")
    received_at = datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    log_line = f"{received_at},{safe_line}"

    # 複数スレッド同時受信時にログ行が混ざらないよう排他処理する。
    with LOG_LOCK:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            print(log_line)
            f.write(log_line + "\n")
    return "ok\n", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
