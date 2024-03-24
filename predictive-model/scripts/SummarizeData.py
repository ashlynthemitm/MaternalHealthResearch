'''
@author: Ashlyn Campbell
File Description: This file is used to generate summary information in TLDR format daily and tailor advice when Alerts are displayed
'''

def displayAdvice(type=None):
    match type:
        case 'improve_sleep':
            # read the tldr.json file for sleep metrics and summarize to display
            codehere=None
        case _:
            # generate random advice
            codehere=None