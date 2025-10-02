# YouTube AI Podcast

AIを使用してYouTubeポッドキャストを自動生成するシステムです。

毎日自動で海外の個人開発・AI関連ニュースを収集し、対談形式の動画を生成します。

## ✨ 機能

- 🔍 **自動情報収集**: Claude APIのweb_search機能で最新情報を収集
- 📝 **台本生成**: 対談形式（楽観派 vs 懐疑派）の自然な会話
- 🎤 **音声生成**: Google Cloud TTSで高品質な音声（並列処理で高速化）
- 💬 **字幕生成**: ElevenLabs STTで高精度な字幕（95%以上）
- 🎬 **動画生成**: MoviePyで1920x1080の高品質動画
- ☁️ **自動アップロード**: Google Driveへの自動アップロード
- 📊 **進捗管理**: Google Sheetsで全工程を管理
- 📢 **通知**: Slackで完了・エラー通知

## 📚 ドキュメント

### 📖 まず読むべきドキュメント

1. **[docs/README.md](docs/README.md)** - ドキュメントの読み方ガイド
2. **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - 一目でわかる実装リファレンス
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - システム全体のアーキテクチャ

### 🔧 実装者向け

- **[docs/STEPS_REFERENCE.md](docs/STEPS_REFERENCE.md)** - 各ステップの詳細実装ガイド
- **[docs/MODULE_DEPENDENCIES.md](docs/MODULE_DEPENDENCIES.md)** - モジュール依存関係マップ
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - ステップ4-12の実装コード

## 🚀 クイックスタート

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env` ファイルを作成して以下を設定：

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxx...

# Google APIs
GOOGLE_SHEETS_ID=xxx...
GOOGLE_CREDENTIALS_PATH=assets/credentials/google-credentials.json
GOOGLE_DRIVE_FOLDER_ID=xxx...

# ElevenLabs
ELEVENLABS_API_KEY=xxx...

# Slack
SLACK_BOT_TOKEN=xoxb-xxx...
SLACK_CHANNEL=#your-channel
```

### 3. 認証情報・静的ファイルの準備

```bash
# Google認証情報を配置
assets/credentials/google-credentials.json

# 背景画像を配置（1920x1080推奨）
assets/background.png

# 日本語フォントを配置
assets/fonts/NotoSansJP-Regular.ttf
```

### 4. 実行

```bash
python main.py
```

## 📋 実装状況

### ✅ 実装済み（main.py）

- ✅ ステップ1: 初期化
- ✅ ステップ2: Google Sheets新規行作成
- ✅ ステップ3: Claude APIで情報収集

### 📝 要実装（IMPLEMENTATION_GUIDE.md参照）

- 📝 ステップ4: Claude APIで台本生成
- 📝 ステップ5: 音声生成（並列処理）
- 📝 ステップ6: 字幕データ生成
- 📝 ステップ7: 動画生成
- 📝 ステップ8: メタデータ生成
- 📝 ステップ9: サムネイル生成
- 📝 ステップ10: Google Driveアップロード
- 📝 ステップ11: Google Sheets結果記録
- 📝 ステップ12: 完了通知

## 🎯 処理時間目標

- 情報収集: 2-3分
- 台本生成: 2-3分
- 音声生成: 5-10分（並列処理）
- 動画生成: 3-5分
- その他: 2-3分
- **合計: 15-25分**

## 📁 プロジェクト構造

```
youtube-ai/
├── main.py                     # メインエントリーポイント
├── config/                     # 設定ファイル
│   ├── settings.py
│   └── prompts.yaml
├── modules/                    # コアモジュール
│   ├── sheets_manager.py
│   ├── claude_client.py
│   ├── audio_generator.py
│   ├── video_generator.py
│   ├── metadata_generator.py
│   ├── storage_manager.py
│   └── notifier.py
├── utils/                      # ユーティリティ
│   ├── logger.py
│   ├── error_handler.py
│   └── timer.py
├── docs/                       # 📚 詳細ドキュメント
│   ├── README.md
│   ├── QUICK_REFERENCE.md
│   ├── ARCHITECTURE.md
│   ├── STEPS_REFERENCE.md
│   └── MODULE_DEPENDENCIES.md
├── assets/                     # 静的ファイル
├── temp/                       # 一時ファイル
├── logs/                       # ログファイル
└── tests/                      # テストコード
```

## 🔗 外部サービス

- **Claude API**: 情報収集・台本生成
- **Google Cloud TTS**: 音声生成
- **ElevenLabs**: STT（字幕用）
- **Google Sheets**: データ管理
- **Google Drive**: ファイル保存
- **Slack**: 通知

## 📖 参考

- [元記事（Zenn）](https://zenn.dev/xtm_blog/articles/da1eba90525f91) - 3ヶ月で登録者1,000人達成の実績
