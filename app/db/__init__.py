import datetime
from typing import Dict, List, Optional

from sqlalchemy import ColumnElement, create_engine, Engine, select, \
    text
from sqlalchemy import and_
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.sql.expression import func

from app.db.tables import DailyWeeklyTickerQuoteRow, adjusted_daily_price, adjusted_weekly_price, adjusted_5m_price, \
    intra_day_5m_metadata, intra_day_30m_metadata


def get_adjusted_data_engine(start_date: Optional[datetime.date] = None,
                             end_date: Optional[datetime.date] = None) -> Engine:
    if start_date is None and end_date is None:
        date_part = ''
    elif start_date:
        date_part = '.' + start_date.isoformat()
        if end_date:
            date_part += '_' + end_date.isoformat()
    else:
        raise ValueError('start date and end date must both be non-None or None at the same time.')

    file_path = f'data/adjusted_data{date_part}.db'
    return create_engine(f'sqlite+pysqlite:///{file_path}')


def get_meta_engine() -> Engine:
    file_path = 'data/meta.db'
    return create_engine(f'sqlite+pysqlite:///{file_path}')


def get_adjusted_5m_egnine() -> Engine:
    file_path = 'data/adjusted_5m_data.db'
    return create_engine(f'sqlite+pysqlite:///{file_path}')


def get_adjusted_30m_egnine() -> Engine:
    file_path = 'data/adjusted_5m_data.db'
    return create_engine(f'sqlite+pysqlite:///{file_path}')


class AdjustedDailyWeeklyDaoMixin:
    pass


class AdjustedDailyPriceDao(AdjustedDailyWeeklyDaoMixin):
    t = adjusted_daily_price

    def __init__(self, engine: Engine):
        self.engine = engine

    def get_all(self, limit=100):
        with self.engine.begin() as txn:
            return txn.execute(self.t.select().limit(limit))

    def get_by_symbol(self, symbol: str, limit=10):
        with self.engine.begin() as txn:
            return txn.execute(
                self.t.select().where(self.t.c.symbol == symbol).order_by(self.t.c.date.desc()).limit(limit))

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

    def get_by_symbols_and_date(self, symbols: List[str], start_date: datetime.date, end_date: datetime.date,
                                partition_limit=7):
        wheres: List[ColumnElement] = [self.t.c.symbol.in_(symbols)]
        if start_date:
            wheres.append(self.t.c.date >= start_date)
        if end_date:
            wheres.append(self.t.c.date <= end_date)
        where_clause = and_(*wheres)
        selectable = select('*',
                            func.row_number().over(partition_by=self.t.c.symbol, order_by=self.t.c.date.desc()).label(
                                'row_num')).select_from(self.t).where(where_clause).order_by(self.t.c.symbol,
                                                                                             self.t.c.date.desc())
        with self.engine.begin() as txn:
            return txn.execute(
                select('*').select_from(selectable).where(
                    text('row_num<:partition_limit').bindparams(partition_limit=partition_limit + 1))
            )


class AdjustedWeeklyPriceDao(AdjustedDailyWeeklyDaoMixin):
    t = adjusted_weekly_price

    def __init__(self, engine: Engine):
        self.engine = engine

    def get_all(self, limit=100):
        with self.engine.begin() as txn:
            return txn.execute(self.t.select().limit(limit))

    def get_by_symbol(self, symbol: str):
        with self.engine.begin() as txn:
            return txn.execute(self.t.select().where(self.t.c.symbol == symbol).order_by(self.t.c.date.desc()))

    def get_by_symbols_and_date(self, symbols: List[str], start_date: datetime.date, end_date: datetime.date,
                                partition_limit=7):
        wheres: List[ColumnElement] = [self.t.c.symbol.in_(symbols)]
        if start_date:
            wheres.append(self.t.c.date >= start_date)
        if end_date:
            wheres.append(self.t.c.date <= end_date)
        where_clause = and_(*wheres)
        selectable = select('*',
                            func.row_number().over(partition_by=self.t.c.symbol, order_by=self.t.c.date.desc()).label(
                                'row_num')).select_from(self.t).where(where_clause).order_by(self.t.c.symbol,
                                                                                             self.t.c.date.desc())
        with self.engine.begin() as txn:
            return txn.execute(
                select('*').select_from(selectable).where(
                    text('row_num<:partition_limit').bindparams(partition_limit=partition_limit + 1))
            )

    def get_by_symbols_leq_date(self, symbols: List[str], date: datetime.date, partition_limit=7):
        selectable = select('*',
                            func.row_number().over(partition_by=self.t.c.symbol, order_by=self.t.c.date.desc()).label(
                                'row_num')).select_from(self.t).where(
            and_(self.t.c.symbol.in_(symbols), self.t.c.date <= date)).order_by(self.t.c.symbol, self.t.c.date.desc())
        with self.engine.begin() as txn:
            return txn.execute(
                select('*').select_from(selectable).where(
                    text('row_num<:partition_limit').bindparams(partition_limit=partition_limit + 1))
            )

    def insert(self, records: List[DailyWeeklyTickerQuoteRow]):
        with self.engine.begin() as txn:
            stmt = insert(self.t).values([r.as_dict() for r in records])
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
                ))
            txn.commit()


class AdjustedIntraDayPriceDao:
    interval_to_tables = {
        '5m': adjusted_5m_price
    }

    def __init__(self, interval: str, engine: Engine):
        self.engine = engine
        self.interval = interval
        self.t = self.interval_to_tables[interval]

    def get_all(self):
        with self.engine.begin() as txn:
            return txn.execute(self.t.select().limit(100))

    def insert(self, records: List[Dict]):
        with self.engine.begin() as txn:
            stmt = insert(self.t).values(records)
            txn.execute(
                stmt.on_conflict_do_update(
                    index_elements=[self.t.c.symbol, self.t.c.timestamp],
                    set_=dict(
                        open=stmt.excluded.open,
                        high=stmt.excluded.high,
                        low=stmt.excluded.low,
                        close=stmt.excluded.close,
                        dividends=stmt.excluded.dividends,
                        splits=stmt.excluded.splits,
                        volume=stmt.excluded.volume
                    )
                ))
            txn.commit()
