#!/bin/bash

# 作業ディレクトリの作成
rm -rf package
mkdir package
rm -f function.zip

# 必要なファイルのみをコピー
cp lambda/lambda_function.py package/
cp lambda/requirements.txt package/

# 依存関係のインストール（最小限の形で）
pip install -r lambda/requirements.txt -t package

cd package

# 不要なファイルの削除
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name "docs" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +


# ZIPファイルの作成
zip -r9 ../function.zip .

cd ..
rm -rf package

# サイズの確認
echo "Package size: $(du -h function.zip | cut -f1)"
