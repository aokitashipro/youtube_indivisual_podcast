"""
字幕生成モジュール

ElevenLabs STT APIを使用して音声から字幕を生成し、
元の台本テキストとマッチングして正確な字幕データを作成
"""
import os
import logging
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import difflib

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """字幕生成クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.api_key = settings.ELEVENLABS_API_KEY
        
        if not self.api_key or self.api_key == 'your_elevenlabs_api_key_here':
            logger.warning("⚠️ ElevenLabs APIキーが設定されていません")
        else:
            logger.info("✅ SubtitleGenerator初期化完了")
    
    async def generate_subtitles(
        self,
        audio_path: str,
        script_content: Dict[str, Any],
        time_offset: float = 0.0
    ) -> Dict[str, Any]:
        """
        音声から字幕データを生成（STT + マッチング）
        
        処理フロー:
        1. ElevenLabs STTで音声→テキスト変換（タイムスタンプ付き）
        2. 元の台本テキストとマッチング
        3. タイムスタンプ + 正確なテキストを組み合わせ
        4. タイミングオフセットを適用
        
        Args:
            audio_path: 音声ファイルのパス
            script_content: 台本データ（full_scriptを含む）
            time_offset: 字幕のタイミング調整（秒）
                        正の値: 字幕を遅らせる（音声に対して字幕が早い場合）
                        負の値: 字幕を早める（音声に対して字幕が遅い場合）
            
        Returns:
            字幕データ
            {
                "subtitles": [
                    {
                        "start": float,  # 開始時間（秒）
                        "end": float,    # 終了時間（秒）
                        "text": str,     # 字幕テキスト
                        "speaker": str   # 話者（A/B）
                    }
                ],
                "total_count": int,
                "total_duration": float
            }
        """
        try:
            logger.info("🎤 ElevenLabs STTで音声を文字起こし中...")
            
            # ElevenLabs STTで文字起こし
            transcription_data = self._transcribe_with_elevenlabs(audio_path)
            
            if not transcription_data:
                logger.warning("⚠️ STTの結果が空です。台本から簡易的に字幕を生成します")
                return self._generate_simple_subtitles_from_script(
                    script_content,
                    audio_path
                )
            
            logger.info("📝 台本とマッチング中...")
            
            # 元の台本テキストを取得
            original_script = script_content.get("full_script", "")
            if not original_script:
                original_script = self._extract_text_from_dialogue(
                    script_content.get("dialogue", [])
                )
            
            # タイムスタンプとテキストをマッチング
            subtitles = self._match_timestamps_with_script(
                transcription_data,
                original_script
            )
            
            # タイミングオフセットを適用
            if time_offset != 0.0:
                logger.info(f"⏰ タイミングオフセットを適用: {time_offset:+.2f}秒")
                for subtitle in subtitles:
                    subtitle['start'] = max(0, subtitle['start'] + time_offset)
                    subtitle['end'] = max(0, subtitle['end'] + time_offset)
            
            result = {
                "subtitles": subtitles,
                "total_count": len(subtitles),
                "total_duration": subtitles[-1]["end"] if subtitles else 0
            }
            
            logger.info(f"✅ 字幕生成完了: {len(subtitles)}個のセグメント")
            return result
            
        except Exception as e:
            logger.error(f"❌ 字幕生成エラー: {e}")
            # フォールバック: 台本から簡易的に生成
            logger.info("📝 台本から簡易的に字幕を生成します")
            return self._generate_simple_subtitles_from_script(
                script_content,
                audio_path
            )
    
    def _transcribe_with_elevenlabs(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        ElevenLabs STT APIで音声を文字起こし
        
        Args:
            audio_path: 音声ファイルのパス
            
        Returns:
            文字起こし結果（タイムスタンプ付き）
        """
        try:
            if not self.api_key or self.api_key == 'your_elevenlabs_api_key_here':
                logger.warning("⚠️ ElevenLabs APIキーが未設定のため、STTをスキップ")
                return None
            
            url = "https://api.elevenlabs.io/v1/speech-to-text"
            
            # 音声ファイルを読み込み
            with open(audio_path, 'rb') as audio_file:
                # ElevenLabs APIの正しい形式
                files = {
                    'file': (Path(audio_path).name, audio_file, 'audio/wav')
                }
                headers = {
                    'xi-api-key': self.api_key
                }
                data = {
                    'model_id': 'scribe_v1',  # STT専用モデル
                    'language_code': 'ja'  # 日本語を指定
                }
                
                logger.info(f"🌐 ElevenLabs STT APIにリクエスト中... ({Path(audio_path).name})")
                
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=120  # タイムアウトを延長
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get('text', '')
                    logger.info(f"✅ STT成功: {len(text)}文字")
                    logger.info(f"   認識テキスト: {text[:100]}...")
                    
                    # alignment情報があるかチェック
                    if 'alignment' in result:
                        logger.info(f"   ✅ タイムスタンプ情報を取得しました")
                    else:
                        logger.warning(f"   ⚠️ タイムスタンプ情報がありません")
                    
                    return result
                else:
                    logger.error(f"❌ STT APIエラー: {response.status_code}")
                    logger.error(f"   レスポンス: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ STT実行エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _match_timestamps_with_script(
        self,
        transcription_data: Dict[str, Any],
        original_script: str
    ) -> List[Dict[str, Any]]:
        """
        STTの結果と元の台本をマッチングして正確な字幕を生成
        
        Args:
            transcription_data: STTの結果
            original_script: 元の台本テキスト
            
        Returns:
            字幕データのリスト
        """
        subtitles = []
        
        # STTの結果からテキストとタイムスタンプを取得
        stt_text = transcription_data.get('text', '')
        
        # ElevenLabsのレスポンス構造を確認
        # 'alignment'や'words'などのキーがあるかチェック
        alignment = transcription_data.get('alignment', {})
        words = transcription_data.get('words', [])
        
        logger.info(f"📊 STT結果の構造:")
        logger.info(f"   - テキスト: {len(stt_text)}文字")
        logger.info(f"   - alignment: {bool(alignment)}")
        logger.info(f"   - words: {len(words)}個")
        
        # タイムスタンプ情報がない場合は台本から生成
        if not words and not alignment:
            logger.warning("⚠️ タイムスタンプ情報がないため、台本から推定します")
            return self._create_simple_subtitles(original_script)
        
        # 台本から話者情報を抽出
        script_segments = self._parse_script_segments(original_script)
        
        # wordsがある場合は、それを使ってタイムスタンプを推定
        if words:
            logger.info("✅ 単語レベルのタイムスタンプを使用")
            return self._create_subtitles_from_words(words, script_segments)
        
        # alignmentがある場合はそれを使用
        if alignment:
            logger.info("✅ アライメント情報を使用")
            return self._create_subtitles_from_alignment(alignment, script_segments)
        
        # フォールバック
        return self._create_simple_subtitles(original_script)
    
    def _create_subtitles_from_words(
        self,
        words: List[Dict[str, Any]],
        script_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        単語レベルのタイムスタンプから字幕を生成
        
        Args:
            words: 単語のリスト（タイムスタンプ付き）
            script_segments: 台本のセグメント
            
        Returns:
            字幕データのリスト
        """
        # wordsの構造をデバッグ
        if words:
            logger.info(f"🔍 Words構造（最初の3個）:")
            for word in words[:3]:
                logger.info(f"   {word}")
        
        subtitles = []
        
        # 単語を台本のセグメントにグループ化
        word_index = 0
        
        for seg_idx, segment in enumerate(script_segments):
            segment_text = segment['text']
            segment_chars = segment_text.replace(' ', '').replace('　', '')
            
            logger.info(f"📝 セグメント{seg_idx + 1}: {segment_text[:50]}... ({len(segment_chars)}文字)")
            
            # セグメントの開始時刻を取得
            if word_index < len(words):
                # start_timeまたはstartキーを取得
                start_time = words[word_index].get('start_time', 
                             words[word_index].get('start', 
                             words[word_index].get('timestamp', 0)))
            else:
                start_time = subtitles[-1]['end'] if subtitles else 0
            
            # セグメントに対応する単語を集める
            char_count = 0
            end_time = start_time
            
            while word_index < len(words) and char_count < len(segment_chars):
                word_data = words[word_index]
                word_text = word_data.get('text', word_data.get('word', ''))
                word_chars = word_text.replace(' ', '').replace('　', '')
                
                char_count += len(word_chars)
                
                # 終了時刻を更新
                end_time = word_data.get('end_time',
                           word_data.get('end',
                           word_data.get('start_time', 
                           word_data.get('start', end_time)) + 0.2))
                
                word_index += 1
                
                # セグメントの文字数に達したら終了
                if char_count >= len(segment_chars):
                    break
            
            # 終了時刻が開始時刻より小さい場合は調整
            if end_time <= start_time:
                end_time = start_time + 3.0
            
            subtitles.append({
                "start": start_time,
                "end": end_time,
                "text": segment_text,
                "speaker": segment['speaker']
            })
            
            logger.info(f"   ⏱️ {start_time:.2f}s - {end_time:.2f}s ({end_time - start_time:.2f}秒)")
        
        logger.info(f"✅ {len(subtitles)}個の字幕を生成しました")
        return subtitles
    
    def _create_subtitles_from_alignment(
        self,
        alignment: Dict[str, Any],
        script_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        アライメント情報から字幕を生成
        
        Args:
            alignment: アライメント情報
            script_segments: 台本のセグメント
            
        Returns:
            字幕データのリスト
        """
        # アライメント情報の構造に応じて処理
        # （実際のレスポンス構造に合わせて実装）
        logger.warning("⚠️ アライメント処理は未実装です。簡易生成にフォールバックします")
        return self._create_simple_subtitles_from_segments(script_segments)
    
    def _parse_script_segments(self, script: str) -> List[Dict[str, Any]]:
        """
        台本から話者ごとのセグメントを抽出
        
        Args:
            script: 台本テキスト
            
        Returns:
            セグメントのリスト
        """
        segments = []
        
        # [Aさん] または [Bさん] で分割
        import re
        pattern = r'\[(Aさん|Bさん)\]\s*'
        parts = re.split(pattern, script)
        
        current_speaker = None
        for i, part in enumerate(parts):
            if part in ['Aさん', 'Bさん']:
                current_speaker = 'A' if part == 'Aさん' else 'B'
            elif current_speaker and part.strip():
                segments.append({
                    "speaker": current_speaker,
                    "text": part.strip()
                })
        
        return segments
    
    def _create_simple_subtitles_from_segments(
        self,
        segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        セグメントから簡易的な字幕を生成
        
        Args:
            segments: セグメントのリスト
            
        Returns:
            字幕データのリスト
        """
        subtitles = []
        duration_per_segment = 3.5
        
        for i, segment in enumerate(segments):
            start_time = i * duration_per_segment
            end_time = start_time + duration_per_segment
            
            subtitles.append({
                "start": start_time,
                "end": end_time,
                "text": segment["text"],
                "speaker": segment["speaker"]
            })
        
        return subtitles
    
    def _create_simple_subtitles(self, script: str) -> List[Dict[str, Any]]:
        """
        台本から簡易的な字幕を生成（タイムスタンプは均等配分）
        
        Args:
            script: 台本テキスト
            
        Returns:
            字幕データのリスト
        """
        segments = self._parse_script_segments(script)
        subtitles = []
        
        # 1セグメントあたり平均3秒と仮定
        duration_per_segment = 3.5
        
        for i, segment in enumerate(segments):
            start_time = i * duration_per_segment
            end_time = start_time + duration_per_segment
            
            subtitles.append({
                "start": start_time,
                "end": end_time,
                "text": segment["text"],
                "speaker": segment["speaker"]
            })
        
        return subtitles
    
    def _generate_simple_subtitles_from_script(
        self,
        script_content: Dict[str, Any],
        audio_path: str
    ) -> Dict[str, Any]:
        """
        台本から簡易的に字幕を生成（フォールバック用）
        
        Args:
            script_content: 台本データ
            audio_path: 音声ファイルのパス
            
        Returns:
            字幕データ
        """
        try:
            # 音声の長さを取得
            if os.path.exists(audio_path):
                from pydub import AudioSegment
                audio = AudioSegment.from_file(audio_path)
                total_duration = len(audio) / 1000.0  # ミリ秒→秒
            else:
                total_duration = 600  # デフォルト10分
            
            # 台本テキストを取得
            full_script = script_content.get("full_script", "")
            if not full_script:
                full_script = self._extract_text_from_dialogue(
                    script_content.get("dialogue", [])
                )
            
            # セグメントに分割
            segments = self._parse_script_segments(full_script)
            
            # タイムスタンプを均等配分
            duration_per_segment = total_duration / len(segments) if segments else 3.0
            
            subtitles = []
            for i, segment in enumerate(segments):
                start_time = i * duration_per_segment
                end_time = min(start_time + duration_per_segment, total_duration)
                
                subtitles.append({
                    "start": start_time,
                    "end": end_time,
                    "text": segment["text"],
                    "speaker": segment["speaker"]
                })
            
            return {
                "subtitles": subtitles,
                "total_count": len(subtitles),
                "total_duration": total_duration
            }
            
        except Exception as e:
            logger.error(f"❌ 簡易字幕生成エラー: {e}")
            return {
                "subtitles": [],
                "total_count": 0,
                "total_duration": 0
            }
    
    def _extract_text_from_dialogue(self, dialogue: List[Dict[str, Any]]) -> str:
        """
        dialogueリストから台本テキストを抽出
        
        Args:
            dialogue: 対話のリスト
            
        Returns:
            台本テキスト
        """
        script_lines = []
        for item in dialogue:
            speaker = item.get("speaker", "A")
            text = item.get("text", "")
            speaker_name = "Aさん" if speaker == "A" else "Bさん"
            script_lines.append(f"[{speaker_name}] {text}")
        
        return "\n".join(script_lines)

