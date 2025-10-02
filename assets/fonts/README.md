# フォントディレクトリ

このディレクトリには動画生成で使用するフォントファイルを配置します。

## 推奨フォント

- NotoSansJP-Regular.ttf (日本語対応)
- Arial (英語用)
- Roboto (Google Fonts)

## 使用方法

フォントファイルをこのディレクトリに配置し、`config/settings.py`でパスを設定してください。

```python
FONT_PATH = "assets/fonts/NotoSansJP-Regular.ttf"
```

## 注意事項

- フォントファイルのライセンスを確認してください
- 商用利用可能なフォントを使用してください
- ファイルサイズが大きすぎないように注意してください
