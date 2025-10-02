"""
Claude API呼び出しモジュール
"""
import anthropic
import yaml
from typing import Dict, Any
import logging
from pathlib import Path

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
    
    async def generate_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """メインコンテンツを生成"""
        try:
            # プロンプトテンプレートを取得
            prompt_template = self.prompts.get("main_content_prompt", "")
            
            # データをプロンプトに埋め込み
            prompt = prompt_template.format(data=data)
            
            # Claude APIを呼び出し
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
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
                model="claude-3-sonnet-20240229",
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
