"""
布林带数据模型
"""

import pandas as pd
import numpy as np
from datetime import datetime
from common.database.models import GoldPriceDB
from sqlalchemy import text
import logging
import os
from decimal import Decimal

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bollinger_bands_models.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BollingerBandsModels')

class BollingerBandsData:
    def __init__(self, period=20, std_dev=2):
        """
        初始化布林带数据模型
        :param period: 布林带周期
        :param std_dev: 标准差倍数
        """
        self.db = GoldPriceDB()
        self.period = period
        self.std_dev = std_dev
        
    def calculate_bollinger_bands(self, df):
        """
        计算布林带指标
        :param df: 包含价格数据的DataFrame
        :return: 添加了布林带指标的DataFrame
        """
        # 确保价格数据是float类型
        df['price'] = df['price'].astype(float)
        
        # 计算移动平均线（中轨）
        df['middle_band'] = df['price'].rolling(window=self.period).mean()
        
        # 计算标准差
        df['std'] = df['price'].rolling(window=self.period).std()
        
        # 计算上轨和下轨
        df['upper_band'] = df['middle_band'] + (df['std'] * self.std_dev)
        df['lower_band'] = df['middle_band'] - (df['std'] * self.std_dev)
        
        # 计算带宽
        df['bandwidth'] = (df['upper_band'] - df['lower_band']) / df['middle_band']
        
        # 计算%B指标
        df['percent_b'] = (df['price'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
        
        return df
        
    def generate_weekly_data(self, df):
        """
        生成周线数据
        :param df: 日线数据DataFrame
        :return: 周线数据DataFrame
        """
        try:
            # 确保日期索引是datetime类型
            df.index = pd.to_datetime(df.index)
            
            # 确保价格数据是float类型
            df['price'] = df['price'].astype(float)
            
            # 重采样为周线数据
            weekly_df = df.resample('W').agg({
                'price': 'last',
                'open_price': 'first',
                'high_price': 'max',
                'low_price': 'min',
                'volume': 'sum'
            })
            
            # 计算周线布林带
            weekly_df = self.calculate_bollinger_bands(weekly_df)
            
            return weekly_df
            
        except Exception as e:
            logger.error(f"生成周线数据时发生错误: {str(e)}")
            return None
            
    def save_to_db(self, df, timeframe):
        """
        保存数据到数据库
        :param df: 包含布林带数据的DataFrame
        :param timeframe: 时间周期 ('daily' 或 'weekly')
        :return: 是否保存成功
        """
        try:
            with self.db.get_session() as session:
                for date, row in df.iterrows():
                    # 处理日期
                    if hasattr(date, 'date'):
                        db_date = date.date()
                    else:
                        db_date = date
                    
                    # 检查是否存在该日期的数据
                    result = session.execute(
                        text("""
                            SELECT id FROM bollinger_bands 
                            WHERE date = :date 
                            AND timeframe = :timeframe 
                            AND period = :period 
                            AND std_dev = :std_dev
                        """),
                        {
                            "date": db_date,
                            "timeframe": timeframe,
                            "period": self.period,
                            "std_dev": self.std_dev
                        }
                    )
                    existing_record = result.fetchone()
                    
                    # 处理可能的NaN值
                    middle_band = float(row['middle_band']) if pd.notnull(row['middle_band']) else None
                    upper_band = float(row['upper_band']) if pd.notnull(row['upper_band']) else None
                    lower_band = float(row['lower_band']) if pd.notnull(row['lower_band']) else None
                    bandwidth = float(row['bandwidth']) if pd.notnull(row['bandwidth']) else None
                    percent_b = float(row['percent_b']) if pd.notnull(row['percent_b']) else None
                    
                    if existing_record:
                        # 更新现有记录
                        session.execute(
                            text("""
                                UPDATE bollinger_bands 
                                SET price = :price,
                                    open_price = :open_price,
                                    high_price = :high_price,
                                    low_price = :low_price,
                                    volume = :volume,
                                    middle_band = :middle_band,
                                    upper_band = :upper_band,
                                    lower_band = :lower_band,
                                    bandwidth = :bandwidth,
                                    percent_b = :percent_b,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE id = :id
                            """),
                            {
                                "id": existing_record[0],
                                "price": float(row['price']),
                                "open_price": float(row.get('open_price')) if pd.notnull(row.get('open_price')) else None,
                                "high_price": float(row.get('high_price')) if pd.notnull(row.get('high_price')) else None,
                                "low_price": float(row.get('low_price')) if pd.notnull(row.get('low_price')) else None,
                                "volume": int(row.get('volume')) if pd.notnull(row.get('volume')) else None,
                                "middle_band": middle_band,
                                "upper_band": upper_band,
                                "lower_band": lower_band,
                                "bandwidth": bandwidth,
                                "percent_b": percent_b
                            }
                        )
                    else:
                        # 插入新记录
                        session.execute(
                            text("""
                                INSERT INTO bollinger_bands 
                                (date, timeframe, price, open_price, high_price, low_price, volume,
                                 middle_band, upper_band, lower_band, bandwidth, percent_b,
                                 period, std_dev, source)
                                VALUES 
                                (:date, :timeframe, :price, :open_price, :high_price, :low_price, :volume,
                                 :middle_band, :upper_band, :lower_band, :bandwidth, :percent_b,
                                 :period, :std_dev, 'FMP')
                            """),
                            {
                                "date": db_date,
                                "timeframe": timeframe,
                                "price": float(row['price']),
                                "open_price": float(row.get('open_price')) if pd.notnull(row.get('open_price')) else None,
                                "high_price": float(row.get('high_price')) if pd.notnull(row.get('high_price')) else None,
                                "low_price": float(row.get('low_price')) if pd.notnull(row.get('low_price')) else None,
                                "volume": int(row.get('volume')) if pd.notnull(row.get('volume')) else None,
                                "middle_band": middle_band,
                                "upper_band": upper_band,
                                "lower_band": lower_band,
                                "bandwidth": bandwidth,
                                "percent_b": percent_b,
                                "period": self.period,
                                "std_dev": self.std_dev
                            }
                        )
                
                session.commit()
                logger.info(f"成功保存{timeframe}数据")
                return True
                
        except Exception as e:
            logger.error(f"保存{timeframe}数据时发生错误: {str(e)}")
            return False
            
    def get_bollinger_bands_data(self, timeframe, start_date=None, end_date=None):
        """
        从数据库获取布林带数据
        :param timeframe: 时间周期 ('daily' 或 'weekly')
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 布林带数据DataFrame
        """
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
                    "timeframe": timeframe,
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
            
    def process_historical_data(self, start_date=None, end_date=None):
        """
        处理历史数据
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 是否处理成功
        """
        try:
            # 获取价格数据
            df = self.db.get_prices_df(start_date, end_date)
            if df is None or df.empty:
                logger.error("没有找到价格数据")
                return False
                
            # 计算日线布林带
            daily_df = self.calculate_bollinger_bands(df.copy())
            if not self.save_to_db(daily_df, 'daily'):
                return False
                
            # 计算周线布林带
            weekly_df = self.generate_weekly_data(df.copy())
            if not self.save_to_db(weekly_df, 'weekly'):
                return False
                
            logger.info("历史数据处理完成")
            return True
            
        except Exception as e:
            logger.error(f"处理历史数据时发生错误: {str(e)}")
            return False 