'''
@author: Ashlyn Campbell
File Description: This file takes in a csv file at the moment and will use the Fitbit API
'''

from dotenv import load_dotenv
import pandas as pd
import SummarizeData
import os

# set working directory path
load_dotenv()
os.chdir(os.getenv('DEFAULT_PATH'))

class HealthAnalysis:
    def __init__(self, id):
        self.id = id
        self.analysis = {
            'irregular_heartrate': False,
            'irregular_sleep': False,
            'irregular_activity': False,
        }
class HeartRateCorrelation:
    def __init__(self):
        self.base_il = 0 # base intensity level
        self.base_mets = 10 # base mets value
        self.expected_movement = 0 # in pregnancy theres up and down movement that typically occurs (update based on literature)
        self.resting_hr = self.calculate_resting_heartrate()
        self.hr_health = self.analyze_hr()
        
    def calculate_resting_heartrate(self):
        return None
    
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
    def __init__(self, total_minutes):
        self.total_minutes = total_minutes
        
    def analyzeSleep(self):
        total_hours = self.total_minutes // 60 # convert minutes into hours analysis
        irregular_sleep = False
        if (total_hours <= 6):
            irregular_sleep = True
        self.Alert() # alert with sleep metric
        return irregular_sleep # irregular sleep can be caused by many things so the next steps is to perform a Health Analysis 
        
    def Alert(self):
        # customize types of messages based on the scenario # update this later
        SummarizeData.displayAdvice(type='improve_sleep') # the future may yield exact requests input
        return f'''
                Hello first_name, we have noticed a decline in sleep time. Click the App to learn how to improve these patterns!
                '''
    
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
    
        
    