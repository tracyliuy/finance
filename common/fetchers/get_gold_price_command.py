import schedule
import time
import logging
from datetime import datetime, timedelta
from common.fetchers import FMPFetcher
from common.database.models import GoldPriceDB
from sqlalchemy import text
from bollingerBands.generate_historical_bollinger_bands import BollingerBandsGenerator
import os

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gold_price_fetcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GoldPriceFetcher')

class DataFetchManager:
    def __init__(self):
        self.fetchers = [
            FMPFetcher(),  # 优先使用FMP
        ]
        self.db = GoldPriceDB()
        self.bb_generator = BollingerBandsGenerator()

    def update_bollinger_bands(self, start_date, end_date):
        """更新布林带数据"""
        try:
            logger.info("开始更新布林带数据")
            if self.bb_generator.process_historical_data(start_date, end_date):
                logger.info("布林带数据更新成功")
            else:
                logger.error("布林带数据更新失败")
        except Exception as e:
            logger.error(f"更新布林带数据时发生错误: {str(e)}")

    def fetch_daily_data(self):
        """获取每日数据的主函数"""
        try:
            logger.info("开始执行每日数据获取任务")
            
            # 设置时间范围（获取最近7天的数据，以防有缺失）
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            success = False
            for fetcher in self.fetchers:
                try:
                    logger.info(f"尝试使用 {fetcher.__class__.__name__} 获取数据")
                    df = fetcher.fetch_data(start_date, end_date)
                    
                    if df is not None and not df.empty:
                        # 更新或插入数据
                        if self.db.update_or_insert_data(df, 'FMP'):
                            logger.info(f"使用 {fetcher.__class__.__name__} 成功更新数据")
                            success = True
                            break
                except Exception as e:
                    logger.error(f"{fetcher.__class__.__name__} 获取数据失败: {str(e)}")
                    continue
            
            if success:
                # 更新布林带数据
                # 为了确保计算的准确性，我们获取更多的历史数据
                bb_start_date = start_date - timedelta(days=self.bb_generator.period)
                self.update_bollinger_bands(bb_start_date, end_date)
            else:
                logger.error("所有数据源都获取失败")
            
        except Exception as e:
            logger.error(f"执行每日任务时发生错误: {str(e)}")

def main():
    manager = DataFetchManager()
    
    # 设置每天运行的时间（例如：每天早上9点）
    schedule.every().day.at("09:00").do(manager.fetch_daily_data)
    
    # 首次运行立即执行一次
    manager.fetch_daily_data()
    
    logger.info("调度系统已启动，等待执行定时任务...")
    
    # 保持程序运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次是否有待执行的任务

if __name__ == "__main__":
    main() 