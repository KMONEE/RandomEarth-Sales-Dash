import streamlit as st
from PIL import Image
import requests



def app():

    st.markdown("""## Levana NFT Sales Tracking V2 - Randomearth """)
    st.text('Includes rarity stats for Meteors, Meteor Dust, and Unnested Eggs; the rest will follow shortly')

    
    levana = Image.open("levana.png")
    st.image(levana)