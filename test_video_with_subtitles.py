"""
字幕付き動画生成のテストスクリプト

シンプルな台本で動画を生成して、字幕機能をテストします。
"""
import asyncio
import os
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
from modules.gemini_audio_generator import GeminiAudioGenerator
from modules.video_generator import VideoGenerator
from modules.subtitle_generator import SubtitleGenerator


async def generate_test_audio(audio_generator, script_data):
    """テスト用の音声を生成"""
    logger.info("=" * 80)
    logger.info("🎤 テスト音声を生成中...")
    logger.info("=" * 80)
    
    try:
        # 出力ディレクトリを設定
        output_dir = Path("temp/test_audio")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 台本から音声を生成
        from datetime import datetime
        execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result = await audio_generator.generate_full_audio(
            script_data,
            output_dir,
            execution_id
        )
        
        if result and result.get("audio_file"):
            audio_path = str(result["audio_file"])
            logger.info(f"✅ 音声生成完了: {audio_path}")
            return audio_path
        else:
            raise Exception("音声生成に失敗しました")
    except Exception as e:
        logger.error(f"❌ 音声生成エラー: {e}")
        raise


async def generate_test_subtitles(subtitle_generator, audio_path, script_data):
    """テスト用の字幕を生成"""
    logger.info("=" * 80)
    logger.info("💬 字幕データを生成中（ElevenLabs STT）...")
    logger.info("=" * 80)
    
    try:
        subtitle_data = await subtitle_generator.generate_subtitles(
            audio_path=audio_path,
            script_content=script_data
        )
        logger.info(f"✅ 字幕生成完了: {subtitle_data['total_count']}個のセグメント")
        return subtitle_data
    except Exception as e:
        logger.error(f"❌ 字幕生成エラー: {e}")
        raise


async def generate_test_video(video_generator, audio_path, subtitle_data, background_path):
    """テスト用の動画を生成"""
    logger.info("=" * 80)
    logger.info("🎬 字幕付き動画を生成中...")
    logger.info("=" * 80)
    
    try:
        video_path = await video_generator.generate_video_with_subtitles(
            audio_path=audio_path,
            subtitle_data=subtitle_data['subtitles'],
            background_image_path=background_path
        )
        logger.info(f"✅ 動画生成完了: {video_path}")
        return video_path
    except Exception as e:
        logger.error(f"❌ 動画生成エラー: {e}")
        raise


async def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎬 字幕付き動画生成テスト")
    print("=" * 80 + "\n")
    
    try:
        # 設定を読み込み
        settings = Settings()
        
        # モジュールを初期化
        audio_generator = GeminiAudioGenerator(settings)
        subtitle_generator = SubtitleGenerator(settings)
        video_generator = VideoGenerator(settings)
        
        # 背景画像のパスを設定
        background_path = "/Users/a-aoki/indivisual/youtube-ai/assets/images/background.png"
        
        # 背景画像の存在確認
        if not os.path.exists(background_path):
            logger.warning(f"⚠️ 背景画像が見つかりません: {background_path}")
            logger.info("黒背景で動画を生成します")
        else:
            logger.info(f"✅ 背景画像を使用: {background_path}")
        
        # テスト用の台本データ
        dialogue_list = [
            {
                "speaker": "A",
                "text": "こんにちは、今日は個人開発について話します。"
            },
            {
                "speaker": "B",
                "text": "面白そうですね、どんな内容ですか？"
            },
            {
                "speaker": "A",
                "text": "AIを活用した動画自動生成システムです。"
            },
            {
                "speaker": "B",
                "text": "それは画期的ですね！"
            }
        ]
        
        # full_script形式に変換
        full_script = ""
        for item in dialogue_list:
            speaker_name = "Aさん" if item["speaker"] == "A" else "Bさん"
            full_script += f"[{speaker_name}] {item['text']}\n"
        
        script_data = {
            "dialogue": dialogue_list,
            "full_script": full_script.strip()
        }
        
        logger.info("📝 テスト台本:")
        for item in dialogue_list:
            logger.info(f"  {item['speaker']}: {item['text']}")
        
        # ステップ1: 音声生成
        audio_path = await generate_test_audio(audio_generator, script_data)
        
        # 音声ファイルの確認
        if not os.path.exists(audio_path):
            logger.error(f"❌ 音声ファイルが見つかりません: {audio_path}")
            return
        
        audio_size = os.path.getsize(audio_path) / 1024
        logger.info(f"📊 音声ファイルサイズ: {audio_size:.1f}KB")
        
        # ステップ2: 字幕生成（ElevenLabs STT）
        subtitle_data = await generate_test_subtitles(
            subtitle_generator,
            audio_path,
            script_data
        )
        
        # ステップ3: 動画生成
        video_path = await generate_test_video(
            video_generator,
            audio_path,
            subtitle_data,
            background_path
        )
        
        # 動画ファイルの確認
        if os.path.exists(video_path):
            video_size = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"📊 動画ファイルサイズ: {video_size:.1f}MB")
        
        print("\n" + "=" * 80)
        print("🎉 テスト完了！")
        print("=" * 80)
        print(f"\n✅ 生成された動画: {video_path}")
        print(f"\n💡 動画を確認してください:")
        print(f"   open {video_path}")
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

