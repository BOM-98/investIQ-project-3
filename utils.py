# Write your code to expect a terminal of 80 characters wide and 24 rows high
from math import sqrt
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
import yfinance as yf
from yahoo_fin import stock_info as si
import scipy.stats as stats

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
    #URL of the Wikipedia page from which to scrape the S&P 100 company list
    url_sap_100 = 'https://en.wikipedia.org/wiki/S%26P_100'
    
    while True:
        print("Please choose which stock index you would like to pick stocks from.")
        print("The larger the index, the longer it will take to analyse the stocks")
        print("1: 'dow': 30 companies from the Dow Jones (fast analysis time ~ 1 min)")
        print("2: 'sap100': 100 companies from the S&P100 (slow analysis time ~ 3 min)")
        print("3: 'sap100': 500 companies from the S&P500 (slowest analysis time ~ 6 min)")
        print("Example: 'dow' chooses the Dow Jones  (30) \n")

        index_choice = input("Enter your index here: ")

        if validate_index(index_choice):
            print("Data is valid")
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
        if index_choice != 'dow' and index_choice != 'sap100'and index_choice != 'sap500':
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

# Calculate Log Return
def calculate_log_return(start_price, end_price):
    return log(end_price / start_price)

# Calculate Variance
def calculate_variance(dataset):
    numerator = 0
    mean = sum(dataset)/len(dataset)

    for number in dataset:
        element = (number - mean)**2
        numerator += element

    variance = numerator / len(dataset)
    return variance

# Calculate Standard Deviation
def calculate_stddev(dataset):
    variance = calculate_variance(dataset)
    stddev = sqrt(variance)
    return stddev


# Calculate Correlation Coefficient
def calculate_correlation(set_x, set_y):
    # Sum of all values in each dataset
    sum_x = sum(set_x)
    sum_y = sum(set_y)

    # Sum of all squared values in each dataset
    sum_x2 = sum([x ** 2 for x in set_x])
    sum_y2 = sum([y ** 2 for y in set_y])

    # Sum of the product of each respective element in each dataset
    sum_xy = sum([x * y for x, y in zip(set_x, set_y)])

    # Length of dataset
    n = len(set_x)

    # Calculate correlation coefficient
    numerator = n * sum_xy - sum_x * sum_y
    denominator = sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))

    return numerator / denominator


def calculate_percentile_rank(df):
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


def collect_data(symbols):
    print('calculating your company fundamentals - this may take a minute or two...')
    stocks_list = []
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