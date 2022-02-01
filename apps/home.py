import streamlit as st
from PIL import Image
import requests



def app():

    st.markdown("""## Levana NFT Sales Tracking V2 - Randomearth """)
    st.text('Includes Stats for all NFTs, and all Rarity/Faction tiers per NFT')
    st.text('Github: https://github.com/KMONEE/RandomEarth-Sales-Dash')

    
    levana = Image.open("sales.png")
    st.image(levana)