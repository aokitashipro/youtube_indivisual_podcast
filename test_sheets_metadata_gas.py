"""
Google Sheets（GAS経由）へのメタデータ保存テスト

GAS Web APIを使用してメタデータを保存します。
"""
import asyncio
import os
import requests
import json
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
from modules.sheets_client import SheetsClient


async def test_gas_metadata_save():
    """GAS経由でメタデータを保存"""
    print("\n" + "=" * 80)
    print("📊 Google Sheets（GAS）メタデータ保存テスト")
    print("=" * 80 + "\n")
    
    try:
        # 設定を読み込み
        settings = Settings()
        
        # GAS Web App URLが設定されているか確認
        if not settings.GAS_WEB_APP_URL:
            logger.error("⚠️ GAS_WEB_APP_URLが設定されていません")
            print("\n.envファイルにGAS_WEB_APP_URLを設定してください")
            return
        
        logger.info(f"✅ GAS Web App URL: {settings.GAS_WEB_APP_URL[:50]}...")
        
        # SheetsClientを初期化
        sheets_client = SheetsClient(settings)
        
        # 接続テスト
        logger.info("🔍 GAS接続テスト中...")
        if not sheets_client.test_connection():
            logger.error("❌ GAS接続失敗")
            return
        
        # テスト用のメタデータ
        metadata = {
            "title": "【テスト】AI動画自動生成システムの実装完了",
            "description": """
【実装内容】
✅ ElevenLabs STTで字幕生成
✅ Claude APIでメタデータ生成
✅ サムネイル自動生成
✅ Google Sheets連携

【詳細】
本システムは完全自動化された動画生成パイプラインです。

出典：https://zenn.dev/xtm_blog/articles/da1eba90525f91
""".strip(),
            "tags": ["AI", "動画生成", "自動化", "Claude", "Python", "YouTube"],
            "thumbnail_text": "AI動画生成完成"
        }
        
        comment = "テスト実行です。メタデータとサムネイルの自動生成が完了しました！"
        
        # GAS Web APIでメタデータを送信
        logger.info("\n📤 GAS Web APIにメタデータを送信中...")
        
        payload = {
            'action': 'save_metadata',
            'metadata': metadata,
            'comment': comment,
            'video_path': 'output/test_video.mp4',
            'audio_path': 'temp/test_audio.wav',
            'thumbnail_path': 'output/test_thumbnail.png',
            'processing_time': '45.5秒'
        }
        
        response = requests.post(
            settings.GAS_WEB_APP_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info(f"✅ メタデータ保存成功！")
                logger.info(f"   行番号: {result.get('row_number', 'N/A')}")
                print(f"\n✅ Google Sheetsに保存されました！")
                print(f"   タイトル: {metadata['title']}")
                print(f"   サムネイルテキスト: {metadata['thumbnail_text']}")
                print(f"   コメント: {comment}")
            else:
                logger.error(f"❌ 保存失敗: {result.get('error')}")
        else:
            logger.error(f"❌ HTTPエラー: {response.status_code}")
            logger.error(f"   レスポンス: {response.text}")
        
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_gas_metadata_save())

