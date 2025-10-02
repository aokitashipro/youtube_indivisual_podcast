"""
統合テスト
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

from main import app
from config.settings import Settings
from modules.sheets_manager import SheetsManager
from modules.claude_client import ClaudeClient
from modules.audio_generator import AudioGenerator
from modules.video_generator import VideoGenerator
from modules.metadata_generator import MetadataGenerator
from modules.storage_manager import StorageManager
from modules.notifier import Notifier


class TestIntegration:
    """統合テストクラス"""
    
    @pytest.fixture
    def mock_settings(self):
        """モック設定を作成"""
        settings = Mock(spec=Settings)
        settings.ANTHROPIC_API_KEY = "test_anthropic_key"
        settings.OPENAI_API_KEY = "test_openai_key"
        settings.GOOGLE_SHEETS_ID = "test_sheets_id"
        settings.GOOGLE_CREDENTIALS_PATH = "test_credentials.json"
        settings.SLACK_BOT_TOKEN = "test_slack_token"
        settings.SLACK_CHANNEL = "test_channel"
        settings.GOOGLE_DRIVE_FOLDER_ID = "test_folder_id"
        settings.OUTPUT_DIR = "temp/"
        settings.TEMP_DIR = "temp/"
        settings.DEBUG = True
        settings.LOG_LEVEL = "INFO"
        return settings
    
    @pytest.fixture
    def sample_sheets_data(self):
        """サンプルSheetsデータを作成"""
        return {
            "raw_data": [
                {
                    "title": "AI技術の最新動向",
                    "content": "人工知能の最新技術について説明します。",
                    "category": "Technology",
                    "tags": "AI, 人工知能, 技術"
                }
            ],
            "latest_data": {
                "title": "AI技術の最新動向",
                "content": "人工知能の最新技術について説明します。",
                "category": "Technology",
                "tags": "AI, 人工知能, 技術"
            },
            "total_records": 1
        }
    
    @pytest.fixture
    def sample_claude_content(self):
        """サンプルClaude生成コンテンツを作成"""
        return {
            "title": "AI技術の最新動向",
            "summary": "人工知能の最新技術について詳しく解説します。",
            "main_content": "こんにちは、今日はAI技術の最新動向についてお話しします。\n\nまず、機械学習の分野では...",
            "key_points": [
                "機械学習の進歩",
                "深層学習の応用",
                "自然言語処理の革新"
            ],
            "conclusion": "AI技術は今後も急速に発展していくでしょう。"
        }
    
    @pytest.fixture
    def sample_metadata(self):
        """サンプルメタデータを作成"""
        return {
            "title": "AI技術の最新動向",
            "description": "人工知能の最新技術について詳しく解説します。",
            "tags": ["AI", "人工知能", "技術", "機械学習"],
            "category": "Science & Technology",
            "thumbnail_suggestion": "AI関連の画像を使用",
            "created_at": "2024-01-01T00:00:00",
            "duration": 300,
            "language": "ja",
            "privacy_status": "private"
        }
    
    @pytest.mark.asyncio
    async def test_full_pipeline_success(self, mock_settings, sample_sheets_data, 
                                       sample_claude_content, sample_metadata):
        """完全なパイプラインの成功テスト"""
        with patch('modules.sheets_manager.SheetsManager') as mock_sheets, \
             patch('modules.claude_client.ClaudeClient') as mock_claude, \
             patch('modules.audio_generator.AudioGenerator') as mock_audio, \
             patch('modules.video_generator.VideoGenerator') as mock_video, \
             patch('modules.metadata_generator.MetadataGenerator') as mock_metadata, \
             patch('modules.storage_manager.StorageManager') as mock_storage, \
             patch('modules.notifier.Notifier') as mock_notifier:
            
            # モックの設定
            mock_sheets_instance = Mock()
            mock_sheets_instance.get_podcast_data.return_value = sample_sheets_data
            mock_sheets.return_value = mock_sheets_instance
            
            mock_claude_instance = Mock()
            mock_claude_instance.generate_content.return_value = sample_claude_content
            mock_claude.return_value = mock_claude_instance
            
            mock_audio_instance = Mock()
            mock_audio_instance.generate_audio.return_value = "temp/audio.mp3"
            mock_audio.return_value = mock_audio_instance
            
            mock_video_instance = Mock()
            mock_video_instance.generate_video.return_value = "temp/video.mp4"
            mock_video.return_value = mock_video_instance
            
            mock_metadata_instance = Mock()
            mock_metadata_instance.generate_metadata.return_value = sample_metadata
            mock_metadata.return_value = mock_metadata_instance
            
            mock_storage_instance = Mock()
            mock_storage_instance.upload_video.return_value = "https://drive.google.com/test"
            mock_storage.return_value = mock_storage_instance
            
            mock_notifier_instance = Mock()
            mock_notifier_instance.send_completion_notification.return_value = None
            mock_notifier.return_value = mock_notifier_instance
            
            # テスト実行
            from main import generate_podcast
            result = await generate_podcast()
            
            # 結果の検証
            assert result["status"] == "success"
            assert "drive_url" in result
            assert "metadata" in result
            
            # 各モジュールが呼び出されたことを確認
            mock_sheets_instance.get_podcast_data.assert_called_once()
            mock_claude_instance.generate_content.assert_called_once()
            mock_audio_instance.generate_audio.assert_called_once()
            mock_video_instance.generate_video.assert_called_once()
            mock_metadata_instance.generate_metadata.assert_called_once()
            mock_storage_instance.upload_video.assert_called_once()
            mock_notifier_instance.send_completion_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pipeline_with_sheets_error(self, mock_settings):
        """Sheets取得エラー時のテスト"""
        with patch('modules.sheets_manager.SheetsManager') as mock_sheets:
            # エラーを発生させる
            mock_sheets_instance = Mock()
            mock_sheets_instance.get_podcast_data.side_effect = Exception("Sheets接続エラー")
            mock_sheets.return_value = mock_sheets_instance
            
            # テスト実行
            from main import generate_podcast
            
            with pytest.raises(Exception, match="Sheets接続エラー"):
                await generate_podcast()
    
    @pytest.mark.asyncio
    async def test_pipeline_with_claude_error(self, mock_settings, sample_sheets_data):
        """Claude APIエラー時のテスト"""
        with patch('modules.sheets_manager.SheetsManager') as mock_sheets, \
             patch('modules.claude_client.ClaudeClient') as mock_claude:
            
            # Sheetsは成功
            mock_sheets_instance = Mock()
            mock_sheets_instance.get_podcast_data.return_value = sample_sheets_data
            mock_sheets.return_value = mock_sheets_instance
            
            # Claudeでエラーを発生させる
            mock_claude_instance = Mock()
            mock_claude_instance.generate_content.side_effect = Exception("Claude APIエラー")
            mock_claude.return_value = mock_claude_instance
            
            # テスト実行
            from main import generate_podcast
            
            with pytest.raises(Exception, match="Claude APIエラー"):
                await generate_podcast()
    
    @pytest.mark.asyncio
    async def test_pipeline_with_audio_error(self, mock_settings, sample_sheets_data, 
                                           sample_claude_content):
        """音声生成エラー時のテスト"""
        with patch('modules.sheets_manager.SheetsManager') as mock_sheets, \
             patch('modules.claude_client.ClaudeClient') as mock_claude, \
             patch('modules.audio_generator.AudioGenerator') as mock_audio:
            
            # SheetsとClaudeは成功
            mock_sheets_instance = Mock()
            mock_sheets_instance.get_podcast_data.return_value = sample_sheets_data
            mock_sheets.return_value = mock_sheets_instance
            
            mock_claude_instance = Mock()
            mock_claude_instance.generate_content.return_value = sample_claude_content
            mock_claude.return_value = mock_claude_instance
            
            # 音声生成でエラーを発生させる
            mock_audio_instance = Mock()
            mock_audio_instance.generate_audio.side_effect = Exception("音声生成エラー")
            mock_audio.return_value = mock_audio_instance
            
            # テスト実行
            from main import generate_podcast
            
            with pytest.raises(Exception, match="音声生成エラー"):
                await generate_podcast()
    
    @pytest.mark.asyncio
    async def test_pipeline_with_video_error(self, mock_settings, sample_sheets_data, 
                                           sample_claude_content):
        """動画生成エラー時のテスト"""
        with patch('modules.sheets_manager.SheetsManager') as mock_sheets, \
             patch('modules.claude_client.ClaudeClient') as mock_claude, \
             patch('modules.audio_generator.AudioGenerator') as mock_audio, \
             patch('modules.video_generator.VideoGenerator') as mock_video:
            
            # Sheets、Claude、音声生成は成功
            mock_sheets_instance = Mock()
            mock_sheets_instance.get_podcast_data.return_value = sample_sheets_data
            mock_sheets.return_value = mock_sheets_instance
            
            mock_claude_instance = Mock()
            mock_claude_instance.generate_content.return_value = sample_claude_content
            mock_claude.return_value = mock_claude_instance
            
            mock_audio_instance = Mock()
            mock_audio_instance.generate_audio.return_value = "temp/audio.mp3"
            mock_audio.return_value = mock_audio_instance
            
            # 動画生成でエラーを発生させる
            mock_video_instance = Mock()
            mock_video_instance.generate_video.side_effect = Exception("動画生成エラー")
            mock_video.return_value = mock_video_instance
            
            # テスト実行
            from main import generate_podcast
            
            with pytest.raises(Exception, match="動画生成エラー"):
                await generate_podcast()
    
    @pytest.mark.asyncio
    async def test_pipeline_with_storage_error(self, mock_settings, sample_sheets_data, 
                                            sample_claude_content, sample_metadata):
        """ストレージアップロードエラー時のテスト"""
        with patch('modules.sheets_manager.SheetsManager') as mock_sheets, \
             patch('modules.claude_client.ClaudeClient') as mock_claude, \
             patch('modules.audio_generator.AudioGenerator') as mock_audio, \
             patch('modules.video_generator.VideoGenerator') as mock_video, \
             patch('modules.metadata_generator.MetadataGenerator') as mock_metadata, \
             patch('modules.storage_manager.StorageManager') as mock_storage:
            
            # 前段階は成功
            mock_sheets_instance = Mock()
            mock_sheets_instance.get_podcast_data.return_value = sample_sheets_data
            mock_sheets.return_value = mock_sheets_instance
            
            mock_claude_instance = Mock()
            mock_claude_instance.generate_content.return_value = sample_claude_content
            mock_claude.return_value = mock_claude_instance
            
            mock_audio_instance = Mock()
            mock_audio_instance.generate_audio.return_value = "temp/audio.mp3"
            mock_audio.return_value = mock_audio_instance
            
            mock_video_instance = Mock()
            mock_video_instance.generate_video.return_value = "temp/video.mp4"
            mock_video.return_value = mock_video_instance
            
            mock_metadata_instance = Mock()
            mock_metadata_instance.generate_metadata.return_value = sample_metadata
            mock_metadata.return_value = mock_metadata_instance
            
            # ストレージアップロードでエラーを発生させる
            mock_storage_instance = Mock()
            mock_storage_instance.upload_video.side_effect = Exception("ストレージアップロードエラー")
            mock_storage.return_value = mock_storage_instance
            
            # テスト実行
            from main import generate_podcast
            
            with pytest.raises(Exception, match="ストレージアップロードエラー"):
                await generate_podcast()
    
    def test_health_check_endpoint(self):
        """ヘルスチェックエンドポイントのテスト"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self):
        """ルートエンドポイントのテスト"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "message" in response.json()


if __name__ == "__main__":
    pytest.main([__file__])
