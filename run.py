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
    chosen_index = get_companies_list()
    symbols = scrape_company_tickers(chosen_index)
    fundamentals_data = collect_data(symbols)
    fundamentals_data['quarterlyReturn'] = process_data(symbols)
    print ('----------------------------------------------------')
    typewriter('Here are the fundamentals for your list of companies: \n')
    print('----------------------------------------------------')
    print(fundamentals_data)
    print('')
    fundamentals_information()
    fundamentals_data_dropna = fundamentals_data.dropna()
    removed_companies = fundamentals_data['symbol'].count() - fundamentals_data_dropna['symbol'].count()
    fundamentals_percentile = calculate_percentile_rank(fundamentals_data_dropna[['forwardPE', 'debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']])
    fundamentals_percentile['symbols'] = symbols
    fundamentals_percentile = fundamentals_percentile[['symbols','forwardPE','debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']]

    typewriter('----------------------------------------------------\n')
    typewriter('Here are your companies scored and ranked based on their fundamentals \n - fundamentals are displayed here as percentiles: \n - our alogorithm calculates company scores based on fundamentals \n')
    typewriter('----------------------------------------------------\n')

    rank_stocks(fundamentals_percentile)
    fundamentals_percentile.sort_values('score', ascending = False, inplace = True)
    fundamentals_percentile = fundamentals_percentile[['symbols','score','forwardPE','debtToEquity','forwardEps', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'quarterlyReturn']]
    fundamentals_percentile = fundamentals_percentile.reset_index(drop=True)
    print(fundamentals_percentile)
    print('\n ----------------------------------------------------')
    print(str(removed_companies) + ' stocks removed due to missing data fields from Yahoo Finance')

    portfolio = choose_companies(fundamentals_percentile)

    typewriter('We need to fetch the historical prices of your porfolio companies. \n')
    typewriter('This is used to calculate expected returns and your variance: \n')
    portfolio_stocks = portfolio['symbols'].tolist()
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
    print('Please input how much you would like to invest in your portfolio:')
    print('There is a minimum limit of €100:')
    investment = input("Enter your investment number here: ")
    investment = int(investment)
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=investment)
    allocation, leftover = da.greedy_portfolio()
    print("Discrete allocation:", allocation)
    print("Funds remaining: ${:.2f}".format(leftover))
    
    
    while True: 
        print("Press Enter to start the game again.")
        if input() == '':
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
typewriter("1: Expected Return\n")
typewriter("2: Portfolio Variance\n")
typewriter("3: Sharpe Ratio\n")
typewriter("Your goal is to get each of these scores as high as possible\n")
while True:
    typewriter("Press Enter to start.\n")
    if input() == '':
        main()
