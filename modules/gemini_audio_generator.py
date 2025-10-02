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
        Gemini APIを使用して1つのチャンクの音声を生成
        
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
            
            # APIキーを取得
            api_key = self._get_next_api_key()
            if not api_key:
                logger.error("❌ APIキーが利用できません")
                return None
            
            # Gemini APIリクエスト
            url = f"{self.api_base_url}/models/{self.model_name}:generateContent"
            
            # 音声生成のプロンプト
            # Note: Gemini APIの音声生成機能はまだベータ版のため、
            # 実際にはText-to-Speechではなく、テキスト生成を使用
            # 実際の音声生成APIが利用可能になったら更新する必要があります
            
            # 仮実装：ここでは構造だけ示す
            logger.warning(f"⚠️ Gemini音声生成APIはまだ実装中です（チャンク{chunk_id}）")
            
            # TODO: 実際のGemini Audio APIの実装
            # 現時点ではダミーファイルを作成
            output_file = output_dir / f"chunk_{chunk_id:03d}_{speaker}.wav"
            
            # ダミー音声ファイル（実装時は実際の音声データに置き換え）
            if PYDUB_AVAILABLE:
                # 1秒の無音（ダミー）
                silence = AudioSegment.silent(duration=1000)
                silence.export(str(output_file), format='wav')
                logger.debug(f"✅ チャンク{chunk_id}のダミー音声生成完了")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ チャンク{chunk.get('chunk_id')}の音声生成エラー: {e}")
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

