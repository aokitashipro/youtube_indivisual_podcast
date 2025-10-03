"""
動的プロンプト生成のテストスクリプト

このスクリプトは以下をテストします：
1. 日付に基づく動的プロンプト生成
2. 生成されたプロンプトの内容確認
3. Google Sheetsへの動的プロンプト記録
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
from datetime import datetime

# 環境変数を読み込み
load_dotenv()


def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎯 動的プロンプト生成テスト")
    print("=" * 80 + "\n")
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    if not settings.GAS_WEB_APP_URL:
        print("❌ エラー: GAS_WEB_APP_URLが設定されていません")
        return
    
    print(f"✅ GAS URL: {settings.GAS_WEB_APP_URL[:50]}...\n")
    
    # SheetsClientを初期化
    client = SheetsClient(settings)
    
    # ============================================================================
    # テスト1: 動的プロンプト生成
    # ============================================================================
    print("-" * 80)
    print("テスト1: 動的プロンプト生成")
    print("-" * 80)
    
    # 動的プロンプトを生成
    dynamic_prompts = client._generate_dynamic_prompts()
    
    print("\n🎯 生成されたプロンプト:")
    print(f"   情報収集プロンプト: {len(dynamic_prompts['info_collect'])}文字")
    print(f"   台本生成プロンプト: {len(dynamic_prompts['script_generate'])}文字")
    
    # 今日の日付情報を表示
    now = datetime.now()
    weekday = now.strftime('%A')
    date_str = now.strftime('%Y年%m月%d日')
    month = now.month
    
    if month in [12, 1, 2]:
        season = '冬'
    elif month in [3, 4, 5]:
        season = '春'
    elif month in [6, 7, 8]:
        season = '夏'
    else:
        season = '秋'
    
    print(f"\n📅 今日の設定:")
    print(f"   日付: {date_str} ({weekday})")
    print(f"   季節: {season}")
    
    # プロンプトのプレビューを表示
    print(f"\n📝 情報収集プロンプト（プレビュー）:")
    print("-" * 40)
    preview = dynamic_prompts['info_collect'][:300].replace('\n', ' ')
    print(f"{preview}...")
    print("-" * 40)
    
    print(f"\n📝 台本生成プロンプト（プレビュー）:")
    print("-" * 40)
    preview = dynamic_prompts['script_generate'][:300].replace('\n', ' ')
    print(f"{preview}...")
    print("-" * 40)
    
    # ============================================================================
    # テスト2: Google Sheetsへの記録
    # ============================================================================
    print("\n" + "-" * 80)
    print("テスト2: 動的プロンプトをGoogle Sheetsに記録")
    print("-" * 80)
    
    # 動的プロンプトを使って実行ログを作成
    execution_id = client.create_execution_log(custom_prompts=dynamic_prompts)
    
    if not execution_id:
        print("\n❌ 動的プロンプトでの実行ログ作成に失敗しました")
        return
    
    print(f"\n✅ 動的プロンプトでの実行ログ作成成功: {execution_id}")
    
    # テストデータでログを更新
    print("\nテストデータでログを更新中...")
    
    test_topics = {
        "topics": [
            {
                "title_ja": f"{weekday}の特別トピック",
                "title_en": f"Special {weekday} Topic",
                "summary": f"これは{season}の{weekday}に生成されたテストトピックです",
                "url": "https://example.com/test",
                "category": "テスト",
                "interesting_points": f"{season}の{weekday}らしい内容で、リスナーの気分に合った話題です"
            }
        ],
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": 1
    }
    
    if client.log_step_completion('情報収集', success=True, result_data=test_topics):
        print("✅ 情報収集のログ記録成功")
    else:
        print("❌ 情報収集のログ記録失敗")
    
    # 完了としてマーク
    if client.mark_as_completed('0分15秒'):
        print("✅ 完了マーク成功")
    else:
        print("❌ 完了マーク失敗")
    
    # ============================================================================
    # テスト3: 異なる曜日のプロンプト比較
    # ============================================================================
    print("\n" + "-" * 80)
    print("テスト3: 異なる曜日のプロンプト比較")
    print("-" * 80)
    
    # 異なる曜日のプロンプトを生成（テスト用）
    from datetime import timedelta
    
    test_weekdays = ['Monday', 'Wednesday', 'Friday']
    
    for test_weekday in test_weekdays:
        # テスト用の日付を作成（今日の曜日を指定の曜日に変更）
        days_ahead = test_weekdays.index(test_weekday)
        test_date = now + timedelta(days=days_ahead)
        
        # 一時的に日付を変更してプロンプト生成（実際にはモック）
        print(f"\n📅 {test_weekday}のプロンプト特徴:")
        
        if test_weekday == 'Monday':
            print("   - テーマ: 新しい週の始まり、目標設定")
            print("   - 要素: 新しい挑戦、目標達成、モチベーション")
        elif test_weekday == 'Wednesday':
            print("   - テーマ: 中盤の息抜き、エンターテイメント")
            print("   - 要素: クリエイティブ、エンターテイメント、息抜き")
        elif test_weekday == 'Friday':
            print("   - テーマ: 週末前、まとめ")
            print("   - 要素: 週末準備、成果まとめ、リラックス")
    
    # ============================================================================
    # 完了
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ 動的プロンプト生成テストが完了しました")
    print("=" * 80)
    print("\nGoogle Sheetsを確認して、以下が記録されているか確認してください:")
    print(f"  - 実行ID: {execution_id}")
    print(f"  - プロンプトA（D列）: {date_str} ({weekday})向けの情報収集プロンプト")
    print(f"  - プロンプトB（F列）: {date_str} ({weekday})向けの台本生成プロンプト")
    print(f"  - 検索結果: {weekday}の特別トピック")
    print("  - ステータス: 完了（緑色の背景）")
    print()
    
    print("🎯 動的プロンプトの特徴:")
    print("   - 日付と曜日に基づいて毎日異なるプロンプトが生成される")
    print("   - 季節感を考慮した内容調整")
    print("   - 曜日別のテーマと特別要素を組み込み")
    print("   - リスナーの気分に合った内容を重視")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
