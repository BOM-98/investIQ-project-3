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

def main():
    # Step 1: Choosing Index
    #Function to pick index
    chosen_index = get_companies_list()
    #Function to scrape tickers from chosen index
    symbols = scrape_company_tickers(chosen_index)
    #Function to scrape financial infromation from tickers that were scraped
    fundamentals_data = collect_data(symbols)
    
    # Step 2: Choosing stocks
    #Function to calculate quarterly returns from each stock from our index
    fundamentals_data['quarterlyReturn'] = process_data(symbols)
    print ('----------------------------------------------------')
    typewriter('Here are the fundamentals for your list of companies: \n')
    print('----------------------------------------------------')
    print(fundamentals_data)
    print('')
    #Function to provide information on each company stat / ratio
    fundamentals_information()
    #Remove companies with missing data
    fundamentals_data_dropna = fundamentals_data.dropna()
    #Calculate the number companies with missing data
    removed_companies = fundamentals_data['symbol'].count() - fundamentals_data_dropna['symbol'].count()
    #Calculate the percentiles for each company statistic / ratio
    fundamentals_percentile = calculate_percentile_rank(fundamentals_data_dropna[['forwardPE', 'debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']])
    fundamentals_percentile['symbols'] = symbols
    fundamentals_percentile = fundamentals_percentile[['symbols','forwardPE','debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']]
    typewriter('----------------------------------------------------\n')
    typewriter('Here are your companies scored and ranked based on their fundamentals \n - fundamentals are displayed here as percentiles: \n - The investIQ alogorithm calculates company scores based on fundamentals \n')
    typewriter('----------------------------------------------------\n')
    #Function to rank companies based on their fundamentals
    rank_stocks(fundamentals_percentile)
    #Function to sort companies based on their scores
    fundamentals_percentile.sort_values('score', ascending = False, inplace = True)
    fundamentals_percentile = fundamentals_percentile[['symbols','score','forwardPE','debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']]
    fundamentals_percentile = fundamentals_percentile.reset_index(drop=True)
    print(fundamentals_percentile)
    print('\n--------------------------------------------------------')
    print(str(removed_companies) + ' stocks removed due to missing data fields from Yahoo Finance')
    
    # Step 3: Optimize Portfolio
    #Return the number of companies the user wants to include in their portfolio
    portfolio = choose_companies(fundamentals_percentile)
    portfolio_stocks = portfolio['symbols'].tolist()
    #Return the historical closing prices for each stock in the portfolio
    portfolio_prices = combine_stocks(portfolio_stocks)
    latest_prices = get_latest_prices(portfolio_prices)
    
    # Step 4: Allocating Budget
    #Hierarchical Risk Parity Optimization(HRP)
    hpp_optimization(portfolio_prices, latest_prices)
    reset_program()    
    main()

            
typewriter("""\
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣤⣤⡀⠀⠀⠀⠀⠀⠀⠀⡤⠚⣉⠉⠲⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠶⠛⠉⠀⠀⢻⣿⣿⡀⠀⠀⠀⠀⠀⢸⠀⡞⠉⠙⠒⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣦⠀⠀⠀⠀⠀⢻⣿⣷⡄⠀⠀⠀⠀⠘⣄⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡿⣿⣿⣿⣿⣷⣀⠤⠒⠊⠉⠱⣶⣿⣆⠀⣀⣴⠂⠈⠢⡈⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢧⡈⢿⣿⡿⣋⣴⣀⣀⣀⣠⣤⡬⠭⠼⠻⣏⠀⠀⠀⠀⠈⠲⣌⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⣶⠀⠀⠀⠀⠀⠀⠀⠀⠻⣬⢋⣾⠿⠛⣋⠍⢁⠤⠀⠀⠀⠀⠈⠉⠳⡀⠀⠀⠀⠀⠈⠳⣌⠳⣄⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⣠⣤⡾⠀⢻⡀⠀⠀⠀⠀⠀⠀⠀⢀⣵⠟⣡⠖⠋⠀⠀⠁⠀⠀⠀⠀⠀⠀⠰⠂⢳⠀⠀⠀⠀⠀⠀⠈⣳⠾⠃⡷⠈⠒⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣀⡤⠞⡋⠉⠀⠀⠇⠀⠀⣿⠲⣤⣤⣄⡀⠀⠀⣼⠁⣼⡏⢐⠆⠀⠀⠀⠘⠃⠀⠀⠀⣄⠀⠀⢸⡇⢀⠀⠀⠀⠀⠀⡇⠠⡶⠁⡀⠀⠙⡄⠀⠀⠀⠀⠀⠀⠀⠀
⣼⠁⢀⠩⠔⠀⣀⣀⣀⣀⡼⢁⣾⣿⣿⣿⣿⣶⣤⣹⣆⣻⠓⠀⠀⠀⠀⠀⠀⠀⡠⠤⠐⠋⠉⠑⠚⠓⣻⠀⠀⠀⠀⠀⣧⡀⢧⣞⣠⢂⡰⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠳⠤⠴⠚⠛⠉⠉⠉⠉⠛⢳⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣍⡦⢄⣤⠀⢢⡄⠠⠎⠀⠀⠀⣠⣀⣀⣠⠔⠁⠀⠀⠀⢀⣿⣆⠻⢦⣌⡽⠋⠙⢮⡳⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣷⣄⠑⠢⠤⠤⠴⠋⠉⣀⡞⠁⠀⠀⠀⣀⣴⣿⣿⣿⣷⣤⡽⠃⠀⠀⠀⠙⢮⡳⣄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⡏⠙⢒⠦⠤⠤⠴⢚⣿⣿⣶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠙⢮⡳⣄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⡄⣸⡤⠖⠢⣤⠇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢮⡳⣄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣷⠉⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠊
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⢟⣵⣶⣶⣝⣿⣿⣆⠀⠀⠀⠀⢸⣿⣿⣿⡿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣆⠀⠀⠀⠀⠀⠀⣰⣟⣵⣿⣿⣿⣿⣿⣿⡿⠛⢷⡀⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣷⣶⣤⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠈⣧⣴⡄⢀⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⣴⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⡙⢿⣿⡟⠛⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣌⢿⡇⠀⢀⣤⣾⡍⢻⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⠿⠟⠀⠳⠀⡀⠀⣼⠃⢀⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠁⣀⣼⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣀⣰⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠁⠀⢹⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡳⠀⠀⢸⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢸⢿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⠦⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n""", 0.0025)
typewriter("------------------------------------\n")
typewriter('         Welcome to InvestIQ!       \n')
typewriter("------------------------------------\n")        
typewriter("InvestIQ helps you create the best possible portfolio of stocks from US companies \n")
typewriter("InvestIQ uses live data to create your portfolio \n")
typewriter("InvestIQ does this in four steps\n")
typewriter("Step 1: choosing which group of companies to use in your portfolio\n")
typewriter("Step 2: ranking those companies using our algorithm\n")
typewriter("Step 3: creating the optimal portfolio from these companies to maxmize your returns and minimize risk\n")
typewriter("Step 4: determining how many shares to buy in each company based on your budget\n")
typewriter("At the end of the program, you will be given three metrics\n")
typewriter("1: Expected Annual Return\n")
typewriter("2: Annual Volatility\n")
typewriter("3: Sharpe Ratio\n")
typewriter("Your goal is to get 1 & 3 as high as possible and 2 as low as possible\n")
while True:
    typewriter("Press Enter to start.\n")
    if input() == '':
        main()
