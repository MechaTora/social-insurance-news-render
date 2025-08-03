#!/usr/bin/env python3
"""
社会保険ニュース自動収集システム
GitHubリポジトリ用 - main_automation.py

主な改善点:
1. Yahoo!ニュースのURLを正確に取得
2. URLの有効性チェック
3. 改善されたエラーハンドリング
4. レート制限対応
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import hashlib

class SocialInsuranceNewsScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # User-Agentをランダム化してブロックを回避
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.categories = {
            '健康保険': ['健康保険', '協会けんぽ', '健康保険組合', '国民健康保険'],
            '厚生年金': ['厚生年金', '国民年金', 'ねんきん', '年金'],
            '雇用保険': ['雇用保険', '失業保険', '雇用維持', 'ハローワーク'],
            '労災保険': ['労災保険', '労働災害', '労災'],
            '介護保険': ['介護保険', '要介護', 'ケアマネ', '介護認定'],
            '社会保険全般': ['社会保険', '社会保障', '厚生労働省']
        }
        
    def is_valid_url(self, url):
        """URLの有効性をチェック"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    def safe_request(self, url, timeout=15, retries=3):
        """安全なHTTPリクエスト（リトライ機能付き）"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except Exception as e:
                print(f"⚠️ Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(2, 5))
                else:
                    return None
        return None
    
    def scrape_yahoo_news(self, search_term, max_articles=5):
        """Yahoo!ニュースから記事を取得（改善版）"""
        articles = []
        search_url = f"https://news.yahoo.co.jp/search?p={search_term}&ei=UTF-8"
        
        print(f"🔍 Yahoo!ニュース検索: {search_term}")
        
        response = self.safe_request(search_url)
        if not response:
            print(f"❌ Yahoo!ニュース取得失敗: {search_term}")
            return articles
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 複数のセレクタパターンで記事リンクを取得
        article_links = []
        
        # パターン1: 記事URL直接
        links1 = soup.select('a[href*="/articles/"]')
        article_links.extend(links1)
        
        # パターン2: ニュースフィード内のリンク
        links2 = soup.select('[class*="news"] a[href*="/articles/"]')
        article_links.extend(links2)
        
        # パターン3: 一般的なリンク（/articles/を含む）
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            if '/articles/' in href and 'news.yahoo.co.jp' in href:
                article_links.append(link)
        
        print(f"📰 発見されたリンク数: {len(article_links)}")
        
        processed_urls = set()
        
        for link in article_links:
            if len(articles) >= max_articles:
                break
                
            href = link.get('href', '')
            if not href or href in processed_urls:
                continue
                
            # 完全URLに変換
            if href.startswith('/'):
                full_url = f"https://news.yahoo.co.jp{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                continue
                
            if not self.is_valid_url(full_url) or full_url in processed_urls:
                continue
                
            processed_urls.add(full_url)
            
            # タイトル取得
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
                
            # 社会保険関連の記事かチェック
            if not self.is_social_insurance_related(title):
                continue
                
            # カテゴリ判定
            category = self.categorize_article(title)
            
            # 重要度判定
            importance = self.assess_importance(title)
            
            article = {
                'id': self.generate_id(title, full_url),
                'title': title,
                'url': full_url,
                'source': 'Yahoo!ニュース',
                'category': category,
                'summary': f"【{category}】 {title[:50]}{'...' if len(title) > 50 else ''}",
                'importance': importance,
                'published_date': None,  # Yahoo!ニュースでは取得が困難
                'scraped_at': datetime.now().isoformat(),
                'keywords': self.extract_keywords(title),
                'related_categories': [],
                'content_length': len(title),
                'confidence_score': self.calculate_confidence(title, category)
            }
            
            articles.append(article)
            print(f"✅ Yahoo!記事追加: {title[:50]}...")
            
        return articles
    
    def scrape_mhlw_news(self, max_articles=10):
        """厚生労働省からニュースを取得（改善版）"""
        articles = []
        
        # 複数のMHLWページをチェック
        mhlw_urls = [
            'https://www.mhlw.go.jp/stf/houdou/houdou_list.html',
            'https://www.mhlw.go.jp/stf/houdou/',
        ]
        
        for base_url in mhlw_urls:
            print(f"🏛️ 厚生労働省サイト取得: {base_url}")
            
            response = self.safe_request(base_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # MHLWサイトの記事リンクを取得
            article_links = []
            
            # パターン1: 報道発表リンク
            links1 = soup.select('a[href*="/stf/houdou/"]')
            article_links.extend(links1)
            
            # パターン2: 新着情報リンク
            links2 = soup.select('a[href*="/stf/newpage_"]')
            article_links.extend(links2)
            
            # パターン3: 一般的なリンクで社会保険関連
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                title = link.get_text(strip=True)
                if self.is_social_insurance_related(title):
                    article_links.append(link)
            
            processed_urls = set()
            
            for link in article_links:
                if len(articles) >= max_articles:
                    break
                    
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if not href or not title or href in processed_urls:
                    continue
                    
                # 完全URLに変換
                if href.startswith('/'):
                    full_url = f"https://www.mhlw.go.jp{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                    
                if not self.is_valid_url(full_url):
                    continue
                    
                processed_urls.add(href)
                
                # 社会保険関連のフィルタリング
                if not self.is_social_insurance_related(title):
                    continue
                    
                # カテゴリ判定
                category = self.categorize_article(title)
                
                # 重要度判定
                importance = self.assess_importance(title)
                
                # 公開日を抽出（試行）
                published_date = self.extract_mhlw_date(soup, link)
                
                article = {
                    'id': self.generate_id(title, full_url),
                    'title': title,
                    'url': full_url,
                    'source': '厚生労働省',
                    'category': category,
                    'summary': f"【{category}】 {title[:50]}{'...' if len(title) > 50 else ''}",
                    'importance': importance,
                    'published_date': published_date,
                    'scraped_at': datetime.now().isoformat(),
                    'keywords': self.extract_keywords(title),
                    'related_categories': [],
                    'content_length': len(title),
                    'confidence_score': self.calculate_confidence(title, category)
                }
                
                articles.append(article)
                print(f"✅ MHLW記事追加: {title[:50]}...")
                
            # サーバー負荷軽減
            time.sleep(random.uniform(2, 4))
            
        return articles
    
    def is_social_insurance_related(self, title):
        """社会保険関連の記事かどうかを判定"""
        social_insurance_keywords = [
            '年金', '保険', '社会保険', '健康', '雇用', '労災', '介護',
            '厚生年金', '国民年金', '健康保険', '雇用保険', '労災保険', '介護保険',
            '社会保障', '厚生労働省', 'ハローワーク', '給付'
        ]
        
        return any(keyword in title for keyword in social_insurance_keywords)
    
    def categorize_article(self, title):
        """記事をカテゴリに分類"""
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in title:
                    return category
        return 'その他'
    
    def assess_importance(self, title):
        """記事の重要度を評価"""
        high_priority = ['改正', '新制度', '廃止', '変更', '重要', '緊急', '速報', '施行']
        medium_priority = ['実施', '開始', '延長', '拡大', '見直し', '発表']
        
        for keyword in high_priority:
            if keyword in title:
                return '高'
                
        for keyword in medium_priority:
            if keyword in title:
                return '中'
                
        return '低'
    
    def extract_keywords(self, title):
        """タイトルからキーワードを抽出"""
        keywords = []
        
        # 金額パターン
        money_pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?(?:万|千|億|兆)?円)'
        keywords.extend(re.findall(money_pattern, title))
        
        # 年月パターン
        date_pattern = r'(\d{4}年\d{1,2}月|\d{1,2}月\d{1,2}日|令和\d+年)'
        keywords.extend(re.findall(date_pattern, title))
        
        # 機関名
        institutions = ['厚生労働省', '日本年金機構', '協会けんぽ', '健康保険組合']
        for inst in institutions:
            if inst in title:
                keywords.append(inst)
        
        return keywords[:5]  # 最大5個
    
    def extract_mhlw_date(self, soup, link):
        """厚生労働省記事の公開日を抽出"""
        try:
            # 親要素から日付を探す
            parent = link.find_parent()
            if parent:
                date_text = parent.get_text()
                
                # 日付パターンを検索
                date_patterns = [
                    r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                    r'令和(\d+)年(\d{1,2})月(\d{1,2})日',
                    r'(\d{4})-(\d{1,2})-(\d{1,2})'
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, date_text)
                    if match:
                        return match.group(0)
            return None
        except:
            return None
    
    def calculate_confidence(self, title, category):
        """記事の信頼度スコアを計算"""
        score = 0.5  # ベーススコア
        
        # タイトルの長さ
        if 10 <= len(title) <= 100:
            score += 0.2
            
        # カテゴリの適合度
        if category != 'その他':
            score += 0.2
            
        # 専門用語の有無
        technical_terms = ['保険料', '給付', '適用', '認定', '申請', '制度']
        if any(term in title for term in technical_terms):
            score += 0.1
            
        return min(score, 1.0)
    
    def generate_id(self, title, url):
        """記事IDを生成"""
        combined = f"{title}{url}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def run_collection(self):
        """メインの収集処理"""
        print("🚀 社会保険ニュース自動収集開始（修正版）")
        
        all_articles = []
        
        # Yahoo!ニュースから収集
        yahoo_terms = ['社会保険', '厚生年金', '健康保険', '雇用保険', '介護保険']
        for term in yahoo_terms:
            articles = self.scrape_yahoo_news(term, max_articles=3)
            all_articles.extend(articles)
            # レート制限対応
            time.sleep(random.uniform(3, 6))
        
        # 厚生労働省から収集
        mhlw_articles = self.scrape_mhlw_news(max_articles=10)
        all_articles.extend(mhlw_articles)
        
        # 重複除去
        unique_articles = {}
        for article in all_articles:
            article_id = article['id']
            if article_id not in unique_articles:
                unique_articles[article_id] = article
        
        final_articles = list(unique_articles.values())
        
        # カテゴリ別に整理
        categorized = {}
        for article in final_articles:
            category = article['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(article)
        
        # 統計計算
        high_importance = sum(1 for article in final_articles if article['importance'] == '高')
        
        # JSONファイルに保存
        result = {
            'last_updated': datetime.now().isoformat(),
            'total_count': len(final_articles),
            'categories': categorized
        }
        
        # データファイルの保存
        with open('data/processed_news.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 日次レポートの生成
        daily_report = {
            'date': datetime.now().strftime('%Y年%m月%d日'),
            'summary': {
                'total_news': len(final_articles),
                'high_importance': high_importance,
                'categories': list(categorized.keys()),
                'top_keywords': self.get_top_keywords(final_articles)
            },
            'highlights': [
                article for article in final_articles 
                if article['importance'] == '高'
            ][:5]
        }
        
        with open('data/daily_report.json', 'w', encoding='utf-8') as f:
            json.dump(daily_report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 収集完了: {len(final_articles)}件の記事")
        print(f"📂 カテゴリ数: {len(categorized)}")
        print(f"🔥 重要ニュース: {high_importance}件")
        
        # カテゴリ別統計
        for category, articles in categorized.items():
            print(f"   {category}: {len(articles)}件")
        
        return result
    
    def get_top_keywords(self, articles):
        """記事から主要キーワードを抽出"""
        keyword_count = {}
        for article in articles:
            for keyword in article.get('keywords', []):
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        # 出現回数でソートして上位10個を返す
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:10]]

def main():
    """メイン実行関数"""
    scraper = SocialInsuranceNewsScraper()
    scraper.run_collection()

if __name__ == "__main__":
    main()