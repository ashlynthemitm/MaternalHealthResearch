'''
@author: Ashlyn Campbell
File Description: This file takes in a csv file and computed the resting heart rate at low intensity(value=0) and resting mets(value=10) daily
'''

'''
Plan: 

Identify Period:
Identify periods of inactivity (5-10 minutes calculation) during which the individual is assumed to be at rest and not engaged in any physical activity.

Calculate Resting Heart Rate:
Use AVG over 5-10 mins consistent mets=10 and intensity=0

Repeat for Multiple Days:
Calculate each day to view any shifts and improve this estimate

(How does their heartrate change over a 30 day time span)

Validation and Monitoring:
Validate the calculated resting heart rate estimate against established norms (Pregnant and Black Women)
Monitor changes in resting heart rate over time --> Place this data in a dataframe or database

Step 1: Filter Dataset to intensity_level=0 and mets=10 --> unique id analysis 
func1 - calculate avg hr, func2 - adjust heartrate to typical pregnancy/black woman amounts,func3 - analyze the shift/elevation and use manualInput to view any correlation (elevation or decreasing number/percentage against manualInput) - graph of conditions that align with heartrate increasing and the manualInput
'''

from pyspark.sql import SparkSession
from pyspark.sql.functions import * 
from pyspark.sql.types import *
from dotenv import load_dotenv
import pandas as pd
import os

# set working directory path
load_dotenv()
os.chdir(os.getenv('DEFAULT_PATH'))

## test code - continue testing
spark = SparkSession \
    .builder \
    .appName("heartrate_mets_intensities_merged_inner.csv") \
    .master('local[4]') \
    .getOrCreate()
    
schema1 = StructType([StructField('id', IntegerType(), True), 
                    StructField('timestamp', TimestampType(), True),
                    StructField('intensity_level', IntegerType(), True),
                    StructField('mets', IntegerType(), True),
                    StructField('bpm', IntegerType(), True)])

customer = spark.readStream.format('csv').schema(schema1)\
    .option('header',True).option('maxFilePerTrigger', 1) \
    .load(r'data_interim/heartrate_mets_intensities_merged_inner.csv')   
    
print(customer.isStreaming)
 
    

class CreateHealthAnalysisDataset:
    def __init__(self):
        self.df = self.create_dataframe()
    def create_dataframe(self):
        return pd.DataFrame() # this should include heartrate and manual input analysis 
        

class HeartRateCorrelation:
    def __init__(self):
        self.df = pd.DataFrame() # contains heartrate analysis
        self.input_df = pd.read_csv('data_interim/heartrate_mets_intensities_merged_inner.csv')
        self.base_il = 0 # base intensity level
        self.base_mets = 10 # base mets value
        self.expected_movement = 0 # in pregnancy theres up and down movement that typically occurs (update based on literature)
        self.resting_hr = self.calculate_resting_heartrate()
        self.hr_health = self.analyze_hr()
        
    def calculate_resting_heartrate(self):
        # only viewing resting data
        self.input_df = self.input_df[(self.input_df['mets'] == 10) and (self.input_df['intensity_level'] == 0)]
        self.input_df['timestamp'] = pd.to_datetime(self.input_df['timestamp'], format='%m/%d/%Y %I:%M:%S %p')
        self.input_df = self.input_df.sort_values(by='timestamp')
        rhr = 0
        timestamps = self.input_df['timestamp'].unique()
        ids = self.input_df['id'].unique()
        for id in ids:
            self.input_df[id]['timestamp'] # continue working on the resting heartrate code
        
        # place information into dataframe
        return rhr # dictionary {id:rhr}
    
    def analyze_hr(self):
        return True # healthy possibility=True unhealthy=False

    
class SymptomCorrelation:
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
    

class SleepCorrelation():
    print(None) # sleep is a direct link: https://pubmed.ncbi.nlm.nih.gov/29103944/
    
class ActivityCorrelation(): # read articles on how activity can benefit mental health, obesity, vitals etc.
    print(None) 
    
class MentalHealthCorrelation():
    def __init__(self):
        self.mental_health_code = {
            'mood_swings': ['bipolar'] # work on the correlations between various mental illnesses and maternal health
        }
        
class WeightCorrelation(): # analysis of diabetes and obesity: https://pubmed.ncbi.nlm.nih.gov/20963519/
    print(None)

## Geospatial component
class SubstanceAbuseCorrelation(): # maybe tie in symptoms, mental health, sleep patterns etc. to potential substance abuse
    print(None)
    

class DeathGeoRateCorrelation(): # death rate correlation to geography areas using WONDER data, data of hospitals, and public/private insurance, and black population (women)
    print(None)