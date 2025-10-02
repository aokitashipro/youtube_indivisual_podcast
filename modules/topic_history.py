"""
トピック履歴管理モジュール

過去に取得したトピックのURLを記録し、重複を防ぐ
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TopicHistory:
    """トピック履歴管理クラス"""
    
    def __init__(self, history_file: str = "temp/topic_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True)
        self._load_history()
    
    def _load_history(self):
        """履歴ファイルを読み込み"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                logger.info(f"履歴ファイルを読み込みました: {len(self.history.get('urls', []))}件")
            except Exception as e:
                logger.warning(f"履歴ファイルの読み込みに失敗: {e}")
                self.history = {"urls": [], "topics": []}
        else:
            self.history = {"urls": [], "topics": []}
            logger.info("新しい履歴ファイルを作成します")
    
    def _save_history(self):
        """履歴ファイルを保存"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            logger.info(f"履歴ファイルを保存しました: {len(self.history.get('urls', []))}件")
        except Exception as e:
            logger.error(f"履歴ファイルの保存に失敗: {e}")
    
    def get_used_urls(self) -> Set[str]:
        """過去に使用したURLのセットを取得"""
        return set(self.history.get("urls", []))
    
    def is_duplicate(self, url: str) -> bool:
        """URLが重複しているかチェック"""
        return url in self.get_used_urls()
    
    def add_topic(self, topic: Dict[str, Any]):
        """トピックを履歴に追加"""
        url = topic.get("url", "")
        if not url:
            logger.warning("URLが空のトピックは追加できません")
            return
        
        if url not in self.history["urls"]:
            self.history["urls"].append(url)
            self.history["topics"].append({
                "url": url,
                "title_ja": topic.get("title_ja", ""),
                "title_en": topic.get("title_en", ""),
                "added_at": datetime.now().isoformat(),
                "category": topic.get("category", ""),
                "source": topic.get("source", "")
            })
            self._save_history()
            logger.info(f"トピックを履歴に追加: {topic.get('title_ja', 'N/A')}")
        else:
            logger.debug(f"重複トピック（スキップ）: {url}")
    
    def add_topics(self, topics: List[Dict[str, Any]]):
        """複数のトピックを履歴に追加"""
        for topic in topics:
            self.add_topic(topic)
    
    def filter_duplicates(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """トピックリストから重複を除外"""
        used_urls = self.get_used_urls()
        filtered_topics = []
        
        for topic in topics:
            url = topic.get("url", "")
            if url and url not in used_urls:
                filtered_topics.append(topic)
            else:
                logger.info(f"重複トピックを除外: {topic.get('title_ja', 'N/A')} - {url}")
        
        logger.info(f"重複チェック完了: {len(topics)}件 → {len(filtered_topics)}件（{len(topics) - len(filtered_topics)}件除外）")
        return filtered_topics
    
    def get_history_count(self) -> int:
        """履歴に保存されているトピック数を取得"""
        return len(self.history.get("urls", []))
    
    def get_recent_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """最近のトピックを取得"""
        topics = self.history.get("topics", [])
        return topics[-limit:] if len(topics) > limit else topics
    
    def clear_history(self):
        """履歴をクリア（注意: 全削除）"""
        self.history = {"urls": [], "topics": []}
        self._save_history()
        logger.warning("履歴をクリアしました")

