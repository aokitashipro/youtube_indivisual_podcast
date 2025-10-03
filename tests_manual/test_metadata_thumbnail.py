"""
メタデータとサムネイル生成の統合テスト

ステップ8-9（メタデータ生成、サムネイル生成）をテストします。
"""
import asyncio
import os
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
from modules.claude_client import ClaudeClient
from modules.video_generator import VideoGenerator


async def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎬 メタデータ＆サムネイル生成テスト")
    print("=" * 80 + "\n")
    
    try:
        # 設定を読み込み
        settings = Settings()
        
        # モジュールを初期化
        claude_client = ClaudeClient(settings)
        video_generator = VideoGenerator(settings)
        
        # テスト用の台本データ
        script_data = {
            "full_script": """
[Aさん] こんにちは、今日は個人開発の成功事例について話したいと思います。

[Bさん] 面白そうですね。どんな内容ですか？

[Aさん] AI駆動の個人開発ツールが、わずか8ヶ月で月収10万ドルを達成した事例です。1人の開発者が作ったAIコード補完ツールが大成功を収めています。

[Bさん] 10万ドル！それは凄いですね。でも本当にそんなに稼げるんですか？

[Aさん] はい、ニッチな市場を見つけて、コミュニティとの対話を重視した成長戦略が功を奏したようです。初期投資はほぼゼロで、マーケティングもSNSとコミュニティ活動のみです。

[Bさん] なるほど。でも競合も多そうですよね？

[Aさん] その通りです。しかし、大手が見落としていた特定の開発者層にフォーカスしたこと、無料プランで先にコミュニティを作ったこと、48時間以内にフィードバックを実装する超高速開発サイクル、これらが成功要因です。
""",
            "dialogue": [
                {"speaker": "A", "text": "こんにちは、今日は個人開発の成功事例について話したいと思います。"},
                {"speaker": "B", "text": "面白そうですね。どんな内容ですか？"}
            ]
        }
        
        # テスト用のトピックデータ
        topics_data = {
            "topics": [
                {
                    "title": "AI駆動の個人開発ツールが月収10万ドルを達成",
                    "summary": "1人の開発者が作ったAIコード補完ツールが、わずか8ヶ月で月間収益10万ドルを達成",
                    "url": "https://www.indiehackers.com/example",
                    "category": "個人開発/AI"
                }
            ]
        }
        
        # ステップ1: YouTube用メタデータ生成
        logger.info("=" * 80)
        logger.info("📋 ステップ8: YouTube用メタデータを生成中...")
        logger.info("=" * 80)
        
        metadata = await claude_client.generate_youtube_metadata(
            script_content=script_data,
            topics_data=topics_data
        )
        
        print("\n📋 生成されたメタデータ:")
        print("-" * 80)
        print(f"タイトル: {metadata.get('title', 'N/A')}")
        print(f"\n説明文:\n{metadata.get('description', 'N/A')[:200]}...")
        print(f"\nタグ: {', '.join(metadata.get('tags', []))}")
        print(f"\nサムネイル用テキスト: {metadata.get('thumbnail_text', 'N/A')}")
        print("-" * 80)
        
        # ステップ2: コメント生成
        logger.info("\n" + "=" * 80)
        logger.info("💬 コメントを生成中（毒舌設定）...")
        logger.info("=" * 80)
        
        comment = await claude_client.generate_comment(script_content=script_data)
        
        print(f"\n💬 生成されたコメント:")
        print("-" * 80)
        print(comment)
        print("-" * 80)
        
        # ステップ3: サムネイル生成
        logger.info("\n" + "=" * 80)
        logger.info("🎨 ステップ9: サムネイルを生成中...")
        logger.info("=" * 80)
        
        background_path = "assets/images/background.png"
        
        thumbnail_path = await video_generator.generate_thumbnail(
            metadata=metadata,
            background_path=background_path,
            save_json=True
        )
        
        # 結果の表示
        print("\n" + "=" * 80)
        print("🎉 テスト完了！")
        print("=" * 80)
        print(f"\n✅ 生成されたファイル:")
        print(f"   サムネイル: {thumbnail_path}")
        
        # サムネイルのファイルサイズを確認
        if os.path.exists(thumbnail_path):
            size_kb = os.path.getsize(thumbnail_path) / 1024
            print(f"   サイズ: {size_kb:.1f}KB")
        
        print(f"\n💡 サムネイルを確認:")
        print(f"   open {thumbnail_path}")
        
        print(f"\n📝 テキストを編集して再生成する場合:")
        print(f"   1. JSONファイルを編集: {thumbnail_path.replace('.png', '.json')}")
        print(f"   2. スクリプトを実行: python regenerate_thumbnail.py")
        
        print("\n" + "=" * 80 + "\n")
        
        # メタデータをJSONとして保存（参照用）
        metadata_path = Path("output") / f"metadata_{Path(thumbnail_path).stem}.json"
        full_metadata = {
            "metadata": metadata,
            "comment": comment,
            "thumbnail_path": thumbnail_path,
            "created_at": Path(thumbnail_path).stem.replace('thumbnail_', '')
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 メタデータを保存: {metadata_path}")
        
    except Exception as e:
        logger.error(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # JSONファイルパスが指定された場合
        json_path = sys.argv[1]
        asyncio.run(regenerate_thumbnail_from_json(json_path))
    else:
        # 通常のテスト実行
        asyncio.run(main())

