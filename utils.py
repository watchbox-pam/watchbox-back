import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from skimage import exposure, transform
from transformers import pipeline
import yfinance as yf
import requests
from bs4 import BeautifulSoup

def load_clean_movie_data(movie_file):
    data = pd.read_csv(movie_file)
    data.dropna(inplace=True)
    data[['date_of_release', 'contry_of_release']]= data['release']
    data.drop(['released', 'date_of_release'], axis=1, inplace=True)
    data.dropna(inplace=True)
    data = data[[
        'name',
        'genre',
        'year',
        'director',
        'writer',
        'stars',
        'compagny',
        'country_of_release',
    ]]
    data['year'] = data['year'].astype('str')
    data['cat_features'] = data[data.columns].apply(lambda x: '  ')

    return data


def get_recommendations(title, df, sim, count=5):
    index = df.index[df['name'].str.lower() == title.lower()]

    if len(index) == 0 :
        return []

    if index[0] >= len(sim):
        return []

    similarities = list(enumarate(sim[index[0]]))