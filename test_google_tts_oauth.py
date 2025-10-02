"""
Google Cloud Text-to-Speech API のOAuth認証テスト

現在のOAuth認証ファイルでGoogle TTS APIが動作するかテスト
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from utils.logger import setup_logger

load_dotenv()

def test_google_tts_oauth():
    """Google Cloud TTS APIのOAuth認証テスト"""
    print("\n" + "=" * 60)
    print("🎤 Google Cloud Text-to-Speech API OAuth認証テスト")
    print("=" * 60)
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    # Google Cloud Text-to-Speech APIをテスト
    try:
        from google.cloud import texttospeech
        print("✅ google-cloud-texttospeech インポート成功")
    except ImportError:
        print("❌ google-cloud-texttospeech がインストールされていません")
        print("   インストール: pip install google-cloud-texttospeech")
        return
    
    # 認証ファイルの確認
    credentials_path = Path(settings.GOOGLE_CREDENTIALS_PATH)
    print(f"\n📁 認証ファイル: {credentials_path}")
    
    if credentials_path.exists():
        print("✅ 認証ファイルが存在します")
        
        # ファイルの内容を確認
        import json
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        if "installed" in creds_data:
            print("📋 OAuth認証ファイル（個人アカウント用）")
            print("   ⚠️ Google Cloud TTS APIにはサービスアカウントキーが必要です")
        elif "type" in creds_data and creds_data["type"] == "service_account":
            print("📋 サービスアカウントキー")
            print("   ✅ Google Cloud TTS APIで使用可能です")
        else:
            print("📋 不明な認証ファイル形式")
    else:
        print("❌ 認証ファイルが見つかりません")
        return
    
    # OAuth認証でのTTSクライアント初期化を試行
    print(f"\n🔧 Google Cloud TTS クライアント初期化テスト")
    
    try:
        # 方法1: デフォルト認証
        print("   方法1: デフォルト認証を試行...")
        client = texttospeech.TextToSpeechClient()
        print("   ✅ デフォルト認証成功")
        
    except Exception as e:
        print(f"   ❌ デフォルト認証失敗: {e}")
        
        try:
            # 方法2: 認証ファイルを直接指定
            print("   方法2: 認証ファイル直接指定を試行...")
            client = texttospeech.TextToSpeechClient.from_service_account_file(str(credentials_path))
            print("   ✅ 認証ファイル指定成功")
            
        except Exception as e2:
            print(f"   ❌ 認証ファイル指定失敗: {e2}")
            
            try:
                # 方法3: OAuth認証を使用
                print("   方法3: OAuth認証を使用...")
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                import pickle
                
                # OAuth認証フロー
                SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
                
                creds = None
                token_file = Path("assets/credentials/tts_token.pickle")
                
                if token_file.exists():
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(credentials_path), SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
                
                client = texttospeech.TextToSpeechClient(credentials=creds)
                print("   ✅ OAuth認証成功")
                
            except Exception as e3:
                print(f"   ❌ OAuth認証失敗: {e3}")
                print("\n💡 解決方法:")
                print("   1. Google Cloud Consoleでサービスアカウントキーを取得")
                print("   2. サービスアカウントキーを assets/credentials/ に配置")
                print("   3. Text-to-Speech APIを有効化")
                return
    
    # 実際の音声生成テスト
    print(f"\n🎤 音声生成テスト")
    
    try:
        # 男性声でテスト
        text = "こんにちは！これはGoogle Cloud Text-to-Speech APIのテストです。"
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code='ja-JP',
            name='ja-JP-Neural2-C'  # 男性声
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            pitch=0.0,
            speaking_rate=1.0
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # 音声ファイルを保存
        output_file = Path("temp/test_google_tts_male.wav")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'wb') as out:
            out.write(response.audio_content)
        
        file_size = output_file.stat().st_size / 1024
        print(f"✅ 男性声生成成功: {output_file} ({file_size:.1f}KB)")
        
        # 女性声でもテスト
        voice_female = texttospeech.VoiceSelectionParams(
            language_code='ja-JP',
            name='ja-JP-Neural2-D'  # 女性声
        )
        
        audio_config_female = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            pitch=-2.0,
            speaking_rate=1.0
        )
        
        response_female = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_female,
            audio_config=audio_config_female
        )
        
        output_file_female = Path("temp/test_google_tts_female.wav")
        with open(output_file_female, 'wb') as out:
            out.write(response_female.audio_content)
        
        file_size_female = output_file_female.stat().st_size / 1024
        print(f"✅ 女性声生成成功: {output_file_female} ({file_size_female:.1f}KB)")
        
        print(f"\n🎉 Google Cloud TTS APIテスト成功！")
        print(f"   生成されたファイル:")
        print(f"   - 男性声: {output_file}")
        print(f"   - 女性声: {output_file_female}")
        
    except Exception as e:
        print(f"❌ 音声生成エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_google_tts_oauth()
