"""
Google Driveアップロードモジュール

音声ファイルや動画ファイルをGoogle Driveにアップロードし、
共有URLを取得する
"""
from pathlib import Path
from typing import Optional, Dict, Any
import logging

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2 import service_account
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    logging.warning("Google Drive API not available")

logger = logging.getLogger(__name__)


class GoogleDriveUploader:
    """Google Driveアップロードクラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.service = None
        self.target_folder_id = None
        
        # Google Drive APIを初期化
        self._initialize_drive_api()
        
        # アップロード先フォルダIDを設定
        self._set_target_folder()
    
    def _initialize_drive_api(self):
        """Google Drive APIを初期化"""
        if not GOOGLE_DRIVE_AVAILABLE:
            logger.warning("⚠️ Google Drive APIがインストールされていません")
            logger.info("   インストール: pip install google-api-python-client google-auth")
            return
        
        try:
            credentials_path = self.settings.GOOGLE_CREDENTIALS_PATH
            
            if not Path(credentials_path).exists():
                logger.error(f"❌ 認証ファイルが見つかりません: {credentials_path}")
                return
            
            # 認証情報を読み込み
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=SCOPES
            )
            
            # Drive APIサービスを構築
            self.service = build('drive', 'v3', credentials=credentials)
            
            logger.info("✅ Google Drive API初期化完了")
            
        except Exception as e:
            logger.error(f"❌ Google Drive API初期化エラー: {e}")
            self.service = None
    
    def _set_target_folder(self):
        """アップロード先フォルダを設定"""
        # URLからフォルダIDを抽出
        # https://drive.google.com/drive/u/0/folders/1AvXFr3lBEhP03StfM99qTUNzSbzvPD9w
        # → 1AvXFr3lBEhP03StfM99qTUNzSbzvPD9w
        
        if hasattr(self.settings, 'GOOGLE_DRIVE_FOLDER_ID') and self.settings.GOOGLE_DRIVE_FOLDER_ID:
            self.target_folder_id = self.settings.GOOGLE_DRIVE_FOLDER_ID
            logger.info(f"✅ アップロード先フォルダID: {self.target_folder_id}")
        else:
            logger.warning("⚠️ GOOGLE_DRIVE_FOLDER_IDが設定されていません")
    
    def upload_file(
        self,
        file_path: Path,
        file_name: Optional[str] = None,
        mime_type: str = 'audio/wav',
        make_public: bool = True
    ) -> Optional[Dict[str, str]]:
        """
        ファイルをGoogle Driveにアップロード
        
        Args:
            file_path: アップロードするファイルのパス
            file_name: Google Drive上のファイル名（省略時は元のファイル名）
            mime_type: MIMEタイプ
            make_public: 公開リンクを作成するか
            
        Returns:
            Optional[Dict]: アップロード情報
            {
                'file_id': 'ファイルID',
                'web_view_link': '表示用URL',
                'web_content_link': 'ダウンロード用URL'
            }
        """
        if not self.service:
            logger.error("❌ Google Drive APIが初期化されていません")
            return None
        
        if not file_path.exists():
            logger.error(f"❌ ファイルが見つかりません: {file_path}")
            return None
        
        try:
            logger.info(f"📤 Google Driveにアップロード中: {file_path.name}")
            
            # ファイル名を設定
            if not file_name:
                file_name = file_path.name
            
            # ファイルメタデータ
            file_metadata = {
                'name': file_name
            }
            
            # フォルダを指定する場合
            if self.target_folder_id:
                file_metadata['parents'] = [self.target_folder_id]
            
            # メディアファイルをアップロード
            media = MediaFileUpload(
                str(file_path),
                mimetype=mime_type,
                resumable=True
            )
            
            # アップロード実行
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink'
            ).execute()
            
            file_id = file.get('id')
            web_view_link = file.get('webViewLink')
            web_content_link = file.get('webContentLink')
            
            logger.info(f"✅ アップロード完了: {file_name}")
            logger.info(f"   ファイルID: {file_id}")
            
            # 公開リンクを作成
            if make_public:
                self._make_file_public(file_id)
                # 公開URLを生成
                web_view_link = f"https://drive.google.com/file/d/{file_id}/view"
                web_content_link = f"https://drive.google.com/uc?export=download&id={file_id}"
                logger.info(f"   公開URL: {web_view_link}")
            
            return {
                'file_id': file_id,
                'web_view_link': web_view_link,
                'web_content_link': web_content_link
            }
            
        except Exception as e:
            logger.error(f"❌ アップロードエラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _make_file_public(self, file_id: str) -> bool:
        """ファイルを公開設定にする"""
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            logger.info(f"✅ ファイルを公開しました: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ファイル公開エラー: {e}")
            return False
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        フォルダを作成
        
        Args:
            folder_name: フォルダ名
            parent_folder_id: 親フォルダID（省略時はルート）
            
        Returns:
            Optional[str]: 作成されたフォルダID
        """
        if not self.service:
            logger.error("❌ Google Drive APIが初期化されていません")
            return None
        
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id,name'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"✅ フォルダ作成完了: {folder_name} (ID: {folder_id})")
            
            return folder_id
            
        except Exception as e:
            logger.error(f"❌ フォルダ作成エラー: {e}")
            return None
    
    def get_folder_info(self, folder_id: str) -> Optional[Dict[str, Any]]:
        """フォルダ情報を取得"""
        if not self.service:
            return None
        
        try:
            folder = self.service.files().get(
                fileId=folder_id,
                fields='id,name,webViewLink'
            ).execute()
            
            return {
                'folder_id': folder.get('id'),
                'folder_name': folder.get('name'),
                'web_view_link': folder.get('webViewLink')
            }
            
        except Exception as e:
            logger.error(f"❌ フォルダ情報取得エラー: {e}")
            return None
    
    def list_files_in_folder(self, folder_id: str) -> list:
        """フォルダ内のファイル一覧を取得"""
        if not self.service:
            return []
        
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields='files(id,name,mimeType,createdTime,size)'
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            logger.error(f"❌ ファイル一覧取得エラー: {e}")
            return []


# ============================================================================
# 使用例
# ============================================================================

if __name__ == "__main__":
    from config.settings import Settings
    
    # 設定を読み込み
    settings = Settings()
    
    # GoogleDriveUploaderを初期化
    uploader = GoogleDriveUploader(settings)
    
    # テスト用ファイルをアップロード
    test_file = Path("temp/test.txt")
    
    if test_file.exists():
        result = uploader.upload_file(test_file)
        
        if result:
            print(f"\n✅ アップロード成功")
            print(f"   ファイルID: {result['file_id']}")
            print(f"   表示URL: {result['web_view_link']}")
            print(f"   ダウンロードURL: {result['web_content_link']}")
    else:
        print(f"⚠️ テストファイルが見つかりません: {test_file}")

