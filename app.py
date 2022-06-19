# 引用 Python 套件
import itertools
import json
import os 
from flask import Flask, jsonify, request, send_file
from google.auth.credentials import AnonymousCredentials
from google.cloud import firestore
from google.cloud import storage
from google.api_core.exceptions import NotFound

"""
用 Flask 建立一個一個簡易伺服器，透過 Flask 我們獲得一個類似總機的裝置，
Flask 內部會根據傳送進去 Flask 的 request 判別指向哪個路徑，
若該路徑有被設置，則會導引至該路徑的功能

邏輯：
    1. 創建一個 Flask 定義的物件 
    2. 根據設定好的環境變數，判斷是 development(開發中) 還是 production(生產階段) 
    3. 根據不同階段，設定 Firestore 物件與 Cloud Storage 物件
    4. 定義所需的路徑表，並且註明該路徑必須用什麼 http 方法
    5. 啟動 Flask 的條件式
"""

app = Flask(__name__)

if os.environ["FLASK_ENV"] == "development":
    db = firestore.Client(project=os.environ['FIRESTORE_PROJECT_ID'], credentials=AnonymousCredentials())
    storage_client = storage.Client(
            credentials=AnonymousCredentials(),
            project=os.environ['FIRESTORE_PROJECT_ID']
        )
elif os.environ["FLASK_ENV"] == "production":
    db = firestore.Client()
    storage_client = storage.Client()

@app.route('/')
def hello_world():
    return 'Hello, World'

@app.route('/users', methods=['GET'])
def get_users():
    """取得 Firestore 上 User 資料集的所有用戶資料
    """
    users_list = []

    ref = db.collection(u'User')
    docs = ref.stream()

    try:
        first = next(docs) 
        docs = itertools.chain([first], docs)
    except StopIteration:
        return {'message': 'No data in collection User of Firestore.'}
    
    for doc in docs:
        user_dict = doc.to_dict()
        print(doc.to_dict())
        users_list.append(user_dict)
        print(users_list)

    return jsonify(users_list)

@app.route('/user', methods=['POST'])
def save_user():
    """將用戶資料上傳至 Firestore 資料庫儲存"""

    ref = db.collection(u'User')

    user = request.get_json()
    print(user)
    if 'id' not in user:
        return {'message': '沒有收到用戶 id，請重新上傳！'}, 400
    else:
        ref.document(u'{}'.format(user.get('id'))).set(user)
        return {'message': 'OK'}

@app.route('/users', methods=['POST'])
def save_users_json_to_cloud_storage():
    """將 Firestore 整理成 JSON 檔，儲存至 Cloud Storage"""

    users_list = []

    ref = db.collection(u'User')
    docs = ref.stream()

    for doc in docs:
        user_dict = doc.to_dict()
        print(doc.to_dict())
        users_list.append(user_dict)
        print(users_list)
    
    if os.environ["FLASK_ENV"] == "development":
        temp_path = './user.json'
    elif os.environ["FLASK_ENV"] == "production":
        temp_path = '/tmp/user.json'
    
    with open(temp_path, 'w', newline='') as jsonfile:
        jsonfile.write(json.dumps(users_list, ensure_ascii=False, indent=4))

    bucket = storage_client.bucket(bucket_name=os.environ['BUCKET_NAME'])
    blob = bucket.blob(f"""users.json""")
    blob.upload_from_filename(temp_path)
    os.remove(temp_path)

    return {'message': 'Download to cloud storage bucket successfully.'}


@app.route('/file/<path:file_path>', methods=['GET'])
def file_to_from_storage(file_path):
    """將 file_path 傳入 file_to_from_storage 方法"""
    try:
        bucket = storage_client.bucket(os.environ['BUCKET_NAME'])
        blob = bucket.blob(file_path) # 需給該物件在值區裡面的 "路徑"，由於是練習，所以都放在根目錄，直接給檔案名稱即可
        blob.download_to_filename('/tmp/' + file_path)
        if os.path.exists('/tmp/' + file_path):
            return send_file('/tmp/' + file_path, as_attachment=True)
        else:
            return {"message": "File does not exist."}, 500
    except NotFound:
        return {"message": "File does not exist in Cloud Storage."}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.environ['DEBUG'])