# Python動作確認用クライアント/サーバ

動作確認用の最小構成です。

- クライアント: `username,ip_address` の1行CSVテキストをPOST
- サーバ: 受信した文字列をそのまま1行ログ追記

## 仕様（クライアント）

- 取得情報
  - `username`: ログオンユーザ名
  - `ip_address`: 端末の主IPv4アドレス
- 送信先URL: `http://172.16.5.25:5000/report`（クライアントに固定）
- 送信データ: `username,ip_address` の1行CSV
- 送信方式: `Content-Type: text/plain; charset=utf-8` で `POST`
- 依存ライブラリ: なし (Python標準ライブラリのみ)

## クライアント実行方法

PowerShell 例:

```powershell
cd c:\Users\kataoka\Documents\nwprog
python .\client_report.py
```

<!--
タイムアウト指定:

```powershell
python .\client_report.py --timeout 10
```
-->

## 送信テキスト例

```text
student01,192.168.1.23
```

ここまで

<!--
# ★★★教員側で実行しますので、これ以下は実行不要です★★★
## サーバ実行方法（Flask）

Flaskだけ必要なのでインストールします。

```powershell
cd c:\Users\kataoka\Documents\nwprog
python -m pip install flask
```

実行:

```powershell
python .\server_log.py
```

受信データは同フォルダの `received.log` に追記されます。
-->
## 注意

- `ip_address` は端末の主な送信経路のIPv4を推定して取得します。
- ネットワーク環境によっては `127.0.0.1` が返る場合があります。
