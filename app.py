import os 
import json

# 此套件是用來處理生成器的
import itertools

from flask import Flask, jsonify, request
# 使用 emulator 時，需要引用這個套件的方法來用 
from google.auth.credentials import AnonymousCredentials
# GCP 的 Firestore、Cloud Storage API套件
from google.cloud import firestore
from google.cloud import storage

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


#創建一個 Flask 定義的物件，這是 Flask 的規則，透過這個物件，我們可以使用它的裝飾器與方法
app = Flask(__name__)

# 如果是開發階段
if os.environ["FLASK_ENV"] == "development":
    # 使用本地 docker 模擬器
    db = firestore.Client(project=os.environ['FIRESTORE_PROJECT_ID'], credentials=AnonymousCredentials())
    # 建立 Client
    storage_client = storage.Client(
            credentials=AnonymousCredentials(),
            project=os.environ['FIRESTORE_PROJECT_ID']
        )
# 如果是已經要發布的階段
elif os.environ["FLASK_ENV"] == "production":
    # 直接連 GCP 上面的 Firestore 和 Cloud Storage時，可以不帶參數，會自動偵測
    db = firestore.Client()
    storage_client = storage.Client()

# 定義 / 路徑，此路徑用來測試是否接通 Flask
@app.route('/')
def hello_world():
    return 'Hello, world'

# 定義 /users 路徑，GET 方法
@app.route('/users', methods=['GET'])
def get_users():
    """取得 Firestore 上 User 資料集的所有用戶資料
    """
    # 用戶的資料清單
    users_list = []

    # 與 Firestore 連結
    ref = db.collection(u'User')
    # 取出所有檔案的生成器 (generator)
    docs = ref.stream()

    # 檢查 docs 生成器是否為空
    try:
        first = next(docs)
        docs = itertools.chain([first], docs)
    except StopIteration:
        return {'message': 'No data in collection User of Firestore.'}
    

    # 使用 for 迴圈來疊代生成器
    for doc in docs:
        # 將所有檔案轉化成 dict
        user_dict = doc.to_dict()
        print(doc.to_dict())
        # 將 User 物件放到 user 的清單
        users_list.append(user_dict)
        print(users_list)

    # 回傳用戶 list
    return jsonify(users_list)

# 定義 /user 路徑，POST 方法
@app.route('/user', methods=['POST'])
def save_user():
    """將用戶資料上傳至 Firestore 資料庫儲存"""

    # 與 Firestore 連結
    ref = db.collection(u'User')

    # 將收到 request 取出 json 資料 
    user = request.get_json()
    print(user)
    if 'id' not in user:
        return {'message': '沒有收到用戶 id，請重新上傳！'}
    else:
    # 將收到 request json 上傳到 User 資料集，並以 'id' 欄位的值為文件名稱
        ref.document(u'{}'.format(user.get('id'))).set(user)
        # 回傳 OK
        return {'message': 'OK'}

# 定義 /users 路徑，POST 方法
@app.route('/users', methods=['POST'])
def save_users_json_to_cloud_storage():
    """將 Firestore 整理成 JSON 檔，儲存至 Cloud Storage"""

    # 先從 firestore 取出資料
    # 用戶的資料清單
    users_list = []

    # 與 Firestore 連結
    ref = db.collection(u'User')
    # 取出所有檔案的生成器 (generator)
    docs = ref.stream()

    # 使用 for 迴圈來疊代生成器
    for doc in docs:
        # 將所有檔案轉化成 dict
        user_dict = doc.to_dict()
        print(doc.to_dict())
        # 將 User 物件放到 user 的清單
        users_list.append(user_dict)
        print(users_list)
    
    # temp_path 為暫時要儲存的路徑，若為開發階段則儲存當前工作區域；若為生產階段則存到 cloud run 暫存空間
    if os.environ["FLASK_ENV"] == "development":
        temp_path = './user.json'
    elif os.environ["FLASK_ENV"] == "production":
        temp_path = '/tmp/user.json'
    
    # 將清單寫到 json 檔
    with open(temp_path, 'w', newline='') as jsonfile:
        jsonfile.write(json.dumps(users_list, ensure_ascii=False, indent=4))

    # 生成桶子，桶子(值區)名稱與 yml 檔建立的桶子名稱一致
    bucket = storage_client.bucket(bucket_name=os.environ['BUCKET_NAME'])
    # blob 是桶子的一個物件，第一個參數放入要存放值區的哪個路徑
    blob = bucket.blob(f"""users.json""")
    # 上傳
    blob.upload_from_filename(temp_path)
    # 上傳完後將本地資料刪除
    os.remove(temp_path)

    return {'message': 'Download to cloud storage bucket successfully.'}

# 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.environ['DEBUG'])