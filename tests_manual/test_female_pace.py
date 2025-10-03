"""
女性の声のペース調整テスト

ja-JP-Standard-Aの話す速度を調整して最適なペースを見つける
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

def test_female_pace():
    """女性の声のペース調整テスト"""
    print("\n" + "=" * 60)
    print("🎤 女性の声のペース調整テスト")
    print("=" * 60)
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    # Google Cloud Text-to-Speech API
    try:
        from google.cloud import texttospeech
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        import pickle
        from google.auth.transport.requests import Request
        
        print("✅ google-cloud-texttospeech インポート成功")
    except ImportError:
        print("❌ google-cloud-texttospeech がインストールされていません")
        return
    
    # OAuth認証でクライアントを初期化
    try:
        SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
        credentials_path = Path(settings.GOOGLE_CREDENTIALS_PATH)
        
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
        print("✅ Google TTSクライアント初期化成功")
        
    except Exception as e:
        print(f"❌ クライアント初期化エラー: {e}")
        return
    
    # テスト用のテキスト
    test_text = "こんにちは、これは女性の声のペース調整テストです。様々な話す速度で音声を生成して、最適なペースを見つけましょう。"
    
    # 異なる話す速度をテスト
    speaking_rates = [
        (0.8, "ゆっくり"),
        (1.0, "標準"),
        (1.2, "やや速め"),
        (1.4, "速め"),
        (1.6, "かなり速め")
    ]
    
    print(f"\n🎤 女性音声の話す速度テスト")
    print(f"   音声: {settings.VOICE_B}")
    print(f"   テストテキスト: {test_text[:50]}...")
    
    output_dir = Path("temp/pace_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for rate, description in speaking_rates:
        print(f"\n{description} (speaking_rate: {rate}):")
        try:
            synthesis_input = texttospeech.SynthesisInput(text=test_text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code='ja-JP',
                name=settings.VOICE_B  # ja-JP-Standard-A
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                pitch=float(settings.VOICE_B_PITCH),
                speaking_rate=rate
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # 音声ファイルを保存
            filename = f"female_pace_{rate:.1f}_{description}.wav"
            output_file = output_dir / filename
            
            with open(output_file, 'wb') as out:
                out.write(response.audio_content)
            
            file_size = output_file.stat().st_size / 1024
            print(f"   ✅ 保存: {filename} ({file_size:.1f}KB)")
            
        except Exception as e:
            print(f"   ❌ エラー: {e}")
    
    print(f"\n🎉 ペース調整テスト完了！")
    print(f"   生成されたファイル:")
    for rate, description in speaking_rates:
        filename = f"female_pace_{rate:.1f}_{description}.wav"
        print(f"   - {filename}")
    
    print(f"\n💡 これらのファイルを再生して、最適なペースを選択してください")
    print(f"   推奨: 1.2-1.4（やや速め〜速め）")


if __name__ == "__main__":
    test_female_pace()
