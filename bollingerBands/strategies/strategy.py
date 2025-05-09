import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from common.database.models import GoldPriceDB
from sqlalchemy import text
import logging
import os
from ..config import BACKTEST_CONFIG, BOLLINGER_BANDS_CONFIG

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bollinger_bands_strategy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BollingerBandsStrategy')

class BollingerBandsStrategy:
    def __init__(self, period=None, std_dev=None, timeframe='daily'):
        """
        初始化布林带策略
        :param period: 布林带周期，如果为None则使用配置文件的默认值
        :param std_dev: 标准差倍数，如果为None则使用配置文件的默认值
        :param timeframe: 时间周期，'daily' 或 'weekly'
        """
        self.db = GoldPriceDB()
        self.period = period or BOLLINGER_BANDS_CONFIG['period']
        self.std_dev = std_dev or BOLLINGER_BANDS_CONFIG['std_dev']
        if timeframe not in BOLLINGER_BANDS_CONFIG['timeframes']:
            raise ValueError(f"不支持的时间周期: {timeframe}")
        self.timeframe = timeframe
        
    def get_bollinger_bands_data(self, start_date=None, end_date=None):
        """从数据库获取布林带数据"""
        try:
            with self.db.get_session() as session:
                query = text("""
                    SELECT date, price, middle_band, upper_band, lower_band, 
                           bandwidth, percent_b
                    FROM bollinger_bands
                    WHERE timeframe = :timeframe
                    AND period = :period
                    AND std_dev = :std_dev
                """)
                params = {
                    "timeframe": self.timeframe,
                    "period": self.period,
                    "std_dev": self.std_dev
                }
                
                if start_date:
                    query = text(str(query) + " AND date >= :start_date")
                    params['start_date'] = start_date
                if end_date:
                    query = text(str(query) + " AND date <= :end_date")
                    params['end_date'] = end_date
                    
                query = text(str(query) + " ORDER BY date")
                
                result = session.execute(query, params)
                rows = result.fetchall()
                
                if not rows:
                    return None
                    
                # 转换为DataFrame
                df = pd.DataFrame(rows, columns=['date', 'price', 'middle_band', 
                                               'upper_band', 'lower_band', 
                                               'bandwidth', 'percent_b'])
                df.set_index('date', inplace=True)
                return df
                
        except Exception as e:
            logger.error(f"获取布林带数据时发生错误: {str(e)}")
            return None
            
    def generate_signals(self, start_date=None, end_date=None):
        """
        生成交易信号
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 包含交易信号的DataFrame
        """
        try:
            # 获取布林带数据
            df = self.get_bollinger_bands_data(start_date, end_date)
            if df is None or df.empty:
                logger.error("没有找到布林带数据")
                return None
                
            # 生成交易信号
            signals = pd.DataFrame(index=df.index)
            signals['price'] = df['price']
            signals['signal'] = 0  # 0表示不操作
            
            # 当价格突破上轨时，产生卖出信号
            signals.loc[df['price'] > df['upper_band'], 'signal'] = -1
            
            # 当价格突破下轨时，产生买入信号
            signals.loc[df['price'] < df['lower_band'], 'signal'] = 1
            
            # 添加布林带指标
            signals['middle_band'] = df['middle_band']
            signals['upper_band'] = df['upper_band']
            signals['lower_band'] = df['lower_band']
            signals['bandwidth'] = df['bandwidth']
            signals['percent_b'] = df['percent_b']
            
            return signals
            
        except Exception as e:
            logger.error(f"生成交易信号时发生错误: {str(e)}")
            return None
            
    def backtest(self, start_date=None, end_date=None, initial_capital=None):
        """
        回测策略
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param initial_capital: 初始资金，如果为None则使用配置文件的默认值
        :return: 回测结果
        """
        try:
            # 使用配置的默认值
            start_date = start_date or BACKTEST_CONFIG['start_date']
            end_date = end_date or BACKTEST_CONFIG['end_date']
            initial_capital = initial_capital or BACKTEST_CONFIG['initial_cash']
            
            # 获取交易信号
            signals = self.generate_signals(start_date, end_date)
            if signals is None or signals.empty:
                return None
                
            # 初始化回测结果
            results = pd.DataFrame(index=signals.index)
            results['price'] = signals['price']
            results['signal'] = signals['signal']
            results['position'] = 0  # 0表示空仓，1表示持仓
            results['capital'] = initial_capital
            results['holdings'] = 0.0
            results['cash'] = initial_capital
            results['returns'] = 0.0
            
            # 模拟交易
            position = 0
            for i in range(1, len(results)):
                # 获取当前信号
                signal = results['signal'].iloc[i]
                
                # 更新持仓
                if signal == 1 and position == 0:  # 买入信号
                    position = 1
                    results.loc[results.index[i], 'position'] = 1
                    # 计算可以买入的份额
                    price = results['price'].iloc[i]
                    shares = results['cash'].iloc[i-1] / price
                    # 考虑交易手续费
                    commission = shares * price * BACKTEST_CONFIG['commission']
                    results.loc[results.index[i], 'holdings'] = shares * price - commission
                    results.loc[results.index[i], 'cash'] = 0
                elif signal == -1 and position == 1:  # 卖出信号
                    position = 0
                    results.loc[results.index[i], 'position'] = 0
                    # 计算卖出后的现金
                    price = results['price'].iloc[i]
                    # 考虑交易手续费
                    commission = results['holdings'].iloc[i-1] * BACKTEST_CONFIG['commission']
                    results.loc[results.index[i], 'cash'] = results['holdings'].iloc[i-1] - commission
                    results.loc[results.index[i], 'holdings'] = 0
                else:  # 保持当前持仓
                    results.loc[results.index[i], 'position'] = position
                    if position == 1:
                        # 更新持仓价值
                        price = results['price'].iloc[i]
                        shares = results['holdings'].iloc[i-1] / results['price'].iloc[i-1]
                        results.loc[results.index[i], 'holdings'] = shares * price
                        results.loc[results.index[i], 'cash'] = results['cash'].iloc[i-1]
                    else:
                        results.loc[results.index[i], 'holdings'] = 0
                        results.loc[results.index[i], 'cash'] = results['cash'].iloc[i-1]
                
                # 计算总资产
                results.loc[results.index[i], 'capital'] = results['holdings'].iloc[i] + results['cash'].iloc[i]
                
                # 计算收益率
                results.loc[results.index[i], 'returns'] = (results['capital'].iloc[i] / results['capital'].iloc[i-1]) - 1
            
            # 计算累积收益率
            results['cumulative_returns'] = (1 + results['returns']).cumprod() - 1
            
            # 计算最大回撤
            results['peak'] = results['capital'].cummax()
            results['drawdown'] = (results['capital'] - results['peak']) / results['peak']
            max_drawdown = results['drawdown'].min()
            
            # 计算年化收益率
            days = (results.index[-1] - results.index[0]).days
            annual_return = (results['capital'].iloc[-1] / initial_capital) ** (365 / days) - 1
            
            # 计算夏普比率
            risk_free_rate = BACKTEST_CONFIG['risk_free_rate']
            excess_returns = results['returns'] - risk_free_rate/252  # 转换为日化无风险利率
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
            
            # 打印回测结果
            logger.info(f"\n回测结果 ({self.timeframe}):")
            logger.info(f"初始资金: ${initial_capital:,.2f}")
            logger.info(f"最终资金: ${results['capital'].iloc[-1]:,.2f}")
            logger.info(f"总收益率: {results['cumulative_returns'].iloc[-1]*100:.2f}%")
            logger.info(f"年化收益率: {annual_return*100:.2f}%")
            logger.info(f"最大回撤: {max_drawdown*100:.2f}%")
            logger.info(f"夏普比率: {sharpe_ratio:.2f}")
            
            return results
            
        except Exception as e:
            logger.error(f"回测过程中发生错误: {str(e)}")
            return None 