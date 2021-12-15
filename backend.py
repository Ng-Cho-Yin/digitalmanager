import oss2
import streamlit as st
import os.path
import pandas as pd
import base64
import numpy as np
import pandas as pd
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, shared
from streamlit_echarts import st_echarts


ali_id = 'LTAI5t7cxxNTsPg12NBYaXZa'
ali_access_key = 'vrEr81DhJJjkcfjo47Oue96KSMsf8L'
auth = oss2.Auth(ali_id, ali_access_key)


def download(bucket, path, local):
    # bucket.get_object_to_file('check.csv', 'test.csv')
    bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', bucket)
    bucket.get_object_to_file(path, local)


def upload(bucket, path, local):
    # bucket.put_object_from_file('files/check.csv', 'check.csv')
    bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', bucket)
    bucket.put_object_from_file(path, local)


def iterator(bucket):
    bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', bucket)
    list = []
    for obj in oss2.ObjectIterator(bucket):
        print(obj.key)
        list.append(obj.key)
    return list


def delete(bucket, path):
    bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', bucket)
    bucket.delete_object(path)


def protempload(bucket):
    directory = dict()
    for path in iterator(bucket):
        parent = directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]
    return directory


def openfile(bucket, path, file, dele):
    fname, extension = os.path.splitext(file)
    st.write('文件名:' + str(file))
    download(bucket, path, file)
    if str(extension) == '.xlsx':
        verify_file = pd.read_excel(file)

        st.write(list(verify_file.columns))
        st.table(verify_file)
        if dele:
            if st.checkbox('删除文件' + str(file)):
                if st.checkbox('确认', key='删除文件' + str(file)):
                    delete(bucket, path)

    elif str(extension) == '.csv':

        df = pd.read_csv(file)

        try:
            df.drop('Unnamed: 0', axis=1, inplace=True)
        except:
            pass

        table(df, list(df.columns), fname, False)

    elif str(extension) == '.pdf':
        # Opening file from file path
        with open(file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # Embedding PDF in HTML
        pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="500" type="application/pdf">'

        # Displaying File
        st.markdown(pdf_display, unsafe_allow_html=True)

    elif str(extension) == '.jpg' or '.jpeg' or 'png':

        st.image(file)
        if dele:
            if st.checkbox('删除文件' + str(file)):
                if st.checkbox('确认', key='删除文件' + str(file)):
                    delete(bucket, path)

    else:
        st.write('无法显示文件:' + file)
    os.remove(file)


def ag_form(index, col_ls):
    df_template = pd.DataFrame('', index=range(index), columns=col_ls)
    response = AgGrid(df_template, editable=True, fit_columns_on_grid_load=True, height=64)
    st.form_submit_button()
    st.write(response['data'])


def table(data, cls, name, edit, bucket=None, path=None, fit=False,height=300):
    global ag
    gb = GridOptionsBuilder.from_dataframe(data)
    # make all columns editable
    gb.configure_columns(cls, editable=True)

    js = JsCode("""
    function(e) {
        let api = e.api;
        let rowIndex = e.rowIndex;
        let col = e.column.colId;
        let rowNode = api.getDisplayedRowAtIndex(rowIndex);
        api.flashCells({
          rowNodes: [rowNode],
          columns: [col],
          flashDelay: 10000000000
        });

    };
    """)

    gb.configure_grid_options(onCellValueChanged=js)
    go = gb.build()
    # st.markdown("""
    # ### JsCode injections
    # Cell editions are highlighted here by attaching to ```onCellValueChanged``` of the grid, using JsCode injection
    # ```python
    # js = JsCode(...)
    # gb.configure_grid_options(onCellValueChanged=js)
    # ag = AgGrid(data, gridOptions=gb.build(),  key='grid1', allow_unsafe_jscode=True, reload_data=False)
    # ```
    # """)
    # st.subheader("Grid Options")
    # # st.write(go)
    try:
        ag = AgGrid(data,
                    height=height,
                    gridOptions=go,
                    key=str(name) + 'grid',
                    allow_unsafe_jscode=True,
                    reload_data=False,
                    theme="streamlit",
                    fit_columns_on_grid_load=fit,
                    enable_enterprise_modules=True,
                    update_mode=shared.GridUpdateMode.MODEL_CHANGED,

                    )

        if edit:
            if st.checkbox('更新文件', key=str(name)):

                st.write("输出文件")
                st.table(ag['data'])
                ag['data'].to_csv('updatedcsv.csv')
                if st.checkbox('确认更新文件', key='用户.csv'):
                    plus = pd.read_csv('updatedcsv.csv')
                    for k in range(3):
                        content = [' ' for i in range(len(plus.columns))]
                        add = pd.Series(content, index=plus.columns)
                        plus = plus.append(add, ignore_index=True)
                    try:
                        plus.drop('Unnamed: 0', axis=1, inplace=True)
                    except:
                        pass
                    plus.to_csv('updatedcsv.csv')
                    upload(bucket, path, 'updatedcsv.csv')
                    protempload(bucket[0])
    except:
        print('error:backend.table')

    return ag['data']






def render_pie_simple(title,subtext,name,data):
    options = {
        "title": {"text": title, "subtext": subtext, "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left",},
        "series": [
            {
                "name": name,
                "type": "pie",
                "radius": "50%",
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }
    st_echarts(
        options=options, height="500px",
    )


def render_set_style_of_single_bar(col,data):
    options = {
        "xAxis": {
            "type": "category",
            "data": col,
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "data": data,
                "type": "bar",
            }
        ],
    }
    st_echarts(
        options=options,
        height="300px",

    )