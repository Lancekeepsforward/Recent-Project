import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mysql_connection():
    print("Testing MySQL Connection...")
    print("="*50)
    
    # Get credentials
    root_user = os.getenv('MYSQL_ROOT_USER')
    root_password = os.getenv('MYSQL_ROOT_PASSWORD')
    
    print(f"Root User: {root_user}")
    print(f"Root Password: {'*' * len(root_password) if root_password else 'None'}")
    print("="*50)
    
    try:
        # Try to connect
        print("\nAttempting to connect to MySQL...")
        conn = pymysql.connect(
            host='localhost',
            user=root_user,
            password=root_password,
            charset='utf8mb4'
        )
        print("Successfully connected to MySQL!")
        
        with conn.cursor() as cursor:
            # Check MySQL version
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"\nMySQL Version: {version[0]}")
            
            # Check current user
            cursor.execute("SELECT CURRENT_USER()")
            current_user = cursor.fetchone()
            print(f"Current User: {current_user[0]}")
            
            # Check privileges
            print("\nChecking privileges...")
            cursor.execute("SHOW GRANTS")
            grants = cursor.fetchall()
            print("Current privileges:")
            for grant in grants:
                print(f"- {grant[0]}")
            
            # Try to create a test database
            print("\nTesting database creation...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
            print("Successfully created test database")
            
            # Try to create a test user
            print("\nTesting user creation...")
            test_user = "test_user"
            test_password = "test_password"
            
            try:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{test_user}'@'localhost' IDENTIFIED BY '{test_password}'")
                print("Successfully created test user")
                
                cursor.execute(f"GRANT ALL PRIVILEGES ON test_db.* TO '{test_user}'@'localhost'")
                print("Successfully granted privileges to test user")
                
                cursor.execute("FLUSH PRIVILEGES")
                print("Successfully flushed privileges")
            except pymysql.Error as e:
                print(f"Error during user operations: {str(e)}")
                print("This indicates a permissions issue with the root user")
            
            # Clean up
            print("\nCleaning up...")
            cursor.execute("DROP DATABASE IF EXISTS test_db")
            cursor.execute(f"DROP USER IF EXISTS '{test_user}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print("Cleanup completed")
            
    except pymysql.Error as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure MySQL server is running")
        print("2. Verify your root credentials in .env file")
        print("3. Try connecting manually with: mysql -u root -p")
        print("4. Check if you can create users with: SHOW GRANTS FOR CURRENT_USER;")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nConnection closed")

if __name__ == "__main__":
    test_mysql_connection() 