from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UniqueConstraint, text
from datetime import datetime
import pandas as pd
from .Database import Base, Database
from common.utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger('GoldPriceDB', 'logs/database.log')

class GoldPrice(Base):
    """黄金价格数据模型"""
    __tablename__ = 'gold_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    volume = Column(Integer)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 创建唯一约束
    __table_args__ = (
        UniqueConstraint('date', 'source', name='unique_date_source'),
    )

class GoldPriceDB(Database):
    """黄金价格数据库操作类"""
    
    def __init__(self):
        super().__init__()
        self.table_name = 'gold_prices'
        
    def add_price(self, date, price, open_price=None, high_price=None, 
                 low_price=None, volume=None, source='ALPHA_VANTAGE'):
        """添加单条价格数据"""
        def _add(session):
            price_data = GoldPrice(
                date=date,
                price=price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume,
                source=source
            )
            session.add(price_data)
            return True
            
        return self.execute_transaction(_add)
            
    def add_prices(self, prices_df, source='ALPHA_VANTAGE'):
        """批量添加价格数据"""
        def _add(session):
            for _, row in prices_df.iterrows():
                price_data = GoldPrice(
                    date=row.name if isinstance(row.name, datetime) else pd.to_datetime(row.name),
                    price=row['price'],
                    open_price=row.get('open_price'),
                    high_price=row.get('high_price'),
                    low_price=row.get('low_price'),
                    volume=row.get('volume'),
                    source=source
                )
                session.add(price_data)
            return True
            
        return self.execute_transaction(_add)

    def update_or_insert_data(self, df, source):
        """更新或插入数据"""
        try:
            with self.get_session() as session:
                for date, row in df.iterrows():
                    # 检查是否存在该日期的数据
                    result = session.execute(
                        text("SELECT id FROM gold_prices WHERE date = :date"),
                        {"date": date.date()}
                    )
                    existing_record = result.fetchone()
                    
                    if existing_record:
                        # 更新现有记录
                        session.execute(
                            text("""
                                UPDATE gold_prices 
                                SET price = :price,
                                    open_price = :open_price,
                                    high_price = :high_price,
                                    low_price = :low_price,
                                    volume = :volume,
                                    source = :source,
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
                                "source": source
                            }
                        )
                    else:
                        # 插入新记录
                        session.execute(
                            text("""
                                INSERT INTO gold_prices 
                                (date, price, open_price, high_price, low_price, volume, source)
                                VALUES 
                                (:date, :price, :open_price, :high_price, :low_price, :volume, :source)
                            """),
                            {
                                "date": date.date(),
                                "price": row['price'],
                                "open_price": row.get('open_price'),
                                "high_price": row.get('high_price'),
                                "low_price": row.get('low_price'),
                                "volume": row.get('volume'),
                                "source": source
                            }
                        )
                
                session.commit()
                logger.info("数据更新完成")
                return True
                
        except Exception as e:
            logger.error(f"更新数据时发生错误: {str(e)}")
            return False
            
    def get_price(self, date):
        """获取指定日期的价格数据"""
        def _get(session):
            return session.query(GoldPrice).filter_by(
                date=date
            ).first()
            
        return self.execute_transaction(_get)
            
    def get_prices(self, start_date, end_date):
        """获取指定日期范围的价格数据"""
        def _get(session):
            return session.query(GoldPrice).filter(
                GoldPrice.date.between(start_date, end_date)
            ).order_by(GoldPrice.date).all()
            
        return self.execute_transaction(_get)
            
    def get_prices_df(self, start_date=None, end_date=None):
        """获取价格数据"""
        try:
            with self.get_session() as session:
                query = text("""
                    SELECT date, price, open_price, high_price, low_price, volume
                    FROM gold_prices
                    WHERE 1=1
                """)
                params = {}
                
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
                df = pd.DataFrame(rows, columns=['date', 'price', 'open_price', 'high_price', 'low_price', 'volume'])
                df.set_index('date', inplace=True)
                return df
                
        except Exception as e:
            logger.error(f"获取价格数据时发生错误: {str(e)}")
            return None
            
    def update_price(self, date, price, **kwargs):
        """更新指定日期的价格数据"""
        def _update(session):
            price_data = session.query(GoldPrice).filter_by(
                date=date
            ).first()
            
            if price_data:
                price_data.price = price
                for key, value in kwargs.items():
                    setattr(price_data, key, value)
                return True
            return False
            
        return self.execute_transaction(_update)
            
    def delete_price(self, date):
        """删除指定日期的价格数据"""
        def _delete(session):
            price_data = session.query(GoldPrice).filter_by(
                date=date
            ).first()
            
            if price_data:
                session.delete(price_data)
                return True
            return False
            
        return self.execute_transaction(_delete)
            
    def get_latest_price(self):
        """获取最新的价格数据"""
        def _get(session):
            return session.query(GoldPrice).order_by(
                GoldPrice.date.desc()
            ).first()
            
        return self.execute_transaction(_get)
            
    def get_price_range(self):
        """获取数据日期范围"""
        def _get(session):
            min_date = session.query(GoldPrice.date).order_by(
                GoldPrice.date
            ).first()
            
            max_date = session.query(GoldPrice.date).order_by(
                GoldPrice.date.desc()
            ).first()
            
            return min_date[0] if min_date else None, max_date[0] if max_date else None
            
        return self.execute_transaction(_get)

    def get_latest_date(self):
        """获取数据库中最新的日期"""
        try:
            with self.get_session() as session:
                latest = session.query(GoldPrice).order_by(GoldPrice.date.desc()).first()
                return latest.date if latest else None
        except Exception as e:
            logger.error(f"获取最新日期时发生错误: {str(e)}")
            return None 