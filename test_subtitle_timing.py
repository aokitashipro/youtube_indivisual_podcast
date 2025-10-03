"""
字幕タイミング調整テスト

既存の音声ファイルを使用して、字幕のタイミングを調整したテスト動画を生成します。
"""
import asyncio
import sys
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
from modules.subtitle_generator import SubtitleGenerator
from modules.video_generator import VideoGenerator


async def main():
    """タイミング調整テスト"""
    
    # コマンドライン引数からオフセットを取得（デフォルト: 0.5秒）
    time_offset = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    
    print("\n" + "=" * 80)
    print(f"⏰ 字幕タイミング調整テスト（オフセット: {time_offset:+.2f}秒）")
    print("=" * 80)
    
    try:
        settings = Settings()
        subtitle_generator = SubtitleGenerator(settings)
        video_generator = VideoGenerator(settings)
        
        # 最新の音声ファイルを使用
        audio_path = "temp/test_audio/podcast_20251003_007.wav"
        
        if not Path(audio_path).exists():
            logger.error(f"❌ 音声ファイルが見つかりません: {audio_path}")
            print("\n先に test_full_pipeline_steps1_9.py を実行して音声ファイルを生成してください")
            return
        
        # モック台本
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
[Bさん] それは大変そうですね。でも効果は絶大だったわけですね。"""
        }
        
        # タイミングオフセットを適用して字幕を生成
        print(f"\n📝 字幕生成中（オフセット: {time_offset:+.2f}秒）...")
        subtitle_data = await subtitle_generator.generate_subtitles(
            audio_path,
            script_content,
            time_offset=time_offset
        )
        
        # 動画を生成
        print(f"\n🎬 動画生成中...")
        video_path = await video_generator.generate_video_with_subtitles(
            audio_path,
            subtitle_data.get("subtitles", []),
            background_image_path="assets/images/background.png"
        )
        
        print("\n" + "=" * 80)
        print("✅ テスト完了！")
        print("=" * 80)
        print(f"\n生成された動画: {video_path}")
        print(f"オフセット: {time_offset:+.2f}秒")
        print(f"\n動画を確認:")
        print(f"  open {video_path}")
        print("\n" + "=" * 80)
        print("💡 オフセット調整方法:")
        print("  - 字幕が早すぎる場合（音声より先に出る）: 正の値を増やす")
        print("    例: python test_subtitle_timing.py 1.0")
        print("  - 字幕が遅すぎる場合（音声より後に出る）: 負の値を使う")
        print("    例: python test_subtitle_timing.py -0.5")
        print("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

