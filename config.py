from dotenv import load_dotenv
import os
import pymysql
load_dotenv()

pymysql.install_as_MySQLdb()
user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]
host = os.environ["MYSQL_HOST"]
database = os.environ["MYSQL_DATABASE"]

DATABASE_CONNECTION_URI = f'mysql+pymysql://{user}:{password}@{host}:3306/{database}'
print(DATABASE_CONNECTION_URI)
