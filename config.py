"""
Render版 社会保険ニュースサイト設定
"""

import os
from datetime import timedelta

class Config:
    """基本設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Flask設定
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # タイムゾーン
    TIMEZONE = 'Asia/Tokyo'
    
    # データファイルパス
    DATA_DIR = 'data'
    PROCESSED_NEWS_FILE = os.path.join(DATA_DIR, 'processed_news.json')
    DAILY_REPORT_FILE = os.path.join(DATA_DIR, 'daily_report.json')
    
    # 外部API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # 広告設定
    I_MOBILE_SITE_ID = os.environ.get('I_MOBILE_SITE_ID')
    I_MOBILE_AD_SPOTS = {
        'header': os.environ.get('I_MOBILE_HEADER_SPOT'),
        'middle': os.environ.get('I_MOBILE_MIDDLE_SPOT'),
        'footer': os.environ.get('I_MOBILE_FOOTER_SPOT')
    }
    
    ZUCKS_SITE_ID = os.environ.get('ZUCKS_SITE_ID')
    ZUCKS_AD_SPOTS = {
        'header': os.environ.get('ZUCKS_HEADER_SPOT'),
        'middle': os.environ.get('ZUCKS_MIDDLE_SPOT'),
        'footer': os.environ.get('ZUCKS_FOOTER_SPOT')
    }
    
    # スクレイピング設定
    REQUEST_TIMEOUT = 30
    REQUEST_DELAY = 2  # 秒
    MAX_NEWS_PER_SOURCE = 20
    
    # キャッシュ設定
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 3600  # 1時間

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """本番環境設定（Render）"""
    DEBUG = False
    TESTING = False
    
    # セキュリティ
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # データベース（PostgreSQL）
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Redis（キャッシュ）
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # 監視
    SENTRY_DSN = os.environ.get('SENTRY_DSN')

# 環境別設定マッピング
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}