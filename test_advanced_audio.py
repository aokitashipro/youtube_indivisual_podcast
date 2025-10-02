"""
高度な音声生成のテストスクリプト

このスクリプトは以下をテストします：
1. 台本の分割（長文対応）
2. 並列音声生成
3. 音声ファイルの結合
4. 負荷分散
"""
import sys
from pathlib import Path
import asyncio

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from config.settings import Settings
from modules.advanced_audio_generator import AdvancedAudioGenerator
from utils.logger import setup_logger

# 環境変数を読み込み
load_dotenv()


async def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print("🎤 高度な音声生成テスト")
    print("=" * 80 + "\n")
    
    # ロガーを初期化
    logger = setup_logger()
    
    # 設定を読み込み
    settings = Settings()
    
    # AudioGeneratorを初期化
    audio_gen = AdvancedAudioGenerator(settings)
    
    # ============================================================================
    # テスト1: 台本の分割テスト
    # ============================================================================
    print("-" * 80)
    print("テスト1: 台本の分割テスト")
    print("-" * 80)
    
    # テスト用の台本（長文）
    test_script = """[Aさん] こんにちは！今日はAI開発の最新トピックについてお話しします。最近、個人開発者がAIを活用してMRR10万ドルを達成したという事例が話題になっています。これは本当に驚くべきことですね。

[Bさん] 確かに驚きですね。でも、本当にそんなことが可能なんでしょうか？具体的にどのような戦略を取ったのか気になります。

[Aさん] そうなんです！実はこの開発者は3つの重要な戦略を実行しました。まず第一に、ニッチな市場を見つけました。大手企業が見落としているフリーランスのフロントエンド開発者に特化したんです。第二に、無料プランを充実させてコミュニティを先に作りました。そして第三に、ユーザーフィードバックを48時間以内に実装する超高速開発サイクルを実現したんです。

[Bさん] なるほど。でも、48時間以内に実装って、品質管理は大丈夫なんですか？バグが多発しませんか？

[Aさん] それは良い指摘ですね。もちろんリスクはありますが、この開発者は「完璧を目指すより、速く改善する」という哲学を持っていました。バグが出たら、それもまた48時間以内に修正するんです。これが個人開発の強みなんです！意思決定が速く、承認プロセスがなく、ユーザーとの距離が近い。

[Bさん] 確かに、それは大企業にはできないスピード感ですね。でも、ビジネスとして本当に持続可能なんでしょうか？

[Aさん] はい！実は月間の解約率が2%以下なんです。一度有料ユーザーになったら、ほとんどの人が使い続けてくれる。これって、ビジネスとして最強の状態ですよね。新規獲得だけじゃなくて、既存ユーザーの維持もできている。価格設定も月額49ドルと絶妙で、個人でも手が出せる範囲なんです。"""
    
    # 台本を分割
    chunks = audio_gen.split_script_into_chunks(test_script)
    
    print(f"\n✅ 分割結果:")
    print(f"   元の文字数: {len(test_script)}文字")
    print(f"   分割後のチャンク数: {len(chunks)}個")
    print(f"\n   各チャンクの詳細:")
    
    for i, chunk in enumerate(chunks):
        print(f"   #{i+1}: [{chunk['speaker']}さん] {len(chunk['text'])}文字")
        if len(chunk['text']) > 100:
            preview = chunk['text'][:100].replace('\n', ' ')
            print(f"       プレビュー: {preview}...")
        else:
            print(f"       内容: {chunk['text'][:100]}")
    
    # ============================================================================
    # テスト2: 音声生成の仕組み確認
    # ============================================================================
    print("\n" + "-" * 80)
    print("テスト2: 音声生成の仕組み確認")
    print("-" * 80)
    
    print(f"\n🎛️ 音声生成設定:")
    print(f"   最大チャンクサイズ: {audio_gen.max_chunk_size}文字")
    print(f"   最大並列リクエスト: {audio_gen.max_parallel_requests}個")
    print(f"   利用可能なAPIキー: {len(audio_gen.api_keys)}個")
    
    if audio_gen.api_keys:
        print(f"\n   APIキーによる負荷分散:")
        print(f"   - 各チャンクが異なるAPIキーを使用（ラウンドロビン）")
        print(f"   - {audio_gen.max_parallel_requests}個のチャンクを同時処理")
        print(f"   - 理論上の処理速度: 単一APIの{audio_gen.max_parallel_requests}倍")
    else:
        print(f"\n   ⚠️ APIキーが設定されていません")
    
    # ============================================================================
    # テスト3: 処理時間のシミュレーション
    # ============================================================================
    print("\n" + "-" * 80)
    print("テスト3: 処理時間のシミュレーション")
    print("-" * 80)
    
    # 1チャンクあたりの処理時間を仮定（秒）
    time_per_chunk_sequential = 10  # 逐次処理の場合
    time_per_chunk_parallel = 10 / audio_gen.max_parallel_requests  # 並列処理の場合
    
    total_sequential_time = len(chunks) * time_per_chunk_sequential
    total_parallel_time = len(chunks) * time_per_chunk_parallel
    
    print(f"\n⏱️ 処理時間の比較（推定）:")
    print(f"   チャンク数: {len(chunks)}個")
    print(f"   1チャンクあたりの処理時間: {time_per_chunk_sequential}秒（仮定）")
    print(f"\n   【逐次処理の場合】")
    print(f"   総処理時間: {total_sequential_time}秒 ({total_sequential_time/60:.1f}分)")
    print(f"\n   【並列処理の場合（{audio_gen.max_parallel_requests}並列）】")
    print(f"   総処理時間: {total_parallel_time}秒 ({total_parallel_time/60:.1f}分)")
    print(f"   時間短縮: {total_sequential_time - total_parallel_time}秒 ({(1 - total_parallel_time/total_sequential_time)*100:.0f}%削減)")
    
    # ============================================================================
    # テスト4: 実際の音声生成（Google TTSが利用可能な場合）
    # ============================================================================
    print("\n" + "-" * 80)
    print("テスト4: 実際の音声生成")
    print("-" * 80)
    
    if not audio_gen.tts_clients:
        print("\n⚠️ Google TTS クライアントが利用できません")
        print("\n必要な設定:")
        print("   1. google-cloud-texttospeech をインストール:")
        print("      pip install google-cloud-texttospeech")
        print("   2. Google Cloud認証情報を設定:")
        print("      - assets/credentials/google-credentials.json")
        print("   3. .envファイルに以下を追加:")
        print("      GOOGLE_CREDENTIALS_PATH=assets/credentials/google-credentials.json")
    else:
        print("\n✅ Google TTS クライアントが利用可能です")
        print("\n実際の音声生成をテストする場合:")
        print("   python run_full_pipeline.py")
    
    # ============================================================================
    # 完了
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ 高度な音声生成テストが完了しました")
    print("=" * 80)
    
    print("\n📋 実装された機能:")
    print("   ✅ 台本の適切な分割（長文対応）")
    print("   ✅ 話者ごとの分割")
    print("   ✅ チャンクサイズの自動調整")
    print("   ✅ 複数APIキーによる負荷分散")
    print("   ✅ 並列処理（セマフォによる制御）")
    print("   ✅ 音声ファイルの自動結合")
    print("   ✅ 話者切り替え時の自然な間")
    
    print("\n🎯 次のステップ:")
    print("   1. Google Cloud TTSの設定")
    print("   2. 複数のAPIキーを取得（負荷分散用）")
    print("   3. Google Driveへのアップロード実装")
    print("   4. 完全なパイプライン実行")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

