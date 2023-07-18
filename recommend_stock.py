import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from spare_parts import get_company_list
from tradingview_ta import TA_Handler, Interval, Exchange
import ta
import math



def convert_to_4h_data(ticker_symbol, period = "40d"):
    # Download the 60-minute data
    data_1 = yf.download(ticker_symbol, period=period, interval="60m")


    # Resample the data to 4-hour intervals
    data_4h = data_1.resample('4H').agg({
        'Open': 'first',  #type: ignore
        'High': 'max',  #type: ignore
        'Low': 'min',   #type: ignore
        'Close': 'last', # ype: ignore
        'Adj Close': 'last', #type: ignore
        'Volume': 'sum' #type: ignore
    }) # type: ignore

    # Remove any rows with missing values
    data_4h = data_4h.dropna()

    return data_4h

# Example usage

def calculate_linear_regression_r2_series(source, length):
    r2_values = np.empty_like(source)  # Create an empty array to store R2 values

    for i in range(length, len(source)):
        sub_source = source[i - length:i]

        bar_index = np.arange(1, len(sub_source) + 1)
        sumX = np.sum(bar_index)
        sumY = np.sum(sub_source)
        sumX2 = np.sum(np.power(bar_index, 2))
        sumY2 = np.sum(np.power(sub_source, 2))
        sumXY = np.sum(bar_index * sub_source)

        r = (length * sumXY - sumX * sumY) / math.sqrt((length * sumX2 - sumX ** 2) * (length * sumY2 - sumY ** 2))
        r2 = r ** 2

        r2_values[i] = r2  # Store the R2 value in the array
    
    return pd.Series(r2_values, index=source.index)  # Return a Series with R2 values for each value in the seriesu
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
            data = yf.download(i[1]+".NS", period = "40d", interval = "60m")
            r2 = calculate_linear_regression_r2(data['Close'], 14)
            macd_data = ta.trend.MACD(data['Close']).macd()  # type: ignore
            macdsignal_data = ta.trend.MACD(data['Close']).macd_signal()  # type: ignore
            data['macd'] = macd_data
            data['macd_signal'] = macdsignal_data
            data['r2']  = calculate_linear_regression_r2_series(data['Close'], 14)
            data.dropna(inplace=True)
            data.index = np.arange(0,len(data)) # type: ignore
            #alfa =  data.index
            
            if (macd_data[-1] > macdsignal_data[-1] and macd_data[-1] < 0 and  macdsignal_data[-1] < 0):
              
                final_list[i[1]] = [data[['Close','macd','macd_signal','r2']]]
        except Exception as e:
            print(e)
            pass

    return [list(final_list.keys()),list(final_list.values())]
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
