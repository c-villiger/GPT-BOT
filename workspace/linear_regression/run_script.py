"""
Imports
"""
import pandas as pd
import numpy as np
import random
from sklearn.linear_model import LinearRegression



"""
Functions
"""
def generate_dataframe(dimensions):
    return pd.DataFrame(np.random.rand(dimensions[0], dimensions[1]))


def generate_coefficients(df):
    """
    Generates random coefficients for each column in the given dataframe.

    Parameters:
    df (pandas.DataFrame): The dataframe to generate coefficients for.

    Returns:
    list: A list of random coefficients, with one coefficient for each column in the dataframe.
    """
    # Error for testing
    return "error"


def calculate_dependent_variable(dataframe, coefficients):
    if not isinstance(dataframe, pd.DataFrame):
        return "Error: Dataframe input is not a pandas dataframe"


    if not isinstance(coefficients, dict):
        return "Error: Coefficient input is not a python dictionary"


    dependent_variable = dataframe.dot(pd.Series(coefficients))
    return dependent_variable


def run_linear_regression(dataframe):
    lr = LinearRegression()
    X = dataframe.drop(['dependent_variable'], axis=1)
    y = dataframe['dependent_variable']
    coefficients = lr.coef_
    intercept = lr.intercept_
    print('Coefficients:', coefficients)
    print('Intercept:', intercept)
    return coefficients, intercept


def generate_dataframe(n_rows, n_columns):
    if isinstance(n_rows, int) and isinstance(n_columns, int) and n_rows > 0 and n_columns > 0:
        df = pd.DataFrame(np.random.randn(n_rows, n_columns))
        return df


    else:
        return "Error: Invalid input"


def generate_coefficients(n_columns):
    if isinstance(n_columns, int) and n_columns > 0:
        coefs = np.random.randn(n_columns)
        return coefs


    else:
        return "Error: Invalid input"


def calculate_dependent_variable(df, coefs):
    if isinstance(df, pd.DataFrame) and isinstance(coefs, np.ndarray) and df.shape[1] == coefs.shape[0]:
        X = df.values
        y = X @ coefs + np.random.randn(X.shape[0])
        dependent_variable = pd.Series(y)
        return dependent_variable


    else:
        return "Error: Invalid input"


def run_linear_regression(df, dependent_variable):
    if isinstance(df, pd.DataFrame) and isinstance(dependent_variable, pd.Series) and df.shape[0] == dependent_variable.shape[0]:
        model = LinearRegression().fit(df, dependent_variable)
        coefficients = pd.Series(model.coef_)
        return coefficients


    else:
        return "Error: Invalid input"


def main(n_rows, n_columns):
    df = generate_dataframe(n_rows, n_columns)
    coefs = generate_coefficients(n_columns)
    dependent_variable = calculate_dependent_variable(df, coefs)
    coefficients = run_linear_regression(df, dependent_variable)
    print(coefficients)