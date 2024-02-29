import datetime
from typing import Dict, List

from sqlalchemy import ColumnElement, create_engine, MetaData, Table, INTEGER, REAL, Column, TEXT, DATE, Engine, select, \
    text
from sqlalchemy import and_
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.sql.expression import func


# from app.data_import.facade import DailyWeeklyTickerQuote
# from app.db.tables import DailyWeeklyTickerQuoteRow, adjusted_daily_price, adjusted_weekly_price, adjusted_5m_price, intra_day_5m_metadata, intra_day_30m_metadata

def get_security_engine() -> Engine:
    return create_engine('mysql+pymysql://root:314152380@127.0.0.1:3306/security?charset=utf8mb4')

security_metadata = MetaData()

adjusted_daily_quote = Table(
    'adjusted_daily_price',
    security_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('date', DATE, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)

class AdjustedDailyQuoteDao:
    t = adjusted_daily_quote
    __instance__ = None

    def __init__(self):
        raise Exception('Use instance() to create')
    
    @classmethod
    def instance(cls, self, engine: Engine):
        if self.__instance__:
            return self.__instance__
        else:
            self.__instance = cls.__new__(cls)
            self.engine = engine

    def get_all(self, limit=100):
        with self.engine.begin() as txn:
            return txn.execute(self.t.select().limit(limit))

    def get_by_symbol(self, symbol: str, limit=10):
        with self.engine.begin() as txn:
            return txn.execute(self.t.select().where(self.t.c.symbol == symbol).order_by(self.t.c.date.desc()).limit(limit))

    def insert(self, records: List[Dict]):
        with self.engine.begin() as txn:
            stmt = insert(self.t)
            txn.execute(
                stmt.on_conflict_do_update(
                    index_elements=[self.t.c.symbol, self.t.c.date],
                    set_=dict(
                        open=stmt.excluded.open,
                        high=stmt.excluded.high,
                        low=stmt.excluded.low,
                        close=stmt.excluded.close,
                        dividends=stmt.excluded.dividends,
                        splits=stmt.excluded.splits,
                        volume=stmt.excluded.volume
                    )
                ), records)
            txn.commit()
            
    def get_by_symbols_and_date(self, symbols: List[str], start_date: datetime.date, end_date: datetime.date, partition_limit = 7):
        wheres: List[ColumnElement] = [ self.t.c.symbol.in_(symbols) ]
        if start_date:
            wheres.append(self.t.c.date>=start_date)
        if end_date:
            wheres.append(self.t.c.date<=end_date)
        where_clause = and_(*wheres)
        selectable = select('*', func.row_number().over(partition_by=self.t.c.symbol, order_by=self.t.c.date.desc()).label('row_num')).select_from(self.t).where(where_clause).order_by(self.t.c.symbol, self.t.c.date.desc())
        with self.engine.begin() as txn:
            return txn.execute(
                select('*').select_from(selectable).where(text('row_num<:partition_limit').bindparams(partition_limit=partition_limit+1))
            )