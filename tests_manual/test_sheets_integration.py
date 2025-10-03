"""
Google Sheets連携のテストスクリプト

このスクリプトは以下をテストします：
1. GAS Web APIへの接続
2. プロンプトの取得
3. 統計情報の取得
4. 実行ログの作成と更新
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.sheets_client import SheetsClient
from utils.logger import setup_logger
import json

# 環境変数を読み込み
load_dotenv()


def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🧪 Google Sheets連携テスト")
    print("=" * 80 + "\n")
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    if not settings.GAS_WEB_APP_URL:
        print("❌ エラー: GAS_WEB_APP_URLが設定されていません")
        print("\n.envファイルに以下を追加してください:")
        print("GAS_WEB_APP_URL=https://script.google.com/macros/s/YOUR_DEPLOY_ID/exec")
        return
    
    print(f"✅ GAS URL: {settings.GAS_WEB_APP_URL[:50]}...\n")
    
    # SheetsClientを初期化
    client = SheetsClient(settings)
    
    # ============================================================================
    # テスト1: 接続確認
    # ============================================================================
    print("-" * 80)
    print("テスト1: GAS Web APIへの接続確認")
    print("-" * 80)
    
    if not client.test_connection():
        print("\n❌ 接続に失敗しました")
        print("\n確認事項:")
        print("1. GASコードに doGet 関数が含まれているか")
        print("2. GASのデプロイが「ウェブアプリ」として行われているか")
        print("3. アクセス権限が「全員（匿名ユーザーを含む）」になっているか")
        return
    
    print("✅ 接続成功\n")
    
    # ============================================================================
    # テスト2: 統計情報の取得
    # ============================================================================
    print("-" * 80)
    print("テスト2: 統計情報の取得")
    print("-" * 80)
    
    stats = client.get_statistics()
    
    if stats:
        print("\n📊 実行統計:")
        print(f"   総実行回数: {stats.get('total', 0)}回")
        print(f"   成功: {stats.get('completed', 0)}回")
        print(f"   処理中: {stats.get('processing', 0)}回")
        print(f"   エラー: {stats.get('error', 0)}回")
        
        if stats.get('total', 0) > 0:
            success_rate = (stats.get('completed', 0) / stats.get('total', 1)) * 100
            print(f"   成功率: {success_rate:.1f}%")
    else:
        print("\n⚠️ 統計情報の取得に失敗しました")
    
    print()
    
    # ============================================================================
    # テスト3: プロンプトの取得
    # ============================================================================
    print("-" * 80)
    print("テスト3: プロンプトの取得")
    print("-" * 80)
    
    prompts = client.get_prompts()
    
    if prompts:
        print("\n📝 取得したプロンプト:")
        
        info_collect = prompts.get('info_collect', '')
        script_generate = prompts.get('script_generate', '')
        
        print(f"   情報収集プロンプト: {len(info_collect)}文字")
        if info_collect:
            preview = info_collect[:100].replace('\n', ' ')
            print(f"     プレビュー: {preview}...")
        else:
            print("     ⚠️ プロンプトが空です")
        
        print(f"\n   台本生成プロンプト: {len(script_generate)}文字")
        if script_generate:
            preview = script_generate[:100].replace('\n', ' ')
            print(f"     プレビュー: {preview}...")
        else:
            print("     ⚠️ プロンプトが空です")
    else:
        print("\n⚠️ プロンプトの取得に失敗しました")
        print("\n確認事項:")
        print("1. スプレッドシートに「プロンプト管理」シートが存在するか")
        print("2. プロンプト管理シートに有効なプロンプトが登録されているか")
    
    print()
    
    # ============================================================================
    # テスト4: 実行ログの作成と更新
    # ============================================================================
    print("-" * 80)
    print("テスト4: 実行ログの作成と更新")
    print("-" * 80)
    
    # 実行ログを作成
    execution_id = client.create_execution_log()
    
    if not execution_id:
        print("\n❌ 実行ログの作成に失敗しました")
        print("\n確認事項:")
        print("1. スプレッドシートに「実行ログ」シートが存在するか")
        print("2. GASコードの doPost 関数が正しく実装されているか")
        return
    
    print(f"\n✅ 実行ログ作成成功: {execution_id}")
    
    # ステップ3の完了をログ
    print("\nステップ3（情報収集）の完了をログに記録...")
    test_topics = {
        "topics": [
            {
                "title_ja": "テストトピック",
                "title_en": "Test Topic",
                "summary": "これはテストです",
                "url": "https://example.com",
                "category": "テスト"
            }
        ],
        "collected_at": "2024-10-02 20:00:00",
        "total_count": 1
    }
    
    if client.log_step_completion('情報収集', success=True, result_data=test_topics):
        print("✅ ステップ3のログ記録成功")
    else:
        print("❌ ステップ3のログ記録失敗")
    
    # ステップ4の完了をログ
    print("\nステップ4（台本生成）の完了をログに記録...")
    test_script = {
        "title": "テスト台本",
        "episode_number": 1,
        "full_script": "[Aさん] テストです\n[Bさん] はい、テストですね",
        "word_count": 20,
        "estimated_duration_seconds": 60
    }
    
    if client.log_step_completion('台本生成', success=True, result_data=test_script):
        print("✅ ステップ4のログ記録成功")
    else:
        print("❌ ステップ4のログ記録失敗")
    
    # 完了としてマーク
    print("\n実行を完了としてマーク...")
    if client.mark_as_completed('0分10秒'):
        print("✅ 完了マーク成功")
    else:
        print("❌ 完了マーク失敗")
    
    print()
    
    # ============================================================================
    # 完了
    # ============================================================================
    print("=" * 80)
    print("✅ 全てのテストが完了しました")
    print("=" * 80)
    print("\nスプレッドシートを確認して、以下が記録されているか確認してください:")
    print(f"  - 実行ID: {execution_id}")
    print("  - ステータス: 完了（緑色の背景）")
    print("  - 検索結果: テストトピックのJSON")
    print("  - 生成台本: テスト台本のJSON")
    print("  - 処理時間: 0分10秒")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

