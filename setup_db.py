import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def initialize_database():
    try:
        # 创建数据库连接（使用系统root权限）
        admin_conn = pymysql.connect(
            host='localhost',
            user='root',
            password=os.getenv('MYSQL_ROOT_PASSWORD'),  # 从环境变量获取
            charset='utf8mb4'
        )

        with admin_conn.cursor() as cursor:
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS TravelHub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            
            # 创建应用专用用户（安全实践）
            cursor.execute(
                "CREATE USER IF NOT EXISTS 'travel_user'@'%' IDENTIFIED BY %s;",
                (os.getenv('MYSQL_USER_PASSWORD'),)
            )
            
            # 授予权限
            cursor.execute(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON TravelHub.* TO 'travel_user'@'%';"
            )
            
            # 刷新权限
            cursor.execute("FLUSH PRIVILEGES;")

        admin_conn.commit()
        print("✅ 数据库初始化成功")

    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
    finally:
        if admin_conn:
            admin_conn.close()

if __name__ == "__main__":
    initialize_database()