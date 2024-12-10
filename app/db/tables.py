from typing import Dict, Iterable, List
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import ColumnElement, create_engine, MetaData, Table, INTEGER, REAL, Column, TEXT, DATE, Engine, select, text, TIMESTAMP, DATETIME
import datetime
from sqlalchemy import and_
from sqlalchemy.sql.expression import func
from dataclasses import dataclass
import dataclasses
from pandas import Timestamp
from app.interfaces import DataClassMixin


@dataclass
class DailyWeeklyTickerQuoteRow(DataClassMixin):
    symbol: str
    date: datetime.date
    open: float
    high: float
    low: float
    close: float
    volume: float


meta_metadata = MetaData()

def create_metadata_tables(engine: Engine):
    meta_metadata.create_all(engine)

security = Table(
    'security',
    meta_metadata,
    Column('id', TEXT, primary_key=True),
    Column('symbol', TEXT, index=True),
    Column('created_at', TIMESTAMP, default=text('CURRENT_TIMESTAMP')),
    Column('updated_at', TIMESTAMP, default=text('CURRENT_TIMESTAMP')),
)



daily_weekly_metadata = MetaData()


def create_daily_weekly_tables(engine: Engine):
    daily_weekly_metadata.create_all(engine)


adjusted_daily_price = Table(
    'adjusted_daily_price',
    daily_weekly_metadata,
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


adjusted_weekly_price = Table(
    'adjusted_weekly_price',
    daily_weekly_metadata,
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


ticker = Table(
    'ticker',
    daily_weekly_metadata,
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


intra_day_5m_metadata = MetaData()
adjusted_5m_price = Table(
    'adjusted_5m_price',
    intra_day_5m_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('timestamp', INTEGER, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)


intra_day_30m_metadata = MetaData()
adjusted_30m_price = Table(
    'adjusted_30m_price',
    intra_day_30m_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('timestamp', INTEGER, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)


def create_intra_day_5m_tables(engine: Engine):
    intra_day_5m_metadata.create_all(engine)

def create_intra_day_30m_tables(engine: Engine):
    intra_day_30m_metadata.create_all(engine)


sync_log = Table(
    'sync_log',
    meta_metadata,
    Column('for_date', DATE, primary_key=True),
    Column('run_time', DATETIME, primary_key=True),
    Column('status', TEXT),
)
