# 导入路径设置
from common.utils.path import setup_project_path

# 现在可以导入common模块了
import pandas as pd
from datetime import datetime, timedelta
from common.fetchers import FMPFetcher
from common.database.GoldPriceDB import GoldPriceDB
  
from common.utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger('DailyDataFetchManager', 'logs/daily_data_fetch_manager.log')


class DailyDataFetchManager:
    def __init__(self):
        self.fetchers = [
            FMPFetcher(),  # 优先使用FMP
        ]
        self.db = GoldPriceDB()

    def fetch_daily_data(self):
        """获取每日数据的主函数"""
        try:
            logger.info("开始执行每日数据获取任务")
            
            # 设置时间范围（获取数据最新日期-7天的数据，以防有缺失）
            end_date = datetime.now().date()
            start_date = self.db.get_latest_date()
            if start_date is None:
                start_date = datetime.strptime('2025-01-01', '%Y-%m-%d').date()
            else:
                start_date = start_date - timedelta(days=7)
            
            for fetcher in self.fetchers:
                try:
                    logger.info("尝试使用FMPFetcher获取数据")
                    df = fetcher.fetch_data(start_date, end_date)
                    
                    if df is not None and not df.empty:
                        # 更新或插入数据
                        if self.db.update_or_insert_data(df, 'FMP'):
                            logger.info("使用FMPFetcher成功更新数据")
                            break
                except Exception as e:
                    logger.error("FMPFetcher获取数据失败: {str(e)}")
                    continue
                         
            
        except Exception as e:
            logger.error(f"执行每日任务时发生错误: {str(e)}")

  

if __name__ == "__main__":
    manager = DailyDataFetchManager() 
    logger.info("现在执行定时任务...")
    manager.fetch_daily_data()
    logger.info("定时任务执行完成")