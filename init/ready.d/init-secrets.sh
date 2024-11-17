#!/bin/bash

export AWS_DEFAULT_REGION="ap-northeast-1"

echo "Initializing Secrets Manager..."

# シークレットが既に存在するか確認
SECRET_EXISTS=$(awslocal secretsmanager list-secrets --query "SecretList[?Name=='dev/postgres/credentials'].Name" --output text)

if [ -z "$SECRET_EXISTS" ]; then
    # シークレットが存在しない場合は作成
    awslocal secretsmanager create-secret \
        --name "dev/postgres/credentials" \
        --secret-string "$(cat /etc/localstack/init/secrets.json)"
    echo "Secret created successfully"
else
    echo "Secret already exists"
fi
