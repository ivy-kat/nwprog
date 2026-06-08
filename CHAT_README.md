# WebSocket Chat App

このファイルは、同フォルダ内のチャットアプリ実行手順をまとめたものです。

- サーバ: server/chat_server.py
- クライアント: chat_client.py

## 事前準備

websockets パッケージが必要です。

```powershell
cd c:\Users\kataoka\Documents\nwprog
python -m pip install websockets
```

## サーバ起動

### 基本（引数なし）

```powershell
python .\server\chat_server.py
```

引数なしでも起動できます。既定値は以下です。

- --host: 0.0.0.0
- --port: 8765

### 引数を指定する場合

```powershell
python .\server\chat_server.py --host 0.0.0.0 --port 9000
```

## クライアント起動

### 基本（引数なし）

```powershell
python .\chat_client.py
```

引数なしでも接続できます。既定値は以下です。

- --url: ws://127.0.0.1:8765

起動後に名前入力プロンプトが表示されます。

### 接続先を指定する場合

```powershell
python .\chat_client.py --url ws://172.16.5.25:8765
```

## 操作

- メッセージを入力して Enter で送信
- /quit で終了

## 引数の要否まとめ

- サーバ: 引数は任意（未指定なら既定値で起動）
- クライアント: 引数は任意（未指定なら localhost に接続）

授業で同一サーバへ接続させる場合は、クライアントで --url 指定を使ってください。
