"""
フルパイプライン実行（実際のリサーチから開始）

モックデータではなく、実際のClaude APIリサーチから全ステップを実行します。
"""
import asyncio
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from config.settings import Settings
from modules.claude_client import ClaudeClient
from modules.gemini_audio_generator import GeminiAudioGenerator
from modules.subtitle_generator import SubtitleGenerator
from modules.video_generator import VideoGenerator
from modules.sheets_client import SheetsClient
import requests


class RealPipeline:
    """実際のリサーチから始めるフルパイプライン"""
    
    def __init__(self):
        self.settings = Settings()
        self.results = {}
        self.start_time = time.time()
    
    async def step_01_initialize(self):
        """ステップ1: 初期化"""
        print("\n" + "=" * 80)
        print("📋 ステップ1: 初期化")
        print("=" * 80)
        
        try:
            self.claude_client = ClaudeClient(self.settings)
            self.audio_generator = GeminiAudioGenerator(self.settings)
            self.subtitle_generator = SubtitleGenerator(self.settings)
            self.video_generator = VideoGenerator(self.settings)
            self.sheets_client = SheetsClient(self.settings)
            
            logger.info("✅ 全モジュール初期化完了")
            return True
            
        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            return False
    
    async def step_02_create_sheet_row(self):
        """ステップ2: Google Sheets新規行作成"""
        print("\n" + "=" * 80)
        print("📋 ステップ2: Google Sheets新規行作成")
        print("=" * 80)
        
        try:
            if not self.sheets_client.test_connection():
                logger.warning("⚠️ Google Sheets接続失敗、スキップします")
                return True
            
            execution_id = self.sheets_client.create_execution_log()
            if execution_id:
                self.results["execution_id"] = execution_id
                logger.info(f"✅ 実行ログ作成: {execution_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sheets行作成エラー: {e}")
            return False
    
    async def step_03_collect_information(self):
        """ステップ3: 実際のリサーチで情報収集"""
        print("\n" + "=" * 80)
        print("📋 ステップ3: 情報収集（Claude API - 実際のリサーチ）")
        print("=" * 80)
        
        try:
            # 実際のリサーチを試みる（use_mock_data=False）
            topics_data = self.claude_client.collect_topics_with_web_search(
                use_history=False,
                use_mock_data=False  # 実際のAPIを使用
            )
            
            self.results["topics_data"] = topics_data
            logger.info(f"✅ トピック収集完了: {len(topics_data.get('topics', []))}件")
            
            # トピックをプレビュー
            for i, topic in enumerate(topics_data.get('topics', [])[:3], 1):
                print(f"\n  トピック{i}: {topic.get('title_ja', 'N/A')}")
                print(f"    カテゴリ: {topic.get('category', 'N/A')}")
                print(f"    ソース: {topic.get('source', 'N/A')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 情報収集エラー: {e}")
            return False
    
    async def step_04_generate_script(self):
        """ステップ4: 台本生成"""
        print("\n" + "=" * 80)
        print("📋 ステップ4: 台本生成（Claude API）")
        print("=" * 80)
        
        try:
            topics_data = self.results.get("topics_data")
            
            # 台本生成
            script_content = self.claude_client.generate_dialogue_script(topics_data)
            
            self.results["script_content"] = script_content
            
            full_script = script_content.get('full_script', '')
            logger.info(f"✅ 台本生成完了: {len(full_script)}文字")
            
            # プレビュー
            print(f"\n  台本プレビュー:")
            print(f"    {full_script[:200]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 台本生成エラー: {e}")
            return False
    
    async def step_05_generate_audio(self):
        """ステップ5: 音声生成"""
        print("\n" + "=" * 80)
        print("📋 ステップ5: 音声生成（Gemini API）")
        print("=" * 80)
        
        try:
            script_content = self.results.get("script_content")
            execution_id = self.results.get("execution_id", "real_pipeline")
            
            audio_result = await self.audio_generator.generate_full_audio(
                script_content,
                Path("temp/real_audio"),
                execution_id
            )
            
            self.results["audio_path"] = str(audio_result["audio_file"])
            logger.info(f"✅ 音声生成完了: {audio_result['audio_file']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 音声生成エラー: {e}")
            return False
    
    async def step_06_generate_subtitles(self):
        """ステップ6: 字幕生成"""
        print("\n" + "=" * 80)
        print("📋 ステップ6: 字幕生成（ElevenLabs STT）")
        print("=" * 80)
        
        try:
            audio_path = self.results.get("audio_path")
            script_content = self.results.get("script_content")
            
            subtitle_data = await self.subtitle_generator.generate_subtitles(
                audio_path,
                script_content,
                time_offset=0.0  # 必要に応じて調整
            )
            
            self.results["subtitle_data"] = subtitle_data
            logger.info(f"✅ 字幕生成完了: {len(subtitle_data.get('subtitles', []))}セグメント")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 字幕生成エラー: {e}")
            return False
    
    async def step_07_generate_video(self):
        """ステップ7: 動画生成"""
        print("\n" + "=" * 80)
        print("📋 ステップ7: 動画生成（MoviePy）")
        print("=" * 80)
        
        try:
            audio_path = self.results.get("audio_path")
            subtitle_data = self.results.get("subtitle_data")
            
            video_path = await self.video_generator.generate_video_with_subtitles(
                audio_path,
                subtitle_data.get("subtitles", []),
                background_image_path="assets/images/background.png"
            )
            
            self.results["video_path"] = video_path
            logger.info(f"✅ 動画生成完了: {video_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 動画生成エラー: {e}")
            return False
    
    async def step_08_generate_metadata(self):
        """ステップ8: メタデータ生成"""
        print("\n" + "=" * 80)
        print("📋 ステップ8: メタデータ生成（Claude API）")
        print("=" * 80)
        
        try:
            script_content = self.results.get("script_content")
            topics_data = self.results.get("topics_data")
            
            metadata = await self.claude_client.generate_youtube_metadata(
                script_content,
                topics_data
            )
            
            comment = await self.claude_client.generate_comment(script_content)
            
            self.results["metadata"] = metadata
            self.results["comment"] = comment
            logger.info(f"✅ メタデータ生成完了")
            logger.info(f"   タイトル: {metadata.get('title', 'N/A')[:50]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ メタデータ生成エラー: {e}")
            return False
    
    async def step_09_generate_thumbnail(self):
        """ステップ9: サムネイル生成"""
        print("\n" + "=" * 80)
        print("📋 ステップ9: サムネイル生成（PIL）")
        print("=" * 80)
        
        try:
            metadata = self.results.get("metadata")
            
            thumbnail_path = await self.video_generator.generate_thumbnail(
                metadata,
                background_path="assets/images/background.png",
                save_json=True
            )
            
            self.results["thumbnail_path"] = thumbnail_path
            logger.info(f"✅ サムネイル生成完了: {thumbnail_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ サムネイル生成エラー: {e}")
            return False
    
    async def step_10_save_to_sheets(self):
        """ステップ10: Google Sheetsに保存"""
        print("\n" + "=" * 80)
        print("📋 ステップ10: Google Sheetsに保存（GAS Web API）")
        print("=" * 80)
        
        try:
            metadata = self.results.get("metadata")
            comment = self.results.get("comment")
            video_path = self.results.get("video_path", "")
            audio_path = self.results.get("audio_path", "")
            thumbnail_path = self.results.get("thumbnail_path", "")
            
            execution_time = time.time() - self.start_time
            
            # GAS Web APIでメタデータを送信
            payload = {
                'action': 'save_metadata',
                'metadata': metadata,
                'comment': comment,
                'video_path': video_path,
                'audio_path': audio_path,
                'thumbnail_path': thumbnail_path,
                'processing_time': f'{execution_time:.1f}秒'
            }
            
            response = requests.post(
                self.settings.GAS_WEB_APP_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"✅ Google Sheetsに保存成功: 行{result.get('row_number')}")
                    self.results["sheet_row_number"] = result.get('row_number')
                else:
                    logger.error(f"❌ 保存失敗: {result.get('error')}")
                    return False
            else:
                logger.error(f"❌ HTTPエラー: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sheets保存エラー: {e}")
            return False
    
    async def run_all_steps(self):
        """全ステップを実行"""
        print("\n" + "=" * 80)
        print("🎬 YouTube AI Podcast - 実際のリサーチからフルパイプライン実行")
        print("=" * 80)
        
        steps = [
            ("1. 初期化", self.step_01_initialize),
            ("2. Sheets新規行作成", self.step_02_create_sheet_row),
            ("3. 情報収集（実際のリサーチ）", self.step_03_collect_information),
            ("4. 台本生成", self.step_04_generate_script),
            ("5. 音声生成", self.step_05_generate_audio),
            ("6. 字幕生成", self.step_06_generate_subtitles),
            ("7. 動画生成", self.step_07_generate_video),
            ("8. メタデータ生成", self.step_08_generate_metadata),
            ("9. サムネイル生成", self.step_09_generate_thumbnail),
            ("10. Google Sheetsに保存", self.step_10_save_to_sheets),
        ]
        
        for step_name, step_func in steps:
            try:
                success = await step_func()
                if not success:
                    logger.error(f"❌ {step_name}が失敗しました。中断します。")
                    return False
            except Exception as e:
                logger.error(f"❌ {step_name}で予期しないエラー: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
        
        self.print_summary()
        return True
    
    def print_summary(self):
        """実行結果のサマリーを表示"""
        execution_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("🎉 全パイプライン完了！")
        print("=" * 80)
        
        print(f"\n⏱️  総処理時間: {execution_time:.1f}秒 ({execution_time/60:.1f}分)")
        
        print("\n📊 実行結果:")
        print(f"   トピック数: {len(self.results.get('topics_data', {}).get('topics', []))}件")
        print(f"   台本文字数: {len(self.results.get('script_content', {}).get('full_script', ''))}文字")
        print(f"   字幕セグメント数: {len(self.results.get('subtitle_data', {}).get('subtitles', []))}個")
        
        print("\n📁 生成されたファイル:")
        if "audio_path" in self.results:
            audio_size = os.path.getsize(self.results['audio_path']) / 1024
            print(f"   音声: {self.results['audio_path']}")
            print(f"   サイズ: {audio_size:.1f}KB")
        
        if "video_path" in self.results:
            video_size = os.path.getsize(self.results['video_path']) / 1024 / 1024
            print(f"   動画: {self.results['video_path']}")
            print(f"   サイズ: {video_size:.1f}MB")
        
        if "thumbnail_path" in self.results:
            thumb_size = os.path.getsize(self.results['thumbnail_path']) / 1024
            print(f"   サムネイル: {self.results['thumbnail_path']}")
            print(f"   サイズ: {thumb_size:.1f}KB")
        
        print("\n📊 メタデータ:")
        if "metadata" in self.results:
            metadata = self.results["metadata"]
            print(f"   タイトル: {metadata.get('title', 'N/A')}")
            print(f"   タグ: {', '.join(metadata.get('tags', [])[:5])}...")
            print(f"   サムネイルテキスト: {metadata.get('thumbnail_text', 'N/A')}")
        
        if "comment" in self.results:
            print(f"\n💬 コメント:")
            print(f"   {self.results['comment'][:150]}...")
        
        if "sheet_row_number" in self.results:
            print(f"\n📊 Google Sheets:")
            print(f"   保存先: 行{self.results['sheet_row_number']}")
        
        print("\n" + "=" * 80)
        print("🎬 ファイルを確認:")
        if "video_path" in self.results:
            print(f"   動画: open {self.results['video_path']}")
        if "thumbnail_path" in self.results:
            print(f"   サムネイル: open {self.results['thumbnail_path']}")
        print("=" * 80 + "\n")


async def main():
    """メイン関数"""
    print("\n🚀 実際のリサーチから始めるフルパイプラインを実行します")
    print("✅ Claude API Extended Tools（Web検索）を使用します\n")
    
    pipeline = RealPipeline()
    success = await pipeline.run_all_steps()
    
    if not success:
        print("\n❌ パイプライン実行に失敗しました")
        exit(1)
    
    print("\n✅ パイプライン実行に成功しました")


if __name__ == "__main__":
    asyncio.run(main())

