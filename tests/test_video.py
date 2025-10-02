"""
動画生成テスト
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path

# テスト対象のモジュールをインポート
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.video_generator import VideoGenerator
from config.settings import Settings


class TestVideoGenerator:
    """動画生成テストクラス"""
    
    @pytest.fixture
    def mock_settings(self):
        """モック設定を作成"""
        settings = Mock(spec=Settings)
        settings.VIDEO_WIDTH = 1920
        settings.VIDEO_HEIGHT = 1080
        settings.VIDEO_FPS = 30
        settings.OUTPUT_DIR = "temp/"
        settings.FONT_PATH = "assets/fonts/NotoSansJP-Regular.ttf"
        settings.BACKGROUND_IMAGE_PATH = "assets/background.png"
        return settings
    
    @pytest.fixture
    def video_generator(self, mock_settings):
        """動画生成器を作成"""
        return VideoGenerator(mock_settings)
    
    @pytest.fixture
    def sample_content(self):
        """サンプルコンテンツを作成"""
        return {
            "title": "テストタイトル",
            "summary": "これはテスト用の概要です。",
            "main_content": "これはテスト用のメインコンテンツです。\n\n複数の段落があります。",
            "key_points": ["ポイント1", "ポイント2", "ポイント3"],
            "conclusion": "これはテスト用の結論です。"
        }
    
    @pytest.fixture
    def sample_audio_path(self):
        """サンプル音声ファイルパスを作成"""
        return "temp/test_audio.mp3"
    
    @pytest.mark.asyncio
    async def test_generate_video_success(self, video_generator, sample_content, sample_audio_path):
        """動画生成の成功テスト"""
        with patch('modules.video_generator.AudioFileClip') as mock_audio, \
             patch('modules.video_generator.CompositeVideoClip') as mock_composite, \
             patch('modules.video_generator.ColorClip') as mock_color, \
             patch('modules.video_generator.TextClip') as mock_text:
            
            # モックの設定
            mock_audio_clip = Mock()
            mock_audio_clip.duration = 120.0
            mock_audio.return_value = mock_audio_clip
            
            mock_background_clip = Mock()
            mock_color.return_value = mock_background_clip
            
            mock_text_clip = Mock()
            mock_text.return_value = mock_text_clip
            
            mock_composite_clip = Mock()
            mock_composite.return_value = mock_composite_clip
            
            # テスト実行
            result = await video_generator.generate_video(sample_audio_path, sample_content)
            
            # 結果の検証
            assert result is not None
            assert isinstance(result, str)
            assert result.endswith('.mp4')
            
            # モックの呼び出しを検証
            mock_audio.assert_called_once_with(sample_audio_path)
            mock_composite.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_video_with_effects(self, video_generator, sample_content, sample_audio_path):
        """エフェクト付き動画生成テスト"""
        with patch('modules.video_generator.AudioFileClip') as mock_audio, \
             patch('modules.video_generator.CompositeVideoClip') as mock_composite, \
             patch('modules.video_generator.ColorClip') as mock_color, \
             patch('modules.video_generator.TextClip') as mock_text:
            
            # モックの設定
            mock_audio_clip = Mock()
            mock_audio_clip.duration = 120.0
            mock_audio.return_value = mock_audio_clip
            
            mock_background_clip = Mock()
            mock_color.return_value = mock_background_clip
            
            mock_text_clip = Mock()
            mock_text.return_value = mock_text_clip
            
            mock_composite_clip = Mock()
            mock_composite.return_value = mock_composite_clip
            
            # エフェクト設定
            effects = {
                "transition": "fade",
                "filter": "vintage"
            }
            
            # テスト実行
            result = await video_generator.generate_video_with_effects(sample_audio_path, sample_content, effects)
            
            # 結果の検証
            assert result is not None
            assert isinstance(result, str)
            assert result.endswith('.mp4')
    
    def test_create_background_clip(self, video_generator):
        """背景クリップ作成テスト"""
        with patch('modules.video_generator.ImageClip') as mock_image_clip, \
             patch('modules.video_generator.ColorClip') as mock_color_clip:
            
            # 背景画像が存在する場合
            with patch('os.path.exists', return_value=True):
                mock_clip = Mock()
                mock_image_clip.return_value = mock_clip
                
                result = video_generator._create_background_clip(120.0)
                
                assert result == mock_clip
                mock_image_clip.assert_called_once()
            
            # 背景画像が存在しない場合
            with patch('os.path.exists', return_value=False):
                mock_clip = Mock()
                mock_color_clip.return_value = mock_clip
                
                result = video_generator._create_background_clip(120.0)
                
                assert result == mock_clip
                mock_color_clip.assert_called_once()
    
    def test_create_text_clips(self, video_generator, sample_content):
        """テキストクリップ作成テスト"""
        with patch('modules.video_generator.TextClip') as mock_text_clip:
            mock_clip = Mock()
            mock_text_clip.return_value = mock_clip
            
            result = video_generator._create_text_clips(sample_content, 120.0)
            
            # 結果の検証
            assert isinstance(result, list)
            assert len(result) > 0
            
            # テキストクリップが作成されたことを確認
            mock_text_clip.assert_called()
    
    def test_create_title_clip(self, video_generator):
        """タイトルクリップ作成テスト"""
        with patch('modules.video_generator.TextClip') as mock_text_clip:
            mock_clip = Mock()
            mock_text_clip.return_value = mock_clip
            
            result = video_generator._create_title_clip("テストタイトル", 120.0)
            
            # 結果の検証
            assert result == mock_clip
            mock_text_clip.assert_called_once()
    
    def test_create_content_clips(self, video_generator):
        """コンテンツクリップ作成テスト"""
        with patch('modules.video_generator.TextClip') as mock_text_clip:
            mock_clip = Mock()
            mock_text_clip.return_value = mock_clip
            
            content = "段落1\n\n段落2\n\n段落3"
            result = video_generator._create_content_clips(content, 120.0)
            
            # 結果の検証
            assert isinstance(result, list)
            assert len(result) > 0
            
            # テキストクリップが作成されたことを確認
            mock_text_clip.assert_called()
    
    def test_create_key_points_clips(self, video_generator):
        """キーポイントクリップ作成テスト"""
        with patch('modules.video_generator.TextClip') as mock_text_clip:
            mock_clip = Mock()
            mock_text_clip.return_value = mock_clip
            
            key_points = ["ポイント1", "ポイント2", "ポイント3"]
            result = video_generator._create_key_points_clips(key_points, 120.0)
            
            # 結果の検証
            assert isinstance(result, list)
            assert len(result) == len(key_points)
            
            # テキストクリップが作成されたことを確認
            mock_text_clip.assert_called()
    
    def test_get_font(self, video_generator):
        """フォント取得テスト"""
        with patch('os.path.exists') as mock_exists:
            # フォントファイルが存在する場合
            mock_exists.return_value = True
            result = video_generator._get_font(40)
            assert result == video_generator.settings.FONT_PATH
            
            # フォントファイルが存在しない場合
            mock_exists.return_value = False
            result = video_generator._get_font(40)
            assert result == "Arial"
    
    def test_generate_timestamp(self, video_generator):
        """タイムスタンプ生成テスト"""
        timestamp = video_generator._generate_timestamp()
        
        # 結果の検証
        assert isinstance(timestamp, str)
        assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
        assert timestamp.count('_') == 1
    
    @pytest.mark.asyncio
    async def test_apply_video_effects(self, video_generator):
        """動画エフェクト適用テスト"""
        effects = {
            "transition": "fade",
            "filter": "vintage"
        }
        
        result = await video_generator._apply_video_effects("test_video.mp4", effects)
        
        # 結果の検証
        assert result == "test_video.mp4"


if __name__ == "__main__":
    pytest.main([__file__])
