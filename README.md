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

## Constraints

The deployment terminal is set to 80 columns by 24 rows. That means that each line of text needs to be 80 characters or less otherwise it will be wrapped onto a second line.

## References 
[QuantDare's articule](https://quantdare.com/correlation-prices-returns/) was used to determine whether to calculate correlation on returns or prices between equities. 

[codeCademy](www.codecademy.com) course Python for Finance was used to assist in scraping financial data and creating foundational functions such as variance, standard deviation and correlation coefficient
---

Happy coding!
