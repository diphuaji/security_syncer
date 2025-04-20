import datetime
import more_itertools
import csv
import pandas as pd
import typing
import re
from app.data_import.facade import DailyWeeklyTickerQuote
from app.data_model import Security
import arrow

from app.db.tables import DailyWeeklyTickerQuoteRow


def parse_date(date_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')


def ssec_stock_chunks(size=50) -> typing.Iterable[typing.List[Security]]:
    def generate():
        with open('data/ssec_filtered_tickers.csv', newline='') as csvfile:
            ticker_data = csv.DictReader(csvfile)
            for t in ticker_data:
                exchange='ssec'
                yield Security(name=t['ticker'],symbol=t['ticker'], exchange=exchange)
    return more_itertools.chunked(generate(), size)



def stock_chunks(size=50) -> typing.Iterable[typing.List[Security]]:
    def generate():
        with open('data/stock_pool.csv', newline='') as csvfile:
            ticker_data = csv.DictReader(csvfile)
            for t in ticker_data:
                yield Security(name=t['Symbol'], symbol=t['Symbol'], exchange='')

        with open('data/tse_stock_pool.csv', newline='') as csvfile:
            ticker_data = csv.DictReader(csvfile)
            for t in ticker_data:
                if t['Symbol'].endswith('-T'):
                    symbol = re.sub(r"-T$", ".TO", t['Symbol'])
                    yield Security(name=symbol, symbol=symbol, exchange='TSE')
    
    return more_itertools.chunked(generate(), size)

def get_ticker_log_file_path(ticker: str):
    return f'output/trading_logs/{ticker}.log'


def convert_db_data_from_daily(data):
    dataframe = pd.DataFrame.from_records([x._asdict() for x in data])
    if not dataframe.empty:
        index = pd.MultiIndex.from_arrays([dataframe['symbol'], pd.DatetimeIndex(dataframe['date'])], names=['symbol', 'datetime'])
        dataframe = dataframe.set_index(index)
        # data.index=pd.DatetimeIndex(data.index.values)
    return dataframe


def get_latest_friday(d: datetime.date):
    """Returns the latest Friday including today if today is a Friday"""
    cal = d.isocalendar()
    weekday = cal.weekday
    if weekday < 5:
        # if weekday is less than 5, then we need to move back one week
        cal = get_same_day_previous_week(d).isocalendar()
    return datetime.date.fromisocalendar(cal.year, cal.week, 5)

def get_latest_monday(d: datetime.date):
    """Returns the latest Monday including today if today is a Monday"""
    cal = d.isocalendar()
    return datetime.date.fromisocalendar(cal.year, cal.week, 1)


def get_previous_monday(d: datetime.date):
    prev_cal = get_same_day_previous_week(d).isocalendar()
    return datetime.date.fromisocalendar(prev_cal.year, prev_cal.week, 1)

def get_previous_saturday(d: datetime.date):
    prev_cal = get_same_day_previous_week(d).isocalendar()
    return datetime.date.fromisocalendar(prev_cal.year, prev_cal.week, 6)


def get_latest_trading_day(d: datetime.date):
    cal = d.isocalendar()
    if cal.weekday > 5:
        return datetime.date.fromisocalendar(cal.year, cal.week, 5)
    return d


def get_same_day_previous_week(d: datetime.date):
    return d - datetime.timedelta(weeks=1)


def is_friday(d: datetime.date) -> bool:
    return d.isocalendar().weekday == 5

def date_to_none_tz_datetime(d: datetime.date) -> datetime.datetime:
    return arrow.get(d).datetime.replace(tzinfo=None)

def arrow_to_none_tz_datetime(arrow_instance: arrow.Arrow) -> datetime.datetime:
    return arrow_instance.datetime.replace(tzinfo=None)

def facade_record_to_db_format(ticker_quote: DailyWeeklyTickerQuote) -> DailyWeeklyTickerQuoteRow:
    return DailyWeeklyTickerQuoteRow(
        symbol=ticker_quote.symbol,
        date=ticker_quote.date,
        open=ticker_quote.open,
        high=ticker_quote.high,
        low=ticker_quote.low,
        close=ticker_quote.close,
        volume=ticker_quote.volume,
    )
