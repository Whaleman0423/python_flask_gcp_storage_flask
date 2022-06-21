from google.cloud.sql.connector  import  Connector,  IPTypes 
import sqlalchemy
import pymysql
import os

"""
此 py 檔用來串接 Cloud SQL，
建立 my_table 資料表的功能

"""

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./cloud-easy-app-cbbc8c934106.json" 
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

create_stmt = sqlalchemy.text("""
CREATE TABLE my_table (
    id varchar(255),
    title varchar(255)
);
""")

with pool.connect() as db_conn:

    # db_conn.execute(create_stmt)

    result = db_conn.execute("SELECT * From my_table").fetchall()
    print(result)
    for row in result:
        print(row)
connector.close()