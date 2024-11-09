from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session

class SQLiteClient:
    """SQLite客户端"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not SQLiteClient._initialized:
            # 创建引擎
            self.engine = create_engine(
                "sqlite:///.data/chat.db",
                connect_args={"check_same_thread": False},
                echo=False  # 设置为True可以看到SQL语句,
            )
            
            SQLiteClient._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'SQLiteClient':
        """获取SQLiteClient实例"""
        if cls._instance is None:
            cls._instance = SQLiteClient()
        return cls._instance
    
    @contextmanager
    def get_session(self):
        """获取数据库会话"""
        with Session(self.engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def create_db_and_tables(self):
        """创建数据库和表"""
        SQLModel.metadata.create_all(self.engine)
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()

# 创建全局实例
db_client = SQLiteClient.get_instance()