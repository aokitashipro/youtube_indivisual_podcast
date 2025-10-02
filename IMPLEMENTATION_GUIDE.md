# YouTube AI Podcast 実装ガイド

## main.py の完全な実装

現在の `main.py` には3つのステップまで実装されていますが、残りのステップ (4-12) を実装する必要があります。

### 実装済みのステップ

- ✅ ステップ1: 初期化（環境変数読み込み、通知送信）
- ✅ ステップ2: Google Sheetsに新規行作成
- ✅ ステップ3: Claude APIで情報収集（web_search使用）

### 実装が必要なステップ

#### ステップ4: Claude APIで台本生成

```python
async def step_04_generate_script(self):
    """ステップ4: Claude APIで台本生成"""
    with timer_context("Step 4: 台本生成 (目標: 2-3分)", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("📝 ステップ4: Claude APIで台本を生成します")
        self.logger.info("=" * 80)
        
        try:
            script_content = await self.retry_handler.retry_async(
                self.claude_client.generate_dialogue_script,
                self.results["topics_data"]
            )
            
            self.results["script_content"] = script_content
            
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                {"進捗": "音声生成待ち", "台本文字数": len(script_content.get("full_script", ""))}
            )
            
            self.logger.info(f"✅ ステップ4: 台本生成が完了しました ({len(script_content.get('full_script', ''))}文字)")
            
        except Exception as e:
            self.error_handler.handle_api_error(e, "Claude API (台本生成)")
            raise Exception(f"台本生成に失敗しました: {e}")
```

#### ステップ5: 音声生成（並列処理、分割・結合）

```python
async def step_05_generate_audio(self):
    """ステップ5: 音声生成（並列処理、分割・結合）"""
    with timer_context("Step 5: 音声生成 (目標: 5-10分)", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("🎤 ステップ5: 音声を生成します（並列処理）")
        self.logger.info("=" * 80)
        
        try:
            audio_retry_handler = RetryHandler(self.logger, max_retries=2, delay=1.5)
            
            audio_path = await audio_retry_handler.retry_async(
                self.audio_generator.generate_audio_parallel,
                self.results["script_content"]
            )
            
            self.results["audio_path"] = audio_path
            
            duration = self.audio_generator.get_audio_duration(audio_path)
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                {"進捗": "字幕生成待ち", "音声時間": f"{duration:.1f}秒"}
            )
            
            self.logger.info(f"✅ ステップ5: 音声生成が完了しました ({duration:.1f}秒)")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "generate_audio"})
            raise Exception(f"音声生成に失敗しました: {e}")
```

#### ステップ6: 字幕データ生成（STT + マッチング）

```python
async def step_06_generate_subtitles(self):
    """ステップ6: 字幕データ生成（STT + マッチング）"""
    with timer_context("Step 6: 字幕生成", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("💬 ステップ6: 字幕データを生成します（STT + マッチング）")
        self.logger.info("=" * 80)
        
        try:
            subtitle_data = await self.audio_generator.generate_subtitles(
                self.results["audio_path"],
                self.results["script_content"]
            )
            
            self.results["subtitle_data"] = subtitle_data
            
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                {"進捗": "動画生成待ち", "字幕数": len(subtitle_data.get("subtitles", []))}
            )
            
            self.logger.info(f"✅ ステップ6: 字幕生成が完了しました ({len(subtitle_data.get('subtitles', []))}個)")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "generate_subtitles"})
            raise Exception(f"字幕生成に失敗しました: {e}")
```

#### ステップ7: 動画生成（MoviePy）

```python
async def step_07_generate_video(self):
    """ステップ7: 動画生成（MoviePy）"""
    with timer_context("Step 7: 動画生成 (目標: 3-5分)", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("🎬 ステップ7: 動画を生成します（MoviePy）")
        self.logger.info("=" * 80)
        
        try:
            video_path = await self.video_generator.generate_video_with_subtitles(
                self.results["audio_path"],
                self.results["subtitle_data"],
                self.results["script_content"]
            )
            
            self.results["video_path"] = video_path
            
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                {"進捗": "メタデータ生成待ち"}
            )
            
            self.logger.info(f"✅ ステップ7: 動画生成が完了しました ({video_path})")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "generate_video"})
            raise Exception(f"動画生成に失敗しました: {e}")
```

#### ステップ8: メタデータ生成

```python
async def step_08_generate_metadata(self):
    """ステップ8: メタデータ生成"""
    with timer_context("Step 8: メタデータ生成", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("📋 ステップ8: メタデータを生成します")
        self.logger.info("=" * 80)
        
        try:
            metadata = await self.metadata_generator.generate_metadata(
                self.results["script_content"],
                self.results["topics_data"]
            )
            
            self.results["metadata"] = metadata
            
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                {"進捗": "サムネイル生成待ち", "動画タイトル": metadata.get("title", "")}
            )
            
            self.logger.info(f"✅ ステップ8: メタデータ生成が完了しました")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "generate_metadata"})
            raise Exception(f"メタデータ生成に失敗しました: {e}")
```

#### ステップ9: サムネイル生成

```python
async def step_09_generate_thumbnail(self):
    """ステップ9: サムネイル生成"""
    with timer_context("Step 9: サムネイル生成", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("🖼️  ステップ9: サムネイルを生成します")
        self.logger.info("=" * 80)
        
        try:
            thumbnail_path = await self.video_generator.generate_thumbnail(
                self.results["metadata"]
            )
            
            self.results["thumbnail_path"] = thumbnail_path
            
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                {"進捗": "アップロード待ち"}
            )
            
            self.logger.info(f"✅ ステップ9: サムネイル生成が完了しました ({thumbnail_path})")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "generate_thumbnail"})
            raise Exception(f"サムネイル生成に失敗しました: {e}")
```

#### ステップ10: Google Driveにアップロード

```python
async def step_10_upload_to_drive(self):
    """ステップ10: Google Driveにアップロード"""
    with timer_context("Step 10: Google Driveアップロード", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("☁️  ステップ10: Google Driveにアップロードします")
        self.logger.info("=" * 80)
        
        try:
            video_url = await self.storage_manager.upload_video(
                self.results["video_path"],
                self.results["metadata"]
            )
            self.results["drive_urls"]["video"] = video_url
            
            audio_url = await self.storage_manager.upload_audio(
                self.results["audio_path"],
                self.results["metadata"]
            )
            self.results["drive_urls"]["audio"] = audio_url
            
            thumbnail_url = await self.storage_manager.upload_file(
                self.results["thumbnail_path"],
                "thumbnail",
                self.results["metadata"]
            )
            self.results["drive_urls"]["thumbnail"] = thumbnail_url
            
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                {"進捗": "完了", "動画URL": video_url}
            )
            
            self.logger.info(f"✅ ステップ10: アップロードが完了しました")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "upload_to_drive"})
            raise Exception(f"Google Driveへのアップロードに失敗しました: {e}")
```

#### ステップ11: Google Sheetsに結果記録

```python
async def step_11_record_results(self):
    """ステップ11: Google Sheetsに結果記録"""
    with timer_context("Step 11: 結果記録", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("📝 ステップ11: Google Sheetsに結果を記録します")
        self.logger.info("=" * 80)
        
        try:
            self.results["end_time"] = datetime.now()
            duration = (self.results["end_time"] - self.results["start_time"]).total_seconds()
            self.results["total_duration"] = duration
            
            result_data = {
                "ステータス": "完了",
                "完了日時": self.results["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
                "処理時間（秒）": f"{duration:.1f}",
                "動画URL": self.results["drive_urls"].get("video", ""),
                "音声URL": self.results["drive_urls"].get("audio", ""),
                "サムネイルURL": self.results["drive_urls"].get("thumbnail", ""),
                "動画タイトル": self.results["metadata"].get("title", ""),
                "動画説明": self.results["metadata"].get("description", "")[:100],
                "タグ": ", ".join(self.results["metadata"].get("tags", [])),
            }
            
            await self.sheets_manager.update_row(
                self.results["sheet_row_id"],
                result_data
            )
            
            self.results["status"] = "completed"
            self.logger.info(f"✅ ステップ11: 結果記録が完了しました")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "record_results"})
            raise Exception(f"結果記録に失敗しました: {e}")
```

#### ステップ12: 完了通知（処理時間含む）

```python
async def step_12_send_completion_notification(self):
    """ステップ12: 完了通知（処理時間含む）"""
    with timer_context("Step 12: 完了通知", self.logger):
        self.logger.info("=" * 80)
        self.logger.info("🎉 ステップ12: 完了通知を送信します")
        self.logger.info("=" * 80)
        
        try:
            notification_message = (
                f"🎉 YouTube AIポッドキャスト生成が完了しました！\n"
                f"\n"
                f"📹 タイトル: {self.results['metadata'].get('title', 'N/A')}\n"
                f"⏱️ 処理時間: {self.results['total_duration'] / 60:.1f}分\n"
                f"🎬 動画時間: {self.results['metadata'].get('duration', 'N/A')}秒\n"
                f"\n"
                f"🔗 動画URL: {self.results['drive_urls'].get('video', 'N/A')}\n"
                f"🔗 音声URL: {self.results['drive_urls'].get('audio', 'N/A')}\n"
                f"🔗 サムネイル: {self.results['drive_urls'].get('thumbnail', 'N/A')}\n"
                f"\n"
                f"📊 詳細はGoogle Sheetsをご確認ください"
            )
            
            await self.notifier.send_custom_notification(notification_message)
            
            self.logger.info(f"✅ ステップ12: 完了通知を送信しました")
            
        except Exception as e:
            self.error_handler.handle_error(e, {"step": "send_notification"})
            self.logger.warning(f"完了通知の送信に失敗しました: {e}")
```

### run() メソッドの更新

`run()` メソッドの201行目の `# 他のステップも同様に実装...` を以下に置き換えてください：

```python
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

## 各モジュールで実装が必要なメソッド

### SheetsManager
- `create_new_row(row_data)` - 新規行を作成
- `update_row(row_id, data)` - 行を更新

### ClaudeClient
- `collect_topics_with_web_search()` - Web検索で情報収集
- `generate_dialogue_script(topics_data)` - 台本生成

### AudioGenerator
- `generate_audio_parallel(script_content)` - 並列音声生成
- `generate_subtitles(audio_path, script_content)` - 字幕生成
- `get_audio_duration(audio_path)` - 音声長取得

### VideoGenerator
- `generate_video_with_subtitles(audio_path, subtitle_data, script_content)` - 動画生成
- `generate_thumbnail(metadata)` - サムネイル生成

### MetadataGenerator
- `generate_metadata(script_content, topics_data)` - メタデータ生成

### StorageManager
- `upload_video(video_path, metadata)` - 動画アップロード
- `upload_audio(audio_path, metadata)` - 音声アップロード
- `upload_file(file_path, file_type, metadata)` - ファイルアップロード

## コードの特徴

✅ **読みやすさ**
- 各ステップが独立したメソッドとして定義
- 明確な命名規則（step_XX_機能名）
- 適切なコメントとログ

✅ **メンテナンス性**
- 各ステップが独立しており、個別に修正可能
- エラーハンドリングが統一
- 処理時間の計測が容易

✅ **エラーハンドリング**
- 各ステップでtry-except
- リトライロジック実装
- Slack通知 + Google Sheets記録

✅ **パフォーマンス**
- 処理時間の計測と目標時間の表示
- 各ステップの処理時間をログ出力
- 並列処理の実装（音声生成）

## 次のステップ

1. 上記のメソッドを `main.py` に追加
2. 各モジュールで必要なメソッドを実装
3. `.env` ファイルを設定
4. Google認証情報を配置
5. テスト実行

```bash
python main.py
```

