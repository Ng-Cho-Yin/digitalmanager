import streamlit as st
from backend import download
from backend import upload
from backend import delete
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
buckets = ['karqproducts', 'karqbasics','karqshops']


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
    st.info('登陆身份:' + st.session_state.member)
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
    col1, col2 = st.columns((1, 3))
    with col1:
        func = st.expander('功能', expanded=True)
        function = func.radio('', function_pages)
    with col2:
        render_set_style_of_single_bar(["产品审核中", "产品总量", "SKU总量", "驳回项目"], [unver, ver, sku, failed])
    if function == '产品(SKU)搜索':
        protempload(buckets[0])
        product_search(version=2)
    if function == '产品(SKU)总览':
        protempload(buckets[0])
        product_gallery()
    if function == '产品审核':
        protempload(buckets[0])
        productverifypage()
    if function == '产品总览':
        protempload(buckets[0])
        verified_product()
    if function == 'SKU总览':
        protempload(buckets[0])
        verified_sku()
    if function == '新增产品系列':
        protempload(buckets[0])
        product_uploadinfo('未审核', product_directory, False, False)
    if function == '添加SKU资料':
        protempload(buckets[0])
        product_uploadinfo('SKU', product_directory, False, False)
    if function == '产品范本修改':
        protempload(buckets[0])
        with st.expander("修改产品资料范本"):
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
                                print(img.width, img.height)
                                img = img.resize((88, 88))
                                print(img.width, img.height)
                                st.image(img)
                                img_exist = True

                        if not img_exist:
                            img = Image.open('image_not_found.jpg')
                            print(img.width, img.height)
                            img = img.resize((88, 88))
                            print(img.width, img.height)
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
                                        table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0],path=path)
                                    if '.jpg' in tar2:
                                        img = Image.open(tar2)
                                        print(img.width, img.height)
                                        img = img.resize((100, 100))
                                        print(img.width, img.height)
                                        st.image(img)

                            if st.checkbox('上传图片(替换已有图片):', key=path):
                                file_p = st.file_uploader('上传图片', type=['jpg'])
                                if st.checkbox('上传'):
                                    path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + str(
                                        lang) + '/' + str(
                                        platform) + '/' + '图片' + '/'
                                    upload(buckets[0], str(path) + str(file_p.name), str(file_p.name))
                                    os.remove(str(file_p.name))
                                    st.success('图片上传成功')


def product_gallery():
    global product_directory
    st.subheader('产品总览:')
    product_ls = []
    for cc in (product_directory['已审核']):
        for dd in (product_directory['已审核'][cc]):
            product_ls.append([cc, dd])

    for product in product_ls:
        typ = product[0]
        item = product[1]
        col1, col2 = st.columns((1, 8))
        lan = list(product_directory['已审核'][typ][item].keys())
        lang = lan[0]
        plats = list(product_directory['已审核'][typ][item][lang].keys())
        platform = plats[0]
        with col1:
            img_exist = False
            for tar in filter(lambda x: len(x) > 1,
                              list(product_directory['已审核'][typ][item][lang][platform].keys())):

                for tar2 in filter(lambda x: len(x) > 1,
                                   list(product_directory['已审核'][typ][item][lang][platform][tar].keys())):
                    path = '已审核/' + str(typ) + '/' + str(item) + '/' + str(
                        lang) + '/' + str(platform) + '/' + tar + '/' + tar2

                    if '.jpg' in tar2:
                        download(
                            buckets[0],
                            str(path),
                            tar2)
                        img = Image.open(tar2)
                        print(img.width, img.height)
                        img = img.resize((88, 88))
                        print(img.width, img.height)
                        st.image(img)
                        img_exist = True

                if not img_exist:
                    img = Image.open('image_not_found.jpg')
                    print(img.width, img.height)
                    img = img.resize((88, 88))
                    print(img.width, img.height)
                    st.image(img)
        with col2:
            with st.expander(str(item), expanded=True):
                if st.checkbox('查看' + str(item) + '相关文件'):
                    lan = list(product_directory['已审核'][typ][item].keys())
                    lang = lan[0]
                    plats = list(product_directory['已审核'][typ][item][lang].keys())
                    platform = plats[0]

                    for tar in filter(lambda x: len(x) > 1,
                                      list(product_directory['已审核'][typ][item][lang][platform].keys())):

                        for tar2 in filter(lambda x: len(x) > 1,
                                           list(product_directory['已审核'][typ][item][lang][platform][tar].keys())):
                            path = '已审核/' + str(typ) + '/' + str(item) + '/' + str(
                                lang) + '/' + str(platform) + '/' + tar + '/' + tar2
                            if '.csv' in tar2:
                                download(buckets[0], str(path), tar2)
                                df = pd.read_csv(tar2)
                                try:
                                    df.drop('Unnamed: 0', axis=1, inplace=True)
                                except:
                                    pass
                                table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0],path=path)
                            if '.jpg' in tar2:
                                img = Image.open(tar2)
                                print(img.width, img.height)
                                img = img.resize((100, 100))
                                print(img.width, img.height)
                                st.image(img)
                    if st.checkbox('上传图片(替换已有图片):', key=path):
                        file_p = st.file_uploader('上传图片' + '/' + 'Upload Picture', type=['jpg'])
                        if st.checkbox('上传'):
                            path = str('SKU') + '/' + str(typ) + '/' + str(item) + '/' + str(
                                lang) + '/' + str(
                                platform) + '/' + '图片' + '/'
                            upload(buckets[0], str(path) + str(file_p.name), str(file_p.name))
                            os.remove(str(file_p.name))
                            st.success('图片上传成功')


def productverifypage():
    global product_directory
    st.subheader('需要审核项目:')
    verify_ls = []
    for b in filter(lambda x: len(x) > 1, (product_directory['未审核'])):
        for c in filter(lambda x: len(x) > 1, (product_directory['未审核'][b])):
            verify_ls.append([b, c])

    typ_ls = set([i[0] for i in verify_ls])
    item = st.selectbox('', filter(lambda x: len(x) > 1, typ_ls), key='审核项目')

    product_ls = product_directory['未审核'][item]

    for product in product_ls:
        if product is not None:

            with st.expander('审核' + str(product), expanded=True):
                if st.checkbox('审核' + str(product)):
                    st.write(product)
                    try:

                        lan = list(product_directory['未审核'][item][product].keys())
                        lang = st.selectbox('语言', lan, key=product)
                        plats = list(product_directory['未审核'][item][product][lang].keys())
                        platform = st.selectbox('平台', plats, key=product)

                        if st.checkbox('打开', key=str(lang + platform + product)):
                            protempload(buckets[0])
                            col1, col2, col3 = st.columns((3, 3, 3))
                            for files in (list(product_directory['未审核'][item][product][lang][platform].keys())):
                                for file in filter(lambda x: len(x) > 1,
                                                   (list(product_directory['未审核'][item][product][lang][platform][
                                                             files].keys()))):

                                    col1.write(file, key=product)
                                    if col2.checkbox('打开', key=file + product):
                                        path = '未审核' + '/' + item + '/' + product + '/' + lang + '/' + platform + '/' + files + '/' + file
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
                                    for group in (list(product_directory['未审核'][item][product][lang][platform].keys())):
                                        for pssfile in (
                                                list(product_directory['未审核'][item][product][lang][platform][
                                                         group].keys())):
                                            path = item + '/' + product + '/' + lang + '/' + platform + '/' + \
                                                   group + '/' + pssfile
                                            download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                            upload(buckets[0], '已审核' + '/' + str(path), pssfile)
                                            delete(buckets[0], '未审核' + '/' + str(path))
                                            st.success('成功上传' + pssfile)
                                            protempload(buckets[0])

                            if deci == '不批准':

                                if st.checkbox('确认', key='不批准确认' + product):
                                    for group in (list(product_directory['未审核'][item][product][lang][platform].keys())):
                                        for pssfile in (
                                                list(product_directory['未审核'][item][product][lang][platform][
                                                         group].keys())):
                                            path = item + '/' + product + '/' + lang + '/' + platform + '/' + \
                                                   group + '/' + pssfile
                                            download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                            upload(buckets[0], '驳回产品' + '/' + str(path), pssfile)
                                            delete(buckets[0], '未审核' + '/' + str(path))
                                            st.success('成功上传' + pssfile)
                                            protempload(buckets[0])
                    except:
                        print('error:productverifypage()')
    st.subheader('驳回项目:')
    unsupported_ls = []
    for b in filter(lambda x: len(x) > 1, (product_directory['驳回产品'])):
        for c in filter(lambda x: len(x) > 1, (product_directory['驳回产品'][b])):
            unsupported_ls.append([b, c])
    typ_ls = set([i[0] for i in unsupported_ls])
    if len(list(filter(lambda x: len(x) > 1, typ_ls))) == 0:
        st.write('无')
    else:
        item = st.selectbox('', filter(lambda x: len(x) > 1, typ_ls), key='驳回项目')
        product_ls = product_directory['驳回产品'][item]
        for product in product_ls:
            if product is not None:
                with st.expander(str(product), expanded=True):
                    if st.checkbox('审核' + str(product) + '相关文件'):
                        st.write(product)
                        try:
                            lan = list(product_directory['驳回产品'][item][product].keys())
                            lang = lan[0]
                            plats = list(product_directory['驳回产品'][item][product][lang].keys())
                            platform = plats[0]
                            if st.checkbox('打开', key=str(lang + platform + product)):
                                protempload(buckets[0])
                                col1, col2, col3 = st.columns((3, 3, 3))
                                for files in (list(product_directory['驳回产品'][item][product][lang][platform].keys())):
                                    for file in filter(lambda x: len(x) > 1,
                                                       (list(product_directory['驳回产品'][item][product][lang][platform][
                                                                 files].keys()))):

                                        col1.write(file, key=product)
                                        if col2.checkbox('打开', key=file + product):
                                            path = '驳回产品' + '/' + item + '/' + product + '/' + lang + '/' + platform + '/' + files + '/' + file
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
                                        for group in (list(product_directory['未审核'][item][product][lang][platform].keys())):
                                            for pssfile in (
                                                    list(
                                                        product_directory['未审核'][item][product][lang][platform][
                                                            group].keys())):
                                                path = item + '/' + product + '/' + lang + '/' + platform + '/' + \
                                                       group + '/' + pssfile
                                                download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                                upload(buckets[0], '已审核' + '/' + str(path), pssfile)
                                                delete(buckets[0], '未审核' + '/' + str(path))
                                                st.success('成功上传' + pssfile)
                                                protempload(buckets[0])

                                if deci == '不批准':

                                    if st.checkbox('确认', key='不批准确认' + product):
                                        for group in (list(product_directory['未审核'][item][product][lang][platform].keys())):
                                            for pssfile in (
                                                    list(
                                                        product_directory['未审核'][item][product][lang][platform][
                                                            group].keys())):
                                                path = item + '/' + product + '/' + lang + '/' + platform + '/' + \
                                                       group + '/' + pssfile
                                                download(buckets[0], '未审核' + '/' + str(path), pssfile)
                                                upload(buckets[0], '驳回产品' + '/' + str(path), pssfile)
                                                delete(buckets[0], '未审核' + '/' + str(path))
                                                st.success('成功上传' + pssfile)
                                                protempload(buckets[0])

                        except:
                            print('error:productverifypage()')

    return product_directory


def verified_product():
    global product_directory
    st.subheader('打开产品资料:')

    product_list = list(filter(lambda x: len(x) > 1, list(product_directory['已审核'].keys())))
    typ = st.selectbox('产品类别', ['全部'] + product_list)
    if typ == '全部':
        dst_list = product_list
    else:
        dst_list = [typ]
    for typ in dst_list:
        product_ls = filter(lambda x: len(x) > 1, list(product_directory['已审核'][typ].keys()))
        for item in product_ls:
            col1, col2 = st.columns((1, 10))

            lan = list(product_directory['已审核'][typ][item].keys())
            try:
                lan.remove('SKU')
            except:
                pass

            lang = lan[0]

            plats = list(product_directory['已审核'][typ][item][lang].keys())
            platform = plats[0]
            with col1:
                img_exist = False
                for tar in filter(lambda x: len(x) > 1,
                                  list(product_directory['已审核'][typ][item][lang][platform].keys())):
                    for tar2 in filter(lambda x: len(x) > 1,
                                       list(product_directory['已审核'][typ][item][lang][platform][tar].keys())):
                        path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + str(lang) + '/' + str(
                            platform) + '/' + tar + '/' + tar2

                        if '.jpg' in tar2:
                            download(
                                buckets[0],
                                str(path),
                                tar2)
                            img = Image.open(tar2)
                            print(img.width, img.height)
                            img = img.resize((50, 50))
                            print(img.width, img.height)
                            st.image(img)
                            img_exist = True

                if not img_exist:
                    img = Image.open('image_not_found.jpg')
                    print(img.width, img.height)
                    img = img.resize((50, 50))
                    print(img.width, img.height)
                    st.image(img)

            with col2:
                with st.expander(str(item), expanded=True):
                    if st.checkbox('查看' + str(item) + '相关文件'):


                        for tar in filter(lambda x: len(x) > 1,
                                          list(product_directory['已审核'][typ][item][lang][platform].keys())):

                            for tar2 in filter(lambda x: len(x) > 1,
                                               list(product_directory['已审核'][typ][item][lang][platform][tar].keys())):
                                path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + str(lang) + '/' + str(
                                    platform) + '/' + tar + '/' + tar2

                                if '.csv' in tar2:
                                    download(buckets[0], str(path), tar2)
                                    df = pd.read_csv(tar2)
                                    try:
                                        df.drop('Unnamed: 0', axis=1, inplace=True)
                                    except:
                                        pass
                                    table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0], path=path,
                                          height=150)

                                if '.jpg' in tar2:
                                    img = Image.open(tar2)
                                    print(img.width, img.height)
                                    img = img.resize((200, 200))
                                    print(img.width, img.height)
                                    st.image(img)

                        if st.checkbox('上传图片(替换已有图片):', key=path):
                            file_p = st.file_uploader('上传图片' + '/' + 'Upload Picture', type=['jpg'])
                            if st.checkbox('上传'):
                                path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + str(
                                    lang) + '/' + str(
                                    platform) + '/' + '图片' + '/'
                                upload(buckets[0], str(path) + str(file_p.name), str(file_p.name))
                                os.remove(str(file_p.name))
                                st.success('图片上传成功')

                        if st.checkbox('创建SKU系列', key=str(item) + str(tar) + str(tar2)):
                            asin_name = st.text_input('ASIN 名(必填)')
                            sku_name = st.text_input('SKU 名(必填)')
                            worker_ls = st.multiselect('店铺(非必填)', [str(i) + '-' + str(k) for i, k in
                                                           zip(nonread_file(buckets[1], '店铺/店铺资料.csv', '店铺资料.csv',
                                                                            '店铺名', True),
                                                            nonread_file(buckets[1], '店铺/店铺资料.csv', '店铺资料.csv', '站点',
                                                                            True))])



                            if st.checkbox('确认创建SKU'):
                                for tar in filter(lambda x: len(x) > 1,
                                                  list(product_directory['已审核'][typ][item][lang][platform].keys())):

                                    for tar2 in filter(lambda x: len(x) > 1,
                                                       list(product_directory['已审核'][typ][item][lang][platform][
                                                                tar].keys())):
                                        downloadpath = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + str(
                                            lang) + '/' + str(platform) + '/' + tar + '/' + tar2
                                        uploadpath1 = 'SKU/' + str(typ) + '/' + str(asin_name) + '-' + str(
                                            sku_name) + '/' + str(
                                            lang) + '/' + str(platform) + '/' + tar + '/' + tar2
                                        uploadpath2 = str('已审核') + '/' + str(typ) + '/' + str(
                                            item) + '/' + 'SKU/' + str(asin_name) + '/' + tar + '/' + tar2
                                        download(buckets[0], str(downloadpath), tar2)
                                        upload(buckets[0], str(uploadpath1), tar2)
                                        upload(buckets[0], str(uploadpath2), tar2)
                                        protempload(buckets[0])
                                if len(worker_ls) != 0:
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
                                    clients = [str(asin_name) + '-' + str(sku_name)]
                                    for worker in worker_ls:
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
                                                    work_pos = worker_ls.index(str(worker))
                                                    assigner_df.at[work_pos, client] = 1
                                                    try:
                                                        assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
                                                    except:
                                                        pass
                                                    assigner_df.to_csv('updatedcsv.csv')
                                                    delete(buckets[2], '产品配对/产品配对.csv')
                                                    upload(buckets[2], '产品配对/产品配对.csv', 'updatedcsv.csv')
                                                    download(buckets[2], '产品配对/产品配对.csv', '产品配对.csv')
                                                    assigner_df = pd.read_csv('产品配对.csv')
                                                    os.remove('产品配对.csv')
                                        st.success('完成')

                                st.success('成功创建SKU')
                if st.checkbox('打开关联sku', key=item):
                    for tar in filter(lambda x: len(x) > 1,
                                      list(product_directory['已审核'][typ][item]['SKU'].keys())):
                        with st.expander(tar, expanded=True):
                            if st.checkbox('打开', key=item + tar):
                                for tar2 in filter(lambda x: len(x) > 1,
                                                   list(product_directory['已审核'][typ][item]['SKU'][tar].keys())):
                                    for tar3 in filter(lambda x: len(x) > 1,
                                                       list(product_directory['已审核'][typ][item]['SKU'][tar][
                                                                tar2].keys())):
                                        path = str('已审核') + '/' + str(typ) + '/' + str(item) + '/' + 'SKU' \
                                               + '/' + tar + '/' + tar2 + '/' + tar3
                                        if '.csv' in tar3:
                                            download(buckets[0], str(path), tar3)
                                            df = pd.read_csv(tar3)
                                            try:
                                                df.drop('Unnamed: 0', axis=1, inplace=True)
                                            except:
                                                pass
                                            table(df, df.columns, str(item) + str(tar) + str(tar2), True,
                                                  bucket=buckets[0],
                                                  path=path, height=150)

                                        if '.jpg' in tar3:
                                            img = Image.open(tar3)
                                            print(img.width, img.height)
                                            img = img.resize((100, 100))
                                            print(img.width, img.height)
                                            st.image(img)


def verified_sku():
    global product_directory
    st.subheader('打开SKU:')
    typ = st.selectbox('产品类别', list(filter(lambda x: len(x) > 1, list(product_directory['SKU'].keys()))))
    sku_ls = filter(lambda x: len(x) > 1, list(product_directory['SKU'][typ].keys()))
    for item in sku_ls:

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
                                           list(product_directory['SKU'][typ][item][lang][platform][tar].keys())):
                            col1.write(tar2)

                            if col2.checkbox('打开', key=str(item) + str(tar) + '-SKU'):
                                path = 'SKU/' + str(typ) + '/' + str(item) + '/' + str(
                                    lang) + '/' + str(platform) + '/' + tar + '/' + tar2

                                download(buckets[0], str(path), tar2)
                                try:
                                    df = pd.read_csv(tar2)
                                    try:
                                        df.drop('Unnamed: 0', axis=1, inplace=True)
                                    except:
                                        pass

                                    table(df, df.columns, str(item) + str(tar), True, bucket=buckets[0],path=path)



                                except:
                                    download(
                                        buckets[0],
                                        str(path),
                                        tar2)
                                    st.image(tar2)
                except:
                    print('error:verified_sku()')


def formatter():
    download(buckets[0], '范本/产品参数范本.csv', '产品参数范本.csv')
    with open('产品参数范本.csv', "rb") as file:
        btn = st.download_button(
            label="下载产品参数范本(csv版)",
            data=file,
            file_name='产品参数范本.csv',
            mime="image/png"
        )
    newformat = st.file_uploader('上传新范本', type=['xlsx'])
    if newformat is not None:
        df = pd.read_excel(newformat, engine='openpyxl', index_col=-1)
        excel_ls = []

        df = df.astype(str)
        st.write("新表格")
        for num in range(0, len(df)):
            st.text_input(df.iloc[num, 0])
            excel_ls.append(df.iloc[num, 0])
        format_csv = pd.DataFrame()
        for col in excel_ls:
            format_csv.loc[0, col] = ''
        format_csv.to_csv('产品参数范本.csv')
        st.write(format_csv)

    if st.button('上传'):
        delete(buckets[0], '范本/产品参数范本.xlsx')
        upload(buckets[0], '范本/产品参数范本.csv', '产品参数范本.csv')
        st.success('上传成功')


def product_uploadinfo(verify, dire, Type, Name):
    if Type == Name == False:
        col1, col2, col3, col4 = st.columns((1, 0.5, 1, 1))
        protypels = list(dire['已审核'].keys())
        typ = col1.selectbox('类别', protypels, key='uploadinfo_type')
        pronamels = list(dire['已审核'][typ].keys())
        name = col1.selectbox('产品', pronamels, key='uploadinfo_name')

        if col3.checkbox('旧类别-新产品'):
            typ = col3.selectbox('类别', protypels, key='已有类别-新产品')
            name = col3.text_input('新产品名', key='已有类别-新产品')

        elif col4.checkbox('新类别-新产品'):
            typ = col4.text_input('新产品类别', key='新类别-新产品')
            name = col4.text_input('新产品名', key='新类别-新产品')

    else:
        typ = Type
        name = Name

    basic = False
    picture = False
    video = False

    if st.checkbox('添加产品基础资料'):
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
    lang = form.selectbox('语言', ['中文', '英文', '法语', '德语', '意大利语', '西班牙语', '日语', '韩语'])
    platform = form.selectbox('平台', ['亚马逊', '京东', '淘宝'], key='uploadinfo_platform')

    file_p = form.file_uploader('上传图片' + '/' + 'Upload Picture', type=['jpg'])
    if file_p is not None:
        with open(file_p.name, 'wb') as p:
            p.write(file_p.getbuffer())
            picture = True

    file_v = form.file_uploader('上传视频' + '/' + 'Upload Video', type=['mp4'])
    if file_v is not None:
        with open(file_v.name, 'wb') as v:
            v.write(file_v.getbuffer())
            video = True

    product_uploadinfo_submit = form.form_submit_button('上传')

    if product_uploadinfo_submit:

        path = verify + '/' + typ + '/' + name + '/' + lang + '/' + platform + '/' \
               + '评论' + '/'
        upload(buckets[0], str(path) + 'review.csv', 'review.csv')

        path = verify + '/' + typ + '/' + name + '/' + lang + '/' + platform + '/' \
               + '提问' + '/'
        upload(buckets[0], str(path) + 'qa.csv', 'qa.csv')
        if basic:
            path = verify + '/' + typ + '/' + name + '/' + lang + '/' + platform + '/' \
                   + '基础资料' + '/'
            upload(buckets[0], str(path) + '基础资料.csv', '基础资料.csv')
            os.remove('基础资料.csv')
            os.remove('产品参数范本.csv')
            form.success('基础资料上传成功')
        if picture:
            path = verify + '/' + typ + '/' + name + '/' + lang + '/' + platform + '/' + '图片' + '/'
            upload(buckets[0], str(path) + str(file_p.name), str(file_p.name))
            os.remove(str(file_p.name))
            form.success('图片上传成功')
        if video:
            path = verify + '/' + typ + '/' + name + '/' + lang + '/' + platform + '/' + '视频' + '/'
            upload(buckets[0], str(path) + str(file_v.name), str(file_v.name))
            os.remove(str(file_v.name))
            form.success('视频上传成功')

    return product_directory





def qa_format(qa):
    response = pd.read_csv(qa)
    for x in range(0, len(response)):
        date = response['日期'][x]
        buyer = response['用户'][x]
        question = response['提问'][x]
        answer = response['回答'][x]
        st.markdown(PRODUCT_QA.format('用户:' + str(buyer), '问题 :' + str(question), '回答 :' + str(answer), date),
                    unsafe_allow_html=True)
