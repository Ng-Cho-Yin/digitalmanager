import streamlit as st
import pandas as pd
from backend import download
from backend import upload
from backend import delete
from backend import iterator
from backend import openfile
import os.path
from datetime import date
import random
from backend import table

basic_directory = dict()
shop_directory = dict()
product_directory = dict()
buckets = ['karqbasics', 'karqshops', 'karqproducts']


def protempload(bucket):
    directory = dict()
    for path in iterator(bucket):
        parent = directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]
    return directory


def shop():
    st.success('登陆身份:' + st.session_state.member)
    st.subheader('店铺管理')
    global shop_directory, product_directory
    shop_directory = protempload(buckets[1])
    product_directory = protempload(buckets[2])
    download(buckets[1], '运营配对/运营配对.csv', '运营配对.csv')
    assigner_df = pd.read_csv('运营配对.csv')
    try:
        assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    try:
        os.remove('运营配对.csv')
    except:
        pass
    # table(assigner_df, assigner_df.columns, str('运营配对.csv'), False)
    worker_ls = list(assigner_df['运营人员'])
    work_pos = worker_ls.index(str(st.session_state.member))
    assigner_df = assigner_df[(assigner_df['运营人员'] == str(st.session_state.member))]
    # st.table(assigner_df)
    cols = list(assigner_df.columns)
    cols.remove('运营人员')
    shops = []
    for j in cols:
        if str(assigner_df.at[work_pos, j]) == '1':
            shops.append(j)

    download(buckets[1], '产品配对/产品配对.csv', '产品配对.csv')
    assigner_df = pd.read_csv('产品配对.csv')
    try:
        assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    try:
        os.remove('产品配对.csv')
    except:
        pass
    # table(assigner_df, assigner_df.columns, str('产品配对.csv'), False)

    skus_dict = {}
    for shop in shops:
        shop_skus = []
        shop_ls = list(assigner_df['店铺'])
        shop_pos = shop_ls.index(str(shop))
        new_df = assigner_df[(assigner_df['店铺'] == str(shop))]

        shop_cols = list(new_df.columns)
        shop_cols.remove('店铺')
        for j in shop_cols:
            if str(new_df.at[shop_pos, j]) == '1':
                shop_skus.append(j)

        skus_dict[shop] = shop_skus
    #st.write(skus_dict)
    tar_shop = st.selectbox('店铺', list(skus_dict.keys()))

    for typ in list(filter(lambda x: len(x) > 1, list(product_directory['SKU'].keys()))):
        sku_ls = filter(lambda x: len(x) > 1, list(product_directory['SKU'][typ].keys()))
        for item in sku_ls:
            if item in skus_dict[tar_shop]:
                col1, col2 = st.columns((4, 1))
                col1.write(item)
                with st.expander(str(item), expanded=True):
                    if st.checkbox('查看' + str(item) + '相关文件'):
                        try:
                            lan = list(product_directory['SKU'][typ][item].keys())
                            lang = st.selectbox('语言', lan, key=item)
                            plats = list(product_directory['SKU'][typ][item][lang].keys())
                            platform = st.selectbox('平台', plats, key=item)
                            col1, col2, col3, col4 = st.columns((3, 3, 3, 3))

                            for tar in filter(lambda x: len(x) > 1,
                                              list(product_directory['SKU'][typ][item][lang][platform].keys())):

                                for tar2 in filter(lambda x: len(x) > 1,
                                                   list(product_directory['SKU'][typ][item][lang][platform][
                                                            tar].keys())):
                                    col1.write(tar2)

                                    if col2.checkbox('打开', key=str(item) + str(tar) + '-SKU'):
                                        path = 'SKU/' + str(typ) + '/' + str(item) + '/' + str(
                                            lang) + '/' + str(platform) + '/' + tar + '/' + tar2

                                        download(buckets[2], str(path), tar2)
                                        try:
                                            df = pd.read_csv(tar2)
                                            try:
                                                df.drop('Unnamed: 0', axis=1, inplace=True)
                                            except:
                                                pass


                                            table(df, df.columns, str(item) + str(tar), True)
                                            if st.checkbox('确认更新文件', key=str(item) + str(tar) + '-SKU'):
                                                delete(buckets[2], path)
                                                upload(buckets[2], path, 'updatedcsv.csv')
                                                protempload(buckets[2])


                                        except:
                                            download(
                                                buckets[2],
                                                str(path),
                                                tar2)
                                            st.image(tar2)
                        except:
                            print('error:verified_sku()')
