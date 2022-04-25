import streamlit as st
import pandas as pd
from backend import download
from backend import upload
from backend import iterator
from backend import delete
import os.path
from backend import table
from PIL import Image
from logistics import make_trans_order


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
    basic_directory = protempload(buckets[0])
    make_trans_order('karqbasics', 'karqproducts')
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

    tar_shop = st.selectbox('店铺', ['全部']+list(skus_dict.keys()))
    if tar_shop == '全部':
        tar_shop = list(skus_dict.keys())
    else:
        tar_shop = [tar_shop]
    for typ in list(filter(lambda x: len(x) > 1, list(product_directory['SKU'].keys()))):
        sku_ls = filter(lambda x: len(x) > 1, list(product_directory['SKU'][typ].keys()))

        for item in sku_ls:

            for shop_id in tar_shop:
                if item in skus_dict[shop_id]:
                    col1, col2, col3 = st.columns((1, 10, 2))
                    doc = list(product_directory['SKU'][typ][item].keys())
                    try:
                        with col1:
                            img_exist = False
                            for tar in doc:
                                if '图片' in tar:
                                    for tar2 in list(product_directory['SKU'][typ][item][tar].keys()):
                                        path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + tar2
                                        if '.jpg' in tar2 and img_exist == False:
                                            download(buckets[2], str(path), tar2)
                                            img = Image.open(tar2)
                                            # print(img.width, img.height)
                                            img = img.resize((88, 88))
                                            # print(img.width, img.height)
                                            st.image(img)
                                            img_exist = True

                            if not img_exist:
                                img = Image.open('image_not_found.jpg')
                                # print(img.width, img.height)
                                img = img.resize((88, 88))
                                # print(img.width, img.height)
                                st.image(img)
                        with col2:
                            with st.expander(str(item), expanded=True):
                                if st.checkbox('查看' + str(item) + '相关文件'):
                                    for tar in filter(lambda x: len(x) > 1,
                                                      list(product_directory['SKU'][typ][item].keys())):
                                        if '基础资料' in tar:
                                            path = str('SKU') + '/' + str(typ) + '/' + str(
                                                item) + '/' + tar + '/' + '基础资料.csv'
                                            download(buckets[2], str(path), '基础资料.csv')
                                            df = pd.read_csv('基础资料.csv')
                                            try:
                                                df.drop('Unnamed: 0', axis=1, inplace=True)
                                            except:
                                                pass
                                            table(df, df.columns, str(item) + str(tar), True, bucket=buckets[2],
                                                  path=path,
                                                  height=150)

                                        if '图片' in tar:
                                            for tar2 in list(product_directory['SKU'][typ][item][tar].keys()):
                                                path = str('SKU') + '/' + str(typ) + '/' + str(
                                                    item) + '/' + tar + '/' + tar2
                                                download(buckets[2], str(path), tar2)
                                                img = Image.open(tar2)
                                                # print(img.width, img.height)
                                                img = img.resize((200, 200))
                                                # print(img.width, img.height)
                                                st.image(img)
                                                if st.checkbox('删除', key=tar2 + path):
                                                    delete(buckets[2], str(path))
                                                    protempload(buckets[2])
                                    file_p = st.file_uploader('上传图片', type=['jpg'])
                                    if file_p is not None:
                                        with open(file_p.name, 'wb') as p:
                                            p.write(file_p.getbuffer())

                                    if st.button('上传', key='上传图片'):
                                        path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + '图片' + '/'
                                        upload(buckets[2], str(path) + str(file_p.name), file_p.name)
                                        os.remove(str(file_p.name))
                                        st.success('图片上传成功')

                                    langauage = st.selectbox('说明书语言',
                                                             ['中文', '英文', '法语', '德语', '意大利语', '西班牙语', '日语', '韩语',
                                                              '英法德意西五合一'])
                                    file_p = st.file_uploader('上传说明书', type=['pdf'])
                                    if file_p is not None:
                                        with open(file_p.name, 'wb') as p:
                                            p.write(file_p.getbuffer())
                                    if st.button('上传', key='上传说明书'):
                                        path = str('SKU') + '/' + str(typ) + '/' + str(
                                            item) + '/' + '说明书' + '/' + langauage + '/'
                                        upload(buckets[2], str(path) + str(file_p.name), '说明书.pdf')
                                        os.remove(str(file_p.name))
                                        st.success('说明书上传成功')

                            with st.expander('下载说明书', expanded=False):
                                for tar in doc:
                                    if '说明书' in tar:
                                        for tar2 in list(product_directory['SKU'][typ][item][tar].keys()):
                                            path = str('SKU') + '/' + str(typ) + '/' + str(
                                                item) + '/' + tar + '/' + tar2
                                            if st.checkbox(tar2, key=path):
                                                download(buckets[2], path, tar2)
                                                with open(tar2, "rb") as file:
                                                    st.download_button(
                                                        label="下载" + tar2,
                                                        data=file,
                                                        file_name=tar2,
                                                        mime="image/png"
                                                    )


                        with col3:
                            if st.button('删除' + item, key=item):
                                for folder in list(product_directory['SKU'][typ][item].keys()):
                                    for file in list(product_directory['SKU'][typ][item][folder].keys()):
                                        delete(buckets[2], 'SKU/' + typ + '/' + item + '/' + folder + '/' + file)
                                        protempload(buckets[2])


                    except:
                        st.write('文件不存在')
