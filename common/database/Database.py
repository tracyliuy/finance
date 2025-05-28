from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

import os

# 创建基类
Base = declarative_base()

class Database:
    """数据库基类"""
    
    def __init__(self):
        """初始化数据库连接"""
        # 获取数据库配置
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', 'root')
        db_name = os.getenv('DB_NAME', 'gold_trading')
        
        # 创建数据库连接
        self.engine = create_engine(
            f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
            echo=False
        )
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """创建数据库表"""
        Base.metadata.create_all(self.engine)
        
    @contextmanager
    def get_session(self):
        """获取数据库会话"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def execute_transaction(self, func):
        """执行事务"""
        with self.get_session() as session:
            return func(session)
            
    def close_session(self, session):
        """关闭数据库连接"""
        if session:
            session.close()
        
    def execute_query(self, query):
        """执行查询"""
        session = self.get_session()
        try:
            result = session.execute(query)
            return result
        finally:
            self.close_session(session)
        
    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(self.engine) 