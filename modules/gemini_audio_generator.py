"""
Google Gemini APIを使用した音声生成モジュール

Google AI Studio経由でポッドキャスト風の高品質な音声を生成
- 認証ファイル不要（APIキーのみ）
- 台本の適切な分割
- 複数APIキーによる並列処理
- 音声ファイルの自動結合
"""
import asyncio
import aiohttp
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import re
import json

# pydub for audio manipulation
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("pydub not available")

logger = logging.getLogger(__name__)


class GeminiAudioGenerator:
    """Google Gemini API音声生成クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        
        # 複数のAPIキーをサポート
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        # Gemini API設定
        self.api_base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_name = "gemini-1.5-flash"
        
        # 設定
        self.max_chunk_size = 5000  # 5000文字程度
        self.max_parallel_requests = 3  # 並列リクエスト数
        
        logger.info(f"✅ GeminiAudioGenerator初期化完了")
        logger.info(f"   - 利用可能なAPIキー: {len(self.api_keys)}個")
        logger.info(f"   - 最大並列リクエスト: {self.max_parallel_requests}")
        logger.info(f"   - チャンクサイズ: {self.max_chunk_size}文字")
    
    def _load_api_keys(self) -> List[str]:
        """複数のAPIキーを読み込む"""
        api_keys = []
        
        # メインのAPIキー
        if hasattr(self.settings, 'GEMINI_API_KEY') and self.settings.GEMINI_API_KEY:
            api_keys.append(self.settings.GEMINI_API_KEY)
        
        # サブのAPIキー（環境変数から）
        for i in range(1, 6):  # 最大5個まで
            key_name = f'GEMINI_API_KEY_{i}'
            if hasattr(self.settings, key_name):
                key = getattr(self.settings, key_name)
                if key:
                    api_keys.append(key)
        
        if not api_keys:
            logger.warning("⚠️ Gemini APIキーが設定されていません")
            logger.info("   APIキーの取得: https://aistudio.google.com/app/apikey")
        
        return api_keys
    
    def _get_next_api_key(self) -> Optional[str]:
        """次のAPIキーを取得（ラウンドロビン）"""
        if not self.api_keys:
            return None
        
        api_key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return api_key
    
    def split_script_into_chunks(self, script: str) -> List[Dict[str, Any]]:
        """
        台本を適切なチャンクに分割
        
        Args:
            script: 台本全文
            
        Returns:
            List[Dict]: チャンク情報のリスト
        """
        logger.info(f"📝 台本を分割中... (全{len(script)}文字)")
        
        # 🔧 メタ情報（タイトル、文字数など）を除去
        # 最初の[Aさん]または[Bさん]が出現するまでの部分をスキップ
        first_speaker_match = re.search(r'\[(Aさん|Bさん)\]', script)
        if first_speaker_match:
            removed_prefix = script[:first_speaker_match.start()]
            if removed_prefix.strip():
                logger.info(f"   メタ情報を除去: {len(removed_prefix)}文字")
                logger.debug(f"   除去内容: {removed_prefix[:100]}...")
            script = script[first_speaker_match.start():]
        
        chunks = []
        chunk_id = 0
        
        # 台本を話者ごとに分割
        pattern = r'\[(Aさん|Bさん)\]\s*'
        parts = re.split(pattern, script)
        
        current_speaker = None
        current_text = ""
        
        for i, part in enumerate(parts):
            if part in ['Aさん', 'Bさん']:
                # 前のチャンクを保存
                if current_text.strip():
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
        
        return chunks
    
    def _split_long_text(self, text: str, speaker: str, start_chunk_id: int) -> List[Dict[str, Any]]:
        """長いテキストを小さなチャンクに分割"""
        chunks = []
        
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
        
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'speaker': speaker,
                'chunk_id': chunk_id
            })
        
        return chunks
    
    async def generate_audio_chunk_with_gemini(
        self,
        chunk: Dict[str, Any],
        output_dir: Path
    ) -> Optional[Path]:
        """
        Google Cloud Text-to-Speech APIを使用して1つのチャンクの音声を生成
        
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
            
            # Google Cloud Text-to-Speech APIを使用
            try:
                from google.cloud import texttospeech
            except ImportError:
                logger.error("❌ google-cloud-texttospeech がインストールされていません")
                logger.info("   インストール: pip install google-cloud-texttospeech")
                return None
            
            # Google Cloud TTS クライアントを初期化（OAuth認証対応）
            try:
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.auth.transport.requests import Request
                import pickle
                
                SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
                credentials_path = Path(self.settings.GOOGLE_CREDENTIALS_PATH)
                
                if not credentials_path.exists():
                    logger.error(f"❌ 認証ファイルが見つかりません: {credentials_path}")
                    return None
                
                creds = None
                token_file = Path("assets/credentials/tts_token.pickle")
                
                # 既存のトークンを確認
                if token_file.exists():
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                
                # 認証が無効または期限切れの場合は再認証
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(credentials_path), SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    # トークンを保存
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
                
                client = texttospeech.TextToSpeechClient(credentials=creds)
                logger.debug(f"✅ Google TTSクライアント初期化成功（OAuth認証）")
                
            except Exception as e:
                logger.error(f"❌ Google TTSクライアントの初期化に失敗: {e}")
                logger.info("   認証情報を確認してください: assets/credentials/google-credentials.json")
                return None
            
            # 話者に応じて音声設定を選択（設定ファイルから取得）
            if speaker == 'A':
                # Aさん（男性）- 楽観派
                voice_name = self.settings.VOICE_A  # ja-JP-Neural2-C
                pitch = self.settings.VOICE_A_PITCH  # 0.0
                logger.debug(f"   音声設定: {voice_name} (ピッチ: {pitch})")
            else:
                # Bさん（女性）- 懐疑派
                voice_name = self.settings.VOICE_B  # ja-JP-Standard-A
                pitch = self.settings.VOICE_B_PITCH  # 0.0
                logger.debug(f"   音声設定: {voice_name} (ピッチ: {pitch})")
            
            # 音声生成リクエスト
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code='ja-JP',
                name=voice_name
            )
            
            # 話す速度を設定（Bさんの場合は設定から取得）
            if speaker == 'A':
                speaking_rate = 1.0  # 男性は標準速度
            else:
                speaking_rate = getattr(self.settings, 'VOICE_B_SPEAKING_RATE', 1.2)  # 女性は1.2
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                pitch=float(pitch),
                speaking_rate=float(speaking_rate)
            )
            
            # 音声生成を実行
            try:
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # 音声ファイルを保存
                output_file = output_dir / f"chunk_{chunk_id:03d}_{speaker}.wav"
                
                with open(output_file, 'wb') as out:
                    out.write(response.audio_content)
                
                file_size = output_file.stat().st_size
                logger.info(f"✅ チャンク{chunk_id}の音声生成完了: {output_file.name} ({file_size/1024:.1f}KB)")
                
                return output_file
                
            except Exception as e:
                logger.error(f"❌ Google TTS API呼び出しエラー: {e}")
                return None
            
        except Exception as e:
            logger.error(f"❌ チャンク{chunk.get('chunk_id')}の音声生成エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def generate_audio_parallel(
        self,
        chunks: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[Path]:
        """複数のチャンクを並列処理で音声生成"""
        logger.info(f"🎤 {len(chunks)}個のチャンクを並列処理で音声生成中...")
        
        semaphore = asyncio.Semaphore(self.max_parallel_requests)
        
        async def generate_with_semaphore(chunk):
            async with semaphore:
                return await self.generate_audio_chunk_with_gemini(chunk, output_dir)
        
        tasks = [generate_with_semaphore(chunk) for chunk in chunks]
        audio_files = await asyncio.gather(*tasks)
        
        audio_files = [f for f in audio_files if f is not None]
        logger.info(f"✅ {len(audio_files)}/{len(chunks)}個の音声ファイルを生成しました")
        
        return audio_files
    
    def merge_audio_files(
        self,
        audio_files: List[Path],
        output_file: Path
    ) -> Optional[Path]:
        """複数の音声ファイルを結合"""
        if not PYDUB_AVAILABLE:
            logger.error("❌ pydubがインストールされていません")
            return None
        
        try:
            logger.info(f"🔗 {len(audio_files)}個の音声ファイルを結合中...")
            
            audio_files = sorted(audio_files, key=lambda x: x.name)
            combined = AudioSegment.from_wav(str(audio_files[0]))
            
            for audio_file in audio_files[1:]:
                audio = AudioSegment.from_wav(str(audio_file))
                combined += AudioSegment.silent(duration=300)  # 300ms
                combined += audio
            
            combined.export(str(output_file), format='wav')
            
            duration_seconds = len(combined) / 1000
            logger.info(f"✅ 音声ファイルを結合しました: {output_file.name}")
            logger.info(f"   総時間: {duration_seconds / 60:.1f}分")
            
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
        """台本全体の音声を生成"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            full_script = script_data.get('full_script', '')
            if not full_script:
                logger.error("❌ 台本が空です")
                return None
            
            logger.info(f"🎬 音声生成を開始します（Gemini API）")
            logger.info(f"   台本文字数: {len(full_script)}文字")
            
            # ステップ1: 台本を分割
            chunks = self.split_script_into_chunks(full_script)
            if not chunks:
                return None
            
            # ステップ2: 並列音声生成
            chunk_dir = output_dir / f"chunks_{execution_id}"
            chunk_dir.mkdir(exist_ok=True)
            
            audio_files = await self.generate_audio_parallel(chunks, chunk_dir)
            if not audio_files:
                return None
            
            # ステップ3: 音声結合
            final_audio_file = output_dir / f"podcast_{execution_id}.wav"
            merged_file = self.merge_audio_files(audio_files, final_audio_file)
            
            if not merged_file:
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
            return None

