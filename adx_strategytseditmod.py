from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from datetime import datetime, timedelta
from freqtrade.persistence import Trade

# Optimized With Sortino Ratio and 2 years data

class adx_strategytseditmod(IStrategy):
    ticker_interval = '15m'

    # ROI table:
    minimal_roi = {
        "0": 0.08,
        "30": 0.05,
        "210": 0.03,
        "540": 0.01
    }

    # Stoploss:
    stoploss = -0.1255
    
    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.005
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
      
        # ADX
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['plus_di'] = ta.PLUS_DI(dataframe, timeperiod=25)
        dataframe['minus_di'] = ta.MINUS_DI(dataframe, timeperiod=25)
        dataframe['sar'] = ta.SAR(dataframe)
        dataframe['mom'] = ta.MOM(dataframe, timeperiod=14)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['adx'] > 16) &
                    (dataframe['minus_di'] > 4) &
                    # (dataframe['plus_di'] > 33) &
                    (qtpylib.crossed_above(dataframe['minus_di'], dataframe['plus_di']))

            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['adx'] > 43) &
                    # (dataframe['minus_di'] > 22) &
                    (dataframe['plus_di'] > 24) &
                    (qtpylib.crossed_above(dataframe['plus_di'], dataframe['minus_di']))

            ),
            'sell'] = 1
        return dataframe
        
    # ... populate_* methods

    use_custom_stoploss = False

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:

        # Make sure you have the longest interval first - these conditions are evaluated from top to bottom.
        if current_time - timedelta(minutes=530) > trade.open_date_utc:
            return -0.05
        elif current_time - timedelta(minutes=210) > trade.open_date_utc:
            return -0.10
        return 1

