import streamlit as st
import pandas as pd
import os
from backend import download
from backend import delete
from backend import upload
from backend import iterator
from backend import table
from PIL import Image

# bucket list
buckets = ['karqhuma']
huma_directory = dict()
def protempload(bucket):
    global huma_directory

    for path in iterator(bucket):
        parent = huma_directory
        for dire in path.split('/'):
            if dire not in parent:
                parent[dire] = dict()
            parent = parent[dire]

    return huma_directory



#create staff -> create individual file ->
function_pages = [
        '员工资料总览',
        '新增员工',
        '员工资料范本',
        '企业黑名单'
    ]


# main
def huma():
    global huma_directory
    st.success('登陆身份:' + st.session_state.member)
    huma_directory = protempload(buckets[0])
    st.subheader('人力资源')
    col1, col2 = st.columns((1, 3))
    with col1:
        func = st.expander('功能', expanded=True)
        function = func.radio('', function_pages)
    if function == '员工资料总览':
        protempload(buckets[0])
        staff_gallery()
    if function == '新增员工':
        protempload(buckets[0])
        create_member()
    if function == '员工资料范本':
        protempload(buckets[0])
        formatter()
    if function == '黑名单':
        protempload(buckets[0])
        blacklist()


#staff gallery
def staff_gallery():
    global product_directory
    col1, col2 = st.columns((1, 8))
    for staff in filter(lambda x: len(x) > 1,list(huma_directory['员工资料数据库'].keys())):
        info = list(filter(lambda x: len(x) > 1,list(huma_directory['员工资料数据库'][staff]['基本资料'])))[0]
        image = list(filter(lambda x: len(x) > 1,list(huma_directory['员工资料数据库'][staff]['头像'])))[0]
        path = '员工资料数据库/'+staff+'/'
        with col1:
            download(buckets[0],str(path)+'头像/'+image,image)
            img = Image.open(image)
            print(img.width, img.height)
            img = img.resize((250, 250))
            print(img.width, img.height)
            st.image(img)

        with col2:
            with st.expander(staff,expanded=True):
                if st.checkbox('打开',key=staff):
                    download(buckets[0], str(path) +'基本资料/'+ info, info)
                    df = pd.read_csv(info)
                    try:
                        df.drop('Unnamed: 0', axis=1, inplace=True)
                    except:
                        pass
                    table(df, df.columns, str(info) + str(info), True)

                    if st.checkbox('加入黑名单'):
                        st.warning('确认加入'+staff+'进入人力资源黑名单?')
                        if st.checkbox('确认',key='确认加入'+staff+'进入人力资源黑名单?'):
                            st.success('加入'+staff+'进入人力资源黑名单程序完成')







# create member profile format
def formatter():
    download(buckets[0], '范本/员工资料范本.csv', '员工资料范本.csv')
    with open('员工资料范本.csv', "rb") as file:
        btn = st.download_button(
            label="下载员工资料范本(csv版)",
            data=file,
            file_name='员工资料范本.csv',
            mime="image/png"
        )
    newformat = st.file_uploader('员工资料范本', type='xlsx')
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
        format_csv.to_csv('员工资料范本.csv')
        st.write(format_csv)

    if st.button('上传', key='huma_formatter'):
        delete(buckets[0], '范本/员工资料范本.xlsx')
        upload(buckets[0], '范本/员工资料范本.csv', '员工资料范本.csv')
        st.success('上传成功')


# log new members in
# create profile for each member

def create_member():
    icon = False
    image = st.file_uploader('头像', 'jpg')

    if image is not None:
        with open(image.name, 'wb') as p:
            p.write(image.getbuffer())
            icon = True
        img = Image.open(image.name)
        print(img.width, img.height)
        img = img.resize((150, 150))
        print(img.width, img.height)
        st.image(img)
        st.write(image.name)

    download(buckets[0], '范本/员工资料范本.csv', '员工资料范本.csv')
    df = pd.read_csv('员工资料范本.csv')
    try:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    except:
        pass
    os.remove('员工资料范本.csv')
    name = st.text_input('员工系统命名', help='必填')
    col1, col2 = st.columns((3, 2))
    for col in df.columns:
        df.loc[0, col] = col1.text_input(col)
    for col in df.columns:
        if len(df.loc[0, col]) == 0:
            df.loc[0, col] = ' '
    df.to_csv('员工资料.csv')

    path_info = '员工资料数据库/' + str(name) + '/基本资料/'
    path_img = '员工资料数据库/' + str(name) + '/头像/'
    if st.button('保存', key='create_member'):
        if icon is not True:
            st.warning('未上传头像')
        else:

            upload(buckets[0], path_info + '员工资料.csv', '员工资料.csv')
            upload(buckets[0], path_img + str(image.name), str(image.name))
            st.success('上传成功')




# create black list
def blacklist():
    pass