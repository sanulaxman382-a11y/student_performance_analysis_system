import os
class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "yeshu@3106")
    MYSQL_DB = os.getenv("MYSQL_DB", "student_performance")
    MYSQL_CURSORCLASS = "DictCursor"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
