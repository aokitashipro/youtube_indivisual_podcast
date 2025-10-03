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
            # 認証情報を設定（読み書き権限）
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
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
    
    async def append_metadata_row(
        self,
        metadata: Dict[str, Any],
        comment: str,
        video_path: str = "",
        audio_path: str = "",
        thumbnail_path: str = "",
        execution_time: float = 0
    ) -> int:
        """
        メタデータを新規行として追加
        
        Args:
            metadata: メタデータ（title, description, tags, thumbnail_text）
            comment: コメントテキスト
            video_path: 動画ファイルパス
            audio_path: 音声ファイルパス
            thumbnail_path: サムネイルファイルパス
            execution_time: 処理時間（秒）
            
        Returns:
            追加された行番号
        """
        try:
            from datetime import datetime
            
            spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEETS_ID)
            worksheet = spreadsheet.sheet1
            
            # 行データを準備
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 実行日時
                metadata.get('title', ''),  # タイトル
                metadata.get('description', '')[:500],  # 説明文（最初の500文字）
                ', '.join(metadata.get('tags', [])),  # タグ
                metadata.get('thumbnail_text', ''),  # サムネイルテキスト
                comment,  # コメント
                video_path,  # 動画パス
                audio_path,  # 音声パス
                thumbnail_path,  # サムネイルパス
                f"{execution_time:.1f}秒",  # 処理時間
                "完了"  # ステータス
            ]
            
            # 行を追加
            worksheet.append_row(row_data)
            
            # 追加された行番号を取得
            row_number = len(worksheet.get_all_values())
            
            logger.info(f"✅ メタデータを行{row_number}に追加しました")
            logger.info(f"   タイトル: {metadata.get('title', 'N/A')[:50]}...")
            
            return row_number
            
        except Exception as e:
            logger.error(f"❌ メタデータの追加に失敗: {e}")
            raise
    
    async def update_row_with_urls(
        self,
        row_number: int,
        video_url: str = "",
        audio_url: str = "",
        thumbnail_url: str = ""
    ):
        """
        行にDrive URLを更新
        
        Args:
            row_number: 行番号
            video_url: 動画のDrive URL
            audio_url: 音声のDrive URL
            thumbnail_url: サムネイルのDrive URL
        """
        try:
            spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEETS_ID)
            worksheet = spreadsheet.sheet1
            
            # URL列を更新（仮に12-14列目とする）
            if video_url:
                worksheet.update_cell(row_number, 12, video_url)
            if audio_url:
                worksheet.update_cell(row_number, 13, audio_url)
            if thumbnail_url:
                worksheet.update_cell(row_number, 14, thumbnail_url)
            
            logger.info(f"✅ 行{row_number}にURLを更新しました")
            
        except Exception as e:
            logger.error(f"❌ URLの更新に失敗: {e}")
            raise
