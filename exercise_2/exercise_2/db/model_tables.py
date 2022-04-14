"""Tables definition."""

from sqlalchemy import JSON, Column, Date, Float, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CoinRawData(Base):
    """Coin Raw Data data model."""

    __tablename__ = "coin_raw"

    __table_args__ = (UniqueConstraint("coin_id", "date"),)

    coin_id = Column(String)
    date = Column(Date)
    price = Column(Float)
    response = Column(JSON)

    __mapper_args__ = {"primary_key": [coin_id, date]}

    def __init__(self, coin_id, date, price, response):
        self.coin_id = coin_id
        self.date = date
        self.price = price
        self.response = response

    def __repr__(self):
        return f"""
        <StockValue(coin_id='{self.coin_id}', 
                    date='{self.date}', 
                    price='{self.price}', 
                    response='{self.response}
        )>"""


class CoinAggregatedData(Base):
    """Coin Aggregated Data data model."""

    __tablename__ = "coin_aggregated"

    # __table_args__ = (UniqueConstraint("coin_id", "year_month"),)

    coin_id = Column(String)
    year_month = Column(Date)
    max_price = Column(Float)
    min_price = Column(Float)

    __mapper_args__ = {"primary_key": [coin_id, year_month]}

    def __init__(self, coin_id, year_month, max_price, min_price):
        self.coin_id = coin_id
        self.year_month = year_month
        self.max_price = max_price
        self.min_price = min_price

    def __repr__(self):
        return f"""
        <StockValue(coin_id='{self.coin_id}', 
                    year_month='{self.year_month}', 
                    max_price='{self.max_price}', 
                    min_price='{self.min_price}
        )>"""
