from yahooquery import Ticker
import datetime
import more_itertools
from typing import cast, Any
import numpy as np
import pandas as pd
import argparse
from app.data_import.facade import DataFacade
from app.db import tables, SecurityDao
from app import db
from typing import Optional
import sys
import logging

from app.db.tables import create_metadata_tables
from app.helper_functions import parse_date
import progressbar
import app.api_clients.alpha_vantage
import os


log_level_str = os.getenv('LOG_LEVEL').lower()

LOG_LEVEL_TO_PYTHON = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR
}

log_level = LOG_LEVEL_TO_PYTHON[log_level_str] if log_level_str in LOG_LEVEL_TO_PYTHON else logging.INFO

logging.basicConfig(level=log_level)

# from progressbar import


meta_engine = db.get_meta_engine()
fundamental_engine = db.get_fundamental_data_engine()
daily_weekly_engine = db.get_adjusted_data_engine()
tables.create_daily_weekly_tables(daily_weekly_engine)
intra_day_5m_engine = db.get_adjusted_5m_egnine()
tables.create_intra_day_5m_tables(intra_day_5m_engine)


class Namespace(argparse.Namespace):
    start_date: datetime.date
    end_date: datetime.date
    symbols: str


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=parse_date)
    parser.add_argument('--end-date', type=parse_date)
    parser.add_argument('--symbols', default=None)
    return parser


args = cast(Namespace, setup_parser().parse_known_args()[0])


adjusted_daily_price_dao = db.AdjustedDailyPriceDao(daily_weekly_engine)


def debug_data():
    ticker = Ticker(args.symbol)
    daily_start = datetime.datetime.strptime('2010-03-01', '%Y-%m-%d')
    daily_end = datetime.datetime.strptime('2010-03-02', '%Y-%m-%d')
    daily = ticker.history(
        start=daily_start,
        end=daily_end,
        adj_ohlc=False
    )

    daily_adjusted = ticker.history(
        start=daily_start,
        end=daily_end,
        period='1d',
        adj_ohlc=True
    )

    weekly_start = datetime.datetime.strptime('2010-03-01', '%Y-%m-%d')
    weekly_end = datetime.datetime.strptime('2010-03-14', '%Y-%m-%d')

    weekly = ticker.history(
        start=weekly_start,
        end=weekly_end,
        interval='1wk',
        adj_ohlc=False
    )

    weekly_adjusted = ticker.history(
        start=weekly_start,
        end=weekly_end,
        interval='1wk',
        adj_ohlc=True
    )

    monthly_adjusted = ticker.history(
        start=args.start_date,
        end=args.end_date,
        interval='1mo',
        period='3mo',
        adj_ohlc=True
    )

    monthly = ticker.history(
        start=args.start_date,
        end=args.end_date,
        interval='1mo',
        period='3mo',
        adj_ohlc=False
    )

    print(f'Daily columns: {list(daily.columns)}\n')
    print(f'Daily: {daily}\n')
    print(f'Daily adjusted columns: {list(daily_adjusted.columns)}\n')
    print(f'Daily adjusted: {daily_adjusted}\n')
    print(f'Weekly: {weekly}\n')
    print(f'Weekly adjusted: {weekly_adjusted}\n')
    print(f'Monthly: {monthly}\n')
    print(f'Monthly adjusted: {monthly_adjusted}\n')


def sync_metadata():
    create_metadata_tables(meta_engine)
    facade = DataFacade.instance()
    security_dao = SecurityDao(meta_engine)
    all_stocks = facade.get_nyse_stocks()
    for stock_chunk in more_itertools.chunked(all_stocks, 100):
        security_dao.insert(facade.get_security_details([stock.symbol for stock in stock_chunk]))

def sync_fundamental_data():
    fundamental_engine

def get_weekly():
    pass





sync_metadata()
sync_fundamental_data()

