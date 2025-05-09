from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime, timedelta
from ..database.models import GoldPriceDB

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
        if df is not None and not df.empty:
            return self.db.add_prices(df, source=source)
        return False
        
    def get_latest_date(self, source):
        """获取数据库中最新的日期"""
        latest_price = self.db.get_latest_price(source)
        if latest_price:
            return latest_price.date
        return None
        
    def get_date_range(self, start_date=None, end_date=None, source=None):
        """获取日期范围"""
        if end_date is None:
            end_date = datetime.now().date()
            
        if start_date is None:
            # 如果没有指定开始日期，从最新数据的前一天开始
            latest_date = self.get_latest_date(source)
            if latest_date:
                start_date = latest_date + timedelta(days=1)
            else:
                # 如果没有数据，默认从一年前开始
                start_date = end_date - timedelta(days=365)
                
        return start_date, end_date 