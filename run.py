# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from math import sqrt

def calculate_variance(dataset):
  numerator = 0
  mean = sum(dataset)/len(dataset)

  for number in dataset:
    element = (number - mean)**2
    numerator += element

  variance = numerator / len(dataset)
  return variance

def calculate_stddev(dataset):
  variance = calculate_variance(dataset)
  stddev = sqrt(variance)
  return stddev