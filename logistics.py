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
import base64

today = date.today()
basic_directory = dict()
product_directory = dict()
logistics_directory = dict()
warehouses_directory = dict()
buckets = ['karqbasics', 'karqproducts', 'karqlogistics', 'karqwarehouses']


# 定义运输渠道 加入常规运输时间 飞机20，船60，快递飞机7
# 仓库库存
# 产品+ SKU码 ASIN码 产品编号

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


def reflex_row_col(df):
    data = df.values
    index = list(df.keys())
    data = list(map(list, zip(*data)))
    data = pd.DataFrame(data, index=index)
    return data


def logistics():
    global basic_directory, product_directory, logistics_directory
    st.success('登陆身份:' + st.session_state.member)
    st.subheader('物流管理')
    basic_directory = protempload(buckets[0])
    product_directory = protempload(buckets[1])
    logistics_directory = protempload(buckets[2])

    A = B = C = D = 0
    for a in (logistics_directory['未发订单']):
        if len(a) > 1:
            A += 1
    for b in (logistics_directory['运输中订单']):
        if len(b) > 1:
            B += 1
    for c in (logistics_directory['到达订单']):
        if len(c) > 1:
            C += 1
    for d in (logistics_directory['问题订单']):
        if len(d) > 1:
            D += 1
    make_trans_order('karqbasics','karqproducts')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="未发快递", value=A)
    col2.metric(label="快递运输中", value=B)
    col3.metric(label="到达订单", value=C)
    col4.metric(label="问题订单", value=D)
    render_set_style_of_single_bar(["未发快递", "快递运输中", "到达订单", "问题订单"], [A, B, C, D])
    logistics_logging('物流记录.csv', False, False, True, False)

    function_pages = [
        "未发订单",
        "运输中订单",
        '到达订单',
        '问题订单'
    ]
    col1, col2 = st.columns((1, 3))
    with col1:
        func = st.expander('订单查询', expanded=True)
        pool = func.radio('', function_pages)
    if pool == '未发订单':
        unpack()
    if pool == '运输中订单':
        moving_pack()
    if pool == '到达订单':
        arrive_pack()
    if pool == '问题订单':
        issue_pack()

    return basic_directory, product_directory


def make_trans_order(karqbasics,karqproducts):
    with st.expander('发起运输订单', expanded=True):
        if st.checkbox('设置新订单'):
            platform = st.selectbox('平台', nonread_file(karqbasics, '平台/平台.csv', '平台.csv', '平台', True))
            account = st.selectbox('帐号', [str(i) + '-' + str(k) for i, k in
                                          zip(nonread_file(karqbasics, '店铺/店铺资料.csv', '店铺资料.csv', '店铺名', True),
                                              nonread_file(karqbasics, '店铺/店铺资料.csv', '店铺资料.csv', '站点', True))])
            try:
                product_type_ls = list()

                for i in list(filter(lambda x: len(x) > 1, product_directory['SKU'].keys())):
                    product_type_ls.append(i)
                product_type = st.selectbox('产品类别', product_type_ls)

                product_ls = list()

                for z in product_type_ls:

                    if len(list(filter(lambda b: len(b) > 1, product_directory['SKU'][z].keys()))) > 0:
                        try:
                            for c in (list(filter(lambda b: len(b) > 1, product_directory['SKU'][z].keys()))):
                                product_ls.append(c)
                        except:
                            pass
            except:
                pass

            product = st.selectbox('产品', (list(product_directory['SKU'][product_type].keys())))
            amount = st.number_input('数量', step=10000)
            try:
                tip_lang = (list(product_directory['SKU'][product_type][product].keys())[0])
                tip_platform = (list(product_directory['SKU'][product_type][product][tip_lang].keys())[0])
                tip_product = '基础资料'
                tip_file = (
                    list(product_directory['SKU'][product_type][product][tip_lang][tip_platform][tip_product].keys())[
                        0])
                volume = nonread_file(karqproducts,
                                      'SKU/' + str(product_type) + '/' + str(product) + '/' + str(tip_lang) + '/' + str(
                                          tip_platform) + '/' + str(tip_product) + '/' + str(tip_file), str(tip_file),
                                      '体积',
                                      False, 0)

                st.write('体积:', amount * volume, '平方米')
                tot_volume = amount * volume
            except:
                pass
            end_warehouse = st.selectbox('目的地仓库', nonread_file(karqbasics, '仓库/仓库资料.csv', '仓库资料.csv', '仓库名', True))
            document_file1 = st.file_uploader('相关文件1', type='pdf')
            document_file2 = st.file_uploader('相关文件2', type='pdf')
            if st.button('确定'):
                lst1 = ['平台', '帐号', '产品类别', '产品', '数量', '体积', '目的地仓库']
                lst2 = [platform, account, product_type, product, amount, tot_volume, end_warehouse]
                df = pd.DataFrame(list(zip(lst1, lst2)),
                                  columns=['资料', '值'])
                name = str(product) + '发往' + str(end_warehouse)
                df.to_csv(name + '.csv')
                upload('karqlogistics', '未发订单' + '/' + name + '/' + name + '.csv', name + '.csv')
                os.remove(name + '.csv')

                if document_file1 is not None:
                    with open(document_file1.name, 'wb') as f:
                        f.write(document_file1.getbuffer())
                    upload('karqlogistics', '未发订单' + '/' + str(today) + name + '/' + document_file1.name,
                           document_file1.name)
                    os.remove(document_file1.name)
                if document_file2 is not None:
                    with open(document_file2.name, 'wb') as f:
                        f.write(document_file2.getbuffer())
                    upload('karqlogistics', '未发订单' + '/' + str(today) + name + '/' + document_file2.name,
                           document_file2.name)
                    os.remove(document_file2.name)
                st.success('成功上传' + name)


def unpack():
    u1, u2 = st.columns((3, 1))
    if len(list(logistics_directory['未发订单'].keys())) > 1:
        for u in list(logistics_directory['未发订单'].keys()):
            if len(u) > 1:
                with u1.expander(u, expanded=True):
                    if st.checkbox('查看' + u + '相关资料'):
                        for files in list(logistics_directory['未发订单'][u].keys()):
                            fname, extension = os.path.splitext(files)
                            if extension == '.csv':
                                path = '未发订单' + '/' + u + '/' + files

                                download(buckets[2], str(path), files)
                                df = pd.read_csv(files)
                                try:
                                    df.drop('Unnamed: 0', axis=1, inplace=True)
                                except:
                                    pass

                                table(df, df.columns, str(files), False)
                                os.remove(files)
                            elif extension == '.pdf':
                                with open(files, "rb") as f:
                                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')

                                # Embedding PDF in HTML
                                pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="500" type="application/pdf">'

                                # Displaying File
                                st.markdown(pdf_display, unsafe_allow_html=True)

                        unpacked = st.form(key='unpacked' + files)
                        mail_code = unpacked.text_input('输入快递单号', key=str(u) + '输入快递单号')

                        try:
                            download(buckets[0], '物流/' + '物流模式数据.csv', '物流模式数据.csv')
                        except:
                            unpacked.error('无法下载物流数据')
                        ds = pd.read_csv('物流模式数据.csv')
                        try:
                            ds.drop('Unnamed: 0', axis=1, inplace=True)
                        except:
                            pass
                        ds = ds[(ds['物流模式']) != ' ']
                        unpacked.table(ds)
                        mail_mode = unpacked.selectbox('运输模式', list(ds['物流模式']))
                        try:
                            cost = nonread_file(buckets[0], '物流/' + '物流模式数据.csv', '物流模式数据.csv', '成本每平方米(人民币)', False,
                                                list(ds['物流模式']).index(mail_mode))
                            travel_time = nonread_file(buckets[0], '物流/' + '物流模式数据.csv', '物流模式数据.csv', '最大预计运输时间',
                                                       False,
                                                       list(ds['物流模式']).index(mail_mode))
                            position = int(
                                nonread_file(buckets[2], '未发订单' + '/' + u + '/' + u + '.csv', u + '.csv', '资料',
                                             True).index(
                                    '体积'))
                            unit = nonread_file(buckets[2], '未发订单' + '/' + u + '/' + u + '.csv', u + '.csv', '值', False,
                                                position)
                            tot_cost = cost * unit
                            st.write('预计总运输成本:', tot_cost, '元')
                        except:
                            pass

                        start_warehouse = unpacked.selectbox('发出地仓库',
                                                             nonread_file(buckets[0], '仓库/仓库资料.csv', '仓库资料.csv', '仓库名',
                                                                          True),
                                                             key=str(u) + '发出地仓库')
                        try:
                            os.remove('物流模式数据.csv')
                        except:
                            pass
                        if unpacked.form_submit_button('确认快递已正常发出'):

                            for pssfile in (list(logistics_directory['未发订单'][u].keys())):
                                fname, extension = os.path.splitext(pssfile)
                                path = str(u) + '/' + str(pssfile)
                                download(buckets[2], '未发订单/' + path, pssfile)
                                if extension == '.csv':
                                    df = pd.read_csv(pssfile)
                                    try:
                                        df.drop('Unnamed: 0', axis=1, inplace=True)
                                    except:
                                        pass
                                    df.loc[len(df)] = ['发出地仓库', start_warehouse]
                                    df.loc[len(df)] = ['快递号', str(mail_code)]
                                    df.loc[len(df)] = ['运输模式', mail_mode]
                                    df.loc[len(df)] = ['预计运输总成本', tot_cost]
                                    df.loc[len(df)] = ['发出日期', str(today)]
                                    df.loc[len(df)] = ['最大预计运输时间', travel_time]
                                    df.loc[len(df)] = ['预计到达日期', (
                                            datetime.datetime.now() + datetime.timedelta(days=travel_time)).strftime(
                                        '%Y-%m-%d')]
                                    log_ls = ['产品类别', '产品', '数量', '体积', '发出地仓库', '发出日期', '目的地仓库', '运输模式', '预计运输总成本',
                                              '快递号', '帐号', '最大预计运输时间', '预计到达日期']
                                    log_content = []
                                    for i in log_ls:
                                        log_content.append(list(df[df['资料'] == i]['值'])[0])
                                    log_dict = dict(zip(log_ls, log_content))
                                    log_dict['发起用户'] = str(st.session_state.member)
                                    df.to_csv(str(pssfile))

                                    upload(buckets[2], '运输中订单' + '/' + str(today) +
                                           '-(' + str(mail_code) + ')-' + str(u) + '/' + str(pssfile), pssfile)

                                    delete(buckets[2], '未发订单' + '/' + path)
                                    logistics_logging('运输中物流记录.csv', False, True, False, False,
                                                      content=[log_dict['产品类别'], log_dict['产品'], log_dict['数量'],
                                                               log_dict['体积'], log_dict['发出地仓库'], log_dict['发出日期'],
                                                               log_dict['目的地仓库'], log_dict['运输模式']
                                                          , log_dict['最大预计运输时间'], log_dict['预计到达日期'],
                                                               log_dict['预计运输总成本'],
                                                               log_dict['快递号'], log_dict['帐号'], log_dict['发起用户']])

                                else:
                                    upload(buckets[2], '运输中订单' + '/' + path, pssfile)
                                    delete(buckets[2], '未发订单' + '/' + path)
                                os.remove(pssfile)
                            st.success(u + '运输中')

                    if u2.checkbox('删除订单',key=str(u)):
                        for files in list(logistics_directory['未发订单'][u].keys()):
                            delete(buckets[2], '未发订单' + '/' + str(u) + '/' + files)
                            protempload(buckets[2])


def moving_pack():
    logistics_logging('运输中物流记录.csv', True, False, False, True, height=400)
    u1, u2 = st.columns((3, 1))
    if len(list(logistics_directory['运输中订单'].keys())) > 1:
        for u in list(logistics_directory['运输中订单'].keys()):
            if len(u) > 1:
                with u1.expander(u, expanded=True):
                    if st.checkbox('查看' + u + '相关资料'):
                        for files in list(logistics_directory['运输中订单'][u].keys()):
                            path = '运输中订单' + '/' + u + '/' + files
                            openfile(buckets[2], path, files, False)
                            fname, extension = os.path.splitext(files)
                            st.write(files)
                            try:
                                os.remove(files)
                            except:
                                pass
                            if extension == '.csv':
                                download(buckets[2], path, files)
                                csvfile = pd.read_csv(files)
                                try:
                                    csvfile.drop('Unnamed: 0', axis=1, inplace=True)
                                except:
                                    pass

                                log_ls = ['产品类别', '产品', '数量', '体积', '发出地仓库', '发出日期', '目的地仓库', '运输模式', '预计运输总成本',
                                          '快递号', '帐号', '最大预计运输时间']
                                log_content = []
                                for i in log_ls:
                                    log_content.append(list(csvfile[csvfile['资料'] == i]['值'])[0])
                                log_dict = dict(zip(log_ls, log_content))
                                log_dict['签收时间'] = str(today)
                                log_dict['发起用户'] = str(st.session_state.member)
                                os.remove(files)

                        issue = st.text_input('问题描述', key=str(u) + '问题描述')
                        moving_packed = st.form(key=str(u) + 'moving_packed')
                        if moving_packed.form_submit_button('确认快递已正常发出'):

                            for pssfile in (list(logistics_directory['运输中订单'][u].keys())):
                                fname, extension = os.path.splitext(pssfile)
                                path = str(u) + '/' + str(pssfile)
                                download(buckets[2], '运输中订单' + '/' + path, pssfile)
                                if extension == '.csv':
                                    df = pd.read_csv(pssfile)
                                    try:
                                        df.drop('Unnamed: 0', axis=1, inplace=True)
                                    except:
                                        pass
                                    df.loc[len(df)] = ['签收日期', str(today)]
                                    df.to_csv(str(pssfile))
                                    upload(buckets[2], '到达订单' + '/' + path, pssfile)
                                    delete(buckets[2], '运输中订单' + '/' + path)
                                else:
                                    upload(buckets[2], '到达订单' + '/' + path, pssfile)
                                    delete(buckets[2], '运输中订单' + '/' + path)
                                os.remove(pssfile)
                            logistics_logging('物流记录.csv', False, True, False, False,
                                              content=[log_dict['产品类别'], log_dict['产品'], log_dict['数量'],
                                                       log_dict['体积'], log_dict['发出地仓库'], log_dict['发出日期'],
                                                       log_dict['目的地仓库'], log_dict['签收时间'], log_dict['运输模式']
                                                  , log_dict['最大预计运输时间'], log_dict['预计运输总成本'],
                                                       log_dict['快递号'], log_dict['帐号'], log_dict['发起用户']])
                            logistics_logging('运输中物流记录.csv', False, False, True, False, dele_val=log_dict['快递号'])
                            stocks_assigner(str(log_dict['发出地仓库']), str(log_dict['目的地仓库']), str(log_dict['产品']),
                                            float(log_dict['数量']))
                            st.success(u + '已签收')

                        if moving_packed.form_submit_button('确认标记为问题订单'):

                            for pssfile in (list(logistics_directory['运输中订单'][u].keys())):
                                fname, extension = os.path.splitext(pssfile)
                                path = str(u) + '/' + str(pssfile)
                                download(buckets[2], '运输中订单' + '/' + path, pssfile)
                                if extension == '.csv':
                                    df = pd.read_csv(pssfile)
                                    try:
                                        df.drop('Unnamed: 0', axis=1, inplace=True)
                                    except:
                                        pass
                                    df.loc[len(df)] = ['问题标签日期', str(today)]
                                    df.loc[len(df)] = ['问题描述', str(issue)]
                                    df.to_csv(str(pssfile))
                                    upload(buckets[2], '问题订单' + '/' + path, pssfile)
                                    delete(buckets[2], '运输中订单' + '/' + path)




                                else:
                                    upload(buckets[2], '问题订单' + '/' + path, pssfile)
                                    delete(buckets[2], '运输中订单' + '/' + path)
                                os.remove(pssfile)

                        st.success(u + '已标记问题订单')


def arrive_pack():
    logistics_logging('物流记录.csv', True, False, False, False, height=600)
    u1, u2 = st.columns((3, 1))
    if len(list(logistics_directory['到达订单'].keys())) > 1:
        for u in list(logistics_directory['到达订单'].keys()):
            if len(u) > 1:
                with u1.expander(u, expanded=True):
                    if st.checkbox('查看' + u + '相关资料'):
                        for files in list(logistics_directory['到达订单'][u].keys()):
                            path = '到达订单' + '/' + u + '/' + files
                            openfile(buckets[2], path, files, False)


def issue_pack():
    u1, u2 = st.columns((3, 1))
    if len(list(logistics_directory['问题订单'].keys())) > 1:
        for u in list(logistics_directory['问题订单'].keys()):
            if len(u) > 1:
                with u1.expander(u, expanded=True):
                    if st.checkbox('查看' + u + '相关资料'):
                        for files in list(logistics_directory['问题订单'][u].keys()):
                            path = '问题订单' + '/' + u + '/' + files
                            openfile(buckets[2], path, files, False)


def logistics_logging(csv, show, add, delet, check_delay, content=None, dele_val=None, height=None):
    path = '物流记录' + '/' + csv
    download(buckets[2], str(path), csv)
    df = pd.read_csv(csv)
    try:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    if show:
        table(df, df.columns, csv, False, height=height)
    if add:
        add = pd.Series(content, index=df.columns)
        df = df.append(add, ignore_index=True)
        df.to_csv('updatedcsv.csv')
        delete(buckets[2], path)
        upload(buckets[2], path, 'updatedcsv.csv')
        os.remove('updatedcsv.csv')
        protempload(buckets[2])
    if delet:
        df = df[(df['快递单号'] != str(dele_val))]
        df.to_csv('updatedcsv.csv')
        delete(buckets[2], path)
        upload(buckets[2], path, 'updatedcsv.csv')
        os.remove('updatedcsv.csv')
        protempload(buckets[2])
    if check_delay:
        delay_df = df[(df['预计到达日期'] <= str(today))]
        st.subheader('超时订单:')
        table(delay_df, delay_df.columns, '超时订单.csv', False, height=height/2)
        #st.table(delay_df)
    os.remove(csv)


def stocks_assigner(start, end, sku, quantity):
    download(buckets[3], '仓库出入库统计/仓库出入库统计.csv', '仓库出入库统计.csv')
    assigner_df = pd.read_csv('仓库出入库统计.csv')
    try:
        assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    try:
        os.remove('仓库出入库统计.csv')
    except:
        pass
    warehouses_ls = list(assigner_df['仓库名'])
    start_pos = warehouses_ls.index(start)
    end_pos = warehouses_ls.index(end)
    if sku not in assigner_df.columns:
        assigner_df[sku] = [0 * u for u in range(len(assigner_df))]
    assigner_df.at[start_pos, sku] = assigner_df.at[start_pos, sku] - quantity
    assigner_df.at[end_pos, sku] = assigner_df.at[end_pos, sku] + quantity
    try:
        assigner_df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    assigner_df.to_csv('updatedcsv.csv')
    upload(buckets[3], '仓库出入库统计/仓库出入库统计.csv', 'updatedcsv.csv')
    os.remove('updatedcsv.csv')
    download(buckets[3], '仓库出入库统计/仓库出入库统计.csv', '仓库出入库统计.csv')
    os.remove('仓库出入库统计.csv')
