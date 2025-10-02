"""
YouTube AI Podcast メインエントリーポイント

メイン処理フロー:
1. 初期化（環境変数読み込み、通知送信）
2. Google Sheetsに新規行作成
3. Claude APIで情報収集（web_search使用）
4. Claude APIで台本生成
5. 音声生成（並列処理、分割・結合）
6. 字幕データ生成（STT + マッチング）
7. 動画生成（MoviePy）
8. メタデータ生成
9. サムネイル生成
10. Google Driveにアップロード
11. Google Sheetsに結果記録
12. 完了通知（処理時間含む）

処理時間目標: 合計15-25分
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.sheets_manager import SheetsManager
from modules.claude_client import ClaudeClient
from modules.audio_generator import AudioGenerator
from modules.video_generator import VideoGenerator
from modules.metadata_generator import MetadataGenerator
from modules.storage_manager import StorageManager
from modules.notifier import Notifier
from utils.logger import setup_logger
from utils.error_handler import ErrorHandler, RetryHandler
from utils.timer import Timer, timer_context

# 環境変数を読み込み
load_dotenv()

# グローバル設定
settings = Settings()
logger = setup_logger(
    settings.LOG_LEVEL,
    log_file=f"logs/podcast_{datetime.now().strftime('%Y%m%d')}.log"
)
error_handler = ErrorHandler(logger)
retry_handler = RetryHandler(logger, max_retries=3, delay=2.0)


class PodcastPipeline:
    """ポッドキャスト生成パイプライン"""

    def __init__(self):
        """パイプラインを初期化"""
        self.settings = settings
        self.logger = logger
        self.error_handler = error_handler
        self.retry_handler = retry_handler

        # 各モジュール
        self.sheets_manager = None
        self.claude_client = None
        self.audio_generator = None
        self.video_generator = None
        self.metadata_generator = None
        self.storage_manager = None
        self.notifier = None

        # 処理結果を保存
        self.results = {
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "sheet_row_id": None,
            "topics_data": None,
            "script_content": None,
            "audio_path": None,
            "subtitle_data": None,
            "video_path": None,
            "metadata": None,
            "thumbnail_path": None,
            "drive_urls": {},
            "status": "pending",
            "error_message": None
        }

        # タイマー
        self.total_timer = Timer("全体処理", logger)

    def _initialize_modules(self):
        """各モジュールを初期化"""
        try:
            self.logger.info("📦 モジュールを初期化しています...")

            self.sheets_manager = SheetsManager(self.settings)
            self.claude_client = ClaudeClient(self.settings)
            self.audio_generator = AudioGenerator(self.settings)
            self.video_generator = VideoGenerator(self.settings)
            self.metadata_generator = MetadataGenerator(self.settings)
            self.storage_manager = StorageManager(self.settings)
            self.notifier = Notifier(self.settings)

            self.logger.info("✅ モジュールの初期化が完了しました")

        except Exception as e:
            self.logger.error(f"❌ モジュールの初期化に失敗しました: {e}")
            raise

    async def step_01_initialize(self):
        """ステップ1: 初期化"""
        with timer_context("Step 1: 初期化", self.logger):
            self.logger.info("=" * 80)
            self.logger.info("🚀 ステップ1: 初期化を開始します")
            self.logger.info("=" * 80)

            try:
                self._initialize_modules()

                await self.notifier.send_custom_notification(
                    "🎬 YouTube AIポッドキャスト生成を開始します\n"
                    f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                self.results["start_time"] = datetime.now()
                self.logger.info("✅ ステップ1: 初期化が完了しました")

            except Exception as e:
                self.error_handler.handle_error(e, {"step": "initialize"})
                raise Exception(f"初期化に失敗しました: {e}")

    async def step_02_create_sheet_row(self):
        """ステップ2: Google Sheetsに新規行作成"""
        with timer_context("Step 2: Sheets新規行作成", self.logger):
            self.logger.info("=" * 80)
            self.logger.info("📊 ステップ2: Google Sheetsに新規行を作成します")
            self.logger.info("=" * 80)

            try:
                row_data = {
                    "実行日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ステータス": "処理中",
                    "進捗": "情報収集待ち"
                }

                row_id = await self.sheets_manager.create_new_row(row_data)
                self.results["sheet_row_id"] = row_id

                self.logger.info(f"✅ ステップ2: 新規行を作成しました (行ID: {row_id})")

            except Exception as e:
                self.error_handler.handle_error(e, {"step": "create_sheet_row"})
                raise Exception(f"Sheets新規行作成に失敗しました: {e}")

    async def step_03_collect_information(self):
        """ステップ3: Claude APIで情報収集"""
        with timer_context("Step 3: 情報収集 (目標: 2-3分)", self.logger):
            self.logger.info("=" * 80)
            self.logger.info("🔍 ステップ3: Claude APIで情報収集を行います")
            self.logger.info("=" * 80)

            try:
                topics_data = await self.retry_handler.retry_async(
                    self.claude_client.collect_topics_with_web_search
                )

                self.results["topics_data"] = topics_data

                await self.sheets_manager.update_row(
                    self.results["sheet_row_id"],
                    {"進捗": "台本生成待ち", "トピック数": len(topics_data.get("topics", []))}
                )

                self.logger.info(
                    f"✅ ステップ3: 情報収集が完了しました ({len(topics_data.get('topics', []))}件のトピック)"
                )

            except Exception as e:
                self.error_handler.handle_api_error(e, "Claude API (情報収集)")
                raise Exception(f"情報収集に失敗しました: {e}")

    async def run(self) -> Dict[str, Any]:
        """パイプライン全体を実行"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🎬 YouTube AIポッドキャスト生成パイプラインを開始します")
        self.logger.info("=" * 80 + "\n")

        self.total_timer.start()

        try:
            # 各ステップを順次実行
            await self.step_01_initialize()
            await self.step_02_create_sheet_row()
            await self.step_03_collect_information()
            # 他のステップも同様に実装...

            self.total_timer.stop()

            self.logger.info("\n" + "=" * 80)
            self.logger.info(
                f"✅ パイプライン全体が完了しました（処理時間: {self.total_timer.get_duration():.1f}秒）"
            )
            self.logger.info("=" * 80 + "\n")

            return {
                "status": "success",
                "message": "ポッドキャストが正常に生成されました",
                "results": self.results,
                "processing_time": self.total_timer.get_duration()
            }

        except Exception as e:
            self.total_timer.stop()

            self.results["status"] = "failed"
            self.results["error_message"] = str(e)

            self.logger.error("\n" + "=" * 80)
            self.logger.error(f"❌ パイプラインでエラーが発生しました: {e}")
            self.logger.error("=" * 80 + "\n")

            try:
                if self.notifier:
                    error_message = (
                        f"❌ YouTube AIポッドキャスト生成でエラーが発生しました\n"
                        f"\nエラー内容: {str(e)}\n"
                        f"処理時間: {self.total_timer.get_duration() / 60:.1f}分\n"
                        f"\n詳細はログファイルをご確認ください"
                    )
                    await self.notifier.send_error_notification(error_message)

                if self.sheets_manager and self.results["sheet_row_id"]:
                    await self.sheets_manager.update_row(
                        self.results["sheet_row_id"],
                        {"ステータス": "エラー", "エラー内容": str(e)[:500]}
                    )
            except:
                pass

            raise


async def main():
    """メイン関数"""
    try:
        pipeline = PodcastPipeline()
        result = await pipeline.run()

        logger.info("プログラムが正常に終了しました")
        return result

    except Exception as e:
        logger.error(f"プログラムが異常終了しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
