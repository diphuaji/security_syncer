import datetime
from app import db
from app.db import tables
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
import warnings
from app.data_import.facade import DataFacade

from app.helper_functions import *

logging.basicConfig(level=logging.INFO)

today = datetime.date.today()
start_date = today - datetime.timedelta(days=540)

engine = db.get_adjusted_data_engine()
tables.create_daily_weekly_tables(engine)
adjusted_daily_price_dao = db.AdjustedDailyPriceDao(engine)
adjusted_weekly_price_dao = db.AdjustedWeeklyPriceDao(engine)

daily_table_name = 'adjusted_daily_price'
weekly_table_name = 'adjusted_weekly_price'
logging.info(f'Truncating {weekly_table_name}')
with engine.connect() as conn:
    conn.execute(text(f"DELETE FROM {daily_table_name} WHERE {daily_table_name}.symbol NOT LIKE '60%';"))
    conn.execute(text(f"DELETE FROM {weekly_table_name} WHERE {weekly_table_name}.symbol NOT LIKE '60%';"))
    conn.commit()

facade = DataFacade.instance()

warnings.filterwarnings(action='ignore', category=Warning, module='pandas')
warnings.filterwarnings(action='ignore', category=Warning, module='yahooquery')

with open('sample_data/stock_pool.csv', newline='') as csvfile:
    five_years = 5*365
    delta = datetime.timedelta(days=five_years)
    ticker_data = csv.DictReader(csvfile)
    # Yahoofinance only fetches data up to < end_date
    time_periods = math.ceil(((today-start_date).days + 1)/ five_years)
    logging.info(f'Fetching data from %s to %s.', start_date, today)
    for securities in stock_chunks():
        tickers = ' '.join([s.ticker for s in securities])
        # tickers = ['ABBV']
        ticker = Ticker(tickers)
        logging.info(f'Fetching data for %s.', tickers)
        for i in range(time_periods):
            tmp_start_date = arrow.get(start_date + i*delta).date()
            tmp_end_date = min(tmp_start_date + delta, today)

            logging.info(f'Fetching data from %s to %s for %s.', tmp_start_date, tmp_end_date, tickers)
            
            weekly_tmp_end_date = datetime.date.fromisocalendar(tmp_end_date.year, tmp_end_date.isocalendar().week, 6)
            if weekly_tmp_end_date.isocalendar().week == today.isocalendar().week and today.isocalendar().weekday<5:
                weekly_tmp_end_date = get_previous_saturday(today)
            logging.info(f'Weekly start date: %s.', tmp_start_date)
            logging.info(f'Weekly end date: %s.', weekly_tmp_end_date)
            adjusted_history = facade.get_weekly_price(tickers, tmp_start_date, weekly_tmp_end_date)
            for data_chunk in adjusted_history:
                # print(data_chunk)
                adjusted_weekly_price_dao.insert(data_chunk)

            tmp_daily_end_date = tmp_end_date + datetime.timedelta(days=1)
            adjusted_history = facade.get_daily_price(tickers, tmp_start_date, tmp_daily_end_date)
            for data_chunk in adjusted_history:
                # print(data_chunk)
                adjusted_daily_price_dao.insert(data_chunk)

            sleep_time = 1 + randrange(2)
            # break
            logging.debug(f'Sleeping for %s seconds.', sleep_time)
            time.sleep(sleep_time)
        # break
        

        logging.info(f'Finished fetching data for %s.', tickers)

logging.info('Successfully synced for %s.', today.isoformat())

