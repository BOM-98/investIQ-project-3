# Write your code to expect a terminal of 80 characters wide and 24 rows high
from math import sqrt
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
import yfinance as yf
from yahoo_fin import stock_info as si
import scipy.stats as stats

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
    ranked_percentiles = df.apply(lambda x: [stats.percentileofscore(x, a, 'rank') if pd.notnull(a) else np.nan for a in x])
    
    columns_to_inverse = ['forwardPE', 'debtToEquity']
    
    for column in columns_to_inverse:
        if column in ranked_percentiles:
            ranked_percentiles[column] = 100 - ranked_percentiles[column]
    ranked_percentiles = ranked_percentiles.round(2)
    return ranked_percentiles


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
