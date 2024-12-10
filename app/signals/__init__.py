from typing import Tuple
from app import db
from app.helper_functions import *
import datetime
from datetime import timedelta
import itertools
from sqlalchemy.sql.expression import func
import talib
import pandas as pd
import numpy as np
import functools
import logging


logger=logging.getLogger(__name__)


def v_shape_signals(data):
    macd, macdsignal, macdhist = talib.MACDFIX(data.close)
    macdhist = macdhist.dropna()
    macd_diffs = macdhist.rolling(2).apply(lambda s: s.values[1]-s.values[0])
    sorted_macdhist_bars = macdhist.rolling(6).apply(lambda s: len([ 1 for v in s.values if v<0 ]) > 4)
    macd_diffs = macd_diffs.rolling(6).apply(lambda s: min(s.values[3:6])>=0 and max(s.values[:3])<=0)
    entry_points = macd_diffs + sorted_macdhist_bars
    return entry_points.dropna().loc[entry_points>1]



def u_shape_signals(data: pd.DataFrame, min_bottom_size = 7, percentage= 0.25) -> pd.Series:
    """Used to find the point where a period of MACD bars below 0 are witnessed & the current MACD bar is below certain percentage of the lowest one in the bottom."""
    macd, macdsignal, macdhist = talib.MACDFIX(data.close)
    start_end_pairs = []
    start_pos = 0
    lowest_bar = np.nan
    for idx, date_and_data in enumerate(macdhist.items()):
        lowest_bar = date_and_data[1] if lowest_bar is np.nan else min(date_and_data[1], lowest_bar)
        hist = date_and_data[1]
        if date_and_data[1] > 0 or np.isnan(hist):
            start_pos = idx+1
            lowest_bar = np.nan
        if date_and_data[1] <=0 and lowest_bar <=0 and date_and_data[1]/lowest_bar <= percentage and idx - start_pos > min_bottom_size-1:
            start_end_pairs.append((macdhist.index[start_pos], date_and_data[0]))
            lowest_bar = np.nan
            start_pos = idx+1

    return pd.Series([t[1] for t in start_end_pairs])


def macd_hist_diff(data: pd.DataFrame) -> pd.Series:
    """MACD hist diff with previous day"""
    macd, macdsignal, macdhist = talib.MACDFIX(data.close)
    return macdhist.diff()


def ema_up_down_signals(data: pd.DataFrame, period=14) -> pd.Series:
    """EMA hist diff with previous day"""
    result = talib.EMA(data.close, timeperiod=period)
    return result.diff()


def trends_based_on_past_days(data: pd.Series,  is_bullish=True, threadshold=0.8, days = 7):
    result = data.rolling(2).apply(lambda s: s.values[1]-s.values[0])\
        .rolling(days).apply(lambda s: len([v for v in s.values if (1 if is_bullish else -1)*v>0])>=int(threadshold*days))
    result.loc[result==1]


def support_and_resistance(data: pd.DataFrame, rolling_size=5) -> Tuple[pd.Series, pd.Series]:
    supports = data[data.low == data.low.rolling(rolling_size, center=True).min()].low
    resistances = data[data.high == data.high.rolling(rolling_size, center=True).max()].high
    return supports, resistances


def support_buy_points(data: pd.DataFrame, latest_lowest_price, percentage = 0.02, max_days_to_look_back=90, rolling_size=5) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    :returns (supports_to_filter, key_supports, key_resistances)
    """
    supports, resistances = support_and_resistance(data, rolling_size)
    levels = pd.concat([supports, resistances]).sort_index()
    # logging.info('levels: %s', levels)
    mean = data.close.mean()
    key_levels=levels.loc[abs(levels.diff()) > 0.05*mean]
    if supports.empty:
        return supports.copy(), supports.copy(), supports.copy()
    earliest_support_date = data.index.max() - datetime.timedelta(days=max_days_to_look_back)
    # latest_low= data.iloc[-1].low

    key_supports = supports.loc[supports.index.intersection(key_levels.index)]
    # logging.info('key supports: %s', key_supports)
    key_resistances = resistances.loc[resistances.index.intersection(key_levels.index)]
    supports_to_filter = key_supports.loc[[idx for idx in key_supports.index if idx>=earliest_support_date]]
    # logging.info('low inside function: %s', latest_lowest_price)
    # logging.info('supports_to_filter: %s', supports_to_filter)
    supports_to_filter = supports_to_filter.loc[(supports_to_filter <= (1+percentage)*latest_lowest_price) & (supports_to_filter > (1-percentage)*latest_lowest_price)]
    # logging.info('after supports_to_filter: %s', supports_to_filter)
    return supports_to_filter, key_supports, key_resistances



# def x(data: pd.Series,  is_bullish=True, threadshold=0.8, days = 7):
#     result = data.rolling(2).apply(lambda s: s.values[1]-s.values[0])\
#         .rolling(days).apply(lambda s: len([v for v in s.values if (1 if is_bullish else -1)*v>0])>=int(threadshold*days))
#     result.loc[result==1]
