import pandas as pd
import pandas_datareader.data as web
import numpy as np
import datetime as dt
from datetime import datetime
import yfinance as yf
from yahoo_fin import stock_info as si
from utils import *


start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()

# URL of the Wikipedia page from which to scrape the S&P 500 company list
url_sap = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
# URL of the Wikipedia page from which to scrape the Dow Jones company list
url_dow = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
#URL of the Wikipedia page from which to scrape the S&P 100 company list
url_sap_100 = 'https://en.wikipedia.org/wiki/S%26P_100'

symbols = scrape_company_tickers(url_dow)
print('here is your list of companies')
print(symbols)

# The tickers data frame includes both the ticker symbol and company name
# tickers = dow_table[['Symbol', 'Company']]
# tickers_list = tickers.values.tolist()
# Blank list to 'store' the statistics for each stock
stocks_list = []


def collect_data():
    # Print the tickers and name
    # for ticker in tickers_list:
    #     print(ticker[0]+' - '+ticker[1])

    print('calculating your company fundamentals - this may take a minute or two...')

    for ticker in symbols:
        stocks_list.append(yf.Ticker(ticker).info)

    # Create a list of fundamental information that we are interested in
    fundamentals = ['symbol', 'marketCap', 'forwardPE', 'priceToBook', 'forwardEps',
                    'debtToEquity', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'dividendYield']
    # Create a DataFrame from the info dictionary
    stock_data = pd.DataFrame(stocks_list)
    # # Select only the columns in the fundamentals list
    fundamentals_data = stock_data[fundamentals]
    return fundamentals_data


fundamentals_data = collect_data()


def calculate_quarterly_return(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
        data['quarterly_return'] = data['Adj Close'].resample('Q').ffill().pct_change()
        return data.loc['2023-06-30', 'quarterly_return']
    except Exception as e:
        print(f"Failed to download data for {ticker}. Error: {e}")
        return np.nan

# Step 2: Data Processing
def process_data(tickers):
    index = 0
    returns_list = []
    for ticker in tickers:
        returns_list.append(calculate_quarterly_return(ticker, start, end))
    return returns_list


fundamentals_data['quarterlyReturn'] = process_data(symbols)

print ('---------------------------------------------------- \n')
print('Here are the fundamentals for your list of companies: \n')
print('----------------------------------------------------')
print(fundamentals_data)

fundamentals_percentile = calculate_percentile_rank(fundamentals_data[['marketCap', 'forwardPE', 'priceToBook', 'forwardEps',
                    'debtToEquity', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'dividendYield', 'quarterlyReturn']])
fundamentals_percentile['symbols'] = symbols
fundamentals_percentile.set_index('symbols', inplace=True)

fundamentals_percentile = fundamentals_percentile.dropna()

print ('---------------------------------------------------- \n')
print('Here are the fundamentals for your list of companies ranked as a percentile: \n')
print('----------------------------------------------------')
print(fundamentals_percentile)