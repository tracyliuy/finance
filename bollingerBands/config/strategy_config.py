"""
布林带策略配置
"""

# 布林带策略配置
BOLLINGER_BANDS_CONFIG = {
    'period': 20,          # 布林带周期
    'std_dev': 2,          # 标准差倍数
    'timeframes': ['daily', 'weekly'],  # 支持的时间周期
    'position_size': 1     # 交易数量
} 