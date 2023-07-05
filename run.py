import pandas as pd
import pandas_datareader.data as web
import numpy as np
import datetime as dt
from datetime import datetime
import yfinance as yf
from yahoo_fin import stock_info as si
from utils import *

chosen_index = get_companies_list()
symbols = scrape_company_tickers(chosen_index)
print('here is your list of companies')
print(symbols)

fundamentals_data = collect_data(symbols)
fundamentals_data['quarterlyReturn'] = process_data(symbols)

print ('---------------------------------------------------- \n')
print('Here are the fundamentals for your list of companies: \n')
print('----------------------------------------------------')
print(fundamentals_data)

fundamentals_data_dropna = fundamentals_data.dropna()
removed_companies = fundamentals_data['symbol'].count() - fundamentals_data_dropna['symbol'].count()
fundamentals_percentile = calculate_percentile_rank(fundamentals_data_dropna[['forwardPE', 'debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']])
fundamentals_percentile['symbols'] = symbols
#fundamentals_percentile.set_index('symbols', drop=False, inplace=True)
fundamentals_percentile = fundamentals_percentile[['symbols','forwardPE','debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']]

print ('---------------------------------------------------- \n')
print('Here are your companies scored and ranked based on their fundamentals \n - fundamentals are displayed here as percentiles: \n - our alogorithm calculates company scores based on fundamentals \n')
print('----------------------------------------------------')

rank_stocks(fundamentals_percentile)
fundamentals_percentile.sort_values('score', ascending = False, inplace = True)
fundamentals_percentile = fundamentals_percentile[['symbols','score','forwardPE','debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']]
fundamentals_percentile = fundamentals_percentile.reset_index(drop=True)
print(fundamentals_percentile)
print('\n ----------------------------------------------------')
print(str(removed_companies) + ' stocks removed due to missing data fields from Yahoo Finance')