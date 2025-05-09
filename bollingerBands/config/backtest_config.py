"""
回测配置
"""

# 回测配置
BACKTEST_CONFIG = {
    'start_date': '1980-01-01',  # 默认开始日期
    'end_date': '1999-12-31',    # 默认结束日期
    'initial_cash': 100000,      # 初始资金
    'commission': 0.001,         # 交易手续费
    'risk_free_rate': 0.02       # 无风险利率
} 