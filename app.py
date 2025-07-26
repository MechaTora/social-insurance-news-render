#!/usr/bin/env python3
"""
Render版 社会保険ニュースサイト - Flask App
スマホ特化・i-mobile/Zucks広告対応
"""

from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import subprocess
import sys

app = Flask(__name__)

# 設定
app.config['JSON_AS_ASCII'] = False

class SocialInsuranceNewsApp:
    """Render版ニュースアプリ"""
    
    def __init__(self):
        self.data_file = 'data/processed_news.json'
        self.report_file = 'data/daily_report.json'
    
    def load_news_data(self):
        """ニュースデータ読み込み"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'news': [], 'total_count': 0, 'categories': {}}
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            return {'news': [], 'total_count': 0, 'categories': {}}
    
    def load_report_data(self):
        """レポートデータ読み込み"""
        try:
            if os.path.exists(self.report_file):
                with open(self.report_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'summary': {'high_importance': 0, 'categories': [], 'top_keywords': []}}
        except Exception as e:
            print(f"レポート読み込みエラー: {e}")
            return {'summary': {'high_importance': 0, 'categories': [], 'top_keywords': []}}
    
    def update_news(self):
        """ニュース更新（手動実行用）"""
        try:
            # メインの自動化スクリプトを実行
            result = subprocess.run([sys.executable, 'scripts/main_automation.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {"status": "success", "message": "ニュース更新完了"}
            else:
                return {"status": "error", "message": f"更新エラー: {result.stderr}"}
                
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "更新タイムアウト（5分）"}
        except Exception as e:
            return {"status": "error", "message": f"更新エラー: {str(e)}"}

# アプリインスタンス
news_app = SocialInsuranceNewsApp()

@app.route('/')
def index():
    """メインページ"""
    news_data = news_app.load_news_data()
    report_data = news_app.load_report_data()
    
    # スマホ特化のコンテキスト準備
    context = {
        'news': news_data.get('news', [])[:20],  # スマホ表示用に20件に制限
        'total_count': news_data.get('total_count', 0),
        'categories': news_data.get('categories', {}),
        'high_importance': report_data.get('summary', {}).get('high_importance', 0),
        'category_count': len(news_data.get('categories', {})),
        'top_keywords': report_data.get('summary', {}).get('top_keywords', [])[:5],
        'last_updated': datetime.now().strftime('%Y年%m月%d日 %H:%M'),
        'today_count': len([n for n in news_data.get('news', []) 
                           if n.get('published_date', '').startswith(datetime.now().strftime('%Y'))]),
    }
    
    return render_template('index.html', **context)

@app.route('/api/news')
def api_news():
    """ニュースAPI（JSON）"""
    news_data = news_app.load_news_data()
    return jsonify(news_data)

@app.route('/api/update')
def api_update():
    """手動更新API"""
    result = news_app.update_news()
    return jsonify(result)

@app.route('/health')
def health_check():
    """ヘルスチェック（Render用）"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "social-insurance-news"
    })

if __name__ == '__main__':
    # 開発環境
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Render環境（Gunicorn使用）
    application = app