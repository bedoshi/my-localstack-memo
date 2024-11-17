# my-localstack-memo
Windows上にlocalstack環境を作ってみる自己学習用のメモ。
試した手順とかを色々まとめていく予定。

## 前提環境
|項目名|バージョン等|
|---|---|
|OS|Windows11 22631.4460|
|Rancher Desktop|1.16.0|
|Docker|27.2.1-rd, build cc0ee3e|
|Python|3.11.9|

DockerはRancherDesktop経由でインストール。

## localstackのインストール
ここのqiitaを参考にした。
- [Dockerを知らなくてもWindowsでLocalStackしたい！ - Qiita](https://qiita.com/LightSilver7/items/fdfb3602c19aeb68f493)

ただwsl使わなくてWindows上で作りたかった都合から、powershell上で下記のコマンドを実行した。
```
pip install localstack
pip install awscli-local
docker pull localstack/localstack
localstack start -d
localstack status services
awslocal ec2 describe-vpcs
localstack stop
```
途中で下記のパス（一部ぼかし）がpathに追加されてません、というメッセージが出てたのでユーザ環境変数に追加した。これしないと `localstack` コマンドを実行できなかった。
```
C:\Users\xxxxx\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_xxxxxxxxxxxx\LocalCache\local-packages\Python311\Scripts
```

ただこれについても前述のQiitaを読み進めれば書いてあった。

## AWSサービスの使用例
### S3バケットの操作
```
# バケットの作成
awslocal s3 mb s3://my-test-bucket

# ファイルのアップロード
echo "Hello LocalStack" > test.txt
awslocal s3 cp test.txt s3://my-test-bucket/

# バケット内のファイル一覧表示
awslocal s3 ls s3://my-test-bucket/
```

## LocalStack + PostgreSQLでの環境開発構築
RDS for PostgreSQLをlocalstack上でエミュレートするには無料じゃ無理なためLocalStackとPostgreSQLを含むdocker-compose.ymlで頑張る。
```
# 一旦起動中のコンテナを止める
localstack stop

# Dockerのプロセスを確認し、残っているものがあれば停止
docker ps
docker stop $(docker ps -q)

# 環境の起動
docker-compose up -d

# ステータスの確認
docker-compose ps
```

localstackで使うAWSのリージョンを設定する。

```
# PowerShellで環境変数を設定
$env:AWS_DEFAULT_REGION = "us-east-1"

# AWS CLIの設定
aws configure set region us-east-1 --profile localstack
aws configure set aws_access_key_id test --profile localstack
aws configure set aws_secret_access_key test --profile localstack
```

DB接続情報のためにsecret managerを使う。

```powershell
awslocal secretsmanager create-secret `
    --name "dev/postgres/credentials"  `
    --secret-string (Get-Content -Path ".\secrets.json" -Raw)
```