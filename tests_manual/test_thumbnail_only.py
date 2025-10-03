"""
サムネイルのみのテスト

Claude API不要で、サムネイル生成だけをテストします。
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
from modules.video_generator import VideoGenerator


async def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎨 サムネイル生成テスト（配置確認）")
    print("=" * 80 + "\n")
    
    try:
        # 設定を読み込み
        settings = Settings()
        video_generator = VideoGenerator(settings)
        
        # テスト用のメタデータ
        metadata = {
            "title": "テスト動画タイトル",
            "thumbnail_text": "月収1500万円の秘密"
        }
        
        background_path = "assets/images/background.png"
        
        logger.info("🎨 サムネイルを生成中...")
        logger.info(f"   テキスト: {metadata['thumbnail_text']}")
        logger.info(f"   背景: {background_path}")
        
        thumbnail_path = await video_generator.generate_thumbnail(
            metadata=metadata,
            background_path=background_path,
            save_json=True
        )
        
        print(f"\n✅ サムネイル生成完了！")
        print(f"   ファイル: {thumbnail_path}")
        
        if os.path.exists(thumbnail_path):
            size_kb = os.path.getsize(thumbnail_path) / 1024
            print(f"   サイズ: {size_kb:.1f}KB")
        
        print(f"\n💡 サムネイルを確認:")
        print(f"   open {thumbnail_path}")
        print("\n" + "=" * 80 + "\n")
        
        # 自動で開く
        os.system(f"open {thumbnail_path}")
        
    except Exception as e:
        logger.error(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

