"""
メタデータ生成モジュール
"""
from typing import Dict, Any
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class MetadataGenerator:
    """メタデータ生成クラス"""
    
    def __init__(self, settings):
        self.settings = settings
    
    async def generate_metadata(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """メタデータを生成"""
        try:
            logger.info("メタデータを生成します")
            
            # 基本メタデータを生成
            metadata = {
                "title": self._generate_title(content),
                "description": self._generate_description(content),
                "tags": self._generate_tags(content),
                "category": self._generate_category(content),
                "thumbnail_suggestion": self._generate_thumbnail_suggestion(content),
                "created_at": datetime.now().isoformat(),
                "duration": self._estimate_duration(content),
                "language": "ja",
                "privacy_status": "private"
            }
            
            logger.info("メタデータの生成が完了しました")
            return metadata
            
        except Exception as e:
            logger.error(f"メタデータ生成に失敗しました: {e}")
            raise
    
    def _generate_title(self, content: Dict[str, Any]) -> str:
        """タイトルを生成"""
        try:
            # 既存のタイトルがある場合は使用
            if content.get("title"):
                title = content["title"]
            else:
                # タイトルがない場合は生成
                title = "AI生成ポッドキャスト"
            
            # タイトルの長さを制限（YouTubeの制限: 100文字）
            if len(title) > 100:
                title = title[:97] + "..."
            
            logger.info(f"タイトルを生成しました: {title}")
            return title
            
        except Exception as e:
            logger.error(f"タイトルの生成に失敗しました: {e}")
            return "AI生成ポッドキャスト"
    
    def _generate_description(self, content: Dict[str, Any]) -> str:
        """説明文を生成"""
        try:
            description_parts = []
            
            # 概要を追加
            if content.get("summary"):
                description_parts.append(content["summary"])
            
            # キーポイントを追加
            if content.get("key_points"):
                description_parts.append("\nキーポイント:")
                for point in content["key_points"]:
                    description_parts.append(f"• {point}")
            
            # 結論を追加
            if content.get("conclusion"):
                description_parts.append(f"\n結論: {content['conclusion']}")
            
            # ハッシュタグを追加
            description_parts.append("\n\n#AI #ポッドキャスト #自動生成")
            
            description = "\n".join(description_parts)
            
            # 説明文の長さを制限（YouTubeの制限: 5000文字）
            if len(description) > 5000:
                description = description[:4997] + "..."
            
            logger.info(f"説明文を生成しました: {len(description)}文字")
            return description
            
        except Exception as e:
            logger.error(f"説明文の生成に失敗しました: {e}")
            return "AI生成ポッドキャストの説明文"
    
    def _generate_tags(self, content: Dict[str, Any]) -> list:
        """タグを生成"""
        try:
            tags = []
            
            # 基本タグ
            base_tags = ["AI", "ポッドキャスト", "自動生成", "人工知能"]
            tags.extend(base_tags)
            
            # コンテンツからキーワードを抽出
            if content.get("main_content"):
                keywords = self._extract_keywords(content["main_content"])
                tags.extend(keywords)
            
            # タグの重複を削除
            tags = list(set(tags))
            
            # タグの数を制限（YouTubeの制限: 15個）
            if len(tags) > 15:
                tags = tags[:15]
            
            logger.info(f"タグを生成しました: {tags}")
            return tags
            
        except Exception as e:
            logger.error(f"タグの生成に失敗しました: {e}")
            return ["AI", "ポッドキャスト", "自動生成"]
    
    def _extract_keywords(self, text: str) -> list:
        """テキストからキーワードを抽出"""
        try:
            # 日本語のキーワードを抽出する簡単な実装
            keywords = []
            
            # 一般的なキーワード
            common_keywords = [
                "テクノロジー", "AI", "人工知能", "機械学習", "データサイエンス",
                "プログラミング", "開発", "イノベーション", "デジタル", "自動化"
            ]
            
            text_lower = text.lower()
            for keyword in common_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
            
            return keywords
            
        except Exception as e:
            logger.error(f"キーワードの抽出に失敗しました: {e}")
            return []
    
    def _generate_category(self, content: Dict[str, Any]) -> str:
        """カテゴリを生成"""
        try:
            # デフォルトカテゴリ
            category = "Science & Technology"
            
            # コンテンツに基づいてカテゴリを決定
            if content.get("main_content"):
                text = content["main_content"].lower()
                
                if any(word in text for word in ["ビジネス", "経営", "マーケティング"]):
                    category = "Business"
                elif any(word in text for word in ["教育", "学習", "学校"]):
                    category = "Education"
                elif any(word in text for word in ["エンターテイメント", "映画", "音楽"]):
                    category = "Entertainment"
                elif any(word in text for word in ["健康", "医療", "フィットネス"]):
                    category = "Health"
            
            logger.info(f"カテゴリを生成しました: {category}")
            return category
            
        except Exception as e:
            logger.error(f"カテゴリの生成に失敗しました: {e}")
            return "Science & Technology"
    
    def _generate_thumbnail_suggestion(self, content: Dict[str, Any]) -> str:
        """サムネイルの提案を生成"""
        try:
            suggestions = []
            
            # タイトルに基づく提案
            if content.get("title"):
                title = content["title"]
                suggestions.append(f"タイトル: {title}")
                suggestions.append("大きなフォントでタイトルを表示")
            
            # キーワードに基づく提案
            if content.get("key_points"):
                suggestions.append("キーポイントを箇条書きで表示")
            
            # 一般的な提案
            suggestions.extend([
                "鮮やかな色を使用",
                "読みやすいフォント",
                "関連する画像やアイコンを追加",
                "ブランドカラーを統一"
            ])
            
            suggestion_text = "\n".join(suggestions)
            
            logger.info("サムネイルの提案を生成しました")
            return suggestion_text
            
        except Exception as e:
            logger.error(f"サムネイル提案の生成に失敗しました: {e}")
            return "サムネイルの提案を生成できませんでした"
    
    def _estimate_duration(self, content: Dict[str, Any]) -> int:
        """動画の長さを推定（秒）"""
        try:
            # テキストの長さから音声の長さを推定
            total_text = ""
            
            if content.get("title"):
                total_text += content["title"]
            if content.get("summary"):
                total_text += content["summary"]
            if content.get("main_content"):
                total_text += content["main_content"]
            if content.get("conclusion"):
                total_text += content["conclusion"]
            
            # 日本語の平均的な読み上げ速度: 1文字あたり0.3秒
            estimated_duration = len(total_text) * 0.3
            
            # 最小値と最大値を設定
            estimated_duration = max(60, min(estimated_duration, 3600))  # 1分〜1時間
            
            logger.info(f"動画の長さを推定しました: {estimated_duration:.1f}秒")
            return int(estimated_duration)
            
        except Exception as e:
            logger.error(f"動画の長さの推定に失敗しました: {e}")
            return 300  # デフォルト5分
