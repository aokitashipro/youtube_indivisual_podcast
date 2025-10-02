"""
Google Sheets操作モジュール
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class SheetsManager:
    """Google Sheets操作クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Google Sheetsクライアントを設定"""
        try:
            # 認証情報を設定
            scope = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            creds = Credentials.from_service_account_file(
                self.settings.GOOGLE_CREDENTIALS_PATH,
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            logger.info("Google Sheetsクライアントが正常に初期化されました")
            
        except Exception as e:
            logger.error(f"Google Sheetsクライアントの初期化に失敗しました: {e}")
            raise
    
    async def get_podcast_data(self) -> Dict[str, Any]:
        """ポッドキャストデータを取得"""
        try:
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEETS_ID)
            
            # 最初のワークシートを取得
            worksheet = spreadsheet.sheet1
            
            # 全データを取得
            all_records = worksheet.get_all_records()
            
            if not all_records:
                logger.warning("スプレッドシートにデータが見つかりません")
                return {}
            
            # 最新のデータを取得（最初の行を最新とする）
            latest_data = all_records[0]
            
            logger.info(f"ポッドキャストデータを取得しました: {len(all_records)}件のレコード")
            
            return {
                "raw_data": all_records,
                "latest_data": latest_data,
                "total_records": len(all_records)
            }
            
        except Exception as e:
            logger.error(f"ポッドキャストデータの取得に失敗しました: {e}")
            raise
    
    async def get_specific_data(self, sheet_name: str, range_name: str = None) -> List[Dict[str, Any]]:
        """特定のシートからデータを取得"""
        try:
            spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEETS_ID)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            if range_name:
                data = worksheet.get(range_name)
            else:
                data = worksheet.get_all_records()
            
            logger.info(f"シート '{sheet_name}' からデータを取得しました")
            return data
            
        except Exception as e:
            logger.error(f"シート '{sheet_name}' からのデータ取得に失敗しました: {e}")
            raise
    
    async def update_data(self, sheet_name: str, cell: str, value: str):
        """データを更新"""
        try:
            spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEETS_ID)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            worksheet.update(cell, value)
            logger.info(f"セル {cell} を '{value}' に更新しました")
            
        except Exception as e:
            logger.error(f"データの更新に失敗しました: {e}")
            raise
