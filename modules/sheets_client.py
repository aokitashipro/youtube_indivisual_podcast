"""
Google Sheets連携モジュール

GAS Web APIを通じてGoogle Sheetsとやり取りする
"""
import requests
import json
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SheetsClient:
    """Google Sheets APIクライアントクラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.gas_url = settings.GAS_WEB_APP_URL
        self.execution_id = None
        
    def test_connection(self) -> bool:
        """接続テスト"""
        try:
            response = requests.get(f"{self.gas_url}?action=test", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"✅ Google Sheets API接続成功: {result.get('message')}")
                return True
            else:
                logger.error(f"❌ Google Sheets API接続失敗: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Google Sheets API接続エラー: {e}")
            return False
    
    def get_prompts(self) -> Dict[str, str]:
        """
        スプレッドシートから最新のプロンプトを取得
        
        Returns:
            Dict[str, str]: {
                'info_collect': '情報収集プロンプト',
                'script_generate': '台本生成プロンプト'
            }
        """
        try:
            logger.info("📥 Google Sheetsからプロンプトを取得中...")
            
            response = requests.get(f"{self.gas_url}?action=get_prompts", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                prompts = result.get('prompts', {})
                logger.info("✅ プロンプト取得成功")
                logger.info(f"   - 情報収集プロンプト: {len(prompts.get('info_collect', ''))}文字")
                logger.info(f"   - 台本生成プロンプト: {len(prompts.get('script_generate', ''))}文字")
                return prompts
            else:
                logger.error(f"❌ プロンプト取得失敗: {result.get('error')}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ プロンプト取得エラー: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        実行統計を取得
        
        Returns:
            Dict[str, Any]: {
                'total': 総実行回数,
                'completed': 成功回数,
                'processing': 処理中,
                'error': エラー回数
            }
        """
        try:
            logger.info("📊 実行統計を取得中...")
            
            response = requests.get(f"{self.gas_url}?action=get_stats", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                stats = result.get('stats', {})
                logger.info("✅ 統計取得成功")
                logger.info(f"   - 総実行回数: {stats.get('total', 0)}回")
                logger.info(f"   - 成功: {stats.get('completed', 0)}回")
                logger.info(f"   - 処理中: {stats.get('processing', 0)}回")
                logger.info(f"   - エラー: {stats.get('error', 0)}回")
                return stats
            else:
                logger.error(f"❌ 統計取得失敗: {result.get('error')}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ 統計取得エラー: {e}")
            return {}
    
    def create_execution_log(self, custom_prompts: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        新しい実行ログを作成（動的プロンプト生成対応）
        
        Args:
            custom_prompts: カスタムプロンプト（省略時は動的生成）
                {
                    'info_collect': '情報収集プロンプト',
                    'script_generate': '台本生成プロンプト'
                }
        
        Returns:
            Optional[str]: 実行ID（成功時）、None（失敗時）
        """
        try:
            logger.info("📝 新しい実行ログを作成中...")
            
            # 動的プロンプトを生成（カスタムプロンプトが指定されていない場合）
            if not custom_prompts:
                custom_prompts = self._generate_dynamic_prompts()
                logger.info("🎯 動的プロンプトを生成しました")
                logger.info(f"   - 情報収集: {len(custom_prompts.get('info_collect', ''))}文字")
                logger.info(f"   - 台本生成: {len(custom_prompts.get('script_generate', ''))}文字")
            
            payload = {
                'action': 'create_log',
                'custom_prompts': custom_prompts
            }
            
            response = requests.post(
                self.gas_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                self.execution_id = result.get('execution_id')
                logger.info(f"✅ 実行ログ作成成功: {self.execution_id}")
                return self.execution_id
            else:
                logger.error(f"❌ 実行ログ作成失敗: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 実行ログ作成エラー: {e}")
            return None
    
    def update_execution_log(
        self,
        execution_id: Optional[str] = None,
        status: Optional[str] = None,
        search_result: Optional[str] = None,
        generated_script: Optional[str] = None,
        audio_url: Optional[str] = None,
        video_url: Optional[str] = None,
        processing_time: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        実行ログを更新
        
        Args:
            execution_id: 実行ID（省略時は最後に作成したID）
            status: ステータス（処理中/完了/エラー）
            search_result: 検索結果（JSON文字列）
            generated_script: 生成された台本（JSON文字列）
            audio_url: 音声ファイルのURL
            video_url: 動画ファイルのURL
            processing_time: 処理時間
            notes: 備考
            
        Returns:
            bool: 成功時True、失敗時False
        """
        try:
            exec_id = execution_id or self.execution_id
            
            if not exec_id:
                logger.error("❌ 実行IDが指定されていません")
                return False
            
            logger.info(f"📝 実行ログを更新中: {exec_id}")
            
            # 更新するフィールドのみをペイロードに含める
            payload = {
                'action': 'update_log',
                'execution_id': exec_id
            }
            
            if status:
                payload['status'] = status
            if search_result:
                # JSON文字列が長すぎる場合は要約
                if len(search_result) > 10000:
                    payload['search_result'] = search_result[:10000] + '...(省略)'
                else:
                    payload['search_result'] = search_result
            if generated_script:
                # JSON文字列が長すぎる場合は要約
                if len(generated_script) > 10000:
                    payload['generated_script'] = generated_script[:10000] + '...(省略)'
                else:
                    payload['generated_script'] = generated_script
            if audio_url:
                payload['audio_url'] = audio_url
            if video_url:
                payload['video_url'] = video_url
            if processing_time:
                payload['processing_time'] = processing_time
            if notes:
                payload['notes'] = notes
            
            response = requests.post(
                self.gas_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"✅ 実行ログ更新成功: {exec_id}")
                return True
            else:
                logger.error(f"❌ 実行ログ更新失敗: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 実行ログ更新エラー: {e}")
            return False
    
    def log_step_completion(
        self,
        step_name: str,
        success: bool = True,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        ステップ完了をログに記録
        
        Args:
            step_name: ステップ名（例: '情報収集', '台本生成'）
            success: 成功したかどうか
            result_data: 結果データ
            error_message: エラーメッセージ（失敗時）
            
        Returns:
            bool: 成功時True、失敗時False
        """
        try:
            if not self.execution_id:
                logger.warning("実行IDが設定されていないため、ログを記録できません")
                return False
            
            # ステップごとに適切な列に結果を保存
            if step_name == '情報収集' and result_data:
                search_result = json.dumps(result_data, ensure_ascii=False, indent=2)
                return self.update_execution_log(search_result=search_result)
                
            elif step_name == '台本生成' and result_data:
                generated_script = json.dumps(result_data, ensure_ascii=False, indent=2)
                return self.update_execution_log(generated_script=generated_script)
                
            elif step_name == '音声生成' and result_data:
                audio_url = result_data.get('audio_url', '')
                return self.update_execution_log(audio_url=audio_url)
                
            elif step_name == '動画生成' and result_data:
                video_url = result_data.get('video_url', '')
                return self.update_execution_log(video_url=video_url)
                
            elif not success and error_message:
                return self.update_execution_log(
                    status='エラー',
                    notes=f"{step_name}で失敗: {error_message}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ステップ完了ログ記録エラー: {e}")
            return False
    
    def mark_as_completed(self, processing_time: str) -> bool:
        """
        実行を完了としてマーク
        
        Args:
            processing_time: 処理時間（例: '25分30秒'）
            
        Returns:
            bool: 成功時True、失敗時False
        """
        return self.update_execution_log(
            status='完了',
            processing_time=processing_time
        )
    
    def mark_as_error(self, error_message: str) -> bool:
        """
        実行をエラーとしてマーク
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            bool: 成功時True、失敗時False
        """
        return self.update_execution_log(
            status='エラー',
            notes=error_message
        )
    
    def _generate_dynamic_prompts(self) -> Dict[str, str]:
        """
        日付と状況に基づいて動的にプロンプトを生成
        
        Returns:
            Dict[str, str]: 生成されたプロンプト
        """
        from datetime import datetime
        import random
        
        now = datetime.now()
        weekday = now.strftime('%A')
        date_str = now.strftime('%Y年%m月%d日')
        month = now.month
        
        # 季節判定
        if month in [12, 1, 2]:
            season = '冬'
            season_theme = '内省と計画'
        elif month in [3, 4, 5]:
            season = '春'
            season_theme = '新しい始まりと成長'
        elif month in [6, 7, 8]:
            season = '夏'
            season_theme = '活発でエネルギッシュ'
        else:
            season = '秋'
            season_theme = '収穫と振り返り'
        
        # 曜日別テーマ
        weekday_themes = {
            'Monday': '新しい週の始まり、目標設定',
            'Tuesday': '効率化、生産性向上',
            'Wednesday': '中盤の息抜き、エンターテイメント',
            'Thursday': 'ビジネス戦略、マーケティング',
            'Friday': '週末前、まとめ',
            'Saturday': '週末、趣味、ライフスタイル',
            'Sunday': '振り返り、次週の準備'
        }
        
        # 今日の特別要素
        special_elements = {
            'Monday': ['新しい挑戦', '目標達成', 'モチベーション'],
            'Tuesday': ['効率化ツール', '生産性向上', '自動化'],
            'Wednesday': ['クリエイティブ', 'エンターテイメント', '息抜き'],
            'Thursday': ['ビジネス成功', 'マーケティング', '成長戦略'],
            'Friday': ['週末準備', '成果まとめ', 'リラックス'],
            'Saturday': ['趣味開発', 'ライフスタイル', '週末活用'],
            'Sunday': ['振り返り', '次週準備', '学びの整理']
        }
        
        today_theme = weekday_themes.get(weekday, '通常')
        today_element = random.choice(special_elements.get(weekday, ['通常']))
        
        # 情報収集プロンプト
        info_collect_prompt = f"""あなたは海外の個人開発・AI関連ニュースを収集する専門家です。

【今日の特別設定】
- 日付: {date_str} ({weekday})
- 季節: {season}（{season_theme}の季節）
- 今日のテーマ: {today_theme}
- 注目要素: {today_element}

【収集基準】
- 投稿日時が新しいもの（24-48時間以内を優先）
- {today_element}に関連するトピックを1件は必ず含める
- リスナーの{weekday}の気分に合った内容を選ぶ
- {season_theme}を意識した話題を織り交ぜる
- 個人開発者や小規模チームが参考になる
- ビジネスモデルや技術的に興味深い

【情報源】
1. **Indie Hackers** - 個人開発者の成功事例、MicroSaaSのトレンド
2. **Product Hunt** - 新規AIツール・プロダクト（特に本日・昨日ローンチ）
3. **Hacker News Show HN** - 技術的に興味深いプロジェクト、オープンソース

各トピックについて以下の情報を含めてください：
- タイトル（日本語訳）
- 元のタイトル（英語）
- 概要（200-300文字程度、日本語で詳しく）
- URL（必須: 重複チェックに使用）
- カテゴリ（個人開発/AI/MicroSaaS/技術/オープンソース/その他）
- 興味深いポイント（なぜこれが注目すべきか、300文字程度）
- 投稿日時（可能な限り正確に）

必ずJSONフォーマットで返してください。"""

        # 台本生成プロンプト
        script_generate_prompt = f"""あなたはYouTubeポッドキャスト番組の台本作家です。

【今日の特別設定】
- 日付: {date_str} ({weekday})
- 季節: {season}（{season_theme}の季節）
- 今日のテーマ: {today_theme}
- 注目要素: {today_element}

【キャラクター設定】
- **Aさん（楽観派・興味津々役）**: 新しい技術やアイデアに興奮する。「これ面白い！」「可能性がある！」と前のめり。実装方法や応用例を考えるのが好き。
- **Bさん（懐疑派・現実派）**: 冷静で批判的。「本当にうまくいくの？」「ビジネスとして成立する？」と疑問を投げかける。実用性や収益性を重視。

【今日の対談スタイル】
- {weekday}らしい自然な流れで
- {season_theme}を感じられる表現を織り交ぜる
- {today_element}に関連する具体例を含める
- リスナーの{weekday}の気分に合った内容で

【台本構成（15-18分、約4000-5000文字）】

## 1. オープニング (1分、約300-400文字)
- 軽い挨拶と番組紹介
- 今日のテーマの魅力的な導入（{today_theme}を意識）
- リスナーの興味を引く問いかけ

## 2. 基本情報の紹介 (2分、約500-600文字)
- トピックの背景・概要を説明
- AさんとBさんの第一印象
- 出典を自然に言及

## 3. 深掘り議論 パート1 - 技術・アイデアの詳細 (5-6分、約1200-1400文字)
- 技術的な仕組みや実装方法
- 既存ソリューションとの違い
- Aさんの興奮とBさんのツッコミ
- 具体例を交えた議論

## 4. 深掘り議論 パート2 - ビジネス・実用性 (5-6分、約1200-1400文字)
- ビジネスモデルや収益化の可能性
- ターゲット市場の分析
- 実際に使えるか？売れるか？
- 競合や障壁についての議論

## 5. リスナーへの示唆とまとめ (3分、約800-1000文字)
- 個人開発者や起業家への学び
- 真似できるポイント、注意すべきポイント
- 議論のまとめとリスナーへのメッセージ

【重要な要件】
1. **厳格な文字数制限**: 全体で4000-5000文字以内（約15-18分の音声）
2. **セクション別文字数制限を厳守**: 各セクションの文字数を必ず守る
3. **会話の流れを重視**: 各セクションが自然につながること
4. **簡潔で的確な議論**: 冗長な表現を避け、要点を絞った深い議論
5. **自然な掛け合い**: Aさんが興奮して語る → Bさんが冷静にツッコむ
6. **話者を必ず明記**: [Aさん] [Bさん]
7. **適度な間や相槌**: 「なるほど」「確かに」「面白いですね」など
8. **リスナーへの語りかけ**: 「みなさんはどう思いますか？」など

**文字数チェック**: 生成後、必ず文字数をカウントし、5000文字を超える場合は内容を簡潔にまとめ直してください。

必ず{today_element}に関連する具体例を含め、{weekday}のリスナーに響く内容にしてください。"""

        return {
            'info_collect': info_collect_prompt,
            'script_generate': script_generate_prompt
        }


# ============================================================================
# 使用例
# ============================================================================

if __name__ == "__main__":
    from config.settings import Settings
    
    # 設定を読み込み
    settings = Settings()
    
    # SheetsClientを初期化
    client = SheetsClient(settings)
    
    # 接続テスト
    print("\n=== 接続テスト ===")
    client.test_connection()
    
    # プロンプト取得
    print("\n=== プロンプト取得 ===")
    prompts = client.get_prompts()
    print(f"取得したプロンプト: {list(prompts.keys())}")
    
    # 統計取得
    print("\n=== 統計取得 ===")
    stats = client.get_statistics()
    print(f"統計: {stats}")
    
    # 実行ログ作成（テスト）
    print("\n=== 実行ログ作成テスト ===")
    execution_id = client.create_execution_log()
    
    if execution_id:
        # ログ更新テスト
        print("\n=== ログ更新テスト ===")
        client.update_execution_log(
            status='完了',
            notes='テスト実行'
        )

