import pandas as pd
import pandas_datareader.data as web
import numpy as np
import datetime as dt
from datetime import datetime
import yfinance as yf
#from utils.py import *

# URL of the Wikipedia page from which to scrape the S&P 500 company list
url_sap = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

url_dow = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'

# Use pandas to scrape the tables from the Wikipedia page
tables = pd.read_html(url_dow)

# The first table on the page is the one we want
dow_table = tables[1]

# The ticker symbol is in the 'Symbol' column
symbols = dow_table['Symbol']

#The tickers data frame includes both the ticker symbol and company name
tickers = dow_table[['Symbol', 'Company']]
tickers_list = tickers.values.tolist()

#Blank list to 'store' the statistics for each stock
stocks_list = []

#Print the tickers and name
# for ticker in tickers_list:
#     print(ticker[0]+' - '+ticker[1])

for ticker in symbols:
    stocks_list.append(yf.Ticker(ticker).info)

#Create a list of fundamental information that we are interested in
fundamentals = ['symbol', 'dividendYield', 'marketCap', 'beta', 'forwardPE', 'priceToBook', 'bookValue', 'forwardEps', 'debtToEquity', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth']
# Create a DataFrame from the info dictionary
stock_data = pd.DataFrame(stocks_list)
# # Select only the columns in the fundamentals list
fundamentals_data = stock_data[fundamentals]
print(fundamentals_data)

