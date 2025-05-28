import sys
import os
import pandas as pd
 

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
 

from datetime import datetime
from common.fetchers import FMPFetcher
from common.config import API_KEYS
from common.database.GoldPriceDB import GoldPriceDB
from common.utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger('HistoricalDataFetchManager', 'logs/historical_data.log')


class HistoricalDataFetchManager:
    """历史数据获取管理器"""
    
    def __init__(self):
        self.fmp_fetcher = FMPFetcher()
        self.db = GoldPriceDB()

    def fetch_year_data(self, year):
        """获取指定年份的数据"""
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        logger.info(f"\n开始获取 {year} 年数据:")
        logger.info(f"开始日期: {start_date}")
        logger.info(f"结束日期: {end_date}")
        
        # 获取数据
        df = self.fmp_fetcher.fetch_data(start_date, end_date)
        if df is not None and not df.empty:
            logger.info(f"成功获取 {len(df)} 条数据")
            # 保存数据
            self.fmp_fetcher.save_to_db(df, 'FMP')
            return True
        else:
            logger.error("获取数据失败")
            return False

    def fetch_historical_data(self, start_date=None, end_date=None):
        """获取历史数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        if start_date is None:
            # 如果没有指定开始日期，从最新数据的前一天开始
            latest_date = self.fmp_fetcher.get_latest_date()
            if latest_date:
                start_date = (latest_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                # 如果没有数据，默认从一年前开始
                start_date = (pd.to_datetime(end_date) - pd.Timedelta(days=365)).strftime('%Y-%m-%d')
                
        logger.info("\nAPI密钥验证:")
        logger.info(f"FMP API密钥: {'已配置' if self.fmp_fetcher.api_key else '未配置'}")
        
        logger.info("\n数据获取配置:")
        logger.info(f"开始日期: {start_date}")
        logger.info(f"结束日期: {end_date}")
        
        # 获取数据
        df = self.fmp_fetcher.fetch_data(start_date, end_date)
        if df is not None and not df.empty:
            logger.info(f"成功获取 {len(df)} 条数据")
            # 保存数据
            self.fmp_fetcher.save_to_db(df, 'FMP')
            return True
        else:
            logger.error("获取数据失败")
            return False

if __name__ == '__main__':
    manager = HistoricalDataFetchManager()
    manager.fetch_historical_data('2025-05-01', '2025-05-28')