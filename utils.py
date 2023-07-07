# Write your code to expect a terminal of 80 characters wide and 24 rows high
from math import sqrt
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import random
from functools import reduce
import datetime as dt
from datetime import datetime
import yfinance as yf
from yahoo_fin import stock_info as si
import scipy.stats as stats
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import HRPOpt
import time

start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()

def get_companies_list():
    """
    Get the index from which stocks are to be picked from the user.
    """
    # URL of the Wikipedia page from which to scrape the S&P 500 company list
    url_sap_500 = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    # URL of the Wikipedia page from which to scrape the Dow Jones company list
    url_dow = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
    # URL of the Wikipedia page from which to scrape the S&P 100 company list
    url_sap_100 = 'https://en.wikipedia.org/wiki/S%26P_100'
    typewriter("------------------------------------\n")
    typewriter('  Step 1: Choosing Your Index       \n')
    typewriter("------------------------------------\n")
    typewriter("Please choose which stock index you would like to pick stocks from.\n")
    typewriter("The larger the index, the longer it will take to analyse the stocks\n")
    typewriter("1: To select the 30 companies from the Dow Jones (fast analysis time ~ 1 min) enter 'dow'\n")
    typewriter("2: To select the 100 companies from the S&P100 (slow analysis time ~ 3 min) enter 'sap100': \n")
    typewriter("3: To select the 500 companies from the S&P500 (slowest analysis time ~ 6 min) enter 'sap500'\n")
    typewriter("Example: 'dow' chooses option 1 \n")
    
    while True:
        index_choice = input("Enter your index here: ")

        if validate_index(index_choice):
            print("Input is valid")
            break

    if index_choice == 'dow':
        tickers_source = url_dow
    elif index_choice == 'sap100':
        tickers_source = url_sap_100
    elif index_choice == 'sap500':
        tickers_source = url_sap_500

    return tickers_source


def validate_index(index_choice):
    """
    Determines whether the use choice of index was valid
    """
    try:
        if index_choice != 'dow' and index_choice != 'sap100' and index_choice != 'sap500':
            raise ValueError(
                f"You have not chosen a valid option: choose either 'dow', 'sap100', or 'sap500' "
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


def scrape_company_tickers(index):
    """
    Scrape the company tickers from the Wikipedia page of a given index.

    This function scrapes the company tickers from the Wikipedia page of the S&P 500, S&P 100, or Dow Jones Industrial Average index. 
    It uses pandas to scrape the tables from the Wikipedia page and extracts the 'Symbol' column, which contains the ticker symbols.

    Parameters:
    index (str): The URL of the Wikipedia page of the index. It should be one of the following:
        - 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies' for the S&P 500 index
        - 'https://en.wikipedia.org/wiki/S%26P_100' for the S&P 100 index
        - 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average' for the Dow Jones Industrial Average index

    Returns:
    symbols (Series): A pandas Series containing the ticker symbols of the companies in the index.
    """
    # Use pandas to scrape the tables from the Wikipedia page
    # The first table on the page is the one we want
    # The ticker symbol is in the 'Symbol' column
    if index == 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies':
        tables = pd.read_html(index)
        tabel = tables[0]
        symbols = tabel['Symbol']
    elif index == 'https://en.wikipedia.org/wiki/S%26P_100':
        tables = pd.read_html(index)
        tabel = tables[2]
        symbols = tabel['Symbol']
    elif index == 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average':
        tables = pd.read_html(index)
        tabel = tables[1]
        symbols = tabel['Symbol']
    return symbols

def calculate_percentile_rank(df):
    typewriter("------------------------------------\n")
    typewriter('  Step 2: Ranking Your Companies       \n')
    typewriter("------------------------------------\n")
    ranked_percentiles = df.apply(lambda x: [stats.percentileofscore(
        x, a, 'rank') if pd.notnull(a) else np.nan for a in x])

    columns_to_inverse = ['forwardPE', 'debtToEquity']

    for column in columns_to_inverse:
        if column in ranked_percentiles:
            ranked_percentiles[column] = 100 - ranked_percentiles[column]
    ranked_percentiles = ranked_percentiles.round(2)
    return ranked_percentiles


# rank the stocks by percentiles
def rank_stocks(df):
    """
    Using a variety of criteria, this function determines a score for each stock from the DataFrame passed as a parameter. 


    The score is the sum of the products of each factor's weight and its respective weighting for each factor. 
    Forward PE, Forward EPS, Debt to Equity, Return on Equity, Return on Assets, Revenue Growth, Quick Ratio, 
    and Quarterly Return are the aspects taken into account.

    Factor_weights = [['forwardPE', 0.1],['forwardEps', 0.1],['debtToEquity', 0.1],['returnOnEquity', 0.1],['returnOnAssets', 0.1],['revenueGrowth', 0.2], ['quickRatio', 0.1], ['quarterlyReturn', 0.2]]

    Parameters:
    df (pandas.DataFrame): A DataFrame containing the factors for each stock. The DataFrame 
    should have the factors as columns and each row represents a stock.

    Returns:
    pandas.DataFrame: The input DataFrame with an additional column 'score' that contains the 
    calculated score for each stock.

    Example:
    >>> df =            forwardPE  debtToEquity  forwardEps  returnOnEquity  returnOnAssets  revenueGrowth  quickRatio  quarterlyReturn
    symbols                                                                                                                 
    MMM                    81.82         36.36       50.00           77.27           40.91          13.64       40.91            13.64
    AXP                    50.00         22.73       77.27           63.64           18.18          90.91       86.36            72.73
    AMGN                   68.18         -0.00       90.91          100.00           59.09          31.82      100.00             9.09
    ... })
    >>> rank_stocks(df)
    """

    # step 2: multiply each factor percentile by its weighting to get a score
    df['score'] = df['forwardPE'] * 0.1 + df['forwardEps'] * 0.1 + df['debtToEquity'] * 0.1 + df['returnOnEquity'] * \
        0.1 + df['returnOnAssets']*0.1 + df['revenueGrowth'] * 0.2 + \
        df['quickRatio'] * 0.1 + df['quarterlyReturn'] * 0.2


def calculate_quarterly_return(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
        data['quarterly_return'] = data['Adj Close'].resample(
            'Q').ffill().pct_change()
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


def collect_data(symbols):
    typewriter('first we need to fetch the company financials for each stock...\n')
    stocks_list = []
    for ticker in symbols:
        print(f"Fetching financial data for {ticker}")
        stocks_list.append(yf.Ticker(ticker).info)

    typewriter('InvestIQ is calculating your company fundamentals - this may take a minute or two...\n')
    # Create a list of fundamental information that we are interested in
    fundamentals = ['symbol', 'marketCap', 'forwardPE', 'priceToBook', 'forwardEps',
                    'debtToEquity', 'returnOnEquity', 'returnOnAssets', 'revenueGrowth', 'quickRatio', 'dividendYield']
    # Create a DataFrame from the info dictionary
    stock_data = pd.DataFrame(stocks_list)
    # # Select only the columns in the fundamentals list
    fundamentals_data = stock_data[fundamentals]
    return fundamentals_data


def return_portfolios(expected_returns, cov_matrix):
    np.random.seed(1)
    port_returns = []
    port_volatility = []
    stock_weights = []

    selected = (expected_returns.axes)[0]

    num_assets = len(selected)
    num_portfolios = 5000

    for single_portfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, expected_returns)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

        portfolio = {'Returns': port_returns,
                     'Volatility': port_volatility}

    for counter, symbol in enumerate(selected):
        portfolio[symbol + ' Weight'] = [Weight[counter]
                                         for Weight in stock_weights]

    df = pd.DataFrame(portfolio)

    column_order = ['Returns', 'Volatility'] + \
        [stock+' Weight' for stock in selected]

    df = df[column_order]

    return df


def optimal_portfolio(returns):
    n = returns.shape[1]
    returns = np.transpose(returns.as_matrix())

    N = 100
    mus = [10**(5.0 * t/N - 1.0) for t in range(N)]

    # Convert to cvxopt matrices
    S = opt.matrix(np.cov(returns))
    pbar = opt.matrix(np.mean(returns, axis=1))

    # Create constraint matrices
    G = -opt.matrix(np.eye(n))   # negative n x n identity matrix
    h = opt.matrix(0.0, (n, 1))
    A = opt.matrix(1.0, (1, n))
    b = opt.matrix(1.0)

    # Calculate efficient frontier weights using quadratic programming
    portfolios = [solvers.qp(mu*S, -pbar, G, h, A, b)['x']
                  for mu in mus]
    # CALCULATE RISKS AND RETURNS FOR FRONTIER
    returns = [blas.dot(pbar, x) for x in portfolios]
    risks = [np.sqrt(blas.dot(x, S*x)) for x in portfolios]
    # CALCULATE THE 2ND DEGREE POLYNOMIAL OF THE FRONTIER CURVE
    m1 = np.polyfit(returns, risks, 2)
    x1 = np.sqrt(m1[2] / m1[0])
    # CALCULATE THE OPTIMAL PORTFOLIO
    wt = solvers.qp(opt.matrix(x1 * S), -pbar, G, h, A, b)['x']
    return np.asarray(wt), returns, risks


def choose_companies(df):
    """
    Get the number of companies the user wants to pull from the scored list.
    """
    typewriter("-----------------------------------------------------------\n")
    typewriter("Your companies are now ranked based on their fundamentals in the table above.\n")
    typewriter("You can see the 'score' assigned to each one of them under the 'score' column \n")
    typewriter("Please choose how many companies you would like to include from this list in your portfolio\n")
    typewriter("Example: '10' chooses the top 10 companies from this list \n")
    typewriter("-----------------------------------------------------------\n")
    typewriter("You cannot choose more than the number of companies listed or 50 companies in the case of the S&P 100 and 500 \n")
    while True:
        portfolio_size = input("Enter your number here: ")
        portfolio_size = int(portfolio_size)

        if validate_number(portfolio_size, df):
            print("Data is valid")
            break

    portfolio_df = df.head(portfolio_size)
    
    typewriter("You have chosen your portfolio\n")
    typewriter("The InvestIQ algorithm will now determine the allocation that will get the highest returns with the lowest risk\n")

    return portfolio_df


def validate_number(portfolio_size, df):
    """
    Determines whether the choice of companies was valid
    """
    try:
        if int(portfolio_size) > 50 or int(portfolio_size) > df['symbols'].count():
            raise ValueError(
                f"You have not chosen a valid portfolio size"
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True

def pull_returns(ticker, start, end):
    try:
        print(f"Fetching pricing data for {ticker}")
        data = yf.download(ticker, start=start, end=end, progress=False)
        return data['Adj Close']
    except Exception as e:
        print(f"Failed to download data for {ticker}. Error: {e}")
        return np.nan


def combine_stocks(tickers):
    typewriter("------------------------------------\n")
    typewriter(' Step 3: Optimizing Your Portfolio  \n')
    typewriter("------------------------------------\n")
    typewriter('InvestIQ needs to fetch the historical prices of your porfolio companies. \n')
    typewriter('This is used to calculate expected returns and your variance: \n')
    data_frames = pd.DataFrame()
    for i in tickers:
        data_frames[i] = (pull_returns(i, start, end))
    typewriter('Portfolio weights have been caluclated \n')
    return data_frames

def typewriter(input_text, speed = 0.001):
        for letter in input_text:
            print(letter, end='', flush=True)
            time.sleep(speed)
        
def fundamentals_information():
    typewriter("This is a table of all your important company fundamentals\n")
    typewriter("If you would like to learn more about any of the ratios in the column header, enter in the name\n")
    typewriter("Otherwise to continue to the next step and rank your companies press enter\n")
    
    while True: 
        choice = input("Choose a heading or press Enter:")
        if choice == '':
            break
        elif choice == 'marketCap':
            typewriter("------------------------------------\n")
            typewriter('       Market Capitalization        \n')
            typewriter("------------------------------------\n")
            print("""Market capitalization, commonly known as market cap refers to the overall value of a companys' shares of stock.
This valuation is determined by multiplying the number of outstanding shares with the current market price per share.
To illustrate suppose a company has 1 million outstanding shares and each share is currently priced at $50.
In this scenario. The market cap of that company would amount to $50 million.
Investors frequently rely on market cap as a tool to compare companies and make informed decisions regarding which stocks to purchase.
Additionally market cap is utilized for categorizing companies into distinct sizes such as small cap, mid cap and large cap.\n""")
        elif choice == 'forwardPE':
            typewriter("------------------------------------\n")
            typewriter('       Forward Price to Earnings    \n')
            typewriter("------------------------------------\n")  
            print("""The Forward Price-to-Earnings (Forward P/E) ratio is a way to measure how much investors are willing to pay for a company's future earnings.
In the stock market, a company's Forward P/E ratio is calculated by dividing the current share price by the estimated earnings per share for the next 12 months.
A lower Forward P/E ratio could mean that the stock is undervalued, or it could mean that analysts expect the company's earnings to grow.
A higher Forward P/E ratio could mean the stock is overvalued, or it could mean that investors are willing to pay a premium because they expect strong earnings growth.
Whether a Forward P/E ratio is 'good' or 'bad' can depend on whether the company's future earnings live up to expectations.\n""")
        elif choice == 'priceToBook':
            typewriter("------------------------------------\n")
            typewriter('       Price to Book                \n')
            typewriter("------------------------------------\n")
            print("""The Price-to-Book (P/B) ratio is a financial metric used to assess the market's valuation of a company relative to its book value.\n
The book value is essentially the company's net worth if it were to be liquidated, i.e., all its assets sold and all its debts paid off. It's calculated as the total value of the company's assets minus its liabilities.
The "price" in the P/B ratio refers to the market value of the company, which is determined by the current price of the company's shares times the number of shares outstanding.
The P/B ratio thus compares the market's valuation of the company (price) to its intrinsic value (book value). A P/B ratio less than 1 may indicate that the company's stock is undervalued, while a P/B ratio greater than 1 may suggest it's overvalued.
However, these interpretations can vary depending on the industry and other factors.\n""")
        elif choice == 'forwardEps':
            typewriter("------------------------------------\n")
            typewriter('       Forward EPS                  \n')
            typewriter("------------------------------------\n")
            print("""
Forward Earnings Per Share (EPS) is a measure of a company's predicted profitability for the next financial period. 
It's calculated by taking estimated earnings for a future period and dividing it by the number of outstanding shares of the company's stock. 

This measure is used by investors to assess the company's future profitability and to help determine if the stock is overvalued or undervalued. 
A higher Forward EPS suggests that the company is expected to be more profitable in the future, which could make the stock more attractive to investors. 
However, it's important to remember that these are only estimates and actual results may vary.\n
""")
        elif choice == 'debtToEquity':
            typewriter("------------------------------------\n")
            typewriter('            Debt to Equity          \n')
            typewriter("------------------------------------\n")
            print("""
The Debt to Equity ratio is a financial metric that provides a snapshot of a company's financial leverage. 
It is calculated by dividing a company's total liabilities by its shareholder equity. 
This ratio is used to evaluate a company's financial leverage and risk. A high Debt to Equity ratio often means that a company has been aggressive in financing its growth with debt, which can result in volatile earnings due to the additional interest expense. 
On the other hand, a low Debt to Equity ratio might indicate that a company is not taking advantage of the increased profits that financial leverage may bring. 
Investors often use this ratio to compare the capital structure of different companies.
""")
        elif choice == 'returnOnEquity':
            typewriter("------------------------------------\n")
            typewriter('            Return on Equity        \n')
            typewriter("------------------------------------\n")
            print("""
Return on Equity (ROE) is a measure of financial performance that is calculated by dividing net income by shareholders' equity. 
It is expressed as a percentage and indicates how well a company is generating income from the money shareholders have invested. 
In other words, ROE tells you how good a company is at rewarding its shareholders for their investment. 
A high ROE could mean that a company is effectively generating profits, but it's always important to compare a company's ROE with its industry average or other competing companies. 
On the other hand, a low ROE might suggest that the company is not effectively using its resources to generate profits.
""")
        elif choice == 'returnOnAssets':
            typewriter("------------------------------------\n")
            typewriter('            Return on Assets        \n')
            typewriter("------------------------------------\n")
            print("""
Return on Assets (ROA) is a financial ratio that shows the percentage of profit a company earns in relation to its overall resources. 
It is calculated by dividing a company's annual earnings by its total assets and is displayed as a percentage. 
In other words, ROA tells you how efficiently a company is converting the money it has to invest into net income. 
A high ROA indicates that the company is earning more money on less investment, meaning it is operating efficiently and using its assets effectively to generate profits. 
On the other hand, a low ROA may indicate that the company is investing a lot of money in assets, but it's not generating a lot of profit from these investments.\n
""")
        elif choice == 'revenueGrowth':
            typewriter("------------------------------------\n")
            typewriter('            Revenue Growth          \n')
            typewriter("------------------------------------\n")
            print("""
Revenue Growth is a financial metric that is used to measure the rate at which a company's income, also known as sales revenue, is increasing. 
This gives investors and other stakeholders an idea of how quickly the company is growing its sales revenue.\n
""")
        elif choice == 'quickRatio':
            typewriter("------------------------------------\n")
            typewriter('            Quick Ratio             \n')
            typewriter("------------------------------------\n")
            print("""
Quick Ratio, also known as the acid-test ratio, is a liquidity ratio that measures a company's ability to pay off its current liabilities without relying on the sale of inventory. 
It's calculated as (Current Assets - Inventory) / Current Liabilities. A higher quick ratio means a more liquid current position.\n
""")
        elif choice == 'dividendYield':
            typewriter("------------------------------------\n")
            typewriter('            Dividend Yield          \n')
            typewriter("------------------------------------\n")
            print("""
Dividend Yield is a financial ratio that shows how much a company pays out in dividends each year relative to its stock price. 
It's calculated as Annual Dividends per Share / Price per Share. It's often expressed as a percentage. 
A higher dividend yield means the investor is getting a higher return on their investment.\n
""")
        elif choice == 'quarterlyReturn':
            typewriter("------------------------------------\n")
            typewriter('            Quarterly Return        \n')
            typewriter("------------------------------------\n")
            print("""
Quarterly Return is a measure of an investment's change in value over a three-month period. 
It's calculated as (End Value - Start Value) / Start Value. It's often expressed as a percentage. 
A higher quarterly return means the investment has grown in value over the quarter.\n
""")
        else:
            print("invalid input, try again:")
            
def hpp_optimization(portfolio_prices, latest_prices):
    port_returns = portfolio_prices.pct_change().dropna()
    hrp = HRPOpt(port_returns)
    hrp_weights = hrp.optimize()
    weights = hrp.optimize()
    typewriter("-----------------------------------------\n")
    typewriter(' Step 4: Calculating Shares To Purchase  \n')
    typewriter("-----------------------------------------\n")
    typewriter('Please input how much you would like to invest in your portfolio:\n')
    typewriter('There is a minimum limit of €500:\n')
    while True:
        investment = input("Enter your investment number here: ")
        investment = int(investment)
        if investment > 499:
            break
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=investment)
    allocation, leftover = da.greedy_portfolio()
    print("Your recommended allocation of shares 'stock':'number of shares'\n", allocation)
    print("Funds remaining: ${:.2f}".format(leftover))
    typewriter("--------------------------------------\n")
    hrp.portfolio_performance(verbose=True)
    typewriter("--------------------------------------\n")
        
def reset_program():
    while True: 
        answer = input("Press Enter to start InvestIQ again, or type 1 to learn about expected annual return, 2 to learn about annual volatility and 3 to learn about the sharpe ratio!.")
        if answer == '':
            break
        elif answer == '1':
            typewriter("------------------------------------\n")
            typewriter('      Expected Annual Return        \n')
            typewriter("------------------------------------\n")
            print("""
Expected Annual Return is a projection of the potential earnings or profit from an investment over a one year period. 
It's calculated based on historical data and future predictions. It's often expressed as a percentage. 
A higher expected annual return means the investment is predicted to yield a higher return over the course of a year. 
However, it's important to remember that these are just estimates and actual returns may vary.
""")
        elif answer == '2':
            typewriter("------------------------------------\n")
            typewriter('        Annual Volatility           \n')
            typewriter("------------------------------------\n")
            print("""
Annual Volatility is a statistical measure of the dispersion of returns for a given security or market index over a one year period. 
It is commonly associated with the risk level of the investment. 
High volatility means that the price of the security can change dramatically over a short time period in either direction, which can be seen as more risky.
On the other hand, low volatility would mean that a security's value does not fluctuate dramatically, but changes in value at a steady pace over a period of time.
""")
        elif answer == '3':
            typewriter("------------------------------------\n")
            typewriter('            Sharpe Ratio              \n')
            typewriter("------------------------------------\n")
            print("""
The Sharpe Ratio is a measure used by investors to understand the return of an investment compared to its risk. 
It is the average return earned in excess of the risk-free rate per unit of volatility or total risk. 
The greater a portfolio's Sharpe ratio, the better its risk-adjusted performance. 
If the Sharpe ratio is negative, it means the risk-free rate is greater than the portfolio's return, or the portfolio's return is expected to be negative. 
In this case, a riskless investment would perform better.
Generally a Sharpe ratio above 1 is considered good, while a sharpe ratio above 1.5 is considered excellent
""")
        else:
            print("invalid input, try again")