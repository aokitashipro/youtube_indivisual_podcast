"""
Slack通知モジュール
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Notifier:
    """Slack通知クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Slackクライアントを設定"""
        try:
            if self.settings.SLACK_BOT_TOKEN:
                self.client = WebClient(token=self.settings.SLACK_BOT_TOKEN)
                logger.info("Slackクライアントが正常に初期化されました")
            else:
                logger.warning("Slack Bot Tokenが設定されていません")
                
        except Exception as e:
            logger.error(f"Slackクライアントの初期化に失敗しました: {e}")
            self.client = None
    
    async def send_completion_notification(self, drive_url: str, metadata: Dict[str, Any]):
        """完了通知を送信"""
        try:
            if not self.client:
                logger.warning("Slackクライアントが利用できません")
                return
            
            # 通知メッセージを構築
            message = self._build_completion_message(drive_url, metadata)
            
            # Slackにメッセージを送信
            response = self.client.chat_postMessage(
                channel=self.settings.SLACK_CHANNEL,
                text=message
            )
            
            logger.info("完了通知を送信しました")
            
        except SlackApiError as e:
            logger.error(f"Slack通知の送信に失敗しました: {e}")
        except Exception as e:
            logger.error(f"通知の送信に失敗しました: {e}")
    
    def _build_completion_message(self, drive_url: str, metadata: Dict[str, Any]) -> str:
        """完了通知メッセージを構築"""
        try:
            message_parts = [
                "🎉 ポッドキャスト生成が完了しました！",
                "",
                f"📹 タイトル: {metadata.get('title', 'N/A')}",
                f"⏱️ 推定時間: {metadata.get('duration', 'N/A')}秒",
                f"📁 カテゴリ: {metadata.get('category', 'N/A')}",
                "",
                f"🔗 動画リンク: {drive_url}",
                "",
                "タグ: " + ", ".join(metadata.get('tags', []))
            ]
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"完了通知メッセージの構築に失敗しました: {e}")
            return "ポッドキャスト生成が完了しました"
    
    async def send_error_notification(self, error_message: str):
        """エラー通知を送信"""
        try:
            if not self.client:
                logger.warning("Slackクライアントが利用できません")
                return
            
            # エラー通知メッセージを構築
            message = self._build_error_message(error_message)
            
            # Slackにメッセージを送信
            response = self.client.chat_postMessage(
                channel=self.settings.SLACK_CHANNEL,
                text=message
            )
            
            logger.info("エラー通知を送信しました")
            
        except SlackApiError as e:
            logger.error(f"Slackエラー通知の送信に失敗しました: {e}")
        except Exception as e:
            logger.error(f"エラー通知の送信に失敗しました: {e}")
    
    def _build_error_message(self, error_message: str) -> str:
        """エラー通知メッセージを構築"""
        try:
            message_parts = [
                "❌ ポッドキャスト生成中にエラーが発生しました",
                "",
                f"エラー詳細: {error_message}",
                "",
                "管理者に連絡してください。"
            ]
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"エラー通知メッセージの構築に失敗しました: {e}")
            return "ポッドキャスト生成中にエラーが発生しました"
    
    async def send_progress_notification(self, step: str, progress: int = 0):
        """進捗通知を送信"""
        try:
            if not self.client:
                logger.warning("Slackクライアントが利用できません")
                return
            
            # 進捗通知メッセージを構築
            message = self._build_progress_message(step, progress)
            
            # Slackにメッセージを送信
            response = self.client.chat_postMessage(
                channel=self.settings.SLACK_CHANNEL,
                text=message
            )
            
            logger.info(f"進捗通知を送信しました: {step}")
            
        except SlackApiError as e:
            logger.error(f"Slack進捗通知の送信に失敗しました: {e}")
        except Exception as e:
            logger.error(f"進捗通知の送信に失敗しました: {e}")
    
    def _build_progress_message(self, step: str, progress: int) -> str:
        """進捗通知メッセージを構築"""
        try:
            progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
            
            message_parts = [
                f"🔄 ポッドキャスト生成中...",
                "",
                f"現在のステップ: {step}",
                f"進捗: {progress}% [{progress_bar}]",
                "",
                "しばらくお待ちください..."
            ]
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"進捗通知メッセージの構築に失敗しました: {e}")
            return f"ポッドキャスト生成中: {step}"
    
    async def send_test_notification(self):
        """テスト通知を送信"""
        try:
            if not self.client:
                logger.warning("Slackクライアントが利用できません")
                return
            
            message = "🧪 Slack通知のテストです。設定が正常に動作しています。"
            
            response = self.client.chat_postMessage(
                channel=self.settings.SLACK_CHANNEL,
                text=message
            )
            
            logger.info("テスト通知を送信しました")
            
        except SlackApiError as e:
            logger.error(f"Slackテスト通知の送信に失敗しました: {e}")
        except Exception as e:
            logger.error(f"テスト通知の送信に失敗しました: {e}")
    
    async def send_custom_notification(self, message: str, channel: str = None):
        """カスタム通知を送信"""
        try:
            if not self.client:
                logger.warning("Slackクライアントが利用できません")
                return
            
            target_channel = channel or self.settings.SLACK_CHANNEL
            
            response = self.client.chat_postMessage(
                channel=target_channel,
                text=message
            )
            
            logger.info(f"カスタム通知を送信しました: {target_channel}")
            
        except SlackApiError as e:
            logger.error(f"Slackカスタム通知の送信に失敗しました: {e}")
        except Exception as e:
            logger.error(f"カスタム通知の送信に失敗しました: {e}")
