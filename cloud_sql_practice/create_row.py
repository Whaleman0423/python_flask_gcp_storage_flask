from  google.cloud.sql.connector  import  Connector,  IPTypes 
import  sqlalchemy
import pymysql
import os

"""
此 py 檔用來串接 Cloud SQL，
將值插入 my_table 資料表

"""

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./cloud-easy-app-cbbc8c934106.json" 
# https://github.com/GoogleCloudPlatform/cloud-sql-python-connector
connector = Connector()

def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "cloud-easy-app:asia-east1:easy-mysql-practice",  # "project:region:instance"
        "pymysql",
        user="root", # 資料庫用戶名稱
        password="123456789", # 資料庫用戶密碼
        db="mydb", # 資料庫名稱
        enable_iam_auth=True, # 啟用 IAM 驗證
    )
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

insert_stmt = sqlalchemy.text(
    "INSERT INTO my_table (id, title) VALUES (:id, :title)",
)

# 用資料池連接
with pool.connect() as db_conn:

    db_conn.execute(insert_stmt, id="apple", title="Apple One")

    result = db_conn.execute("SELECT * From my_table").fetchall()

    for row in result:
        print(row)
connector.close()