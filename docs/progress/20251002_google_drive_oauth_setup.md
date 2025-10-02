# 作業ログ：Google Drive OAuth 2.0認証設定

**日付**: 2025年10月2日  
**作業内容**: Google Drive APIの認証方式をサービスアカウントからOAuth 2.0に変更

---

## 📋 **作業概要**

### **背景**
- サービスアカウントでは個人のGoogle Driveフォルダにアクセスできない
- エラー: "Service Accounts do not have storage quota"
- 共有ドライブは個人アカウントでは利用不可（Google Workspace必須）

### **解決策**
- OAuth 2.0認証を使用して個人のGoogleアカウントでGoogle Driveにアクセス

---

## ✅ **完了した作業**

### 1. **OAuth 2.0認証モジュールの作成**

作成したファイル：
- `modules/google_drive_oauth.py` - OAuth 2.0認証とGoogle Driveアップロード機能
- `test_google_drive_oauth.py` - OAuth認証のテストスクリプト
- `docs/GOOGLE_DRIVE_OAUTH_SETUP.md` - OAuth設定手順のドキュメント

### 2. **主な機能**

`GoogleDriveOAuthUploader`クラス：
- OAuth 2.0フローによる認証
- 認証トークンの保存・再利用（`assets/credentials/token.pickle`）
- ファイルのアップロード
- 公開リンクの作成
- フォルダ情報の取得
- ファイル一覧の取得

### 3. **認証フロー**

1. 初回実行時にブラウザが自動的に開く
2. Googleアカウントでログイン
3. アクセス許可を承認
4. 認証トークンが自動保存される
5. 2回目以降は保存されたトークンを使用

---

## ⏸️ **未完了の作業（明日対応）**

### **Google Cloud Console側の設定**

#### **完了済み**
1. ✅ サービスアカウントの作成
2. ✅ Google Drive APIの有効化
3. ✅ Text-to-Speech APIの有効化
4. ✅ サービスアカウントのJSONキー作成

#### **残作業**
1. ⏸️ **OAuth同意画面の作成**
   - User Type: 「外部」を選択
   - アプリ名: `YouTube AI Podcast`
   - ユーザーサポートメール: `webmocha2@gmail.com`
   - デベロッパーの連絡先: `webmocha2@gmail.com`

2. ⏸️ **テストユーザーの追加**
   - `webmocha2@gmail.com` をテストユーザーに追加

3. ⏸️ **OAuthクライアントIDの作成**
   - アプリケーションの種類: 「デスクトップアプリ」
   - 名前: `YouTube AI Podcast Desktop`
   - JSONファイルをダウンロード

4. ⏸️ **認証ファイルの配置**
   - ダウンロードした `client_secret_*.json` を以下に配置:
     ```
     /Users/a-aoki/indivisual/youtube-ai/assets/credentials/google-credentials.json
     ```

5. ⏸️ **初回認証テストの実行**
   ```bash
   python test_google_drive_oauth.py
   ```

---

## 🔗 **参考URL**

### **Google Cloud Console**
- プロジェクト: `gen-lang-client-0946363977`
- プロジェクトURL: https://console.cloud.google.com/home/dashboard?project=gen-lang-client-0946363977
- OAuth同意画面: https://console.cloud.google.com/apis/credentials/consent?project=gen-lang-client-0946363977
- 認証情報: https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0946363977

### **Google Drive**
- フォルダID: `1AvXFr3lBEhP03StfM99qTUNzSbzvPD9w`
- フォルダURL: https://drive.google.com/drive/folders/1AvXFr3lBEhP03StfM99qTUNzSbzvPD9w

---

## 📁 **ファイル構成**

### **作成したファイル**
```
youtube-ai/
├── modules/
│   ├── google_drive_uploader.py          # サービスアカウント版（旧）
│   └── google_drive_oauth.py             # OAuth 2.0版（新）★
├── docs/
│   ├── GOOGLE_DRIVE_OAUTH_SETUP.md       # OAuth設定手順★
│   └── progress/
│       └── 20251002_google_drive_oauth_setup.md  # 本ファイル★
├── test_google_services.py                # サービスアカウントテスト（旧）
└── test_google_drive_oauth.py             # OAuth認証テスト（新）★
```

### **認証ファイル（予定）**
```
assets/credentials/
├── google-credentials.json   # OAuth認証情報（要配置）
└── token.pickle              # 認証トークン（自動生成）
```

---

## 🎯 **次回の作業手順（明日）**

### **ステップ1: OAuth同意画面の確認・作成**
1. https://console.cloud.google.com/apis/credentials/consent?project=gen-lang-client-0946363977 を開く
2. 「外部」を選択して「作成」
3. アプリ情報を入力:
   - アプリ名: `YouTube AI Podcast`
   - ユーザーサポートメール: `webmocha2@gmail.com`
   - デベロッパーの連絡先: `webmocha2@gmail.com`
4. 「保存して次へ」
5. スコープ: そのまま「保存して次へ」
6. テストユーザー: `webmocha2@gmail.com` を追加
7. 「保存して次へ」→「ダッシュボードに戻る」

### **ステップ2: OAuthクライアントIDの作成**
1. https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0946363977 を開く
2. 「+ 認証情報を作成」→「OAuthクライアントID」
3. アプリケーションの種類: **「デスクトップアプリ」**
4. 名前: `YouTube AI Podcast Desktop`
5. 「作成」
6. 「JSONをダウンロード」

### **ステップ3: 認証ファイルの配置**
```bash
# ダウンロードフォルダから認証ファイルを配置
cp ~/Downloads/client_secret_*.json /Users/a-aoki/indivisual/youtube-ai/assets/credentials/google-credentials.json
```

### **ステップ4: 初回認証テスト**
```bash
cd /Users/a-aoki/indivisual/youtube-ai
source venv/bin/activate
python test_google_drive_oauth.py
```

ブラウザが開いて認証画面が表示されたら：
1. Googleアカウントでログイン
2. 「このアプリは確認されていません」→「詳細」→「安全ではないページに移動」
3. アクセス許可を承認
4. 「認証が完了しました」と表示されたらブラウザを閉じる

---

## ⚠️ **注意事項**

### **「このアプリは確認されていません」警告について**
- これは正常な動作です
- 個人開発のアプリなので、Googleの審査は不要
- 「詳細」→「安全ではないページに移動」で進めてOK

### **認証トークンの管理**
- 初回認証後、`assets/credentials/token.pickle` に保存される
- このファイルがある限り、再認証は不要
- トークンが期限切れの場合は自動的に更新される

### **セキュリティ**
- `google-credentials.json` と `token.pickle` は機密情報
- `.gitignore` に追加済み
- Gitにコミットしないこと

---

## 📊 **現在のステータス**

| 項目 | ステータス |
|------|----------|
| サービスアカウント認証 | ✅ 完了（個人Driveには使用不可） |
| OAuth 2.0モジュール実装 | ✅ 完了 |
| OAuth同意画面設定 | ⏸️ 保留（Google側の処理待ち） |
| OAuthクライアントID作成 | ⏸️ 保留 |
| 認証ファイル配置 | ⏸️ 保留 |
| 初回認証テスト | ⏸️ 保留 |
| Google Driveアップロードテスト | ⏸️ 保留 |

---

## 🔍 **発生したエラーと解決策**

### **エラー1: Service Accounts do not have storage quota**
**原因**: サービスアカウントには個人のGoogle Driveストレージ容量がない

**解決策**: OAuth 2.0認証に切り替え

### **エラー2: アクセスをブロック - Google の審査プロセスを完了していません**
**原因**: OAuth同意画面が未作成、またはテストユーザーが未追加

**解決策**: 
- OAuth同意画面を作成
- テストユーザーに自分のメールアドレスを追加
- 公開ステータスを「テスト中」に設定

---

## 📚 **参考資料**

### **Google公式ドキュメント**
- [Google Drive API - Python Quickstart](https://developers.google.com/drive/api/quickstart/python)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Google Drive API Scopes](https://developers.google.com/drive/api/guides/api-specific-auth)

### **プロジェクト内ドキュメント**
- `docs/GOOGLE_DRIVE_OAUTH_SETUP.md` - OAuth設定手順の詳細
- `modules/google_drive_oauth.py` - OAuth認証実装
- `test_google_drive_oauth.py` - テストスクリプト

---

## 💡 **今後の展開**

OAuth認証が完了したら：

1. ✅ **音声生成のテスト**
   ```bash
   python test_audio_generation.py
   ```

2. ✅ **Google Driveへの音声アップロード**
   - 音声生成 → Google Driveアップロード → URL取得

3. ✅ **Google Sheetsとの統合**
   - 動的プロンプト生成
   - 実行ログ記録
   - 音声URL保存

4. ✅ **フルパイプラインの実行**
   ```bash
   python run_pipeline_with_sheets.py
   ```

5. ✅ **動画生成機能の実装**
   - 字幕生成
   - 動画生成
   - YouTubeアップロード

---

## 📝 **メモ**

- Google側の処理に時間がかかる場合がある（通常は即座）
- OAuth同意画面の作成は初回のみ必要
- 一度認証すれば、トークンが有効な限り再認証不要
- トークンの有効期限は通常7日間（自動更新可能）

---

**次回作業日**: 2025年10月3日  
**次回タスク**: OAuth同意画面の作成とOAuthクライアントIDの設定

---

**作成者**: AI Assistant  
**作成日時**: 2025年10月2日 21:45

