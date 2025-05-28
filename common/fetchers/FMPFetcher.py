import requests
import pandas as pd
from datetime import datetime
from common.fetchers.BaseFetcher import BaseFetcher
from common.config import API_KEYS, FETCHER_CONFIG
from common.utils.logger import setup_logger


# 设置日志记录器
logger = setup_logger('FMPFetcher', 'logs/fmp_fetcher.log')

class FMPFetcher(BaseFetcher):
    """Financial Modeling Prep API 数据获取器"""
    
    def __init__(self):
        super().__init__()
        self.api_key = API_KEYS.get('FMP_API_KEY')
        self.base_url = FETCHER_CONFIG['fmp']['base_url']
        self.symbol = FETCHER_CONFIG['fmp']['symbol']
        self.historical_price_endpoint = FETCHER_CONFIG['fmp']['historical_price']
        self.historical_chart_endpoint = FETCHER_CONFIG['fmp']['historical_chart']
        self.quote_endpoint = FETCHER_CONFIG['fmp']['quote']
        self.interval = FETCHER_CONFIG['fmp']['interval']
        
    def fetch_data(self, start_date=None, end_date=None):
        """获取历史价格数据"""
        if not self.api_key:
            logger.error("FMP API密钥未配置")
            return None
            
        try:
            # 构建API请求URL
            url = f"{self.base_url}{self.historical_price_endpoint}{self.symbol}"
            params = {
                'apikey': self.api_key,
                'from': start_date,
                'to': end_date
            }
            
            # 发送请求
            logger.info(f"正在获取 {self.symbol} 的历史价格数据...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # 解析响应数据
            data = response.json()
            if not data or 'historical' not in data:
                logger.error("API返回数据格式错误")
                return None
                
            # 转换为DataFrame
            df = pd.DataFrame(data['historical'])
            if df.empty:
                logger.warning("没有获取到数据")
                return None
                
            # 处理日期列
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 重命名列
            df.rename(columns={
                'close': 'price',
                'open': 'open_price',
                'high': 'high_price',
                'low': 'low_price'
            }, inplace=True)
            
            # 选择需要的列
            columns = ['price', 'open_price', 'high_price', 'low_price', 'volume']
            df = df[columns]
            
            logger.info(f"成功获取 {len(df)} 条数据")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"处理数据错误: {str(e)}")
            return None
            
    def fetch_quote(self):
        """获取实时报价"""
        if not self.api_key:
            logger.error("FMP API密钥未配置")
            return None
            
        try:
            # 构建API请求URL
            url = f"{self.base_url}{self.quote_endpoint}{self.symbol}"
            params = {'apikey': self.api_key}
            
            # 发送请求
            logger.info(f"正在获取 {self.symbol} 的实时报价...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # 解析响应数据
            data = response.json()
            if not data or not isinstance(data, list) or len(data) == 0:
                logger.error("API返回数据格式错误")
                return None
                
            # 获取第一条数据
            quote = data[0]
            
            # 创建DataFrame
            df = pd.DataFrame([{
                'price': quote.get('price'),
                'open_price': quote.get('open'),
                'high_price': quote.get('dayHigh'),
                'low_price': quote.get('dayLow'),
                'volume': quote.get('volume')
            }], index=[pd.Timestamp.now()])
            
            logger.info("成功获取实时报价")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"处理数据错误: {str(e)}")
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