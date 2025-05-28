# 导入路径设置
from common.utils.path import setup_project_path

# 现在可以导入common模块了
from datetime import datetime 
from common.database.GoldPriceDB import GoldPriceDB
from sqlalchemy import text
from common.utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger('BollingerBandsGenerator', 'logs/bollinger_bands_generator.log')

class BollingerBandsGenerator:
    def __init__(self, period=20, std_dev=2):
        self.db = GoldPriceDB()
        self.period = period
        self.std_dev = std_dev
        
    def calculate_bollinger_bands(self, df):
        """计算布林带指标"""
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
        """生成周线数据"""
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
        
    def save_to_db(self, df, timeframe):
        """保存数据到数据库"""
        try:
            with self.db.get_session() as session:
                for date, row in df.iterrows():
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
                            "date": date.date(),
                            "timeframe": timeframe,
                            "period": self.period,
                            "std_dev": self.std_dev
                        }
                    )
                    existing_record = result.fetchone()
                    
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
                                "price": row['price'],
                                "open_price": row.get('open_price'),
                                "high_price": row.get('high_price'),
                                "low_price": row.get('low_price'),
                                "volume": row.get('volume'),
                                "middle_band": row['middle_band'],
                                "upper_band": row['upper_band'],
                                "lower_band": row['lower_band'],
                                "bandwidth": row['bandwidth'],
                                "percent_b": row['percent_b']
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
                                "date": date.date(),
                                "timeframe": timeframe,
                                "price": row['price'],
                                "open_price": row.get('open_price'),
                                "high_price": row.get('high_price'),
                                "low_price": row.get('low_price'),
                                "volume": row.get('volume'),
                                "middle_band": row['middle_band'],
                                "upper_band": row['upper_band'],
                                "lower_band": row['lower_band'],
                                "bandwidth": row['bandwidth'],
                                "percent_b": row['percent_b'],
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
            
    def process_historical_data(self, start_date=None, end_date=None):
        """处理历史数据"""
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

def main():
    # 创建生成器实例
    generator = BollingerBandsGenerator()
    
    # 设置时间范围（例如：从1980年到2024年）
    start_date = datetime(1980, 1, 1).date()
    end_date = datetime.now().date()
    
    # 处理历史数据
    generator.process_historical_data(start_date, end_date)

if __name__ == "__main__":
    main() 