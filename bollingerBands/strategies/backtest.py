import backtrader as bt
import pandas as pd
from datetime import datetime
from common.database.models import GoldPriceDB
from common.config import BACKTEST_CONFIG
from .strategy import BollingerBandsStrategy

def get_gold_prices_from_db(start_date, end_date):
    """从数据库获取黄金价格数据"""
    try:
        # 创建数据库实例
        db = GoldPriceDB()
        
        # 获取数据
        df = db.get_prices_df(start_date, end_date)
        
        if df is None or df.empty:
            print(f"警告：在 {start_date} 到 {end_date} 期间没有找到数据")
            return None
            
        print(f"成功获取 {len(df)} 条数据")
        return df
        
    except Exception as e:
        print(f"数据库读取错误: {str(e)}")
        return None

def run_backtest(start_date, end_date, initial_cash=None):
    """运行回测"""
    # 使用配置的初始资金
    if initial_cash is None:
        initial_cash = BACKTEST_CONFIG['initial_cash']
    
    # 从数据库获取数据
    df = get_gold_prices_from_db(start_date, end_date)
    if df is None or df.empty:
        print("无法获取数据，请检查数据库连接和查询条件")
        return

    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()

    # 加载数据
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引作为日期
        open='open_price',
        high='high_price',
        low='low_price',
        close='price',
        volume='volume',
        openinterest=-1
    )

    # 添加数据
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(initial_cash)

    # 设置手续费
    cerebro.broker.setcommission(commission=BACKTEST_CONFIG['commission'])

    # 添加策略
    cerebro.addstrategy(BollingerBandsStrategy, debug=True)

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # 运行回测
    print('初始资金: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('最终资金: %.2f' % cerebro.broker.getvalue())

    # 获取分析结果
    strat = results[0]
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    trades = strat.analyzers.trades.get_analysis()

    # 打印分析结果
    print('\n=== 回测结果 ===')
    print(f'夏普比率: {sharpe["sharperatio"]:.2f}')
    print(f'最大回撤: {drawdown["max"]["drawdown"]:.2%}')
    print(f'年化收益率: {returns["rnorm100"]:.2f}%')
    print(f'总交易次数: {trades["total"]["total"]}')
    print(f'盈利交易次数: {trades["won"]["total"]}')
    print(f'亏损交易次数: {trades["lost"]["total"]}')
    if trades["won"]["total"] > 0:
        print(f'平均盈利: {trades["won"]["pnl"]["average"]:.2f}')
    if trades["lost"]["total"] > 0:
        print(f'平均亏损: {trades["lost"]["pnl"]["average"]:.2f}')

    # 绘制结果
    cerebro.plot(style='candlestick')
    
    return {
        'sharpe_ratio': sharpe["sharperatio"],
        'max_drawdown': drawdown["max"]["drawdown"],
        'annual_return': returns["rnorm100"],
        'total_trades': trades["total"]["total"],
        'won_trades': trades["won"]["total"],
        'lost_trades': trades["lost"]["total"],
        'final_value': cerebro.broker.getvalue()
    } 