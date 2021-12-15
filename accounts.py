import streamlit as st
import pandas as pd
from backend import download
from backend import upload
from backend import delete
from backend import iterator
from backend import openfile
from backend import render_set_style_of_single_bar
import os.path
from datetime import date
from backend import table
import datetime

basic_directory = dict()
shop_directory = dict()
product_directory = dict()
buckets = ['karqbasics', 'karqshops','karqproducts']


def protempload(bucket):
    directory = dict()
    for path in iterator(bucket):
        parent = directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]
    return directory


def nonread_file(bucket, path, file, col, lsit, pos=None):
    download(bucket, path, file)
    read = pd.read_csv(file)
    os.remove(file)
    if lsit:
        return list(read[str(col)])
    else:
        return float(read[col].iloc[pos])


def accounts():
    st.success('登陆身份:' + st.session_state.member)
    st.subheader('店铺帐号管理')
    global product_directory
    product_directory = protempload(buckets[2])
    worker_assigner()
    product_assigner()


def worker_assigner():
    with st.expander('运营匹配', expanded=True):
        if st.checkbox('将运营人员与店铺进行匹配'):
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
            table(assigner_df, assigner_df.columns, str('运营配对.csv'), False)
            assigner = st.form(key='assigner')
            assigner.subheader('店铺匹配')
            col1, col2 = assigner.columns(2)
            col1.write('选择店铺')
            clients = col1.multiselect('店铺', [str(i) + '-' + str(k) for i, k in
                                              zip(nonread_file(buckets[0], '店铺/店铺资料.csv', '店铺资料.csv', '店铺名', True),
                                                  nonread_file(buckets[0], '店铺/店铺资料.csv', '店铺资料.csv', '站点', True))])
            col2.write('选择运营人员')
            download(buckets[0], ('用户' + '/' + '用户.csv'), '用户.csv')
            df = pd.read_csv('用户.csv')
            client_staff = list(df[(df['角色'] == '销售')]['帐号'])
            worker = col2.selectbox('运营人员', client_staff)
            if assigner.form_submit_button('匹配'):
                for client in clients:
                    columns = assigner_df.columns
                    old_workers = list(assigner_df['运营人员'])
                    new_clients = [i for i in clients if i not in columns]
                    old_clients = [j for j in clients if j in columns]
                    if client in new_clients:

                        if worker in old_workers:
                            # new client old worker

                            worker_ls = list(assigner_df['运营人员'])
                            pos = worker_ls.index(worker)
                            add_ls = [u * 0 for u in range(len(assigner_df) - 1)]
                            add_ls.insert(pos, 1)
                            assigner_df[client] = add_ls
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '运营配对/运营配对.csv')
                            upload(buckets[1], '运营配对/运营配对.csv', 'updatedcsv.csv')
                            os.remove('updatedcsv.csv')
                            download(buckets[1], '运营配对/运营配对.csv', '运营配对.csv')
                            assigner_df = pd.read_csv('运营配对.csv')
                            os.remove('运营配对.csv')
                        else:
                            # new client new worker

                            assigner_df[client] = [u * 0 for u in range(len(assigner_df.columns) - 1)]
                            add_ls = [0 * p for p in range(len(assigner_df.columns) - 2)]
                            add_ls.append(1)
                            add_ls.insert(0, str(worker))
                            add_df = pd.Series(add_ls, index=assigner_df.columns)
                            assigner_df = assigner_df.append(add_df, ignore_index=True)
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '运营配对/运营配对.csv')
                            upload(buckets[1], '运营配对/运营配对.csv', 'updatedcsv.csv')
                            os.remove('updatedcsv.csv')
                            download(buckets[1], '运营配对/运营配对.csv', '运营配对.csv')
                            assigner_df = pd.read_csv('运营配对.csv')
                            os.remove('运营配对.csv')
                    if client in old_clients:
                        if worker in old_workers:
                            # old client old worker

                            worker_ls = list(assigner_df['运营人员'])
                            work_pos = worker_ls.index(str(worker))
                            assigner_df.at[work_pos, client] = 1
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '运营配对/运营配对.csv')
                            upload(buckets[1], '运营配对/运营配对.csv', 'updatedcsv.csv')
                            download(buckets[1], '运营配对/运营配对.csv', '运营配对.csv')
                            assigner_df = pd.read_csv('运营配对.csv')
                            os.remove('运营配对.csv')

                        else:
                            # old client new worker

                            add_ls = [0 * u for u in range(len(assigner_df.columns) - 1)]
                            add_ls.insert(0, worker)
                            add_df = pd.Series(add_ls, index=assigner_df.columns)
                            assigner_df = assigner_df.append(add_df, ignore_index=True)
                            worker_ls = list(assigner_df['运营人员'])
                            work_pos = worker_ls.index(str(worker))
                            assigner_df.at[work_pos, client] = 1
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '运营配对/运营配对.csv')
                            upload(buckets[1], '运营配对/运营配对.csv', 'updatedcsv.csv')
                            download(buckets[1], '运营配对/运营配对.csv', '运营配对.csv')
                            assigner_df = pd.read_csv('运营配对.csv')
                            os.remove('运营配对.csv')
                st.success('完成')



def product_assigner():
    global product_directory

    with st.expander('产品匹配', expanded=True):
        if st.checkbox('将产品(SKU)与店铺进行匹配'):
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
            table(assigner_df, assigner_df.columns, str('产品配对.csv'), False)
            assigner = st.form(key='assigner')
            assigner.subheader('店铺匹配')
            col1, col2 = assigner.columns(2)

            col1.write('选择产品(SKU)')
            # sku list
            sku_ls = []
            for sku_typ in list(filter(lambda x: len(x) > 1, list(product_directory['SKU'].keys()))):
                sku_ls = sku_ls + list(filter(lambda x: len(x) > 1, list(product_directory['SKU'][sku_typ].keys())))
            clients = col1.multiselect('产品(SKU)', sku_ls)

            col2.write('选择店铺')
            worker = col2.selectbox('店铺', [str(i) + '-' + str(k) for i, k in
                                              zip(nonread_file(buckets[0], '店铺/店铺资料.csv', '店铺资料.csv', '店铺名', True),
                                                  nonread_file(buckets[0], '店铺/店铺资料.csv', '店铺资料.csv', '站点', True))])
            if assigner.form_submit_button('匹配'):
                for client in clients:
                    columns = assigner_df.columns
                    old_workers = list(assigner_df['店铺'])
                    new_clients = [i for i in clients if i not in columns]
                    old_clients = [j for j in clients if j in columns]
                    if client in new_clients:

                        if worker in old_workers:
                            # new client old worker
                            worker_ls = list(assigner_df['店铺'])
                            pos = worker_ls.index(worker)
                            add_ls = [u * 0 for u in range(len(assigner_df) - 1)]
                            add_ls.insert(pos, 1)
                            assigner_df[client] = add_ls
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '产品配对/产品配对.csv')
                            upload(buckets[1], '产品配对/产品配对.csv', 'updatedcsv.csv')
                            os.remove('updatedcsv.csv')
                            download(buckets[1], '产品配对/产品配对.csv', '产品配对.csv')
                            assigner_df = pd.read_csv('产品配对.csv')
                            os.remove('产品配对.csv')
                        else:
                            # new client new worker

                            assigner_df[client] = [u * 0 for u in range(len(assigner_df.columns) - 1)]
                            add_ls = [0 * p for p in range(len(assigner_df.columns) - 2)]
                            add_ls.append(1)
                            add_ls.insert(0, str(worker))
                            add_df = pd.Series(add_ls, index=assigner_df.columns)
                            assigner_df = assigner_df.append(add_df, ignore_index=True)
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '产品配对/产品配对.csv')
                            upload(buckets[1], '产品配对/产品配对.csv', 'updatedcsv.csv')
                            os.remove('updatedcsv.csv')
                            download(buckets[1], '产品配对/产品配对.csv', '产品配对.csv')
                            assigner_df = pd.read_csv('产品配对.csv')
                            os.remove('产品配对.csv')
                    if client in old_clients:
                        if worker in old_workers:
                            # old client old worker

                            worker_ls = list(assigner_df['店铺'])
                            work_pos = worker_ls.index(str(worker))
                            assigner_df.at[work_pos, client] = 1
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '产品配对/产品配对.csv')
                            upload(buckets[1], '产品配对/产品配对.csv', 'updatedcsv.csv')
                            download(buckets[1], '产品配对/产品配对.csv', '产品配对.csv')
                            assigner_df = pd.read_csv('产品配对.csv')
                            os.remove('产品配对.csv')

                        else:
                            # old client new worker

                            add_ls = [0 * u for u in range(len(assigner_df.columns) - 1)]
                            add_ls.insert(0, worker)
                            add_df = pd.Series(add_ls, index=assigner_df.columns)
                            assigner_df = assigner_df.append(add_df, ignore_index=True)
                            worker_ls = list(assigner_df['店铺'])
                            work_pos = worker_ls.index(str(worker))
                            assigner_df.at[work_pos, client] = 1
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[1], '产品配对/产品配对.csv')
                            upload(buckets[1], '产品配对/产品配对.csv', 'updatedcsv.csv')
                            download(buckets[1], '产品配对/产品配对.csv', '产品配对.csv')
                            assigner_df = pd.read_csv('产品配对.csv')
                            os.remove('产品配对.csv')
                st.success('完成')
