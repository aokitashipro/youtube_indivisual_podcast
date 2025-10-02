"""
Google Drive操作モジュール
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageManager:
    """Google Drive操作クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.service = None
        self._setup_service()
    
    def _setup_service(self):
        """Google Driveサービスを設定"""
        try:
            # 認証情報を設定
            scope = [
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive.metadata'
            ]
            
            creds = Credentials.from_service_account_file(
                self.settings.GOOGLE_CREDENTIALS_PATH,
                scopes=scope
            )
            
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Driveサービスが正常に初期化されました")
            
        except Exception as e:
            logger.error(f"Google Driveサービスの初期化に失敗しました: {e}")
            raise
    
    async def upload_video(self, video_path: str, metadata: Dict[str, Any]) -> str:
        """動画ファイルをGoogle Driveにアップロード"""
        try:
            logger.info(f"動画ファイルをアップロードします: {video_path}")
            
            # ファイルのメタデータを設定
            file_metadata = {
                'name': Path(video_path).name,
                'description': metadata.get('description', ''),
                'parents': [self.settings.GOOGLE_DRIVE_FOLDER_ID] if self.settings.GOOGLE_DRIVE_FOLDER_ID else None
            }
            
            # メディアファイルを準備
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True
            )
            
            # ファイルをアップロード
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            # ファイルの共有設定
            self._set_file_permissions(file['id'])
            
            # 共有リンクを取得
            share_link = file.get('webViewLink', '')
            
            logger.info(f"動画ファイルのアップロードが完了しました: {share_link}")
            return share_link
            
        except Exception as e:
            logger.error(f"動画ファイルのアップロードに失敗しました: {e}")
            raise
    
    def _set_file_permissions(self, file_id: str):
        """ファイルの共有権限を設定"""
        try:
            # ファイルを一般公開に設定
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            logger.info(f"ファイルの共有権限を設定しました: {file_id}")
            
        except Exception as e:
            logger.error(f"ファイルの共有権限設定に失敗しました: {e}")
            # エラーが発生しても処理を続行
    
    async def upload_audio(self, audio_path: str, metadata: Dict[str, Any]) -> str:
        """音声ファイルをGoogle Driveにアップロード"""
        try:
            logger.info(f"音声ファイルをアップロードします: {audio_path}")
            
            # ファイルのメタデータを設定
            file_metadata = {
                'name': Path(audio_path).name,
                'description': metadata.get('description', ''),
                'parents': [self.settings.GOOGLE_DRIVE_FOLDER_ID] if self.settings.GOOGLE_DRIVE_FOLDER_ID else None
            }
            
            # メディアファイルを準備
            media = MediaFileUpload(
                audio_path,
                mimetype='audio/mpeg',
                resumable=True
            )
            
            # ファイルをアップロード
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            # ファイルの共有設定
            self._set_file_permissions(file['id'])
            
            # 共有リンクを取得
            share_link = file.get('webViewLink', '')
            
            logger.info(f"音声ファイルのアップロードが完了しました: {share_link}")
            return share_link
            
        except Exception as e:
            logger.error(f"音声ファイルのアップロードに失敗しました: {e}")
            raise
    
    async def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """フォルダを作成"""
        try:
            logger.info(f"フォルダを作成します: {folder_name}")
            
            # フォルダのメタデータを設定
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id] if parent_folder_id else None
            }
            
            # フォルダを作成
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id,name'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"フォルダが作成されました: {folder_id}")
            return folder_id
            
        except Exception as e:
            logger.error(f"フォルダの作成に失敗しました: {e}")
            raise
    
    async def list_files(self, folder_id: str = None) -> list:
        """ファイル一覧を取得"""
        try:
            logger.info("ファイル一覧を取得します")
            
            # クエリを構築
            query = f"'{folder_id}' in parents" if folder_id else None
            
            # ファイル一覧を取得
            results = self.service.files().list(
                q=query,
                fields='files(id,name,mimeType,createdTime,size)'
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"{len(files)}個のファイルが見つかりました")
            return files
            
        except Exception as e:
            logger.error(f"ファイル一覧の取得に失敗しました: {e}")
            raise
    
    async def delete_file(self, file_id: str):
        """ファイルを削除"""
        try:
            logger.info(f"ファイルを削除します: {file_id}")
            
            self.service.files().delete(fileId=file_id).execute()
            
            logger.info("ファイルが削除されました")
            
        except Exception as e:
            logger.error(f"ファイルの削除に失敗しました: {e}")
            raise
    
    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """ファイル情報を取得"""
        try:
            logger.info(f"ファイル情報を取得します: {file_id}")
            
            file_info = self.service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,createdTime,size,webViewLink'
            ).execute()
            
            logger.info("ファイル情報を取得しました")
            return file_info
            
        except Exception as e:
            logger.error(f"ファイル情報の取得に失敗しました: {e}")
            raise
