# 🏛️ 社会保険ニュース - Render版（スマホ特化）

社会保険に関する最新ニュースを自動収集・要約してお届けするスマホ特化サイト。i-mobile/Zucks広告対応。

## 🚀 特徴

### 📱 スマホ最適化
- **レスポンシブデザイン**: iPhone/Android完全対応
- **タッチ操作最適化**: スムーズなスクロール・タップ
- **PWA対応**: ホーム画面追加・オフライン表示
- **軽量設計**: 高速読み込み

### 💰 収益化
- **i-mobile広告**: スマホ特化の高収益広告
- **Zucks広告**: ネイティブ広告対応
- **戦略的配置**: ヘッダー・中間・フッター
- **UX配慮**: 広告とコンテンツの調和

### 🤖 自動化
- **毎朝4時更新**: Render Cron Jobs
- **多源スクレイピング**: 厚労省・Yahoo!ニュース
- **AI要約**: 重要度・カテゴリ自動判定
- **重複除去**: 高品質なニュース提供

## 🏗️ 技術構成

### バックエンド
- **Flask**: 軽量Webフレームワーク
- **Gunicorn**: WSGI サーバー
- **PostgreSQL**: データ永続化（無料プラン）
- **Redis**: キャッシュ・セッション管理

### フロントエンド
- **バニラJS**: 軽量・高速
- **CSS Grid/Flexbox**: モダンレイアウト
- **Service Worker**: PWA・キャッシュ
- **Touch Events**: スマホ操作最適化

### インフラ
- **Render**: ホスティング・自動デプロイ
- **Cron Jobs**: 定期実行（毎朝4時）
- **GitHub**: ソースコード管理
- **Environment Variables**: 設定管理

## 📁 ディレクトリ構造

```
render-social-insurance-news/
├── app.py                    # メインアプリケーション
├── config.py                 # 設定ファイル
├── requirements.txt          # Python依存関係
├── render.yaml              # Render設定
├── README.md                # このファイル
├── templates/               # Flaskテンプレート
│   └── index.html          # メインページ
├── static/                  # 静的ファイル
│   ├── manifest.json       # PWAマニフェスト
│   └── sw.js               # Service Worker
├── scripts/                 # 自動化スクリプト
│   └── main_automation.py  # ニュース収集・処理
└── data/                    # データファイル
    ├── processed_news.json  # 処理済みニュース
    └── daily_report.json    # 日次レポート
```

## 🔧 デプロイ手順

### 1. Renderアカウント準備
```bash
# Render.comでアカウント作成
# GitHubリポジトリ連携
```

### 2. 環境変数設定
```bash
# Renderダッシュボードで設定
OPENAI_API_KEY=your_openai_key
I_MOBILE_SITE_ID=your_i_mobile_id
ZUCKS_SITE_ID=your_zucks_id
FLASK_ENV=production
TZ=Asia/Tokyo
```

### 3. 自動デプロイ
```bash
git push origin main
# Render自動デプロイ実行
```

### 4. 広告設定
```javascript
// 広告コード実装
// i-mobile スクリプト追加
// Zucks 広告ユニット設定
```

## 📊 運用・監視

### 自動更新
- **実行時間**: 毎朝4:00 JST
- **処理時間**: 約3-5分
- **データ保持**: 最新100件

### パフォーマンス
- **応答時間**: < 500ms
- **Lighthouse**: 90+ スコア
- **モバイル最適化**: 完全対応

### 監視項目
- **ヘルスチェック**: `/health`
- **エラーログ**: Render Console
- **アクセス解析**: Google Analytics

## 💡 広告最適化Tips

### i-mobile
```html
<!-- レスポンシブバナー推奨 -->
<script>
  // 320x50 (ヘッダー)
  // 320x100 (中間)
  // 320x50 (フッター)
</script>
```

### Zucks
```html
<!-- ネイティブ広告推奨 -->
<script>
  // インフィード型
  // レコメンド型
</script>
```

## 🔒 セキュリティ

- **HTTPS**: 強制リダイレクト
- **CSP**: Content Security Policy
- **Rate Limiting**: スクレイピング制御
- **環境変数**: 機密情報保護

## 📈 拡張計画

### Phase 1: 基本機能
- [x] ニュース自動収集
- [x] スマホ最適化UI
- [x] 広告統合準備

### Phase 2: 機能強化
- [ ] プッシュ通知
- [ ] ユーザー設定
- [ ] 検索機能

### Phase 3: 収益向上
- [ ] A/Bテスト
- [ ] 広告最適化
- [ ] アフィリエイト

## 🆘 トラブルシューティング

### よくある問題

**Q: ニュースが更新されない**
```bash
# Cron Job ログ確認
# Render Console > Cron Jobs
```

**Q: 広告が表示されない**
```javascript
// ブラウザConsoleでエラー確認
console.log('広告読み込み状況');
```

**Q: スマホで表示が崩れる**
```css
/* Viewport設定確認 */
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

## 📞 サポート

- **Repository**: [GitHub](https://github.com/your-repo)
- **Issues**: バグ報告・機能要望
- **Discussions**: 質問・相談

---

🏛️ **社会保険ニュース - Render版** | Powered by Flask + Render | © 2025