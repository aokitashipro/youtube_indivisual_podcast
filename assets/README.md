# アセットディレクトリ

このディレクトリには動画生成で使用する静的ファイルを配置します。

## ディレクトリ構成

```
assets/
├── background.png          # 背景画像（1920x1080推奨）
├── fonts/                 # フォントファイル
│   └── NotoSansJP-Regular.ttf
└── credentials/           # 認証情報
    └── google-credentials.json
```

## ファイル説明

### background.png
- 動画の背景として使用される画像
- 推奨サイズ: 1920x1080
- 形式: PNG, JPG
- 高解像度の画像を使用してください

### fonts/
- 動画内のテキスト表示に使用されるフォント
- 日本語対応フォントを推奨
- 商用利用可能なフォントを使用してください

### credentials/
- Google API認証情報
- セキュリティのため、このディレクトリは.gitignoreに含まれています
- google-credentials.jsonファイルを配置してください

## 設定方法

1. 背景画像を`assets/background.png`に配置
2. フォントファイルを`assets/fonts/`に配置
3. Google認証情報を`assets/credentials/google-credentials.json`に配置
4. `config/settings.py`でパスを確認・調整

## 注意事項

- ファイルサイズを適切に管理してください
- 著作権に注意してください
- 認証情報は適切に管理してください
