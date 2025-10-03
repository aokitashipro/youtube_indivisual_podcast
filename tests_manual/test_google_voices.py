"""
Google Cloud Text-to-Speech API の利用可能な音声一覧テスト

日本語で利用可能な音声を確認して、より女性らしい声質を探す
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

def test_google_voices():
    """Google Cloud TTS APIの利用可能な音声を確認"""
    print("\n" + "=" * 60)
    print("🎤 Google Cloud Text-to-Speech API 音声一覧")
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
    
    # 利用可能な音声を取得
    try:
        print(f"\n🔍 利用可能な音声を取得中...")
        voices = client.list_voices()
        
        # 日本語音声をフィルタリング
        japanese_voices = []
        for voice in voices.voices:
            if voice.language_codes[0].startswith('ja'):
                japanese_voices.append(voice)
        
        print(f"✅ 日本語音声: {len(japanese_voices)}個見つかりました")
        
        # 音声一覧を表示
        print(f"\n📋 日本語音声一覧:")
        for i, voice in enumerate(japanese_voices):
            gender = "男性" if voice.ssml_gender == texttospeech.SsmlVoiceGender.MALE else "女性" if voice.ssml_gender == texttospeech.SsmlVoiceGender.FEMALE else "中性"
            print(f"   {i+1:2d}. {voice.name:20s} | {gender:2s} | {voice.natural_sample_rate_hertz}Hz")
        
        # 女性音声のみを抽出
        female_voices = [v for v in japanese_voices if v.ssml_gender == texttospeech.SsmlVoiceGender.FEMALE]
        
        if female_voices:
            print(f"\n👩 女性音声 ({len(female_voices)}個):")
            for i, voice in enumerate(female_voices):
                print(f"   {i+1:2d}. {voice.name:20s} | {voice.natural_sample_rate_hertz}Hz")
        else:
            print(f"\n⚠️ 女性音声が見つかりませんでした")
        
        # 音声テスト
        test_text = "こんにちは、これは音声テストです。"
        
        print(f"\n🎤 音声テストを実行します")
        
        # 現在の設定（男性）
        print(f"\n1. 現在の男性音声 (ja-JP-Neural2-C):")
        try:
            synthesis_input = texttospeech.SynthesisInput(text=test_text)
            voice = texttospeech.VoiceSelectionParams(
                language_code='ja-JP',
                name='ja-JP-Neural2-C'
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                pitch=0.0
            )
            
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            output_file = Path("temp/voice_test_male_current.wav")
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, 'wb') as out:
                out.write(response.audio_content)
            
            print(f"   ✅ 保存: {output_file}")
            
        except Exception as e:
            print(f"   ❌ エラー: {e}")
        
        # 推奨女性音声のテスト
        recommended_female_voices = [
            'ja-JP-Standard-A',  # 女性音声
            'ja-JP-Standard-C',  # 女性音声
            'ja-JP-Wavenet-A',   # 女性音声
            'ja-JP-Wavenet-C',   # 女性音声
        ]
        
        for i, voice_name in enumerate(recommended_female_voices):
            print(f"\n{i+2}. 推奨女性音声 ({voice_name}):")
            try:
                voice = texttospeech.VoiceSelectionParams(
                    language_code='ja-JP',
                    name=voice_name
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    pitch=0.0  # 女性らしさを強調するためピッチを上げる場合もある
                )
                
                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
                
                output_file = Path(f"temp/voice_test_female_{i+1}_{voice_name.replace('-', '_')}.wav")
                with open(output_file, 'wb') as out:
                    out.write(response.audio_content)
                
                print(f"   ✅ 保存: {output_file}")
                
            except Exception as e:
                print(f"   ❌ エラー: {e}")
        
        print(f"\n🎉 音声テスト完了！")
        print(f"   生成されたファイルを再生して、最適な女性音声を選択してください")
        
    except Exception as e:
        print(f"❌ 音声取得エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_google_voices()
