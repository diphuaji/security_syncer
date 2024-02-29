import datetime
from ratelimit import limits
import csv
import more_itertools
import time
from random import randrange
import logging
from yahooquery import Ticker
import math
import arrow
import copy
from sqlalchemy import text
from app.data_import.facade import DataFacade
from app.helper_functions import *


logging.basicConfig(level=logging.INFO)


engine = db.get_adjusted_data_egnine()
tables.create_daily_weekly_tables(engine)
adjusted_daily_price_dao = db.AdjustedDailyPriceDao(engine)
adjusted_weekly_price_dao = db.AdjustedWeeklyPriceDao(engine)

start_date = arrow.get(parse_date('2010-10-01')).date()
# Yahoofinance only fetches data up to < end_date
today = datetime.date.today()

weekly_table_name = 'adjusted_weekly_price'
logging.info(f'Truncating {weekly_table_name}')
with engine.connect() as conn:
    conn.execute(text(
        f"DELETE FROM {weekly_table_name} WHERE {weekly_table_name}.symbol NOT LIKE '60%';"))
    conn.commit()

facade = DataFacade.instance()


with open('data/stock_pool.csv', newline='') as csvfile:
    five_years = 5*365
    delta = datetime.timedelta(days=five_years)
    ticker_data = csv.DictReader(csvfile)
    time_periods = math.ceil(((today-start_date).days + 1) / five_years)
    logging.info(f'Fetching data from %s to %s.', start_date, today)
    for securities in stock_chunks():
        tickers = ' '.join([s.ticker for s in securities])
        # tickers = ['ABBV']
        ticker = Ticker(tickers)
        logging.info(f'Fetching data for %s.', tickers)
        for i in range(time_periods):
            tmp_start_date = arrow.get(start_date + i*delta).date()
            tmp_end_date = min(tmp_start_date + delta, today)

            logging.info(f'Fetching data from %s to %s for %s.',
                         tmp_start_date, tmp_end_date, tickers)
            tmp_daily_end_date = tmp_end_date + datetime.timedelta(days=1)

            adjusted_history = ticker.history(
                start=tmp_start_date,
                end=tmp_daily_end_date,
                interval='1d',
                adj_ohlc=True
            ).reset_index().to_dict('records')

            for data_chunk in adjusted_history:
                # print(data_chunk)
                adjusted_daily_price_dao.insert(data_chunk)

            sleep_time = 1 + randrange(2)
            # break
            logging.debug(f'Sleeping for %s seconds.', sleep_time)
            time.sleep(sleep_time)
        # break

        logging.info(f'Finished fetching data for %s.', tickers)
