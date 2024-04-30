'''
@author: Ashlyn Campbell
@description: This file analyzes the thresholds and trends in the modelling analysis to output understandable information about personal health.
'''

from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import torch