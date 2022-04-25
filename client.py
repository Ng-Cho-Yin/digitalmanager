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

client_directory = dict()

buckets = ['karqbasics', 'karqproducts', 'karqlogistics', 'karqclients']

CLIENT_RESULT = """
 <div style="width:60%;height:100%;margin:5px;padding:5px;position:relative;border-radius:5px;
  background-color:#f5f5f5;border-left: 5px solid #013770;line-height: 0.3;">
 <h6>{}</h6>
 </div>
 """


def protempload(bucket):
    directory = dict()
    for path in iterator(bucket):
        parent = directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]
    return directory


def client():
    st.success('登陆身份:' + st.session_state.member)
    st.warning('Under Maintainance')
    st.info('提示:若在30天内从未对个人客户进行维护工作,客户资料将流入公共客户池')
    st.subheader('客户维护')
    global client_directory
    client_directory = protempload(buckets[3])

    function_pages = [
        "客户池",
        "维护记录",
        "添加新客户",
        '修改范本(客户资料)',
        '修改范本(成交资料)'
    ]
    col1, col2, col3 = st.columns((1, 1, 2))
    with col1:
        func = st.expander('功能', expanded=True)
        function = func.radio('', function_pages)



    if function == '客户池':
        client_directory = protempload(buckets[3])
        all_pool()
    if function == '维护记录':
        client_directory = protempload(buckets[3])
        maintain_record()
    if function == '添加新客户':
        client_directory = protempload(buckets[3])
        new_client()
    if function == '修改范本(客户资料)':
        client_directory = protempload(buckets[3])
        formatter("客户资料范本")

    if function == '修改范本(成交资料)':
        client_directory = protempload(buckets[3])
        formatter("成交资料范本")








def all_pool():
    pool = st.selectbox('选择客户池', ['公共客户池', '个人客户池'])
    if pool == '公共客户池':
        public_pool()
    if pool == '个人客户池':
        private_pool()



def maintain_record():
    st.subheader('维护记录')
    form = st.form(key='maintain_record')
    download(buckets[3], '范本/汇报模版/汇报模版.csv', '汇报模版.csv')
    df = pd.read_csv('汇报模版.csv')
    os.remove('汇报模版.csv')
    





def new_client():
    st.subheader('添加新客户')
    form = st.form(key='new_client')
    name = form.text_input('客户名')
    download(buckets[3], '范本/客户资料范本/客户资料范本.xlsx', '客户资料范本.xlsx')
    df = pd.read_excel('客户资料范本.xlsx', engine='openpyxl', index_col=-1)
    os.remove('客户资料范本.xlsx')
    df = df.astype(str)
    titles = []
    for num in range(0, len(df)):
        titles.append(df.iloc[num, 0])
    dv = pd.DataFrame(columns=titles, index=[0])
    for num in range(0, len(df)):
        dv[(df.iloc[num, 0])] = form.text_input(df.iloc[num, 0])
    dv.to_csv('客户资料.csv',
              index=False)
    if form.form_submit_button('上传'):
        path = '公共客户池/' + name + '/' + name + '.csv'
        upload(buckets[3], str(path), '客户资料.csv')



def public_pool():
    st.write('### 公共客户池')

    for item in list(filter(lambda x: len(x) > 1, client_directory['公共客户池'].keys())):

        st.markdown(CLIENT_RESULT.format('客户名称:' + str(item)), unsafe_allow_html=True)

        if st.checkbox('查看', key=item):

            for files in list(client_directory['公共客户池'][item].keys()):
                path = '公共客户池/' + item + '/' + files
                download(buckets[3], path, files)
                df = pd.read_csv(files)
                table(df, df.columns, str(files), False)
                os.remove(files)


def private_pool():
    st.write('### 个人客户池')
    download(buckets[3], '维护配对/维护配对.csv', '维护配对.csv')
    assigner_df = pd.read_csv('维护配对.csv')
    worker_ls = list(assigner_df['维护人员'])
    work_pos = worker_ls.index(str(st.session_state.member))
    assigner_df = assigner_df[(assigner_df['维护人员'] == str(st.session_state.member))]
    try:
        assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    try:
        os.remove('维护配对.csv')
    except:
        pass
    cols = list(assigner_df.columns)
    cols.remove('维护人员')
    for j in cols:
        # st.write(j,(assigner_df.at[1, j]))
        if str(assigner_df.at[work_pos, j]) == '1':
            st.markdown(CLIENT_RESULT.format('客户名称:' + str(j)), unsafe_allow_html=True)
            if st.checkbox('查看', key=j):

                for files in list(client_directory['公共客户池'][j].keys()):
                    path = '公共客户池/' + j + '/' + files
                    download(buckets[3], path, files)
                    df = pd.read_csv(files)
                    table(df, df.columns, str(files), False)
                    os.remove(files)

def formatter(key):
    newformat = st.file_uploader('上传Excel文件', type=['xlsx'], key=key)
    if newformat is not None:

        df = pd.read_excel(newformat, engine='openpyxl', index_col=-1)
        df = df.astype(str)
        st.write("## 新表格")
        for num in range(0, len(df)):
            st.text_input(df.iloc[num, 0], key=str(df.iloc[num, 0]) + str(key))

    if st.button('确认修改', key=key + 'button'):
        with open(newformat.name, 'wb') as x:
            x.write(newformat.getbuffer())
            delete(buckets[3], '范本' + '/' + str(key) + '/' + str(key) + '.xlsx')
            upload(buckets[3], '范本' + '/' + str(key) + '/' + str(key) + '.xlsx', str(newformat.name))
            st.success('修改成功')


def client_assigner():
    client_directory = protempload(buckets[3])
    with st.expander('客户匹配',expanded=True):
        if st.checkbox('将维护人员与客户进行匹配'):
            download(buckets[3], '维护配对/维护配对.csv', '维护配对.csv')
            assigner_df = pd.read_csv('维护配对.csv')
            try:
                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
            except:
                pass
            try:
                os.remove('维护配对.csv')
            except:
                pass
            table(assigner_df, assigner_df.columns, str('维护配对.csv'), False)
            assigner = st.form(key='assigner')
            assigner.subheader('客户匹配')
            col1, col2 = assigner.columns(2)
            col1.write('选择客户')
            clients = col1.multiselect('客户', list(filter(lambda x: len(x) > 1, client_directory['公共客户池'].keys())))
            col2.write('选择维护人员')
            download(buckets[0], ('用户' + '/' + '用户.csv'), '用户.csv')
            df = pd.read_csv('用户.csv')
            client_staff = list(df[(df['角色'] == '销售')]['帐号'])
            worker = col2.selectbox('维护人员', client_staff)
            if assigner.form_submit_button('匹配'):
                for client in clients:
                    columns = assigner_df.columns
                    old_workers = list(assigner_df['维护人员'])
                    new_clients = [i for i in clients if i not in columns]
                    old_clients = [j for j in clients if j in columns]
                    if client in new_clients:

                        if worker in old_workers:
                            # new client old worker

                            worker_ls = list(assigner_df['维护人员'])
                            pos = worker_ls.index(worker)
                            add_ls = [u * 0 for u in range(len(assigner_df) - 1)]
                            add_ls.insert(pos, 1)
                            assigner_df[client] = add_ls
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[3], '维护配对/维护配对.csv')
                            upload(buckets[3], '维护配对/维护配对.csv', 'updatedcsv.csv')
                            os.remove('updatedcsv.csv')
                            download(buckets[3], '维护配对/维护配对.csv', '维护配对.csv')
                            assigner_df = pd.read_csv('维护配对.csv')
                            os.remove('维护配对.csv')
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
                            delete(buckets[3], '维护配对/维护配对.csv')
                            upload(buckets[3], '维护配对/维护配对.csv', 'updatedcsv.csv')
                            os.remove('updatedcsv.csv')
                            download(buckets[3], '维护配对/维护配对.csv', '维护配对.csv')
                            assigner_df = pd.read_csv('维护配对.csv')
                            os.remove('维护配对.csv')
                    if client in old_clients:
                        if worker in old_workers:
                            # old client old worker

                            worker_ls = list(assigner_df['维护人员'])
                            work_pos = worker_ls.index(str(worker))
                            assigner_df.at[work_pos, client] = 1
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[3], '维护配对/维护配对.csv')
                            upload(buckets[3], '维护配对/维护配对.csv', 'updatedcsv.csv')
                            download(buckets[3], '维护配对/维护配对.csv', '维护配对.csv')
                            assigner_df = pd.read_csv('维护配对.csv')
                            os.remove('维护配对.csv')

                        else:
                            # old client new worker

                            add_ls = [0 * u for u in range(len(assigner_df.columns) - 1)]
                            add_ls.insert(0, worker)
                            add_df = pd.Series(add_ls, index=assigner_df.columns)
                            assigner_df = assigner_df.append(add_df, ignore_index=True)
                            worker_ls = list(assigner_df['维护人员'])
                            work_pos = worker_ls.index(str(worker))
                            assigner_df.at[work_pos, client] = 1
                            try:
                                assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                            except:
                                pass
                            assigner_df.to_csv('updatedcsv.csv')
                            delete(buckets[3], '维护配对/维护配对.csv')
                            upload(buckets[3], '维护配对/维护配对.csv', 'updatedcsv.csv')
                            download(buckets[3], '维护配对/维护配对.csv', '维护配对.csv')
                            assigner_df = pd.read_csv('维护配对.csv')
                            os.remove('维护配对.csv')
                st.success('完成')
