from flask import Flask

# 最簡單的 flask 展示
# 連結根路徑會跟你說 Hello, world

# 建立 Flask 物件
app = Flask(__name__)

# 定義根路由
@app.route('/')
def hello_world():
    return 'Hello, world'

if __name__ == '__main__':
    app.run(host='0.0.0.0')