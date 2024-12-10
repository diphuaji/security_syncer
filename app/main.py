from yahooquery import Ticker
import datetime
import more_itertools
from typing import cast, Any
import numpy as np
import talib
import pandas as pd
import argparse
from app.data_import.facade import DataFacade
from app.db import tables
from app import db
from typing import Optional
import sys
import logging
from app.helper_functions import parse_date
import progressbar
import app.api_clients.alpha_vantage


logging.basicConfig(level=logging.INFO)

# from progressbar import


daily_weekly_engine = db.get_adjusted_data_engine()
tables.create_daily_weekly_tables(daily_weekly_engine)
intra_day_5m_engine = db.get_adjusted_5m_egnine()
tables.create_intra_day_5m_tables(intra_day_5m_engine)


class Namespace(argparse.Namespace):
    start_date: datetime.date
    end_date: datetime.date
    interval: str
    run_import: bool
    symbol: str
    action: Optional[str]



def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=parse_date)
    parser.add_argument('--end-date', type=parse_date)
    parser.add_argument('--interval', default='1d')
    parser.add_argument('--run-import', action='store_true', default=False)
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--action', default=None)
    return parser


args = cast(Namespace, setup_parser().parse_known_args()[0])


adjusted_daily_price_dao = db.AdjustedDailyPriceDao(daily_weekly_engine)

if args.run_import:
    progress = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    logging.info('Importing data for %s, interval: %s', args.symbol, args.interval)
    import_facade = DataFacade()
    chunk: object
    if args.interval.endswith('d'):
        progress = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
        for chunk in import_facade.get_daily_price(symbol=args.symbol, start_date =args.start_date, end_date=args.end_date):
            adjusted_daily_price_dao.insert(chunk)
            progress.update((len(chunk)))
    elif args.interval.endswith('wk'):
        logging.warning('interval %s not supported.', args.interval)
    elif args.interval.endswith('m') or args.interval.endswith('h'):
        adjusted_intra_day_price_dao = db.AdjustedIntraDayPriceDao(interval=args.interval, engine=intra_day_5m_engine)
        for chunk in import_facade.get_intra_day_price(symbol=args.symbol, interval=args.interval, start_date =args.start_date, end_date=args.end_date):
            adjusted_intra_day_price_dao.insert([ r.as_dict() for r in chunk])
            progress.update((len(chunk)))
    progress.finish()


def entry_points_14_day():
    db_data = map(lambda x: x._asdict(),
                adjusted_daily_price_dao.get_by_symbol(args.symbol))

    data = pd.DataFrame.from_records(data=db_data).set_index(['symbol', 'date'])

    penetration_days = 42
    ema_days = 14

    ema = talib.EMA(pd.Series(
        data.close), timeperiod=ema_days)

    ema22 = talib.EMA(pd.Series(
        data.close), timeperiod=22)


    daily_penetrations: pd.Series = ema - pd.Series(data.low)
    daily_penetrations = daily_penetrations.map(
        lambda x: x if x > 0 else np.NAN,
        na_action='ignore'
    )

    avg_down_penetration = daily_penetrations.rolling(
        penetration_days, 1).mean()

    # entry points
    print((ema.rolling(2).apply(lambda s: s.values[1]*2-s.values[0]) - avg_down_penetration).to_csv(na_rep='NAN'))

    # stop loss 

    # print(avg_down_penetration.to_frame().merge(daily_penetrations.rename(
    #     'daily_penetration'), left_index=True, right_index=True).merge(pd.Series(data.close).rename('close'), left_index=True, right_index=True).reset_index().to_csv(na_rep='NAN'))



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


def get_weekly():
    pass


this_module=sys.modules[__name__]
if args.action:
    if hasattr(this_module, args.action):
        getattr(this_module, args.action)()
    else:
        logging.info(f'Action not found: %s.', args.action)
