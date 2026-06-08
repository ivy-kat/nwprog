#!/usr/bin/env python3
"""1行のCSV (username,ip_address) をサーバへ送信する。"""

# import argparse
import getpass
import socket
import sys
from urllib import error, request

SERVER_URL = "http://172.16.5.25:5000/report"


def get_username() -> str:
    """ログオン中のユーザ名を返す。"""
    return getpass.getuser()


def get_primary_ip_address() -> str:
    """この端末の代表的なIPv4アドレスを取得する。
    UDPソケットで送信経路のインターフェースを推定し、
    取得できない場合は localhost を返す。
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # 宛先を仮に設定する（OSが8.8.8.8に出る時どのNIC/IPを使うか決める）
            # ルーティング判定しやすい代表例として8.8.8.8を使っているだけ
            sock.connect(("8.8.8.8", 80))
            # この時に選ばれた自分側のIPを読む
            return sock.getsockname()[0]
    except OSError:
        # オフライン時などのフォールバック用
        return "127.0.0.1"


def build_csv_line() -> str:
    """username, ip_address 形式の1行CSVを作る。"""
    username = get_username().replace(",", " ")
    ip_address = get_primary_ip_address().replace(",", " ")
    return f"{username},{ip_address}"


def post_text(url: str, line: str, timeout: float) -> tuple[int, str]:
    """プレーンテキストをPOSTし、(status_code, response_body) を返す。"""
    data = line.encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "text/plain; charset=utf-8"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.getcode(), body


# def parse_args(argv: list[str]) -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#         description="ユーザ名とIPアドレスを1行CSVで固定サーバへ送信する。",
#     )
#     parser.add_argument(
#         "--timeout",
#         type=float,
#         default=5.0,
#         help="HTTPタイムアウト秒数 (既定: 5.0)",
#     )
#     return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    # args = parse_args(argv)
    csv_line = build_csv_line()

    print(f"送信先URL: {SERVER_URL}")
    print("送信するCSV:")
    print(csv_line)

    try:
        status, body = post_text(SERVER_URL, csv_line, timeout=5.0)
    except error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTPエラー: {exc.code}", file=sys.stderr)
        if response_body:
            print(response_body, file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"接続エラー: {exc.reason}", file=sys.stderr)
        return 1
    except TimeoutError:
        print("接続がタイムアウトしました。", file=sys.stderr)
        return 1

    print(f"送信成功: HTTP {status}")
    if body:
        print("サーバ応答:", end="")
        print(body)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
