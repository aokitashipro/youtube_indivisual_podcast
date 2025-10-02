"""
ElevenLabs API の直接HTTPリクエストテスト

ElevenLabs APIを直接HTTPリクエストで呼び出して音声生成をテスト
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_elevenlabs_direct():
    """ElevenLabs APIの直接呼び出しテスト"""
    print("\n" + "=" * 60)
    print("🎤 ElevenLabs API 直接呼び出しテスト")
    print("=" * 60)
    
    # APIキーの確認
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key or api_key == 'your_elevenlabs_api_key_here':
        print("\n⚠️ ElevenLabs APIキーが設定されていません")
        return
    
    print(f"\n✅ APIキーが設定されています: {api_key[:20]}...")
    
    # ElevenLabs API エンドポイント
    url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"  # Adam (男性声)
    
    # リクエストヘッダー
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    # リクエストボディ
    data = {
        "text": "こんにちは！これはElevenLabs APIのテストです。",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    print(f"\n🎤 男性声（Adam）で音声生成中...")
    
    try:
        # API呼び出し
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # 音声ファイルを保存
            output_dir = Path("temp")
            output_dir.mkdir(exist_ok=True)
            
            audio_file = output_dir / "test_male_direct.mp3"
            with open(audio_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / 1024
            print(f"✅ 男性声生成成功: {audio_file} ({file_size:.1f}KB)")
            
        else:
            print(f"❌ API呼び出し失敗: {response.status_code}")
            print(f"   レスポンス: {response.text}")
            return
    
    except Exception as e:
        print(f"❌ エラー: {e}")
        return
    
    # 女性声でもテスト
    url_female = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"  # Bella (女性声)
    
    print(f"\n🎤 女性声（Bella）で音声生成中...")
    
    try:
        response = requests.post(url_female, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_file = output_dir / "test_female_direct.mp3"
            with open(audio_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / 1024
            print(f"✅ 女性声生成成功: {audio_file} ({file_size:.1f}KB)")
            
        else:
            print(f"❌ 女性声API呼び出し失敗: {response.status_code}")
            print(f"   レスポンス: {response.text}")
    
    except Exception as e:
        print(f"❌ 女性声エラー: {e}")
    
    print(f"\n🎉 音声生成テスト完了！")
    print(f"   生成されたファイル:")
    print(f"   - 男性声: temp/test_male_direct.mp3")
    print(f"   - 女性声: temp/test_female_direct.mp3")
    print(f"\n💡 これらのファイルを再生して音声を確認してください")


if __name__ == "__main__":
    test_elevenlabs_direct()
