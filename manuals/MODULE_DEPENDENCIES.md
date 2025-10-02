# モジュール依存関係マップ

このドキュメントは、各モジュールが依存するファイルと外部ライブラリを視覚的に示します。

---

## 📊 依存関係グラフ

```
main.py
  │
  ├─→ config/
  │     ├─→ settings.py
  │     │     └─→ .env (環境変数)
  │     └─→ prompts.yaml
  │
  ├─→ modules/
  │     ├─→ sheets_manager.py
  │     │     ├─→ config/settings.py
  │     │     ├─→ assets/credentials/google-credentials.json
  │     │     ├─→ [外部] gspread
  │     │     └─→ [外部] google.oauth2
  │     │
  │     ├─→ claude_client.py
  │     │     ├─→ config/settings.py
  │     │     ├─→ config/prompts.yaml
  │     │     └─→ [外部] anthropic
  │     │
  │     ├─→ audio_generator.py
  │     │     ├─→ config/settings.py
  │     │     ├─→ [外部] google.cloud.texttospeech
  │     │     ├─→ [外部] elevenlabs
  │     │     └─→ [外部] pydub
  │     │
  │     ├─→ video_generator.py
  │     │     ├─→ config/settings.py
  │     │     ├─→ assets/background.png
  │     │     ├─→ assets/fonts/NotoSansJP-Regular.ttf
  │     │     ├─→ [外部] moviepy
  │     │     └─→ [外部] Pillow
  │     │
  │     ├─→ metadata_generator.py
  │     │     └─→ config/settings.py
  │     │
  │     ├─→ storage_manager.py
  │     │     ├─→ config/settings.py
  │     │     ├─→ assets/credentials/google-credentials.json
  │     │     ├─→ [外部] google.oauth2
  │     │     └─→ [外部] googleapiclient
  │     │
  │     └─→ notifier.py
  │           ├─→ config/settings.py
  │           └─→ [外部] slack_sdk
  │
  └─→ utils/
        ├─→ logger.py
        ├─→ error_handler.py
        └─→ timer.py
```

---

## 📦 各モジュールの詳細依存関係

### 1️⃣ config/settings.py

#### 📥 入力（依存）
```
.env
├── ANTHROPIC_API_KEY
├── GOOGLE_SHEETS_ID
├── GOOGLE_CREDENTIALS_PATH
├── ELEVENLABS_API_KEY
├── SLACK_BOT_TOKEN
├── SLACK_CHANNEL
├── GOOGLE_DRIVE_FOLDER_ID
└── その他設定値
```

#### 📤 出力（提供）
```
Settings クラス
├── 全ての設定値をプロパティとして提供
└── Pydantic BaseSettingsを継承
```

#### 🔗 外部ライブラリ
- `pydantic` - 設定管理

---

### 2️⃣ modules/sheets_manager.py

#### 📥 入力（依存）
```
内部ファイル:
├── config/settings.py
│   ├── GOOGLE_SHEETS_ID
│   └── GOOGLE_CREDENTIALS_PATH
└── assets/credentials/google-credentials.json

外部API:
└── Google Sheets API
```

#### 📤 出力（提供）
```
SheetsManager クラス
├── get_podcast_data() -> Dict
├── create_new_row(data: Dict) -> str
├── update_row(row_id: str, data: Dict) -> None
└── get_specific_data(sheet: str, range: str) -> List
```

#### 🔗 外部ライブラリ
```
gspread==6.1.2
├── Google Sheets操作

oauth2client==4.1.3
├── Google OAuth2認証

google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.1
└── Google認証関連
```

#### ⚙️ 必要な設定
```bash
# Google Cloud Consoleで設定
1. Google Sheets API を有効化
2. サービスアカウント作成
3. JSONキーをダウンロード
4. assets/credentials/google-credentials.json に配置
```

---

### 3️⃣ modules/claude_client.py

#### 📥 入力（依存）
```
内部ファイル:
├── config/settings.py
│   └── ANTHROPIC_API_KEY
└── config/prompts.yaml
    ├── main_content_prompt
    ├── metadata_prompt
    └── その他プロンプト

外部API:
└── Claude API (Anthropic)
```

#### 📤 出力（提供）
```
ClaudeClient クラス
├── collect_topics_with_web_search() -> Dict
│   └── web_search機能を使用した情報収集
├── generate_dialogue_script(topics: Dict) -> Dict
│   └── 対談形式の台本生成
├── generate_content(data: Dict) -> Dict
│   └── コンテンツ生成
└── generate_metadata(content: Dict) -> Dict
    └── メタデータ生成
```

#### 🔗 外部ライブラリ
```
anthropic==0.34.0
└── Claude API クライアント

pyyaml==6.0.2
└── YAMLファイル読み込み
```

#### ⚙️ 必要な設定
```bash
# Anthropic Console で取得
ANTHROPIC_API_KEY=sk-ant-xxx...
```

---

### 4️⃣ modules/audio_generator.py

#### 📥 入力（依存）
```
内部ファイル:
├── config/settings.py
│   ├── GOOGLE_CREDENTIALS_PATH
│   ├── ELEVENLABS_API_KEY
│   ├── AUDIO_SAMPLE_RATE
│   ├── AUDIO_BITRATE
│   └── OUTPUT_DIR
└── assets/credentials/google-credentials.json

外部API:
├── Google Cloud Text-to-Speech
└── ElevenLabs API (STT用)
```

#### 📤 出力（提供）
```
AudioGenerator クラス
├── generate_audio(content: Dict) -> str
│   └── 基本的な音声生成
├── generate_audio_parallel(script: Dict) -> str
│   └── 並列処理で音声生成（高速）
├── generate_subtitles(audio: str, script: Dict) -> Dict
│   └── STT + マッチングで字幕生成
├── get_audio_duration(path: str) -> float
│   └── 音声ファイルの長さを取得
└── generate_audio_with_effects(content: Dict, effects: Dict) -> str
    └── エフェクト付き音声生成
```

#### 🔗 外部ライブラリ
```
google-cloud-texttospeech==2.16.3
└── Google TTS (ポッドキャスト風音声)

elevenlabs==1.5.0
└── ElevenLabs STT (字幕用)

pydub==0.25.1
└── 音声処理・結合
```

#### ⚙️ 必要な設定
```bash
# Google Cloud Console
1. Text-to-Speech API を有効化
2. サービスアカウント作成
3. JSONキーをダウンロード

# ElevenLabs
ELEVENLABS_API_KEY=xxx...
```

#### 🎤 音声設定
```
Aさん（楽観派）:
├── 声: ja-JP-Neural2-C
├── ピッチ: 0
└── スタイル: 明るく前向き

Bさん（懐疑派）:
├── 声: ja-JP-Neural2-D
├── ピッチ: -2
└── スタイル: 冷静で批判的
```

---

### 5️⃣ modules/video_generator.py

#### 📥 入力（依存）
```
内部ファイル:
├── config/settings.py
│   ├── VIDEO_WIDTH (1920)
│   ├── VIDEO_HEIGHT (1080)
│   ├── VIDEO_FPS (30)
│   ├── FONT_PATH
│   ├── BACKGROUND_IMAGE_PATH
│   └── OUTPUT_DIR
├── assets/background.png
│   └── 1920x1080の背景画像
└── assets/fonts/NotoSansJP-Regular.ttf
    └── 日本語フォント
```

#### 📤 出力（提供）
```
VideoGenerator クラス
├── generate_video(audio: str, content: Dict) -> str
│   └── 基本的な動画生成
├── generate_video_with_subtitles(audio: str, subs: Dict, script: Dict) -> str
│   └── 字幕付き動画生成
├── generate_thumbnail(metadata: Dict) -> str
│   └── サムネイル生成
└── generate_video_with_effects(video: str, effects: Dict) -> str
    └── エフェクト付き動画
```

#### 🔗 外部ライブラリ
```
moviepy==1.0.3
└── 動画生成・編集

Pillow==10.4.0
└── 画像処理
```

#### ⚙️ 動画設定
```
解像度: 1920x1080 (Full HD)
FPS: 30
字幕:
├── 位置: 下部中央（Y=900）
├── フォントサイズ: 40px
├── 色: 白
└── 背景: 黒（透過度70%）
```

---

### 6️⃣ modules/metadata_generator.py

#### 📥 入力（依存）
```
内部ファイル:
└── config/settings.py

入力データ:
├── script_content (台本)
└── topics_data (トピック情報)
```

#### 📤 出力（提供）
```
MetadataGenerator クラス
└── generate_metadata(script: Dict, topics: Dict) -> Dict
    ├── title: str (70文字以内)
    ├── description: str (5000文字以内)
    ├── tags: List[str] (15個以内)
    ├── category: str
    ├── thumbnail_suggestion: str
    ├── created_at: str
    ├── duration: int
    ├── language: str
    └── privacy_status: str
```

#### 🔗 外部ライブラリ
- なし（標準ライブラリのみ）

---

### 7️⃣ modules/storage_manager.py

#### 📥 入力（依存）
```
内部ファイル:
├── config/settings.py
│   ├── GOOGLE_CREDENTIALS_PATH
│   └── GOOGLE_DRIVE_FOLDER_ID
└── assets/credentials/google-credentials.json

外部API:
└── Google Drive API
```

#### 📤 出力（提供）
```
StorageManager クラス
├── upload_video(path: str, metadata: Dict) -> str
│   └── 動画をGoogle Driveにアップロード
├── upload_audio(path: str, metadata: Dict) -> str
│   └── 音声をGoogle Driveにアップロード
├── upload_file(path: str, type: str, metadata: Dict) -> str
│   └── 汎用ファイルアップロード
├── create_folder(name: str, parent: str) -> str
│   └── フォルダ作成
└── list_files(folder_id: str) -> List
    └── ファイル一覧取得
```

#### 🔗 外部ライブラリ
```
google-api-python-client==2.147.0
└── Google Drive API

google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.1
└── Google認証
```

#### ⚙️ 必要な設定
```bash
# Google Cloud Console
1. Google Drive API を有効化
2. サービスアカウント作成
3. JSONキーをダウンロード
4. Drive フォルダIDを取得

# .env
GOOGLE_DRIVE_FOLDER_ID=xxx...
```

---

### 8️⃣ modules/notifier.py

#### 📥 入力（依存）
```
内部ファイル:
└── config/settings.py
    ├── SLACK_BOT_TOKEN
    └── SLACK_CHANNEL

外部API:
└── Slack API
```

#### 📤 出力（提供）
```
Notifier クラス
├── send_completion_notification(url: str, metadata: Dict) -> None
│   └── 完了通知
├── send_error_notification(error: str) -> None
│   └── エラー通知
├── send_progress_notification(step: str, progress: int) -> None
│   └── 進捗通知
└── send_custom_notification(message: str, channel: str) -> None
    └── カスタム通知
```

#### 🔗 外部ライブラリ
```
slack-sdk==3.23.0
└── Slack API クライアント
```

#### ⚙️ 必要な設定
```bash
# Slack App作成
1. https://api.slack.com/apps でApp作成
2. Bot Token Scopes を設定
   - chat:write
   - chat:write.public
3. Bot User OAuth Token を取得
4. ワークスペースにインストール

# .env
SLACK_BOT_TOKEN=xoxb-xxx...
SLACK_CHANNEL=#your-channel
```

---

### 9️⃣ utils/logger.py

#### 📥 入力（依存）
- なし（標準ライブラリのみ）

#### 📤 出力（提供）
```
関数・クラス:
├── setup_logger(level: str, log_file: str) -> Logger
│   └── ロガーの初期化・設定
├── get_logger(name: str) -> Logger
│   └── ロガー取得
├── LoggerMixin
│   └── クラスにロガープロパティを追加
├── @log_function_call
│   └── 関数呼び出しログ（同期）
└── @log_async_function_call
    └── 関数呼び出しログ（非同期）
```

#### 📁 ログ出力先
```
logs/
└── podcast_YYYYMMDD.log
```

---

### 🔟 utils/error_handler.py

#### 📥 入力（依存）
- なし（標準ライブラリのみ）

#### 📤 出力（提供）
```
ErrorHandler クラス:
├── handle_error(error: Exception, context: Dict) -> Dict
│   └── 一般的なエラー処理
├── handle_validation_error(error: Exception, field: str) -> Dict
│   └── バリデーションエラー
├── handle_api_error(error: Exception, api_name: str) -> Dict
│   └── APIエラー
├── handle_file_error(error: Exception, file_path: str) -> Dict
│   └── ファイルエラー
└── get_error_summary() -> Dict
    └── エラーサマリー取得

RetryHandler クラス:
├── retry_async(func, *args, **kwargs)
│   └── 非同期関数のリトライ（指数バックオフ）
└── retry_sync(func, *args, **kwargs)
    └── 同期関数のリトライ（指数バックオフ）
```

#### ⚙️ リトライ設定
```
Claude API: 最大3回、2秒間隔
音声生成: 最大2回、1.5秒間隔
その他: 設定可能
```

---

### 1️⃣1️⃣ utils/timer.py

#### 📥 入力（依存）
- なし（標準ライブラリのみ）

#### 📤 出力（提供）
```
Timer クラス:
├── start() -> None
│   └── 計測開始
├── stop() -> None
│   └── 計測終了
├── get_duration() -> float
│   └── 処理時間取得（秒）
└── get_timings() -> List[Dict]
    └── 全計測履歴

コンテキストマネージャー:
├── timer_context(name: str, logger: Logger)
│   └── 同期版
└── async_timer_context(name: str, logger: Logger)
    └── 非同期版

デコレーター:
├── @time_function
│   └── 関数計測（同期）
└── @time_async_function
    └── 関数計測（非同期）

PerformanceMonitor クラス:
├── create_timer(name: str) -> Timer
├── record_performance(name: str, duration: float, metadata: Dict)
└── get_performance_summary() -> Dict
```

---

## 🔄 ステップごとの依存関係フロー

### ステップ1: 初期化
```
main.py
└─→ 全モジュール初期化
    ├─→ config/settings.py (.env読み込み)
    ├─→ utils/logger.py (ロガー初期化)
    ├─→ utils/error_handler.py (エラーハンドラー初期化)
    ├─→ utils/timer.py (タイマー初期化)
    └─→ modules/notifier.py (開始通知)
```

### ステップ2: Sheets新規行作成
```
main.py
└─→ modules/sheets_manager.py
    ├─→ config/settings.py (GOOGLE_SHEETS_ID)
    ├─→ assets/credentials/google-credentials.json
    └─→ Google Sheets API
```

### ステップ3: 情報収集
```
main.py
└─→ modules/claude_client.py
    ├─→ config/settings.py (ANTHROPIC_API_KEY)
    ├─→ config/prompts.yaml
    └─→ Claude API (web_search機能)
```

### ステップ4: 台本生成
```
main.py
└─→ modules/claude_client.py
    ├─→ config/settings.py (ANTHROPIC_API_KEY)
    ├─→ config/prompts.yaml
    ├─→ ステップ3の結果 (topics_data)
    └─→ Claude API
```

### ステップ5: 音声生成
```
main.py
└─→ modules/audio_generator.py
    ├─→ config/settings.py
    ├─→ assets/credentials/google-credentials.json
    ├─→ ステップ4の結果 (script_content)
    └─→ Google Cloud TTS (並列処理)
```

### ステップ6: 字幕生成
```
main.py
└─→ modules/audio_generator.py
    ├─→ config/settings.py (ELEVENLABS_API_KEY)
    ├─→ ステップ5の結果 (audio_path)
    ├─→ ステップ4の結果 (script_content)
    └─→ ElevenLabs STT API
```

### ステップ7: 動画生成
```
main.py
└─→ modules/video_generator.py
    ├─→ config/settings.py
    ├─→ assets/background.png
    ├─→ assets/fonts/NotoSansJP-Regular.ttf
    ├─→ ステップ5の結果 (audio_path)
    ├─→ ステップ6の結果 (subtitle_data)
    └─→ MoviePy
```

### ステップ8: メタデータ生成
```
main.py
└─→ modules/metadata_generator.py
    ├─→ ステップ4の結果 (script_content)
    └─→ ステップ3の結果 (topics_data)
```

### ステップ9: サムネイル生成
```
main.py
└─→ modules/video_generator.py
    ├─→ config/settings.py
    ├─→ ステップ8の結果 (metadata)
    └─→ Pillow
```

### ステップ10: Driveアップロード
```
main.py
└─→ modules/storage_manager.py
    ├─→ config/settings.py (GOOGLE_DRIVE_FOLDER_ID)
    ├─→ assets/credentials/google-credentials.json
    ├─→ ステップ7の結果 (video_path)
    ├─→ ステップ5の結果 (audio_path)
    ├─→ ステップ9の結果 (thumbnail_path)
    └─→ Google Drive API
```

### ステップ11: 結果記録
```
main.py
└─→ modules/sheets_manager.py
    ├─→ config/settings.py (GOOGLE_SHEETS_ID)
    ├─→ assets/credentials/google-credentials.json
    ├─→ 全ステップの結果
    └─→ Google Sheets API
```

### ステップ12: 完了通知
```
main.py
└─→ modules/notifier.py
    ├─→ config/settings.py (SLACK_BOT_TOKEN, SLACK_CHANNEL)
    ├─→ 全ステップの結果
    └─→ Slack API
```

---

## 📌 チェックリスト

### 🔧 設定ファイル
- [ ] `.env` ファイル作成
- [ ] `config/settings.py` の環境変数設定
- [ ] `config/prompts.yaml` のプロンプト確認

### 🔑 認証情報
- [ ] `assets/credentials/google-credentials.json` 配置
- [ ] Google Sheets API 有効化
- [ ] Google Drive API 有効化
- [ ] Google Cloud TTS API 有効化
- [ ] Claude API キー取得
- [ ] ElevenLabs API キー取得
- [ ] Slack Bot Token 取得

### 🎨 静的ファイル
- [ ] `assets/background.png` (1920x1080)
- [ ] `assets/fonts/NotoSansJP-Regular.ttf`

### 📦 外部ライブラリ
- [ ] `pip install -r requirements.txt`
- [ ] 全ての依存関係がインストール済み

### 🧪 動作確認
- [ ] 各モジュールが正常にインポート可能
- [ ] Google APIs接続テスト
- [ ] Claude API接続テスト
- [ ] Slack通知テスト

