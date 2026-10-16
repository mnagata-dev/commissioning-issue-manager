# Phase 1・1台目のOneDrive実機検証準備

作成日: 2026-10-16。**準備時点では以下の実機操作は未実行で、成果物は手順のみだった。**
その後実施したオンライン基本試験の結果は[検証結果文書の8・9章](../../docs/sync/sync_phase_0_1_validation_results.md#9-2026-10-16-クラウド経由の整合性受信確認)を参照する。以下の「今回」は準備時点を指す。
既存の方針・計画・結果文書は変更しない。本書は検証専用の操作メモであり、同期仕様ではない。

## 今回確認したこと

- 作業ブランチは `main`。ブランチ変更、commit、push、PR、Mergeは行っていない。
- 指定Windowsフォルダーは下記WSLパスに存在し、`os.scandir` で直下2エントリーを列挙できた。
- 実施したアクセスはディレクトリの属性確認と列挙のみ。ファイル本文の読取り、ハッシュ計算、書込み、削除はしていない。
- よってディレクトリアクセスは確認済み。ファイル本文の読取り可否、プレースホルダー取得、書込み権限は未検証。
- WindowsとSharePointのテストファイル双方向反映はユーザーによるStep 1完了報告。今回再実行していない。

```text
<ONEDRIVE_SYNC_ROOT>
```

## 既存プログラムの判断

`transport.py` は標準ライブラリのみの独立部品。`Peer` の初期化でローカルSQLiteと incoming/outgoing/quarantineを作る。`change` がレコードとOutboxを同一トランザクションで保存し、`publish` がpart→jsonl→manifestの順で公開する。`receive` は完全性・版・依存・重複を検査し、適用または保留・隔離する。

**Peerはそのまま再利用可能。自動テストをそのまま実行してもOneDrive実機検証にはならない。**
`test_transport.py` は一時領域にA/Bを作り、`shutil.copyfile` で転送を模擬する9テスト。従来の実行方法はリポジトリルートで `python3 -B scripts/sync_validation/test_transport.py`。今回は実行していない。

実機では手動で送受信する。Peerのrootは必ずWSL内の新規専用領域に置く。OneDriveをrootにするとSQLiteまで同期対象になるため指定しない。自動監視・再試行CLIは追加せず、以下のPython対話操作で既存部品を利用する。
`sent=1` はPeerのローカルoutgoingへの公開のみで、共有フォルダーへの書出しやクラウド到達の証拠ではない。ファイルI/O例外は網羅的に処理されないため、例外時は記録して停止し、成功扱いしない。

## 実行前の確認事項

次回、実機検証の実行許可を得てから進める。今回は以下のコマンドも実行しない。

1. 対象SharePointサイト・ライブラリ・ショートカットの対応、テスト用フォルダーへの書込み権限、組織の運用ルールを確認する。
2. Windows/WSL/Python/SQLite/OneDriveの版、同期方式、Files On-Demand設定、空き容量、時計・タイムゾーンを記録する。
3. OneDriveの既存同期エラーがないことを確認する。同期停止やネット切断は他の業務にも影響するため、実施可能な時間と復旧手段を確認する。
4. 新規runフォルダーだけを操作対象にする。既存ファイルは上書き・移動・削除しない。サンプルは合成文字列のみ。
5. 受信ダウンロード先・ログ・DBはWSL内。ブラウザーの自動ダウンロード先が同期先でないことを確認する。
6. 観測上限を事前に決める（例: 各段階10分、3試行）。これは性能要件ではない。未到達ならタイムアウトとして証拠を保存する。

## 初期準備（次回のみ）

環境変数 `ONEDRIVE_SYNC_ROOT` に検証専用同期フォルダーのWSL絶対パスを、`VALIDATION_WORK_PARENT` に同期対象外のWSL内作業領域の絶対パスを設定する。前者を本書では `<ONEDRIVE_SYNC_ROOT>`、生成される専用作業ディレクトリを `<VALIDATION_WORK_DIR>` と表記する。両方が既存ディレクトリであることを確認し、会社名・ユーザー名・社内階層を含む実値は公開しない。

リポジトリルートで `python3 -B` を起動し、以下を対話入力する。同一セッションを使う。

```python
import os, sys, tempfile, shutil, hashlib, time
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
sys.path.insert(0, str(Path("scripts/sync_validation").resolve()))
from transport import Peer
local = Path(tempfile.mkdtemp(prefix="cim-onedrive-", dir=os.environ["VALIDATION_WORK_PARENT"]))
shared = Path(os.environ["ONEDRIVE_SYNC_ROOT"])
run = shared / ("run-" + str(uuid4()))
run.mkdir(exist_ok=False)
(run / "outbound").mkdir()
(run / "inbound").mkdir()
a = Peer(local / "a", "A")
b = Peer(local / "b", "B-synthetic")
print(local, run)

def stamp(label):
    print(label, datetime.now(timezone.utc).isoformat(), time.perf_counter())

def export_new(source, destination):
    # 既存名を上書きしない。途中で失敗した場合は停止し、別runで再試験する。
    with source.open("rb") as src, destination.open("xb") as dst:
        shutil.copyfileobj(src, dst)

def state(peer):
    for table in ("records", "outbox", "applied", "effects"):
        print(table, peer.db.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall())
```

共有領域に出すのはjsonlとmanifestのみ。DB・part・quarantineは出さない。この手動コピー方式はローカルpublishのrenameをOneDriveがどう転送するかを検証する方式ではない。その部分は2台構成で別途検証する。

## 1台で行う手順

### A. 公開・クラウド到達と遅延

```python
stamp("save-start")
eid = a.change("sample", "one")
stamp("local-saved")
a.publish()
stamp("local-published")
for suffix in (".jsonl", ".manifest"):
    name = eid + suffix
    export_new(a.root / "outgoing" / name, run / "outbound" / name)
    stamp("shared-written-" + suffix)
state(a)
```

1. SharePointブラウザーでrun/outboundを再読込みし、両ファイルを初めて確認できたUTC時刻を記録する。OneDrive状態表示も別に記録する。
2. ブラウザーから両方を同期先以外へダウンロードし、WSLの `local / "b" / "incoming"` に同名で配置する。既存名があれば停止する。
3. 次を実施する。

```python
m = b.root / "incoming" / (eid + ".manifest")
stamp("web-download-ready")
print(b.receive(m))  # applied
stamp("applied")
state(b)  # records=sample/one、applied/effects各1件
print(b.receive(m))  # duplicate
state(b)  # records/applied/effectsが不変
```

SharePointから取得した実体とローカルoutgoing実体のSHA-256も比較する。3回試行するなら新規entity_idを使い、各イベントを別々に記録する。
共有書出し→Web初回確認はポーリング間隔・操作時間を含む観測遅延。Webダウンロードまで含む往復は純粋なOneDrive遅延ではない。ローカルmtimeやsentからアップロード完了時刻を推定しない。

### B. SharePointからOneDriveへ受信

1. `rid = b.change("reverse", "from-web")`、`b.publish()` で別の合成イベントをローカル生成する。
2. ブラウザーでBのoutgoingからridのjsonl/manifestだけをrun/inboundへアップロードし、各操作時刻を記録する。WSLからinboundにコピーするとダウンロード経路を試せない。
3. WindowsとWSLで対象2ファイルの到着・状態を観測する。本文読取りが取得を誘発する可能性を区別して記録する。
4. 両方が利用可能になったら `a.receive(run / "inbound" / (rid + ".manifest"))` を実行する。applied、reverseの値、applied/effects各1件を確認する。再読込はduplicateで不変。
5. 欠落・不完全なら状態を記録して、到着後に同じreceiveを手動再試行する。I/O例外は別記する。自動復旧したと記載しない。

### C. OneDrive停止・通信断・復旧（T08の一部）

同期の一時停止と実回線切断は別試験として新規runで行う。

1. 正常な基準試行を済ませ、停止／切断時刻とOneDriveの状態を記録する。
2. Aで同じ新規entity_idに5回changeし、各ID・順序とOutbox未送信5件を記録する。a.close後、同じroot/device_idで再度Peerを開き、5件残存を確認する。
3. publishし、新規ファイルだけoutboundへexportする。ローカルsent=1でもクラウド到達とは扱わない。
4. 回線切断中は同PCブラウザーでSharePointを確認できないため「クラウド未到達確認済み」としない。一時停止でもWeb観測とローカル状態を区別する。
5. 元の回線・同期状態に戻し、時刻を記録する。Webで5組を確認してダウンロードし、Bのincomingへ置く。
6. 5manifestを繰り返しreceiveし、必要な依存待ちを再試行する。最終値、applied/effects各5件、A/Bのrecords一致、再読込で不変を確認する。他の試行とDBを共有しない。

復旧しても到達しない、値が失われる、重複副作用が発生する場合は停止してNo-Go事象として記録する。既存ファイルの削除や同期設定のリセットは行わない。

### D. Files On-Demand（T18の一部）

1. run内だけにブラウザーから新規合成サンプルをアップロードし、サイズ・SHA-256を同期外に控える。
2. Windows Explorerで初期状態と「ディスク上のサイズ」を記録する。オンラインのみでない場合、その条件での試験は未実施とする。
3. オンラインのみの状態で、WSLの属性確認・列挙前後のアイコンを記録する。その後、本文を読みSHA-256を比較し、所要時間・取得状態・例外を記録する。
4. このrunのアップロード完了確認済みサンプルだけをExplorerの「空き領域を増やす」で解放する。削除操作は使わない。クラウド原本が残ることを確認する。
5. オンラインのみで回線を切断し本文読取りを試し、成功／失敗／待機を記録する。端末全体の停止を避けるため、事前に中止時間と手動中断方法を決める。
6. 回線復旧後に再取得・ハッシュ一致を確認する。同サンプルを「このデバイス上で常に保持する」にし、取得完了後、オフラインで読取り・ハッシュ一致を確認する。

設定変更は対象サンプルだけ。取得・解放の自動制御、プロジェクト別キャッシュ、大量ファイル負荷はこの少数試行では未検証。

## 範囲と未検証項目

|対象|1台で可能な範囲|残る未検証|
|---|---|---|
|T01|Web往復による公開・完全性・受信|独立PC-Bへの到達・検出遅延、真の端末間双方向転送|
|T05|同一受信の再試行・Peer再起動|2台のクライアントによる再配送・競合コピー|
|T06/T07|既存ローカル試験で部分入力・逆順を制御可能|2台間の実際の到着順・部分可視性・rename伝播。自然発生しなければ観測なし|
|T08|1クライアントの停止・切断・復旧とWeb確認|相手PCが稼働する状態での収束|
|T09|既存プロセス中断試験を別途再実行可能|Windows/OS強制停止・電源断。今回は手順対象外|
|T10|既存ローカル不正入力試験を別途再実行可能|OneDriveロック・権限・容量不足。共有原本の破壊試験はしない|
|T18|少数専用サンプルの手動取得・解放|2台差、負荷、自動制御|
|T02〜04、T11〜17|今回対象外|業務競合・添付・スナップショット・復元等。Peerに必要機能なし|

2台目が必要なT01とT05〜T10の端末間実機部分はすべて未検証。1台の合成A/BとWeb往復を2台試験の合格に置き換えない。Phase 1合格・CIM導入承認の判断は行わない。

## 記録・終了

各試行にrun ID、シナリオ、環境、開始／終了UTC、単調時計、イベントID、ファイルサイズ・SHA-256、公開／Web確認／ローカル検出／適用時刻、DB件数、保留・重複・例外・再試行数、期待値／実測／判定を残す。ブラウザー観測間隔と手動操作時間も残す。観測不能は未観測とする。

終了時はa.close()/b.close()し、回線と同期状態を復旧確認する。ローカルログ・専用DB・共有サンプルは証拠として保持し、自動清掃しない。後日の削除は別途範囲を確認する。

今回の確認はディレクトリ読取りとコード静的確認のみ。実機試験・ローカル9テスト・CIMのUnit/Service/Repository/APIテストは実行していない。コード変更はなく、実機試験は今回の許可範囲外のためである。
