![CI logo](https://codeinstitute.s3.amazonaws.com/fullstack/ci_logo_small.png)

Welcome,

This is the Code Institute student template for deploying your third portfolio project, the Python command-line project. The last update to this file was: **March 14, 2023**

## Reminders

- Your code must be placed in the `run.py` file
- Your dependencies must be placed in the `requirements.txt` file
- Do not edit any of the other files or your code may not deploy properly

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
---

Happy coding!
