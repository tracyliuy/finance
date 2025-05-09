import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Alpha Vantage API 配置
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")  # Get API key from environment variable
BASE_URL = os.getenv("ALPHA_VANTAGE_BASE_URL", "https://www.alphavantage.co/query")  # Get base URL from environment variable

def get_stock_info(ticker, use_cache=True, cache_expiry_hours=24):
    """
    获取股票信息，支持本地缓存
    
    参数:
    ticker (str): 股票代码
    use_cache (bool): 是否使用缓存
    cache_expiry_hours (int): 缓存过期时间（小时）
    """
    cache_file = f"data/{ticker}_daily.csv"
    
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    # 检查缓存
    if use_cache and os.path.exists(cache_file):
        cache_data = pd.read_csv(cache_file)
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        
        # 如果缓存未过期，直接返回缓存数据
        if datetime.now() - cache_time < timedelta(hours=cache_expiry_hours):
            print(f"使用缓存数据（更新于 {cache_time}）")
            return cache_data.iloc[0].to_dict()
    
    print("从API获取新数据...")
    
    # 构建API请求
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": API_KEY
    }
    
    try:
        # 发送API请求
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # 检查HTTP错误
        data = response.json()
        
        if "Global Quote" not in data:
            raise Exception("API返回数据格式错误或没有数据")
            
        quote = data["Global Quote"]
        
        # 构建股票信息字典
        stock_info = {
            "symbol": quote["01. symbol"],
            "price": float(quote["05. price"]),
            "change": float(quote["09. change"]),
            "change_percent": quote["10. change percent"].rstrip('%'),
            "volume": int(quote["06. volume"]),
            "latest_trading_day": quote["07. latest trading day"]
        }
        
        # 将数据保存到CSV
        df = pd.DataFrame([stock_info])
        df.to_csv(cache_file, index=False)
        print(f"数据已保存到 {cache_file}")
        
        return stock_info
        
    except requests.exceptions.RequestException as e:
        print(f"API请求错误: {str(e)}")
        raise
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise

def format_number(num):
    """格式化数字显示"""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    else:
        return f"${num:,.2f}"

# 主程序
if __name__ == "__main__":
    # 设置股票代码
    ticker = "AAPL"
    
    try:
        # 获取股票信息
        stock_info = get_stock_info(ticker)
        
        # 打印基本信息
        print("\n股票基本信息:")
        print(f"代码: {stock_info['symbol']}")
        print(f"当前价格: ${float(stock_info['price']):.2f}")
        print(f"涨跌额: ${float(stock_info['change']):.2f}")
        print(f"涨跌幅: {stock_info['change_percent']}%")
        print(f"成交量: {int(stock_info['volume']):,}")
        print(f"交易日期: {stock_info['latest_trading_day']}")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
