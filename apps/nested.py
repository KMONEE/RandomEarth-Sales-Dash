import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly
import plotly.express as px
import ast

def app():
    st.sidebar.header("Choose Grouping:")
    grouping_check = st.sidebar.checkbox('Group Without Rarirty'
    )

    if grouping_check:
        group_master = ['BLOCK_TIMESTAMP']
        merge_cols = ['BLOCK_TIMESTAMP', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']

    else:
        group_master = ['BLOCK_TIMESTAMP', 'RARITY']
        merge_cols = ['BLOCK_TIMESTAMP', 'RARITY', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']


    nested_egg = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/290a91fb-8186-486d-992e-985839352809/data/latest')
    nested_rarity = pd.read_csv('http://165.22.125.123/nested_egg_nfts.csv')
    nested_rarity_merge = pd.merge(nested_egg, nested_rarity[['token_id', 'traits']], left_on='TOKEN_ID', right_on='token_id', how='inner')
    nested_rarity_merge['RARITY'] = nested_rarity_merge['traits'].apply(lambda x: ast.literal_eval(x).get('Rarity'))
    nested_rarity_merge.pop('traits')

    nested_rarity_merge = nested_rarity_merge[merge_cols]
    nested_rarity_merge['BLOCK_TIMESTAMP'] = pd.to_datetime(nested_rarity_merge['BLOCK_TIMESTAMP'])
    nested_rarity_merge.set_index('BLOCK_TIMESTAMP', inplace = True)
    nested_rarity_merge.index = nested_rarity_merge.index.floor('D')

    total_df = nested_rarity_merge.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST'})
    average_df = nested_rarity_merge.groupby(group_master).mean().rename(columns={'NFT_LUNA_PRICE':'AVERAGE_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'AVERAGE_UST'})
    tx_count_df = nested_rarity_merge.groupby(group_master).count().rename(columns={'NFT_LUNA_PRICE':'TRANSACTION_COUNT'})
    tx_count_df = tx_count_df['TRANSACTION_COUNT']
    min_df = nested_rarity_merge.groupby(group_master).min().rename(columns={'NFT_LUNA_PRICE':'MIN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MIN_UST'})
    max_df = nested_rarity_merge.groupby(group_master).max().rename(columns={'NFT_LUNA_PRICE':'MAX_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MAX_UST'})
    median_df = nested_rarity_merge.groupby(group_master).median().rename(columns={'NFT_LUNA_PRICE':'MEDIAN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MEDIAN_UST'})
    cum_sum = nested_rarity_merge.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA_CUMULATIVE', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST_CUMULATIVE'}).cumsum(axis=0)

    nested_master = pd.concat([total_df, tx_count_df, average_df, min_df, max_df, median_df, cum_sum], axis = 1).reset_index().sort_values(by=group_master, ascending=False)

    st.sidebar.header("Choose Columns:")
    columns = st.sidebar.multiselect(
        "Select the columns to plot",
        options = nested_master.columns,
        default = nested_master.columns.min()
    )

    st.sidebar.header("Logarithmic / Linear:")
    log_lin = st.sidebar.checkbox('Enable Log'
    )

    if log_lin:
        t_f = True
    else:
        t_f = False

    if grouping_check:
        line = px.line(nested_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(nested_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, orientation = "v", template = "plotly_white", height = 600, width = 1000)
    else:
        line = px.line(nested_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "RARITY", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(nested_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "RARITY", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        
        ust_pie_df = nested_master[['RARITY', 'TOTAL_UST']].groupby(['RARITY']).sum()
        ust_pie = px.pie(ust_pie_df, values = 'TOTAL_UST', names = ust_pie_df.index, width = 1000)
        counts_pie_df = nested_master[['RARITY', 'TRANSACTION_COUNT']].groupby(['RARITY']).sum()
        counts_pie = px.pie(counts_pie_df, values = 'TRANSACTION_COUNT', names = counts_pie_df.index, width = 1000)


    


    st.title('Nested Eggs (Dragons)')
    st.text("""
    Nested Egg Stats by rarity
    """)
    st.markdown("""
    ---
    """)

    st.markdown("""
    ### Master Dataframe
    """)
    st.dataframe(nested_master)

    st.download_button(
    "Press to Download",
    nested_master.to_csv().encode('utf-8'),
    "master_dataframe_nested.csv",
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

    if not grouping_check:

        st.markdown("""
        ### UST Exchanged to Date by Rarity
        """)
        st.plotly_chart(ust_pie, use_column_width=True)

        st.markdown("""
        ### Transaction Count to Date by Rarity
        """)
        st.plotly_chart(counts_pie, use_column_width=True)