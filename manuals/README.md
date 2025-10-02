# YouTube AI Podcast ドキュメント

このディレクトリには、YouTube AI Podcastプロジェクトの詳細なドキュメントが含まれています。

---

## 📚 ドキュメント一覧

### 1. [ARCHITECTURE.md](./ARCHITECTURE.md)
**プロジェクトアーキテクチャの全体像**

- プロジェクト構造概要
- データフロー図
- モジュール間依存関係
- 外部API・サービス依存
- 設定ファイルの説明
- 静的ファイル管理
- 認証情報の管理方法
- 重要な注意事項

**こんな時に読む:**
- プロジェクト全体の構造を理解したい
- モジュール間の関係を知りたい
- どの外部APIが必要か確認したい
- 設定ファイルの役割を理解したい

---

### 2. [STEPS_REFERENCE.md](./STEPS_REFERENCE.md)
**各ステップの実装リファレンス**

- 12ステップの詳細説明
- 各ステップで参照すべきファイル
- 実装が必要なメソッド
- サンプルコード
- 実装状況の確認

**こんな時に読む:**
- 特定のステップを実装する前に
- どのファイルを編集すべきか確認したい
- 実装済み/未実装の機能を把握したい
- 具体的なコード例が欲しい

---

### 3. [MODULE_DEPENDENCIES.md](./MODULE_DEPENDENCIES.md)
**モジュール依存関係マップ**

- 依存関係グラフ
- 各モジュールの詳細依存関係
- 外部ライブラリ一覧
- ステップごとの依存関係フロー
- セットアップチェックリスト

**こんな時に読む:**
- 特定のモジュールが何に依存しているか知りたい
- どの外部ライブラリが必要か確認したい
- ステップ実行時にどのファイルが使われるか確認したい
- セットアップ時に何が必要か確認したい

---

## 🚀 クイックスタート

### 初めての方へ

1. **プロジェクト全体を理解する**
   - まず [ARCHITECTURE.md](./ARCHITECTURE.md) を読む
   - プロジェクト構造とデータフローを把握

2. **実装を始める**
   - [STEPS_REFERENCE.md](./STEPS_REFERENCE.md) で実装すべきステップを確認
   - 各ステップの実装リファレンスに従って開発

3. **依存関係を確認する**
   - [MODULE_DEPENDENCIES.md](./MODULE_DEPENDENCIES.md) で必要なファイル・ライブラリを確認
   - セットアップチェックリストで環境を整える

---

## 📖 ドキュメントの使い方

### シナリオ別ガイド

#### 🔧 「ステップ4（台本生成）を実装したい」

1. **STEPS_REFERENCE.md** を開く
2. 「ステップ4: Claude APIで台本生成」セクションを読む
3. 必要なファイルを確認:
   - `modules/claude_client.py`
   - `config/prompts.yaml`
4. **MODULE_DEPENDENCIES.md** で詳細を確認:
   - `modules/claude_client.py` のセクション
   - 必要な外部ライブラリ（anthropic）
5. サンプルコードを参考に実装

#### 🐛 「音声生成がエラーになる」

1. **MODULE_DEPENDENCIES.md** を開く
2. `modules/audio_generator.py` のセクションを確認
3. 依存関係をチェック:
   - `config/settings.py` の設定値
   - `assets/credentials/google-credentials.json` の存在
   - 外部ライブラリのインストール状況
4. **ARCHITECTURE.md** で認証情報の管理方法を確認

#### 📦 「新しい環境でセットアップしたい」

1. **MODULE_DEPENDENCIES.md** の最後のチェックリストを使用
2. 設定ファイル、認証情報、静的ファイル、外部ライブラリを順に確認
3. **ARCHITECTURE.md** で各設定の詳細を確認

#### 🔍 「特定のモジュールが何に依存しているか知りたい」

1. **MODULE_DEPENDENCIES.md** を開く
2. 該当モジュールのセクションを確認
3. 依存関係グラフで全体像を把握

---

## 🗂️ その他のドキュメント

### プロジェクトルートのドキュメント

#### [../README.md](../README.md)
- プロジェクト概要
- 基本的な使用方法
- セットアップ手順

#### [../IMPLEMENTATION_GUIDE.md](../IMPLEMENTATION_GUIDE.md)
- 全ステップの実装ガイド
- 詳細なコード例
- ステップ4-12の実装方法

#### [../.cursor/rules/要件定義.mdc](../.cursor/rules/要件定義.mdc)
- 詳細な要件定義
- システム要件
- 機能要件

---

## 📊 ドキュメント間の関係

```
README.md (このファイル)
  │
  ├─→ 新規参入者向け
  │     └─→ ARCHITECTURE.md (全体像)
  │           └─→ STEPS_REFERENCE.md (実装)
  │                 └─→ MODULE_DEPENDENCIES.md (詳細)
  │
  ├─→ 実装者向け
  │     └─→ STEPS_REFERENCE.md (実装リファレンス)
  │           └─→ MODULE_DEPENDENCIES.md (依存関係)
  │                 └─→ ARCHITECTURE.md (全体構造)
  │
  └─→ トラブルシューティング
        └─→ MODULE_DEPENDENCIES.md (依存関係チェック)
              └─→ ARCHITECTURE.md (設定・認証)
                    └─→ STEPS_REFERENCE.md (該当ステップ)
```

---

## 🎯 学習パス

### レベル1: 初心者
```
1. README.md（このファイル）
2. ARCHITECTURE.md（全体像）
3. プロジェクトルートのREADME.md
```
**目標:** プロジェクトの全体像を理解する

### レベル2: 実装開始
```
1. STEPS_REFERENCE.md（実装リファレンス）
2. MODULE_DEPENDENCIES.md（依存関係）
3. IMPLEMENTATION_GUIDE.md（詳細実装）
```
**目標:** 実装済みステップを理解し、新しいステップを実装する

### レベル3: 上級者
```
1. MODULE_DEPENDENCIES.md（詳細な依存関係）
2. ARCHITECTURE.md（アーキテクチャの深掘り）
3. ソースコード直接確認
```
**目標:** システム全体を深く理解し、カスタマイズや最適化を行う

---

## 🔄 ドキュメントの更新

### ドキュメントを更新すべきタイミング

- ✅ 新しいモジュールを追加した
- ✅ 依存関係が変更された
- ✅ 新しい外部APIを使用する
- ✅ 設定ファイルの構造が変わった
- ✅ 重要な実装パターンを変更した

### 更新すべきドキュメント

| 変更内容 | 更新ドキュメント |
|---------|----------------|
| 新モジュール追加 | ARCHITECTURE.md, MODULE_DEPENDENCIES.md |
| ステップ実装完了 | STEPS_REFERENCE.md |
| 依存関係変更 | MODULE_DEPENDENCIES.md |
| 設定変更 | ARCHITECTURE.md |
| 実装パターン変更 | STEPS_REFERENCE.md, IMPLEMENTATION_GUIDE.md |

---

## 💡 Tips

### 効率的なドキュメントの読み方

1. **目的を明確にする**
   - 「全体を理解したい」→ ARCHITECTURE.md
   - 「特定機能を実装したい」→ STEPS_REFERENCE.md
   - 「依存関係を確認したい」→ MODULE_DEPENDENCIES.md

2. **必要な部分だけ読む**
   - 目次を活用してジャンプ
   - 検索機能を使う（Ctrl+F / Cmd+F）

3. **複数のドキュメントを組み合わせる**
   - 概要はARCHITECTURE.md
   - 詳細はMODULE_DEPENDENCIES.md
   - 実装はSTEPS_REFERENCE.md

---

## 📞 困った時は

### よくある問題と参照先

| 問題 | 参照先 |
|-----|-------|
| セットアップ方法がわからない | MODULE_DEPENDENCIES.md（チェックリスト） |
| モジュールが見つからない | ARCHITECTURE.md（プロジェクト構造） |
| APIキーの設定方法がわからない | ARCHITECTURE.md（認証情報の管理） |
| 特定ステップの実装方法がわからない | STEPS_REFERENCE.md（該当ステップ） |
| 依存関係エラーが出る | MODULE_DEPENDENCIES.md（依存関係グラフ） |
| 全体の流れがわからない | ARCHITECTURE.md（データフロー図） |

---

## 📝 ドキュメント作成日

- 作成日: 2024-01-01
- 最終更新: 2024-01-01
- バージョン: 1.0.0

---

## 🤝 コントリビューション

ドキュメントの改善提案や誤りの報告は歓迎します。

### ドキュメントの改善方法

1. 誤りや不明瞭な点を見つけた
2. 該当ドキュメントを編集
3. 変更内容を明確に記述
4. プルリクエストを作成

---

## 📚 関連リンク

### 外部ドキュメント

- [Anthropic Claude API](https://docs.anthropic.com/)
- [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech/docs)
- [ElevenLabs API](https://elevenlabs.io/docs)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Google Drive API](https://developers.google.com/drive/api)
- [Slack API](https://api.slack.com/)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)

### 参考記事

- [元記事（Zenn）](https://zenn.dev/xtm_blog/articles/da1eba90525f91)

