import requests
import pandas as pd
from datetime import datetime
from .base import BaseFetcher
from ..config import API_KEYS, FETCHER_CONFIG

class FMPFetcher(BaseFetcher):
    """Financial Modeling Prep数据获取类"""
    
    def __init__(self):
        super().__init__()
        self.api_key = API_KEYS['FMP_API_KEY']
        self.config = FETCHER_CONFIG['fmp']
        self.base_url = self.config['base_url']
        
    def fetch_data(self, start_date=None, end_date=None):
        """获取黄金价格数据"""
        try:
            # 获取日期范围
            start_date, end_date = self.get_date_range(start_date, end_date, 'FMP')
            
            # 构建请求URL
            url = f"{self.base_url}{self.config['historical_price']}{self.config['symbol']}"
            params = {
                'apikey': self.api_key,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            # 发送请求
            print(f"正在从FMP获取从 {start_date} 到 {end_date} 的黄金价格数据...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'historical' not in data:
                print("API返回数据为空或格式错误")
                print("API响应:", data)
                return None
                
            # 处理数据
            historical_data = data['historical']
            df = pd.DataFrame(historical_data)
            
            # 重命名列
            df = df.rename(columns={
                'date': 'date',
                'close': 'price',
                'open': 'open_price',
                'high': 'high_price',
                'low': 'low_price',
                'volume': 'volume'
            })
            
            # 设置日期索引
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 按日期排序
            df.sort_index(inplace=True)
            
            # 只保留需要的列
            df = df[['price', 'open_price', 'high_price', 'low_price', 'volume']]
            
            print(f"成功获取了 {len(df)} 条数据")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {str(e)}")
            return None
        except Exception as e:
            print(f"处理数据错误: {str(e)}")
            return None
            
    def update_data(self):
        """更新数据到最新"""
        # 获取数据库中最新的日期
        latest_date = self.get_latest_date('FMP')
        if latest_date:
            start_date = latest_date
        else:
            # 如果数据库为空，使用默认开始日期
            start_date = datetime.strptime(FETCHER_CONFIG['fmp']['start_date'], '%Y-%m-%d').date()
            
        end_date = datetime.now().date()
        
        # 获取新数据
        df = self.fetch_data(start_date, end_date)
        if df is not None:
            return self.save_to_db(df, 'FMP')
        return False 