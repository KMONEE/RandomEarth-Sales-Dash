import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly
import plotly.express as px
import ast

def app():

    
    st.title('CSV - All Transactions')
    st.text("""
    First table is for every transaction made thus far, second table is for transaction stats grouped by day - for all NFTs
    """)
    st.markdown("""
    ---
    """)
    
    nested_egg = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/290a91fb-8186-486d-992e-985839352809/data/latest')
    loot = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/2208cc91-e624-4b40-b666-f65c8b6405f8/data/latest')
    eggs = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/ee319c5f-4f03-41b5-b607-99f306fe1e2f/data/latest')
    meteor_dust = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/8eebec3c-db0e-4051-a5c2-50a5deb1070b/data/latest')
    meteors = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/b9778a1d-9b63-4ba5-a48f-7b28569b5603/data/latest')
    #IT IS ABSOLUTELY CRUCIAL THAT YOU DO NOT CHANGE THE ORIGINAL NAMES OF THE DATAFRAME COLUMNS ON VELOCITY

    #MUST STORE IN A DICTIONARY 
    current_nft_dict = {'nested_egg':nested_egg, 'loot':loot, 'eggs':eggs, 'meteor_dust':meteor_dust, 'meteors':meteors}

    meteor_rarity = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/5d7b0f96-a537-46e5-9b3c-d5145072279f/data/latest')
    meteor_rarity_merge = pd.merge(meteors, meteor_rarity[['TOKEN_ID', 'RARITY']], on='TOKEN_ID')
    egg_rarity = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/284600cc-7b4c-4d47-ab50-dbdd528daf93/data/latest')
    egg_rarity_merge = pd.merge(eggs, egg_rarity[['TOKEN_ID', 'RARITY']], on='TOKEN_ID')
    dust_rarity = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/f4b78c34-07ec-4f5e-8099-7e6db2db24a9/data/latest')
    dust_rarity_merge = pd.merge(meteor_dust, dust_rarity[['TOKEN_ID', 'RARITY']], on='TOKEN_ID')

    nested_rarity = pd.read_csv('http://165.22.125.123/nested_egg_nfts.csv')
    nested_rarity_merge = pd.merge(nested_egg, nested_rarity[['token_id', 'traits']], left_on='TOKEN_ID', right_on='token_id', how='inner')
    nested_rarity_merge['RARITY'] = nested_rarity_merge['traits'].apply(lambda x: ast.literal_eval(x).get('Rarity'))
    nested_rarity_merge.pop('traits')
    nested_rarity_merge.pop('token_id')

    loot = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/2208cc91-e624-4b40-b666-f65c8b6405f8/data/latest')
    loot_ROLE = pd.read_csv('http://165.22.125.123/loot_nfts.csv')
    master_2 = pd.merge(loot, loot_ROLE[['token_id', 'traits']], left_on='TOKEN_ID', right_on='token_id', how='inner')
    master_2['ROLE'] = master_2['traits'].apply(lambda x: ast.literal_eval(x).get('Role'))
    master_2['FACTION'] = master_2['traits'].apply(lambda x: ast.literal_eval(x).get('Faction'))
    master_2.pop('traits')
    master_2.pop('token_id')
    master_2['NFT_TYPE'] = master_2['NFT_TYPE'] + (' - ') + master_2['ROLE']
    master_2.pop('ROLE')
    master_2 = master_2.rename(columns = {'FACTION':'RARITY'})

    st.markdown("""
    ## All transactions, not grouped
    """)
    master_1 = pd.concat([meteor_rarity_merge, dust_rarity_merge, egg_rarity_merge, nested_rarity_merge, master_2]).reset_index(drop=True)
    st.dataframe(master_1)

    st.download_button(
        "Press to Download",
        master_1.to_csv().encode('utf-8'),
        "total_dataframe.csv",
        "text/csv",
        key='download-csv'
        )

    group_master = ['BLOCK_TIMESTAMP', 'NFT_TYPE', 'RARITY']
    merge_cols = ['BLOCK_TIMESTAMP', 'NFT_TYPE', 'RARITY', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']

    master_2 = master_1[merge_cols].copy()
    master_2['BLOCK_TIMESTAMP'] = pd.to_datetime(master_2['BLOCK_TIMESTAMP'])
    master_2.set_index('BLOCK_TIMESTAMP', inplace = True)
    master_2.index = master_2.index.floor('D')

    total_df = master_2.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST'})
    average_df = master_2.groupby(group_master).mean().rename(columns={'NFT_LUNA_PRICE':'AVERAGE_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'AVERAGE_UST'})
    tx_count_df = master_2.groupby(group_master).count().rename(columns={'NFT_LUNA_PRICE':'TRANSACTION_COUNT'})
    tx_count_df = tx_count_df['TRANSACTION_COUNT']
    min_df = master_2.groupby(group_master).min().rename(columns={'NFT_LUNA_PRICE':'MIN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MIN_UST'})
    max_df = master_2.groupby(group_master).max().rename(columns={'NFT_LUNA_PRICE':'MAX_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MAX_UST'})
    median_df = master_2.groupby(group_master).median().rename(columns={'NFT_LUNA_PRICE':'MEDIAN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MEDIAN_UST'})
    cum_sum = master_2.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA_CUMULATIVE', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST_CUMULATIVE'}).cumsum(axis=0)

    master_2 = pd.concat([total_df, tx_count_df, average_df, min_df, max_df, median_df, cum_sum], axis = 1).reset_index().sort_values(by=group_master, ascending=False).reset_index(drop=True)
    
    all_df = pd.DataFrame({
    'BLOCK_TIMESTAMP':[master_2['BLOCK_TIMESTAMP'].max()],
    'NFT_TYPE':['ALL'],
    'RARITY':['ALL'],
    'TOTAL_LUNA':[master_2['TOTAL_LUNA'].sum()],
    'TOTAL_UST':[master_2['TOTAL_UST'].sum()],
    'TRANSACTION_COUNT':[master_2['TRANSACTION_COUNT'].sum()],
    'AVERAGE_LUNA':[master_2['AVERAGE_LUNA'].mean()],
    'AVERAGE_UST':[master_2['AVERAGE_UST'].mean()],
    'MIN_LUNA':[master_2['MIN_LUNA'].min()],
    'MIN_UST':[master_2['MIN_UST'].min()],
    'MAX_LUNA':[master_2['MAX_LUNA'].max()],
    'MAX_UST':[master_2['MAX_UST'].max()],
    'MEDIAN_LUNA':[master_2['MEDIAN_LUNA'].median()],
    'MEDIAN_UST':[master_2['MEDIAN_UST'].median()],
    'TOTAL_LUNA_CUMULATIVE':[master_2['TOTAL_LUNA_CUMULATIVE'].sum()],
    'TOTAL_UST_CUMULATIVE':[master_2['TOTAL_UST_CUMULATIVE'].sum()]
    })

    master_2 = pd.concat([all_df, master_2])
    
    st.markdown("""
    ## All transactions, grouped by timestamp
    """)
    st.dataframe(master_2)

    st.download_button(
        "Press to Download",
        master_2.to_csv().encode('utf-8'),
        "total_dataframe_group_by_timestamp.csv",
        "text/csv",
        key='download-csv'
        )