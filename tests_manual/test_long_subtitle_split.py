"""
長い字幕の分割テスト

1つのセリフが3行を超える場合の字幕分割機能をテストします。
修正した「最後のセグメントは元の終了時刻に合わせる」処理を確認します。
"""
import asyncio
import os
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
from modules.gemini_audio_generator import GeminiAudioGenerator
from modules.video_generator import VideoGenerator
from modules.subtitle_generator import SubtitleGenerator


async def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎬 長い字幕の分割テスト（3行超えの字幕を自動分割）")
    print("=" * 80 + "\n")
    
    try:
        settings = Settings()
        audio_generator = GeminiAudioGenerator(settings)
        subtitle_generator = SubtitleGenerator(settings)
        video_generator = VideoGenerator(settings)
        
        background_path = "/Users/a-aoki/indivisual/youtube-ai/assets/images/background.png"
        
        # 非常に長いセリフの台本（確実に4行以上に分割される）
        dialogue_list = [
            {
                "speaker": "A",
                "text": "こんにちは、今日は個人開発について話します。"
            },
            {
                "speaker": "B",
                "text": "面白そうですね、どんな内容ですか？具体的にどのような技術を使っているのでしょうか？また、開発期間はどれくらいかかりましたか？費用面での課題はありましたか？そして、ユーザーからの反応はどうでしたか？マーケティング戦略についても教えてください。収益化の見通しは立っていますか？今後の展開についても興味があります。どのような機能を追加する予定ですか？"
            },
            {
                "speaker": "A",
                "text": "AIを活用した動画自動生成システムです。非常に複雑な処理を行っています。"
            }
        ]
        
        full_script = ""
        for item in dialogue_list:
            speaker_name = "Aさん" if item["speaker"] == "A" else "Bさん"
            full_script += f"[{speaker_name}] {item['text']}\n"
        
        script_data = {
            "dialogue": dialogue_list,
            "full_script": full_script.strip()
        }
        
        logger.info("📝 テスト台本（2番目のセリフが長い）:")
        for i, item in enumerate(dialogue_list, 1):
            logger.info(f"  {i}. {item['speaker']}: {item['text'][:50]}{'...' if len(item['text']) > 50 else ''}")
        
        print("\n" + "=" * 80)
        print("⚠️  重要: 2番目のセリフ（Bさん）が3行を超えて分割されることを確認")
        print("=" * 80 + "\n")
        
        # 音声生成
        logger.info("=" * 80)
        logger.info("🎤 テスト音声を生成中...")
        logger.info("=" * 80)
        
        output_dir = Path("temp/test_audio_long")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result = await audio_generator.generate_full_audio(
            script_data,
            output_dir,
            execution_id
        )
        
        if not result or not result.get("audio_file"):
            logger.error("❌ 音声生成に失敗しました")
            return
        
        audio_path = str(result["audio_file"])
        audio_size = os.path.getsize(audio_path) / 1024
        logger.info(f"✅ 音声生成完了: {audio_path} ({audio_size:.1f}KB)")
        
        # 字幕生成
        logger.info("=" * 80)
        logger.info("💬 字幕データを生成中（ElevenLabs STT + 分割処理）...")
        logger.info("=" * 80)
        
        subtitle_data = await subtitle_generator.generate_subtitles(
            audio_path=audio_path,
            script_content=script_data
        )
        
        logger.info(f"✅ 字幕生成完了: {subtitle_data['total_count']}個のセグメント")
        
        # 字幕の詳細を表示
        print("\n" + "=" * 80)
        print("📊 生成された字幕の詳細:")
        print("=" * 80)
        for i, subtitle in enumerate(subtitle_data['subtitles'], 1):
            duration = subtitle['end'] - subtitle['start']
            print(f"\n字幕 {i}/{subtitle_data['total_count']}:")
            print(f"  時間: {subtitle['start']:.2f}s - {subtitle['end']:.2f}s ({duration:.2f}秒)")
            print(f"  話者: {subtitle.get('speaker', 'N/A')}さん")
            print(f"  内容: {subtitle['text'][:60]}{'...' if len(subtitle['text']) > 60 else ''}")
            print(f"  文字数: {len(subtitle['text'])}文字")
        
        # 動画生成
        logger.info("\n" + "=" * 80)
        logger.info("🎬 字幕付き動画を生成中...")
        logger.info("=" * 80)
        
        video_path = await video_generator.generate_video_with_subtitles(
            audio_path=audio_path,
            subtitle_data=subtitle_data['subtitles'],
            background_image_path=background_path
        )
        
        if os.path.exists(video_path):
            video_size = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"📊 動画ファイルサイズ: {video_size:.1f}MB")
        
        print("\n" + "=" * 80)
        print("🎉 テスト完了！")
        print("=" * 80)
        print(f"\n✅ 生成された動画: {video_path}")
        print(f"\n📝 確認事項:")
        print(f"   1. 2番目の長いセリフが複数の字幕に分割されているか")
        print(f"   2. 分割された字幕が正しく切り替わるか（4行目以降も）")
        print(f"   3. タイムスタンプが重複せず、連続しているか")
        print(f"   4. 最後のセグメントの終了時刻が元の時刻に合っているか")
        print(f"\n💡 動画を確認してください:")
        print(f"   open {video_path}")
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

