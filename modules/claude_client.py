"""
Claude API呼び出しモジュール
"""
import anthropic
import yaml
import json
import asyncio
from typing import Dict, Any, List
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Claude APIクライアントクラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = anthropic.Anthropic(
            api_key=self.settings.ANTHROPIC_API_KEY
        )
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """プロンプトテンプレートを読み込み"""
        try:
            prompts_path = Path("config/prompts.yaml")
            with open(prompts_path, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
            logger.info("プロンプトテンプレートを読み込みました")
            return prompts
        except Exception as e:
            logger.error(f"プロンプトテンプレートの読み込みに失敗しました: {e}")
            return {}
    
    def _get_mock_topics(self) -> Dict[str, Any]:
        """モックデータを返す（実際のAPI統合までの暫定対応）"""
        return {
            "topics": [
                {
                    "title_ja": "AI駆動の個人開発ツールが月収10万ドルを達成",
                    "title_en": "AI-Powered Solo Dev Tool Hits $100K MRR",
                    "summary": "1人の開発者が作ったAIコード補完ツールが、わずか8ヶ月で月間収益10万ドルを達成。ニッチな市場を見つけ、コミュニティとの対話を重視した成長戦略が功を奏した。初期投資はほぼゼロで、マーケティングもSNSとコミュニティ活動のみ。",
                    "url": "https://www.indiehackers.com/post/ai-tool-100k-mrr-example",
                    "category": "個人開発/AI",
                    "interesting_points": "このツールの成功要因は3つ。第一に、大手企業が見落としていた特定の開発者層（フリーランスのフロントエンド開発者）にフォーカスしたこと。第二に、無料プランを充実させてコミュニティを先に作り、その後有料化したこと。第三に、ユーザーフィードバックを48時間以内に実装する超高速開発サイクル。価格設定も月額49ドルと絶妙で、個人でも手が出せる範囲。競合のCopilotが月額10ドルなのに対し、より専門特化した機能で価格差を正当化している。",
                    "source": "Indie Hackers",
                    "posted_at": "2025-10-01"
                },
                {
                    "title_ja": "ノーコードで構築されたSaaSが1年でエグジット",
                    "title_en": "No-Code SaaS Exits After 1 Year",
                    "summary": "Bubble.ioとAirtableだけで構築されたプロジェクト管理ツールが、立ち上げから1年で大手企業に買収された。開発コストは月額200ドル以下、創業者はコードを一行も書いていない。",
                    "url": "https://www.producthunt.com/posts/no-code-saas-exit",
                    "category": "MicroSaaS/ノーコード",
                    "interesting_points": "この事例が示すのは「技術力がすべてではない」という事実。創業者は元マーケターで、コーディング経験ゼロ。しかし、実際のユーザーの痛みを深く理解しており、既存ツールの組み合わせだけで解決策を提供できた。特筆すべきは、MVPを2週間で作り、3ヶ月で最初の有料顧客を獲得したスピード感。Bubble.ioのテンプレートをベースに、必要最小限の機能だけを実装。「完璧を待つな、出荷せよ」を体現した成功例。買収額は非公開だが、年間収益の5-7倍程度と推測されている。",
                    "source": "Product Hunt",
                    "posted_at": "2025-09-30"
                },
                {
                    "title_ja": "オープンソースのAI音声クローンツールが爆発的人気",
                    "title_en": "Open Source AI Voice Cloning Tool Goes Viral",
                    "summary": "GitHub上で公開された音声クローニングツールが、公開3日で1万スター獲得。商用利用も可能なMITライセンスで、数秒の音声サンプルから高品質な音声合成が可能。個人開発者による週末プロジェクトとして始まった。",
                    "url": "https://news.ycombinator.com/item?id=12345678",
                    "category": "AI/オープンソース",
                    "interesting_points": "このツールが注目される理由は、技術的な革新性だけでなく、倫理面への配慮。音声の透かし（watermark）機能を標準搭載し、生成された音声がAIによるものだと識別できるようにしている。また、悪用防止のため、使用には同意確認が必須。開発者はボイスアクター出身で、「技術の民主化と倫理のバランス」を重視。ElevenLabsなどの商用サービスが月額数十ドルするのに対し、ローカルで動作するため完全無料。ただし、GPUが必要で、M1 Mac以上を推奨。すでに数十のフォークが生まれ、エコシステムが形成されつつある。",
                    "source": "Hacker News",
                    "posted_at": "2025-10-02"
                }
            ],
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_count": 3
        }
    
    async def generate_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """メインコンテンツを生成"""
        try:
            # プロンプトテンプレートを取得
            prompt_template = self.prompts.get("main_content_prompt", "")
            
            # データをプロンプトに埋め込み
            prompt = prompt_template.format(data=data)
            
            # Claude APIを呼び出し
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            
            logger.info("Claude APIでコンテンツを生成しました")
            
            # 生成されたコンテンツを解析して構造化
            structured_content = self._parse_content(content)
            
            return structured_content
            
        except Exception as e:
            logger.error(f"コンテンツ生成に失敗しました: {e}")
            raise
    
    def _parse_content(self, content: str) -> Dict[str, Any]:
        """生成されたコンテンツを解析して構造化"""
        try:
            lines = content.split('\n')
            structured = {
                "title": "",
                "summary": "",
                "main_content": "",
                "key_points": [],
                "conclusion": ""
            }
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # セクションの識別
                if "タイトル" in line or "Title" in line:
                    current_section = "title"
                elif "概要" in line or "Summary" in line:
                    current_section = "summary"
                elif "メインコンテンツ" in line or "Main Content" in line:
                    current_section = "main_content"
                elif "キーポイント" in line or "Key Points" in line:
                    current_section = "key_points"
                elif "結論" in line or "Conclusion" in line:
                    current_section = "conclusion"
                else:
                    # コンテンツを適切なセクションに追加
                    if current_section == "title":
                        structured["title"] = line
                    elif current_section == "summary":
                        structured["summary"] += line + "\n"
                    elif current_section == "main_content":
                        structured["main_content"] += line + "\n"
                    elif current_section == "key_points":
                        if line.startswith("-") or line.startswith("•"):
                            structured["key_points"].append(line[1:].strip())
                    elif current_section == "conclusion":
                        structured["conclusion"] += line + "\n"
            
            # 空の文字列をクリーンアップ
            for key in ["summary", "main_content", "conclusion"]:
                structured[key] = structured[key].strip()
            
            logger.info("コンテンツの解析が完了しました")
            return structured
            
        except Exception as e:
            logger.error(f"コンテンツの解析に失敗しました: {e}")
            return {"raw_content": content}
    
    async def generate_metadata(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """メタデータを生成"""
        try:
            prompt_template = self.prompts.get("metadata_prompt", "")
            prompt = prompt_template.format(content=content)
            
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.5,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            metadata_content = response.content[0].text
            metadata = self._parse_metadata(metadata_content)
            
            logger.info("メタデータを生成しました")
            return metadata
            
        except Exception as e:
            logger.error(f"メタデータ生成に失敗しました: {e}")
            raise
    
    async def generate_youtube_metadata(
        self,
        script_content: Dict[str, Any],
        topics_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        YouTube用のメタデータを生成
        
        Args:
            script_content: 台本データ
            topics_data: トピック情報（オプション）
            
        Returns:
            メタデータ
            {
                "title": str,
                "description": str,
                "tags": List[str],
                "thumbnail_text": str
            }
        """
        try:
            logger.info("📋 YouTube用メタデータを生成中...")
            
            prompt_template = self.prompts.get("youtube_metadata_prompt", "")
            
            # 台本テキストを取得
            script_text = script_content.get("full_script", "")
            if not script_text:
                script_text = str(script_content)
            
            # トピック情報を整形
            topics_text = json.dumps(topics_data, ensure_ascii=False, indent=2) if topics_data else "トピック情報なし"
            
            prompt = prompt_template.format(
                script_content=script_text[:2000],  # 長すぎる場合は省略
                topics_data=topics_text[:1000]
            )
            
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",  # Sonnet 3.5使用（コスト削減）
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            metadata_text = response.content[0].text
            
            # JSON形式で返ってくることを期待
            try:
                # JSONブロックを抽出
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', metadata_text, re.DOTALL)
                if json_match:
                    metadata = json.loads(json_match.group(1))
                else:
                    # JSON形式でない場合はパース
                    metadata = self._parse_metadata_text(metadata_text)
            except Exception as e:
                logger.warning(f"⚠️ JSONパースエラー: {e}, テキストパースを試行")
                metadata = self._parse_metadata_text(metadata_text)
            
            logger.info(f"✅ メタデータ生成完了:")
            logger.info(f"   - タイトル: {metadata.get('title', 'N/A')[:50]}...")
            logger.info(f"   - タグ数: {len(metadata.get('tags', []))}")
            logger.info(f"   - サムネイルテキスト: {metadata.get('thumbnail_text', 'N/A')}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ YouTube用メタデータ生成エラー: {e}")
            raise
    
    async def generate_comment(self, script_content: Dict[str, Any]) -> str:
        """
        動画用コメントを生成（毒舌の女の子設定）
        
        Args:
            script_content: 台本データ
            
        Returns:
            コメントテキスト
        """
        try:
            logger.info("💬 コメントを生成中（毒舌設定）...")
            
            prompt_template = self.prompts.get("comment_generation_prompt", "")
            
            script_text = script_content.get("full_script", str(script_content))
            prompt = prompt_template.format(script_content=script_text[:1000])
            
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.8,  # 創造性を高める
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            comment = response.content[0].text.strip()
            
            logger.info(f"✅ コメント生成完了: {comment[:50]}...")
            return comment
            
        except Exception as e:
            logger.error(f"❌ コメント生成エラー: {e}")
            return "面白い内容でした！"
    
    def _parse_metadata_text(self, text: str) -> Dict[str, Any]:
        """
        テキスト形式のメタデータをパース
        
        Args:
            text: メタデータテキスト
            
        Returns:
            パースされたメタデータ
        """
        metadata = {
            "title": "",
            "description": "",
            "tags": [],
            "thumbnail_text": ""
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # セクション判定
            if 'タイトル' in line or 'title' in line.lower():
                current_section = 'title'
                # タイトルが同じ行にある場合
                if ':' in line:
                    metadata['title'] = line.split(':', 1)[1].strip().strip('"')
            elif '説明' in line or 'description' in line.lower():
                current_section = 'description'
            elif 'タグ' in line or 'tags' in line.lower():
                current_section = 'tags'
            elif 'サムネイル' in line or 'thumbnail' in line.lower():
                current_section = 'thumbnail'
                if ':' in line:
                    metadata['thumbnail_text'] = line.split(':', 1)[1].strip().strip('"')
            else:
                # データを追加
                if current_section == 'title' and not metadata['title']:
                    metadata['title'] = line.strip('"').strip('-').strip()
                elif current_section == 'description':
                    metadata['description'] += line + '\n'
                elif current_section == 'tags':
                    # カンマ区切り or 箇条書き
                    if ',' in line:
                        tags = [t.strip().strip('"') for t in line.split(',')]
                        metadata['tags'].extend(tags)
                    elif line.startswith('-') or line.startswith('•'):
                        tag = line.lstrip('-•').strip().strip('"')
                        if tag:
                            metadata['tags'].append(tag)
                elif current_section == 'thumbnail' and not metadata['thumbnail_text']:
                    metadata['thumbnail_text'] = line.strip('"').strip('-').strip()
        
        # クリーンアップ
        metadata['description'] = metadata['description'].strip()
        metadata['tags'] = [t for t in metadata['tags'] if t][:15]  # 15個まで
        
        return metadata
    
    def _parse_metadata(self, content: str) -> Dict[str, Any]:
        """メタデータを解析"""
        try:
            lines = content.split('\n')
            metadata = {
                "title": "",
                "description": "",
                "tags": [],
                "category": "",
                "thumbnail_suggestion": ""
            }
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "タイトル" in line or "Title" in line:
                    current_section = "title"
                elif "説明文" in line or "Description" in line:
                    current_section = "description"
                elif "タグ" in line or "Tags" in line:
                    current_section = "tags"
                elif "カテゴリ" in line or "Category" in line:
                    current_section = "category"
                elif "サムネイル" in line or "Thumbnail" in line:
                    current_section = "thumbnail_suggestion"
                else:
                    if current_section == "title":
                        metadata["title"] = line
                    elif current_section == "description":
                        metadata["description"] += line + "\n"
                    elif current_section == "tags":
                        if "," in line:
                            metadata["tags"] = [tag.strip() for tag in line.split(",")]
                        else:
                            metadata["tags"].append(line)
                    elif current_section == "category":
                        metadata["category"] = line
                    elif current_section == "thumbnail_suggestion":
                        metadata["thumbnail_suggestion"] += line + "\n"
            
            # 空の文字列をクリーンアップ
            metadata["description"] = metadata["description"].strip()
            metadata["thumbnail_suggestion"] = metadata["thumbnail_suggestion"].strip()
            
            return metadata
            
        except Exception as e:
            logger.error(f"メタデータの解析に失敗しました: {e}")
            return {"raw_metadata": content}
    
    def collect_topics_with_web_search(self, use_history: bool = True, use_mock_data: bool = True) -> Dict[str, Any]:
        """
        情報収集（外部APIまたはモックデータを使用）
        
        Args:
            use_history: 過去の履歴と照合して重複を除外するか（デフォルト: True）
            use_mock_data: モックデータを使用するか（デフォルト: True、実装中）
        
        情報源:
            - Indie Hackers (https://www.indiehackers.com/)
            - Product Hunt (https://www.producthunt.com/)
            - Hacker News Show HN (https://news.ycombinator.com/show)
        
        Returns:
            Dict[str, Any]: 収集したトピックデータ（重複除外済み）
        """
        try:
            # トピック履歴を初期化
            if use_history:
                from modules.topic_history import TopicHistory
                history = TopicHistory()
                history_count = history.get_history_count()
                logger.info(f"📚 トピック履歴: {history_count}件の過去トピックを確認")
            
            # モックデータを使用（実際のAPI統合までの暫定対応）
            if use_mock_data:
                logger.info("🔍 モックデータで情報収集を開始します（実際のAPI統合は未実装）")
                topics_data = self._get_mock_topics()
                logger.info(f"📥 モックデータ取得完了: {len(topics_data.get('topics', []))}件のトピック")
            else:
                logger.info("🔍 Claude API Extended Tools（Web検索）で最新情報を収集します")
                logger.info("🌐 Indie Hackers, Product Hunt, Hacker Newsから情報を取得中...")
                
                prompt = """
あなたは海外の個人開発・AI関連ニュースを収集する専門家です。

**重要**: 必ず**最新・新着順**のトピックを優先して収集してください。数日前や1週間前の古い情報ではなく、**直近24-48時間以内**に投稿されたものを選んでください。

以下の情報源から、最新の興味深いトピックを**5件**収集してください：

1. **Indie Hackers** (https://www.indiehackers.com/)
   - 個人開発者の成功事例
   - MicroSaaSのトレンド
   - 収益化の実例
   
2. **Product Hunt** (https://www.producthunt.com/)
   - 新規AIツール・プロダクト（特に本日・昨日ローンチ）
   - 注目のスタートアップ
   - 革新的なサービス
   
3. **Hacker News Show HN** (https://news.ycombinator.com/show)
   - 技術的に興味深いプロジェクト
   - オープンソースの新規プロジェクト
   - 個人開発のツール

**収集基準**:
- 投稿日時が新しいもの（24-48時間以内を優先）
- 具体的なプロダクト・サービス・技術がある
- 個人開発者や小規模チームが参考になる
- ビジネスモデルや技術的に興味深い

各トピックについて以下の情報を含めてください：
- タイトル（日本語訳）
- 元のタイトル（英語）
- 概要（200-300文字程度、日本語で詳しく）
- URL（必須: 重複チェックに使用）
- カテゴリ（個人開発/AI/MicroSaaS/技術/オープンソース/その他）
- 興味深いポイント（なぜこれが注目すべきか、300文字程度）
- 投稿日時（可能な限り正確に）

**必ずJSONフォーマットで返してください。**

フォーマット例:
{
  "topics": [
    {
      "title_ja": "日本語タイトル",
      "title_en": "English Title",
      "summary": "概要...",
      "url": "https://...",
      "category": "AI",
      "interesting_points": "注目ポイント...",
      "source": "Product Hunt"
    }
  ],
  "collected_at": "2024-10-02 14:00:00",
  "total_count": 3
}
"""
                
                # Extended Tools: Web検索を有効化（2025年3月5日版）
                response = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4000,
                    temperature=0.7,
                    tools=[
                        {
                            "type": "web_search_20250305",
                            "name": "web_search"
                        }
                    ],
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                # レスポンスを解析（ツール使用の場合とテキストの場合を処理）
                logger.info(f"📊 レスポンスブロック数: {len(response.content)}")
                logger.info(f"📊 最初のブロック型: {type(response.content[0])}")
                
                # 全てのcontentブロックからテキストを抽出
                final_text = ""
                tool_used = False
                
                for i, block in enumerate(response.content):
                    block_type = getattr(block, 'type', 'unknown')
                    logger.info(f"   ブロック{i+1}: {block_type}")
                    
                    if block_type == 'tool_use':
                        tool_used = True
                        tool_name = getattr(block, 'name', 'unknown')
                        logger.info(f"   🔧 ツール使用: {tool_name}")
                    elif block_type == 'text':
                        text_content = getattr(block, 'text', '')
                        final_text += text_content
                        logger.info(f"   📝 テキスト取得: {len(text_content)}文字")
                
                if tool_used:
                    logger.info("✅ Web検索が実行されました")
                
                if not final_text:
                    # テキストがない場合はモックデータを使用
                    logger.warning("⚠️ レスポンスにテキストが含まれていません")
                    logger.info("📝 モックデータを使用します")
                    topics_data = self._get_mock_topics()
                else:
                    logger.info(f"📄 取得したテキスト: {len(final_text)}文字")
                    topics_data = self._parse_topics_response(final_text)
                
                logger.info(f"📥 情報収集完了: {len(topics_data.get('topics', []))}件のトピック")
            
            # 重複チェック（モックデータの場合はスキップ）
            if use_history and not use_mock_data:
                original_count = len(topics_data.get('topics', []))
                filtered_topics = history.filter_duplicates(topics_data.get('topics', []))
                topics_data['topics'] = filtered_topics
                
                # 新しいトピックを履歴に追加
                if filtered_topics:
                    history.add_topics(filtered_topics)
                    logger.info(f"✅ 新規トピック: {len(filtered_topics)}件（{original_count - len(filtered_topics)}件は重複除外）")
                else:
                    logger.warning("⚠️ 全てのトピックが重複していました。再収集を推奨します。")
            else:
                if use_mock_data:
                    logger.info(f"✅ モックデータ使用: {len(topics_data.get('topics', []))}件のトピック")
                else:
                    logger.info(f"✅ 情報収集完了: {len(topics_data.get('topics', []))}件のトピック")
            
            return topics_data
            
        except Exception as e:
            logger.error(f"❌ 情報収集に失敗しました: {e}")
            raise
    
    def _parse_topics_response(self, content: str) -> Dict[str, Any]:
        """Claudeのレスポンスからトピックデータを解析"""
        try:
            # JSONブロックを抽出
            import re
            
            # ```json ... ``` または { ... } を探す
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # { ... } を直接探す
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("JSON形式のデータが見つかりません")
            
            # JSONをパース
            topics_data = json.loads(json_str)
            
            # デフォルト値を設定
            if "collected_at" not in topics_data:
                topics_data["collected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if "total_count" not in topics_data:
                topics_data["total_count"] = len(topics_data.get("topics", []))
            
            logger.info(f"トピックデータを解析しました: {topics_data['total_count']}件")
            return topics_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}")
            # フォールバック: テキストをそのまま返す
            return {
                "topics": [{"title_ja": "解析エラー", "summary": content[:500]}],
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": 1,
                "raw_content": content
            }
        except Exception as e:
            logger.error(f"トピックデータ解析エラー: {e}")
            raise
    
    def generate_dialogue_script(self, topics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        対談形式の台本を生成
        
        Args:
            topics_data: collect_topics_with_web_search()で収集したトピックデータ
            
        Returns:
            Dict[str, Any]: 生成された台本
        """
        try:
            logger.info("📝 Claude APIで対談形式の台本を生成します")
            
            # トピックをフォーマット
            topics_text = self._format_topics_for_script(topics_data)
            
            # トピックから最も興味深いものを1つ選択
            topics = topics_data.get("topics", [])
            if not topics:
                raise ValueError("トピックが見つかりません")
            
            # 最初のトピックを選択（後で改善：選択ロジックを追加）
            selected_topic = topics[0]
            
            prompt = f"""
あなたはYouTubeポッドキャスト番組の台本作家です。
海外のテック・個人開発・AI関連ニュースを紹介する番組で、以下の1つのトピックについて深く掘り下げた対談形式の台本を生成してください。

# 今回のトピック
## {selected_topic.get('title_ja', 'N/A')}

- **元タイトル**: {selected_topic.get('title_en', 'N/A')}
- **カテゴリ**: {selected_topic.get('category', 'N/A')}
- **出典**: {selected_topic.get('source', 'N/A')} - {selected_topic.get('url', 'N/A')}
- **概要**: {selected_topic.get('summary', 'N/A')}
- **注目ポイント**: {selected_topic.get('interesting_points', 'N/A')}

# キャラクター設定
- **Aさん（テック専門家役）**: 技術に詳しいが、一般の人にもわかりやすく説明するのが得意。「つまり、わかりやすくいうと...」「例えば...」と具体例を交えて説明。技術的な詳細も知っているが、相手の理解度に合わせて話す。
- **Bさん（一般リスナー役）**: テックに興味はあるが、専門用語は苦手。「それって何？」「普通の人にはどういう意味？」と素朴な質問をする。専門用語が出ると「ちょっと待って、それって何？」と聞き返す。理解できた時は「なるほど！」と納得する。

# 台本構成（15-18分、約4000-5000文字）

## 1. オープニング (1分、約300-400文字)
- 軽い挨拶と番組紹介
- 今日のテーマの魅力的な導入
- リスナーの興味を引く問いかけ

## 2. 基本情報の紹介 (2分、約500-600文字)
- トピックの背景・概要を説明
- Bさんが「それって何？」と質問し、Aさんがわかりやすく説明
- 出典を自然に言及

## 3. 深掘り議論 パート1 - 技術・アイデアの詳細 (5-6分、約1200-1400文字)
- Aさんが技術的な仕組みを説明
- Bさんが「ちょっと待って、それって何？」と専門用語を質問
- Aさんが「わかりやすくいうと...」「例えば...」と具体例で説明
- Bさんが「なるほど！」と理解し、さらに深い質問をする
- 既存ソリューションとの違いを身近な例で説明

## 4. 深掘り議論 パート2 - ビジネス・実用性 (5-6分、約1200-1400文字)
- Aさんがビジネスモデルを説明
- Bさんが「普通の人にはどういう意味？」と質問
- Aさんが身近な例（レストラン、コンビニなど）で説明
- 実際に使えるか？売れるか？を一般ユーザー目線で議論
- 競合や障壁についてもわかりやすく説明

## 5. リスナーへの示唆とまとめ (3分、約800-1000文字)
- 個人開発者や起業家への学び
- 真似できるポイント、注意すべきポイント
- 議論のまとめとリスナーへのメッセージ

# 重要な要件
1. **厳格な文字数制限**: 全体で4000-5000文字以内（約15-18分の音声）
2. **セクション別文字数制限を厳守**: 各セクションの文字数を必ず守る
3. **会話の流れを重視**: 各セクションが自然につながること。前の話を受けて次の話に展開する。
4. **専門用語の解説を必須**: 専門用語が出たら必ずBさんが質問し、Aさんが具体例で説明する
5. **身近な例での説明**: 技術的な内容も身近な例（料理、買い物、学校など）で説明する
6. **理解の確認**: Bさんが「なるほど！」「そういうことか！」と理解を示す場面を作る
7. **自然な掛け合い**: 
   - Aさんが専門的な話をする → Bさんが「それって何？」と質問
   - Aさんが具体例で説明 → Bさんが「なるほど！」と理解
   - お互いの意見に反応し合う
8. **話者を必ず明記**: [Aさん] [Bさん]
9. **適度な間や相槌**: 「なるほど」「確かに」「面白いですね」など
10. **リスナーへの語りかけ**: 「みなさんはどう思いますか？」など

**文字数チェック**: 生成後、必ず文字数をカウントし、5000文字を超える場合は内容を簡潔にまとめ直してください。

# 出力フォーマット
以下のJSON形式で出力してください：

```json
{{
  "title": "エピソードタイトル（70文字以内、SEO最適化）",
  "episode_number": 1,
  "full_script": "[Aさん] こんにちは！...\n\n[Bさん] はい、...\n\n[Aさん] ...",
  "sections": [
    {{
      "section_name": "オープニング",
      "content": "[Aさん] ...",
      "estimated_duration_seconds": 60,
      "word_count": 350
    }},
    {{
      "section_name": "基本情報の紹介",
      "content": "[Aさん] ...",
      "estimated_duration_seconds": 120,
      "word_count": 550
    }},
    {{
      "section_name": "深掘り議論 パート1 - 技術・アイデアの詳細",
      "content": "[Aさん] ...",
      "estimated_duration_seconds": 360,
      "word_count": 1300
    }},
    {{
      "section_name": "深掘り議論 パート2 - ビジネス・実用性",
      "content": "[Aさん] ...",
      "estimated_duration_seconds": 360,
      "word_count": 1300
    }},
    {{
      "section_name": "リスナーへの示唆とまとめ",
      "content": "[Aさん] ...",
      "estimated_duration_seconds": 180,
      "word_count": 900
    }}
  ],
  "estimated_duration_seconds": 1080,
  "word_count": 4500,
  "topics_covered": ["{selected_topic.get('title_ja', '')}"]
}}
```

必ず1つのトピックに集中し、深く掘り下げた対談を生成してください。

**⚠️ 重要: 文字数制限の厳守**
- 全体の文字数: 4000-5000文字以内
- 各セクションの文字数制限を必ず守る
- 冗長な表現は避け、簡潔で的確な内容にする
- 生成後、必ず文字数をカウントして確認する
"""
            
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # レスポンスを解析
            content = response.content[0].text
            script_data = self._parse_script_response(content)
            
            logger.info(f"✅ 台本生成完了: {script_data.get('word_count', 0)}文字、"
                       f"{script_data.get('estimated_duration_seconds', 0)}秒相当")
            
            return script_data
            
        except Exception as e:
            logger.error(f"❌ 台本生成に失敗しました: {e}")
            raise
    
    def _format_topics_for_script(self, topics_data: Dict[str, Any]) -> str:
        """トピックを台本生成用にフォーマット"""
        topics = topics_data.get("topics", [])
        
        formatted = []
        for i, topic in enumerate(topics, 1):
            topic_text = f"""
## トピック{i}: {topic.get('title_ja', topic.get('title_en', 'No Title'))}

- 元タイトル: {topic.get('title_en', 'N/A')}
- カテゴリ: {topic.get('category', 'N/A')}
- 出典: {topic.get('source', 'N/A')}
- URL: {topic.get('url', 'N/A')}
- 概要: {topic.get('summary', 'N/A')}
- 興味深いポイント: {topic.get('interesting_points', 'N/A')}
"""
            formatted.append(topic_text)
        
        return "\n".join(formatted)
    
    def _parse_script_response(self, content: str) -> Dict[str, Any]:
        """Claudeのレスポンスから台本データを解析"""
        try:
            import re
            
            # JSONブロックを抽出
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                script_data = json.loads(json_str)
            else:
                # { ... } を直接探す
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    script_data = json.loads(json_str)
                else:
                    # JSONが見つからない場合はテキスト全体を台本として扱う
                    logger.warning("JSON形式が見つからないため、テキスト全体を台本として使用します")
                    script_data = {
                        "title": "AI生成ポッドキャスト",
                        "full_script": content,
                        "sections": [],
                        "estimated_duration_seconds": len(content) * 0.3,  # 1文字0.3秒
                        "word_count": len(content)
                    }
            
            # デフォルト値を設定
            if "word_count" not in script_data and "full_script" in script_data:
                script_data["word_count"] = len(script_data["full_script"])
            
            if "estimated_duration_seconds" not in script_data:
                script_data["estimated_duration_seconds"] = script_data.get("word_count", 0) * 0.3
            
            logger.info(f"台本データを解析しました: {script_data.get('word_count', 0)}文字")
            return script_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}")
            # フォールバック
            return {
                "title": "AI生成ポッドキャスト",
                "full_script": content,
                "sections": [],
                "estimated_duration_seconds": len(content) * 0.3,
                "word_count": len(content),
                "raw_content": content
            }
        except Exception as e:
            logger.error(f"台本データ解析エラー: {e}")
            raise
