"""
布林带策略回测脚本
"""

from datetime import datetime, timedelta
from .strategy import BollingerBandsStrategy
import logging
import os

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bollinger_bands_backtest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BollingerBandsBacktest')

def run_backtest():
    """运行布林带策略回测"""
    try:
        # 创建策略实例
        daily_strategy = BollingerBandsStrategy(timeframe='daily')
        weekly_strategy = BollingerBandsStrategy(timeframe='weekly')
        
        # 设置回测时间范围
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)  # 回测最近一年的数据
        
        # 执行回测
        logger.info("开始回测日线策略...")
        daily_results = daily_strategy.backtest(start_date, end_date)
        
        logger.info("\n开始回测周线策略...")
        weekly_results = weekly_strategy.backtest(start_date, end_date)
        
        return daily_results, weekly_results
        
    except Exception as e:
        logger.error(f"回测过程中发生错误: {str(e)}")
        return None, None

if __name__ == '__main__':
    # 设置回测参数
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 3, 1)
    
    # 运行回测
    results = run_backtest(start_date, end_date)
    
    if results:
        print("\n=== 回测结果汇总 ===")
        print(f"夏普比率: {results['sharpe_ratio']:.2f}")
        print(f"最大回撤: {results['max_drawdown']:.2%}")
        print(f"年化收益率: {results['annual_return']:.2f}%")
        print(f"总交易次数: {results['total_trades']}")
        print(f"盈利交易次数: {results['won_trades']}")
        print(f"亏损交易次数: {results['lost_trades']}")
        print(f"最终资金: {results['final_value']:.2f}") 