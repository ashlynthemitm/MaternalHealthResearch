'''
@author: Ashlyn Campbell
'''

from transformers import BartForConditionalGeneration, BartTokenizer
# from transformers import pipeline
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from collections import Counter
from string import punctuation
from heapq import nlargest
import requests
import json
import os
import re

load_dotenv()
def readText(): # Continue creating this model algorithm
    nhs_key = os.getenv('NHS_KEY')
    headers = {
        'subscription-key': nhs_key,
        'Content-Type': 'application/json'
    }

    with open('/home/azureuser/ClientFolder/tldr.json', 'r') as json_file:
        tldr_data = json.load(json_file)

    for data in tldr_data['week-by-week'].values():
        response = requests.get(data['website_url'],headers=headers)
        if response.status_code == 200:
            text = response.text
            data['title'], text = parseHTML(text)
            data['summary'] = generateTransformerSummary(text)
            # print(f'{data['title']}: {data['summary']}')
            print('Loading TLDR summaries...')
            print('------------------------------------------------------')
        else:
            print(f'Request failed with status code {response.status_code}')
        break
    with open('/home/azureuser/ClientFolder/tldr.json', 'w') as json_file:
        print('Adding json data to tldr.json file...')
        print('------------------------------------------------------')
        json.dump(tldr_data, json_file, indent=4)

    print('TLDR Data has been collected...')
    print('------------------------------------------------------')

def parseHTML(text):
    soup = BeautifulSoup(text, 'html.parser')
    title_tags = soup.find_all('title')
    article_tags = soup.find_all('article')
    titles = [title.get_text() for title in title_tags]
    updated_title = re.sub(r"'", "", titles[0])
    text_content = [text.get_text() for text in article_tags]
    text_content = [re.sub(r'\n+','', text) for text in text_content]
    text_content = [re.sub(r"'", "", text) for text in text_content]
    return titles[0], text_content[0] # weekly data only contains one article

def splitText(text): # for larger documents
    max_chunk_size = 2048
    chunk_list = []
    current_chunk = ''
    # split text by sentences
    for sentence in text.split('.'):
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + '.'
        else:
            current_chunk = re.sub(r'\n+','', current_chunk)
            chunk_list.append(current_chunk)
            current_chunk = sentence + '.'
    if current_chunk:
        current_chunk = re.sub(r'\n+','', current_chunk)
        chunk_list.append(current_chunk)
    return chunk_list

def generateTransformerSummary(text):
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
    model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=300, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

readText()
