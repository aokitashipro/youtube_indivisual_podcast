"""
実際の対談音声生成テスト

更新された音声設定（ja-JP-Standard-A）で対談形式の音声を生成
"""
import sys
from pathlib import Path
import asyncio

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.gemini_audio_generator import GeminiAudioGenerator
from modules.google_drive_oauth import GoogleDriveOAuthUploader
from utils.logger import setup_logger

load_dotenv()


async def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎤 実際の対談音声生成テスト")
    print("=" * 80 + "\n")
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    print(f"🎛️ 音声設定:")
    print(f"   Aさん（男性）: {settings.VOICE_A} (ピッチ: {settings.VOICE_A_PITCH})")
    print(f"   Bさん（女性）: {settings.VOICE_B} (ピッチ: {settings.VOICE_B_PITCH})")
    
    # ============================================================================
    # 実際の対談台本（参考元記事スタイル）
    # ============================================================================
    print("\n" + "-" * 80)
    print("対談台本の準備")
    print("-" * 80)
    
    dialogue_script = """[Aさん] こんにちは！今日はAI技術の最新動向についてお話しします。最近、個人開発者がAIを活用して月収100万円を達成したという事例が話題になっていますね。

[Bさん] そうですね。でも、本当にそんなことが可能なんでしょうか？AI技術を使えば誰でも稼げるというのは、少し疑わしい気がします。

[Aさん] 確かに疑問に思うのも当然です。でも、実際に成功している開発者の多くは、特定のニッチな問題を解決するツールを作っているんです。例えば、フリーランスのデザイナー向けの効率化ツールや、小規模企業向けの顧客管理システムなどですね。

[Bさん] なるほど。でも、そういったツールは既に大手企業が提供しているものが多いのではないですか？個人開発者に勝ち目はあるんでしょうか？

[Aさん] 実は、そこが個人開発者の強みなんです！大手企業は大規模なソリューションを提供しますが、個人開発者は特定のユーザーの細かいニーズに応えることができる。そして、フィードバックを素早く反映できるスピード感が武器になります。

[Bさん] 確かに、大企業では意思決定に時間がかかりますよね。でも、技術的な質はどうなんでしょうか？個人開発だけでは限界があるのでは？

[Aさん] それは良い指摘ですね。でも、現在はAI技術が発達しているので、個人でも高品質なプロダクトを作ることが可能になりました。ChatGPTやClaudeなどのAIアシスタントを活用すれば、コーディングからマーケティングまで幅広くサポートしてもらえます。

[Bさん] なるほど、AIを活用することで個人でも競争力のあるプロダクトが作れるということですね。でも、マーケティングや顧客獲得はどうするんですか？

[Aさん] これもAIの活用が効果的です。SEO対策、SNS運用、コンテンツマーケティングなど、多くの作業をAIがサポートしてくれます。ただし、重要なのは「継続すること」と「ユーザーフィードバックを真摯に受け止めること」です。

[Bさん] 確かに、技術だけでなく継続性やユーザーとの関係性が重要ですね。でも、失敗のリスクはどう考えればいいでしょうか？

[Aさん] 良い質問ですね。失敗のリスクを最小限に抑えるには、まず小規模から始めることです。MVP（最小実行可能プロダクト）を作って、ユーザーの反応を見ながら改善していく。そして、本業を維持しながら副業として始めるのが現実的です。

[Bさん] そうですね。いきなり大きな投資をするのではなく、段階的に進めることが大切ですね。最後に、これから始めたい人へのアドバイスはありますか？

[Aさん] はい！まずは自分の経験や専門知識を活かせる分野を見つけること。そして、AIツールを積極的に活用して効率化を図ること。最後に、完璧を目指すより、まずは動かすことを優先することです。完璧なプロダクトより、改善し続けるプロダクトの方がユーザーに愛されますからね。

[Bさん] 素晴らしいアドバイスですね。AI技術の発達により、個人でも大きなチャンスがある時代になったということですね。今日はありがとうございました！"""
    
    print(f"✅ 対談台本を準備しました ({len(dialogue_script)}文字)")
    
    # ============================================================================
    # Gemini Audio Generator の初期化
    # ============================================================================
    print("\n" + "-" * 80)
    print("音声生成システムの初期化")
    print("-" * 80)
    
    audio_gen = GeminiAudioGenerator(settings)
    
    print(f"✅ 初期化完了")
    print(f"   - 利用可能なAPIキー: {len(audio_gen.api_keys)}個")
    print(f"   - 最大並列リクエスト: {audio_gen.max_parallel_requests}個")
    
    # ============================================================================
    # 台本の分割
    # ============================================================================
    print("\n" + "-" * 80)
    print("台本の分割")
    print("-" * 80)
    
    chunks = audio_gen.split_script_into_chunks(dialogue_script)
    
    print(f"✅ 分割完了: {len(chunks)}個のチャンク")
    print("\n各チャンクの詳細:")
    for i, chunk in enumerate(chunks):
        speaker = "Aさん（男性）" if chunk['speaker'] == 'A' else "Bさん（女性）"
        print(f"   #{i+1:2d}: [{speaker}] {len(chunk['text'])}文字")
    
    # ============================================================================
    # 実際の音声生成
    # ============================================================================
    print("\n" + "-" * 80)
    print("実際の音声生成")
    print("-" * 80)
    
    # 出力ディレクトリを作成
    output_dir = Path("temp/dialogue_audio")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 出力ディレクトリ: {output_dir}")
    print(f"🎤 {len(chunks)}個のチャンクを並列処理で音声生成中...")
    
    try:
        # 音声生成を実行
        audio_files = await audio_gen.generate_audio_parallel(chunks, output_dir)
        
        print(f"\n✅ 音声生成完了: {len(audio_files)}個のファイル")
        
        # 生成されたファイルを確認
        for i, audio_file in enumerate(audio_files):
            if audio_file and audio_file.exists():
                size_kb = audio_file.stat().st_size / 1024
                print(f"   #{i+1:2d}: {audio_file.name} ({size_kb:.1f}KB)")
            else:
                print(f"   #{i+1:2d}: 生成失敗")
        
        # 音声ファイルの結合
        if audio_files:
            print(f"\n🔗 音声ファイルの結合")
            final_audio = output_dir / "dialogue_final.wav"
            
            merged_file = audio_gen.merge_audio_files(audio_files, final_audio)
            
            if merged_file and merged_file.exists():
                size_kb = merged_file.stat().st_size / 1024
                print(f"✅ 結合完了: {merged_file.name} ({size_kb:.1f}KB)")
                
                # Google Driveへのアップロード
                print(f"\n📤 Google Driveへのアップロード")
                uploader = GoogleDriveOAuthUploader(settings)
                
                result = uploader.upload_file(
                    file_path=merged_file,
                    file_name="ai_dialogue_final.wav",
                    mime_type='audio/wav',
                    make_public=True
                )
                
                if result:
                    print(f"✅ アップロード成功！")
                    print(f"   ファイルID: {result['file_id']}")
                    print(f"   表示URL: {result['web_view_link']}")
                    print(f"\n🌐 ブラウザで確認:")
                    print(f"   {result['web_view_link']}")
                    
                    print(f"\n🎉 実際の対談音声が完成しました！")
                    print(f"   Aさん（男性）: {settings.VOICE_A}")
                    print(f"   Bさん（女性）: {settings.VOICE_B}")
                    print(f"   総再生時間: 約{len(chunks) * 2}秒（推定）")
                else:
                    print(f"❌ アップロードに失敗しました")
            else:
                print(f"❌ 音声ファイルの結合に失敗しました")
        
    except Exception as e:
        print(f"❌ 音声生成エラー: {e}")
        import traceback
        traceback.print_exc()
    
    # ============================================================================
    # 完了
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ 実際の対談音声生成テストが完了しました")
    print("=" * 80)
    
    print("\n📋 実装された機能:")
    print("   ✅ 実際の対談台本での音声生成")
    print("   ✅ 男性音声（ja-JP-Neural2-C）")
    print("   ✅ 女性音声（ja-JP-Standard-A）")
    print("   ✅ 並列処理による高速生成")
    print("   ✅ 音声ファイルの自動結合")
    print("   ✅ Google Driveへの自動アップロード")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
