import streamlit as st
from backend import download
from backend import iterator
import pandas as pd
import os
from backend import table
from accounts import accounts
from client import client_assigner


basic_directory = dict()
buckets = ['karqbasics']


def protempload(bucket):
    directory = dict()
    for path in iterator(bucket):
        parent = directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]
    return directory


def basics():
    st.success('登陆身份:' + st.session_state.member)
    global basic_directory
    basic_directory = protempload(buckets[0])
    col1,col2,col3 = st.columns((1,4,1))
    col1.subheader('基础数据')
    col3.metric(label="基础数据集", value=7)
    accounts()
    client_assigner()
    shop()
    warehouse()
    transport()
    user()


def shop():
    with st.expander('店铺帐号数据',expanded=True):
        if st.checkbox('店铺帐号数据'):
            path = '店铺' + '/' + '店铺资料.csv'
            download(buckets[0], str(path), '店铺资料.csv')
            df = pd.read_csv('店铺资料.csv')
            try:
                df.drop('Unnamed: 0', axis=1, inplace=True)
            except:
                pass
            table(df, df.columns, '店铺资料.csv', True, bucket=buckets[0], path=path)
            os.remove('店铺资料.csv')


def warehouse():
    with st.expander('仓库数据',expanded=True):
        if st.checkbox('仓库数据'):
            path = '仓库' + '/' + '仓库资料.csv'
            download(buckets[0], str(path), '仓库资料.csv')
            df = pd.read_csv('仓库资料.csv')
            try:
                df.drop('Unnamed: 0', axis=1, inplace=True)
            except:
                pass
            table(df, df.columns, '仓库资料.csv', True, bucket=buckets[0], path=path)
            os.remove('仓库资料.csv')


def transport():
    with st.expander('物流数据',expanded=True):
        if st.checkbox('物流数据'):
            try:
                choice = st.selectbox('选择', ['物流模式数据'])
                if choice is not None:
                    info = str(choice) + '.csv'
                    path = '物流' + '/' + info
                    download(buckets[0], str(path), info)
                    df = pd.read_csv(info)
                    try:
                        df.drop('Unnamed: 0', axis=1, inplace=True)
                    except:
                        pass
                    table(df, df.columns, info, True, bucket=buckets[0], path=path)
                    os.remove(info)

            except:
                print('transport()')


def user():
    with st.expander('用户数据',expanded=True):
        if st.checkbox('用户数据'):
            path = '用户' + '/' + '用户.csv'
            download(buckets[0], str(path), '用户.csv')
            df = pd.read_csv('用户.csv')
            try:
                df.drop('Unnamed: 0', axis=1, inplace=True)
            except:
                pass
            table(df, df.columns, '用户.csv', True, bucket=buckets[0], path=path)
            os.remove('用户.csv')


