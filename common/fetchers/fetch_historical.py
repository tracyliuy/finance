import sys
from datetime import datetime, timedelta
from .fmp import FMPFetcher
from ..config import API_KEYS
import time

def fetch_year_data(year, fmp_fetcher):
    """获取指定年份的数据"""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    print(f"\n获取 {year} 年的数据...")
    df = fmp_fetcher.fetch_data(start_date, end_date)
    
    if df is not None and not df.empty:
        print(f"成功获取 {year} 年数据，日期范围: {df.index.min()} 到 {df.index.max()}")
        print(f"数据条数: {len(df)}")
        
        # 保存到数据库
        if fmp_fetcher.save_to_db(df, 'FMP'):
            print(f"{year} 年数据已成功保存到数据库")
            return True
        else:
            print(f"{year} 年数据保存失败")
            return False
    else:
        print(f"{year} 年数据获取失败")
        return False

def fetch_historical_data(start_date=None, end_date=None):
    """获取历史黄金价格数据"""
    # 验证API密钥
    print("\nAPI密钥验证:")
    print(f"FMP API Key: {API_KEYS['FMP_API_KEY'][:4]}...{API_KEYS['FMP_API_KEY'][-4:]}")
    
    # 设置默认日期
    if start_date is None:
        start_date = '2000-01-01'
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
        
    # 转换日期
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    print(f"\n开始获取从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')} 的黄金价格数据...")
    
    # 创建FMP获取器实例
    fmp_fetcher = FMPFetcher()
    
    # 按年份获取数据
    start_year = start_date.year
    end_year = end_date.year
    success_count = 0
    total_years = end_year - start_year + 1
    
    for year in range(start_year, end_year + 1):
        print(f"\n进度: {year - start_year + 1}/{total_years}")
        if fetch_year_data(year, fmp_fetcher):
            success_count += 1
        # 在年份之间添加延时，避免API限制
        if year < end_year:
            print("等待5秒后继续...")
            time.sleep(5)
    
    print(f"\n数据获取完成！成功获取了 {success_count}/{total_years} 年的数据。")
    return success_count == total_years

if __name__ == '__main__':
    # 从命令行参数获取日期范围
    start_date = sys.argv[1] if len(sys.argv) > 1 else None
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    fetch_historical_data(start_date, end_date)