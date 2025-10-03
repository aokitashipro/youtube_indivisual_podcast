"""
フルパイプライン統合テスト（ステップ1-9）

このスクリプトは以下のステップを実行します：
1. 初期化
2. Google Sheets新規行作成
3. 情報収集（Claude API）
4. 台本生成（Claude API）
5. 音声生成（Gemini API）
6. 字幕生成（ElevenLabs STT）
7. 動画生成（MoviePy）
8. メタデータ生成（Claude API）
9. サムネイル生成（PIL）
"""
import asyncio
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import logging

# 環境変数を読み込み
load_dotenv()

# ログ設定
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


class FullPipeline:
    """フルパイプライン実行クラス"""
    
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
            # 各モジュールを初期化
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
            # 接続テスト
            if not self.sheets_client.test_connection():
                logger.warning("⚠️ Google Sheets接続失敗、スキップします")
                return True
            
            # 新規ログ作成
            execution_id = self.sheets_client.create_execution_log()
            if execution_id:
                self.results["execution_id"] = execution_id
                logger.info(f"✅ 実行ログ作成: {execution_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sheets行作成エラー: {e}")
            return False
    
    async def step_03_collect_information(self):
        """ステップ3: 情報収集"""
        print("\n" + "=" * 80)
        print("📋 ステップ3: 情報収集（Claude API）")
        print("=" * 80)
        
        try:
            # モックデータを使用（実際のweb_searchは時間がかかるため）
            topics_data = {
                "topics": [
                    {
                        "title_ja": "AI駆動の個人開発ツールが月収10万ドルを達成",
                        "title_en": "AI-Powered Indie Dev Tool Hits $100K MRR",
                        "summary": "1人の開発者が作ったAIコード補完ツールが、わずか8ヶ月で月間収益10万ドルを達成。ニッチな市場を見つけ、コミュニティとの対話を重視した成長戦略が功を奏した。",
                        "url": "https://www.indiehackers.com/example1",
                        "category": "個人開発",
                        "source": "Indie Hackers"
                    },
                    {
                        "title_ja": "新しいAI動画編集ツールがProduct Huntで1位獲得",
                        "title_en": "New AI Video Editor Takes #1 on Product Hunt",
                        "summary": "わずか3ヶ月で開発されたAI動画編集ツールがProduct Huntで1位を獲得。自然言語で指示するだけで動画編集ができる革新的なインターフェースが評価された。",
                        "url": "https://www.producthunt.com/example2",
                        "category": "AI",
                        "source": "Product Hunt"
                    }
                ]
            }
            
            self.results["topics_data"] = topics_data
            logger.info(f"✅ トピック収集完了: {len(topics_data['topics'])}件")
            
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
            # テスト用のモック台本を使用
            script_content = {
                "full_script": """[Aさん] こんにちは、今日は個人開発について話します。
[Bさん] 面白そうですね、どんな内容ですか？
[Aさん] AIを活用した動画自動生成システムについてです。個人開発者が8ヶ月で月収10万ドルを達成した事例があるんです。
[Bさん] それは驚きですね。どんな戦略だったんですか？
[Aさん] ニッチな市場を見つけて、コミュニティとの対話を重視した成長戦略が功を奏しました。
[Bさん] なるほど、具体的にどうやってニッチ市場を見つけたんでしょうか？
[Aさん] まず、大手が見落としている課題を特定して、そこにフォーカスしました。
[Bさん] コミュニティ対話は、具体的にどんなことをしたんですか？
[Aさん] 48時間以内のフィードバック対応を徹底して、ユーザーの声を積極的に取り入れました。
[Bさん] それは大変そうですね。でも効果は絶大だったわけですね。""",
                "sections": [
                    {
                        "title": "オープニング",
                        "content": "[Aさん] こんにちは、今日は個人開発について話します。\n[Bさん] 面白そうですね、どんな内容ですか？"
                    }
                ]
            }
            
            self.results["script_content"] = script_content
            logger.info(f"✅ 台本生成完了: {len(script_content.get('full_script', ''))}文字")
            
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
            execution_id = self.results.get("execution_id", "test_pipeline")
            
            # 音声生成
            audio_result = await self.audio_generator.generate_full_audio(
                script_content,
                Path("temp/test_audio"),
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
            
            # 字幕生成
            subtitle_data = await self.subtitle_generator.generate_subtitles(
                audio_path,
                script_content
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
            
            # 動画生成
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
            
            # メタデータ生成
            metadata = await self.claude_client.generate_youtube_metadata(
                script_content,
                topics_data
            )
            
            # コメント生成
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
            
            # サムネイル生成
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
    
    async def run_all_steps(self):
        """全ステップを実行"""
        print("\n" + "=" * 80)
        print("🎬 YouTube AI Podcast - フルパイプライン実行（ステップ1-9）")
        print("=" * 80)
        
        steps = [
            ("1. 初期化", self.step_01_initialize),
            ("2. Sheets新規行作成", self.step_02_create_sheet_row),
            ("3. 情報収集", self.step_03_collect_information),
            ("4. 台本生成", self.step_04_generate_script),
            ("5. 音声生成", self.step_05_generate_audio),
            ("6. 字幕生成", self.step_06_generate_subtitles),
            ("7. 動画生成", self.step_07_generate_video),
            ("8. メタデータ生成", self.step_08_generate_metadata),
            ("9. サムネイル生成", self.step_09_generate_thumbnail),
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
        
        # 結果サマリー
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """実行結果のサマリーを表示"""
        execution_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("🎉 全ステップ完了！")
        print("=" * 80)
        
        print(f"\n⏱️  処理時間: {execution_time:.1f}秒")
        
        print("\n📁 生成されたファイル:")
        if "audio_path" in self.results:
            print(f"   音声: {self.results['audio_path']}")
        if "video_path" in self.results:
            print(f"   動画: {self.results['video_path']}")
            print(f"   サイズ: {os.path.getsize(self.results['video_path']) / 1024 / 1024:.1f}MB")
        if "thumbnail_path" in self.results:
            print(f"   サムネイル: {self.results['thumbnail_path']}")
            print(f"   サイズ: {os.path.getsize(self.results['thumbnail_path']) / 1024:.1f}KB")
        
        print("\n📊 メタデータ:")
        if "metadata" in self.results:
            metadata = self.results["metadata"]
            print(f"   タイトル: {metadata.get('title', 'N/A')}")
            print(f"   タグ: {len(metadata.get('tags', []))}個")
            print(f"   サムネイルテキスト: {metadata.get('thumbnail_text', 'N/A')}")
        
        if "comment" in self.results:
            print(f"\n💬 コメント:")
            print(f"   {self.results['comment'][:100]}...")
        
        print("\n" + "=" * 80)
        print("🎬 動画を確認:")
        if "video_path" in self.results:
            print(f"   open {self.results['video_path']}")
        print("\n🎨 サムネイルを確認:")
        if "thumbnail_path" in self.results:
            print(f"   open {self.results['thumbnail_path']}")
        print("=" * 80 + "\n")


async def main():
    """メイン関数"""
    pipeline = FullPipeline()
    success = await pipeline.run_all_steps()
    
    if not success:
        print("\n❌ パイプライン実行に失敗しました")
        exit(1)
    
    print("\n✅ パイプライン実行に成功しました")


if __name__ == "__main__":
    asyncio.run(main())

