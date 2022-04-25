import streamlit as st
from backend import download
from backend import upload
from backend import delete
from backend import copy
from backend import iterator
from backend import table
from backend import render_set_style_of_single_bar
import pandas as pd
import os.path
import base64
import time
from PIL import Image
from backend import nonread_file


# Initialize session state
if 'search_sku' not in st.session_state:
    st.session_state.search_sku = False

product_directory = dict()
buckets = ['karqproducts', 'karqbasics', 'karqshops']


def protempload(bucket):
    global product_directory

    for path in iterator(bucket):
        parent = product_directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]

    return product_directory


def productpage():
    global product_directory
    st.info('注意:统计数据可能出现延迟')
    product_directory = protempload(buckets[0])
    st.subheader('产品资料')
    protempload(buckets[0])
    ver = unver = sku = failed = 0
    for aa in (product_directory['已审核']):
        ver = ver + len(list(filter(lambda x: len(x) > 1, (product_directory['已审核'][aa]))))

    for bb in (product_directory['未审核']):
        unver = unver + len(list(filter(lambda x: len(x) > 1, (product_directory['未审核'][bb]))))

    for cc in (product_directory['SKU']):
        sku = sku + len(list(filter(lambda x: len(x) > 1, (product_directory['SKU'][cc]))))

    for dd in (product_directory['驳回产品']):
        failed = failed + len(list(filter(lambda x: len(x) > 1, (product_directory['驳回产品'][dd]))))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="产品审核中", value=unver)
    col2.metric(label="产品总量", value=ver)
    col3.metric(label="SKU总量", value=sku)
    col4.metric(label="驳回项目", value=failed)

    function_pages = [
        "产品审核",
        "产品总览",
        'SKU总览',
        '新增产品系列',
        '产品范本修改'
    ]
    render_set_style_of_single_bar(["产品审核中", "产品总量", "SKU总量", "驳回项目"], [unver, ver, sku, failed])
    col1, col2, col3 = st.columns((1, 1, 2))

    with col1:
        func = st.expander('功能', expanded=True)
        function = func.radio('', function_pages)
    with col2:
        sub_function = st.empty()
    if function == '产品(SKU)搜索':
        product_directory = protempload(buckets[0])
        product_search(version=2)
    if function == '产品(SKU)总览':
        product_directory = protempload(buckets[0])
        product_gallery()
    if function == '产品审核':
        product_directory = protempload(buckets[0])
        productverifypage()
    if function == '产品总览':
        product_directory = protempload(buckets[0])
        verified_product(sub_function)
    if function == 'SKU总览':
        product_directory = protempload(buckets[0])
        verified_sku()
    if function == '新增产品系列':
        product_directory = protempload(buckets[0])
        product_uploadinfo('未审核', product_directory, False, False)
    if function == '添加SKU资料':
        product_directory = protempload(buckets[0])
        product_uploadinfo('SKU', product_directory, False, False)
    if function == '产品范本修改':
        product_directory = protempload(buckets[0])
        with st.expander("修改产品资料范本",expanded=True):
            formatter()


timestr = time.strftime("%Y%m%d-%H%M%S")


def csv_downloader(data, name):
    csvfile = data.to_csv()
    b64 = base64.b64encode(csvfile.encode()).decode()
    name = name + ".csv"
    new_filename = name.format(timestr)
    st.markdown("#### " + name + " ###")
    href = f'<a href="data:file/csv;base64,{b64}" download="{new_filename}">点击下载 </a>'
    st.markdown(href, unsafe_allow_html=True)


def product_search(version):
    global product_directory
    st.subheader('产品(SKU)搜索:')
    if version == 1:
        with st.form(key='searchform'):
            nav1, nav2, nav3 = st.columns((3, 2, 1))
            with nav1:
                search_term = st.text_input('名称')
            with nav2:
                feature1 = st.text_input("特征1")
            with nav3:
                st.text('查询')
                submit_search = st.form_submit_button('确认')
    if version == 2:
        sku_list = []

        for cc in (product_directory['SKU']):
            for dd in (product_directory['SKU'][cc]):
                sku_list.append((cc, dd))

        sku_dict = {letter: score for score, letters in sku_list for letter in letters.split()}
        list(sku_dict.keys())
        sku_list = list(sku_dict.keys())
        sku_list.insert(0, ' ')
        with st.form(key='searchform'):
            nav1, nav2, nav3 = st.columns((3, 2, 1))
            with nav1:
                select = st.selectbox('搜索', sku_list)
            with nav2:
                st.selectbox('筛选', [])
            with nav3:
                st.text('查询')
                submit_search = st.form_submit_button('确认')
                st.session_state.search_sku = True
            sku_ls = [select]
        if submit_search or st.session_state.search_sku and select != ' ':
            for sku in sku_ls:
                typ = sku_dict[sku]
                item = sku

                col1, col2 = st.columns((1, 8))
                lan = list(product_directory['SKU'][typ][item].keys())
                lang = lan[0]
                plats = list(product_directory['SKU'][typ][item][lang].keys())
                platform = plats[0]
                with col1:
                    img_exist = False
                    for tar in filter(lambda x: len(x) > 1,
                                      list(product_directory['SKU'][typ][item][lang][platform].keys())):

                        for tar2 in filter(lambda x: len(x) > 1,
                                           list(product_directory['SKU'][typ][item][lang][platform][
                                                    tar].keys())):
                            path = 'SKU/' + str(typ) + '/' + str(item) + '/' + str(
                                lang) + '/' + str(platform) + '/' + tar + '/' + tar2

                            if '.jpg' in tar2:
                                download(
                                    buckets[0],
                                    str(path),
                                    tar2)
                                img = Image.open(tar2)
                                #print(img.width, img.height)
                                img = img.resize((88, 88))
                                #print(img.width, img.height)
                                st.image(img)
                                img_exist = True

                        if not img_exist:
                            img = Image.open('image_not_found.jpg')
                            #print(img.width, img.height)
                            img = img.resize((88, 88))
                            #print(img.width, img.height)
                            st.image(img)
                with col2:
                    with st.expander(str(item), expanded=True):
                        if st.checkbox('查看' + str(item) + '相关文件'):
                            lan = list(product_directory['SKU'][typ][item].keys())
                            lang = lan[0]
                            plats = list(product_directory['SKU'][typ][item][lang].keys())
                            platform = plats[0]

                            for tar in filter(lambda x: len(x) > 1,
                                              list(product_directory['SKU'][typ][item][lang][platform].keys())):

                                for tar2 in filter(lambda x: len(x) > 1,
                                                   list(product_directory['SKU'][typ][item][lang][platform][
                                                            tar].keys())):

                                    path = 'SKU/' + str(typ) + '/' + str(item) + '/' + str(
                                        lang) + '/' + str(platform) + '/' + tar + '/' + tar2

                                    if '.csv' in tar2:
                                        download(buckets[0], str(path), tar2)
                                        df = pd.read_csv(tar2)
                                        try:
                                            df.drop('Unnamed: 0', axis=1, inplace=True)
                                        except:
                                            pass
                                        table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0], path=path)
                                    if '.jpg' in tar2:
                                        img = Image.open(tar2)
                                        #print(img.width, img.height)
                                        img = img.resize((100, 100))
                                        #print(img.width, img.height)
                                        st.image(img)

                            if st.checkbox('上传图片', key=path):
                                file_p = st.file_uploader('上传图片', type=['jpg'])
                                if st.checkbox('上传'):
                                    path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + str(
                                        lang) + '/' + str(
                                        platform) + '/' + '图片' + '/'
                                    upload(buckets[0], str(path) + str(file_p.name), str(file_p.name))
                                    os.remove(str(file_p.name))
                                    st.success('图片上传成功')
    return product_directory


def product_gallery():
    global product_directory
    protempload(buckets[0])
    st.subheader('产品总览:')
    product_ls = []
    for cc in (product_directory['已审核']):
        for dd in (product_directory['已审核'][cc]):
            product_ls.append([cc, dd])

    for product in product_ls:
        typ = product[0]
        item = product[1]
        col1, col2 = st.columns((1, 8))
        doc = list(product_directory['已审核'][typ][item].keys())
        docu = doc[0]

        with col1:
            img_exist = False
            for tar in filter(lambda x: len(x) > 1,
                              list(product_directory['已审核'][typ][item][docu].keys())):

                for tar2 in filter(lambda x: len(x) > 1,
                                   list(product_directory['已审核'][typ][item][docu][tar].keys())):
                    path = '已审核/' + str(typ) + '/' + str(item) + '/' + str(
                        docu) + '/'  + tar + '/' + tar2

                    if '.jpg' in tar2:
                        download(
                            buckets[0],
                            str(path),
                            tar2)
                        img = Image.open(tar2)
                        #print(img.width, img.height)
                        img = img.resize((88, 88))
                        #print(img.width, img.height)
                        st.image(img)
                        img_exist = True

                if not img_exist:
                    img = Image.open('image_not_found.jpg')
                    #print(img.width, img.height)
                    img = img.resize((88, 88))
                    #print(img.width, img.height)
                    st.image(img)
        with col2:
            with st.expander(str(item), expanded=True):
                if st.checkbox('查看' + str(item) + '相关文件'):
                    doc = list(product_directory['已审核'][typ][item].keys())
                    docu = doc[0]


                    for tar in filter(lambda x: len(x) > 1,
                                      list(product_directory['已审核'][typ][item][docu].keys())):

                        for tar2 in filter(lambda x: len(x) > 1,
                                           list(product_directory['已审核'][typ][item][docu][tar].keys())):
                            path = '已审核/' + str(typ) + '/' + str(item) + '/' + str(
                                docu) + '/' + tar + '/' + tar2
                            if '.csv' in tar2:
                                download(buckets[0], str(path), tar2)
                                df = pd.read_csv(tar2)
                                try:
                                    df.drop('Unnamed: 0', axis=1, inplace=True)
                                except:
                                    pass
                                table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0], path=path)
                            if '.jpg' in tar2:
                                img = Image.open(tar2)
                                #print(img.width, img.height)
                                img = img.resize((100, 100))
                                #print(img.width, img.height)
                                st.image(img)
                    if st.checkbox('上传图片', key=path):
                        file_p = st.file_uploader('上传图片' + '/' + 'Upload Picture', type=['jpg'])
                        if st.checkbox('上传'):
                            path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + str(docu) + '/' + '图片' + '/'
                            upload(buckets[0], str(path) + str(file_p.name), str(file_p.name))
                            os.remove(str(file_p.name))
                            st.success('图片上传成功')
    return product_directory


def productverifypage():
    st.subheader('需要审核项目:')
    protempload(buckets[0])
    verify_ls = []
    for b in filter(lambda x: len(x) > 1, (product_directory['未审核'])):
        for c in filter(lambda x: len(x) > 1, (product_directory['未审核'][b])):
            verify_ls.append([b, c])

    typ_ls = set([i[0] for i in verify_ls])
    if len(list(filter(lambda x: len(x) > 1, typ_ls))) == 0:
        st.write('无审核项目')
    else:
        item = st.selectbox('', filter(lambda x: len(x) > 1, typ_ls), key='审核项目')
        product_ls = product_directory['未审核'][item]

        for product in product_ls:
            if product is not None:

                with st.expander('审核' + str(product), expanded=True):
                    if st.checkbox('审核' + str(product)):
                        st.write(product)
                        try:
                            protempload(buckets[0])
                            col1, col2, col3 = st.columns((3, 3, 3))
                            for files in (list(product_directory['未审核'][item][product].keys())):
                                for file in filter(lambda x: len(x) > 1,
                                                   (list(product_directory['未审核'][item][product][files].keys()))):

                                    col1.write(file, key=product)
                                    if col2.checkbox('打开', key=file + product):
                                        path = '未审核' + '/' + item + '/' + product + '/' + files + '/' + file
                                        download(buckets[0], str(path), file)
                                        try:
                                            df = pd.read_csv(file)
                                            try:
                                                df.drop('Unnamed: 0', axis=1, inplace=True)
                                            except:
                                                pass
                                            table(df, df.columns, str(file), True)



                                        except:
                                            download(
                                                buckets[0],
                                                str(path),
                                                file)
                                            st.image(file)

                            deci = st.selectbox('决定', ['批准', '不批准'], key=product)
                            if deci == '批准':
                                if st.checkbox('确认', key='批准确认' + product):
                                    for group in (list(product_directory['未审核'][item][product].keys())):
                                        for pssfile in (
                                                list(product_directory['未审核'][item][product][group].keys())):
                                            path = item + '/' + product + '/' + group + '/' + pssfile
                                            download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                            upload(buckets[0], '已审核' + '/' + str(path), pssfile)
                                            delete(buckets[0], '未审核' + '/' + str(path))
                                            protempload(buckets[0])
                                            st.success('成功上传' + pssfile)

                            if deci == '不批准':

                                if st.checkbox('确认', key='不批准确认' + product):
                                    for group in (list(product_directory['未审核'][item][product].keys())):
                                        for pssfile in (
                                                list(product_directory['未审核'][item][product][group].keys())):
                                            path = item + '/' + product + '/' + group + '/' + pssfile
                                            download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                            upload(buckets[0], '驳回产品' + '/' + str(path), pssfile)
                                            delete(buckets[0], '未审核' + '/' + str(path))
                                            protempload(buckets[0])
                                            st.success('成功上传' + pssfile)
                        except:
                            print('error:productverifypage()')
    st.subheader('驳回项目:')
    unsupported_ls = []
    for b in filter(lambda x: len(x) > 1, (product_directory['驳回产品'])):
        for c in filter(lambda x: len(x) > 1, (product_directory['驳回产品'][b])):
            unsupported_ls.append([b, c])
    typ_ls = set([i[0] for i in unsupported_ls])
    if len(list(filter(lambda x: len(x) > 1, typ_ls))) == 0:
        st.write('无驳回项目')
    else:
        item = st.selectbox('', filter(lambda x: len(x) > 1, typ_ls), key='驳回项目')
        product_ls = product_directory['驳回产品'][item]
        for product in product_ls:
            if product is not None:
                with st.expander(str(product), expanded=True):
                    if st.checkbox('审核' + str(product) + '相关文件'):
                        st.write(product)
                        try:

                            if st.checkbox('打开', key=str(product)):
                                protempload(buckets[0])
                                col1, col2, col3 = st.columns((3, 3, 3))
                                for files in (list(product_directory['驳回产品'][item][product].keys())):
                                    for file in filter(lambda x: len(x) > 1,
                                                       (list(product_directory['驳回产品'][item][product][files].keys()))):

                                        col1.write(file, key=product)
                                        if col2.checkbox('打开', key=file + product):
                                            path = '驳回产品' + '/' + item + '/' + product + '/' + files + '/' + file
                                            download(buckets[0], str(path), file)
                                            try:
                                                df = pd.read_csv(file)
                                                try:
                                                    df.drop('Unnamed: 0', axis=1, inplace=True)
                                                except:
                                                    pass
                                                table(df, df.columns, str(file), True)



                                            except:
                                                download(
                                                    buckets[0],
                                                    str(path),
                                                    file)
                                                st.image(file)

                                deci = st.selectbox('决定', ['批准', '不批准'], key=product)
                                if deci == '批准':
                                    if st.checkbox('确认', key='批准确认' + product):
                                        for group in (
                                                list(product_directory['未审核'][item][product].keys())):
                                            for pssfile in (
                                                    list(
                                                        product_directory['未审核'][item][product][group].keys())):

                                                path = item + '/' + product + '/' + group + '/' + pssfile
                                                download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                                upload(buckets[0], '已审核' + '/' + str(path), pssfile)
                                                delete(buckets[0], '未审核' + '/' + str(path))
                                                protempload(buckets[0])
                                                st.success('成功上传' + pssfile)


                                if deci == '不批准':

                                    if st.checkbox('确认', key='不批准确认' + product):
                                        for group in (
                                                list(product_directory['未审核'][item][product].keys())):
                                            for pssfile in (
                                                    list(
                                                        product_directory['未审核'][item][product][group].keys())):
                                                path = item + '/' + product + '/' + group + '/' + pssfile
                                                download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                                upload(buckets[0], '驳回产品' + '/' + str(path), pssfile)
                                                delete(buckets[0], '未审核' + '/' + str(path))
                                                protempload(buckets[0])
                                                st.success('成功上传' + pssfile)


                        except:
                            print('error:productverifypage()')

    return product_directory


def verified_product(sub_function):
    global product_directory
    protempload(buckets[0])
    with sub_function.expander("",expanded=True):
        sub_func = st.radio('其他选项',["基础资料","使用方法与故障排除"])
    st.subheader('产品资料:')
    product_list = list(filter(lambda x: len(x) > 1, list(product_directory['已审核'].keys())))
    typ = st.selectbox('产品类别', ['全部'] + product_list)
    if typ == '全部':
        dst_list = product_list
    else:
        dst_list = [typ]
    for typ in dst_list:
        product_ls = filter(lambda x: len(x) > 1, list(product_directory['已审核'][typ].keys()))
        for item in product_ls:
            col1, col2,col3 = st.columns((1, 10, 2))
            doc = list(product_directory['已审核'][typ][item].keys())
            try:
                doc.remove('SKU')
            except:
                pass
            try:
                with col1:
                    img_exist = False
                    for tar in doc:
                        if '图片' in tar:
                            for tar2 in list(product_directory['已审核'][typ][item][tar].keys()):
                                path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + tar2
                                if '.jpg' in tar2 and img_exist == False:
                                    download(buckets[0],str(path),tar2)
                                    img = Image.open(tar2)
                                    #print(img.width, img.height)
                                    img = img.resize((88, 88))
                                    #print(img.width, img.height)
                                    st.image(img)
                                    img_exist = True

                    if not img_exist:
                        img = Image.open('image_not_found.jpg')
                        #print(img.width, img.height)
                        img = img.resize((88, 88))
                        #print(img.width, img.height)
                        st.image(img)

                with col2:
                    with st.expander(str(item), expanded=True):
                        if st.checkbox('查看' + str(item) + '相关文件'):

                            for tar in doc:
                                if sub_func == '基础资料':
                                    if '基础资料' in tar:
                                        path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + '基础资料.csv'
                                        download(buckets[0], str(path), '基础资料.csv')
                                        df = pd.read_csv('基础资料.csv')
                                        try:
                                            df.drop('Unnamed: 0', axis=1, inplace=True)
                                        except:
                                            pass
                                        table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0], path=path,
                                              height=150)

                                    if '图片' in tar:
                                        for tar2 in list(product_directory['已审核'][typ][item][tar].keys()):
                                            path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + tar2
                                            download(buckets[0], str(path), tar2)
                                            img = Image.open(tar2)
                                            #print(img.width, img.height)
                                            img = img.resize((200, 200))
                                            #print(img.width, img.height)
                                            st.image(img)
                                            if st.checkbox('删除', key=tar2 + path):
                                                delete(buckets[0], str(path))
                                                protempload(buckets[0])







                                if sub_func == "使用方法与故障排除":
                                    if '提问' in tar:
                                        path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + '问答.csv'
                                        download(buckets[0], str(path), '问答.csv')
                                        df = pd.read_csv('问答.csv')
                                        try:
                                            df.drop('Unnamed: 0', axis=1, inplace=True)
                                        except:
                                            pass
                                        table(df, df.columns, str(item) + '问答.csv', True, bucket=buckets[0], path=path,
                                              height=150)

                                    if '评论' in tar:
                                        path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + '评论.csv'
                                        download(buckets[0], str(path), '评论.csv')
                                        df = pd.read_csv('评论.csv')
                                        try:
                                            df.drop('Unnamed: 0', axis=1, inplace=True)
                                        except:
                                            pass
                                        table(df, df.columns, str(item) + '评论.csv', True, bucket=buckets[0], path=path,
                                              height=150)




                            if sub_func == '基础资料':

                                file_p = st.file_uploader('上传图片', type=['jpg'])
                                if file_p is not None:
                                    with open(file_p.name, 'wb') as p:
                                        p.write(file_p.getbuffer())

                                if st.button('上传',key='上传图片'):
                                    path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + '图片' + '/'
                                    upload(buckets[0], str(path) + str(file_p.name), file_p.name)
                                    os.remove(str(file_p.name))
                                    st.success('图片上传成功')

                                langauage = st.selectbox('说明书语言',['中文', '英文', '法语', '德语', '意大利语', '西班牙语', '日语', '韩语', '英法德意西五合一'])
                                file_p = st.file_uploader('上传说明书', type=['pdf'])
                                if file_p is not None:
                                    with open(file_p.name, 'wb') as p:
                                        p.write(file_p.getbuffer())
                                if st.button('上传',key='上传说明书'):
                                    path = str('已审核') + '/' + str(typ) + '/' + str(
                                        item) + '/' + '说明书' + '/' + langauage + '/'
                                    upload(buckets[0], str(path) + str(file_p.name), '说明书.pdf')
                                    os.remove(str(file_p.name))
                                    st.success('说明书上传成功')




                    with st.expander('创建SKU/查看关联SKU',expanded=False):
                        if st.checkbox('创建SKU系列', key=str(item) + str(tar) + str(tar)):
                            asin_name = st.text_input('ASIN 名(必填)')
                            sku_name = st.text_input('SKU 名(必填)')
                            langauage = st.selectbox('语言', ['中文', '英文', '法语', '德语', '意大利语', '西班牙语', '日语', '韩语'])
                            worker = st.selectbox('店铺(非必填)', [str(i) + '-' + str(k) for i, k in
                                                              zip(nonread_file(buckets[1], '店铺/店铺资料.csv',
                                                                               '店铺资料.csv',
                                                                               '店铺名', True),
                                                                  nonread_file(buckets[1], '店铺/店铺资料.csv',
                                                                               '店铺资料.csv', '站点',
                                                                               True))])

                            if st.button('确认创建SKU'):

                                downloadpath1 = str('已审核') + '/' + str(typ) + '/' + str(
                                    item) + '/' + '基础资料' + '/' + '基础资料.csv'

                                uploadpath1 = 'SKU/' + str(typ) + '/' + str(asin_name) + '-' + str(
                                    sku_name) + '-' + langauage + '/' + '基础资料' + '/' + '基础资料.csv'

                                uploadpath2 = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + 'SKU/' + str(
                                    asin_name) + '-' + str(sku_name) + '-' + langauage + '/' + '基础资料' + '/' + '基础资料.csv'

                                # check if manual of lan exist
                                if len(product_directory['已审核'][typ][item]['说明书'][langauage].keys()) > 0:
                                    st.info(langauage + '说明书存在')
                                    downloadpath3 = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + '说明书' + '/' + langauage + '/' + '说明书.pdf'
                                    uploadpath3 = 'SKU/' + str(typ) + '/' + str(asin_name) + '-' + str(sku_name) + '-' + langauage + '/' + '说明书' + '/' + '说明书.pdf'
                                    copy(buckets[0],buckets[0], downloadpath3,uploadpath3)



                                copy(buckets[0],buckets[0],downloadpath1,uploadpath1)
                                upload(buckets[0], str(uploadpath2), '基础资料.csv')
                                protempload(buckets[0])

                                if worker is not None:
                                    download(buckets[2], '产品配对/产品配对.csv', '产品配对.csv')
                                    assigner_df = pd.read_csv('产品配对.csv')
                                    try:
                                        assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                                    except:
                                        pass
                                    try:
                                        os.remove('产品配对.csv')
                                    except:
                                        pass
                                    clients = [str(asin_name) + '-' + str(sku_name) + '-' + langauage]
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
                                                delete(buckets[2], '产品配对/产品配对.csv')
                                                protempload(buckets[0])
                                                upload(buckets[2], '产品配对/产品配对.csv', 'updatedcsv.csv')
                                                os.remove('updatedcsv.csv')
                                                download(buckets[2], '产品配对/产品配对.csv', '产品配对.csv')
                                                assigner_df = pd.read_csv('产品配对.csv')
                                                os.remove('产品配对.csv')
                                            else:
                                                # new client new worker

                                                assigner_df[client] = [u * 0 for u in
                                                                       range(len(assigner_df.columns) - 1)]
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
                                                delete(buckets[2], '产品配对/产品配对.csv')
                                                protempload(buckets[0])
                                                upload(buckets[2], '产品配对/产品配对.csv', 'updatedcsv.csv')
                                                os.remove('updatedcsv.csv')
                                                download(buckets[2], '产品配对/产品配对.csv', '产品配对.csv')
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
                                                delete(buckets[2], '产品配对/产品配对.csv')
                                                protempload(buckets[0])
                                                upload(buckets[2], '产品配对/产品配对.csv', 'updatedcsv.csv')
                                                download(buckets[2], '产品配对/产品配对.csv', '产品配对.csv')
                                                assigner_df = pd.read_csv('产品配对.csv')
                                                os.remove('产品配对.csv')

                                            else:
                                                # old client new worker

                                                add_ls = [0 * u for u in range(len(assigner_df.columns) - 1)]
                                                add_ls.insert(0, worker)
                                                add_df = pd.Series(add_ls, index=assigner_df.columns)
                                                assigner_df = assigner_df.append(add_df, ignore_index=True)
                                                worker_ls = list(assigner_df['店铺'])
                                                st.write(worker_ls)
                                                st.write(worker)
                                                work_pos = worker_ls.index(str(worker))
                                                assigner_df.at[work_pos, client] = 1
                                                try:
                                                    assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                                                except:
                                                    pass
                                                assigner_df.to_csv('updatedcsv.csv')
                                                delete(buckets[2], '产品配对/产品配对.csv')
                                                protempload(buckets[0])
                                                upload(buckets[2], '产品配对/产品配对.csv', 'updatedcsv.csv')
                                                download(buckets[2], '产品配对/产品配对.csv', '产品配对.csv')
                                                assigner_df = pd.read_csv('产品配对.csv')
                                                os.remove('产品配对.csv')
                                                protempload(buckets[0])
                                    st.success('完成')
                        if st.checkbox('打开关联sku', key=item):

                            for tar in filter(lambda x: len(x) > 1,
                                              list(product_directory['已审核'][typ][item]['SKU'].keys())):
                                st.write(tar)



                    with st.expander('下载说明书',expanded=False):

                        for tar in doc:

                            if '说明书' in tar:
                                for lang in list(product_directory['SKU'][typ][item][tar].keys()):
                                    for tar2 in list(product_directory['SKU'][typ][item][tar][lang].keys()):
                                        path = str('SKU') + '/' + str(typ) + '/' + str(
                                            item) + '/' + tar + '/' + lang + '/' + tar2
                                        st.write(path)
                                        if st.checkbox(lang+'-'+tar2, key=path):
                                            download(buckets[0],path,tar2)
                                            with open(tar2, "rb") as file:
                                                st.download_button(
                                                    label="下载"+lang+'-'+tar2,
                                                    data=file,
                                                    file_name=tar2,
                                                    mime="image/png"
                                                )


                with col3:
                    if st.button('删除'+item,key=item):
                        for folder in list(product_directory['已审核'][typ][item].keys()):
                            for file in list(product_directory['已审核'][typ][item][folder].keys()):
                                delete(buckets[0],'已审核/'+typ+'/'+item+'/'+folder+'/'+file)
                                protempload(buckets[0])

                        try:
                            if len(list(product_directory['已审核'][typ][item]['SKU'].keys())) > 0:
                                for skus in list(product_directory['已审核'][typ][item]['SKU'].keys()):
                                    for skus_folder in list(product_directory['已审核'][typ][item]["SKU"][skus].keys()):
                                        for skus_files in list(product_directory['已审核'][typ][item]["SKU"][skus][skus_folder].keys()):
                                            delete(buckets[0], '已审核/' + typ + '/' + item + '/' + 'SKU' + '/' + skus + '/' + skus_folder + '/' + skus_files)
                                            protempload(buckets[0])


                        except:
                            print('no sku in this product')

                        try:
                            if len(list(product_directory['已审核'][typ][item]['说明书'].keys())) > 0:
                                for lang in list(product_directory['已审核'][typ][item]['说明书'].keys()):
                                    for files in list(product_directory['已审核'][typ][item]['说明书'][lang].keys()):
                                        delete(buckets[0],
                                               '已审核/' + typ + '/' + item + '/' + '说明书' + '/' + lang + '/' + files)
                                        protempload(buckets[0])

                        except:
                            print('no manual in this product')
            except:
                pass



    return product_directory










def verified_sku():
    global product_directory
    protempload(buckets[0])
    st.subheader('打开SKU:')
    if len(list(filter(lambda x: len(x) > 1, list(product_directory['SKU'].keys())))) == 0:
        st.write('无SKU')
    else:
        typ = st.selectbox('产品类别', list(filter(lambda x: len(x) > 1, list(product_directory['SKU'].keys()))))
        sku_ls = filter(lambda x: len(x) > 1, list(product_directory['SKU'][typ].keys()))
        protempload(buckets[0])
        for item in sku_ls:
            col1, col2, col3 = st.columns((1, 10, 2))
            doc=list(product_directory['SKU'][typ][item].keys())
            try:
                with col1:
                    img_exist = False
                    for tar in doc:
                        if '图片' in tar:
                            for tar2 in list(product_directory['SKU'][typ][item][tar].keys()):
                                path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + tar2
                                if '.jpg' in tar2 and img_exist == False:
                                    download(buckets[0], str(path), tar2)
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
                                    path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + '基础资料.csv'
                                    download(buckets[0], str(path), '基础资料.csv')
                                    df = pd.read_csv('基础资料.csv')
                                    try:
                                        df.drop('Unnamed: 0', axis=1, inplace=True)
                                    except:
                                        pass
                                    table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0], path=path,
                                          height=150)

                                if '图片' in tar:
                                    for tar2 in list(product_directory['SKU'][typ][item][tar].keys()):
                                        path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + tar + '/' + tar2
                                        download(buckets[0], str(path), tar2)
                                        img = Image.open(tar2)
                                        # print(img.width, img.height)
                                        img = img.resize((200, 200))
                                        # print(img.width, img.height)
                                        st.image(img)
                                        if st.checkbox('删除', key=tar2 + path):
                                            delete(buckets[0], str(path))
                                            protempload(buckets[0])
                            file_p = st.file_uploader('上传图片', type=['jpg'])
                            if file_p is not None:
                                with open(file_p.name, 'wb') as p:
                                    p.write(file_p.getbuffer())

                            if st.button('上传', key='上传图片'):
                                path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + '图片' + '/'
                                upload(buckets[0], str(path) + str(file_p.name), file_p.name)
                                os.remove(str(file_p.name))
                                st.success('图片上传成功')


                            langauage = st.selectbox('说明书语言', ['中文', '英文', '法语', '德语', '意大利语', '西班牙语', '日语', '韩语', '英法德意西五合一'])
                            file_p = st.file_uploader('上传说明书', type=['pdf'])
                            if file_p is not None:
                                with open(file_p.name, 'wb') as p:
                                    p.write(file_p.getbuffer())
                            if st.button('上传', key='上传说明书'):
                                path = str('SKU') + '/' + str(typ) + '/' + str(
                                    item) + '/' + '说明书' + '/' + langauage + '/'
                                upload(buckets[0], str(path) + str(file_p.name), '说明书.pdf')
                                os.remove(str(file_p.name))
                                st.success('说明书上传成功')

                    with st.expander('下载说明书', expanded=False):
                        for tar in doc:
                            if '说明书' in tar:
                                for tar2 in list(product_directory['SKU'][typ][item][tar].keys()):
                                    path = str('SKU') + '/' + str(typ) + '/' + str(
                                        item) + '/' + tar + '/' + tar2
                                    if st.checkbox(tar2, key=path):
                                        download(buckets[0], path, tar2)
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
                                delete(buckets[0], 'SKU/' + typ + '/' + item + '/' + folder + '/' + file)
                                protempload(buckets[0])


            except:
                st.write('文件不存在')
    return product_directory


def formatter():
    download(buckets[0], '范本/产品参数范本.csv', '产品参数范本.csv')
    with open('产品参数范本.csv', "rb") as file:
        st.download_button(
            label="下载产品参数范本(csv版)",
            data=file,
            file_name='产品参数范本.csv',
            mime="image/png"
        )
    newformat = st.file_uploader('上传新范本', type=['csv'])
    if newformat is not None:
        df = pd.read_csv(newformat)
        try:
            df.drop('Unnamed: 0', axis=1, inplace=True)
        except:
            pass
        df.to_csv('产品参数范本.csv')
        table(df, df.columns, '产品参数范本.csv',False,height=100)

    if st.button('上传'):
        upload(buckets[0], '范本/产品参数范本.csv', '产品参数范本.csv')
        protempload(buckets[0])
        st.success('上传成功')



def product_uploadinfo(verify, dire, Type, Name):
    if Type == Name == False:
        col1, col2, col3, col4 = st.columns((1, 1, 1, 1))
        protypels = list(dire['已审核'].keys())
        add_type=col1.selectbox('',['旧类别-新产品','新类别-新产品'])

        if add_type=='旧类别-新产品':
            typ = col1.selectbox('类别', protypels, key='已有类别-新产品')
            name = col1.text_input('新产品名', key='已有类别-新产品')
        elif add_type=='新类别-新产品':
            typ = col1.text_input('新产品类别', key='新类别-新产品')
            name = col1.text_input('新产品名', key='新类别-新产品')


    else:
        typ = Type
        name = Name

    #basic = False
    picture = False
    #video = False

    basic = True
    download(buckets[0], '范本/产品参数范本.csv', '产品参数范本.csv')
    df = pd.read_csv('产品参数范本.csv')
    try:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    col1, col2 = st.columns((3, 2))
    for col in df.columns:
        df.loc[0, col] = col1.text_input(col)
    for col in df.columns:
        if len(df.loc[0, col]) == 0:
            df.loc[0, col] = ' '
    df.to_csv('基础资料.csv')


    form = st.form(key='my-form')
    # lang = form.selectbox('语言', ['中文', '英文', '法语', '德语', '意大利语', '西班牙语', '日语', '韩语'])
    # platform = form.selectbox('平台', ['亚马逊', '京东', '淘宝'], key='uploadinfo_platform')

    file_p = form.file_uploader('上传图片' + '/' + 'Upload Picture', type=['jpg'])
    if file_p is not None:
        with open(file_p.name, 'wb') as p:
            p.write(file_p.getbuffer())
            picture = True

    # file_v = form.file_uploader('上传视频' + '/' + 'Upload Video', type=['mp4'])
    # if file_v is not None:
    #     with open(file_v.name, 'wb') as v:
    #         v.write(file_v.getbuffer())
    #         video = True



    product_uploadinfo_submit = form.form_submit_button('上传')

    if product_uploadinfo_submit:

        path = verify + '/' + typ + '/' + name + '/' + '评论' + '/'
        upload(buckets[0], str(path) + '评论.csv', '评论.csv')

        path = verify + '/' + typ + '/' + name + '/' + '提问' + '/'
        upload(buckets[0], str(path) + '问答.csv', '问答.csv')
        if basic:
            path = verify + '/' + typ + '/' + name + '/' + '基础资料' + '/'
            upload(buckets[0], str(path) + '基础资料.csv', '基础资料.csv')
            os.remove('基础资料.csv')
            os.remove('产品参数范本.csv')
            form.success('基础资料上传成功')
        if picture:
            path = verify + '/' + typ + '/' + name + '/' + '图片' + '/'
            upload(buckets[0], str(path) + str(file_p.name), str(file_p.name))
            os.remove(str(file_p.name))
            form.success('图片上传成功')

        # if video:
        #     path = verify + '/' + typ + '/' + name + '/' + '视频' + '/'
        #     upload(buckets[0], str(path) + str(file_v.name), str(file_v.name))
        #     os.remove(str(file_v.name))
        #     form.success('视频上传成功')

    return product_directory


PRODUCT_QA = """
 <div style="width:90%;height:100%;margin:1px;border-radius:5px;
  background-color:#70dc70;font-size:18px;height:auto;border-left: 5px solid #dc70dc;">
 <h4 style="color:#000000;">{}</h4>
 <h4 style="color:#000000;">{}</h4>
 <h4 style="color:#000000;">{}</h4>
 <h6 style="color:#000000;text-align:center">{}</h6>
 </div>
 """


def qa_format(qa):
    response = pd.read_csv(qa)
    for x in range(0, len(response)):
        date = response['日期'][x]
        buyer = response['用户'][x]
        question = response['提问'][x]
        answer = response['回答'][x]
        st.markdown(PRODUCT_QA.format('用户:' + str(buyer), '问题 :' + str(question), '回答 :' + str(answer), date),
                    unsafe_allow_html=True)
