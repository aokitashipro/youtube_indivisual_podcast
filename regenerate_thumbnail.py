"""
サムネイル再生成スクリプト

既存のサムネイルJSONを編集して、サムネイルだけを再生成します。
自動生成後に手動でテキストを調整したい場合に使用します。

使い方:
1. output/thumbnail_YYYYMMDD_HHMMSS.json を編集
2. このスクリプトを実行
3. 新しいサムネイルが output/thumbnail_YYYYMMDD_HHMMSS_v2.png として生成される
"""
import asyncio
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

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


async def regenerate_thumbnail_from_json(json_path: str):
    """
    JSONファイルからサムネイルを再生成
    
    Args:
        json_path: サムネイル設定のJSONファイルパス
    """
    try:
        print("\n" + "=" * 80)
        print("🎨 サムネイル再生成")
        print("=" * 80 + "\n")
        
        # JSONファイルを読み込み
        if not os.path.exists(json_path):
            logger.error(f"❌ JSONファイルが見つかりません: {json_path}")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            thumbnail_data = json.load(f)
        
        logger.info(f"📄 設定ファイル読み込み: {json_path}")
        logger.info(f"   現在のテキスト: {thumbnail_data.get('text', 'N/A')}")
        
        # ユーザーに確認
        print(f"\n現在のサムネイルテキスト:")
        print(f"  「{thumbnail_data.get('text', '')}」")
        print(f"\nこのテキストでサムネイルを再生成しますか？")
        print(f"  y: そのまま再生成")
        print(f"  e: テキストを編集して再生成")
        print(f"  n: キャンセル")
        
        choice = input("\n選択 (y/e/n): ").lower()
        
        if choice == 'n':
            logger.info("キャンセルしました")
            return
        elif choice == 'e':
            new_text = input("\n新しいテキストを入力: ")
            if new_text:
                thumbnail_data['text'] = new_text
                # JSONも更新
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(thumbnail_data, f, ensure_ascii=False, indent=2)
                logger.info(f"✅ テキストを更新しました: {new_text}")
        
        # 設定を読み込み
        settings = Settings()
        video_generator = VideoGenerator(settings)
        
        # メタデータを構築
        metadata = {
            "title": thumbnail_data.get('title', ''),
            "thumbnail_text": thumbnail_data.get('text', '')
        }
        
        # サムネイルを再生成
        logger.info("🎨 サムネイルを再生成中...")
        
        thumbnail_path = await video_generator.generate_thumbnail(
            metadata=metadata,
            thumbnail_text=thumbnail_data.get('text'),
            background_path=thumbnail_data.get('background_path'),
            save_json=False  # 新しいJSONは作らない
        )
        
        print(f"\n✅ サムネイル再生成完了！")
        print(f"   {thumbnail_path}")
        print(f"\n💡 サムネイルを確認:")
        print(f"   open {thumbnail_path}")
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"❌ サムネイル再生成エラー: {e}")
        import traceback
        traceback.print_exc()


async def list_available_thumbnails():
    """利用可能なサムネイルJSONファイルを一覧表示"""
    output_dir = Path("output")
    json_files = sorted(output_dir.glob("thumbnail_*.json"), reverse=True)
    
    if not json_files:
        logger.warning("⚠️ サムネイルJSONファイルが見つかりません")
        return None
    
    print("\n利用可能なサムネイル設定:")
    print("-" * 80)
    for i, json_file in enumerate(json_files[:10], 1):  # 最新10件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = data.get('text', 'N/A')
        created = data.get('created_at', 'N/A')
        print(f"{i}. {json_file.name}")
        print(f"   作成: {created}")
        print(f"   テキスト: {text[:50]}...")
        print()
    
    choice = input("番号を選択（Enterで最新、qでキャンセル）: ")
    
    if choice.lower() == 'q':
        return None
    
    if choice.strip() == '':
        return str(json_files[0])
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(json_files):
            return str(json_files[idx])
    except:
        pass
    
    logger.error("無効な選択です")
    return None


async def main():
    """メイン処理"""
    try:
        # 利用可能なサムネイルJSONを表示
        json_path = await list_available_thumbnails()
        
        if json_path:
            await regenerate_thumbnail_from_json(json_path)
        else:
            logger.info("処理をキャンセルしました")
    
    except KeyboardInterrupt:
        logger.info("\n処理を中断しました")
    except Exception as e:
        logger.error(f"エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

