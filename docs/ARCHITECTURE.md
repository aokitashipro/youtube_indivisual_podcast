# YouTube AI Podcast アーキテクチャドキュメント

## 📁 プロジェクト構造概要

```
youtube-ai/
├── main.py                     # メインエントリーポイント
├── config/                     # 設定ファイル
│   ├── settings.py            # アプリケーション設定
│   └── prompts.yaml           # プロンプトテンプレート
├── modules/                    # コアモジュール
│   ├── sheets_manager.py      # Google Sheets操作
│   ├── claude_client.py       # Claude API呼び出し
│   ├── audio_generator.py     # 音声生成
│   ├── video_generator.py     # 動画生成
│   ├── metadata_generator.py  # メタデータ生成
│   ├── storage_manager.py     # Google Drive操作
│   └── notifier.py            # Slack通知
├── utils/                      # ユーティリティ
│   ├── logger.py              # ロギング
│   ├── error_handler.py       # エラーハンドリング
│   └── timer.py               # 処理時間計測
├── assets/                     # 静的ファイル
├── temp/                       # 一時ファイル
├── logs/                       # ログファイル
└── tests/                      # テストコード
```

## 🔄 データフロー図

```
[開始]
  ↓
[ステップ1: 初期化]
  ├→ config/settings.py (設定読み込み)
  ├→ utils/logger.py (ロガー初期化)
  ├→ utils/error_handler.py (エラーハンドラー初期化)
  └→ modules/notifier.py (通知送信)
  ↓
[ステップ2: Google Sheets新規行作成]
  ├→ modules/sheets_manager.py (新規行作成)
  └→ Google Sheets API
  ↓
[ステップ3: 情報収集]
  ├→ modules/claude_client.py (Web検索)
  ├→ config/prompts.yaml (プロンプト取得)
  └→ Claude API (web_search使用)
  ↓
[ステップ4: 台本生成]
  ├→ modules/claude_client.py (台本生成)
  ├→ config/prompts.yaml (プロンプト取得)
  └→ Claude API
  ↓
[ステップ5: 音声生成]
  ├→ modules/audio_generator.py (並列音声生成)
  └→ Google Cloud TTS / ElevenLabs API
  ↓
[ステップ6: 字幕生成]
  ├→ modules/audio_generator.py (STT + マッチング)
  └→ ElevenLabs STT API
  ↓
[ステップ7: 動画生成]
  ├→ modules/video_generator.py (MoviePy)
  ├→ assets/background.png (背景画像)
  └→ assets/fonts/ (フォント)
  ↓
[ステップ8: メタデータ生成]
  └→ modules/metadata_generator.py
  ↓
[ステップ9: サムネイル生成]
  ├→ modules/video_generator.py
  └→ Pillow (画像処理)
  ↓
[ステップ10: Google Driveアップロード]
  ├→ modules/storage_manager.py
  └→ Google Drive API
  ↓
[ステップ11: 結果記録]
  ├→ modules/sheets_manager.py
  └→ Google Sheets API
  ↓
[ステップ12: 完了通知]
  ├→ modules/notifier.py
  └→ Slack API
  ↓
[完了]
```

## 📊 モジュール間依存関係

### main.py
```
依存モジュール:
├── config/settings.py          (必須)
├── modules/sheets_manager.py   (必須)
├── modules/claude_client.py    (必須)
├── modules/audio_generator.py  (必須)
├── modules/video_generator.py  (必須)
├── modules/metadata_generator.py (必須)
├── modules/storage_manager.py  (必須)
├── modules/notifier.py         (必須)
├── utils/logger.py             (必須)
├── utils/error_handler.py      (必須)
└── utils/timer.py              (必須)
```

### modules/sheets_manager.py
```
依存:
├── config/settings.py          (設定取得)
├── gspread                     (Google Sheets API)
├── google.oauth2               (認証)
└── assets/credentials/google-credentials.json (認証情報)

提供メソッド:
├── get_podcast_data()          # データ取得
├── create_new_row(data)        # 新規行作成
├── update_row(row_id, data)    # 行更新
└── get_specific_data(sheet, range) # 特定データ取得
```

### modules/claude_client.py
```
依存:
├── config/settings.py          (API Key取得)
├── config/prompts.yaml         (プロンプト取得)
└── anthropic                   (Claude API)

提供メソッド:
├── collect_topics_with_web_search() # 情報収集 (web_search使用)
├── generate_dialogue_script(topics) # 台本生成
├── generate_content(data)           # コンテンツ生成
└── generate_metadata(content)       # メタデータ生成
```

### modules/audio_generator.py
```
依存:
├── config/settings.py          (設定取得)
├── google.cloud.texttospeech   (Google TTS)
├── elevenlabs                  (ElevenLabs)
└── pydub                       (音声処理)

提供メソッド:
├── generate_audio(content)              # 音声生成
├── generate_audio_parallel(script)      # 並列音声生成
├── generate_subtitles(audio, script)    # 字幕生成 (STT)
├── get_audio_duration(path)             # 音声長取得
└── generate_audio_with_effects(content) # エフェクト付き音声
```

### modules/video_generator.py
```
依存:
├── config/settings.py          (設定取得)
├── moviepy                     (動画生成)
├── Pillow                      (画像処理)
├── assets/background.png       (背景画像)
└── assets/fonts/               (フォント)

提供メソッド:
├── generate_video(audio, content)              # 動画生成
├── generate_video_with_subtitles(audio, subs)  # 字幕付き動画
├── generate_thumbnail(metadata)                # サムネイル生成
└── generate_video_with_effects(video, effects) # エフェクト付き動画
```

### modules/metadata_generator.py
```
依存:
├── config/settings.py          (設定取得)
└── (標準ライブラリのみ)

提供メソッド:
├── generate_metadata(script, topics)  # メタデータ生成
├── _generate_title(content)           # タイトル生成
├── _generate_description(content)     # 説明文生成
├── _generate_tags(content)            # タグ生成
└── _generate_category(content)        # カテゴリ生成
```

### modules/storage_manager.py
```
依存:
├── config/settings.py          (設定取得)
├── google.oauth2               (認証)
├── googleapiclient             (Google Drive API)
└── assets/credentials/google-credentials.json (認証情報)

提供メソッド:
├── upload_video(path, metadata)    # 動画アップロード
├── upload_audio(path, metadata)    # 音声アップロード
├── upload_file(path, type, meta)   # ファイルアップロード
├── create_folder(name, parent)     # フォルダ作成
└── list_files(folder_id)           # ファイル一覧
```

### modules/notifier.py
```
依存:
├── config/settings.py          (設定取得)
└── slack_sdk                   (Slack API)

提供メソッド:
├── send_completion_notification(url, meta)  # 完了通知
├── send_error_notification(error)           # エラー通知
├── send_progress_notification(step, prog)   # 進捗通知
└── send_custom_notification(message)        # カスタム通知
```

### utils/logger.py
```
依存:
└── (標準ライブラリのみ)

提供:
├── setup_logger(level, log_file)  # ロガー設定
├── get_logger(name)               # ロガー取得
├── LoggerMixin                    # ロガーミックスイン
├── log_function_call              # デコレーター
└── log_async_function_call        # 非同期デコレーター
```

### utils/error_handler.py
```
依存:
└── (標準ライブラリのみ)

提供:
├── ErrorHandler                   # エラーハンドラークラス
│   ├── handle_error(error, context)
│   ├── handle_validation_error(error)
│   ├── handle_api_error(error, api_name)
│   └── get_error_summary()
└── RetryHandler                   # リトライハンドラークラス
    ├── retry_async(func, *args)
    └── retry_sync(func, *args)
```

### utils/timer.py
```
依存:
└── (標準ライブラリのみ)

提供:
├── Timer                          # タイマークラス
│   ├── start()
│   ├── stop()
│   └── get_duration()
├── timer_context                  # コンテキストマネージャー
├── async_timer_context            # 非同期コンテキスト
└── PerformanceMonitor             # パフォーマンス監視
```

## 🔑 外部API・サービス依存

### 必須サービス
1. **Claude API (Anthropic)**
   - 用途: 情報収集（web_search）、台本生成
   - 認証: ANTHROPIC_API_KEY
   - 使用箇所: modules/claude_client.py

2. **Google Cloud Text-to-Speech**
   - 用途: 音声生成（ポッドキャスト風音声）
   - 認証: google-credentials.json
   - 使用箇所: modules/audio_generator.py

3. **ElevenLabs API**
   - 用途: STT（字幕生成）
   - 認証: ELEVENLABS_API_KEY
   - 使用箇所: modules/audio_generator.py

4. **Google Sheets API**
   - 用途: データ管理、結果記録
   - 認証: google-credentials.json
   - 使用箇所: modules/sheets_manager.py

5. **Google Drive API**
   - 用途: ファイルアップロード
   - 認証: google-credentials.json
   - 使用箇所: modules/storage_manager.py

6. **Slack API**
   - 用途: 通知送信
   - 認証: SLACK_BOT_TOKEN
   - 使用箇所: modules/notifier.py

## 📝 設定ファイル

### config/settings.py
```python
必須環境変数:
├── ANTHROPIC_API_KEY          # Claude API
├── GOOGLE_SHEETS_ID           # Google Sheets ID
├── GOOGLE_CREDENTIALS_PATH    # Google認証情報パス
├── ELEVENLABS_API_KEY         # ElevenLabs API
├── SLACK_BOT_TOKEN            # Slack Bot Token
├── SLACK_CHANNEL              # Slack Channel
└── GOOGLE_DRIVE_FOLDER_ID     # Google Drive Folder ID

オプション設定:
├── DEBUG                      # デバッグモード
├── LOG_LEVEL                  # ログレベル
├── TEMP_DIR                   # 一時ディレクトリ
├── OUTPUT_DIR                 # 出力ディレクトリ
├── VIDEO_WIDTH                # 動画幅
├── VIDEO_HEIGHT               # 動画高さ
└── VIDEO_FPS                  # 動画FPS
```

### config/prompts.yaml
```yaml
プロンプトテンプレート:
├── main_content_prompt         # メインコンテンツ生成
├── metadata_prompt             # メタデータ生成
├── audio_prompt                # 音声生成
├── video_prompt                # 動画生成
└── error_handling_prompt       # エラーハンドリング
```

## 🎨 静的ファイル

### assets/
```
必須ファイル:
├── background.png                      # 背景画像 (1920x1080)
├── fonts/NotoSansJP-Regular.ttf       # 日本語フォント
└── credentials/google-credentials.json # Google認証情報

推奨サイズ:
├── background.png: 1920x1080px, PNG/JPG
└── fonts: TTF/OTF形式、日本語対応
```

## 🔒 認証情報の管理

### Google認証情報 (google-credentials.json)
```
場所: assets/credentials/google-credentials.json
用途:
├── Google Sheets API
├── Google Drive API
└── Google Cloud Text-to-Speech

取得方法:
1. Google Cloud Consoleでプロジェクト作成
2. 各APIを有効化
3. サービスアカウント作成
4. JSONキーをダウンロード
```

### 環境変数 (.env)
```
場所: プロジェクトルート/.env
内容:
├── ANTHROPIC_API_KEY=sk-ant-xxx...
├── ELEVENLABS_API_KEY=xxx...
├── SLACK_BOT_TOKEN=xoxb-xxx...
└── その他設定値
```

## 📌 重要な注意事項

1. **認証情報の保護**
   - `.gitignore`に認証情報ファイルが含まれていることを確認
   - 環境変数は`.env`ファイルで管理
   - 本番環境では環境変数を直接設定

2. **ファイルサイズ**
   - 動画ファイル: 大きくなる可能性あり（Google Drive容量に注意）
   - 一時ファイル: 定期的にクリーンアップ
   - ログファイル: ローテーション設定推奨

3. **API制限**
   - Claude API: リクエスト数制限あり（リトライロジック実装済み）
   - Google APIs: クォータ制限あり
   - ElevenLabs: 月間文字数制限あり

4. **処理時間**
   - 目標: 15-25分
   - 音声生成が最も時間がかかる（5-10分）
   - 並列処理で高速化

5. **エラーハンドリング**
   - 各ステップで個別にエラーハンドリング
   - リトライロジック実装
   - Slack通知 + Sheets記録

