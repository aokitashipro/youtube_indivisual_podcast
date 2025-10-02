"""
Google Services（TTS & Drive）の動作確認スクリプト

以下をテストします：
1. Google Cloud認証の確認
2. Text-to-Speech APIの接続テスト
3. Google Drive APIの接続テスト
4. フォルダへのアクセス確認
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.google_drive_uploader import GoogleDriveUploader
from utils.logger import setup_logger

# 環境変数を読み込み
load_dotenv()


def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🔧 Google Services 動作確認テスト")
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
    
    # 認証ファイルの確認
    creds_path = Path(settings.GOOGLE_CREDENTIALS_PATH)
    if creds_path.exists():
        print(f"✅ 認証ファイルが見つかりました: {creds_path}")
        print(f"   ファイルサイズ: {creds_path.stat().st_size} bytes")
    else:
        print(f"❌ 認証ファイルが見つかりません: {creds_path}")
        print("\n確認事項:")
        print("   1. Google Cloud Consoleでサービスアカウントを作成")
        print("   2. JSONキーをダウンロード")
        print("   3. assets/credentials/google-credentials.json に配置")
        return
    
    # Google Drive設定の確認
    if settings.GOOGLE_DRIVE_FOLDER_ID:
        print(f"✅ Google Drive フォルダID: {settings.GOOGLE_DRIVE_FOLDER_ID}")
    else:
        print("⚠️ GOOGLE_DRIVE_FOLDER_IDが設定されていません")
        print("   .envファイルに以下を追加してください:")
        print("   GOOGLE_DRIVE_FOLDER_ID=your_folder_id")
    
    # Gemini APIキーの確認
    gemini_keys = []
    if settings.GEMINI_API_KEY:
        gemini_keys.append("GEMINI_API_KEY")
    if hasattr(settings, 'GEMINI_API_KEY_1') and settings.GEMINI_API_KEY_1:
        gemini_keys.append("GEMINI_API_KEY_1")
    if hasattr(settings, 'GEMINI_API_KEY_2') and settings.GEMINI_API_KEY_2:
        gemini_keys.append("GEMINI_API_KEY_2")
    
    if gemini_keys:
        print(f"✅ Gemini APIキー: {len(gemini_keys)}個設定済み")
        for key_name in gemini_keys:
            print(f"   - {key_name}")
    else:
        print("⚠️ Gemini APIキーが設定されていません")
    
    print()
    
    # ============================================================================
    # テスト2: Google Drive API接続テスト
    # ============================================================================
    print("-" * 80)
    print("テスト2: Google Drive API接続テスト")
    print("-" * 80)
    
    # GoogleDriveUploaderを初期化
    uploader = GoogleDriveUploader(settings)
    
    if not uploader.service:
        print("❌ Google Drive APIの初期化に失敗しました")
        print("\n確認事項:")
        print("   1. 認証ファイルが正しいか")
        print("   2. Google Drive APIが有効化されているか")
        print("   3. サービスアカウントに適切な権限があるか")
        return
    
    print("✅ Google Drive APIの初期化成功")
    
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
            print("   2. サービスアカウントがフォルダに共有されているか")
            print(f"   3. サービスアカウント: youtube-podcast-bot@gen-lang-client-*.iam.gserviceaccount.com")
            print("   4. フォルダの「共有」設定で上記アカウントを「編集者」として追加")
    
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
    test_file = test_dir / "test_upload.txt"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Google Drive アップロードテスト\n")
        f.write("このファイルは自動生成されたテストファイルです。\n")
        f.write(f"作成日時: {Path(__file__).stat().st_mtime}\n")
    
    print(f"📝 テストファイルを作成: {test_file}")
    
    # アップロードテスト
    print(f"\n📤 Google Driveにアップロード中...")
    
    result = uploader.upload_file(
        file_path=test_file,
        file_name="test_upload_from_python.txt",
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
    else:
        print(f"\n❌ アップロードに失敗しました")
    
    print()
    
    # ============================================================================
    # テスト4: Text-to-Speech API接続テスト
    # ============================================================================
    print("-" * 80)
    print("テスト4: Text-to-Speech API接続テスト")
    print("-" * 80)
    
    try:
        from google.cloud import texttospeech
        
        # TTSクライアントを初期化
        tts_client = texttospeech.TextToSpeechClient.from_service_account_file(
            settings.GOOGLE_CREDENTIALS_PATH
        )
        
        print("✅ Text-to-Speech APIの初期化成功")
        
        # 利用可能な音声を確認
        print("\n🎤 利用可能な日本語音声（最初の5件）:")
        voices = tts_client.list_voices(language_code='ja-JP')
        
        count = 0
        for voice in voices.voices:
            if count >= 5:
                break
            print(f"   - {voice.name}")
            count += 1
        
        print(f"\n   設定済み音声:")
        print(f"   - Aさん: {settings.VOICE_A} (ピッチ: {settings.VOICE_A_PITCH})")
        print(f"   - Bさん: {settings.VOICE_B} (ピッチ: {settings.VOICE_B_PITCH})")
        
    except ImportError:
        print("⚠️ google-cloud-texttospeech がインストールされていません")
        print("   インストール: pip install google-cloud-texttospeech")
    except Exception as e:
        print(f"❌ Text-to-Speech API接続エラー: {e}")
    
    print()
    
    # ============================================================================
    # 完了
    # ============================================================================
    print("=" * 80)
    print("✅ Google Services 動作確認テストが完了しました")
    print("=" * 80)
    
    print("\n📋 次のステップ:")
    print("   1. ✅ 認証ファイルの配置")
    print("   2. ✅ Google Drive APIの接続")
    print("   3. ✅ Text-to-Speech APIの接続")
    print("   4. 🎬 完全なパイプライン実行")
    print("\n実行コマンド:")
    print("   python run_pipeline_with_sheets.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

