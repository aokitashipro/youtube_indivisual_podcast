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
            
            # 🔧 デバッグ: 分割前の字幕情報をログ出力
            logger.info(f"📊 分割前の字幕: {len(subtitles)}個")
            if subtitles:
                logger.info(f"   最初: {subtitles[0]['start']:.2f}s - {subtitles[0]['end']:.2f}s")
                logger.info(f"   最後: {subtitles[-1]['start']:.2f}s - {subtitles[-1]['end']:.2f}s")
            
            # 3行を超える字幕を分割
            subtitles = self._split_long_subtitles(subtitles)
            
            # 🔧 デバッグ: 分割後の字幕情報をログ出力
            logger.info(f"📊 分割後の字幕: {len(subtitles)}個")
            if subtitles:
                logger.info(f"   最初: {subtitles[0]['start']:.2f}s - {subtitles[0]['end']:.2f}s")
                logger.info(f"   最後: {subtitles[-1]['start']:.2f}s - {subtitles[-1]['end']:.2f}s")
                
                # タイムスタンプの連続性をチェック
                for i in range(1, len(subtitles)):
                    if subtitles[i]['start'] < subtitles[i-1]['end']:
                        logger.warning(f"   ⚠️ 字幕{i}が重複: 前={subtitles[i-1]['end']:.2f}s, 現={subtitles[i]['start']:.2f}s")
                    elif subtitles[i]['start'] > subtitles[i-1]['end'] + 0.5:
                        gap = subtitles[i]['start'] - subtitles[i-1]['end']
                        logger.warning(f"   ⚠️ 字幕{i}に大きな間隔: {gap:.2f}秒")
            
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
            
            logger.info(f"✅ 字幕生成完了: {len(subtitles)}個のセグメント、総時間: {result['total_duration']:.2f}秒")
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
        
        # 🔧 修正: difflibを使ったより正確なマッチング
        # STT結果の全テキストを結合
        stt_full_text = ''.join([w.get('text', w.get('word', '')) for w in words]).replace(' ', '').replace('　', '')
        
        # 台本の全テキストを結合
        script_full_text = ''.join([seg['text'] for seg in script_segments]).replace(' ', '').replace('　', '')
        
        logger.info(f"📊 マッチング準備:")
        logger.info(f"   STT文字数: {len(stt_full_text)}")
        logger.info(f"   台本文字数: {len(script_full_text)}")
        
        # 単語を台本のセグメントにグループ化
        word_index = 0
        accumulated_chars = 0  # STT側の累積文字数
        
        for seg_idx, segment in enumerate(script_segments):
            segment_text = segment['text']
            segment_chars = segment_text.replace(' ', '').replace('　', '')
            
            logger.info(f"📝 セグメント{seg_idx + 1}/{len(script_segments)}: {segment_text[:50]}... ({len(segment_chars)}文字)")
            
            # セグメントの開始時刻を取得
            if word_index < len(words):
                start_time = words[word_index].get('start_time', 
                             words[word_index].get('start', 
                             words[word_index].get('timestamp', 0)))
            else:
                # 単語が足りない場合は前のセグメントから推定
                if subtitles:
                    start_time = subtitles[-1]['end']
                else:
                    start_time = 0
                logger.warning(f"   ⚠️ 単語インデックス超過: {word_index}/{len(words)}")
            
            # 🔧 改善: セグメントの文字数分の単語を取得（柔軟に）
            target_chars = accumulated_chars + len(segment_chars)
            char_count = accumulated_chars
            end_time = start_time
            words_used = 0
            
            while word_index < len(words):
                word_data = words[word_index]
                word_text = word_data.get('text', word_data.get('word', ''))
                word_chars = word_text.replace(' ', '').replace('　', '')
                
                # 終了時刻を更新
                end_time = word_data.get('end_time',
                           word_data.get('end',
                           word_data.get('start_time', 
                           word_data.get('start', end_time)) + 0.2))
                
                char_count += len(word_chars)
                word_index += 1
                words_used += 1
                
                # 目標文字数に達したら終了（多少のマージンを許容）
                if char_count >= target_chars:
                    accumulated_chars = char_count
                    break
                
                # 最後の単語に達した場合は終了
                if word_index >= len(words):
                    accumulated_chars = char_count
                    logger.warning(f"   ⚠️ 最後の単語に到達: {word_index}/{len(words)}")
                    break
            
            # 終了時刻が開始時刻より小さい場合は調整
            if end_time <= start_time:
                end_time = start_time + 3.0
                logger.warning(f"   ⚠️ 終了時刻を調整: {end_time:.2f}s")
            
            subtitles.append({
                "start": start_time,
                "end": end_time,
                "text": segment_text,  # 🔧 重要: STT結果ではなく台本のテキストを使用
                "speaker": segment['speaker']
            })
            
            logger.info(f"   ⏱️ {start_time:.2f}s - {end_time:.2f}s ({end_time - start_time:.2f}秒, {words_used}単語使用)")
        
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
        
        # 🔧 デバッグ: 元の台本の情報
        logger.info(f"📝 台本パース開始: {len(script)}文字")
        
        # メタ情報（タイトル、文字数など）を除去
        # 最初の[Aさん]または[Bさん]が出現するまでの部分をスキップ
        first_speaker_match = re.search(r'\[(Aさん|Bさん)\]', script)
        if first_speaker_match:
            removed_prefix = script[:first_speaker_match.start()]
            if removed_prefix.strip():
                logger.info(f"   メタ情報を除去: {len(removed_prefix)}文字")
                logger.debug(f"   除去内容: {removed_prefix[:100]}...")
            script = script[first_speaker_match.start():]
        
        pattern = r'\[(Aさん|Bさん)\]\s*'
        parts = re.split(pattern, script)
        
        current_speaker = None
        skipped_segments = 0
        
        for i, part in enumerate(parts):
            if part in ['Aさん', 'Bさん']:
                current_speaker = 'A' if part == 'Aさん' else 'B'
            elif current_speaker and part.strip():
                text = part.strip()
                
                # 🔧 改善: 最低文字数を3文字に緩和（短い相槌なども含める）
                if len(text) >= 3:
                    segments.append({
                        "speaker": current_speaker,
                        "text": text
                    })
                else:
                    skipped_segments += 1
                    logger.debug(f"   スキップ: {current_speaker}さん「{text}」({len(text)}文字)")
        
        logger.info(f"✅ 台本パース完了: {len(segments)}セグメント（スキップ: {skipped_segments}個）")
        if segments:
            logger.info(f"   最初: {segments[0]['speaker']}さん「{segments[0]['text'][:30]}...」")
            logger.info(f"   最後: {segments[-1]['speaker']}さん「{segments[-1]['text'][:30]}...」")
        
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
    
    def _split_long_subtitles(self, subtitles: List[Dict[str, Any]], max_lines: int = 3) -> List[Dict[str, Any]]:
        """
        3行を超える字幕を自動分割
        
        Args:
            subtitles: 字幕データのリスト
            max_lines: 1セグメントの最大行数（デフォルト: 3）
            
        Returns:
            分割後の字幕データのリスト
        """
        from PIL import Image, ImageDraw, ImageFont
        import os
        
        logger.info(f"✂️ 字幕分割処理開始: {len(subtitles)}セグメント（最大{max_lines}行）")
        
        # フォントを読み込み
        font_size = 60
        font_path = "assets/fonts/Noto_Sans_JP/static/NotoSansJP-Medium.ttf"
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                logger.debug(f"   フォント読み込み成功: {font_path}")
            else:
                font = ImageFont.load_default()
                logger.warning(f"   ⚠️ フォントが見つかりません: {font_path}、デフォルトフォント使用")
        except Exception as e:
            font = ImageFont.load_default()
            logger.warning(f"   ⚠️ フォント読み込みエラー: {e}、デフォルトフォント使用")
        
        new_subtitles = []
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        max_width = 1920 - 300  # 字幕の最大幅
        
        for subtitle in subtitles:
            text = subtitle['text']
            
            # 改行ロジックで実際の行数を計算
            lines = []
            current_line = ""
            
            for i, char in enumerate(text):
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = bbox[2] - bbox[0]
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
                
                # 句読点で改行を促進
                if char in ['、', '。', '！', '？'] and i < len(text) - 1:
                    if i + 1 < len(text):
                        next_test = current_line + text[i + 1]
                        bbox = draw.textbbox((0, 0), next_test, font=font)
                        next_width = bbox[2] - bbox[0]
                        
                        if next_width > max_width * 0.75:
                            lines.append(current_line)
                            current_line = ""
            
            if current_line:
                lines.append(current_line)
            
            # 3行以下ならそのまま追加
            if len(lines) <= max_lines:
                new_subtitles.append(subtitle)
            else:
                # 3行ごとに分割
                logger.info(f"📝 長い字幕を分割: {len(lines)}行 → {(len(lines) + max_lines - 1) // max_lines}セグメント")
                
                duration = subtitle['end'] - subtitle['start']
                chars_per_line = [len(line) for line in lines]
                total_chars = sum(chars_per_line)
                
                segments_count = (len(lines) + max_lines - 1) // max_lines
                
                for seg_idx in range(segments_count):
                    start_line_idx = seg_idx * max_lines
                    end_line_idx = min(start_line_idx + max_lines, len(lines))
                    
                    segment_lines = lines[start_line_idx:end_line_idx]
                    segment_text = ''.join(segment_lines)
                    
                    # タイムスタンプを文字数で比例配分
                    segment_chars = sum(chars_per_line[start_line_idx:end_line_idx])
                    char_ratio = segment_chars / total_chars
                    
                    segment_duration = duration * char_ratio
                    
                    # 前のセグメントの終了時刻から開始
                    if seg_idx == 0:
                        segment_start = subtitle['start']
                    else:
                        segment_start = new_subtitles[-1]['end']
                    
                    # 🔧 修正: 最後のセグメントは元の終了時刻に合わせる
                    if seg_idx == segments_count - 1:
                        segment_end = subtitle['end']
                        logger.info(f"   📌 最終セグメント: 元の終了時刻に調整 ({segment_end:.2f}s)")
                    else:
                        segment_end = segment_start + segment_duration
                    
                    new_subtitles.append({
                        "start": segment_start,
                        "end": segment_end,
                        "text": segment_text,
                        "speaker": subtitle.get('speaker', '')
                    })
                    
                    logger.info(f"   セグメント{seg_idx + 1}/{segments_count}: {segment_text[:30]}... ({len(segment_lines)}行, {segment_end - segment_start:.2f}秒, {segment_start:.2f}-{segment_end:.2f}s)")
        
        logger.info(f"🔄 字幕分割完了: {len(subtitles)}セグメント → {len(new_subtitles)}セグメント")
        return new_subtitles
    
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

