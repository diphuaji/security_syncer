import csv
import datetime
import math
from typing import Any, Dict, Iterable, List
import more_itertools
from typing import Optional
from typing import NamedTuple
from lxml import etree

import pandas
from yahooquery import Ticker
from datetime import date
from pandas import Timestamp
from dataclasses import dataclass
import logging

from app.constants import SECTOR_MAPPING_YAHOO_TO_GICS, INDUSTRY_MAPPING_YAHOO_TO_GICS
from app.data_model import Security
from app.interfaces import DataClassMixin


@dataclass
class DailyWeeklyTickerQuote(DataClassMixin):
    symbol: str
    date: datetime.date
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @classmethod
    def from_yahoo_quote(cls, record:dict) -> 'DailyWeeklyTickerQuote':
        return DailyWeeklyTickerQuote(
            symbol = record['symbol'],
            date = record['date'],
            open = record['open'],
            high = record['high'],
            low = record['low'],
            close = record['close'],
            volume = record['volume'],
        )


class DataFacade:
    __instance = None
    def __init__(self):
        raise Exception('Please use instatnce()')
        
    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = cls.__new__(cls)
        return cls.__instance

    def get_nyse_stocks(self) -> Iterable[Security]:
        with open('data/stock_pool.csv', newline='') as csvfile:
            five_years = 5 * 365
            delta = datetime.timedelta(days=five_years)
            ticker_data = csv.DictReader(csvfile)
            for t in ticker_data:
                yield Security(name=t['Symbol'], symbol=t['Symbol'], exchange='NYSE')

    def get_russel_2000_stocks(self) -> Iterable[str]:
        with open('data/roussel_2000.html', encoding='utf8') as f:
            parser = etree.HTMLParser()
            html_root = etree.fromstring(f.read(), parser)
            tr_path = etree.XPath("//tr")
            ticker_path = etree.XPath("td[1]/a[@class='profile-link']/div[2]/text()")
            for e in tr_path(html_root):
                data = ticker_path(e)
                if len(data):
                    print(data[0])

    def get_fundamentals(self, symbols: list[str], provider='yahoo'):
        if provider == 'yahoo':
            tickers = Ticker(symbols)


    def get_security_details(self, symbols: list[str], provider='yahoo') -> list[Security]:
        if provider == 'yahoo':
            tickers = Ticker(symbols)

            # Fetch profile and key stats
            summary = tickers.asset_profile
            quotes = tickers.quote_type
            price = tickers.price
            key_stats = tickers.key_stats

            # Parse results
            data = []
            for symbol in symbols:
                try:
                    profile = summary.get(symbol, {}) or {}
                    quote = quotes.get(symbol, {}) or {}
                    stats = key_stats.get(symbol, {}) or {}
                    price_info = price.get(symbol, {}) or {}

                    logging.debug('Original sector: %s', profile.get("sector"))
                    logging.debug('Original industry: %s', profile.get("industry"))
                    data.append(Security(
                        symbol=symbol,
                        name=quote.get("longName", ""),
                        exchange=quote.get("exchange", "UNKNOWN"),
                        asset_class=profile.get("quoteType", "EQUITY"),
                        currency=price_info.get("currency", "USD"),
                        country=profile.get("country", "US"),
                        sector=SECTOR_MAPPING_YAHOO_TO_GICS.get(profile.get("sector"), 'UNKNOWN'),
                        industry=INDUSTRY_MAPPING_YAHOO_TO_GICS.get(profile.get("industry"), 'UNKNOWN'),
                        isin=stats.get("isin") or profile.get("isin") or price_info.get("isin"),
                        cusip=stats.get("cusip"),
                        ipo_date=profile.get("ipoDate"),
                        is_active=True  # Assume active unless other data says otherwise
                    ))
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
            return data
        raise NotImplementedError(f'The provider - {provider} does not support fetching security details.')

    def get_daily_price(self, symbol:str, start_date: Optional[date] = None, end_date: Optional[date] = None, provider='yahoo', chunk_size=5000) -> Iterable[List[Dict]]:
        start_date = start_date if start_date else datetime.date.today() - datetime.timedelta(days=7)
        end_date = end_date if end_date else datetime.date.today()
        if provider == 'yahoo':
            ticker = Ticker(symbol)
            adjusted_history = ticker.history(
                start=start_date,
                end=end_date,
                interval='1d',
                adj_ohlc=True
            ).reset_index().to_dict('records')

            for chunk in more_itertools.chunked(adjusted_history, 5000):
                yield chunk
        else:
            raise Exception(f'provider not implemented: {provider}.')
        

    def get_weekly_price(
        self, 
        symbol:str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None, 
        whole_week_only: bool = True,
        provider='yahoo', 
        chunk_size=5000
    ) -> Iterable[List[DailyWeeklyTickerQuote]]:
        start_date = start_date if start_date else datetime.date.today() - datetime.timedelta(days=7)
        end_date = end_date if end_date else datetime.date.today()
        if provider == 'yahoo':
            ticker = Ticker(symbol)
            adjusted_history = ticker.history(
                start=start_date,
                end=end_date,
                interval='1wk',
                adj_ohlc=True
            )
            adjusted_history = adjusted_history\
                .loc[[idx for idx in adjusted_history.index if not isinstance(idx[1], datetime.datetime)]]\
                .reset_index()\
                .to_dict('records')

            for chunk in more_itertools.chunked(map(lambda x: DailyWeeklyTickerQuote.from_yahoo_quote(x), adjusted_history), chunk_size):
                yield chunk
        else:
            raise Exception(f'provider not implemented: {provider}.')

        
    def get_intra_day_price(
            self, 
            symbol:str, 
            interval='5m', 
            start_date: Optional[date] = None,
            end_date: Optional[date] = None, 
            provider='yahoo', 
            chunk_size=5000
        ) -> Iterable[List[DailyWeeklyTickerQuote]]:
        start_date = start_date if start_date else datetime.date.today() - datetime.timedelta(days=7)
        end_date = end_date if end_date else datetime.date.today()
        
        if provider == 'yahoo':
            ticker = Ticker(symbol)
            days_in_between = (end_date - start_date).days
            days_interval = 15
            batches = math.ceil(days_in_between / days_interval)
            tmp_start_date = start_date
            for i in range(batches):
                tmp_end_date = min(start_date + datetime.timedelta(days=days_interval), end_date)
                adjusted_history = ticker.history(
                    start=tmp_start_date,
                    end=tmp_end_date,
                    interval=interval,
                    adj_ohlc=True
                ).reset_index().rename(columns={'date': 'timestamp'}).to_dict('records')
                tmp_start_date =  tmp_end_date + datetime.timedelta(days=1)

                for chunk in more_itertools.chunked(map(lambda x: DailyWeeklyTickerQuote.from_yahoo_quote(x), adjusted_history), 5000):
                    yield chunk
        else:
            raise Exception(f'provider not implemented: {provider}.')
