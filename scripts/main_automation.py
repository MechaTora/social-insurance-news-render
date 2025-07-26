#!/usr/bin/env python3
"""
Render版 社会保険ニュース自動化スクリプト
毎朝4時実行 - スクレイピング→AI要約→データ更新
"""

import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
import random

# パス設定
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

class RenderNewsAutomation:
    """Render用ニュース自動化クラス"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
        })
        
        # データファイルパス
        self.processed_file = DATA_DIR / 'processed_news.json'
        self.report_file = DATA_DIR / 'daily_report.json'
    
    def scrape_mhlw_news(self):
        """厚生労働省ニュース取得"""
        news_list = []
        
        try:
            print("🏛️ 厚生労働省ニュース取得開始")
            
            # 厚労省プレスリリース
            mhlw_urls = [
                'https://www.mhlw.go.jp/stf/houdou/houdou_list.html',
                'https://www.mhlw.go.jp/stf/newpage_index.html'
            ]
            
            for url in mhlw_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # ニュース項目を抽出
                    links = soup.find_all('a', href=True)
                    
                    for link in links[:10]:  # 上位10件
                        href = link.get('href', '')
                        title = link.get_text(strip=True)
                        
                        if (len(title) > 10 and 
                            ('年金' in title or '保険' in title or '社会保険' in title)):
                            
                            # 相対URLを絶対URLに変換
                            if href.startswith('/'):
                                full_url = 'https://www.mhlw.go.jp' + href
                            else:
                                full_url = href
                            
                            news_item = {
                                'title': title,
                                'url': full_url,
                                'source': '厚生労働省',
                                'category': self.categorize_news(title),
                                'importance': self.assess_importance(title),
                                'summary': f"【{self.categorize_news(title)}】 {title[:50]}...",
                                'keywords': self.extract_keywords(title),
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            news_list.append(news_item)
                    
                    time.sleep(2)  # レート制限対応
                    
                except Exception as e:
                    print(f"厚労省URL取得エラー {url}: {e}")
                    continue
            
            print(f"✅ 厚労省ニュース {len(news_list)}件取得")
            return news_list
            
        except Exception as e:
            print(f"❌ 厚労省ニュース取得エラー: {e}")
            return []
    
    def scrape_yahoo_news(self):
        """Yahoo!ニュース 社会保険関連取得"""
        news_list = []
        
        try:
            print("📺 Yahoo!ニュース取得開始")
            
            # Yahoo!ニュース検索（社会保険関連）
            search_terms = ['社会保険', '厚生年金', '健康保険', '雇用保険', '年金改正']
            
            for term in search_terms:
                try:
                    search_url = f"https://news.yahoo.co.jp/search?p={term}&ei=UTF-8"
                    response = self.session.get(search_url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # ニュースアイテム抽出
                    articles = soup.find_all('div', class_='newsFeed_item')
                    
                    for article in articles[:5]:  # 各検索語で5件
                        try:
                            link_elem = article.find('a')
                            if not link_elem:
                                continue
                            
                            title = link_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            
                            if url.startswith('/'):
                                url = 'https://news.yahoo.co.jp' + url
                            
                            news_item = {
                                'title': title,
                                'url': url,
                                'source': 'Yahoo!ニュース',
                                'category': self.categorize_news(title),
                                'importance': self.assess_importance(title),
                                'summary': f"【{self.categorize_news(title)}】 {title[:60]}...",
                                'keywords': self.extract_keywords(title),
                                'published_date': 'None',
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            news_list.append(news_item)
                            
                        except Exception as e:
                            print(f"Yahoo記事解析エラー: {e}")
                            continue
                    
                    time.sleep(3)  # レート制限
                    
                except Exception as e:
                    print(f"Yahoo検索エラー {term}: {e}")
                    continue
            
            print(f"✅ Yahoo!ニュース {len(news_list)}件取得")
            return news_list
            
        except Exception as e:
            print(f"❌ Yahoo!ニュース取得エラー: {e}")
            return []
    
    def categorize_news(self, title):
        """ニュースカテゴリ分類"""
        title_lower = title.lower()
        
        if '健康保険' in title or '医療保険' in title:
            return '健康保険'
        elif '厚生年金' in title or '年金' in title:
            return '厚生年金'
        elif '雇用保険' in title or '失業' in title:
            return '雇用保険'
        elif '労災' in title or '労働災害' in title:
            return '労災保険'
        elif '介護保険' in title or '介護' in title:
            return '介護保険'
        elif '社会保険' in title:
            return '社会保険全般'
        else:
            return 'その他'
    
    def assess_importance(self, title):
        """重要度判定"""
        high_keywords = ['改正', '変更', '引き上げ', '引き下げ', '新制度', '廃止', '緊急']
        medium_keywords = ['見直し', '検討', '予定', '案', '方針']
        
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in high_keywords):
            return '高'
        elif any(keyword in title_lower for keyword in medium_keywords):
            return '中'
        else:
            return '低'
    
    def extract_keywords(self, text):
        """キーワード抽出（簡易版）"""
        import re
        
        # 金額パターン
        money_patterns = re.findall(r'\d+(?:,\d+)*(?:万円|円|億円)', text)
        
        # 年度パターン  
        year_patterns = re.findall(r'(?:令和|平成)?\d+年(?:\d+月)?', text)
        
        # 重要キーワード
        important_words = []
        keywords = ['厚生労働省', '年金機構', '社会保険', '改正案', '新制度']
        
        for keyword in keywords:
            if keyword in text:
                important_words.append(keyword)
        
        return money_patterns + year_patterns + important_words
    
    def generate_daily_report(self, news_data):
        """日次レポート生成"""
        try:
            total_news = len(news_data)
            high_importance = len([n for n in news_data if n.get('importance') == '高'])
            
            # カテゴリ別集計
            categories = {}
            for news in news_data:
                cat = news.get('category', 'その他')
                categories[cat] = categories.get(cat, 0) + 1
            
            # 頻出キーワード
            all_keywords = []
            for news in news_data:
                all_keywords.extend(news.get('keywords', []))
            
            keyword_count = {}
            for keyword in all_keywords:
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            
            top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_news': total_news,
                    'high_importance': high_importance,
                    'categories': list(categories.keys()),
                    'top_keywords': [k[0] for k in top_keywords]
                },
                'categories': categories,
                'keywords': dict(top_keywords)
            }
            
            # レポート保存
            with open(self.report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"📊 日次レポート生成完了: {total_news}件")
            return report
            
        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")
            return None
    
    def save_processed_data(self, news_data):
        """処理済みデータ保存"""
        try:
            # 重複除去
            unique_news = []
            seen_urls = set()
            
            for news in news_data:
                url = news.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_news.append(news)
            
            # 重要度順・新しい順でソート
            importance_order = {'高': 3, '中': 2, '低': 1}
            unique_news.sort(
                key=lambda x: (
                    importance_order.get(x.get('importance', '低'), 1),
                    x.get('scraped_at', '')
                ),
                reverse=True
            )
            
            # データ構造
            processed_data = {
                'last_updated': datetime.now().isoformat(),
                'total_count': len(unique_news),
                'news': unique_news,
                'categories': {}
            }
            
            # カテゴリ別分類
            for news in unique_news:
                category = news.get('category', 'その他')
                if category not in processed_data['categories']:
                    processed_data['categories'][category] = []
                processed_data['categories'][category].append(news)
            
            # ファイル保存
            with open(self.processed_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 処理済みデータ保存完了: {len(unique_news)}件")
            return True
            
        except Exception as e:
            print(f"❌ データ保存エラー: {e}")
            return False
    
    def run_automation(self):
        """自動化実行"""
        try:
            print("🚀 Render版社会保険ニュース自動化開始")
            print(f"⏰ 開始時刻: {self.start_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            print("-" * 60)
            
            # Step 1: ニュース収集
            all_news = []
            
            # 厚労省ニュース
            mhlw_news = self.scrape_mhlw_news()
            all_news.extend(mhlw_news)
            
            # Yahoo!ニュース
            yahoo_news = self.scrape_yahoo_news()
            all_news.extend(yahoo_news)
            
            if not all_news:
                print("❌ ニュース収集失敗")
                return False
            
            print(f"📡 総収集件数: {len(all_news)}件")
            
            # Step 2: データ処理・保存
            if not self.save_processed_data(all_news):
                print("❌ データ保存失敗")
                return False
            
            # Step 3: レポート生成
            self.generate_daily_report(all_news)
            
            # 実行時間計算
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            print("-" * 60)
            print("🎉 自動化完了!")
            print(f"⏱️  実行時間: {duration.total_seconds():.1f}秒")
            print(f"📊 処理件数: {len(all_news)}件")
            print(f"🕐 完了時刻: {end_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 自動化エラー: {e}")
            print("詳細エラー:")
            traceback.print_exc()
            return False

def main():
    """メイン実行"""
    automation = RenderNewsAutomation()
    success = automation.run_automation()
    
    if success:
        print("\n✅ 社会保険ニュース自動化成功!")
        sys.exit(0)
    else:
        print("\n❌ 社会保険ニュース自動化失敗!")
        sys.exit(1)

if __name__ == "__main__":
    main()