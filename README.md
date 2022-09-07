Python flask 串接 GCP Cloud Storage、Firestore 小實作

# 在本地測試使用前提與流程
1. 更新 docker-compose.yml 的 Ngrok Ahth ID
至 https://ngrok.com/ 登入，複製 Your Authtoken 後貼上

2. 輸入指令 docker-compose up -d，起容器
```
docker-compose up -d

<!-- 輸入後查看容器狀況，預期要 4 個容器皆 up 狀態 -->
docker ps -a

```
# 在 Cloud She測試使用前提與流程
1. 已在該專案建立一個值區

2. 已在該專案啟用 Firestore 原生模式

3. 在 Cloud Shell 建立並進入虛擬環境、下載套件、設定環境變數、執行 app.py
```
python3 -m venv venv

source venv/bin/activate

python -m pip install --upgrade pip

pip3 install -r requirements.txt

export FLASK_ENV=production; export DEBUG=True; export BUCKET_NAME=<Bucket Name>

python app.py

```

4. 因在 Cloud Shell 測試，無法使用 Post 等，需添加 Ngrok 網址已用來測試
```
<!-- 在開一個終端機 -->

wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip

unzip ngrok-stable-linux-amd64.zip

sudo chmod u+x ngrok

./ngrok http --region ap  5000

<!-- 啟用後，複製網址，使用 POSTMAN 進行測試 -->
```

# 部署至 Cloud Run 
1. 已在該專案建立一個值區

2. 已在該專案啟用 Firestore 原生模式

3. 已建立 IAM 服務帳號，並賦予 Cloud Datastore 使用者、Storage 物件管理員

4. 將程式碼封裝成 image
```
<!-- 更新指令的專案 ID，至 Cloud Shell 執行-->
gcloud builds submit --tag gcr.io/<Project ID>/cloud-easy-app:0.0.1

<!-- 預期 build image 為 success -->
```

5. 至 Container Registry 確認映像，建立部署

部署至 Cloud Run，  
區域：台灣  
允許所有流量  
允許未經驗證的叫用  
選擇前面所建立的服務帳戶  
環境變數:  
DEBUG=False; FLASK_ENV=production; BUCKET_NAME=Bucket Name ID

建立