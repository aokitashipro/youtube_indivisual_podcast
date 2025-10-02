"""
音声生成テスト
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

from modules.audio_generator import AudioGenerator
from config.settings import Settings


class TestAudioGenerator:
    """音声生成テストクラス"""
    
    @pytest.fixture
    def mock_settings(self):
        """モック設定を作成"""
        settings = Mock(spec=Settings)
        settings.OPENAI_API_KEY = "test_api_key"
        settings.OUTPUT_DIR = "temp/"
        settings.AUDIO_SAMPLE_RATE = 44100
        settings.AUDIO_BITRATE = "192k"
        return settings
    
    @pytest.fixture
    def audio_generator(self, mock_settings):
        """音声生成器を作成"""
        return AudioGenerator(mock_settings)
    
    @pytest.fixture
    def sample_content(self):
        """サンプルコンテンツを作成"""
        return {
            "title": "テストタイトル",
            "summary": "これはテスト用の概要です。",
            "main_content": "これはテスト用のメインコンテンツです。",
            "key_points": ["ポイント1", "ポイント2", "ポイント3"],
            "conclusion": "これはテスト用の結論です。"
        }
    
    @pytest.mark.asyncio
    async def test_generate_audio_success(self, audio_generator, sample_content):
        """音声生成の成功テスト"""
        with patch('modules.audio_generator.openai.OpenAI') as mock_openai:
            # モックの設定
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = b"fake_audio_data"
            mock_client.audio.speech.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # テスト実行
            result = await audio_generator.generate_audio(sample_content)
            
            # 結果の検証
            assert result is not None
            assert isinstance(result, str)
            assert result.endswith('.mp3')
            assert os.path.exists(result)
            
            # ファイルのクリーンアップ
            if os.path.exists(result):
                os.remove(result)
    
    @pytest.mark.asyncio
    async def test_generate_audio_empty_content(self, audio_generator):
        """空のコンテンツでの音声生成テスト"""
        empty_content = {}
        
        with pytest.raises(ValueError, match="メインコンテンツが空です"):
            await audio_generator.generate_audio(empty_content)
    
    @pytest.mark.asyncio
    async def test_generate_audio_with_effects(self, audio_generator, sample_content):
        """エフェクト付き音声生成テスト"""
        with patch('modules.audio_generator.openai.OpenAI') as mock_openai:
            # モックの設定
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = b"fake_audio_data"
            mock_client.audio.speech.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # エフェクト設定
            effects = {
                "noise_reduction": True,
                "volume_boost": 1.2
            }
            
            # テスト実行
            result = await audio_generator.generate_audio_with_effects(sample_content, effects)
            
            # 結果の検証
            assert result is not None
            assert isinstance(result, str)
            assert result.endswith('.mp3')
            
            # ファイルのクリーンアップ
            if os.path.exists(result):
                os.remove(result)
    
    def test_prepare_audio_text(self, audio_generator, sample_content):
        """音声テキスト準備テスト"""
        result = audio_generator._prepare_audio_text(sample_content)
        
        # 結果の検証
        assert isinstance(result, str)
        assert "テストタイトル" in result
        assert "これはテスト用の概要です" in result
        assert "これはテスト用のメインコンテンツです" in result
        assert "ポイント1" in result
        assert "これはテスト用の結論です" in result
    
    def test_clean_audio_text(self, audio_generator):
        """音声テキストクリーンアップテスト"""
        dirty_text = "**太字** #見出し## 複数\n\n\n改行"
        clean_text = audio_generator._clean_audio_text(dirty_text)
        
        # 結果の検証
        assert "**" not in clean_text
        assert "#" not in clean_text
        assert clean_text.count('\n\n') <= 1
    
    def test_generate_timestamp(self, audio_generator):
        """タイムスタンプ生成テスト"""
        timestamp = audio_generator._generate_timestamp()
        
        # 結果の検証
        assert isinstance(timestamp, str)
        assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
        assert timestamp.count('_') == 1
    
    @pytest.mark.asyncio
    async def test_get_audio_duration(self, audio_generator):
        """音声ファイルの長さ取得テスト"""
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(b"fake_audio_data")
            temp_file_path = temp_file.name
        
        try:
            # モックを使用してテスト
            with patch('modules.audio_generator.librosa.get_duration') as mock_duration:
                mock_duration.return_value = 120.5
                
                duration = audio_generator.get_audio_duration(temp_file_path)
                
                # 結果の検証
                assert duration == 120.5
                mock_duration.assert_called_once_with(filename=temp_file_path)
        
        finally:
            # ファイルのクリーンアップ
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_get_audio_duration_error(self, audio_generator):
        """音声ファイルの長さ取得エラーテスト"""
        with patch('modules.audio_generator.librosa.get_duration') as mock_duration:
            mock_duration.side_effect = Exception("Test error")
            
            duration = audio_generator.get_audio_duration("nonexistent.mp3")
            
            # 結果の検証
            assert duration == 0.0


if __name__ == "__main__":
    pytest.main([__file__])
