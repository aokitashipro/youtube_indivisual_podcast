"""
エラーハンドリングモジュール
"""
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
import json


class ErrorHandler:
    """エラーハンドリングクラス"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_count = 0
        self.error_history = []
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """エラーを処理"""
        try:
            self.error_count += 1
            
            # エラー情報を構築
            error_info = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {},
                "error_count": self.error_count
            }
            
            # エラーログを記録
            self.logger.error(f"エラーが発生しました: {error_info['error_message']}")
            self.logger.debug(f"エラー詳細: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
            
            # エラーヒストリーに追加
            self.error_history.append(error_info)
            
            # エラーヒストリーのサイズを制限
            if len(self.error_history) > 100:
                self.error_history = self.error_history[-100:]
            
            return error_info
            
        except Exception as e:
            self.logger.error(f"エラーハンドリング中にエラーが発生しました: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error_type": "ErrorHandlerError",
                "error_message": str(e),
                "context": {"original_error": str(error)}
            }
    
    def handle_validation_error(self, error: Exception, field: str = None) -> Dict[str, Any]:
        """バリデーションエラーを処理"""
        try:
            error_info = {
                "timestamp": datetime.now().isoformat(),
                "error_type": "ValidationError",
                "error_message": str(error),
                "field": field,
                "context": {"validation_failed": True}
            }
            
            self.logger.warning(f"バリデーションエラー: {error_info['error_message']}")
            return error_info
            
        except Exception as e:
            self.logger.error(f"バリデーションエラーハンドリング中にエラーが発生しました: {e}")
            return self.handle_error(e)
    
    def handle_api_error(self, error: Exception, api_name: str = None) -> Dict[str, Any]:
        """APIエラーを処理"""
        try:
            error_info = {
                "timestamp": datetime.now().isoformat(),
                "error_type": "APIError",
                "error_message": str(error),
                "api_name": api_name,
                "context": {"api_call_failed": True}
            }
            
            self.logger.error(f"APIエラー ({api_name}): {error_info['error_message']}")
            return error_info
            
        except Exception as e:
            self.logger.error(f"APIエラーハンドリング中にエラーが発生しました: {e}")
            return self.handle_error(e)
    
    def handle_file_error(self, error: Exception, file_path: str = None) -> Dict[str, Any]:
        """ファイルエラーを処理"""
        try:
            error_info = {
                "timestamp": datetime.now().isoformat(),
                "error_type": "FileError",
                "error_message": str(error),
                "file_path": file_path,
                "context": {"file_operation_failed": True}
            }
            
            self.logger.error(f"ファイルエラー ({file_path}): {error_info['error_message']}")
            return error_info
            
        except Exception as e:
            self.logger.error(f"ファイルエラーハンドリング中にエラーが発生しました: {e}")
            return self.handle_error(e)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """エラーサマリーを取得"""
        try:
            if not self.error_history:
                return {"total_errors": 0, "recent_errors": []}
            
            # 最近のエラーを取得
            recent_errors = self.error_history[-10:] if len(self.error_history) > 10 else self.error_history
            
            # エラータイプ別の集計
            error_types = {}
            for error in self.error_history:
                error_type = error.get("error_type", "Unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            return {
                "total_errors": self.error_count,
                "recent_errors": recent_errors,
                "error_types": error_types,
                "last_error": self.error_history[-1] if self.error_history else None
            }
            
        except Exception as e:
            self.logger.error(f"エラーサマリーの取得に失敗しました: {e}")
            return {"total_errors": 0, "recent_errors": []}
    
    def clear_error_history(self):
        """エラーヒストリーをクリア"""
        try:
            self.error_history.clear()
            self.error_count = 0
            self.logger.info("エラーヒストリーをクリアしました")
            
        except Exception as e:
            self.logger.error(f"エラーヒストリーのクリアに失敗しました: {e}")
    
    def is_error_rate_high(self, threshold: float = 0.1) -> bool:
        """エラー率が高いかどうかを判定"""
        try:
            if self.error_count == 0:
                return False
            
            # 最近のエラー率を計算（簡易実装）
            recent_errors = len([e for e in self.error_history[-10:] if e])
            return recent_errors / 10 > threshold
            
        except Exception as e:
            self.logger.error(f"エラー率の計算に失敗しました: {e}")
            return False


class RetryHandler:
    """リトライハンドリングクラス"""
    
    def __init__(self, logger: logging.Logger, max_retries: int = 3, delay: float = 1.0):
        self.logger = logger
        self.max_retries = max_retries
        self.delay = delay
    
    async def retry_async(self, func, *args, **kwargs):
        """非同期関数をリトライ"""
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    self.logger.error(f"最大リトライ回数に達しました: {e}")
                    raise
                
                self.logger.warning(f"リトライ {attempt + 1}/{self.max_retries}: {e}")
                await asyncio.sleep(self.delay * (2 ** attempt))  # 指数バックオフ
    
    def retry_sync(self, func, *args, **kwargs):
        """同期関数をリトライ"""
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    self.logger.error(f"最大リトライ回数に達しました: {e}")
                    raise
                
                self.logger.warning(f"リトライ {attempt + 1}/{self.max_retries}: {e}")
                import time
                time.sleep(self.delay * (2 ** attempt))  # 指数バックオフ
