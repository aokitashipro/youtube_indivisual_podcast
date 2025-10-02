"""
高度な音声生成モジュール

Google Gemini APIを使用した音声生成with:
- 台本の適切な分割（長文対応）
- 音声ファイルの自動結合
- 複数APIキーによる並列処理
- 負荷分散
- Google Driveへのアップロード
"""
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
import re
from datetime import datetime
import json

# Google Cloud TTS
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    logging.warning("Google Cloud Text-to-Speech not available")

# pydub for audio manipulation
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("pydub not available")

logger = logging.getLogger(__name__)


class AdvancedAudioGenerator:
    """高度な音声生成クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        
        # 複数のAPIキーをサポート
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        # TTSクライアントのプール
        self.tts_clients = []
        self._initialize_tts_clients()
        
        # 設定
        self.max_chunk_size = 5000  # Google TTSの制限（約5000文字）
        self.max_parallel_requests = 3  # 並列リクエスト数
        
        logger.info(f"✅ AdvancedAudioGenerator初期化完了")
        logger.info(f"   - 利用可能なAPIキー: {len(self.api_keys)}個")
        logger.info(f"   - 最大並列リクエスト: {self.max_parallel_requests}")
        logger.info(f"   - チャンクサイズ: {self.max_chunk_size}文字")
    
    def _load_api_keys(self) -> List[str]:
        """複数のAPIキーを読み込む"""
        api_keys = []
        
        # メインのAPIキー
        if hasattr(self.settings, 'GOOGLE_TTS_API_KEY') and self.settings.GOOGLE_TTS_API_KEY:
            api_keys.append(self.settings.GOOGLE_TTS_API_KEY)
        
        # サブのAPIキー（環境変数から）
        for i in range(1, 6):  # 最大5個まで
            key_name = f'GOOGLE_TTS_API_KEY_{i}'
            if hasattr(self.settings, key_name):
                key = getattr(self.settings, key_name)
                if key:
                    api_keys.append(key)
        
        if not api_keys:
            logger.warning("⚠️ Google TTS APIキーが設定されていません")
        
        return api_keys
    
    def _initialize_tts_clients(self):
        """TTSクライアントを初期化"""
        if not GOOGLE_TTS_AVAILABLE:
            logger.warning("⚠️ Google Cloud Text-to-Speech がインストールされていません")
            return
        
        # 各APIキーに対してクライアントを作成
        # 注: Google Cloud TTSはサービスアカウントを使用するため、
        # 実際には credentials.json を使用します
        try:
            # 認証情報ファイルが存在する場合
            if hasattr(self.settings, 'GOOGLE_CREDENTIALS_PATH'):
                client = texttospeech.TextToSpeechClient.from_service_account_file(
                    self.settings.GOOGLE_CREDENTIALS_PATH
                )
                self.tts_clients.append(client)
                logger.info("✅ Google TTS クライアントを初期化しました")
        except Exception as e:
            logger.error(f"❌ Google TTS クライアント初期化エラー: {e}")
    
    def _get_next_client(self):
        """次のTTSクライアントを取得（ラウンドロビン）"""
        if not self.tts_clients:
            return None
        
        client = self.tts_clients[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.tts_clients)
        return client
    
    def split_script_into_chunks(self, script: str) -> List[Dict[str, Any]]:
        """
        台本を適切なチャンクに分割
        
        Args:
            script: 台本全文
            
        Returns:
            List[Dict]: チャンク情報のリスト
            [
                {
                    'text': 'チャンクのテキスト',
                    'speaker': 'A' or 'B',
                    'chunk_id': 0
                },
                ...
            ]
        """
        logger.info(f"📝 台本を分割中... (全{len(script)}文字)")
        
        chunks = []
        chunk_id = 0
        
        # 台本を話者ごとに分割
        # パターン: [Aさん] または [Bさん]
        pattern = r'\[(Aさん|Bさん)\]\s*'
        parts = re.split(pattern, script)
        
        current_speaker = None
        current_text = ""
        
        for i, part in enumerate(parts):
            if part in ['Aさん', 'Bさん']:
                # 前のチャンクを保存
                if current_text.strip():
                    # 長すぎる場合はさらに分割
                    sub_chunks = self._split_long_text(current_text, current_speaker, chunk_id)
                    chunks.extend(sub_chunks)
                    chunk_id += len(sub_chunks)
                
                # 新しい話者
                current_speaker = 'A' if part == 'Aさん' else 'B'
                current_text = ""
            else:
                current_text += part
        
        # 最後のチャンク
        if current_text.strip() and current_speaker:
            sub_chunks = self._split_long_text(current_text, current_speaker, chunk_id)
            chunks.extend(sub_chunks)
        
        logger.info(f"✅ 台本を{len(chunks)}個のチャンクに分割しました")
        
        # チャンク情報を表示
        for i, chunk in enumerate(chunks[:5]):  # 最初の5個を表示
            text_preview = chunk['text'][:50].replace('\n', ' ')
            logger.info(f"   チャンク{i}: [{chunk['speaker']}さん] {text_preview}... ({len(chunk['text'])}文字)")
        
        if len(chunks) > 5:
            logger.info(f"   ... 他{len(chunks) - 5}個のチャンク")
        
        return chunks
    
    def _split_long_text(self, text: str, speaker: str, start_chunk_id: int) -> List[Dict[str, Any]]:
        """
        長いテキストをさらに小さなチャンクに分割
        
        Args:
            text: 分割するテキスト
            speaker: 話者（'A' or 'B'）
            start_chunk_id: 開始チャンクID
            
        Returns:
            List[Dict]: チャンク情報のリスト
        """
        chunks = []
        
        # max_chunk_size以下の場合はそのまま
        if len(text) <= self.max_chunk_size:
            chunks.append({
                'text': text.strip(),
                'speaker': speaker,
                'chunk_id': start_chunk_id
            })
            return chunks
        
        # 文単位で分割
        sentences = re.split(r'([。！？\n])', text)
        
        current_chunk = ""
        chunk_id = start_chunk_id
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
            
            full_sentence = sentence + delimiter
            
            # チャンクサイズを超える場合
            if len(current_chunk) + len(full_sentence) > self.max_chunk_size:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'speaker': speaker,
                        'chunk_id': chunk_id
                    })
                    chunk_id += 1
                current_chunk = full_sentence
            else:
                current_chunk += full_sentence
        
        # 最後のチャンク
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'speaker': speaker,
                'chunk_id': chunk_id
            })
        
        return chunks
    
    async def generate_audio_chunk(
        self,
        chunk: Dict[str, Any],
        output_dir: Path
    ) -> Optional[Path]:
        """
        1つのチャンクの音声を生成
        
        Args:
            chunk: チャンク情報
            output_dir: 出力ディレクトリ
            
        Returns:
            Optional[Path]: 生成された音声ファイルのパス
        """
        try:
            chunk_id = chunk['chunk_id']
            speaker = chunk['speaker']
            text = chunk['text']
            
            logger.debug(f"🎤 チャンク{chunk_id}の音声生成中... (話者: {speaker}さん, {len(text)}文字)")
            
            # TTSクライアントを取得
            client = self._get_next_client()
            
            if not client:
                logger.error("❌ TTSクライアントが利用できません")
                return None
            
            # 音声設定
            voice_name = self.settings.VOICE_A if speaker == 'A' else self.settings.VOICE_B
            pitch = self.settings.VOICE_A_PITCH if speaker == 'A' else self.settings.VOICE_B_PITCH
            
            # 音声生成リクエスト
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code='ja-JP',
                name=voice_name
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                pitch=float(pitch),
                speaking_rate=1.0
            )
            
            # 音声生成（同期処理をasyncで実行）
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
            )
            
            # 音声ファイルを保存
            output_file = output_dir / f"chunk_{chunk_id:03d}_{speaker}.wav"
            with open(output_file, 'wb') as f:
                f.write(response.audio_content)
            
            logger.debug(f"✅ チャンク{chunk_id}の音声生成完了: {output_file.name}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ チャンク{chunk.get('chunk_id')}の音声生成エラー: {e}")
            return None
    
    async def generate_audio_parallel(
        self,
        chunks: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[Path]:
        """
        複数のチャンクを並列処理で音声生成
        
        Args:
            chunks: チャンクのリスト
            output_dir: 出力ディレクトリ
            
        Returns:
            List[Path]: 生成された音声ファイルのリスト
        """
        logger.info(f"🎤 {len(chunks)}個のチャンクを並列処理で音声生成中...")
        logger.info(f"   並列度: {self.max_parallel_requests}")
        
        # セマフォで並列度を制限
        semaphore = asyncio.Semaphore(self.max_parallel_requests)
        
        async def generate_with_semaphore(chunk):
            async with semaphore:
                return await self.generate_audio_chunk(chunk, output_dir)
        
        # 全チャンクを並列処理
        tasks = [generate_with_semaphore(chunk) for chunk in chunks]
        audio_files = await asyncio.gather(*tasks)
        
        # Noneを除外
        audio_files = [f for f in audio_files if f is not None]
        
        logger.info(f"✅ {len(audio_files)}/{len(chunks)}個の音声ファイルを生成しました")
        
        return audio_files
    
    def merge_audio_files(
        self,
        audio_files: List[Path],
        output_file: Path
    ) -> Optional[Path]:
        """
        複数の音声ファイルを結合
        
        Args:
            audio_files: 音声ファイルのリスト（順番通り）
            output_file: 出力ファイル
            
        Returns:
            Optional[Path]: 結合された音声ファイルのパス
        """
        if not PYDUB_AVAILABLE:
            logger.error("❌ pydubがインストールされていません")
            return None
        
        try:
            logger.info(f"🔗 {len(audio_files)}個の音声ファイルを結合中...")
            
            # 音声ファイルを順番にソート
            audio_files = sorted(audio_files, key=lambda x: x.name)
            
            # 最初のファイルを読み込み
            combined = AudioSegment.from_wav(str(audio_files[0]))
            
            # 残りのファイルを結合
            for audio_file in audio_files[1:]:
                audio = AudioSegment.from_wav(str(audio_file))
                
                # 話者が変わる場合は短い無音を追加（自然な間）
                combined += AudioSegment.silent(duration=300)  # 300ms
                combined += audio
            
            # 結合した音声を保存
            combined.export(str(output_file), format='wav')
            
            duration_seconds = len(combined) / 1000
            logger.info(f"✅ 音声ファイルを結合しました: {output_file.name}")
            logger.info(f"   総時間: {duration_seconds / 60:.1f}分 ({duration_seconds:.1f}秒)")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ 音声ファイルの結合エラー: {e}")
            return None
    
    async def generate_full_audio(
        self,
        script_data: Dict[str, Any],
        output_dir: Path,
        execution_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        台本全体の音声を生成（分割→並列生成→結合）
        
        Args:
            script_data: 台本データ
            output_dir: 出力ディレクトリ
            execution_id: 実行ID
            
        Returns:
            Optional[Dict]: 音声情報
            {
                'audio_file': Path,
                'duration_seconds': float,
                'chunk_count': int
            }
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 台本を取得
            full_script = script_data.get('full_script', '')
            
            if not full_script:
                logger.error("❌ 台本が空です")
                return None
            
            logger.info(f"🎬 音声生成を開始します")
            logger.info(f"   台本文字数: {len(full_script)}文字")
            
            # ステップ1: 台本を分割
            chunks = self.split_script_into_chunks(full_script)
            
            if not chunks:
                logger.error("❌ 台本の分割に失敗しました")
                return None
            
            # ステップ2: チャンクごとに音声生成（並列処理）
            chunk_dir = output_dir / f"chunks_{execution_id}"
            chunk_dir.mkdir(exist_ok=True)
            
            audio_files = await self.generate_audio_parallel(chunks, chunk_dir)
            
            if not audio_files:
                logger.error("❌ 音声ファイルの生成に失敗しました")
                return None
            
            # ステップ3: 音声ファイルを結合
            final_audio_file = output_dir / f"podcast_{execution_id}.wav"
            merged_file = self.merge_audio_files(audio_files, final_audio_file)
            
            if not merged_file:
                logger.error("❌ 音声ファイルの結合に失敗しました")
                return None
            
            # 音声情報を取得
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_wav(str(merged_file))
                duration_seconds = len(audio) / 1000
            else:
                duration_seconds = 0
            
            return {
                'audio_file': merged_file,
                'duration_seconds': duration_seconds,
                'chunk_count': len(chunks),
                'chunk_files': audio_files
            }
            
        except Exception as e:
            logger.error(f"❌ 音声生成エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def upload_to_google_drive(self, audio_file: Path) -> Optional[str]:
        """
        音声ファイルをGoogle Driveにアップロード
        
        Args:
            audio_file: 音声ファイル
            
        Returns:
            Optional[str]: Google DriveのURL
        """
        # TODO: Google Drive APIの実装
        logger.warning("⚠️ Google Driveへのアップロードは未実装です")
        logger.info(f"   ローカルファイル: {audio_file}")
        
        # 仮のURLを返す（実装時は実際のDrive URLに変更）
        return f"file://{audio_file.absolute()}"

