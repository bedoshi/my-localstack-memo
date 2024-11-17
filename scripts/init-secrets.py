#!/usr/bin/env python
import boto3
import json

secret_string = {
    "username": "postgres",
    "password": "postgres",
    "engine": "postgres",
    "host": "postgres",
    "port": 5432,
    "dbname": "testdb"
}

def init_secrets():
    session = boto3.session.Session()
    client = boto3.client(
        'secretsmanager',
        endpoint_url='http://localhost:4566',
        region_name='ap-northeast-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

    try:
        client.create_secret(
            Name='dev/postgres/credentials',
            SecretString=json.dumps(secret_string)
        )
        print("Secret created successfully")
    except Exception as e:
        print(f"Error creating secret: {e}")

if __name__ == "__main__":
    init_secrets()