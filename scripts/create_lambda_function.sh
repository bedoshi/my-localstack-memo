# 一旦固定関数名で実行するスクリプトとして作成
awslocal lambda create-function \
  --function-name hello-lambda \
  --runtime python3.11 \
  --handler lambda_function.handler \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --zip-file fileb://function.zip

awslocal lambda get-function --function-name hello-lambda

echo "Done."

