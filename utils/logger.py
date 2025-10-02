"""
ロギング設定モジュール
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """ロガーを設定"""
    try:
        # ログレベルを設定
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # ロガーを作成
        logger = logging.getLogger("youtube_ai_podcast")
        logger.setLevel(numeric_level)
        
        # 既存のハンドラーをクリア
        logger.handlers.clear()
        
        # フォーマッターを設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # コンソールハンドラーを追加
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # ファイルハンドラーを追加（指定されている場合）
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # ログの重複を防ぐ
        logger.propagate = False
        
        logger.info(f"ロガーが初期化されました: レベル={log_level}")
        return logger
        
    except Exception as e:
        print(f"ロガーの初期化に失敗しました: {e}")
        # フォールバック用のシンプルなロガー
        fallback_logger = logging.getLogger("youtube_ai_podcast_fallback")
        fallback_logger.setLevel(logging.INFO)
        return fallback_logger


def get_logger(name: str = "youtube_ai_podcast") -> logging.Logger:
    """ロガーを取得"""
    return logging.getLogger(name)


class LoggerMixin:
    """ロガーミックスインクラス"""
    
    @property
    def logger(self) -> logging.Logger:
        """ロガーを取得"""
        return get_logger(self.__class__.__name__)


def log_function_call(func):
    """関数呼び出しをログに記録するデコレーター"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"関数 '{func.__name__}' を呼び出し中...")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"関数 '{func.__name__}' が正常に完了しました")
            return result
        except Exception as e:
            logger.error(f"関数 '{func.__name__}' でエラーが発生しました: {e}")
            raise
    
    return wrapper


def log_async_function_call(func):
    """非同期関数呼び出しをログに記録するデコレーター"""
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"非同期関数 '{func.__name__}' を呼び出し中...")
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"非同期関数 '{func.__name__}' が正常に完了しました")
            return result
        except Exception as e:
            logger.error(f"非同期関数 '{func.__name__}' でエラーが発生しました: {e}")
            raise
    
    return wrapper
