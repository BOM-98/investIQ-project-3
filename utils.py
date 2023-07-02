# Write your code to expect a terminal of 80 characters wide and 24 rows high
from math import sqrt

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