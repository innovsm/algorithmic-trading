import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from spare_parts import get_company_list
from tradingview_ta import TA_Handler, Interval, Exchange
import ta


# main class
class bollinger_band:
    def __init__(self, ticker):
        self.ticker = ticker
        self.MAX_PROFIT_LIMIT = 0.2
        self.MAX_LOSS_LIMIT = -0.1
        self.current_position = 0
        self.output = 0
        self.positions = []
        self.logs = []
        # special - signal
        self.call = "" 
        self.signal = 0 # this signal changes once stock reaches the upper - bollinger band
    # define function
    def download_data(self):
        data_raw = yf.download(self.ticker+".NS", period="2y", interval = "1d")
        # calculating bollinger band
        volatile = ta.volatility.BollingerBands(data_raw['Close']) # type: ignore
        data_raw['bollinger_hband'] = volatile.bollinger_hband()
        data_raw['bollinger_lband'] = volatile.bollinger_lband()
        data_raw['bollinger_mavg'] = volatile.bollinger_mavg()
        data_raw['bollinger_pband'] = volatile.bollinger_pband()
        # calculating obv
        volatile_obv = ta.volume.OnBalanceVolumeIndicator(data_raw['Close'], data_raw['Volume']) #type: ignore
        data_raw['obv'] = volatile_obv.on_balance_volume()
        # calculating rsi
        data_raw['rsi'] = ta.momentum.RSIIndicator(data_raw['Close']).rsi() #type: ignore
        data_raw.dropna(inplace = True)
        data_raw['diff'] = data_raw['obv'].diff(periods=10) # slope
        #print(data_raw.columns)
        self.data_list = data_raw.to_numpy()
        return data_raw
    
    def signal_check(self):
        self.download_data()
        main_list = self.data_list[-7:]
        for i in main_list:
            if(i[3] >= i[6]):
                self.signal = 1
        #print(self.signal)
    # main function
    def run_test(self):
        self.signal_check()
        i = self.data_list[-1]
        

            # --
        try:
                current_node = i
                # buying section
                # checking the bollinger signal
                data = TA_Handler(
                    symbol = self.ticker,
                    exchange="NSE",
                    screener="india",
                    interval=Interval.INTERVAL_1_DAY
                )
                x = data.get_analysis().summary #type: ignore
                if(self.signal == 1):
                    # checking [RSI] and [OBV - diff] condition
                    if(current_node[12] > 0 and current_node[11] > 50):  # initally current_node[11] > 50
                        print(x)
                        if(x['RECOMMENDATION'] == "STRONG_BUY"):
                            self.call = "strong_buy"
                        elif(x['RECOMMENDATION'] == "BUY"):
                            self.call = "buy"
    

                else:
                    # checking [RSI] and [OBV - diff] condition
                    if(current_node[3] < current_node[7]):
                        if(x['RECOMMENDATION'] == "SELL"):
                            self.call = "strong_sell"

                # selling the stock
                
        except:
            self.call = "sell"

