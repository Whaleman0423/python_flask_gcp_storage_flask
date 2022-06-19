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
        url = 'http://localhost:5000/'

        response = requests.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(b'Hello, World', response.content)

    def test_get_users(self):
        url = 'http://localhost:5000/users'

        response = requests.get(url)
        
        self.assertEqual(200, response.status_code)

    def test_save_user(self):
        url = 'http://localhost:5000/user'

        user_dict = {
            "id": "0",
            "user_name": "Amy",
            "user_sex": "man",
            "user_age": 27,
            "user_phone": "0800-080-080"
        }

        response = requests.post(url, json=user_dict)
        self.assertEqual(200, response.status_code)

        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual('OK', response_dict["message"])

        url = 'http://localhost:5000/users'

        response = requests.get(url)
        self.assertEqual(200, response.status_code)

        response_dict = json.loads(response.content.decode('utf-8'))[0]

        self.assertEqual("0", response_dict.get("id"))
        self.assertEqual("Amy", response_dict.get("user_name"))
        self.assertEqual("man", response_dict.get("user_sex"))
        self.assertEqual(27, response_dict.get("user_age"))
        self.assertEqual("0800-080-080", response_dict.get("user_phone"))

        url = 'http://localhost:5000/user'

        user_dict = {
            "user_name": "Jack",
            "user_sex": "woman",
            "user_age": 18,
            "user_phone": "0900-123-123"
        }

        response = requests.post(url, json=user_dict)
        self.assertEqual(400, response.status_code)

        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual('沒有收到用戶 id，請重新上傳！', response_dict["message"])

    def test_save_users_json_to_cloud_storage(self):
        url = "http://localhost:5000/users"

        response = requests.post(url)
        response_dict = json.loads(response.content.decode('utf-8'))

        self.assertEqual("Download to cloud storage bucket successfully.", response_dict["message"])

    def test_file_to_from_storage(self):
        url = 'http://localhost:5000/file/users.json'

        response = requests.get(url)
        self.assertEqual(200, response.status_code)

        url = 'http://localhost:5000/file/abc.png'

        response = requests.get(url)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(404, response.status_code)
        self.assertEqual("File does not exist in Cloud Storage.", response_dict["message"])
        