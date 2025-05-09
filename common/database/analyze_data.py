import pandas as pd
from datetime import datetime, timedelta
from .models import GoldPriceDB

def analyze_data_completeness(start_date=None, end_date=None, source='FMP'):
    """
    分析数据库中的数据完整性，找出缺失的日期
    
    Args:
        start_date: 开始日期，默认为None（使用数据库中最小的日期）
        end_date: 结束日期，默认为None（使用当前日期）
        source: 数据来源，默认为'FMP'
    
    Returns:
        tuple: (数据统计信息字典, 缺失日期列表)
    """
    # 创建数据库实例
    db = GoldPriceDB()
    
    # 获取日期范围
    if start_date is None or end_date is None:
        min_date, max_date = db.get_price_range(source)
        if min_date is None or max_date is None:
            print("数据库中没有数据")
            return None, None
            
        start_date = start_date or min_date
        end_date = end_date or max_date
    
    # 获取数据
    df = db.get_prices_df(start_date, end_date, source)
    if df is None or df.empty:
        print(f"在 {start_date} 到 {end_date} 期间没有找到数据")
        return None, None
    
    # 生成完整的日期范围
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 找出缺失的日期
    existing_dates = pd.to_datetime(df.index)
    missing_dates = date_range.difference(existing_dates)
    
    # 计算统计信息
    stats = {
        '总天数': len(date_range),
        '有数据的天数': len(existing_dates),
        '缺失的天数': len(missing_dates),
        '数据完整率': f"{(len(existing_dates) / len(date_range) * 100):.2f}%",
        '开始日期': start_date,
        '结束日期': end_date,
        '数据来源': source,
        '价格统计': {
            '最小值': df['price'].min(),
            '最大值': df['price'].max(),
            '平均值': df['price'].mean(),
            '标准差': df['price'].std()
        }
    }
    
    return stats, missing_dates

def print_analysis_results(stats, missing_dates):
    """打印分析结果"""
    if stats is None:
        return
        
    print("\n=== 数据统计信息 ===")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value:.2f}")
        else:
            print(f"{key}: {value}")
    
    if missing_dates is not None and len(missing_dates) > 0:
        print(f"\n=== 缺失的日期 ({len(missing_dates)}天) ===")
        # 将缺失日期按月份分组显示
        missing_by_month = {}
        for date in missing_dates:
            month_key = date.strftime('%Y-%m')
            if month_key not in missing_by_month:
                missing_by_month[month_key] = []
            missing_by_month[month_key].append(date.strftime('%Y-%m-%d'))
        
        for month, dates in missing_by_month.items():
            print(f"\n{month} 缺失 {len(dates)} 天:")
            print(", ".join(dates))

if __name__ == '__main__':
    # 分析数据完整性
    stats, missing_dates = analyze_data_completeness()
    print_analysis_results(stats, missing_dates) 