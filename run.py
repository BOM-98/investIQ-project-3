import pandas as pd
import pandas_datareader.data as web
import numpy as np
import datetime as dt
from datetime import datetime
import yfinance as yf
from yahoo_fin import stock_info as si
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import HRPOpt
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

portfolio = choose_companies(fundamentals_percentile)

print('here is your portfolio of companies: \n')
print(portfolio)

portfolio_stocks = portfolio['symbols'].tolist()
print(portfolio_stocks)
portfolio_prices = combine_stocks(portfolio_stocks)

#Mean Variance Optimization 
# mu = mean_historical_return(portfolio_prices)
# S = CovarianceShrinkage(portfolio_prices).ledoit_wolf()
# ef = EfficientFrontier(mu, S)
# weights = ef.max_sharpe()
# cleaned_weights = ef.clean_weights()
# print(dict(cleaned_weights))
# ef.portfolio_performance(verbose=True)
latest_prices = get_latest_prices(portfolio_prices)

#Hierarchical Risk Parity (HRP)
port_returns = portfolio_prices.pct_change().dropna()
hrp = HRPOpt(port_returns)
hrp_weights = hrp.optimize()
weights = hrp.optimize()
hrp.portfolio_performance(verbose=True)
print(dict(hrp_weights))


print('Please input how much you would like to invest in your portfolio:')
print('There is a minimum limit of €100:')
investment = input("Enter your investment number here: ")
investment = int(investment)
da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=investment)
allocation, leftover = da.greedy_portfolio()
print("Discrete allocation:", allocation)
print("Funds remaining: ${:.2f}".format(leftover))