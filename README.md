# InvestIQ
<img src="assets/images/invest-iq-logo-1.png" alt="drawing" width="100%"/>

## Table of Contents

---

## Project Background

InvestIQ is a Python command line application built to assist users in creating an optimal stock portfolio from US publically listed companies. Programs exist to help people optimize their stock portfolio in order to maximize their sharpe ratio - i.e. their return relative to their risk. However, these programs presuppose that users already know which stocks they should consider. Only after the user has added their stocks do the programs work to optimize how much should be allocated towards each stock. Some programs exist to help people assess which stocks to consider using tecnhical analysis - examining past pricing data. However these are separate from the programs that optimize the portfolios. There is a gap in helping people to choose which companies to include in your porfolio by using fundamental analysis - analysis using company financial reports instead of past pricing data. There is a further gap to combine this approach with portfolio optimization to make sure the user picks the best stocks and then optimizes them in the one place.

Invest IQ uses an algorithm to rank stocks from either the Dow Jones, S&P100 or S&P500 using fundamental analysis, and create an optimized portfolio from those stocks to give users the highest return for a given level of risk. By harnessing the capabilities of Python, InvestIQ can analyse up to 500 companies and perform thousands of calculations within a matter of minutes to provide users with their stock portfolios - significantly decreasing the amount of time and effort required on their part.

Users can select which stock index they want to analyze stocks from - rank those stocks based on their fundamental ratios, choose how many stocks they want to include in their portfolio and automatically optimize their investment allocation towards each stock to get the highest expected returns for the lowest level of risk using Hierarchical Risk Parity Optimization(HRP).

InvestIQ makes creating your stock portfolio effortless.

---

## Features

- On initialisation, InvestIQ explains to users the intent of the program before encouraging them to proceed through the program by pressing enter.

    <details>
    <summary>InvestIQ intro</summary>

    ![InvestIQ intro](assets/images/intro-description.png)
    </details>

- Index chooser: InvestIQ prompts the user to decide which stock index (Dow Jones, S&P100 & S&P500) the user would like to pick stocks from. Each index contains a different number of stocks, which impacts the time required to fetch financial data from each stock and analyze their fundamentals. 

    <details>
    <summary>Index Chooser</summary>

    ![Index Chooser](assets/images/index-chooser.png)
    </details>

- Data Scraper: InvestIQ fetches the financial information from each company in the index using yfinance

    <details>
    <summary>Data Scraper</summary>

    ![Data Scraper](assets/images/fetching-data.png)
    </details>

- Stock Ranker: InvestIQ fetches financial data from each company in the index and displays it as a dataFrame to the user.

    <details>
    <summary>Stock Ranker 1</summary>

    ![Stock Ranker 1](assets/images/stock-ranker-1.png)
    </details>

- Stock Ranker contd.: The financial ratios are then converted into percentiles based on their standing relative to the other stocks in the index. These percentiles are passed into an algorithm that calculates a 'score' for each stock and sorts the stocks in the dataFrame based on their score. The user is given the raw fundamentals data, percentiles data and score allocated towards each stock. The user is then prompted to decide how many stocks they would like to include in their portfolio, and the highest ranking stocks within that range are then used for further analysis. 

    <details>
    <summary>Stock Ranker 2</summary>

    ![Stock Ranker 2](/assets/images/stock-ranker-2.png)
    </details>

- Stock 'scores' are determined by the sum of the following ratios with the weights attached. 
    ![Stock Ranking Algorithm](/assets/images/score-algorithm.png)

- Ratio explainer: The program provides the user with the option to type in any fundamentals ratio and receive a description of that ratio for their own analysis. 

    <details>
    <summary>Ratio Explainer</summary>

    ![Ratio Explainer](assets/images/information-finder.png "Ratio Explainer")
    </details>

- Portfolio Optimizer: The program takes the number of stocks the user has selected and calculates the optimial weights to be assigned towards each stock in the portfolio to produce the greatest returns at a given level of risk using Hierarchical Risk Parity Optimization(HRP). 

    <details>
    <summary>Portfolio Optimizer</summary>

    ![Portfolio Optimizer](assets/images/portfolio-optimizer.png)
    </details>

- Investment Allocator: After calculating the optimal portfolio weights, the program prompts the user to input how much they intend to invest in stocks and returns to them to number of shares they should buy in each company, in addition to their expected returns, annual volatility and Sharpe Ratio (a measure of expected returns relative to risk). 

    <details>
    <summary>Investment Allocator</summary>
    
    ![Investment Allocator](assets/images/investment-allocator.png)
    </details>

---

## Creating the Heroku app

When you create the app, you will need to add two buildpacks from the _Settings_ tab. The ordering is as follows:

1. `heroku/python`
2. `heroku/nodejs`

You must then create a _Config Var_ called `PORT`. Set this to `8000`

If you have credentials, such as in the Love Sandwiches project, you must create another _Config Var_ called `CREDS` and paste the JSON into the value field.

Connect your GitHub repository and deploy as normal.

# Dependencies

To run this application locally you need to install pandas.
Pandas was installed by running pip3 install pandas in the terminal and inserting import pandas as pd in the run.py file.
Pandas Datareader was installed by running pip3 install pandas-datareader in the terminal and inserting import pandas_datareader.data as web in the run.py file.
yfinance was installed by running pip3 install yfinance in the terminal and inserting import yfinance as yf in the run.py file. 
Check yfinance dependencies. 
PyPortfolioOpt was installed using pip install PyPortfolioOpt
scikit-learn was installed using pip install scikit-learn

## Constraints

The deployment terminal is set to 80 columns by 24 rows. That means that each line of text needs to be 80 characters or less otherwise it will be wrapped onto a second line.

## Bugs

The scraping of all financial information from the companies took a very long time. Getting all of the ticker information from each company took about 5mins to collect - which is prohibitivly long for a program a user intends to use. To solve this, I attempted to store all of the infromation in a Google sheet, and then have the program collect the informaiton periodically from that sheet. This way multiple network requests were made to yfinance in the background, while one network request was made to the google sheets. This saved a lot of processing time. 

Using the yfinance api caused some problems as there was a lot of nan or missing values in the fundamentals I was looking for. This serious impeded my analysis. 

The deployment terminal is set to 80 columns by 24 rows. That means that each line of text needs to be 80 characters or less otherwise it will be wrapped onto a second line.

## References 
[QuantDare's articule](https://quantdare.com/correlation-prices-returns/) was used to determine whether to calculate correlation on returns or prices between equities. 

[codeCademy](www.codecademy.com) course Python for Finance was used to assist in scraping financial data and creating foundational functions such as variance, standard deviation and correlation coefficient

[Investopedia's](https://www.investopedia.com/financial-edge/0910/6-basic-financial-ratios-and-what-they-tell-you.aspx#:~:text=Key%20Takeaways&text=There%20are%20six%20basic%20ratios,return%20on%20equity%20(ROE).) article on financial ratios was used to determine which ratios I need to evaluate my stocks

Information on how to gather stock information using yfinance was gathered from [Algovibes](https://www.youtube.com/watch?v=ZUQEd22oNek) Youtube video.

Inspiration on how to rank stocks was taken from [B/O Trading Blog's Article](https://medium.com/@chris_42047/a-weighted-ranking-system-for-stocks-python-tutorial-6af425ff65a4) where an example approach to scoring and applying weights to stocks was taken. 

Portfolio optimization methods were taken from [Sadrach Pierre's Artile](https://builtin.com/data-science/portfolio-optimization-python) on how to Optimize a stock portfolio using Python. 

Monopoly art from [emojicombos.com](https://emojicombos.com/monopoly-ascii-art).

Chat gpt generated the descriptions for each fundamental financial metric in the program.

[Python Style Guide](https://peps.python.org/pep-0008/#comments) was used for determining how to style my comments.

---

Happy coding!
