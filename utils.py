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
import requests
import time
from urllib.error import HTTPError

# The start and end date range for the stock data we will be analysing
start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()
index_choice = ""


def get_companies_list():
    """
    The function prompts the user to continue analysing
    the dow jones stock index .The user needs to input their
    choice, which is later validated with the
    `validate_index` function. Once marked valid,
    the function returns the relevant URL of a
    Wikipedia page with information on the Dow Jones index.

    Args:
        None

    Returns:
        str: The URL of the Wikipedia page that lists
        the companies in the chosen index.

    Raises:
        ValueError: If the user's input is not 'y' or 'Y
    """

    # URL of the Wikipedia page from which to scrape
    # the Dow Jones company list
    url_dow = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"

    typewriter("------------------------------------\n")
    typewriter("  Step 1: Constructing Your Index   \n")
    typewriter("------------------------------------\n")
    typewriter("The program will gather your stocks.\n")
    typewriter("The stocks are from the Dow Jones Industrial \
 Average (30 stocks)\n")

    while True:
        index_choice = input("Enter 'y' or 'Y to continue:\n")

        if validate_index(index_choice):
            print("Input is valid")
            break

    if index_choice == "y":
        tickers_source = url_dow
    elif index_choice == "Y":
        tickers_source = url_dow

    return tickers_source


def validate_index(index_choice):
    """
    Validates the user's choice of stock index.

    This function checks if the user's input matches:
    'Y' or 'y''. If it doesn't, a
    ValueError is raised and the function returns
    False. If the input is valid, the function returns True.

    Args:
        index_choice (str): The user's input representing
        their choice of stock index.

    Returns:
        bool: True if the input is valid, False
        otherwise.

    Raises:
        ValueError: If the input is not '1',
         or '2'.
    """
    try:
        if (
            index_choice != "y"
            and index_choice != "Y"
        ):
            raise ValueError(
                f"You have not chosen a valid option: choose\
 either 'y', or 'Y'"
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


def scrape_company_tickers(index):
    """
    Extract the company tickers from an index's Wikipedia page.

    This function copies the stock tickers from the Dow Jones Industrial
    Average index pages on Wikipedia.
    It pulls the tables from the Wikipedia page using
    pandas and then extracts the ticker symbols from the 'Symbol' column.

    Parameters:
    index (str): The URL of the Wikipedia page of the index.
        - 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
        for the Dow Jones Industrial Average index

    Returns:
    symbols (Series): A pandas Series containing the ticker
    symbols of the companies in the index.
    """
    if index == "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies":
        tables = pd.read_html(index)
        tabel = tables[0]
        symbols = tabel["Symbol"]
    elif index == "https://en.wikipedia.org/wiki/S%26P_100":
        tables = pd.read_html(index)
        tabel = tables[2]
        symbols = tabel["Symbol"]
    elif index == "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average":
        tables = pd.read_html(index)
        tabel = tables[1]
        symbols = tabel["Symbol"]
    return symbols


def collect_data(symbols):
    """
    Retrieves and processes financial data for the Dow Jones.

    The yfinance library is used by this function to loop through a
    list of stock symbols and retrieve financial data for each one.
    After retrieving the data, it creates a DataFrame from it and
    selects a subset of it that corresponds to a preset list of
    important financial metrics.
    The resultant DataFrame is given back.

    Args:
        symbols (list): A list of strings representing the
        stock symbols for which data is to be retrieved.

    Returns:
        pandas.DataFrame: A DataFrame containing the
        selected financial data for each stock symbol.
        The DataFrame's columns correspond to the
        selected financial metrics, and its rows correspond
        to the stock symbols.
    Raises:
        KeyError: If the fetched data does not contain
        one of the chosen financial measures.
    """

    fundamentals_data = pd.read_csv('fundamentals_data_dow.csv')
    symbols = fundamentals_data["symbol"]
    return fundamentals_data, symbols


def process_data(tickers, start=start, end=end):
    """
    Processes a list of stock tickers by calculating
    their quarterly returns.

    This function uses the 'calculate_quarterly_return'
    function to iteratively calculate the quarterly return
    for each stock ticker in a list of tickers.
    The calculation's beginning and ending dates are
    specified in the file.
    Lists of the calculated returns are returned
    by the function.

    Args:
        tickers (list): A list of strings representing
        the stock tickers to process.

    Returns:
        list: A list of floats representing the calculated
        quarterly returns for each stock ticker.

    Raises:
        NameError: If `start` or `end` are not defined
        elsewhere in the code.
        Any exceptions raised by
        `calculate_quarterly_return`.
    """
    returns_list = []
    for ticker in tickers:
        returns_list.append(calculate_quarterly_return(ticker, start, end))
    return returns_list


def calculate_quarterly_return(ticker, start, end):
    """
    Determines the quarterly return for a
    specific stock ticker over a given time period.

    Using the yfinance package, this function downloads
    historical data for a specified stock ticker, resamples the
    data to a quarterly frequency, and then computes the percentage
    change in the adjusted closing price.
    The function outputs the last quarterly return.

    Args:
        ticker (str): A string representing the stock ticker
        to fetch data for.
        start (str): A string representing the start date
        for the data fetch in 'YYYY-MM-DD' format.
        end (str): A string representing the end date for
        the data fetch in 'YYYY-MM-DD' format.

    Returns:
        float: The quarterly return for the quarter ending
        on '2023-06-30', or np.nan if the data fetch fails.

    Raises:
        Exception: If the data fetch fails for any reason.
    """
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
        data["quarterly_return"] = \
            data["Adj Close"].resample("Q").ffill().pct_change()
        return data.loc["2023-06-30", "quarterly_return"]
    except Exception as e:
        print(
            f"Failed to download data for {ticker}. Error: {e} - continuing\
            with remaining tickers."
        )
        return np.nan


def fundamentals_information():
    """
    Information on several financial fundamentals is provided.

    The user can find out additional information about any of
    the ratios listed in the column header using this function,
    which shows a table of significant company basics.
    The user can press enter to move on to the next phase and
    rank the businesses or enter the name of a ratio to read more about it.
    Market Capitalization, Forward Price to Earnings, Price to Book,
    Forward EPS, Debt to Equity, Return on Equity, Return on Assets,
    Revenue Growth, Quick Ratio, Dividend Yield, and Quarterly Return
    are among the financial fundamentals covered by the function.
    The function use a while loop to repeatedly elicit input from
    the user up until the user presses enter, at which point the
    function is terminated.

    Raises:
        Exception: If the user enters an invalid input, the function
        prints an error message and asks for input again.
    """
    typewriter("This is a table of all your important company fundamentals\n")
    typewriter(
        "If you would like to learn more about any of the ratios in the\
 column header, enter in:\n"
    )
    print("1 for marketCap")
    print("2 for forwardPE")
    print("3 for priceToBook")
    print("4 for forwardEps")
    print("5 for debtToEquity")
    print("6 for returnOnEquity")
    print("7 for returnOnAssets")
    print("8 for revenueGrowth")
    print("9 for quickRatio")
    print("10 for dividendYield")
    print("11 for quarterlyReturn")

    typewriter(
        "Otherwise to continue to the next step and rank your companies\
 press enter\n"
    )

    while True:
        choice = input("Choose a number or press Enter:\n")
        if choice == "":
            break
        elif choice == "1":
            typewriter("------------------------------------\n")
            typewriter("       Market Capitalization        \n")
            typewriter("------------------------------------\n")
            print(
                """Market capitalization, commonly known as market cap
refers to the overall value of a companys' shares of stock.
This valuation is determined by multiplying the number of outstanding
shares with the current market price per share.
To illustrate suppose a company has 1 million outstanding shares
and each share is currently priced at $50.
In this scenario. The market cap of that company would amount to $50 million.
Investors frequently rely on market cap as a tool to compare companies and
make informed decisions regarding which stocks to purchase.
Additionally market cap is utilized for categorizing companies into
distinct sizes such as small cap, mid cap and large cap.\n"""
            )
        elif choice == "2":
            typewriter("------------------------------------\n")
            typewriter("       Forward Price to Earnings    \n")
            typewriter("------------------------------------\n")
            print(
                """The Forward Price-to-Earnings (Forward P/E) ratio is
a way to measure how much investors are willing to pay
for a company's future earnings.
In the stock market, a company's Forward P/E ratio is calculated
by dividing the current share price by the estimated earnings
per share for the next 12 months.
A lower Forward P/E ratio could mean that the stock is undervalued,
or it could mean that analysts expect the company's earnings to grow.
A higher Forward P/E ratio could mean the stock is overvalued, or it
could mean that investors are willing to pay a premium because
they expect strong earnings growth.
Whether a Forward P/E ratio is 'good' or 'bad' can depend on
whether the company's future earnings live up to expectations.\n"""
            )
        elif choice == "3":
            typewriter("------------------------------------\n")
            typewriter("       Price to Book                \n")
            typewriter("------------------------------------\n")
            print(
                """The Price-to-Book (P/B) ratio is a financial metric
                used to assess the market's valuation of a company relative
                to its book value.\n
The book value is essentially the company's net worth if it were to be
liquidated,
i.e., all its assets sold and all its debts paid off. It's calculated
as the total value of the company's assets minus
its liabilities.
The "price" in the P/B ratio refers to the market value of the company,
which is determined by the current price of the company's shares times
the number of shares outstanding.
The P/B ratio thus compares the market's valuation of the company
(price) to its intrinsic value (book value). A P/B ratio less than
1 may indicate that the company's stock is undervalued, while a
P/B ratio greater than 1 may suggest it's overvalued.
However, these interpretations can vary depending on the industry and
other factors.\n"""
            )
        elif choice == "4":
            typewriter("------------------------------------\n")
            typewriter("       Forward EPS                  \n")
            typewriter("------------------------------------\n")
            print(
                """
Forward Earnings Per Share (EPS) is a measure of a company's predicted
profitability for the next financial period.
It's calculated by taking estimated earnings for a future period and
dividing it by the number of outstanding shares of the company's stock.

This measure is used by investors to assess the company's future profitability
and to help determine if the stock is overvalued or undervalued.
A higher Forward EPS suggests that the company is expected to be more
profitable in the future, which could make the stock more attractive
to investors.
However, it's important to remember that these are only estimates and
actual results may vary.\n
"""
            )
        elif choice == "5":
            typewriter("------------------------------------\n")
            typewriter("            Debt to Equity          \n")
            typewriter("------------------------------------\n")
            print(
                """
The Debt to Equity ratio is a financial metric that provides a snapshot
of a company's financial leverage.
It is calculated by dividing a company's total liabilities by its
shareholder equity.
This ratio is used to evaluate a company's financial leverage and risk.
A high Debt to Equity ratio often means that a company has been aggressive
in financing its growth with debt, which can result in volatile earnings
due to the additional interest expense.
On the other hand, a low Debt to Equity ratio might indicate that a company
is not taking advantage of the increased profits that financial
leverage may bring.
Investors often use this ratio to compare the capital structure of
different companies.
"""
            )
        elif choice == "6":
            typewriter("------------------------------------\n")
            typewriter("            Return on Equity        \n")
            typewriter("------------------------------------\n")
            print(
                """
Return on Equity (ROE) is a measure of financial performance that
is calculated by dividing net income by shareholders' equity.
It is expressed as a percentage and indicates how well a company
is generating income from the money shareholders have invested.
In other words, ROE tells you how good a company is at rewarding
its shareholders for their investment.
A high ROE could mean that a company is effectively generating
profits, but it's always important to compare a company's ROE
with its industry average or other competing companies.
On the other hand, a low ROE might suggest that the company is
not effectively using its resources to generate profits.
"""
            )
        elif choice == "7":
            typewriter("------------------------------------\n")
            typewriter("            Return on Assets        \n")
            typewriter("------------------------------------\n")
            print(
                """
Return on Assets (ROA) is a financial ratio that shows the percentage
of profit a company earns in relation to its overall resources.
It is calculated by dividing a company's annual earnings by its total
assets and is displayed as a percentage.
In other words, ROA tells you how efficiently a company is converting
the money it has to invest into net income.
A high ROA indicates that the company is earning more money on less
investment, meaning it is operating efficiently and using its assets
effectively to generate profits.
On the other hand, a low ROA may indicate that the company is investing
a lot of money in assets, but it's not generating a lot of profit from
these investments.\n
"""
            )
        elif choice == "8":
            typewriter("------------------------------------\n")
            typewriter("            Revenue Growth          \n")
            typewriter("------------------------------------\n")
            print(
                """
Revenue Growth is a financial metric that is used to measure the rate
at which a company's income, also known as sales revenue, is increasing.
This gives investors and other stakeholders an idea of how quickly
the company is growing its sales revenue.\n
"""
            )
        elif choice == "9":
            typewriter("------------------------------------\n")
            typewriter("            Quick Ratio             \n")
            typewriter("------------------------------------\n")
            print(
                """
Quick Ratio, also known as the acid-test ratio, is a liquidity ratio
that measures a company's ability to pay off its current liabilities
without relying on the sale of inventory.
It's calculated as (Current Assets - Inventory) / Current Liabilities.
A higher quick ratio means a more liquid current position.\n
"""
            )
        elif choice == "10":
            typewriter("------------------------------------\n")
            typewriter("            Dividend Yield          \n")
            typewriter("------------------------------------\n")
            print(
                """
Dividend Yield is a financial ratio that shows how much a company
pays out in dividends each year relative to its stock price.
It's calculated as Annual Dividends per Share / Price per Share.
It's often expressed as a percentage.
A higher dividend yield means the investor is getting a higher
return on their investment.\n
"""
            )
        elif choice == "11":
            typewriter("------------------------------------\n")
            typewriter("            Quarterly Return        \n")
            typewriter("------------------------------------\n")
            print(
                """
Quarterly Return is a measure of an investment's change in value
over a three-month period.
It's calculated as (End Value - Start Value) / Start Value.
It's often expressed as a percentage.
A higher quarterly return means the investment has grown in
value over the quarter.\n
"""
            )
        else:
            print("invalid input, try again:")
            print("make sure you have no spaces\
                after your number")


def calculate_percentile_rank(df):
    """
    Calculates the percentile rank for each value in the DataFrame.

    Determines each value's percentile rating for the DataFrame.
    Each value in the DataFrame is subjected to this function's application
    of the percentileofscore function from the scipy.stats module.
    The percentage of values in the DataFrame that are less than or equal
    to a certain value is known as the percentile rank of that value.
    The function then reverses the percentile ranks for the columns
    "forwardPE" and "debtToEquity," where a lower value is preferred.
    With the values replaced by their percentile ranks, the function
    produces a DataFrame with the same shape as the input DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing the values for which
        to calculate percentile ranks.

    Returns:
        pd.DataFrame: A DataFrame of the same shape as the input DataFrame,
        but with the values replaced by their percentile ranks.

    """
    typewriter("------------------------------------\n")
    typewriter("  Step 2: Ranking Your Companies       \n")
    typewriter("------------------------------------\n")
    ranked_percentiles = df.apply(
        lambda x: [
            stats.percentileofscore(x, a, "rank") if pd.notnull(a) else np.nan
            for a in x
        ]
    )
    columns_to_inverse = ["forwardPE", "debtToEquity"]

    for column in columns_to_inverse:
        if column in ranked_percentiles:
            ranked_percentiles[column] = 100 - ranked_percentiles[column]
    ranked_percentiles = ranked_percentiles.round(2)
    return ranked_percentiles


# rank the stocks by percentiles
def rank_stocks(df):
    """
    This function calculates a score for each stock from the DataFrame
    supplied.

    The score is the sum of the products of each factor's weight and
    its respective weighting for each factor.
    Aspects considered include Forward PE, Forward EPS, Debt to Equity,
    Return on Equity, Return on Assets, Revenue Growth, Quick Ratio, and
    Quarterly Return.

    Factor_weights = [['forwardPE', 0.1],['forwardEps', 0.1],['debtToEquity',
    0.1],['returnOnEquity', 0.1],['returnOnAssets', 0.1],
    ['revenueGrowth', 0.2],['quickRatio', 0.1], ['quarterlyReturn', 0.2]]

    Parameters:
    df (pandas.DataFrame): A DataFrame containing the factors for each stock.
    The DataFrame
    should have the factors as columns and each row
    represents a stock.

    Returns:
    pandas.DataFrame: The input DataFrame with an additional
    column 'score' that contains the
    calculated score for each stock.
    """
    df["score"] = (
        df["forwardPE"] * 0.1
        + df["forwardEps"] * 0.1
        + df["debtToEquity"] * 0.1
        + df["returnOnEquity"] * 0.1
        + df["returnOnAssets"] * 0.1
        + df["revenueGrowth"] * 0.2
        + df["quickRatio"] * 0.1
        + df["quarterlyReturn"] * 0.2
    )


def choose_companies(df):
    """
    Prompts the user to select the number of companies to include
    in the portfolio from the ranked list.

    The user and this function communicate to decide how many
    top-ranked businesses the user wants to put in their portfolio.
    A number is requested from the user, which is then checked
    to see if it falls within the permitted range.
    Up until a valid input is obtained, the function keeps
    asking the user for input.

    Args:
        df (pd.DataFrame): A DataFrame containing the
        ranked list of companies.

    Returns:
        None. This function is used for its side effect of
        interacting with the user and does not return a value.
    """
    typewriter("-----------------------------------------------------------\n")
    typewriter(
        "Your companies are now ranked based on their\
 fundamentals in the table above.\n"
    )
    typewriter(
        "You can see the 'score' assigned to each one\
 of them under the 'score' column \n"
    )
    typewriter(
        "Please choose how many companies you would like\
 to include from this list in your portfolio\n"
    )
    typewriter("Example: '10' chooses the top 10 companies\
 from this list \n")
    typewriter("-------------------------------------------\
----------------\n")
    typewriter(
        "You must choose more than 3 and the number cannot\
 be greater than the total \nnumber of companies listed\
 in the table - note index starts with 0 \n"
    )
    while True:
        portfolio_size = input("Enter your number here: ")

        if validate_number(portfolio_size, df):
            print("Data is valid")
            break

    portfolio_size = int(portfolio_size)
    portfolio_df = df.head(portfolio_size)

    typewriter("You have chosen your portfolio\n")
    typewriter(
        "The InvestIQ algorithm will now determine the allocation\
 that will get the highest returns with the lowest risk\n"
    )

    return portfolio_df


def validate_number(portfolio_size, df):
    """
    Validates the number of companies chosen by the user for
    the portfolio.

    This function determines whether the user-selected input
    number of firms falls within the permitted range.
    The function returns False and a ValueError is raised if
    the input integer is outside of the permitted range.
    The function returns True if the provided number falls
    inside the permitted range.

    Args:
        portfolio_size (int): The number of companies
        chosen by the user for the portfolio.
        df (pd.DataFrame): A DataFrame containing the
        ranked list of companies.

    Returns:
        bool: True if the input number is within the
        acceptable range, False otherwise.
    """
    try:
        portfolio_size = int(portfolio_size)
    except ValueError:
        print("Invalid data: portfolio size is not a number,\
 please try again.\n")
        return False

    if (
        portfolio_size > df["symbols"].count()
        or portfolio_size < 3
    ):
        print("You have not chosen a valid portfolio size,\
 please try again.\n")
        return False

    return True


def pull_returns(ticker, start, end):
    """
    Retrieves, for a given ticker symbol and time frame,
    the historical adjusted close prices.

    This function downloads historical pricing information
    for a particular ticker symbol using the yfinance library.
    The obtained data is then used to extract the
    "Adj Close" prices.
    If the data download fails for any reason, the
    function handles the exception and returns NaN.

    Args:
        ticker (str): The ticker symbol of the company
        for which to fetch the historical pricing data.
        start (str): The start date of the date range
        for which to fetch the data, in the format
        'YYYY-MM-DD'.
        end (str): The end date of the date range for
        which to fetch the data, in the format 'YYYY-MM-DD'.

    Returns:
        pd.Series: A pandas Series containing the historical
        adjusted close prices for the given ticker symbol,
                   indexed by date. If the data download
                   fails, returns NaN.
    """
    try:
        print(f"Fetching pricing data for {ticker}")
        data = yf.download(ticker, start=start, end=end, progress=False)
        return data["Adj Close"]
    except Exception as e:
        print(
            f"Failed to download data for {ticker}. Error:\
 {e} - continuing with remaining tickers."
        )
        return np.nan


def combine_stocks(tickers):
    """
    Fetches the historical prices for a list of ticker
    symbols and combines them into a single DataFrame.

    This function iterates over a list of ticker symbols,
    fetches the historical prices for each symbol using the
    pull_returns function, and combines these price series
    into a single DataFrame. The DataFrame is then returned
    for further processing. This data is used to calculate
    expected returns and variance for portfolio optimization.

    Args:
        tickers (list): A list of ticker symbols for which
        to fetch the historical prices.

    Returns:
        pd.DataFrame: A DataFrame where each column
        represents the historical prices for a ticker symbol,
                      and the column name is the ticker
                      symbol. The DataFrame's index is the date.
    """
    typewriter("------------------------------------\n")
    typewriter(" Step 3: Optimizing Your Portfolio  \n")
    typewriter("------------------------------------\n")
    typewriter(
        "InvestIQ needs to fetch the historical prices\
 of your porfolio companies. \n"
    )
    typewriter("This is used to calculate expected returns\
 and your variance: \n")
    data_frames = pd.DataFrame()
    for i in tickers:
        data_frames[i] = pull_returns(i, start, end)
        time.sleep(1)  # Add a delay of 1 second between each request

    if index_choice == "dow":
        data_frames.to_csv('pricing_data_dow.csv', index=False)
    elif index_choice == "sap100":
        data_frames.to_csv('pricing_data_sap100.csv', index=False)
    elif index_choice == "sap500":
        data_frames.to_csv('pricing_data_sap500.csv', index=False)
    return data_frames


def typewriter(input_text, speed=0.025):
    """
    Prints out the input text at a specified speed to
    simulate the effect of a typewriter.

    This function iterates over each character in the input
    text and prints it out with a delay between each character.
    The delay is specified by the speed parameter. The effect
    is that the text appears to be typed out in real time,
    similar to a typewriter.

    Args:
        input_text (str): The text to be printed out.
        speed (float, optional): The delay between each
        character in seconds. Default is 0.001 seconds.

    Returns:
        None
    """
    for letter in input_text:
        print(letter, end="", flush=True)
        time.sleep(speed)


def hpp_optimization(portfolio_prices, latest_prices):
    """
    Using Hierarchical Risk Parity (HRP), a portfolio is optimised,
    and the number of shares to buy for each stock is determined.

    The HRP optimisation approach is used in this function to determine
    the ideal weights for each stock in the portfolio after first
    calculating the portfolio returns.
    The user is then prompted to enter the total sum they intend
    to put into the portfolio.
    It determines the remaining funds and the number of shares
    to buy for each stock using the DiscreteAllocation function
    from the PyPortfolioOpt package.

    Args:
        portfolio_prices (pd.DataFrame): A DataFrame containing
        the historical prices for each stock in the portfolio.
        latest_prices (pd.Series): A Series containing the
        latest prices for each stock in the portfolio.

    Returns:
        None
    """
    port_returns = portfolio_prices.pct_change().dropna()
    hrp = HRPOpt(port_returns)
    hrp_weights = hrp.optimize()
    weights = hrp.optimize()
    typewriter("-----------------------------------------\n")
    typewriter(" Step 4: Calculating Shares To Purchase  \n")
    typewriter("-----------------------------------------\n")
    typewriter("Please input how much you would like to invest\
 in your portfolio:\n")
    typewriter("There is a minimum limit of 1000 and max limit of 9999999:\n")
    while True:
        investment = input("Enter your investment number here:\n")
        try:
            investment = int(investment)
            if investment > 999 and investment < 10000000:
                break
            else:
                print("Invalid Input: Your input must be between 1000 and\
 9999999. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    da = DiscreteAllocation(weights,
                            latest_prices,
                            total_portfolio_value=investment)
    allocation, leftover = da.greedy_portfolio()
    print(
        "Your recommended allocation of shares\
 'stock':'number of shares'\n", allocation
    )
    print("Funds remaining: ${:.2f}".format(leftover))
    typewriter("--------------------------------------\n")
    hrp.portfolio_performance(verbose=True)
    typewriter("--------------------------------------\n")


def reset_program():
    """
    Resets the program and provides the user with options to
    learn about various financial terms.

    This function runs in a loop, prompting the user to either
    start the InvestIQ program again or learn about various
    financial terms such as 'Expected Annual Return',
    'Annual Volatility', and 'Sharpe Ratio'. The user can
    choose to learn about these terms by entering the corresponding
    number (1, 2, or 3) or press Enter to restart the program.
    The loop continues until a valid input is provided.

    Args:
        None

    Returns:
        None
    """
    while True:
        answer = input(
            "Press Enter to start InvestIQ again, or type 1 to learn about\
 expected annual return, 2 to learn about annual volatility\
 and 3 to learn about the sharpe ratio!.\n"
        )
        if answer == "":
            break
        elif answer == "1":
            typewriter("------------------------------------\n")
            typewriter("      Expected Annual Return        \n")
            typewriter("------------------------------------\n")
            print(
                """
Expected Annual Return is a projection\
 of the potential earnings or profit\
 from an investment over a one year period.
It's calculated based on historical data and future predictions.\
 It's often expressed as a percentage.
A higher expected annual return means the investment is predicted\
 to yield a higher return over the course of a year.
However, it's important to remember that these are just estimates\
 and actual returns may vary.
"""
            )
        elif answer == "2":
            typewriter("------------------------------------\n")
            typewriter("        Annual Volatility           \n")
            typewriter("------------------------------------\n")
            print(
                """
Annual Volatility is a statistical measure of the dispersion of returns\
 for a given security or market index over a one year period.
It is commonly associated with the risk level of the investment.
High volatility means that the price of the security can change\
 dramatically over a short time period in either direction,\
 which can be seen as more risky.
On the other hand, low volatility would mean that a security's value\
 does not fluctuate dramatically, but changes in value at a steady\
 pace over a period of time.
"""
            )
        elif answer == "3":
            typewriter("------------------------------------\n")
            typewriter("            Sharpe Ratio              \n")
            typewriter("------------------------------------\n")
            print(
                """
The Sharpe Ratio is a measure used by investors to understand the\
 return of an investment compared to its risk.
It is the average return earned in excess of the risk-free rate per\
 unit of volatility or total risk.
The greater a portfolio's Sharpe ratio, the better its risk-adjusted\
 performance.
If the Sharpe ratio is negative, it means the risk-free rate is greater
 than the portfolio's return, or the portfolio's return is expected\
 to be negative.
In this case, a riskless investment would perform better.
Generally a Sharpe ratio above 1 is considered good, while a sharpe\
 ratio above 1.5 is considered excellent
"""
            )
        else:
            print("invalid input, try again")
