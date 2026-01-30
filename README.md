# Simple Survey System

Python (Flask) と SQLite を使用した、シンプルなアンケート管理システムです。

## 機能
- **アンケート一覧表示**: 公開中のアンケートを表示します。
- **アンケート回答**: 選択肢形式での回答が可能です。
- **リアルタイム集計**: 回答後、即座に集計結果をグラフやリストで確認できます。

## セットアップ
1. ライブラリのインストール:
   ```bash
   pip install flask flask-sqlalchemy
2. アプリケーションの起動:
    python app.py
3. ブラウザで http://123.0.0.1:5000 にアクセスしてください。

## データベース構造
本プロジェクトでは SQLite を使用しており、以下の5つのテーブルでリレーションを管理しています。

User, Survey, Question, Choice, Answer