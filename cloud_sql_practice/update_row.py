from  google.cloud.sql.connector  import  Connector,  IPTypes 
import  sqlalchemy
import pymysql
import os

"""
此 py 檔用來串接 Cloud SQL，
將特定值從 my_table 資料表中更新

"""

# 在本地串接 Cloud SQL 時，需設置 GOOGLE_APPLICATION_CREDENTIALS 環境變數
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./cloud-easy-app-cbbc8c934106.json" 
# 建立客戶端連接器，這是套件所規定的 # https://github.com/GoogleCloudPlatform/cloud-sql-python-connector
connector = Connector()

# function to return the database connection # 與 mysql 資料庫連接的方法
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

# create connection pool 創建連接池，並將方法放入連接池
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

# 更新 my_table 資料表中，
update_stmt = sqlalchemy.text("""
UPDATE my_table
SET title='Pineapple One'
WHERE id='apple';
""")

# 用資料池連接
with pool.connect() as db_conn:

    # 實行 sql 語句
    db_conn.execute(update_stmt)

    # query database 查詢資料表的所有值
    result = db_conn.execute("SELECT * From my_table").fetchall()

    # Do something with the results
    for row in result:
        print(row)
# 關閉連接器
connector.close()