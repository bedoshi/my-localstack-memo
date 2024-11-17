import boto3
import json
import psycopg2
from psycopg2.extras import RealDictCursor

def get_secret():
    session = boto3.session.Session()
    # region_name を明示的に指定
    client = session.client(
        service_name='secretsmanager',
        endpoint_url='http://localhost:4566',
        region_name='ap-northeast-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

    secret = client.get_secret_value(SecretId='dev/postgres/credentials')
    return json.loads(secret['SecretString'])

def connect_to_db():
    secret = get_secret()

    conn = psycopg2.connect(
        dbname=secret['dbname'],
        user=secret['username'],
        password=secret['password'],
        host=secret['host'],
        port=secret['port']
    )
    return conn

def test_connection():
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # テストテーブルの作成
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # テストデータの挿入
        cur.execute("""
            INSERT INTO test_table (name) VALUES
            ('Test 1'),
            ('Test 2')
        """)

        # データの確認
        cur.execute("SELECT * FROM test_table")
        rows = cur.fetchall()
        for row in rows:
            print(row)

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == '__main__':
    test_connection()