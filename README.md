# my-localstack-memo
Windows上にlocalstack環境を作ってみる自己学習用のメモ。
試した手順とかを色々まとめていく予定。

2024/11/18追記
- powershell上で操作するコマンドでチャレンジしてみたけど、SecretsManager上にsecretを登録する際に `{` のみになる問題を確認ずみ。
  - wsl(ubunts 22.04.5)から実行すると問題なく登録できることを確認。
- 一旦コマンドやらをwslで実行できるように変更する予定。

## 前提環境
|項目名|バージョン等|
|---|---|
|OS|Windows11 22631.4460|
|Rancher Desktop|1.16.0|
|Docker|27.2.1-rd, build cc0ee3e|
|Python|3.11.9|

DockerはRancherDesktop経由でインストール。

## 依存ライブラリのインストール
以降の説明に出てきそうなやつを一旦まとめたのが `requirements.txt` 。
```
pip install -r requirements.txt
```

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
$env:AWS_DEFAULT_REGION = "ap-northeast-1"
# WSLで実行する場合はこちら
export AWS_DEFAULT_REGION="ap-northeast-1"

# AWS CLIの設定
aws configure set region ap-northeast-1 --profile localstack
aws configure set aws_access_key_id test --profile localstack
aws configure set aws_secret_access_key test --profile localstack
```

DB接続情報のためにsecret managerを使う。

```powershell
# 登録前のsecretsの存在を確認
awslocal --endpoint-url=http://localhost:4566 secretsmanager list-secrets

awslocal --endpoint-url=http://localhost:4566 secretsmanager create-secret `
    --name "dev/postgres/credentials"  `
    --secret-string (Get-Content -Path ".\secrets.json" -Raw)

# WSL上で実行する場合はこちら
awslocal --endpoint-url=http://localhost:4566 secretsmanager create-secret \
    --name "dev/postgres/credentials" \
    --secret-string "$(cat secrets.json)"
```
登録された情報を確認する。
```powershell
# 登録された情報の確認
awslocal --endpoint-url=http://localhost:4566 secretsmanager list-secrets
```
こんな感じ。
```json
{
    "SecretList": [
        {
            "ARN": "arn:aws:secretsmanager:ap-northeast-1:000000000000:secret:dev/postgres/credentials-maLkvY",
            "Name": "dev/postgres/credentials",
            "LastChangedDate": "2024-11-17T20:44:02.306553+09:00",
            "SecretVersionsToStages": {
                "a8ba0869-3825-4370-b13c-16f73bccda2f": [
                    "AWSCURRENT"
                ]
            },
            "CreatedDate": "2024-11-17T20:44:02.306553+09:00"
        }
    ]
}
```

登録したsecretを直接参照する時はこちら。
```powershell
awslocal secretsmanager get-secret-value --secret-id dev/postgres/credentials

# jqがある場合はこれで見ることも可能
awslocal secretsmanager get-secret-value --secret-id dev/postgres/credentials | jq -r .SecretString
```

WSL上で実行すると問題なく結果が取得できる。
```
{
    "username": "postgres",
    "password": "postgres",
    "engine": "postgres",
    "host": "postgres",
    "port": 5432,
    "dbname": "testdb"
}
```

期待される結果はこちら。
```
 my-localstack-memo  python connecting-db.py
RealDictRow([('id', 1), ('name', 'Test 1'), ('created_at', datetime.datetime(2024, 11, 23, 18, 17, 1, 412438))])
RealDictRow([('id', 2), ('name', 'Test 2'), ('created_at', datetime.datetime(2024, 11, 23, 18, 17, 1, 412438))])
```

登録した情報を消したいときはこちら。ただ `docker-compose down` して再度 `docker-compose up -d` し直しても登録したsecretをなかった状態にできる。

```powershell
awslocal secretsmanager delete-secret `
    --secret-id "dev/postgres/credentials" `
    --force-delete-without-recovery
```

もしかすると `scripts/init-secrets.py` にて登録を自動でやってしまうことも可能かも。ローカルテスト環境を作るときにはそういうのが良いかもしれない。

DB接続情報がSecretsManager上に保存できたら `connecting-db.py` で接続を確認する。
```bash
# WSL上で実行する
python connecting-db.py
```

一旦ここまでのDB接続情報の登録は `init/ready.d/init-secrets.sh` で書いたため、 `docker-compose up -d` のタイミングで実行される。

## Lambda関数のセットアップとデプロイ
- デプロイパッケージの作成
```
# 依存関係のインストール
pip install -r requirements.txt -t ./lambda/dependencies

# ZIP パッケージの作成
zip -r function.zip ./lambda/dependencies
```

- Lambda関数の作成
```
awslocal lambda create-function \
  --function-name hello-lambda \
  --runtime python3.11 \
  --handler lambda_function.handler \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --zip-file fileb://function.zip
```

- lambda関数の一覧と状態確認
```
awslocal lambda list-functions

# 特定の関数の詳細確認
awslocal lambda get-function --function-name hello-lambda
```
- lambda関数の実行
```
awslocal lambda invoke \
  --function-name hello-lambda \
  --payload '{"key": "value"}' \
  output.json
```
期待されるレスポンスはこんな感じ。
```
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
```

ただこれをposgresqlに接続する形に変更するため、期待されるレスポンスが変わる。

一旦lambda関数をlocalstackにデプロイするためのスクリプトを用意した。
- `scripts/create_deployment_package.sh`
- `scripts/create_lambda_function.sh`

一応上の順番に沿って実行すればlocalstackにデプロイされる。
