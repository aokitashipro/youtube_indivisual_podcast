"""
処理時間計測モジュール
"""
import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from contextlib import contextmanager, asynccontextmanager


class Timer:
    """処理時間計測クラス"""
    
    def __init__(self, name: str = "Timer", logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.timings = []
        self.is_running = False
    
    def start(self):
        """計測開始"""
        self.start_time = time.time()
        self.is_running = True
        self.logger.debug(f"{self.name} の計測を開始しました")
    
    def stop(self):
        """計測終了"""
        if self.start_time is None:
            self.logger.warning(f"{self.name} の計測が開始されていません")
            return
        
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.is_running = False
        
        self.logger.info(f"{self.name} の処理時間: {self.duration:.3f}秒")
        
        # タイミングを記録
        self.timings.append({
            "name": self.name,
            "duration": self.duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_formatted_time(self) -> str:
        """フォーマットされた処理時間を取得（例: "25分30秒"）"""
        if self.duration is None:
            return "0秒"
        
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        
        if minutes > 0:
            return f"{minutes}分{seconds}秒"
        else:
            return f"{seconds}秒"
    
    def get_duration(self) -> Optional[float]:
        """処理時間を取得"""
        return self.duration
    
    def get_timings(self) -> list:
        """全てのタイミングを取得"""
        return self.timings.copy()
    
    def get_average_duration(self) -> float:
        """平均処理時間を取得"""
        if not self.timings:
            return 0.0
        
        total_duration = sum(timing["duration"] for timing in self.timings)
        return total_duration / len(self.timings)
    
    def get_total_duration(self) -> float:
        """総処理時間を取得"""
        return sum(timing["duration"] for timing in self.timings)
    
    def clear_timings(self):
        """タイミング履歴をクリア"""
        self.timings.clear()
        self.logger.debug(f"{self.name} のタイミング履歴をクリアしました")


class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.timers = {}
        self.performance_data = []
    
    def create_timer(self, name: str) -> Timer:
        """タイマーを作成"""
        timer = Timer(name, self.logger)
        self.timers[name] = timer
        return timer
    
    def get_timer(self, name: str) -> Optional[Timer]:
        """タイマーを取得"""
        return self.timers.get(name)
    
    def record_performance(self, name: str, duration: float, metadata: Dict[str, Any] = None):
        """パフォーマンスデータを記録"""
        performance_record = {
            "name": name,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.performance_data.append(performance_record)
        self.logger.debug(f"パフォーマンスデータを記録しました: {name} ({duration:.3f}秒)")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        if not self.performance_data:
            return {"total_records": 0}
        
        # 名前別の集計
        name_stats = {}
        for record in self.performance_data:
            name = record["name"]
            if name not in name_stats:
                name_stats[name] = {
                    "count": 0,
                    "total_duration": 0.0,
                    "min_duration": float('inf'),
                    "max_duration": 0.0
                }
            
            stats = name_stats[name]
            stats["count"] += 1
            stats["total_duration"] += record["duration"]
            stats["min_duration"] = min(stats["min_duration"], record["duration"])
            stats["max_duration"] = max(stats["max_duration"], record["duration"])
        
        # 平均値を計算
        for name, stats in name_stats.items():
            stats["average_duration"] = stats["total_duration"] / stats["count"]
            stats["min_duration"] = stats["min_duration"] if stats["min_duration"] != float('inf') else 0.0
        
        return {
            "total_records": len(self.performance_data),
            "name_stats": name_stats,
            "overall_stats": {
                "total_duration": sum(record["duration"] for record in self.performance_data),
                "average_duration": sum(record["duration"] for record in self.performance_data) / len(self.performance_data)
            }
        }
    
    def clear_performance_data(self):
        """パフォーマンスデータをクリア"""
        self.performance_data.clear()
        self.logger.debug("パフォーマンスデータをクリアしました")


@contextmanager
def timer_context(name: str, logger: Optional[logging.Logger] = None):
    """コンテキストマネージャーとしてタイマーを使用"""
    timer = Timer(name, logger)
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()


@asynccontextmanager
async def async_timer_context(name: str, logger: Optional[logging.Logger] = None):
    """非同期コンテキストマネージャーとしてタイマーを使用"""
    timer = Timer(name, logger)
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()


def time_function(func):
    """関数の実行時間を計測するデコレーター"""
    def wrapper(*args, **kwargs):
        timer = Timer(func.__name__)
        timer.start()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            timer.stop()
    
    return wrapper


def time_async_function(func):
    """非同期関数の実行時間を計測するデコレーター"""
    async def wrapper(*args, **kwargs):
        timer = Timer(func.__name__)
        timer.start()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            timer.stop()
    
    return wrapper


class Benchmark:
    """ベンチマーククラス"""
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.results = []
    
    def run(self, func, *args, **kwargs):
        """関数を実行してベンチマーク"""
        timer = Timer(f"{self.name}_benchmark", self.logger)
        timer.start()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            timer.stop()
            self.results.append({
                "function": func.__name__,
                "duration": timer.get_duration(),
                "timestamp": datetime.now().isoformat()
            })
    
    async def run_async(self, func, *args, **kwargs):
        """非同期関数を実行してベンチマーク"""
        timer = Timer(f"{self.name}_async_benchmark", self.logger)
        timer.start()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            timer.stop()
            self.results.append({
                "function": func.__name__,
                "duration": timer.get_duration(),
                "timestamp": datetime.now().isoformat()
            })
    
    def get_results(self) -> list:
        """ベンチマーク結果を取得"""
        return self.results.copy()
    
    def get_average_duration(self) -> float:
        """平均実行時間を取得"""
        if not self.results:
            return 0.0
        
        total_duration = sum(result["duration"] for result in self.results)
        return total_duration / len(self.results)
    
    def clear_results(self):
        """結果をクリア"""
        self.results.clear()
        self.logger.debug(f"{self.name} のベンチマーク結果をクリアしました")
