'''
@author: Ashlyn Campbell
@description: A system to analyze the overall health of an individual based on Fitbit data.
'''
from numpy import quantile, random, where
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import confusion_matrix
from datetime import datetime, timedelta
from sklearn.datasets import make_blobs
from collections import defaultdict
from sklearn.utils import resample
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from dotenv import load_dotenv
from scipy.stats import zscore
from numpy import average
import seaborn as sns
import pandas as pd
import numpy as np
import threading
import math
import os

# set working directory path
load_dotenv()
os.chdir(os.getenv('DEFAULT_PATH'))

class HealthAnalysis: # Risk Assessment
    def __init__(self, id):
        self.id = id # may use name instead of id for future usage
        self.analysis = {
            'irregular_heartrate': False,
            'irregular_sleep': False,
            'irregular_activity': False,
            'irregular_blood_pressure': False,
            'irregular_symptoms': []
        }
    
    def store_irregularities(self):
        # different tables for regular analysis versus irregular analysis
        codehere=None
        
    def Alert(self):
        print (f'Hello {self.id}, we have noticed something. Click the App for additional details!')
        
    def generate_summary():
        return None
        
class AnalyzeHeartRate(HealthAnalysis): # this dataset represents the first month of pregnancy
    def __init__(self):
        self.base_il = 0 # base intensity level
        self.base_mets = 10 # base mets value
        self.resting_heartrate = self.findRestingHeartRate()
        self.heartrate_health = self.generateAnomalies()
        
    def processId(self, df, id_, rhr, minutes):
        date_df = df[df['id'] == id_]
        prev_time = None
        curr_bpm = []
        num_bpm = 0
        for index, row in date_df.iterrows():
            time_ = row['time']
            date_ = row['date']
            bpm_ = row['bpm']
            if prev_time is not None: # contains a previous time value
                if (time_ - prev_time <= minutes): # use of couple minute interval due to inconsistent one minute interval times
                    num_bpm += 1
                    curr_bpm.append(bpm_)
                else:
                    num_bpm = 0
                    curr_bpm = []
            else: # first initial time
                curr_bpm.append(bpm_)
                num_bpm += 1
            if num_bpm == 5:
                avg_bpm = sum(curr_bpm) // num_bpm  # calculate the avg mean in the interval
                rhr[id_][date_] += avg_bpm
                rhr[id_][date_] //= 2
                num_bpm = 0 # restart the interval amount
                curr_bpm = []
            prev_time = time_ # previous should always be moved to current
    def findRestingHeartRate(self):
        df = pd.read_csv('data_interim/heartrate_mets_intensities_merged_inner.csv')
        df = df[(df['mets'] == 10) & (df['intensity_level'] == 0)]
        rhr = defaultdict(dict)
        date_column = []
        time_column = []
        for index,row in df.iterrows():
            dt_object = datetime.strptime(row['timestamp'], "%m/%d/%Y %I:%M:%S %p")
            date_part = dt_object.date()
            date_column.append(date_part)
            time_column.append(dt_object)
            rhr[row['id']][date_part] = 0
        df['date'] = date_column
        df['time'] = time_column
        minutes = timedelta(minutes=15) # viewing resting heartrate within a larger interval due to fitbit data frequency of readings
        threads = []
        for id_ in df['id'].unique():
            thread = threading.Thread(target=self.process_id, args=(df, id_, rhr, minutes))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        data = [{'id': id_, 'date': date, 'resting_heart_rate': value} 
            for id_, dates in rhr.items()
            for date, value in dates.items()]
        new_df = pd.DataFrame(data)
        # normalize columns containing 0
        d = {}
        avg_group = new_df.groupby('id')
        for id_, group in avg_group:
            avg_rhr = 0
            count = 0
            for hr in list(group['resting_heart_rate']):
                avg_rhr += hr
                count += 1 if hr != 0 else 0
            avg_rhr /= count
            d[id_] = avg_rhr
        for index, row in new_df.iterrows():
            if row['resting_heart_rate'] <=10:
                new_df.at[index, 'resting_heart_rate'] = d[row['id']]
        # Create a Day Column
        start_date = datetime(2016, 4, 12)
        interval = timedelta(days=1)
        date_dict = {}
        current_date = start_date
        for i in range(1,33):
            formatted_date = current_date.strftime('%Y-%m-%d')
            date_obj = datetime.strptime(formatted_date, '%Y-%m-%d').date()
            date_dict[date_obj] = i
            current_date += interval
        day_column = []     
        for index, row in new_df.iterrows():
            if row['date'] in date_dict:
                day_column.append(date_dict[row['date']])
            else:
                print('Type Error')
        new_df['day'] = day_column
        new_df.to_csv('data_processed/daily_resting_heartrate.csv', index=False)
        print(new_df.head())
        
    def generateAnomalies(self): 
        df = pd.read_csv('data_interim/heartrate_mets_intensities_merged_inner.csv')
        df = df[df['intensity_level'] == 0] # only viewing resting anomalies
        analysis_file = open('reports/anomaly_analysis.txt', 'w')
        day_timestamp = pd.to_datetime(df['timestamp'])
        day_timestamp = day_timestamp.dt.day
        df['day'] = day_timestamp 
        grouped = df.groupby(['id','day'])
        anomalies = {}
        for (id, day), group in grouped:
            X = group[['bpm','mets']].values

            ## Isolation Forest
            model = IsolationForest(n_estimators=50, max_samples='auto', contamination=float(0.1),max_features=1.0)
            model.fit(X)
            anomaly_scores = model.decision_function(X)
            anomaly_scores_reshaped = anomaly_scores.reshape(-1, 1)
            scaler = MinMaxScaler(feature_range=(-1, 1))
            anomaly_scores_scaled = scaler.fit_transform(anomaly_scores_reshaped)
            anomaly_scores_scaled = anomaly_scores_scaled.flatten()
            group['if_anomaly_score'] = anomaly_scores_scaled
            group['if_anomaly'] = model.predict(X)

            ## Local Outlier Factor
            N = len(X)-1 if len(X) < 20 else 20
            lof = LocalOutlierFactor(n_neighbors=N)
            lof_anomaly_scores = lof.fit_predict(X)
            group['lof_anomaly'] = lof_anomaly_scores
            outlier_scores = lof.negative_outlier_factor_
            outlier_scores_reshaped = outlier_scores.reshape(-1, 1)
            scaler = MinMaxScaler(feature_range=(-1, 1))
            outlier_scores_scaled = scaler.fit_transform(outlier_scores_reshaped)
            outlier_scores_scaled = outlier_scores_scaled.flatten()
            group['lof_anomaly_score'] = outlier_scores_scaled

            anomalies[(id, day)] = group

        # store the individual anomalies into a dataframe
        dataframes = []
        for key, value in anomalies.items():
            df_anomalies = pd.DataFrame()
            df_anomalies['id'] = value['id']
            df_anomalies['timestamp'] = value['timestamp']
            df_anomalies['day'] = value['day']
            # df_anomalies['intensity_level'] = value['intensity_level']
            df_anomalies['mets'] = value['mets']
            df_anomalies['bpm'] = value['bpm']
            df_anomalies['if_anomaly_score'] = value['if_anomaly_score']
            df_anomalies['if_anomaly'] = value['if_anomaly']

            if ('lof_anomaly_score' in value) and ('lof_anomaly' in value):
                df_anomalies['lof_anomaly_score'] = value['lof_anomaly_score']
                df_anomalies['lof_anomaly'] = value['lof_anomaly']
            else:
                size = len(value)
                df_anomalies['lof_anomaly_score'] = np.zeros(size)
                df_anomalies['lof_anomaly'] = np.zeros(size) 

            dataframes.append(df_anomalies)

            ## Create Document for Group Patterns
            text = f'ID: {key[0]}, DAY: {key[1]} = {value.describe()}'
            analysis_file.write(text)

        df_merged = pd.concat(dataframes, ignore_index=True)
        df_merged.to_csv('data_interim/anomalies_heartrate.csv', index=False)
        
        return self.findHeartRateHealth()
    
    def findHeartRateHealth(self):
        df = pd.read_csv('data_interim/anomalies_heartrate.csv')
        grouped = df.groupby(['id', 'day'])
        low_column = []
        medium_column = []
        high_column = []
        for (id_, day_), group in grouped: # viewing each day for each unique id
            
            # Medium Risk in Isolation Forest, Local Outlier Factor, and Std Resting Heart Rate
            high_risk_bin = group[(group['std_rhr_bin'] == 'High') & 
                        (group['lof_bin'] == 'High') & 
                        (group['if_bin'] == 'High')]

            # Medium Risk in Isolation Forest, Local Outlier Factor, and Std Resting Heart Rate
            medium_risk_bin = group[(group['std_rhr_bin'] == 'Medium') & 
                        (group['lof_bin'] == 'Medium') & 
                        (group['if_bin'] == 'Medium')]

            # Isolation Forest Advantages in detecting lower limit anomalies
            if_lower_limit = group[(group['std_rhr_bin'] == 'Low') & 
                        (group['lof_bin'] == 'Low') & 
                        (group['if_bin'] == 'High') & 
                        (group['std_description'] == 'Lower')]

            # Find mean in each limit
            high_risk_mean = high_risk_bin['bpm'].mean()
            medium_risk_mean = medium_risk_bin['bpm'].mean()
            if_lower_mean = if_lower_limit['bpm'].mean()
            
            abnormal_elevation, abnormal_med, abnormal_decline = 0,0,0
            if high_risk_mean >= (self.resting_heartrate + (self.resting_heartrate * 0.20)):
                abnormal_elevation = 1
                
            if medium_risk_mean >= (self.resting_heartrate + (self.resting_heartrate * 0.10)):
                abnormal_med = 1
                
            if if_lower_mean <= (self.resting_heartrate - (self.resting_heartrate * 0.20)):
                abnormal_decline = 1
            
            high_column.append(abnormal_elevation)
            medium_column.append(abnormal_med)
            low_column.append(abnormal_decline)
            
        df['abnormal_decline'] = low_column
        df['abnormal_med'] = medium_column
        df['abnormal_elevation'] = high_column


    def Alert(self):
        super().Alert() # initial message
        print('Hello! Your heart rate has shown variability. Have you started any new habits?') # In the App Alert Message
        

class SymptomCorrelation(HealthAnalysis):
    # Manual Input use against heartrate
    def __init__(self): # typical conditions of pregnant women 
        self.typical_symptoms = {
            'Nausea and Vomiting': ['Morning Sickness (Nausea and Vomiting)', 'Hyperemesis Gravidarum (Severe Morning Sickness)'],
            'Fatigue': ['Morning Sickness (Nausea and Vomiting)', 'Gestational Diabetes', 'Hyperemesis Gravidarum (Severe Morning Sickness)'],
            'Headaches': ['Preeclampsia', 'Gestational Hypertension'],
            'Swelling in Extremities': ['Preeclampsia', 'Gestational Hypertension', 'Deep Vein Thrombosis (DVT)', 'Varicose Veins', 'Venous Insufficiency'],
            'Back Pain': ['Sciatica', 'Pelvic Girdle Pain', 'Preterm Labor'],
            'Heartburn': ['Preeclampsia', 'Gestational Diabetes'],
            'Constipation': ['Iron Deficiency Anemia', 'Gestational Diabetes'],
            'Frequent Urination': ['Urinary Tract Infections (UTIs)', 'Gestational Diabetes'],
            'Braxton Hicks Contractions': ['Preterm Labor'],
            'Round Ligament Pain': ['Urinary Tract Infection (UTI)', 'Preterm Labor']
        }
        self.hypertension = self.analyze_bp() # return true or false
        self.obesity = True if self.analyze_bmi() >= 30 else False
        
    def analyze_bp(self):
        return True
    
    def analyze_bmi(self):
        return 30
    
    def Alert(self):
        super().Alert() # initial message
        print('Hello! Your symptoms seem to be consistent with: ') # In the App Alert Message # high blood pressure, ov
        

class SleepCorrelation(HealthAnalysis): # sleep is a direct link: https://pubmed.ncbi.nlm.nih.gov/29103944/
    def __init__(self, total_minutes):
        self.total_minutes = total_minutes
        self.irregular_sleep, self.type_sleep = self.analyzeSleep()
        
    def analyzeSleep(self):
        total_hours = self.total_minutes // 60 # convert minutes into hours analysis
        irregular_sleep = False
        type_sleep = 'normal'
        if (total_hours <= 6):
            irregular_sleep = True
            type_sleep = 'little'
            self.Alert() # alert with sleep metric
        elif (total_hours >= 10):
            irregular_sleep = True
            type_sleep = 'excessive'
            self.Alert() # alert with sleep metric
        return irregular_sleep, type_sleep # irregular sleep can be caused by many things so the next steps is to perform a Health Analysis 
        
    def Alert(self):
        # customize types of messages based on the scenario # update this later
        SummarizeData.displayAdvice(type='improve_sleep') # the future may yield exact requests input
        print(f'We have noticed a {self.type_sleep} in sleep time. Click the App to learn how to improve these patterns!')
    
class ActivityCorrelation(HealthAnalysis): # read articles on how activity can benefit mental health, obesity, vitals etc.
    print(None) 
    
class MentalHealthCorrelation(HealthAnalysis):
    def __init__(self):
        self.mental_health_code = {
            'mood_swings': ['bipolar'] # work on the correlations between various mental illnesses and maternal health
        }
   
class WeightCorrelation(HealthAnalysis): # analysis of diabetes and obesity: https://pubmed.ncbi.nlm.nih.gov/20963519/
    print(None)

## Geospatial component
class SubstanceAbuseCorrelation(HealthAnalysis): # maybe tie in symptoms, mental health, sleep patterns etc. to potential substance abuse
    print(None)
    

class DeathGeoRateCorrelation(HealthAnalysis): # death rate correlation to geography areas using WONDER data, data of hospitals, and public/private insurance, and black population (women)
    print(None)
    
        
