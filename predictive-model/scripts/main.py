'''
author: Ashlyn Campbell
File Description: This is the main file that currently reads excel data 
'''

from HealthAnalysis import *

def connectionFitbitAPI():
    # connection to Fitbit API, ill compile all of this data into readable csv data and preprocess accordingly
    return None

def main():
    # for now, read the various csv files corresponding to inputs of user
    df = pd.read_csv('predictive_model/data_interim/daily_sleep_activity.csv')
    for index, row in df.iterrows():
        analysis = HealthAnalysis(row['id'], row[''])
        analysis.irregular_sleep = SleepCorrelation.analyzeSleep()
        