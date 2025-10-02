# クイックスタート - ステップ3-4のテスト

このガイドは、**情報収集→台本生成**（ステップ3-4）のみを実行してテストする手順です。

---

## 🎯 目標

- ✅ Claude APIで海外ニュースを収集
- ✅ 収集したトピックから対談形式の台本を生成
- ✅ 結果をファイルに保存して確認

**所要時間**: 5-10分（API処理時間含む）

---

## 📋 必要なもの

### 必須
- [x] Python 3.11+
- [x] Claude API Key（Anthropic）
  - まだの場合: https://console.anthropic.com/ で取得

### 不要（今回は使いません）
- [ ] Google Sheets
- [ ] Google Cloud TTS
- [ ] ElevenLabs
- [ ] Slack
- [ ] 背景画像・フォント

---

## 🚀 実行手順

### ステップ1: 依存関係のインストール

```bash
cd /Users/a-aoki/indivisual/youtube-ai

# 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 必要最小限の依存関係をインストール
pip install anthropic python-dotenv pyyaml pydantic
```

**または、全ての依存関係をインストール:**
```bash
pip install -r requirements.txt
```

---

### ステップ2: 環境変数の設定

```bash
# .envファイルを作成
cp .env.template .env

# エディタで.envを開いて、Claude API Keyを設定
vim .env
# または
code .env
```

**.envファイルの内容:**
```bash
# Claude API設定（必須）
ANTHROPIC_API_KEY=sk-ant-api03-あなたのAPIキーをここに入力

# アプリケーション設定
DEBUG=True
LOG_LEVEL=INFO
TEMP_DIR=temp/
OUTPUT_DIR=output/
```

**⚠️ 重要:**
- `ANTHROPIC_API_KEY` は必ず設定してください
- その他の設定はコメントアウトのままでOK

---

### ステップ3: ディレクトリの準備

```bash
# 必要なディレクトリを作成
mkdir -p temp output logs

# 確認
ls -la temp/ output/ logs/
```

---

### ステップ4: テスト実行

```bash
# テストスクリプトを実行
python test_step_3_4.py
```

**期待される出力:**
```
🎬 YouTube AI Podcast - ステップ3-4テスト

このテストでは以下を実行します:
  1. Claude APIで情報収集（Indie Hackers, Product Hunt, Hacker News）
  2. 収集したトピックから対談形式の台本を生成
  3. 結果をtemp/フォルダに保存

必要な環境変数:
  - ANTHROPIC_API_KEY (必須)

================================================================================

2024-10-02 15:00:00 - youtube_ai_podcast - INFO - 🧪 ステップ3-4のテストを開始します
2024-10-02 15:00:00 - youtube_ai_podcast - INFO - ✅ 設定を読み込みました
2024-10-02 15:00:00 - youtube_ai_podcast - INFO - ✅ Claude Clientを初期化しました
...
```

---

### ステップ5: 結果の確認

テストが成功すると、以下のファイルが生成されます：

```bash
# 生成されたファイルを確認
ls -lh temp/

# 出力例:
# topics_20241002_150000.json    # 収集したトピック（JSON）
# script_20241002_150200.json    # 生成された台本（JSON）
# script_20241002_150200.txt     # 生成された台本（テキスト）
```

**台本の内容を確認:**
```bash
# テキストファイルで確認（読みやすい）
cat temp/script_*.txt

# または
less temp/script_*.txt

# JSONファイルで確認
cat temp/script_*.json | python -m json.tool
```

---

## ✅ 成功の確認ポイント

### 1. トピック収集の成功
```bash
cat temp/topics_*.json
```

**確認事項:**
- [ ] 3-5件のトピックが含まれている
- [ ] 各トピックにタイトル、概要、URLが含まれている
- [ ] 最新の情報が取得されている

### 2. 台本生成の成功
```bash
cat temp/script_*.txt
```

**確認事項:**
- [ ] 4500-6000文字程度の台本
- [ ] [Aさん] [Bさん] の会話形式
- [ ] オープニング、トピック1-3、クロージングの構成
- [ ] 自然な掛け合い
- [ ] 15-20分相当の内容

### 3. ログの確認
```bash
cat logs/test_*.log
```

**確認事項:**
- [ ] エラーがない
- [ ] 各ステップの処理時間が記録されている
- [ ] ✅ マークで成功が示されている

---

## 🆘 トラブルシューティング

### エラー: ModuleNotFoundError

```bash
# 依存関係を再インストール
pip install anthropic python-dotenv pyyaml pydantic
```

### エラー: ANTHROPIC_API_KEY が設定されていません

```bash
# .envファイルを確認
cat .env

# ANTHROPIC_API_KEY が設定されているか確認
grep ANTHROPIC_API_KEY .env

# 設定されていない場合
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-key-here" >> .env
```

### エラー: No module named 'config.settings'

```bash
# 現在のディレクトリを確認
pwd
# /Users/a-aoki/indivisual/youtube-ai にいることを確認

# Pythonパスを確認
python -c "import sys; print('\n'.join(sys.path))"
```

### エラー: Claude API呼び出しエラー

```bash
# API Keyの形式を確認
# 正しい形式: sk-ant-api03-...

# API Keyをテスト
python -c "
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
response = client.messages.create(
    model='claude-sonnet-4-5-20250929',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print('✅ API Key は有効です')
print(response.content[0].text)
"
```

### 情報収集に時間がかかる

これは正常です。Claude APIがWeb検索を行っているため、2-5分程度かかることがあります。

```bash
# 進捗を確認（別ターミナルで）
tail -f logs/test_*.log
```

---

## 📊 期待される処理時間

- **ステップ3（情報収集）**: 2-5分
  - Web検索を含むため時間がかかります
  
- **ステップ4（台本生成）**: 1-3分
  - トピックから台本を生成

**合計: 3-8分程度**

---

## 💾 生成ファイルの例

### topics_*.json
```json
{
  "topics": [
    {
      "title_ja": "月間$5000を達成したSaaSツールの構築方法",
      "title_en": "How I Built a SaaS That Makes $5k/Month",
      "summary": "個人開発者が6ヶ月でMRR $5000を達成...",
      "url": "https://www.indiehackers.com/...",
      "category": "個人開発",
      "interesting_points": "小さく始めて段階的にスケール...",
      "source": "Indie Hackers"
    }
  ],
  "collected_at": "2024-10-02 15:00:00",
  "total_count": 3
}
```

### script_*.txt
```
タイトル: 個人開発者の成功事例とAI最新動向
文字数: 4850
推定時間: 16.2分
================================================================================

[Aさん] こんにちは！今日は個人開発者の成功事例とAI関連の最新トピックについてお話しします！

[Bさん] はい、今日は興味深いトピックが集まりましたね。

[Aさん] そうなんです！まず1つ目のトピックは...
```

---

## 🎯 次のステップ

### テストが成功したら

1. **台本の内容を確認**
   ```bash
   cat temp/script_*.txt
   ```
   
2. **Git管理を開始**（推奨）
   ```bash
   # .cursor/commands/01-初期設定.md を参照
   git init
   git add .
   git commit -m "feat: ステップ3-4実装完了（情報収集・台本生成）"
   ```

3. **次のステップに進む**
   - ステップ5: 音声生成
   - ステップ6: 字幕生成
   - ステップ7: 動画生成

---

## 📝 このテストで確認できること

✅ Claude APIとの連携  
✅ Web検索機能の動作  
✅ トピック収集の精度  
✅ 台本生成の品質  
✅ 対談形式の自然さ  
✅ エラーハンドリングの動作  
✅ ログ出力の適切さ  

---

## 💡 Tips

### より詳細なログを見たい場合

```bash
# ログレベルをDEBUGに変更
# .envファイルで:
LOG_LEVEL=DEBUG

# 再実行
python test_step_3_4.py
```

### 生成された台本を編集したい場合

```bash
# テキストファイルを編集
vim temp/script_*.txt

# 次のステップ（音声生成）で、このファイルを使用することも可能
```

### 複数回テストしたい場合

```bash
# 何度でも実行可能（新しいファイルが生成されます）
python test_step_3_4.py
python test_step_3_4.py
python test_step_3_4.py

# 古いファイルを削除
rm temp/topics_*.json temp/script_*
```

---

## ❓ よくある質問

### Q: Claude API Keyはどこで取得できますか？

A: https://console.anthropic.com/ にアクセスして、アカウント作成後にAPI Keyを発行できます。

### Q: API利用料金はかかりますか？

A: はい。Claude APIは従量課金制です。このテスト1回で約$0.10-0.30程度です。

### Q: web_search機能は無料ですか？

A: web_search機能は追加料金なしで使用できます（2024年10月時点）。

### Q: Google Sheetsは必須ですか？

A: いいえ。ステップ3-4のテストでは不要です。後のステップで使用します。

### Q: 生成された台本の品質が低い場合は？

A: `config/prompts.yaml` を編集するか、`claude_client.py` のプロンプトを調整してください。

---

**準備ができたら、`python test_step_3_4.py` を実行してください！** 🚀

