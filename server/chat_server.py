#!/usr/bin/env python3
"""WebSocket チャットサーバ。クライアントからの接続を受け入れ、クライアントからのメッセージを全クライアントへ送信する。"""

import argparse
import asyncio
import json
from datetime import datetime, timezone
from typing import Any

import websockets


clients = {}

# 送信時刻はサーバ側で付与するため、クライアントからは受け取らない。
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# クライアントからの接続を受け入れ、メッセージを処理する。
async def broadcast(payload: dict[str, Any]) -> None:
    if not clients:
        return

    # payload を全クライアントへ送信する。接続切れなどで送信できないクライアントは切り離す。
    message = json.dumps(payload, ensure_ascii=False)
    disconnected = []

    # clients は接続中クライアントのWebSocketをキー、ユーザ名を値とする辞書。
    for ws in clients:
        try:
            #  送信時に例外が出る場合は接続切れとみなす。
            await ws.send(message)
        except websockets.ConnectionClosed:
            disconnected.append(ws)

    # 切断されたクライアントを clients から削除する。
    for ws in disconnected:
        clients.pop(ws, None)


# クライアントからの接続を処理する。クライアントごとに独立して呼び出される。
async def handle_client(ws) -> None:
    # クライアントが接続してきたとき、まだ名前がわからないので仮の名前をつける。
    guest_name = f"Guest-{id(ws) % 10000:04d}"
    # clients に ws をキー、名前を値として登録する。
    clients[ws] = guest_name

    # クライアントへ接続完了と名前の送信を行う。
    await ws.send(
        json.dumps(
            {
                "type": "system",
                "text": "接続しました。最初に名前を送信してください。",
                "sent_at": now_iso(),
            },
            ensure_ascii=False,
        )
    )

    # クライアントからのメッセージを処理するループ。接続切れなどで例外が出るまで続ける。
    try:
        async for raw in ws:
            try:
                # クライアントからのメッセージはJSON形式を想定する。形式が正しくない場合はエラーを返す。
                data = json.loads(raw)
            except json.JSONDecodeError:
                # JSON形式が正しくない場合はエラーを返す。
                await ws.send(
                    json.dumps(
                        {
                            "type": "error",
                            "text": "JSON形式が正しくありません。",
                            "sent_at": now_iso(),
                        },
                        ensure_ascii=False,
                    )
                )
                continue

            # type フィールドでメッセージの種類を判別する。type がない場合はエラーを返す。
            event_type = data.get("type")

            # type に応じて処理を分ける。join は名前の登録、chat はチャットメッセージの送信を行う。未対応の type の場合はエラーを返す。
            if event_type == "join":
                # join イベントはクライアントが最初に送るべきもので、これを受け取ったときに clients に名前を登録する。
                new_name = str(data.get("name", "")).strip()
                if not new_name:
                    # 名前が空の場合はエラーを返す。
                    await ws.send(
                        json.dumps(
                            {
                                "type": "error",
                                "text": "名前が空です。",
                                "sent_at": now_iso(),
                            },
                            ensure_ascii=False,
                        )
                    )
                    continue

                # すでに同じ名前が存在する場合はエラーを返す。
                old_name = clients.get(ws, guest_name)
                clients[ws] = new_name

                # 名前の変更を全クライアントへ通知する。最初は guest_name から new_name への変更になる。
                await broadcast(
                    {
                        "type": "system",
                        "text": f"{old_name} -> {new_name} が参加しました。",
                        "sent_at": now_iso(),
                    }
                )
                continue

            # chat イベントはクライアントが送るチャットメッセージで、これを受け取ったときに全クライアントへ送信する。
            if event_type == "chat":
                text = str(data.get("text", "")).strip()
                if not text:
                    continue

                # chat イベントを受け取ったとき、clients からクライアントの名前を取得する。クライアントの名前が見つからない場合は guest_name を使う。
                await broadcast(
                    {
                        "type": "chat",
                        "name": clients.get(ws, guest_name),
                        "text": text,
                        "sent_at": now_iso(),
                    }
                )
                continue

            # 未対応の type の場合はエラーを返す。
            await ws.send(
                json.dumps(
                    {
                        "type": "error",
                        "text": "未対応のtypeです。",
                        "sent_at": now_iso(),
                    },
                    ensure_ascii=False,
                )
            )

    except websockets.ConnectionClosed:
        pass
    # 接続が切れたとき、clients からクライアントを削除し、全クライアントへ退出を通知する。
    finally:
        left_name = clients.pop(ws, guest_name)
        await broadcast(
            {
                "type": "system",
                "text": f"{left_name} が退出しました。",
                "sent_at": now_iso(),
            }
        )


# コマンドライン引数を処理する。--host と --port を受け付ける。
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WebSocketチャットサーバ")
    parser.add_argument("--host", default="0.0.0.0", help="待受ホスト")
    parser.add_argument("--port", type=int, default=8765, help="待受ポート")
    return parser.parse_args()


# メイン関数。コマンドライン引数を処理し、WebSocketサーバを起動する。
async def main() -> None:
    args = parse_args()
    # WebSocketサーバを起動する。クライアントからの接続があるたびに handle_client が呼び出される。
    async with websockets.serve(handle_client, args.host, args.port):
        print(f"Chat server started: ws://{args.host}:{args.port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
