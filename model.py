import requests
import csv
import finnhub
import pandas as pd
import copy
import numpy as np
import datetime
from functools import reduce

################# Helper Function #################
def strategy1(x):
    """
    momentum strategy 4(a)
    :param x: pandas series with price, S_avg, S_std
    :return: position
    """
    if x['price'] > x['S_avg'] + x['S_std']:
        return 1
    elif x['price'] < x['S_avg'] - x['S_std']:
        return -1
    else:
        return np.nan

def strategy2(x):
    """
    mean reversion strategy 4(b)
    :param x: pandas series with price, S_avg, S_std
    :return: position
    """
    if x['price'] > x['S_avg'] + x['S_std']:
        return -1
    elif x['price'] < x['S_avg'] - x['S_std']:
        return 1
    else:
        return np.nan

############## Obejects ##############
class Ticker(object):
    def __init__(self, symbol, df_historical, df_result):
        """Tickers object contains relevant information.
        Args:
            tickers (:obj:`str`): ticker symbol
            df_historical (:obj:pd.DataFrame): historical price time series
            df_result (:obj:pd.DataFrame): historical price time series together with signal and pnl
        """

        self.symbol = symbol
        self.df_historical = df_historical
        self.df_result = df_result


class TickersTracker(object):
    def __init__(self, symbols=["AAPL"], interval=5, filenames=[]):
        """Tickers Tracker object which construct Ticker Object and pull data from API

        Args:
            symbols (:obj:`list` of :obj:`str`): list of ticker symbolss
            interval (:obj:`int`): historical data query interval
            filenames (:obj:`list` of :obj:`str`): list of filenames to reload
        """

        # Take the assumption that if data file is provided, each file mathces each of tickers, in case of ambiguity.

        if filenames != []:
            assert len(symbols) == len(filenames)
        self.symbols = symbols
        self.interval = interval
        self.filenames = filenames

        self.api_key_alphavantage = "TP7GV4210NIYI1PR"
        self.api_key_finhub = "c7m961iad3id8p04d5c0"
        # self.api_key_finhub_sandbox = "sandbox_c7m961iad3id8p04d5cg"

        self.alphavantage_base_url = 'https://www.alphavantage.co/query'
        # Full two year history slides. due to api request frequency limiataion, use only the first two.
        self.slides = ["year{year}month{month}".format(year=year, month=month) for year in [1, 2] for month in
                       range(1, 13, 1)]
        self.slides = self.slides[:2]
        self.finnhub_client = finnhub.Client(api_key=self.api_key_finhub)

        self.init()

    def init(self):
        """Init trackers records
        """

        self.tracker = {}

        for i, symbol in enumerate(self.symbols):
            if self.filenames != []:
                all_record_pd = pd.read_csv(self.filenames[i])
                print("Reload:, ", self.filenames[i])
                all_record_w_signal = self.generate_signal_pnl(symbol, all_record_pd)
                new_ticker = Ticker(symbol, all_record_pd, all_record_w_signal)
            else:
                new_ticker = self.query_ticker(symbol)

            self.tracker[symbol] = new_ticker
        return 0

    def update_tickers(self):
        for symbol, ticker in self.tracker.items():
            self.update_ticker(symbol, ticker.df_historical)

    def update_ticker(self, symbol, df):
        """Update one ticker based on current market price

        Args:
            symbol (:obj:`str`): ticker symbol
            df (:obj:pd.DataFrame): price time series
        """

        out = self.finnhub_client.quote(symbol)
        price = out['c']
        curr_time = out['t']
        s = curr_time
        time = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d-%H:%M')
        if time in df.datetime.values:
            print('Datetime exist for ticker: ', symbol, 'Time:', time)
        else:
            new = pd.DataFrame([[time, price]], columns=['datetime', 'price'])
            new['datetime'] = pd.to_datetime(new['datetime'], errors='coerce')
            new['datetime'] = new.datetime.dt.strftime('%Y-%m-%d-%H:%M')
            for col in new.columns[1:]:
                new[col] = pd.to_numeric(new[col], errors='coerce')
            all_record_pd = pd.concat([df, new], ignore_index=True)
            csv_filename = '{ticker}_price.csv'.format(ticker=symbol)
            all_record_pd.to_csv(csv_filename)
            print("Update:, ", csv_filename)
            df = all_record_pd
            all_record_w_signal = self.generate_signal_pnl(symbol, df)

            new_ticker = Ticker(symbol, all_record_pd, all_record_w_signal)
            self.tracker[symbol] = new_ticker

    def generate_signal_pnl(self, symbol, df):
        """Computes a Boolean trading signal series for the entire price time series,
        also updates the trading signal and profit & loss calculation the price gets updated live.

        Args:
            symbol (:obj:str): ticker symbol
            df (:obj:pd.DataFrame): price time series
        """
        df_cp = copy.deepcopy(df)
        df_cp['datetime'] = pd.to_datetime(df_cp['datetime'], errors='coerce')
        df_cp.index = df_cp['datetime'].apply(lambda x: pd.Timestamp(x))
        df_cp = df_cp[['price']]
        df_cp = df_cp.sort_index()
        # calculate MA & sigma by datetime delta < 24hr, to be tested
        S_avg = df_cp.rolling('24H', min_periods=1).mean()
        S_std = df_cp.rolling('24H', min_periods=1).std()
        S_avg.columns = ['S_avg']
        S_std.columns = ['S_std']
        data_frames = [df_cp, S_avg, S_std]
        df_merged = reduce(lambda left, right: pd.merge(left, right,
                                                        left_index= True, right_index=True,
                                                        how='outer'), data_frames)
        # Two strategies. Use strategy1 as default
        df_merged['signal'] = df_merged.apply(strategy1, axis = 1) #4a momentum strategy
        # df_merged['signal'] = df_merged.apply(strategy2, axis=1) #4b mean reversion strategy
        df_merged['signal'] = df_merged['signal'].fillna(method = 'ffill')
        df_merged['pnl'] = df_merged['signal'].shift(1)*(df_merged['price'] - df_merged['price'].shift(1))

        # reformat df
        df_merged = df_merged.reset_index()
        df_merged['datetime'] = pd.to_datetime(df_merged['datetime'], errors='coerce')
        df_merged['datetime'] = df_merged.datetime.dt.strftime('%Y-%m-%d-%H:%M')
        csv_filename = '{ticker}_result.csv'.format(ticker=symbol)
        df_merged.to_csv(csv_filename)
        print("Generate:, ", csv_filename)
        return df_merged

    def query_ticker(self, symbol):
        """Query ticker historical data give list of tickers

        Args:
            symbol (:obj:`str`): ticker symbol
        """
        all_record = []
        for slide in self.slides:
            CSV_URL = self.alphavantage_base_url + \
                      '?function=TIME_SERIES_INTRADAY_EXTENDED&symbol={symbol}&interval={interval}min&slice={slice}&apikey={key}'. \
                          format(symbol=symbol, interval=self.interval, slice=slide, key=self.api_key_alphavantage)

            with requests.Session() as s:
                download = s.get(CSV_URL)
                decoded_content = download.content.decode('utf-8')
                cr = csv.reader(decoded_content.splitlines(), delimiter=',')

                df = pd.DataFrame(cr)
                if len(df) == 1:
                    print("Could not fount tickr given symbol")
                    return None

                df.iloc[0, 0] = 'datetime'
                new_header = df.iloc[0]  # grab the first row for the header
                df = df[1:]  # take the data less the header row
                df.columns = new_header  # set the header row as the df header
                df.head()

                new_df = df[['datetime', 'close']]
                new_df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
                new_df['datetime'] = new_df.datetime.dt.strftime('%Y-%m-%d-%H:%M')
                for col in new_df.columns[1:]:
                    new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
                new_df.rename(columns={'close': 'price'}, inplace=True)
                all_record.append(new_df)

        all_record_pd = pd.concat(all_record, ignore_index=True)
        csv_filename = '{ticker}_price.csv'.format(ticker=symbol)
        all_record_pd.to_csv(csv_filename)
        print("Generate:, ", csv_filename)

        all_record_w_signal = self.generate_signal_pnl(symbol, all_record_pd)
        new_ticker = Ticker(symbol, all_record_pd, all_record_w_signal)
        return new_ticker

    def query_price_by_time(self, datetime_object):
        """query and print price by time

        Args:
            datetime_object (:obj:`str`): datetime string
        """
        out_str = []
        for symbol, ticker in self.tracker.items():
            df = ticker.df_historical
            mask = (df.datetime.values == datetime_object)
            if mask.sum() == 0:
                out_str.append("Server has no data")
                continue
            price_record = df.loc[mask]['price'].values
            if len(price_record) > 0:
                out_str.append("{symbol} {price}".format(symbol=symbol, price=price_record[0]))
            else:
                out_str.append("{symbol} No Data".format(symbol=symbol))
        out_str = "\n".join(out_str)
        return out_str

    def query_signal_by_time(self, datetime_object):
        """query and print signal by time

        Args:
            datetime_object (:obj:`str`): datetime string
        """
        out_str = []
        for symbol, ticker in self.tracker.items():
            df = ticker.df_result
            mask = (df.datetime.values == datetime_object)
            if mask.sum() == 0:
                out_str.append("Server has no data")
                continue
            record = df.loc[mask]['signal'].values
            if len(record) > 0:
                out_str.append("{symbol} {signal}".format(symbol=symbol, signal=record[0]))
            else:
                out_str.append("{symbol} No Data".format(symbol=symbol))
        out_str = "\n".join(out_str)
        return out_str

    def del_ticker(self, symbol):
        """delete ticker from server

        Args:
            symbol (:obj:`str`): ticker symbol
        """
        try:
            if symbol not in self.tracker:
                print("Symbol {symbol}  not found".format(symbol=symbol))

                return 2
            else:
                self.tracker.pop(symbol)
                return 0
        except Exception as e:
            print("Error when running function del_ticker, ", e)
            return 1

    def add_ticker(self, symbol):
        """add ticker to server

        Args:
            symbol (:obj:`str`): ticker symbol
        """
        try:
            new_ticker = self.query_ticker(symbol)
            if new_ticker is None:
                print("Symbol {symbol} is not valid".format(symbol=symbol))
                return 2
            self.tracker[symbol] = new_ticker
            return 0

        except Exception as e:
            print("Error when running function add_ticker, ", e)
            return 1

    def reset(self):
        """Init trackers records with exception handler
        """
        try:
           self.init()
        except Exception as e:
            print("Error when running function reset, ", e)
            return 1
        return 0

if __name__ == '__main__':
    ## Testings
    tic = TickersTracker(['AAPL', 'IBM'], 5, filenames=['AAPL_price.csv', 'IBM_price.csv'])
    # print(tic.del_ticker('IBM'))
    # print(tic.add_ticker('NVDA'))
    # out = tic.query_price_by_time('2024-01-21-16:35')
    # print("Price", out)
    out = tic.query_signal_by_time('2022-01-21-16:35')
    print("Signal", out)
    # print(tic.reset())
    # out = tic.query_price_by_time('2022-01-21-16:35')
    # print("Price", out)
