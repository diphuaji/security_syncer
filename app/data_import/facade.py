import datetime
import math
from typing import Any, Dict, Iterable, List
import more_itertools
from typing import Optional
from typing import NamedTuple
from yahooquery import Ticker
from datetime import date
from pandas import Timestamp
from dataclasses import dataclass
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
