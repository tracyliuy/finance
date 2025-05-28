from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime, timedelta
from common.database.GoldPriceDB import GoldPriceDB
from common.utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger('BaseFetcher', 'logs/fetcher.log')

class BaseFetcher(ABC):
    """数据获取基类"""
    
    def __init__(self):
        self.db = GoldPriceDB()
        
    @abstractmethod
    def fetch_data(self, start_date=None, end_date=None):
        """获取数据"""
        pass
        
    def save_to_db(self, df, source):
        """保存数据到数据库"""
        if df is None or df.empty:
            logger.warning("没有数据需要保存")
            return False
            
        try:
            # 确保日期列是datetime类型
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
                
            # 保存数据
            success = self.db.update_or_insert_data(df, source)
            if success:
                logger.info("成功保存 {len(df)} 条数据到数据库")
            else:
                logger.error("保存数据失败")
            return success
            
        except Exception as e:
            logger.error(f"保存数据时发生错误: {str(e)}")
            return False
        
    def get_latest_date(self):
        """获取数据库中最新的日期"""
        return self.db.get_latest_date()
        
    def get_date_range(self, start_date=None, end_date=None, source=None):
        """获取日期范围"""
        if end_date is None:
            end_date = datetime.now().date()
            
        if start_date is None:
            # 如果没有指定开始日期，从最新数据的前一天开始
            latest_date = self.get_latest_date()
            if latest_date:
                start_date = latest_date + timedelta(days=1)
            else:
                # 如果没有数据，默认从一年前开始
                start_date = end_date - timedelta(days=365)
                
        return start_date, end_date 