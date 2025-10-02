"""
Google Sheets連携付きパイプライン実行スクリプト

元記事の処理フローを完全再現：
1. 動的プロンプト生成 → スプレッドシート保存
2. プロンプトA実行（情報収集） → 検索結果をスプレッドシート保存
3. プロンプトB実行（台本生成） → 生成台本をスプレッドシート保存
4. ステータス更新 → 完了/エラー
"""
import sys
from pathlib import Path
from datetime import datetime
import json

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.sheets_client import SheetsClient
from modules.claude_client import ClaudeClient
from utils.logger import setup_logger
from utils.timer import Timer

# 環境変数を読み込み
load_dotenv()


def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎬 YouTube AIポッドキャスト生成パイプライン（Google Sheets連携）")
    print("=" * 80 + "\n")
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    # 必須設定のチェック
    if not settings.ANTHROPIC_API_KEY:
        logger.error("❌ ANTHROPIC_API_KEYが設定されていません")
        return
    
    if not settings.GAS_WEB_APP_URL:
        logger.error("❌ GAS_WEB_APP_URLが設定されていません")
        logger.info("Google Sheets連携なしで実行する場合は test_step_3_4.py を使用してください")
        return
    
    # クライアントを初期化
    sheets_client = SheetsClient(settings)
    claude_client = ClaudeClient(settings)
    
    # 全体タイマー開始
    total_timer = Timer("全体処理", logger)
    total_timer.start()
    
    execution_id = None
    
    try:
        # ====================================================================
        # ステップ1: Google Sheets接続テスト
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("ステップ1: Google Sheets接続テスト")
        logger.info("=" * 80)
        
        if not sheets_client.test_connection():
            logger.error("❌ Google Sheets接続に失敗しました")
            return
        
        # ====================================================================
        # ステップ2: スプレッドシート準備（実行ログ作成 + 動的プロンプト生成）
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("ステップ2: スプレッドシート準備")
        logger.info("=" * 80)
        
        step_timer = Timer("ステップ2", logger)
        step_timer.start()
        
        logger.info("📝 動的プロンプトを生成中...")
        
        # 動的プロンプトを生成してスプレッドシートに保存
        execution_id = sheets_client.create_execution_log()
        
        if not execution_id:
            logger.error("❌ 実行ログの作成に失敗しました")
            return
        
        logger.info(f"✅ 実行ログを作成しました: {execution_id}")
        logger.info("   - 動的プロンプトAをD列に保存")
        logger.info("   - 動的プロンプトBをF列に保存")
        logger.info("   - ステータスを「処理中」に設定")
        
        step_timer.stop()
        
        # ====================================================================
        # ステップ3: プロンプトA実行（情報収集）
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("ステップ3: プロンプトA実行（情報収集）")
        logger.info("=" * 80)
        
        step_timer = Timer("ステップ3: 情報収集", logger)
        step_timer.start()
        
        logger.info("🔍 Claude APIで情報収集を開始します")
        logger.info("   - 動的プロンプトAを使用")
        logger.info("   - モックデータで動作確認（実際のWeb検索は未実装）")
        
        # 情報収集を実行
        topics_data = claude_client.collect_topics_with_web_search(
            use_history=True,
            use_mock_data=True  # モックデータを使用
        )
        
        if not topics_data or not topics_data.get('topics'):
            logger.error("❌ 情報収集に失敗しました")
            sheets_client.mark_as_error("情報収集に失敗しました")
            return
        
        logger.info(f"✅ 情報収集完了: {len(topics_data.get('topics', []))}件のトピック")
        
        for i, topic in enumerate(topics_data.get('topics', []), 1):
            logger.info(f"   {i}. {topic.get('title_ja', 'N/A')}")
            logger.info(f"      カテゴリ: {topic.get('category', 'N/A')}")
        
        # 検索結果をスプレッドシートに保存
        logger.info("\n💾 検索結果をスプレッドシート（E列）に保存中...")
        
        if not sheets_client.log_step_completion('情報収集', success=True, result_data=topics_data):
            logger.warning("⚠️ 検索結果の保存に失敗しました（処理は続行）")
        else:
            logger.info("✅ 検索結果を保存しました")
        
        step_timer.stop()
        
        # ====================================================================
        # ステップ4: プロンプトB実行（台本生成）
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("ステップ4: プロンプトB実行（台本生成）")
        logger.info("=" * 80)
        
        step_timer = Timer("ステップ4: 台本生成", logger)
        step_timer.start()
        
        logger.info("📝 Claude APIで対談形式の台本を生成します")
        logger.info("   - 動的プロンプトBを使用")
        logger.info("   - 検索結果を基に台本を生成")
        logger.info("   - 1つのトピックに絞って深掘り")
        
        # 台本生成を実行
        script_data = claude_client.generate_dialogue_script(topics_data)
        
        if not script_data:
            logger.error("❌ 台本生成に失敗しました")
            sheets_client.mark_as_error("台本生成に失敗しました")
            return
        
        logger.info(f"✅ 台本生成完了")
        logger.info(f"   タイトル: {script_data.get('title', 'N/A')}")
        logger.info(f"   文字数: {script_data.get('word_count', 0)}文字")
        logger.info(f"   推定時間: {script_data.get('estimated_duration_seconds', 0) / 60:.1f}分")
        
        # 生成台本をスプレッドシートに保存
        logger.info("\n💾 生成台本をスプレッドシート（G列）に保存中...")
        
        if not sheets_client.log_step_completion('台本生成', success=True, result_data=script_data):
            logger.warning("⚠️ 台本の保存に失敗しました（処理は続行）")
        else:
            logger.info("✅ 台本を保存しました")
        
        # 台本のプレビューを表示
        full_script = script_data.get("full_script", "")
        if full_script:
            preview_length = 300
            logger.info(f"\n📖 台本プレビュー（最初の{preview_length}文字）:")
            logger.info("-" * 40)
            logger.info(full_script[:preview_length] + ("..." if len(full_script) > preview_length else ""))
            logger.info("-" * 40)
        
        step_timer.stop()
        
        # ====================================================================
        # ステップ5: ローカルファイルに保存
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("ステップ5: ローカルファイルに保存")
        logger.info("=" * 80)
        
        output_dir = Path("temp")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # トピックをJSON保存
        topics_file = output_dir / f"topics_{timestamp}.json"
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(topics_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 トピックを保存: {topics_file}")
        
        # 台本をJSON保存
        script_file = output_dir / f"script_{timestamp}.json"
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 台本（JSON）を保存: {script_file}")
        
        # 台本をテキスト保存
        script_txt_file = output_dir / f"script_{timestamp}.txt"
        with open(script_txt_file, 'w', encoding='utf-8') as f:
            f.write(f"タイトル: {script_data.get('title', 'N/A')}\n")
            f.write(f"文字数: {script_data.get('word_count', 0)}\n")
            f.write(f"推定時間: {script_data.get('estimated_duration_seconds', 0) / 60:.1f}分\n")
            f.write("=" * 80 + "\n\n")
            f.write(full_script)
        logger.info(f"💾 台本（テキスト）を保存: {script_txt_file}")
        
        # ====================================================================
        # ステップ6: 完了処理
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("ステップ6: 完了処理")
        logger.info("=" * 80)
        
        total_timer.stop()
        
        # 処理時間を取得
        processing_time = total_timer.get_formatted_time()
        
        # スプレッドシートのステータスを「完了」に更新
        logger.info("📝 スプレッドシートのステータスを「完了」に更新中...")
        
        if sheets_client.mark_as_completed(processing_time):
            logger.info("✅ ステータスを「完了」に更新しました")
        else:
            logger.warning("⚠️ ステータス更新に失敗しました")
        
        # ====================================================================
        # 完了メッセージ
        # ====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("✅ パイプライン実行完了！")
        logger.info("=" * 80)
        
        logger.info(f"\n📊 実行サマリー:")
        logger.info(f"   実行ID: {execution_id}")
        logger.info(f"   処理時間: {processing_time}")
        logger.info(f"   収集トピック数: {len(topics_data.get('topics', []))}件")
        logger.info(f"   台本文字数: {script_data.get('word_count', 0)}文字")
        logger.info(f"   推定動画時間: {script_data.get('estimated_duration_seconds', 0) / 60:.1f}分")
        
        logger.info(f"\n📁 保存ファイル:")
        logger.info(f"   - {topics_file}")
        logger.info(f"   - {script_file}")
        logger.info(f"   - {script_txt_file}")
        
        logger.info(f"\n📊 Google Sheetsを確認してください:")
        logger.info(f"   実行ID: {execution_id}")
        logger.info(f"   D列: 動的プロンプトA（情報収集用）")
        logger.info(f"   E列: 検索結果（JSON）")
        logger.info(f"   F列: 動的プロンプトB（台本生成用）")
        logger.info(f"   G列: 生成台本（JSON）")
        logger.info(f"   ステータス: 完了（緑色の背景）")
        
        logger.info("\n🎉 次のステップ:")
        logger.info("   1. スプレッドシートで結果を確認")
        logger.info("   2. プロンプトを調整（必要に応じて）")
        logger.info("   3. 音声生成・動画生成を実装")
        logger.info("   4. 自動実行（Render Cron）を設定")
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️ ユーザーによって中断されました")
        if execution_id:
            sheets_client.mark_as_error("ユーザーによって中断されました")
        
    except Exception as e:
        logger.error(f"\n\n❌ エラーが発生しました: {e}")
        
        if execution_id:
            sheets_client.mark_as_error(f"エラー: {str(e)}")
        
        import traceback
        logger.error("\n" + traceback.format_exc())
        
        total_timer.stop()
    
    finally:
        if total_timer.is_running:
            total_timer.stop()


if __name__ == "__main__":
    main()

