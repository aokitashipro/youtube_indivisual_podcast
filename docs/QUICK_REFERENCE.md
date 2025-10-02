# クイックリファレンス - 一目でわかる実装ガイド

各ステップで「どのファイルを見ればいいか」を一覧化した早見表です。

---

## 🎯 実装済みステップ（1-3）

### ✅ ステップ1: 初期化

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py:116-136` |
| **メソッド** | `PodcastPipeline.step_01_initialize()` |
| **参照ファイル** | ✅ `config/settings.py`<br>✅ `utils/logger.py`<br>✅ `utils/error_handler.py`<br>✅ `utils/timer.py`<br>✅ `modules/notifier.py` |
| **外部API** | Slack API（通知用） |
| **実装状態** | ✅ **完了** |

---

### ✅ ステップ2: Google Sheets新規行作成

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py:138-159` |
| **メソッド** | `PodcastPipeline.step_02_create_sheet_row()` |
| **参照ファイル** | ✅ `modules/sheets_manager.py`<br>📝 要追加: `create_new_row()` メソッド<br>✅ `config/settings.py`<br>✅ `assets/credentials/google-credentials.json` |
| **外部API** | Google Sheets API |
| **必要な環境変数** | `GOOGLE_SHEETS_ID`<br>`GOOGLE_CREDENTIALS_PATH` |
| **実装状態** | ✅ main.py完了<br>📝 sheets_manager.pyに`create_new_row()`追加必要 |

**追加が必要なコード:**
```python
# modules/sheets_manager.py に追加
async def create_new_row(self, row_data: Dict[str, Any]) -> str:
    """新規行を作成"""
    spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEETS_ID)
    worksheet = spreadsheet.sheet1
    row_values = list(row_data.values())
    worksheet.append_row(row_values)
    row_id = len(worksheet.get_all_values())
    return str(row_id)
```

---

### ✅ ステップ3: Claude APIで情報収集

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py:161-186` |
| **メソッド** | `PodcastPipeline.step_03_collect_information()` |
| **参照ファイル** | ✅ `modules/claude_client.py`<br>📝 要追加: `collect_topics_with_web_search()` メソッド<br>✅ `config/settings.py`<br>✅ `config/prompts.yaml` |
| **外部API** | Claude API（web_search機能） |
| **必要な環境変数** | `ANTHROPIC_API_KEY` |
| **目標処理時間** | 2-3分 |
| **実装状態** | ✅ main.py完了<br>📝 claude_client.pyに`collect_topics_with_web_search()`追加必要 |

**追加が必要なコード:**
```python
# modules/claude_client.py に追加
async def collect_topics_with_web_search(self) -> Dict[str, Any]:
    """Web検索で情報収集（Indie Hackers, Product Hunt, Hacker News）"""
    prompt = """最新の個人開発・AI関連トピックを3-5件収集..."""
    response = self.client.messages.create(
        model="claude-3-sonnet-20240229",
        tools=[{"type": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )
    return self._parse_topics_response(response)
```

---

## 📝 未実装ステップ（4-12）

### ステップ4: Claude APIで台本生成

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_04_generate_script()` |
| **参照ファイル** | 📝 `modules/claude_client.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 要追加: `generate_dialogue_script(topics_data)` |
| **入力データ** | `self.results["topics_data"]` |
| **出力データ** | `self.results["script_content"]` |
| **目標処理時間** | 2-3分 |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ5: 音声生成（並列処理）

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_05_generate_audio()` |
| **参照ファイル** | 📝 `modules/audio_generator.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 要追加: `generate_audio_parallel(script_content)` |
| **入力データ** | `self.results["script_content"]` |
| **出力データ** | `self.results["audio_path"]` |
| **外部API** | Google Cloud Text-to-Speech |
| **音声設定** | Aさん: ja-JP-Neural2-C (ピッチ0)<br>Bさん: ja-JP-Neural2-D (ピッチ-2) |
| **目標処理時間** | 5-10分 |
| **リトライ** | 最大2回 |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ6: 字幕データ生成

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_06_generate_subtitles()` |
| **参照ファイル** | 📝 `modules/audio_generator.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 要追加: `generate_subtitles(audio_path, script_content)` |
| **入力データ** | `self.results["audio_path"]`<br>`self.results["script_content"]` |
| **出力データ** | `self.results["subtitle_data"]` |
| **外部API** | ElevenLabs STT |
| **目標精度** | 95%以上 |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ7: 動画生成

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_07_generate_video()` |
| **参照ファイル** | 📝 `modules/video_generator.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 要追加: `generate_video_with_subtitles(audio, subs, script)`<br>✅ `assets/background.png`<br>✅ `assets/fonts/NotoSansJP-Regular.ttf` |
| **入力データ** | `self.results["audio_path"]`<br>`self.results["subtitle_data"]`<br>`self.results["script_content"]` |
| **出力データ** | `self.results["video_path"]` |
| **動画設定** | 1920x1080, 30fps |
| **目標処理時間** | 3-5分 |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ8: メタデータ生成

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_08_generate_metadata()` |
| **参照ファイル** | ✅ `modules/metadata_generator.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 既存メソッドを使用 |
| **入力データ** | `self.results["script_content"]`<br>`self.results["topics_data"]` |
| **出力データ** | `self.results["metadata"]` |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ9: サムネイル生成

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_09_generate_thumbnail()` |
| **参照ファイル** | 📝 `modules/video_generator.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 要追加: `generate_thumbnail(metadata)` |
| **入力データ** | `self.results["metadata"]` |
| **出力データ** | `self.results["thumbnail_path"]` |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ10: Google Driveアップロード

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_10_upload_to_drive()` |
| **参照ファイル** | ✅ `modules/storage_manager.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 既存メソッドを使用<br>✅ `assets/credentials/google-credentials.json` |
| **入力データ** | `self.results["video_path"]`<br>`self.results["audio_path"]`<br>`self.results["thumbnail_path"]`<br>`self.results["metadata"]` |
| **出力データ** | `self.results["drive_urls"]` |
| **外部API** | Google Drive API |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ11: 結果記録

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_11_record_results()` |
| **参照ファイル** | 📝 `modules/sheets_manager.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 要追加: `update_row(row_id, data)` |
| **入力データ** | 全ステップの結果 |
| **外部API** | Google Sheets API |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

### ステップ12: 完了通知

| 項目 | ファイル/場所 |
|-----|-------------|
| **実装場所** | `main.py` - **要追加** |
| **メソッド** | `PodcastPipeline.step_12_send_completion_notification()` |
| **参照ファイル** | ✅ `modules/notifier.py`<br>&nbsp;&nbsp;&nbsp;&nbsp;└ 既存メソッドを使用 |
| **入力データ** | 全ステップの結果 |
| **外部API** | Slack API |
| **詳細** | → `IMPLEMENTATION_GUIDE.md` 参照 |

---

## 📋 実装チェックリスト

### main.py の更新

```python
# run() メソッドの201行目付近を更新
async def run(self) -> Dict[str, Any]:
    # ...
    try:
        await self.step_01_initialize()
        await self.step_02_create_sheet_row()
        await self.step_03_collect_information()
        # ↓ 以下を追加
        await self.step_04_generate_script()
        await self.step_05_generate_audio()
        await self.step_06_generate_subtitles()
        await self.step_07_generate_video()
        await self.step_08_generate_metadata()
        await self.step_09_generate_thumbnail()
        await self.step_10_upload_to_drive()
        await self.step_11_record_results()
        await self.step_12_send_completion_notification()
```

### 各モジュールに追加が必要なメソッド

- [ ] `modules/sheets_manager.py`
  - [ ] `create_new_row(row_data)` - ステップ2
  - [ ] `update_row(row_id, data)` - ステップ11

- [ ] `modules/claude_client.py`
  - [ ] `collect_topics_with_web_search()` - ステップ3
  - [ ] `generate_dialogue_script(topics_data)` - ステップ4

- [ ] `modules/audio_generator.py`
  - [ ] `generate_audio_parallel(script_content)` - ステップ5
  - [ ] `generate_subtitles(audio_path, script_content)` - ステップ6

- [ ] `modules/video_generator.py`
  - [ ] `generate_video_with_subtitles(audio, subs, script)` - ステップ7
  - [ ] `generate_thumbnail(metadata)` - ステップ9

---

## 🔧 環境変数チェックリスト

`.env` ファイルに以下の環境変数が必要です：

- [ ] `ANTHROPIC_API_KEY` - Claude API（ステップ3, 4）
- [ ] `GOOGLE_SHEETS_ID` - Google Sheets（ステップ2, 11）
- [ ] `GOOGLE_CREDENTIALS_PATH` - Google認証（ステップ2, 5, 10, 11）
- [ ] `ELEVENLABS_API_KEY` - ElevenLabs STT（ステップ6）
- [ ] `SLACK_BOT_TOKEN` - Slack通知（ステップ1, 12）
- [ ] `SLACK_CHANNEL` - Slackチャンネル（ステップ1, 12）
- [ ] `GOOGLE_DRIVE_FOLDER_ID` - Google Drive（ステップ10）

---

## 📁 静的ファイルチェックリスト

以下のファイルが必要です：

- [ ] `assets/credentials/google-credentials.json` - Google認証情報
- [ ] `assets/background.png` - 背景画像（1920x1080）
- [ ] `assets/fonts/NotoSansJP-Regular.ttf` - 日本語フォント

---

## 🚀 実装の優先順位

### フェーズ1: 基本実装（ステップ4-7）
1. **ステップ4**: 台本生成 → Claude APIの基本的な使い方
2. **ステップ5**: 音声生成 → 並列処理の実装
3. **ステップ6**: 字幕生成 → STTとマッチング
4. **ステップ7**: 動画生成 → MoviePyの使い方

### フェーズ2: 仕上げ（ステップ8-12）
5. **ステップ8**: メタデータ生成 → 既存メソッド使用
6. **ステップ9**: サムネイル生成 → Pillow使用
7. **ステップ10**: Driveアップロード → 既存メソッド使用
8. **ステップ11**: 結果記録 → Sheets更新
9. **ステップ12**: 完了通知 → 既存メソッド使用

---

## 💡 よくある質問

### Q1: どのファイルから実装を始めればいい？

**A:** まず `modules/sheets_manager.py` と `modules/claude_client.py` に必要なメソッドを追加してから、`main.py` にステップ4-12を追加してください。

### Q2: 実装の確認方法は？

**A:** 各ステップを個別にテストできます：
```python
# テスト用コード例
async def test_step():
    pipeline = PodcastPipeline()
    await pipeline.step_01_initialize()
    await pipeline.step_02_create_sheet_row()
    # 特定のステップのみテスト
```

### Q3: エラーが出た時は？

**A:** 
1. `MODULE_DEPENDENCIES.md` で依存関係を確認
2. 必要な環境変数・ファイルが揃っているか確認
3. ログファイル（`logs/`）を確認

---

## 📚 詳細ドキュメント

- 全体像: `docs/ARCHITECTURE.md`
- 各ステップ詳細: `docs/STEPS_REFERENCE.md`
- 依存関係: `docs/MODULE_DEPENDENCIES.md`
- 実装ガイド: `IMPLEMENTATION_GUIDE.md`

