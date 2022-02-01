import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly
import plotly.express as px


eggs = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/ee319c5f-4f03-41b5-b607-99f306fe1e2f/data/latest')
egg_rarity = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/284600cc-7b4c-4d47-ab50-dbdd528daf93/data/latest')
egg_rarity_merge = pd.merge(eggs, egg_rarity[['TOKEN_ID', 'RARITY']], on='TOKEN_ID')

egg_rarity_merge = egg_rarity_merge[['BLOCK_TIMESTAMP', 'RARITY', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']]
egg_rarity_merge['BLOCK_TIMESTAMP'] = pd.to_datetime(egg_rarity_merge['BLOCK_TIMESTAMP'])
egg_rarity_merge.set_index('BLOCK_TIMESTAMP', inplace = True)
egg_rarity_merge.index = egg_rarity_merge.index.round('D')

total_df = egg_rarity_merge.groupby(['BLOCK_TIMESTAMP', 'RARITY']).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST'})
average_df = egg_rarity_merge.groupby(['BLOCK_TIMESTAMP', 'RARITY']).mean().rename(columns={'NFT_LUNA_PRICE':'AVERAGE_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'AVERAGE_UST'})
tx_count_df = egg_rarity_merge.groupby(['BLOCK_TIMESTAMP', 'RARITY']).count().rename(columns={'NFT_LUNA_PRICE':'TRANSACTION_COUNT'})
tx_count_df = tx_count_df['TRANSACTION_COUNT']
min_df = egg_rarity_merge.groupby(['BLOCK_TIMESTAMP', 'RARITY']).min().rename(columns={'NFT_LUNA_PRICE':'MIN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MIN_UST'})
max_df = egg_rarity_merge.groupby(['BLOCK_TIMESTAMP', 'RARITY']).max().rename(columns={'NFT_LUNA_PRICE':'MAX_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MAX_UST'})
median_df = egg_rarity_merge.groupby(['BLOCK_TIMESTAMP', 'RARITY']).median().rename(columns={'NFT_LUNA_PRICE':'MEDIAN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MEDIAN_UST'})
cum_sum = egg_rarity_merge.groupby(['BLOCK_TIMESTAMP', 'RARITY']).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA_CUMULATIVE', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST_CUMULATIVE'}).cumsum(axis=0)

egg_master = pd.concat([total_df, tx_count_df, average_df, min_df, max_df, median_df, cum_sum], axis = 1).reset_index().sort_values(by=['BLOCK_TIMESTAMP', 'RARITY'], ascending=False)

def app():

    st.sidebar.header("Choose Columns:")
    columns = st.sidebar.multiselect(
        "Select the columns to plot",
        options = egg_master.columns,
        default = egg_master.columns.min()
    )

    line = px.line(
        egg_master, #this is the dataframe you are trying to plot
        x = "BLOCK_TIMESTAMP",
        y = columns,
        
        color = "RARITY",
        orientation = "v",
        template = "plotly_white",
        height = 600,
        width = 1000
    )

    bar = px.bar(
        egg_master, #this is the dataframe you are trying to plot
        x = "BLOCK_TIMESTAMP",
        y = columns,
        
        color = "RARITY",
        orientation = "v",
        template = "plotly_white",
        height = 600,
        width = 1000
    )

    ust_pie_df = egg_master[['RARITY', 'TOTAL_UST']].groupby(['RARITY']).sum()
    ust_pie = px.pie(
        ust_pie_df, #this is the dataframe you are trying to plot
        values = 'TOTAL_UST',
        names = ust_pie_df.index,
        width = 1000
    )


    counts_pie_df = egg_master[['RARITY', 'TRANSACTION_COUNT']].groupby(['RARITY']).sum()
    counts_pie = px.pie(
        counts_pie_df, #this is the dataframe you are trying to plot
        values = 'TRANSACTION_COUNT',
        names = counts_pie_df.index,
        width = 1000
    )


    st.title('Eggs (Not Nested)')
    st.text("""
    Egg Stats by rarity
    """)
    st.markdown("""
    ---
    """)

    st.markdown("""
    ### Master Dataframe
    """)
    st.dataframe(egg_master)

    st.download_button(
    "Press to Download",
    egg_master.to_csv().encode('utf-8'),
    "master_dataframe.csv",
    "text/csv",
    key='download-csv'
    )

    st.markdown("""
    # Line Chart Builder
    """)
    st.plotly_chart(line)

    st.markdown("""
    # Bar Chart Builder
    """)
    st.plotly_chart(bar)

    st.markdown("""
    ### UST Exchanged to Date by Rarity
    """)
    st.plotly_chart(ust_pie, use_column_width=True)

    st.markdown("""
    ### Transaction Count to Date by Rarity
    """)
    st.plotly_chart(counts_pie, use_column_width=True)