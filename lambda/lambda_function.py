import json
import boto3
import psycopg2

def get_secret():
    """SecretsManagerから接続情報を取得"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        endpoint_url='http://localstack:4566'  # LocalStackのエンドポイント
    )

    try:
        secret_value = client.get_secret_value(SecretId='dev/postgres/credentials')
        secret = json.loads(secret_value['SecretString'])
        print ("SecretsManagerから取得した接続情報: ", secret)
        return secret
    except Exception as e:
        raise Exception(f"Failed to get secret: {str(e)}")

def get_db_connection():
    """データベース接続を取得"""
    # SecretsManagerから接続情報を取得
    secret = get_secret()

    return psycopg2.connect(
        host=secret['host'],
        database=secret['dbname'],
        user=secret['username'],
        password=secret['password']
    )

def handler(event, context):
    """
    Lambda handler for PostgreSQL operations
    """
    try:
        # データベースに接続
        conn = get_db_connection()
        cur = conn.cursor()

        # テストクエリの実行
        cur.execute("SELECT current_timestamp;")
        timestamp = cur.fetchone()[0]

        # 接続のクリーンアップ
        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully connected to PostgreSQL',
                'timestamp': str(timestamp)
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }