import streamlit as st
from backend import download
from backend import upload
from backend import delete
from backend import iterator
from backend import openfile
from backend import table
from backend import render_pie_simple
import pandas as pd
import os.path
import base64
import time


basic_directory = dict()
warehouses_directory = dict()
buckets = ['karqbasics', 'karqwarehouses']


def protempload(bucket):
    directory = dict()
    for path in iterator(bucket):
        parent = directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]
    return directory


def warehouse():
    # show all warehouses with stats
    # stats: num of specific product
    st.success('登陆身份:' + st.session_state.member)
    global basic_directory, warehouses_directory
    basic_directory = protempload(buckets[0])
    warehouses_directory = protempload(buckets[1])
    st.subheader('仓库管理')
    path = '仓库出入库统计' + '/' + '仓库出入库统计.csv'
    download(buckets[1], str(path), '仓库出入库统计.csv')
    df = pd.read_csv('仓库出入库统计.csv')
    try:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass

    warehouses_ls = list(df['仓库名'])
    house = st.selectbox('仓库', filter(lambda x: len(x) > 1, warehouses_ls))
    house_pos = warehouses_ls.index(house)
    target_warehouse = df[(df['仓库名'] == house)]
    target_col = list(target_warehouse.columns)
    target_col.remove('仓库名')
    col1, col2, col3, col4 = st.columns(4)
    col_pos = 1
    data = []
    for sku in target_col:
        if col_pos == 1:
            col1.metric(label=sku, value=int(df.at[house_pos, sku]))

            Dict = {"value": int(df.at[house_pos, sku]), "name": sku}
            data.append(Dict)

        elif col_pos == 2:
            col2.metric(label=sku, value=int(df.at[house_pos, sku]))
            Dict = {"value": int(df.at[house_pos, sku]), "name": sku}
            data.append(Dict)

        elif col_pos == 3:
            col3.metric(label=sku, value=int(df.at[house_pos, sku]))
            Dict = {"value": int(df.at[house_pos, sku]), "name": sku}
            data.append(Dict)

        elif col_pos == 4:
            col4.metric(label=sku, value=int(df.at[house_pos, sku]))
            Dict = {"value": int(df.at[house_pos, sku]), "name": sku}
            data.append(Dict)

        col_pos += 1

    render_pie_simple('统计1', '统计2', '统计3', data)

    st.write('## ')

    with st.expander('仓库详细资料', expanded=True):
        if st.checkbox('查看各仓库的类型,名称,国家'):
            path = '仓库' + '/' + '仓库资料.csv'
            download(buckets[0], str(path), '仓库资料.csv')
            df = pd.read_csv('仓库资料.csv')
            try:
                df.drop('Unnamed: 0', axis=1, inplace=True)
            except:
                pass
            table(df, df.columns, '仓库资料.csv', False, height=500)
            os.remove('仓库资料.csv')
    with st.expander('仓库出入库统计', expanded=True):
        if st.checkbox('查看所以仓库各产品的现存量'):
            path = '仓库出入库统计' + '/' + '仓库出入库统计.csv'
            download(buckets[1], str(path), '仓库出入库统计.csv')
            df = pd.read_csv('仓库出入库统计.csv')
            try:
                df.drop('Unnamed: 0', axis=1, inplace=True)
            except:
                pass
            table(df, df.columns, '仓库出入库统计.csv', False, height=500)
            os.remove('仓库出入库统计.csv')
