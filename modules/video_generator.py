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
    
    def _create_subtitle_frame(self, text: str, width: int = 1920, height: int = 1080) -> Image.Image:
        """
        字幕フレームを生成（PIL Image）
        
        Args:
            text: 字幕テキスト
            width: 画像の幅
            height: 画像の高さ
            
        Returns:
            PIL Image: 字幕付きの透明画像
        """
        try:
            # 透明な画像を作成
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # フォント設定 - Noto Sans JP Mediumを使用
            font_size = 60  # 40px → 60pxに拡大
            font_path = "assets/fonts/Noto_Sans_JP/static/NotoSansJP-Medium.ttf"
            
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    logger.info(f"✅ フォント読み込み成功: {font_path}")
                elif os.path.exists(self.font_path):
                    font = ImageFont.truetype(self.font_path, font_size)
                    logger.info(f"✅ フォント読み込み成功: {self.font_path}")
                else:
                    # デフォルトフォント
                    font = ImageFont.load_default()
                    logger.warning(f"⚠️ フォントファイルが見つかりません、デフォルトフォントを使用")
            except Exception as e:
                logger.warning(f"⚠️ フォント読み込みエラー: {e}、デフォルトフォントを使用")
                font = ImageFont.load_default()
            
            # テキストのサイズを計算（日本語対応の複数行処理）
            lines = []
            max_width = width - 300  # 左右の余白を十分に確保（150pxずつ）
            
            # 日本語対応の自動改行処理
            current_line = ""
            for i, char in enumerate(text):
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = bbox[2] - bbox[0]
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    # 現在の行を保存
                    if current_line:
                        lines.append(current_line)
                    current_line = char
                
                # 句読点の後で改行を推奨（ただし行が長くなりすぎない場合）
                if char in ['、', '。', '！', '？'] and i < len(text) - 1:
                    # 次の文字を含めても幅が収まるかチェック
                    if i + 1 < len(text):
                        next_test = current_line + text[i + 1]
                        bbox = draw.textbbox((0, 0), next_test, font=font)
                        next_width = bbox[2] - bbox[0]
                        
                        # 次の文字を含めると幅が80%以上になる場合は改行
                        if next_width > max_width * 0.75:
                            lines.append(current_line)
                            current_line = ""
            
            # 最後の行を追加
            if current_line:
                lines.append(current_line)
            
            # 3行を超える場合は警告
            if len(lines) > 3:
                logger.warning(f"⚠️ 字幕が3行を超えています（{len(lines)}行）。最初の3行のみ表示します。")
                lines = lines[:3]
            
            # 字幕背景の黒帯を描画（画面下部いっぱいに）
            # 3行分のスペースを常に確保
            padding_x = 80  # 左右のパディング
            padding_y = 45  # 上下のパディング（少し広めに）
            line_height = 75  # 行間（3行が綺麗に表示できるように）
            max_lines = 3  # 最大3行
            
            # 3行分の固定高さを計算
            bg_height = (line_height * max_lines) + (padding_y * 2)
            bg_y = height - bg_height  # 画面下部に固定
            
            # 黒背景（半透明）- 画面の底まで
            draw.rectangle(
                [(0, bg_y), (width, height)],  # 下部いっぱいまで
                fill=(0, 0, 0, 200)  # 透過度を少し上げて読みやすく
            )
            
            # テキストを中央に描画（縦方向も中央揃え）
            total_text_height = len(lines) * line_height
            # 3行分のスペースの中でテキストを中央配置
            available_height = bg_height - (padding_y * 2)
            start_y = bg_y + padding_y + ((available_height - total_text_height) // 2)
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = (width - text_width) // 2
                text_y = start_y + (i * line_height)
                
                # 白文字で描画（より明るく）
                draw.text((text_x, text_y), line, font=font, fill=(255, 255, 255, 255))
            
            return img
            
        except Exception as e:
            logger.error(f"字幕フレーム生成に失敗: {e}")
            raise
    
    async def generate_video_with_subtitles(
        self,
        audio_path: str,
        subtitle_data: List[Dict[str, Any]],
        background_image_path: str = None
    ) -> str:
        """
        字幕付き動画を生成
        
        Args:
            audio_path: 音声ファイルのパス
            subtitle_data: 字幕データのリスト
                [
                    {
                        "start": float,  # 開始時間（秒）
                        "end": float,    # 終了時間（秒）
                        "text": str,     # 字幕テキスト
                        "speaker": str   # 話者（オプション）
                    }
                ]
            background_image_path: 背景画像のパス（Noneの場合は設定値を使用）
            
        Returns:
            str: 生成された動画ファイルのパス
        """
        try:
            logger.info("字幕付き動画生成を開始します")
            
            # 音声ファイルを読み込み
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            logger.info(f"音声の長さ: {duration:.2f}秒")
            
            # 背景画像を読み込み
            bg_path = background_image_path if background_image_path else self.background_path
            
            if not os.path.exists(bg_path):
                logger.warning(f"背景画像が見つかりません: {bg_path}、黒背景を使用")
                background_clip = ColorClip(
                    size=(self.settings.VIDEO_WIDTH, self.settings.VIDEO_HEIGHT),
                    color=(0, 0, 0),
                    duration=duration
                )
            else:
                # Pillowで画像を読み込んでリサイズ（MoviePyのバグ回避）
                from PIL import Image as PILImage
                pil_img = PILImage.open(bg_path)
                
                # 目標サイズにリサイズ
                target_size = (self.settings.VIDEO_WIDTH, self.settings.VIDEO_HEIGHT)
                if pil_img.size != target_size:
                    # Pillow 10.0.0以降では LANCZOS を使用
                    pil_img = pil_img.resize(target_size, PILImage.LANCZOS)
                    logger.info(f"背景画像をリサイズしました: {pil_img.size}")
                
                # 一時ファイルに保存
                temp_dir = Path(self.settings.TEMP_DIR)
                temp_dir.mkdir(exist_ok=True)
                temp_bg_path = temp_dir / "resized_background.png"
                pil_img.save(temp_bg_path)
                
                # リサイズ済み画像を読み込み
                background_clip = ImageClip(str(temp_bg_path), duration=duration)
                logger.info(f"背景画像を読み込みました: {bg_path}")
            
            # 字幕クリップを作成
            subtitle_clips = []
            for i, subtitle in enumerate(subtitle_data):
                start_time = subtitle.get("start", 0)
                end_time = subtitle.get("end", start_time + 3)
                text = subtitle.get("text", "")
                
                if not text:
                    continue
                
                # 字幕フレームを生成
                subtitle_img = self._create_subtitle_frame(
                    text,
                    self.settings.VIDEO_WIDTH,
                    self.settings.VIDEO_HEIGHT
                )
                
                # 一時ファイルに保存
                temp_dir = Path(self.settings.TEMP_DIR)
                temp_dir.mkdir(exist_ok=True)
                temp_subtitle_path = temp_dir / f"subtitle_{i}.png"
                subtitle_img.save(temp_subtitle_path)
                
                # 字幕クリップを作成
                subtitle_clip = (ImageClip(str(temp_subtitle_path))
                               .set_start(start_time)
                               .set_duration(end_time - start_time)
                               .set_position(("center", "center")))
                
                subtitle_clips.append(subtitle_clip)
                logger.info(f"字幕 {i+1}/{len(subtitle_data)}: {start_time:.2f}s - {end_time:.2f}s")
            
            # 動画を合成
            logger.info("動画を合成中...")
            video_clip = CompositeVideoClip([background_clip] + subtitle_clips)
            video_clip = video_clip.set_audio(audio_clip)
            
            # ファイルパスを生成
            video_filename = f"video_with_subtitles_{self._generate_timestamp()}.mp4"
            video_path = self.output_dir / video_filename
            
            # 動画を出力
            logger.info("動画をエンコード中...")
            video_clip.write_videofile(
                str(video_path),
                fps=self.settings.VIDEO_FPS,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4
            )
            
            # 一時ファイルを削除
            for i in range(len(subtitle_data)):
                temp_subtitle_path = temp_dir / f"subtitle_{i}.png"
                if temp_subtitle_path.exists():
                    temp_subtitle_path.unlink()
            
            # リソースを解放
            audio_clip.close()
            video_clip.close()
            background_clip.close()
            for clip in subtitle_clips:
                clip.close()
            
            logger.info(f"✅ 字幕付き動画を生成しました: {video_path}")
            return str(video_path)
            
        except Exception as e:
            logger.error(f"字幕付き動画生成に失敗しました: {e}")
            raise