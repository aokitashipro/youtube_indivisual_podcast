"""
ステップ3-4のテストスクリプト（情報収集→台本生成）

このスクリプトは、Google Sheetsを使わずにステップ3-4のみをテストします。
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.claude_client import ClaudeClient
from utils.logger import setup_logger
from utils.error_handler import ErrorHandler, RetryHandler
from utils.timer import Timer, timer_context

# 環境変数を読み込み
load_dotenv()


async def test_steps_3_and_4():
    """ステップ3-4のテスト実行"""
    
    # ロガーを初期化
    logger = setup_logger("INFO", log_file=f"logs/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logger.info("\n" + "=" * 80)
    logger.info("🧪 ステップ3-4のテストを開始します")
    logger.info("=" * 80 + "\n")
    
    try:
        # 設定を初期化
        settings = Settings()
        logger.info(f"✅ 設定を読み込みました")
        logger.info(f"   - Anthropic API Key: {'設定済み' if settings.ANTHROPIC_API_KEY else '❌ 未設定'}")
        
        # Claude Clientを初期化
        claude_client = ClaudeClient(settings)
        logger.info(f"✅ Claude Clientを初期化しました")
        
        # エラーハンドラーとリトライハンドラーを初期化
        error_handler = ErrorHandler(logger)
        retry_handler = RetryHandler(logger, max_retries=3, delay=2.0)
        
        # タイマーを開始
        total_timer = Timer("全体処理", logger)
        total_timer.start()
        
        # ステップ3: 情報収集
        logger.info("\n" + "-" * 80)
        logger.info("🔍 ステップ3: 情報収集を開始します")
        logger.info("-" * 80)
        
        with timer_context("ステップ3: 情報収集", logger):
            try:
                topics_data = await retry_handler.retry_async(
                    claude_client.collect_topics_with_web_search
                )
                
                logger.info(f"\n📊 収集したトピック:")
                for i, topic in enumerate(topics_data.get("topics", []), 1):
                    logger.info(f"   {i}. {topic.get('title_ja', 'N/A')}")
                    logger.info(f"      カテゴリ: {topic.get('category', 'N/A')}")
                    logger.info(f"      出典: {topic.get('source', 'N/A')}")
                
                # 結果をJSONファイルに保存
                output_dir = Path("temp")
                output_dir.mkdir(exist_ok=True)
                
                topics_file = output_dir / f"topics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(topics_file, 'w', encoding='utf-8') as f:
                    json.dump(topics_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"\n💾 トピックデータを保存しました: {topics_file}")
                
            except Exception as e:
                error_handler.handle_api_error(e, "Claude API (情報収集)")
                raise
        
        # ステップ4: 台本生成
        logger.info("\n" + "-" * 80)
        logger.info("📝 ステップ4: 台本生成を開始します")
        logger.info("-" * 80)
        
        with timer_context("ステップ4: 台本生成", logger):
            try:
                script_content = await retry_handler.retry_async(
                    claude_client.generate_dialogue_script,
                    topics_data
                )
                
                logger.info(f"\n📄 生成された台本:")
                logger.info(f"   タイトル: {script_content.get('title', 'N/A')}")
                logger.info(f"   文字数: {script_content.get('word_count', 0)}文字")
                logger.info(f"   推定時間: {script_content.get('estimated_duration_seconds', 0)}秒 "
                           f"({script_content.get('estimated_duration_seconds', 0) / 60:.1f}分)")
                logger.info(f"   セクション数: {len(script_content.get('sections', []))}")
                
                # 台本の冒頭を表示
                full_script = script_content.get("full_script", "")
                preview_length = 500
                logger.info(f"\n📖 台本プレビュー（最初の{preview_length}文字）:")
                logger.info("-" * 40)
                logger.info(full_script[:preview_length] + ("..." if len(full_script) > preview_length else ""))
                logger.info("-" * 40)
                
                # 結果をファイルに保存
                script_file = output_dir / f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(script_file, 'w', encoding='utf-8') as f:
                    json.dump(script_content, f, ensure_ascii=False, indent=2)
                
                # 台本のテキストも別途保存
                script_text_file = output_dir / f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(script_text_file, 'w', encoding='utf-8') as f:
                    f.write(f"タイトル: {script_content.get('title', '')}\n")
                    f.write(f"文字数: {script_content.get('word_count', 0)}\n")
                    f.write(f"推定時間: {script_content.get('estimated_duration_seconds', 0) / 60:.1f}分\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(full_script)
                
                logger.info(f"\n💾 台本データを保存しました:")
                logger.info(f"   JSON: {script_file}")
                logger.info(f"   テキスト: {script_text_file}")
                
            except Exception as e:
                error_handler.handle_api_error(e, "Claude API (台本生成)")
                raise
        
        # 全体の処理時間
        total_timer.stop()
        
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ テストが正常に完了しました")
        logger.info(f"   総処理時間: {total_timer.get_duration():.1f}秒 ({total_timer.get_duration() / 60:.1f}分)")
        logger.info("=" * 80 + "\n")
        
        # サマリーを表示
        logger.info("📊 実行サマリー:")
        logger.info(f"   ✅ トピック収集: {topics_data.get('total_count', 0)}件")
        logger.info(f"   ✅ 台本生成: {script_content.get('word_count', 0)}文字")
        logger.info(f"   ✅ 推定動画時間: {script_content.get('estimated_duration_seconds', 0) / 60:.1f}分")
        logger.info(f"\n   📁 出力ファイル:")
        logger.info(f"      - {topics_file}")
        logger.info(f"      - {script_file}")
        logger.info(f"      - {script_text_file}")
        
        return {
            "topics_data": topics_data,
            "script_content": script_content,
            "total_duration": total_timer.get_duration()
        }
        
    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error(f"❌ テストでエラーが発生しました: {e}")
        logger.error("=" * 80 + "\n")
        raise


if __name__ == "__main__":
    print("\n🎬 YouTube AI Podcast - ステップ3-4テスト\n")
    print("このテストでは以下を実行します:")
    print("  1. Claude APIで情報収集（Indie Hackers, Product Hunt, Hacker News）")
    print("  2. 収集したトピックから対談形式の台本を生成")
    print("  3. 結果をtemp/フォルダに保存")
    print("\n必要な環境変数:")
    print("  - ANTHROPIC_API_KEY (必須)")
    print("\n" + "=" * 80 + "\n")
    
    # 実行確認
    try:
        result = asyncio.run(test_steps_3_and_4())
        
        print("\n" + "🎉" * 20)
        print("\n✅ テスト完了！")
        print("\n生成されたファイルを確認してください:")
        print("  - temp/topics_*.json")
        print("  - temp/script_*.json")
        print("  - temp/script_*.txt")
        print("\n" + "🎉" * 20 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        print("\n詳細はログファイル (logs/) を確認してください")
        sys.exit(1)

