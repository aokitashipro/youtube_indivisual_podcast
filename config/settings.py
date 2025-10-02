"""
アプリケーション設定管理
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """アプリケーション設定クラス"""
    
    # Claude API設定
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    
    # Google Sheets設定
    GOOGLE_SHEETS_ID: str = Field(..., env="GOOGLE_SHEETS_ID")
    GOOGLE_CREDENTIALS_PATH: str = Field(
        default="assets/credentials/google-credentials.json",
        env="GOOGLE_CREDENTIALS_PATH"
    )
    
    # OpenAI設定（音声生成用）
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    
    # Slack通知設定
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_CHANNEL: Optional[str] = Field(default=None, env="SLACK_CHANNEL")
    
    # アプリケーション設定
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    TEMP_DIR: str = Field(default="temp/", env="TEMP_DIR")
    OUTPUT_DIR: str = Field(default="output/", env="OUTPUT_DIR")
    
    # Google Drive設定
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = Field(
        default=None, 
        env="GOOGLE_DRIVE_FOLDER_ID"
    )
    
    # 動画設定
    VIDEO_WIDTH: int = Field(default=1920, env="VIDEO_WIDTH")
    VIDEO_HEIGHT: int = Field(default=1080, env="VIDEO_HEIGHT")
    VIDEO_FPS: int = Field(default=30, env="VIDEO_FPS")
    
    # 音声設定
    AUDIO_SAMPLE_RATE: int = Field(default=44100, env="AUDIO_SAMPLE_RATE")
    AUDIO_BITRATE: str = Field(default="192k", env="AUDIO_BITRATE")
    
    # フォント設定
    FONT_PATH: str = Field(
        default="assets/fonts/NotoSansJP-Regular.ttf",
        env="FONT_PATH"
    )
    
    # 背景画像設定
    BACKGROUND_IMAGE_PATH: str = Field(
        default="assets/background.png",
        env="BACKGROUND_IMAGE_PATH"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
