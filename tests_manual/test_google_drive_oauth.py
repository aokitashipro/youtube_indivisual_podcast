"""
Google Drive OAuth 2.0認証テスト

個人のGoogleアカウントでGoogle Driveにアクセスするための
OAuth 2.0認証をテストします。
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.google_drive_oauth import GoogleDriveOAuthUploader
from utils.logger import setup_logger

# 環境変数を読み込み
load_dotenv()


def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🔧 Google Drive OAuth 2.0 認証テスト")
    print("=" * 80 + "\n")
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    # ============================================================================
    # テスト1: 設定確認
    # ============================================================================
    print("-" * 80)
    print("テスト1: 設定確認")
    print("-" * 80)
    
    # OAuth認証ファイルの確認
    creds_path = Path(settings.GOOGLE_CREDENTIALS_PATH)
    if creds_path.exists():
        print(f"✅ OAuth認証ファイルが見つかりました: {creds_path}")
        print(f"   ファイルサイズ: {creds_path.stat().st_size} bytes")
    else:
        print(f"❌ OAuth認証ファイルが見つかりません: {creds_path}")
        print("\n📋 OAuth認証ファイルの作成手順:")
        print("   1. docs/GOOGLE_DRIVE_OAUTH_SETUP.md を参照")
        print("   2. Google Cloud ConsoleでOAuthクライアントIDを作成")
        print("   3. JSONファイルをダウンロード")
        print("   4. assets/credentials/google-credentials.json に配置")
        return
    
    # トークンファイルの確認
    token_path = Path("assets/credentials/token.pickle")
    if token_path.exists():
        print(f"✅ 認証トークンが見つかりました: {token_path}")
        print(f"   （既存の認証を使用します）")
    else:
        print(f"⚠️ 認証トークンが見つかりません: {token_path}")
        print(f"   （初回認証を実行します）")
    
    # Google Drive設定の確認
    if settings.GOOGLE_DRIVE_FOLDER_ID:
        print(f"✅ Google Drive フォルダID: {settings.GOOGLE_DRIVE_FOLDER_ID}")
    else:
        print("⚠️ GOOGLE_DRIVE_FOLDER_IDが設定されていません")
        print("   マイドライブのルートにアップロードされます")
    
    print()
    
    # ============================================================================
    # テスト2: OAuth 2.0認証とGoogle Drive API接続
    # ============================================================================
    print("-" * 80)
    print("テスト2: OAuth 2.0認証とGoogle Drive API接続")
    print("-" * 80)
    
    # GoogleDriveOAuthUploaderを初期化
    uploader = GoogleDriveOAuthUploader(settings)
    
    if not uploader.service:
        print("❌ Google Drive APIの初期化に失敗しました")
        print("\n確認事項:")
        print("   1. OAuth認証ファイルが正しいか")
        print("   2. Google Drive APIが有効化されているか")
        print("   3. 認証フローを完了したか")
        return
    
    print("✅ Google Drive APIの初期化成功（OAuth 2.0）")
    
    # フォルダ情報を取得
    if settings.GOOGLE_DRIVE_FOLDER_ID:
        print(f"\n📁 フォルダ情報を取得中...")
        folder_info = uploader.get_folder_info(settings.GOOGLE_DRIVE_FOLDER_ID)
        
        if folder_info:
            print(f"✅ フォルダアクセス成功")
            print(f"   フォルダ名: {folder_info.get('folder_name', 'N/A')}")
            print(f"   フォルダID: {folder_info.get('folder_id', 'N/A')}")
            print(f"   URL: {folder_info.get('web_view_link', 'N/A')}")
            
            # フォルダ内のファイル一覧
            print(f"\n📄 フォルダ内のファイル一覧:")
            files = uploader.list_files_in_folder(settings.GOOGLE_DRIVE_FOLDER_ID)
            
            if files:
                for file in files[:5]:  # 最初の5件を表示
                    print(f"   - {file.get('name')} ({file.get('mimeType')})")
                if len(files) > 5:
                    print(f"   ... 他{len(files) - 5}件")
            else:
                print("   （フォルダは空です）")
        else:
            print("❌ フォルダへのアクセスに失敗しました")
            print("\n確認事項:")
            print("   1. フォルダIDが正しいか")
            print("   2. 認証したGoogleアカウントがフォルダにアクセスできるか")
    
    print()
    
    # ============================================================================
    # テスト3: テストファイルのアップロード
    # ============================================================================
    print("-" * 80)
    print("テスト3: テストファイルのアップロード")
    print("-" * 80)
    
    # テストファイルを作成
    test_dir = Path("temp")
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test_oauth_upload.txt"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Google Drive OAuth 2.0 アップロードテスト\n")
        f.write("このファイルは自動生成されたテストファイルです。\n")
        f.write(f"認証方式: OAuth 2.0\n")
        f.write(f"作成日時: {Path(__file__).stat().st_mtime}\n")
    
    print(f"📝 テストファイルを作成: {test_file}")
    
    # アップロードテスト
    print(f"\n📤 Google Driveにアップロード中...")
    
    result = uploader.upload_file(
        file_path=test_file,
        file_name="test_oauth_upload_from_python.txt",
        mime_type='text/plain',
        make_public=True
    )
    
    if result:
        print(f"\n✅ アップロード成功！")
        print(f"   ファイルID: {result['file_id']}")
        print(f"   表示URL: {result['web_view_link']}")
        print(f"   ダウンロードURL: {result['web_content_link']}")
        print(f"\n🌐 ブラウザで確認:")
        print(f"   {result['web_view_link']}")
        
        if settings.GOOGLE_DRIVE_FOLDER_ID:
            print(f"\nまたは、フォルダを直接開く:")
            print(f"   https://drive.google.com/drive/folders/{settings.GOOGLE_DRIVE_FOLDER_ID}")
    else:
        print(f"\n❌ アップロードに失敗しました")
    
    print()
    
    # ============================================================================
    # 完了
    # ============================================================================
    print("=" * 80)
    print("✅ Google Drive OAuth 2.0 認証テストが完了しました")
    print("=" * 80)
    
    print("\n📋 次のステップ:")
    print("   1. ✅ OAuth認証ファイルの配置")
    print("   2. ✅ 初回認証の完了")
    print("   3. ✅ Google Driveへのアップロード")
    print("   4. 🎬 音声生成とアップロードのテスト")
    print("\n実行コマンド:")
    print("   python test_audio_generation.py  # 音声生成テスト")
    print("   python run_pipeline_with_sheets.py  # フルパイプライン実行")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

