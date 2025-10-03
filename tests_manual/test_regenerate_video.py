"""
既存の台本と音声から動画を再生成するテスト

修正した字幕生成機能を使って、既存のリサーチ結果から動画を生成します。
"""
import asyncio
import json
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
    """既存データから動画を再生成"""
    
    print("\n" + "=" * 80)
    print("🎬 既存リサーチデータから動画を再生成")
    print("=" * 80 + "\n")
    
    try:
        settings = Settings()
        subtitle_generator = SubtitleGenerator(settings)
        video_generator = VideoGenerator(settings)
        
        # 台本データを読み込み
        script_path = Path("temp/script_20251002_210149.json")
        logger.info(f"📝 台本を読み込み: {script_path}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        
        logger.info(f"   タイトル: {script_data['title']}")
        logger.info(f"   文字数: {script_data['word_count']}文字")
        logger.info(f"   推定時間: {script_data['estimated_duration_seconds']/60:.1f}分")
        
        # 音声ファイルのパス
        audio_path = "temp/real_audio/podcast_20251003_014.wav"
        
        if not Path(audio_path).exists():
            logger.error(f"❌ 音声ファイルが見つかりません: {audio_path}")
            return
        
        audio_size = Path(audio_path).stat().st_size / (1024 * 1024)
        logger.info(f"🎤 音声ファイル: {audio_path} ({audio_size:.1f}MB)")
        
        # 字幕を生成（修正版の字幕生成機能を使用）
        print("\n" + "=" * 80)
        print("💬 字幕データを生成中（修正版・ElevenLabs STT）...")
        print("=" * 80)
        
        subtitle_data = await subtitle_generator.generate_subtitles(
            audio_path=audio_path,
            script_content=script_data,
            time_offset=0.0  # 必要に応じて調整
        )
        
        logger.info(f"✅ 字幕生成完了: {subtitle_data['total_count']}個のセグメント")
        logger.info(f"   総時間: {subtitle_data['total_duration']:.1f}秒 ({subtitle_data['total_duration']/60:.1f}分)")
        
        # 動画を生成
        print("\n" + "=" * 80)
        print("🎬 字幕付き動画を生成中...")
        print("=" * 80)
        
        video_path = await video_generator.generate_video_with_subtitles(
            audio_path=audio_path,
            subtitle_data=subtitle_data['subtitles'],
            background_image_path="assets/images/background.png"
        )
        
        # 動画ファイルの確認
        if Path(video_path).exists():
            video_size = Path(video_path).stat().st_size / (1024 * 1024)
            logger.info(f"📊 動画ファイルサイズ: {video_size:.1f}MB")
        
        print("\n" + "=" * 80)
        print("🎉 動画生成完了！")
        print("=" * 80)
        print(f"\n✅ 生成された動画: {video_path}")
        print(f"\n📝 台本タイトル: {script_data['title']}")
        print(f"💬 字幕セグメント: {subtitle_data['total_count']}個")
        print(f"⏱️  動画時間: {subtitle_data['total_duration']/60:.1f}分")
        print(f"\n💡 動画を確認してください:")
        print(f"   open {video_path}")
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

