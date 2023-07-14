import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from spare_parts import get_company_list
from tradingview_ta import TA_Handler, Interval, Exchange
import ta
import math


# main class
def calculate_linear_regression_r2(source, length):
    # Calculate linear regression
    bar_index = np.arange(1, len(source) + 1)
    sumX = np.sum(bar_index[-length:])
    sumY = np.sum(source[-length:])
    sumX2 = np.sum(np.power(bar_index[-length:], 2))
    sumY2 = np.sum(np.power(source[-length:], 2))
    sumXY = np.sum(bar_index[-length:] * source[-length:])

    # Pearson correlation coefficient
    r = (length * sumXY - sumX * sumY) / math.sqrt((length * sumX2 - sumX ** 2) * (length * sumY2 - sumY ** 2))

    # Coefficient of determination (R2)
    r2 = r ** 2

    return r2
def process_company_list(data_test,company_number):
    final_list = {}
    for i in data_test[:company_number]:
        try:
            data = yf.download(i[1]+".NS", period="30d", interval="30m")
            r2 = calculate_linear_regression_r2(data['Close'], 14)
            macd_data = ta.trend.MACD(data['Close']).macd()  # type: ignore
            macdsignal_data = ta.trend.MACD(data['Close']).macd_signal()  # type: ignore

            
            if (r2>0.3 and r2 <= 0.7) and macd_data[-1] > macdsignal_data[-1]:
              
                final_list[i[1]] = ["BUY",data['Close'],macd_data,macdsignal_data]
        except Exception as e:
            print(e)
            pass

    return list(final_list.keys()),list(final_list.values())
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



# =============================================
