import pandas as pd
import pandas_datareader.data as web
import numpy as np
from datetime import datetime

# URL of the Wikipedia page from which to scrape the S&P 500 company list
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

# Use pandas to scrape the tables from the Wikipedia page
tables = pd.read_html(url)

# The first table on the page is the one we want
sp500_table = tables[0]

# The ticker symbol is in the 'Symbol' column
tickers = sp500_table[['Symbol', 'Security']]
tickers_list = tickers.values.tolist()

# Print the tickers and name
for ticker in tickers_list:
    print(ticker[0]+' - '+ticker[1])