"""
音声生成モジュール
"""
import openai
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AudioGenerator:
    """音声生成クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = openai.OpenAI(
            api_key=self.settings.OPENAI_API_KEY
        )
        
        # 出力ディレクトリを作成
        self.output_dir = Path(self.settings.OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_audio(self, content: Dict[str, Any]) -> str:
        """音声を生成"""
        try:
            # メインコンテンツを取得
            main_content = content.get("main_content", "")
            if not main_content:
                raise ValueError("メインコンテンツが空です")
            
            # 音声生成用のテキストを準備
            audio_text = self._prepare_audio_text(content)
            
            # OpenAI TTS APIを使用して音声を生成
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=audio_text,
                response_format="mp3"
            )
            
            # ファイルパスを生成
            audio_filename = f"podcast_audio_{self._generate_timestamp()}.mp3"
            audio_path = self.output_dir / audio_filename
            
            # 音声ファイルを保存
            with open(audio_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"音声ファイルを生成しました: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"音声生成に失敗しました: {e}")
            raise
    
    def _prepare_audio_text(self, content: Dict[str, Any]) -> str:
        """音声生成用のテキストを準備"""
        try:
            # タイトルと概要を追加
            audio_text = ""
            
            if content.get("title"):
                audio_text += f"タイトル: {content['title']}\n\n"
            
            if content.get("summary"):
                audio_text += f"概要: {content['summary']}\n\n"
            
            # メインコンテンツを追加
            if content.get("main_content"):
                audio_text += content["main_content"]
            
            # キーポイントを追加
            if content.get("key_points"):
                audio_text += "\n\nキーポイント:\n"
                for point in content["key_points"]:
                    audio_text += f"• {point}\n"
            
            # 結論を追加
            if content.get("conclusion"):
                audio_text += f"\n\n結論: {content['conclusion']}"
            
            # テキストをクリーンアップ
            audio_text = self._clean_audio_text(audio_text)
            
            logger.info(f"音声生成用テキストを準備しました: {len(audio_text)}文字")
            return audio_text
            
        except Exception as e:
            logger.error(f"音声テキストの準備に失敗しました: {e}")
            raise
    
    def _clean_audio_text(self, text: str) -> str:
        """音声テキストをクリーンアップ"""
        # 不要な文字を削除
        text = text.replace("**", "")
        text = text.replace("*", "")
        text = text.replace("#", "")
        text = text.replace("##", "")
        text = text.replace("###", "")
        
        # 複数の改行を単一の改行に
        import re
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 先頭と末尾の空白を削除
        text = text.strip()
        
        return text
    
    def _generate_timestamp(self) -> str:
        """タイムスタンプを生成"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def generate_audio_with_effects(self, content: Dict[str, Any], 
                                        effects: Dict[str, Any] = None) -> str:
        """エフェクト付きの音声を生成"""
        try:
            # 基本的な音声を生成
            audio_path = await self.generate_audio(content)
            
            # エフェクトが指定されている場合は適用
            if effects:
                audio_path = await self._apply_audio_effects(audio_path, effects)
            
            return audio_path
            
        except Exception as e:
            logger.error(f"エフェクト付き音声生成に失敗しました: {e}")
            raise
    
    async def _apply_audio_effects(self, audio_path: str, effects: Dict[str, Any]) -> str:
        """音声エフェクトを適用"""
        try:
            # ここで音声エフェクトを適用する処理を実装
            # 例: ノイズ除去、音量調整、エコー追加など
            
            logger.info(f"音声エフェクトを適用しました: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"音声エフェクトの適用に失敗しました: {e}")
            raise
    
    def get_audio_duration(self, audio_path: str) -> float:
        """音声ファイルの長さを取得"""
        try:
            import librosa
            duration = librosa.get_duration(filename=audio_path)
            logger.info(f"音声ファイルの長さ: {duration:.2f}秒")
            return duration
            
        except Exception as e:
            logger.error(f"音声ファイルの長さ取得に失敗しました: {e}")
            return 0.0
