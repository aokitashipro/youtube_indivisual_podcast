"""
アプリケーション設定管理
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定クラス"""
    
    # Claude API設定（必須）
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    
    # Google Sheets設定（オプション: ステップ2, 11で使用）
    GOOGLE_SHEETS_ID: Optional[str] = Field(default=None, env="GOOGLE_SHEETS_ID")
    GOOGLE_CREDENTIALS_PATH: str = Field(
        default="assets/credentials/google-credentials.json",
        env="GOOGLE_CREDENTIALS_PATH"
    )
    GAS_WEB_APP_URL: Optional[str] = Field(default=None, env="GAS_WEB_APP_URL")
    
    # Google Drive設定
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = Field(default=None, env="GOOGLE_DRIVE_FOLDER_ID")
    
    # OpenAI設定（オプション: 音声生成で使用しない）
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Slack通知設定
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_CHANNEL: Optional[str] = Field(default=None, env="SLACK_CHANNEL")
    
    # Google Gemini API設定（複数APIキー対応・推奨）
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    GEMINI_API_KEY_1: Optional[str] = Field(default=None, env="GEMINI_API_KEY_1")
    GEMINI_API_KEY_2: Optional[str] = Field(default=None, env="GEMINI_API_KEY_2")
    GEMINI_API_KEY_3: Optional[str] = Field(default=None, env="GEMINI_API_KEY_3")
    
    # ElevenLabs API設定
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    
    # Google Cloud TTS設定（オプション・認証ファイル必要）
    GOOGLE_TTS_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_TTS_API_KEY")
    GOOGLE_TTS_API_KEY_1: Optional[str] = Field(default=None, env="GOOGLE_TTS_API_KEY_1")
    GOOGLE_TTS_API_KEY_2: Optional[str] = Field(default=None, env="GOOGLE_TTS_API_KEY_2")
    GOOGLE_TTS_API_KEY_3: Optional[str] = Field(default=None, env="GOOGLE_TTS_API_KEY_3")
    
    # 音声設定
    VOICE_A: str = Field(default="ja-JP-Neural2-C", env="VOICE_A")
    VOICE_A_PITCH: float = Field(default=0.0, env="VOICE_A_PITCH")
    VOICE_B: str = Field(default="ja-JP-Standard-A", env="VOICE_B")
    VOICE_B_PITCH: float = Field(default=0.0, env="VOICE_B_PITCH")
    
    # 音声設定（追加）
    VOICE_B_SPEAKING_RATE: float = Field(default=1.2, env="VOICE_B_SPEAKING_RATE")
    
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
