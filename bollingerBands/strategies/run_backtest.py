"""
运行布林带策略回测
"""

from datetime import datetime, timedelta
from bollingerBands.strategies.strategy import BollingerBandsStrategy

import logging
import os
import sys

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bollinger_bands_strategy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('BollingerBandsStrategy')

def run_backtest():
    """运行回测"""
    try:
        # 创建日线和周线策略实例
        daily_strategy = BollingerBandsStrategy(timeframe='daily')
        weekly_strategy = BollingerBandsStrategy(timeframe='weekly')
        
        # 设置回测时间范围（例如：最近一年）
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        logger.info("回测时间范围: {start_date} 到 {end_date}")
        
        # 运行回测
        logger.info("开始运行日线策略回测...")
        daily_results = daily_strategy.backtest(start_date, end_date)
        if daily_results is None:
            logger.error("日线策略回测失败")
        else:
            logger.info("日线策略回测完成")
        
        logger.info("开始运行周线策略回测...")
        weekly_results = weekly_strategy.backtest(start_date, end_date)
        if weekly_results is None:
            logger.error("周线策略回测失败")
        else:
            logger.info("周线策略回测完成")
        
        return daily_results, weekly_results
        
    except Exception as e:
        logger.error(f"回测过程中发生错误: {str(e)}", exc_info=True)
        return None, None

if __name__ == "__main__":
    # 当作为模块运行时，使用 python -m 命令
    run_backtest() 