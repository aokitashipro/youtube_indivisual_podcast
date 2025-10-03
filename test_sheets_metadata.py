"""
Google Sheetsへのメタデータ保存テスト

メタデータとコメントをスプレッドシートに保存する機能をテストします。
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
from modules.sheets_manager import SheetsManager


async def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("📊 Google Sheetsメタデータ保存テスト")
    print("=" * 80 + "\n")
    
    try:
        # 設定を読み込み
        settings = Settings()
        
        # Google Sheets IDが設定されているか確認
        if not settings.GOOGLE_SHEETS_ID:
            logger.warning("⚠️ GOOGLE_SHEETS_IDが設定されていません")
            print("\n.envファイルにGOOGLE_SHEETS_IDを設定してください")
            return
        
        # SheetsManagerを初期化
        sheets_manager = SheetsManager(settings)
        
        # テスト用のメタデータ
        metadata = {
            "title": "【テスト】AIで動画自動生成システムを作ってみた",
            "description": """
【主なポイント】
✅ Claude APIで台本生成
✅ Gemini APIで音声生成
✅ ElevenLabs STTで字幕生成
✅ MoviePyで動画生成

【詳細】
本動画では、AIを活用した動画自動生成システムの構築方法を解説します。

出典：https://zenn.dev/xtm_blog/articles/da1eba90525f91
""".strip(),
            "tags": ["AI", "動画生成", "自動化", "Claude", "Python", "個人開発"],
            "thumbnail_text": "AI動画自動生成"
        }
        
        # テスト用のコメント
        comment = "自動生成された動画のテストです。実際の運用ではClaudeが毒舌コメントを生成します！"
        
        # ファイルパス（テスト用）
        video_path = "output/test_video.mp4"
        audio_path = "output/test_audio.wav"
        thumbnail_path = "output/test_thumbnail.png"
        execution_time = 45.5  # テスト用の処理時間
        
        logger.info("📋 メタデータをGoogle Sheetsに保存中...")
        logger.info(f"   スプレッドシートID: {settings.GOOGLE_SHEETS_ID[:20]}...")
        logger.info(f"   タイトル: {metadata['title']}")
        
        # メタデータを追加
        row_number = await sheets_manager.append_metadata_row(
            metadata=metadata,
            comment=comment,
            video_path=video_path,
            audio_path=audio_path,
            thumbnail_path=thumbnail_path,
            execution_time=execution_time
        )
        
        print(f"\n✅ メタデータの保存成功！")
        print(f"   行番号: {row_number}")
        print(f"   タイトル: {metadata['title']}")
        print(f"   タグ数: {len(metadata['tags'])}")
        print(f"   コメント: {comment[:50]}...")
        
        # テスト: Drive URLを更新
        logger.info("\n📤 Drive URLを更新中（テスト）...")
        
        await sheets_manager.update_row_with_urls(
            row_number=row_number,
            video_url="https://drive.google.com/file/d/test_video_id",
            audio_url="https://drive.google.com/file/d/test_audio_id",
            thumbnail_url="https://drive.google.com/file/d/test_thumbnail_id"
        )
        
        print(f"\n✅ Drive URLの更新成功！")
        print(f"\n💡 Google Sheetsを確認:")
        print(f"   https://docs.google.com/spreadsheets/d/{settings.GOOGLE_SHEETS_ID}")
        
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

