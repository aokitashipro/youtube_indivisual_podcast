"""
ElevenLabs API の簡単なテスト

実際の音声生成をテストするためのスクリプト
"""
import os
from pathlib import Path

# ElevenLabs APIのテスト
try:
    from elevenlabs import generate, set_api_key, voices
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("❌ elevenlabs がインストールされていません")
    print("   インストール: pip install elevenlabs")

def test_elevenlabs():
    """ElevenLabs APIのテスト"""
    print("\n" + "=" * 60)
    print("🎤 ElevenLabs API テスト")
    print("=" * 60)
    
    if not ELEVENLABS_AVAILABLE:
        return
    
    # APIキーの確認
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key or api_key == 'your_elevenlabs_api_key_here':
        print("\n⚠️ ElevenLabs APIキーが設定されていません")
        print("\n📋 ElevenLabs APIキーの取得方法:")
        print("   1. https://elevenlabs.io/ にアクセス")
        print("   2. 無料アカウントを作成")
        print("   3. プロフィール → API Key からキーをコピー")
        print("   4. .envファイルに追加:")
        print("      ELEVENLABS_API_KEY=your_actual_api_key")
        print("\n💡 無料プランでも月10,000文字まで音声生成可能です")
        return
    
    print(f"\n✅ APIキーが設定されています: {api_key[:20]}...")
    
    # APIキーを設定
    set_api_key(api_key)
    
    # 利用可能な音声一覧を取得
    try:
        voices_list = voices()
        print(f"\n🎭 利用可能な音声数: {len(voices_list)}個")
        
        # 日本語対応の音声を探す
        japanese_voices = []
        for voice in voices_list:
            if hasattr(voice, 'labels') and voice.labels:
                if 'japanese' in str(voice.labels).lower() or 'ja' in str(voice.labels).lower():
                    japanese_voices.append(voice)
        
        if japanese_voices:
            print(f"\n🇯🇵 日本語対応音声: {len(japanese_voices)}個")
            for voice in japanese_voices[:3]:  # 最初の3個を表示
                print(f"   - {voice.name} (ID: {voice.voice_id})")
        else:
            print(f"\n🌍 推奨音声（多言語対応）:")
            # 多言語対応の音声を表示
            multilingual_voices = [
                ("Adam", "pNInz6obpgDQGcFmaJgB", "男性"),
                ("Bella", "EXAVITQu4vr4xnSDxMaL", "女性"),
                ("Antoni", "ErXwobaYiN019PkySvjV", "男性"),
                ("Elli", "MF3mGyEYCl7XYWbV9V6O", "女性")
            ]
            
            for name, voice_id, gender in multilingual_voices:
                print(f"   - {name} (ID: {voice_id}) - {gender}")
        
        # 簡単な音声生成テスト
        print(f"\n🎤 音声生成テスト")
        test_text = "こんにちは！これはElevenLabs APIのテストです。"
        
        try:
            # 男性声（Adam）でテスト
            print(f"   男性声（Adam）で生成中...")
            audio_male = generate(
                text=test_text,
                voice="pNInz6obpgDQGcFmaJgB",  # Adam
                model="eleven_multilingual_v2"
            )
            
            # 音声ファイルを保存
            output_dir = Path("temp/elevenlabs_test")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            male_file = output_dir / "test_male.wav"
            with open(male_file, 'wb') as f:
                f.write(audio_male)
            
            print(f"   ✅ 男性声生成完了: {male_file} ({len(audio_male)/1024:.1f}KB)")
            
            # 女性声（Bella）でテスト
            print(f"   女性声（Bella）で生成中...")
            audio_female = generate(
                text=test_text,
                voice="EXAVITQu4vr4xnSDxMaL",  # Bella
                model="eleven_multilingual_v2"
            )
            
            female_file = output_dir / "test_female.wav"
            with open(female_file, 'wb') as f:
                f.write(audio_female)
            
            print(f"   ✅ 女性声生成完了: {female_file} ({len(audio_female)/1024:.1f}KB)")
            
            print(f"\n🎉 音声生成テストが成功しました！")
            print(f"   生成されたファイル:")
            print(f"   - 男性声: {male_file}")
            print(f"   - 女性声: {female_file}")
            
            print(f"\n💡 これらのファイルを再生して音声を確認してください")
            
        except Exception as e:
            print(f"   ❌ 音声生成エラー: {e}")
            print(f"   APIキーやクォータを確認してください")
    
    except Exception as e:
        print(f"❌ API呼び出しエラー: {e}")
        print(f"   APIキーが正しいか確認してください")


if __name__ == "__main__":
    test_elevenlabs()
