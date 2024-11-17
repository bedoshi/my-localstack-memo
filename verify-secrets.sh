#!/bin/bash

# シークレットの一覧を表示
echo "Listing secrets..."
awslocal secretsmanager list-secrets

# 特定のシークレットの内容を表示
echo "Getting secret value..."
awslocal secretsmanager get-secret-value --secret-id dev/postgres/credentials
