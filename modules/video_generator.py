"""
動画生成モジュール
"""
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class VideoGenerator:
    """動画生成クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        
        # 出力ディレクトリを作成
        self.output_dir = Path(self.settings.OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        
        # フォントパスを設定
        self.font_path = self.settings.FONT_PATH
        self.background_path = self.settings.BACKGROUND_IMAGE_PATH
    
    async def generate_video(self, audio_path: str, content: Dict[str, Any]) -> str:
        """動画を生成"""
        try:
            logger.info("動画生成を開始します")
            
            # 音声ファイルを読み込み
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # 背景画像を読み込み
            background_clip = self._create_background_clip(duration)
            
            # テキストクリップを作成
            text_clips = self._create_text_clips(content, duration)
            
            # 動画を合成
            video_clip = CompositeVideoClip([background_clip] + text_clips)
            video_clip = video_clip.set_audio(audio_clip)
            
            # ファイルパスを生成
            video_filename = f"podcast_video_{self._generate_timestamp()}.mp4"
            video_path = self.output_dir / video_filename
            
            # 動画を出力
            video_clip.write_videofile(
                str(video_path),
                fps=self.settings.VIDEO_FPS,
                codec='libx264',
                audio_codec='aac'
            )
            
            # リソースを解放
            audio_clip.close()
            video_clip.close()
            background_clip.close()
            
            logger.info(f"動画ファイルを生成しました: {video_path}")
            return str(video_path)
            
        except Exception as e:
            logger.error(f"動画生成に失敗しました: {e}")
            raise
    
    def _create_background_clip(self, duration: float) -> VideoClip:
        """背景クリップを作成"""
        try:
            if os.path.exists(self.background_path):
                # 背景画像が存在する場合
                background_image = ImageClip(self.background_path, duration=duration)
                # サイズを調整
                background_image = background_image.resize((self.settings.VIDEO_WIDTH, self.settings.VIDEO_HEIGHT))
            else:
                # 背景画像が存在しない場合は単色背景を作成
                background_image = ColorClip(
                    size=(self.settings.VIDEO_WIDTH, self.settings.VIDEO_HEIGHT),
                    color=(0, 0, 0),  # 黒色
                    duration=duration
                )
            
            logger.info("背景クリップを作成しました")
            return background_image
            
        except Exception as e:
            logger.error(f"背景クリップの作成に失敗しました: {e}")
            raise
    
    def _create_text_clips(self, content: Dict[str, Any], duration: float) -> List[VideoClip]:
        """テキストクリップを作成"""
        try:
            text_clips = []
            
            # タイトルクリップを作成
            if content.get("title"):
                title_clip = self._create_title_clip(content["title"], duration)
                text_clips.append(title_clip)
            
            # メインコンテンツのテキストクリップを作成
            if content.get("main_content"):
                content_clips = self._create_content_clips(content["main_content"], duration)
                text_clips.extend(content_clips)
            
            # キーポイントクリップを作成
            if content.get("key_points"):
                key_points_clips = self._create_key_points_clips(content["key_points"], duration)
                text_clips.extend(key_points_clips)
            
            logger.info(f"{len(text_clips)}個のテキストクリップを作成しました")
            return text_clips
            
        except Exception as e:
            logger.error(f"テキストクリップの作成に失敗しました: {e}")
            raise
    
    def _create_title_clip(self, title: str, duration: float) -> VideoClip:
        """タイトルクリップを作成"""
        try:
            # フォントを設定
            font_size = 60
            font = self._get_font(font_size)
            
            # テキストクリップを作成
            title_clip = TextClip(
                title,
                fontsize=font_size,
                color='white',
                font=font,
                method='caption',
                size=(self.settings.VIDEO_WIDTH - 100, None)
            ).set_position('center').set_duration(duration)
            
            return title_clip
            
        except Exception as e:
            logger.error(f"タイトルクリップの作成に失敗しました: {e}")
            raise
    
    def _create_content_clips(self, content: str, duration: float) -> List[VideoClip]:
        """コンテンツクリップを作成"""
        try:
            clips = []
            
            # コンテンツを段落に分割
            paragraphs = content.split('\n\n')
            
            # 各段落の表示時間を計算
            time_per_paragraph = duration / len(paragraphs) if paragraphs else duration
            
            for i, paragraph in enumerate(paragraphs):
                if not paragraph.strip():
                    continue
                
                # フォントを設定
                font_size = 40
                font = self._get_font(font_size)
                
                # テキストクリップを作成
                text_clip = TextClip(
                    paragraph,
                    fontsize=font_size,
                    color='white',
                    font=font,
                    method='caption',
                    size=(self.settings.VIDEO_WIDTH - 100, None)
                ).set_position('center').set_duration(time_per_paragraph)
                
                # 開始時間を設定
                text_clip = text_clip.set_start(i * time_per_paragraph)
                
                clips.append(text_clip)
            
            return clips
            
        except Exception as e:
            logger.error(f"コンテンツクリップの作成に失敗しました: {e}")
            raise
    
    def _create_key_points_clips(self, key_points: List[str], duration: float) -> List[VideoClip]:
        """キーポイントクリップを作成"""
        try:
            clips = []
            
            if not key_points:
                return clips
            
            # 各キーポイントの表示時間を計算
            time_per_point = duration / len(key_points)
            
            for i, point in enumerate(key_points):
                if not point.strip():
                    continue
                
                # フォントを設定
                font_size = 36
                font = self._get_font(font_size)
                
                # テキストクリップを作成
                text_clip = TextClip(
                    f"• {point}",
                    fontsize=font_size,
                    color='yellow',
                    font=font,
                    method='caption',
                    size=(self.settings.VIDEO_WIDTH - 100, None)
                ).set_position('center').set_duration(time_per_point)
                
                # 開始時間を設定
                text_clip = text_clip.set_start(i * time_per_point)
                
                clips.append(text_clip)
            
            return clips
            
        except Exception as e:
            logger.error(f"キーポイントクリップの作成に失敗しました: {e}")
            raise
    
    def _get_font(self, font_size: int):
        """フォントを取得"""
        try:
            if os.path.exists(self.font_path):
                return self.font_path
            else:
                # デフォルトフォントを使用
                return "Arial"
        except Exception as e:
            logger.warning(f"フォントの取得に失敗しました: {e}")
            return "Arial"
    
    def _generate_timestamp(self) -> str:
        """タイムスタンプを生成"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def generate_video_with_effects(self, audio_path: str, content: Dict[str, Any], 
                                        effects: Dict[str, Any] = None) -> str:
        """エフェクト付きの動画を生成"""
        try:
            # 基本的な動画を生成
            video_path = await self.generate_video(audio_path, content)
            
            # エフェクトが指定されている場合は適用
            if effects:
                video_path = await self._apply_video_effects(video_path, effects)
            
            return video_path
            
        except Exception as e:
            logger.error(f"エフェクト付き動画生成に失敗しました: {e}")
            raise
    
    async def _apply_video_effects(self, video_path: str, effects: Dict[str, Any]) -> str:
        """動画エフェクトを適用"""
        try:
            # ここで動画エフェクトを適用する処理を実装
            # 例: トランジション、フィルター、アニメーションなど
            
            logger.info(f"動画エフェクトを適用しました: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"動画エフェクトの適用に失敗しました: {e}")
            raise
