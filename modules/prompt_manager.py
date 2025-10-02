"""
プロンプト管理モジュール

Google Spreadsheetからプロンプトを読み取り、日付に基づいて動的に調整する
"""
import gspread
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import random

logger = logging.getLogger(__name__)


class PromptManager:
    """プロンプト管理クラス"""
    
    def __init__(self, settings):
        self.settings = settings
        self.gc = None
        self._init_google_sheets()
        
        # 日別の特別要素
        self.daily_elements = {
            'Monday': ['新しい週の始まり', '目標設定', 'モチベーション'],
            'Tuesday': ['効率化', '生産性', 'ツール紹介'],
            'Wednesday': ['中盤の息抜き', 'エンターテイメント', 'クリエイティブ'],
            'Thursday': ['ビジネス戦略', 'マーケティング', '成長'],
            'Friday': ['週末前', 'まとめ', 'リラックス'],
            'Saturday': ['週末', '趣味', 'ライフスタイル'],
            'Sunday': ['振り返り', '次週の準備', '学び']
        }
        
        # 季節別の調整
        self.season_adjustments = {
            'Spring': '新しい始まりと成長の季節',
            'Summer': '活発でエネルギッシュな季節',
            'Autumn': '収穫と振り返りの季節',
            'Winter': '内省と計画の季節'
        }
    
    def _init_google_sheets(self):
        """Google Sheets接続を初期化"""
        try:
            self.gc = gspread.service_account(filename=self.settings.GOOGLE_CREDENTIALS_PATH)
            logger.info("Google Sheets接続を初期化しました")
        except Exception as e:
            logger.error(f"Google Sheets接続に失敗しました: {e}")
            self.gc = None
    
    def get_season(self, date: datetime) -> str:
        """日付から季節を判定"""
        month = date.month
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'
    
    def get_daily_prompt(self, prompt_type: str, date: datetime = None) -> str:
        """日付に基づいてプロンプトを動的に生成"""
        if date is None:
            date = datetime.now()
        
        # ベースプロンプトを取得
        base_prompt = self._get_base_prompt(prompt_type)
        
        # 日付情報を取得
        weekday = date.strftime('%A')
        season = self.get_season(date)
        
        # 特別要素を選択
        daily_element = random.choice(self.daily_elements.get(weekday, ['通常']))
        season_adj = self.season_adjustments.get(season, '')
        
        # プロンプトを動的に生成
        if prompt_type == "info_collect":
            return self._build_info_collect_prompt(base_prompt, date, weekday, season_adj, daily_element)
        elif prompt_type == "script_generate":
            return self._build_script_generate_prompt(base_prompt, date, weekday, season_adj, daily_element)
        else:
            return base_prompt
    
    def _get_base_prompt(self, prompt_type: str) -> str:
        """Google Sheetsからベースプロンプトを取得"""
        if not self.gc:
            return self._get_fallback_prompt(prompt_type)
        
        try:
            # プロンプト管理シートを開く
            sheet = self.gc.open_by_key(self.settings.GOOGLE_SHEETS_ID).worksheet("プロンプト管理")
            
            # 有効なプロンプトを検索
            records = sheet.get_all_records()
            for record in records:
                if (record.get('プロンプトID') == prompt_type and 
                    record.get('有効/無効') == '有効'):
                    return record.get('プロンプト内容', '')
            
            logger.warning(f"プロンプト {prompt_type} が見つかりません")
            return self._get_fallback_prompt(prompt_type)
            
        except Exception as e:
            logger.error(f"プロンプト取得エラー: {e}")
            return self._get_fallback_prompt(prompt_type)
    
    def _build_info_collect_prompt(self, base_prompt: str, date: datetime, weekday: str, 
                                   season_adj: str, daily_element: str) -> str:
        """情報収集プロンプトを構築"""
        return f"""{base_prompt}

【今日の特別設定】
- 日付: {date.strftime('%Y年%m月%d日')} ({weekday})
- 季節: {season_adj}
- 今日のテーマ: {daily_element}

【今日の特別要求】
- {daily_element}に関連するトピックを1件は必ず含める
- リスナーの{weekday}の気分に合った内容を選ぶ
- {season_adj}を意識した話題を織り交ぜる

必ず最新・新着順の情報を優先してください。
"""
    
    def _build_script_generate_prompt(self, base_prompt: str, date: datetime, weekday: str,
                                      season_adj: str, daily_element: str) -> str:
        """台本生成プロンプトを構築"""
        return f"""{base_prompt}

【今日の特別設定】
- 日付: {date.strftime('%Y年%m月%d日')} ({weekday})
- 季節: {season_adj}
- 今日のテーマ: {daily_element}

【今日の対談スタイル】
- {weekday}らしい自然な流れで
- {season_adj}を感じられる表現を織り交ぜる
- {daily_element}に関連する具体例を含める

【文字数制限】
- 全体: 4000-5000文字（15-18分）
- 各セクションの文字数制限を厳守

必ず{weekday}のリスナーに響く内容にしてください。
"""
    
    def _get_fallback_prompt(self, prompt_type: str) -> str:
        """フォールバック用のプロンプト"""
        if prompt_type == "info_collect":
            return """
あなたは海外の個人開発・AI関連ニュースを収集する専門家です。

以下の情報源から、最新の興味深いトピックを5件収集してください：
- Indie Hackers
- Product Hunt  
- Hacker News Show HN

必ず最新・新着順の情報を優先してください。
"""
        elif prompt_type == "script_generate":
            return """
あなたはYouTubeポッドキャスト番組の台本作家です。

収集された情報を基に、15-18分の対談形式の台本を生成してください。

文字数制限: 4000-5000文字以内
"""
        else:
            return "プロンプトが見つかりません。"
    
    def log_execution(self, execution_data: Dict[str, Any]) -> bool:
        """実行ログをGoogle Sheetsに記録"""
        if not self.gc:
            logger.warning("Google Sheetsが利用できないため、ログを記録できません")
            return False
        
        try:
            # メインシートを開く
            sheet = self.gc.open_by_key(self.settings.GOOGLE_SHEETS_ID).worksheet("実行ログ")
            
            # 新しい行を追加
            row_data = [
                execution_data.get('execution_id', ''),
                execution_data.get('execution_time', ''),
                execution_data.get('status', ''),
                execution_data.get('prompt_a', ''),
                execution_data.get('search_result', ''),
                execution_data.get('prompt_b', ''),
                execution_data.get('generated_script', ''),
                execution_data.get('audio_url', ''),
                execution_data.get('video_url', ''),
                execution_data.get('processing_time', ''),
                execution_data.get('notes', '')
            ]
            
            sheet.append_row(row_data)
            logger.info(f"実行ログを記録しました: {execution_data.get('execution_id')}")
            return True
            
        except Exception as e:
            logger.error(f"実行ログ記録エラー: {e}")
            return False
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """プロンプトの統計情報を取得"""
        if not self.gc:
            return {}
        
        try:
            sheet = self.gc.open_by_key(self.settings.GOOGLE_SHEETS_ID).worksheet("プロンプト管理")
            records = sheet.get_all_records()
            
            stats = {
                'total_prompts': len(records),
                'active_prompts': len([r for r in records if r.get('有効/無効') == '有効']),
                'avg_success_rate': sum(float(r.get('成功率', 0)) for r in records) / len(records) if records else 0,
                'most_used': max(records, key=lambda x: int(x.get('使用回数', 0))) if records else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"統計情報取得エラー: {e}")
            return {}
