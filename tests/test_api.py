import unittest
from urllib import response
import requests
import json

"""
用來測試 app.py 的 API
執行:python -m unittest tests/test_api.py
"""

class TestApp(unittest.TestCase):

    def test_hello_world(self):
        # 測試 GET "/" 
        url = 'http://localhost:5000/'

        # 發送 request 並將放入回應變數
        response = requests.get(url)

        # 若 response http 狀態碼為 200 則不會出錯 
        self.assertEqual(200, response.status_code)
        self.assertEqual(b'Hello, World', response.content)

    def test_get_users(self):
        # 測試 GET "/users"
        url = 'http://localhost:5000/users'

        # 發送 request 並將放入回應變數
        response = requests.get(url)
        
        # 若 response http 狀態碼為 200 則不會出錯 
        self.assertEqual(200, response.status_code)
        # 在還沒匯入任何資料前，應當匯回傳 {'message': 'No data in collection User of Firestore.'}
        # 若已經匯入過，就把它註解掉不測
        # self.assertEqual('No data in collection User of Firestore.', json.loads(response.content.decode('utf-8'))["message"])

    def test_save_user(self):
        # 測試 POST "/user"
        url = 'http://localhost:5000/user'

        # 定義一個要 post 的假用戶資料 dict
        user_dict = {
            "id": "0",
            "user_name": "Amy",
            "user_sex": "man",
            "user_age": 27,
            "user_phone": "0800-080-080"
        }

        # 發送 request 並將放入回應變數
        response = requests.post(url, json=user_dict)
        # 若 response http 狀態碼為 200 則不會出錯 
        self.assertEqual(200, response.status_code)

        # print(json.loads(response.content.decode('utf-8')))
        # 取出獲得的 response 內容
        response_dict = json.loads(response.content.decode('utf-8'))
        # 驗證是否為 'OK'
        self.assertEqual('OK', response_dict["message"])

        # 這邊驗證一下是否真的有被寫入，並順道測試 GET '/users'
        url = 'http://localhost:5000/users'

        # 發送 request 並將放入回應變數
        response = requests.get(url)
        # 若 response http 狀態碼為 200 則不會出錯 
        self.assertEqual(200, response.status_code)

        # 取出獲得的 response 內容，會是一個清單，取出第一筆
        response_dict = json.loads(response.content.decode('utf-8'))[0]

        # 查看第一筆的字典是否為我們匯進去的
        self.assertEqual("0", response_dict.get("id"))
        self.assertEqual("Amy", response_dict.get("user_name"))
        self.assertEqual("man", response_dict.get("user_sex"))
        self.assertEqual(27, response_dict.get("user_age"))
        self.assertEqual("0800-080-080", response_dict.get("user_phone"))

        # 測試如果沒有匯入內含  id 資料的 json
        url = 'http://localhost:5000/user'

        # 定義一個要 post 的假用戶資料 dict
        user_dict = {
            "user_name": "Jack",
            "user_sex": "woman",
            "user_age": 18,
            "user_phone": "0900-123-123"
        }

        # 發送 request 並將放入回應變數
        response = requests.post(url, json=user_dict)
        # 若 response http 狀態碼為 200 則不會出錯 
        self.assertEqual(400, response.status_code)

        # print(json.loads(response.content.decode('utf-8')))
        # 取出獲得的 response 內容
        response_dict = json.loads(response.content.decode('utf-8'))
        # 驗證是否為 'OK'
        self.assertEqual('沒有收到用戶 id，請重新上傳！', response_dict["message"])

    def test_save_users_json_to_cloud_storage(self):
        # 測試 POST /users
        url = "http://localhost:5000/users"

        # 發送 request 並將放入回應變數
        response = requests.post(url)
        # 取出獲得的 response 內容
        response_dict = json.loads(response.content.decode('utf-8'))

        # 驗證 response 內容
        self.assertEqual("Download to cloud storage bucket successfully.", response_dict["message"])

    def test_file_to_from_storage(self):
        # 測試 GET /file/<path:file_path>
        url = 'http://localhost:5000/file/users.json'

        # 發送 request 並將放入回應變數
        response = requests.get(url)
        # 若 response http 狀態碼為 200 則不會出錯 
        self.assertEqual(200, response.status_code)

        # 測試不存在於值區內的物件請求
        url = 'http://localhost:5000/file/abc.png'

        # 發送 request 並將放入回應變數
        response = requests.get(url)
        # 取出獲得的 response 內容
        response_dict = json.loads(response.content.decode('utf-8'))
        # 若不存在，則獲得狀態碼 404
        self.assertEqual(404, response.status_code)
        self.assertEqual("File does not exist in Cloud Storage.", response_dict["message"])
        