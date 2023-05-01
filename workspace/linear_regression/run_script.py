"""
Imports
"""
import random
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression



"""
Functions
"""
def generate_random_numbers(n):
    return [random.random() for _ in range(n)]


def generate_random_dataframe(n):
    random_data = np.random.rand(n, 5)
    df = pd.DataFrame(random_data, columns=['Column1', 'Column2', 'Column3', 'Column4', 'Column5'])
    return df


def split_train_test(df, train_size):
    train = df.sample(frac=train_size, random_state=42)
    test = df.drop(train.index)
    return train, test


def linear_regression(train):
    X_train = train.iloc[:,:-1]
    y_train = train.iloc[:,-1]
    lr = LinearRegression()
    return lr


def print_coefficients(lr):
    """
    This function takes in a linear regression model object and prints out the coefficients of the model.
    
    Parameters:
    lr (LinearRegression object): A trained linear regression model object
    
    Returns:
    None
    """
    coefs = lr.coef_
    intercept = lr.intercept_
    print("Coefficients: ", coefs)
    print("Intercept: ", intercept)
    return None


def predict_target_values(model, test):
    return model.predict(test.drop(columns=['target']))


def calculate_error(predicted, actual):
    error = actual - predicted
    return error


def repeat_iterations(num_iterations):
    errors = []
    for i in range(num_iterations):
        df = generate_random_dataframe(n)
        lr = linear_regression(train)
        predicted = predict_target_values(lr, test)
        error = calculate_error(predicted, test)
    return errors


def calculate_average_error(errors):
    avg_error = sum(errors)/len(errors)
    return avg_error


def main():
    df = generate_random_dataframe(n)
    lr = linear_regression(train)
    predict = predict_target_values(lr, test)
    error = calculate_error(predict, test.iloc[:,-1])
    errors = repeat_iterations(num_iterations)
    avg_error = calculate_average_error(errors)
    return avg_error

