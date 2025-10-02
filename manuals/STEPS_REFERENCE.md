# YouTube AI Podcast - 各ステップの実装リファレンス

このドキュメントは、各ステップで参照・実装が必要なファイルとメソッドを明確に示します。

---

## 📋 ステップ概要

| ステップ | 説明 | 目標時間 | 実装状況 |
|---------|------|----------|----------|
| 1 | 初期化 | - | ✅ 実装済み |
| 2 | Sheets新規行作成 | - | ✅ 実装済み |
| 3 | 情報収集 | 2-3分 | ✅ 実装済み |
| 4 | 台本生成 | 2-3分 | 📝 要実装 |
| 5 | 音声生成 | 5-10分 | 📝 要実装 |
| 6 | 字幕生成 | 1-2分 | 📝 要実装 |
| 7 | 動画生成 | 3-5分 | 📝 要実装 |
| 8 | メタデータ生成 | 1分 | 📝 要実装 |
| 9 | サムネイル生成 | 1分 | 📝 要実装 |
| 10 | Driveアップロード | 2-3分 | 📝 要実装 |
| 11 | 結果記録 | - | 📝 要実装 |
| 12 | 完了通知 | - | 📝 要実装 |

---

## ✅ ステップ1: 初期化

### 📍 実装場所
- `main.py` → `PodcastPipeline.step_01_initialize()`
- `main.py` → `PodcastPipeline._initialize_modules()`

### 📂 参照ファイル

#### 必須
```
config/settings.py
├── Settings クラス
└── 全ての環境変数を読み込み

utils/logger.py
├── setup_logger(level, log_file)
└── ロガーの初期化

utils/error_handler.py
├── ErrorHandler(logger)
└── エラーハンドラーの初期化

utils/timer.py
├── Timer(name, logger)
└── タイマーの初期化
```

#### 初期化するモジュール
```
modules/sheets_manager.py
├── SheetsManager(settings)
└── Google Sheets接続の初期化

modules/claude_client.py
├── ClaudeClient(settings)
└── Claude API接続の初期化

modules/audio_generator.py
├── AudioGenerator(settings)
└── 音声生成の初期化

modules/video_generator.py
├── VideoGenerator(settings)
└── 動画生成の初期化

modules/metadata_generator.py
├── MetadataGenerator(settings)
└── メタデータ生成の初期化

modules/storage_manager.py
├── StorageManager(settings)
└── Google Drive接続の初期化

modules/notifier.py
├── Notifier(settings)
└── Slack接続の初期化
```

### 🔧 実装内容
- 環境変数の読み込み（`.env`）
- 各モジュールのインスタンス化
- ロガー、エラーハンドラー、タイマーの初期化
- Slackへの開始通知送信

### ✅ 実装状態
**完了** - `main.py` の116-136行目に実装済み

---

## ✅ ステップ2: Google Sheetsに新規行作成

### 📍 実装場所
- `main.py` → `PodcastPipeline.step_02_create_sheet_row()`

### 📂 参照ファイル

#### 必須
```
modules/sheets_manager.py
├── create_new_row(row_data: Dict) -> str
│   ├── 新規行をGoogle Sheetsに追加
│   └── 行IDを返す
└── 依存: gspread, Google Sheets API
```

#### 実装が必要なメソッド
```python
# modules/sheets_manager.py に追加
async def create_new_row(self, row_data: Dict[str, Any]) -> str:
    """
    Google Sheetsに新規行を作成
    
    Args:
        row_data: 行に書き込むデータ
        
    Returns:
        作成された行のID（行番号）
    """
    try:
        spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEETS_ID)
        worksheet = spreadsheet.sheet1
        
        # データを行として追加
        row_values = list(row_data.values())
        worksheet.append_row(row_values)
        
        # 追加された行番号を取得
        row_id = len(worksheet.get_all_values())
        
        return str(row_id)
    except Exception as e:
        logger.error(f"新規行作成に失敗: {e}")
        raise
```

### 🔧 実装内容
- 実行日時、ステータス、進捗情報を含む新規行を作成
- 作成された行IDを `self.results["sheet_row_id"]` に保存

### ✅ 実装状態
**完了** - `main.py` の138-159行目に実装済み
**要追加** - `modules/sheets_manager.py` に `create_new_row()` メソッドを追加

---

## ✅ ステップ3: Claude APIで情報収集

### 📍 実装場所
- `main.py` → `PodcastPipeline.step_03_collect_information()`

### 📂 参照ファイル

#### 必須
```
modules/claude_client.py
├── collect_topics_with_web_search() -> Dict
│   ├── Claude APIのweb_search機能を使用
│   ├── Indie Hackers, Product Hunt, Hacker Newsから情報収集
│   └── 3-5件のトピックを収集
└── 依存: anthropic, Claude API

config/prompts.yaml
└── 情報収集用プロンプトテンプレート
```

#### 実装が必要なメソッド
```python
# modules/claude_client.py に追加
async def collect_topics_with_web_search(self) -> Dict[str, Any]:
    """
    Claude APIのweb_search機能で情報収集
    
    情報源:
    - Indie Hackers
    - Product Hunt
    - Hacker News Show HN
    
    Returns:
        収集したトピックデータ
    """
    try:
        prompt = """
        以下の情報源から、最新の個人開発・AI関連の興味深いトピックを3-5件収集してください：
        
        1. Indie Hackers (https://www.indiehackers.com/)
        2. Product Hunt (https://www.producthunt.com/)
        3. Hacker News Show HN (https://news.ycombinator.com/show)
        
        各トピックについて以下の情報を含めてください：
        - タイトル
        - 概要（200文字程度）
        - URL
        - カテゴリ（個人開発/AI/MicroSaaS等）
        - 興味深いポイント
        """
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.7,
            tools=[{"type": "web_search"}],  # web_search有効化
            messages=[{"role": "user", "content": prompt}]
        )
        
        # レスポンスを解析してトピックデータを構造化
        topics_data = self._parse_topics_response(response)
        
        return topics_data
        
    except Exception as e:
        logger.error(f"情報収集に失敗: {e}")
        raise
```

### 🔧 実装内容
- Claude APIの `web_search` 機能を使用して最新情報を収集
- 3-5件のトピックを取得
- 結果を `self.results["topics_data"]` に保存
- Google Sheetsの進捗を更新

### ✅ 実装状態
**完了** - `main.py` の161-186行目に実装済み
**要追加** - `modules/claude_client.py` に `collect_topics_with_web_search()` メソッドを追加

---

## 📝 ステップ4: Claude APIで台本生成

### 📍 実装場所
- `main.py` → `PodcastPipeline.step_04_generate_script()`（要追加）

### 📂 参照ファイル

#### 必須
```
modules/claude_client.py
├── generate_dialogue_script(topics_data: Dict) -> Dict
│   ├── 対談形式の台本を生成
│   ├── Aさん（楽観派）とBさん（懐疑派）の掛け合い
│   └── 15-20分の長さ
└── 依存: anthropic, Claude API

config/prompts.yaml
├── 台本生成用プロンプトテンプレート
└── キャラクター設定
```

#### 実装が必要なメソッド
```python
# modules/claude_client.py に追加
async def generate_dialogue_script(self, topics_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    対談形式の台本を生成
    
    Args:
        topics_data: ステップ3で収集したトピックデータ
        
    Returns:
        生成された台本データ
        {
            "title": str,
            "full_script": str,
            "sections": List[Dict],
            "estimated_duration": int
        }
    """
    try:
        prompt = f"""
        以下のトピックについて、対談形式のポッドキャスト台本を生成してください：
        
        トピック:
        {json.dumps(topics_data, ensure_ascii=False, indent=2)}
        
        キャラクター:
        - Aさん（楽観派）: 新しいものに興味津々、実装の可能性を考える
        - Bさん（懐疑派）: 現実的・批判的視点、ビジネス面を問う
        
        構成（15-20分）:
        1. オープニング (1分)
        2. トピック1 (3-4分)
        3. トピック2 (3-4分)
        4. トピック3 (3-4分)
        5. [追加トピック]（オプション）
        6. クロージング (1-2分)
        
        自然な会話形式で、聞き手が興味を持てる内容にしてください。
        """
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        script_content = self._parse_script_response(response)
        
        return script_content
        
    except Exception as e:
        logger.error(f"台本生成に失敗: {e}")
        raise
```

### 🔧 実装内容
- ステップ3で収集したトピックを元に台本生成
- Aさん（楽観派）とBさん（懐疑派）の対談形式
- 15-20分の長さ
- 結果を `self.results["script_content"]` に保存

### 📝 実装状態
**未実装** - `IMPLEMENTATION_GUIDE.md` 参照

---

## 📝 ステップ5: 音声生成（並列処理）

### 📍 実装場所
- `main.py` → `PodcastPipeline.step_05_generate_audio()`（要追加）

### 📂 参照ファイル

#### 必須
```
modules/audio_generator.py
├── generate_audio_parallel(script_content: Dict) -> str
│   ├── 台本を分割して並列処理
│   ├── Google Cloud TTS使用
│   ├── 複数APIキーで3並列処理
│   └── 音声ファイルを結合
└── 依存: google-cloud-texttospeech, pydub

config/settings.py
├── GOOGLE_CREDENTIALS_PATH
└── AUDIO_SAMPLE_RATE, AUDIO_BITRATE
```

#### 実装が必要なメソッド
```python
# modules/audio_generator.py に追加
async def generate_audio_parallel(self, script_content: Dict[str, Any]) -> str:
    """
    台本から音声を並列生成
    
    処理フロー:
    1. 台本を5000文字以内のチャンクに分割
    2. 各チャンクを並列処理（3並列）
    3. 生成された音声ファイルを結合
    
    Args:
        script_content: ステップ4で生成した台本
        
    Returns:
        結合された音声ファイルのパス
    """
    try:
        full_script = script_content.get("full_script", "")
        
        # 台本を話者ごとに分割
        chunks = self._split_script_by_speaker(full_script)
        
        # 並列処理で音声生成
        audio_files = []
        tasks = []
        
        for i, chunk in enumerate(chunks):
            task = self._generate_single_audio(
                chunk["text"],
                chunk["speaker"],
                f"temp/audio_chunk_{i}.mp3"
            )
            tasks.append(task)
        
        audio_files = await asyncio.gather(*tasks)
        
        # 音声ファイルを結合
        final_audio_path = self._merge_audio_files(audio_files)
        
        return final_audio_path
        
    except Exception as e:
        logger.error(f"音声生成に失敗: {e}")
        raise

async def _generate_single_audio(self, text: str, speaker: str, output_path: str) -> str:
    """
    単一のチャンクを音声に変換
    
    Google Cloud TTSを使用:
    - Aさん: ja-JP-Neural2-C (ピッチ: 0)
    - Bさん: ja-JP-Neural2-D (ピッチ: -2)
    """
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    
    # 話者に応じて声を選択
    if speaker == "A":
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            name="ja-JP-Neural2-C",
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=0.0,
        )
    else:  # B
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            name="ja-JP-Neural2-D",
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=-2.0,
        )
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    
    return output_path
```

### 🔧 実装内容
- 台本を5000文字以内のチャンクに分割
- Google Cloud TTSで音声生成（3並列）
- Aさん（ja-JP-Neural2-C）、Bさん（ja-JP-Neural2-D）
- 音声ファイルを結合
- リトライは2回

### 📝 実装状態
**未実装** - `IMPLEMENTATION_GUIDE.md` 参照

---

## 📝 ステップ6: 字幕データ生成（STT + マッチング）

### 📍 実装場所
- `main.py` → `PodcastPipeline.step_06_generate_subtitles()`（要追加）

### 📂 参照ファイル

#### 必須
```
modules/audio_generator.py
├── generate_subtitles(audio_path: str, script_content: Dict) -> Dict
│   ├── ElevenLabs STTで音声→テキスト変換
│   ├── 元の台本テキストとマッチング
│   └── タイムスタンプ + 正確なテキスト
└── 依存: elevenlabs

config/settings.py
└── ELEVENLABS_API_KEY
```

#### 実装が必要なメソッド
```python
# modules/audio_generator.py に追加
async def generate_subtitles(
    self, 
    audio_path: str, 
    script_content: Dict[str, Any]
) -> Dict[str, Any]:
    """
    音声から字幕データを生成
    
    処理フロー:
    1. ElevenLabs STTで音声→テキスト変換（タイムスタンプ付き）
    2. 元の台本テキストとマッチング
    3. タイムスタンプと正確なテキストを組み合わせ
    
    Args:
        audio_path: ステップ5で生成した音声ファイルパス
        script_content: ステップ4で生成した台本
        
    Returns:
        字幕データ
        {
            "subtitles": List[{
                "start_time": float,
                "end_time": float,
                "text": str,
                "speaker": str
            }]
        }
    """
    try:
        from elevenlabs import transcribe
        
        # ElevenLabs STTで文字起こし
        with open(audio_path, "rb") as audio_file:
            transcription = transcribe(audio_file)
        
        # 元の台本テキストを取得
        original_script = script_content.get("full_script", "")
        
        # タイムスタンプとテキストをマッチング
        subtitles = self._match_timestamps_with_script(
            transcription,
            original_script
        )
        
        return {"subtitles": subtitles}
        
    except Exception as e:
        logger.error(f"字幕生成に失敗: {e}")
        raise
```

### 🔧 実装内容
- ElevenLabs STTで音声→テキスト変換
- 元の台本テキストとマッチング（精度95%以上）
- タイムスタンプ + 正確なテキスト
- 結果を `self.results["subtitle_data"]` に保存

### 📝 実装状態
**未実装** - `IMPLEMENTATION_GUIDE.md` 参照

---

## 📝 ステップ7: 動画生成（MoviePy）

### 📍 実装場所
- `main.py` → `PodcastPipeline.step_07_generate_video()`（要追加）

### 📂 参照ファイル

#### 必須
```
modules/video_generator.py
├── generate_video_with_subtitles(audio_path, subtitle_data, script) -> str
│   ├── MoviePyで動画生成
│   ├── 背景画像 + 音声 + 字幕
│   └── 1920x1080, 30fps
└── 依存: moviepy, Pillow

assets/background.png
├── 背景画像（1920x1080）
└── Lo-fi風の静止画

assets/fonts/NotoSansJP-Regular.ttf
└── 日本語フォント

config/settings.py
├── VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS
└── FONT_PATH, BACKGROUND_IMAGE_PATH
```

#### 実装が必要なメソッド
```python
# modules/video_generator.py に追加
async def generate_video_with_subtitles(
    self,
    audio_path: str,
    subtitle_data: Dict[str, Any],
    script_content: Dict[str, Any]
) -> str:
    """
    字幕付き動画を生成
    
    構成:
    - 背景画像（1920x1080）
    - 音声
    - 字幕（下部中央、Y=900）
    
    Args:
        audio_path: 音声ファイルパス
        subtitle_data: 字幕データ
        script_content: 台本データ
        
    Returns:
        生成された動画ファイルパス
    """
    try:
        from moviepy.editor import (
            AudioFileClip, ImageClip, TextClip,
            CompositeVideoClip
        )
        
        # 音声を読み込み
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # 背景画像を読み込み
        background = ImageClip(
            self.settings.BACKGROUND_IMAGE_PATH,
            duration=duration
        ).resize((self.settings.VIDEO_WIDTH, self.settings.VIDEO_HEIGHT))
        
        # 字幕クリップを作成
        subtitle_clips = []
        for sub in subtitle_data.get("subtitles", []):
            txt_clip = TextClip(
                sub["text"],
                fontsize=40,
                color="white",
                font=self.settings.FONT_PATH,
                method='caption',
                size=(self.settings.VIDEO_WIDTH - 100, None),
                bg_color='black@0.7'  # 黒背景（透過度70%）
            ).set_position(('center', 900))  # Y=900
            
            txt_clip = txt_clip.set_start(sub["start_time"])
            txt_clip = txt_clip.set_duration(
                sub["end_time"] - sub["start_time"]
            )
            
            subtitle_clips.append(txt_clip)
        
        # 動画を合成
        video = CompositeVideoClip(
            [background] + subtitle_clips
        ).set_audio(audio_clip)
        
        # 出力
        output_path = f"{self.settings.OUTPUT_DIR}/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video.write_videofile(
            output_path,
            fps=self.settings.VIDEO_FPS,
            codec='libx264',
            audio_codec='aac'
        )
        
        return output_path
        
    except Exception as e:
        logger.error(f"動画生成に失敗: {e}")
        raise
```

### 🔧 実装内容
- MoviePyで動画生成
- 背景画像 + 音声 + 字幕
- 1920x1080, 30fps
- 字幕: 下部中央（Y=900）、フォントサイズ40px、黒背景（透過70%）

### 📝 実装状態
**未実装** - `IMPLEMENTATION_GUIDE.md` 参照

---

## 📝 ステップ8-12

残りのステップについては `IMPLEMENTATION_GUIDE.md` を参照してください。

各ステップの詳細な実装コードと説明が記載されています。

---

## 🔗 関連ドキュメント

- `docs/ARCHITECTURE.md` - アーキテクチャとモジュール依存関係
- `IMPLEMENTATION_GUIDE.md` - 全ステップの実装ガイド
- `README.md` - プロジェクト概要
- `.cursor/rules/要件定義.mdc` - 詳細な要件定義

