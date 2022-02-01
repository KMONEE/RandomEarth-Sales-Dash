import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly
import plotly.express as px
import ast

loot = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/2208cc91-e624-4b40-b666-f65c8b6405f8/data/latest')
loot_FACTION = pd.read_csv('http://165.22.125.123/loot_nfts.csv')
loot_FACTION_merge = pd.merge(loot, loot_FACTION[['token_id', 'traits']], left_on='TOKEN_ID', right_on='token_id', how='inner')
loot_FACTION_merge['FACTION'] = loot_FACTION_merge['traits'].apply(lambda x: ast.literal_eval(x).get('Faction'))
loot_FACTION_merge.pop('traits')

loot_FACTION_merge = loot_FACTION_merge[['BLOCK_TIMESTAMP', 'FACTION', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']]
loot_FACTION_merge['BLOCK_TIMESTAMP'] = pd.to_datetime(loot_FACTION_merge['BLOCK_TIMESTAMP'])
loot_FACTION_merge.set_index('BLOCK_TIMESTAMP', inplace = True)
loot_FACTION_merge.index = loot_FACTION_merge.index.round('D')

total_df = loot_FACTION_merge.groupby(['BLOCK_TIMESTAMP', 'FACTION']).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST'})
average_df = loot_FACTION_merge.groupby(['BLOCK_TIMESTAMP', 'FACTION']).mean().rename(columns={'NFT_LUNA_PRICE':'AVERAGE_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'AVERAGE_UST'})
tx_count_df = loot_FACTION_merge.groupby(['BLOCK_TIMESTAMP', 'FACTION']).count().rename(columns={'NFT_LUNA_PRICE':'TRANSACTION_COUNT'})
tx_count_df = tx_count_df['TRANSACTION_COUNT']
min_df = loot_FACTION_merge.groupby(['BLOCK_TIMESTAMP', 'FACTION']).min().rename(columns={'NFT_LUNA_PRICE':'MIN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MIN_UST'})
max_df = loot_FACTION_merge.groupby(['BLOCK_TIMESTAMP', 'FACTION']).max().rename(columns={'NFT_LUNA_PRICE':'MAX_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MAX_UST'})
median_df = loot_FACTION_merge.groupby(['BLOCK_TIMESTAMP', 'FACTION']).median().rename(columns={'NFT_LUNA_PRICE':'MEDIAN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MEDIAN_UST'})
cum_sum = loot_FACTION_merge.groupby(['BLOCK_TIMESTAMP', 'FACTION']).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA_CUMULATIVE', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST_CUMULATIVE'}).cumsum(axis=0)

loot_master = pd.concat([total_df, tx_count_df, average_df, min_df, max_df, median_df, cum_sum], axis = 1).reset_index().sort_values(by=['BLOCK_TIMESTAMP', 'FACTION'], ascending=False)

def app():
    st.sidebar.header("Choose Columns:")
    columns = st.sidebar.multiselect(
        "Select the columns to plot",
        options = loot_master.columns,
        default = loot_master.columns.min()
    )

    line = px.line(
        loot_master, #this is the dataframe you are trying to plot
        x = "BLOCK_TIMESTAMP",
        y = columns,
        
        color = "FACTION",
        orientation = "v",
        template = "plotly_white",
        height = 600,
        width = 1000
    )

    bar = px.bar(
        loot_master, #this is the dataframe you are trying to plot
        x = "BLOCK_TIMESTAMP",
        y = columns,
        
        color = "FACTION",
        orientation = "v",
        template = "plotly_white",
        height = 600,
        width = 1000
    )

    ust_pie_df = loot_master[['FACTION', 'TOTAL_UST']].groupby(['FACTION']).sum()
    ust_pie = px.pie(
        ust_pie_df, #this is the dataframe you are trying to plot
        values = 'TOTAL_UST',
        names = ust_pie_df.index,
        width = 1000
    )


    counts_pie_df = loot_master[['FACTION', 'TRANSACTION_COUNT']].groupby(['FACTION']).sum()
    counts_pie = px.pie(
        counts_pie_df, #this is the dataframe you are trying to plot
        values = 'TRANSACTION_COUNT',
        names = counts_pie_df.index,
        width = 1000
    )


    st.title('Loot (Talismans)')
    st.text("""
    Loot Stats by FACTION
    """)
    st.markdown("""
    ---
    """)

    st.markdown("""
    ### Master Dataframe
    """)
    st.dataframe(loot_master)

    st.download_button(
    "Press to Download",
    loot_master.to_csv().encode('utf-8'),
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
    ### UST Exchanged to Date by FACTION
    """)
    st.plotly_chart(ust_pie, use_column_width=True)

    st.markdown("""
    ### Transaction Count to Date by FACTION
    """)
    st.plotly_chart(counts_pie, use_column_width=True)