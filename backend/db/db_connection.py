import mysql.connector
from mysql.connector import Error
import json
import os

class DatabaseConnection:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()
        self.test_db = None
        self.prod_db = None
        self.test_cursor = None
        self.prod_cursor = None
    
    def load_config(self):
        """加载配置文件"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def connect_test_db(self):
        """连接到测试数据库"""
        try:
            db_config = self.config['database']['test']
            self.test_db = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                charset='utf8mb4'
            )
            self.test_cursor = self.test_db.cursor(dictionary=True)
            print(f"成功连接到测试数据库: {db_config['database']}")
            return True
        except Error as e:
            print(f"连接测试数据库失败: {e}")
            return False
    
    def connect_prod_db(self):
        """连接到生产数据库"""
        try:
            db_config = self.config['database']['production']
            self.prod_db = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                charset='utf8mb4'
            )
            self.prod_cursor = self.prod_db.cursor(dictionary=True)
            print(f"成功连接到生产数据库: {db_config['database']}")
            return True
        except Error as e:
            print(f"连接生产数据库失败: {e}")
            return False
    
    def disconnect_test_db(self):
        """断开测试数据库连接"""
        if self.test_cursor:
            self.test_cursor.close()
        if self.test_db and self.test_db.is_connected():
            self.test_db.close()
            print("测试数据库连接已关闭")
    
    def disconnect_prod_db(self):
        """断开生产数据库连接"""
        if self.prod_cursor:
            self.prod_cursor.close()
        if self.prod_db and self.prod_db.is_connected():
            self.prod_db.close()
            print("生产数据库连接已关闭")
    
    def execute_query(self, cursor, query, params=None):
        """执行SQL查询"""
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return True
        except Error as e:
            print(f"执行查询失败: {e}")
            print(f"查询语句: {query}")
            return False
    
    def fetch_all(self, cursor):
        """获取所有查询结果"""
        return cursor.fetchall()
    
    def fetch_one(self, cursor):
        """获取单个查询结果"""
        return cursor.fetchone()
    
    def commit(self, db):
        """提交事务"""
        try:
            db.commit()
            return True
        except Error as e:
            print(f"提交事务失败: {e}")
            return False
    
    def rollback(self, db):
        """回滚事务"""
        try:
            db.rollback()
            return True
        except Error as e:
            print(f"回滚事务失败: {e}")
            return False