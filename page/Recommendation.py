import streamlit as st
import numpy as np
from utils import load_clean_movie_data, get_recommendations

movie_data = load_clean_movie_data("./data/movies.csv")

st.title('WatchBox')

name = st.selectbox('Nom du film', movie_data['name'].unique())
num_recommendations = st.number_input('Nombre de films a recommander', min_value=1, value)

if st.button('Obtenir les recommendations'):
    similarity_matrix_loaded = np.load('./models/similarity_matrix.npy')

    recommendations = get_recommendations(
        title=name, df=movie_data,
        sim=similarity_matrix_loaded,
        count=num_recommendations
    )
    st.write('Films recommendés :', recommendations)