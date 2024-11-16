# my-localstack-memo
Windows上にlocalstack環境を作ってみる自己学習用のメモ。
試した手順とかを色々まとめていく予定。

## localstackのインストール
ここのqiitaを参考にした。
- [Dockerを知らなくてもWindowsでLocalStackしたい！ - Qiita](https://qiita.com/LightSilver7/items/fdfb3602c19aeb68f493)

Pythonは3.11.9でインストール済み、DockerはRancher Desktopでインストール済み。<br>
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
