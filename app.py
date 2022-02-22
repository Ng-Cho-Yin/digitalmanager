# https://karqlife.herokuapp.com/



import streamlit as st
from productpage import productpage
from mainpage import mainpage
from huma import huma
from quiz import quiz
from shop import shop
from logistics import logistics
from client import client
from accounts import accounts
from basics import basics
from warehouse import warehouse
from finance import finance
from backend import download
from backend import upload
from backend import iterator
from backend import delete
import pandas as pd
import os
from backend import table
from datetime import date

st.set_page_config(layout='wide', page_title='电商智能管理平台')

hide_menu_style = """
                    <style>
                    #MainMenu {visibility:hidden;}
                    footer {visibility:hidden;}
                    </style>
                """
st.markdown(hide_menu_style, unsafe_allow_html=True)
if 'member' not in st.session_state:
    st.session_state.member = ''
function_pages = {
    "主页":mainpage,
    "人力资源":huma,
    "财务管理": finance,
    "产品资料": productpage,
    "店铺管理": shop,
    '店铺匹配': accounts,
    '物流管理': logistics,
    '仓库管理': warehouse,
    '客户维护': client,
    '基础数据': basics
}

func_ls = []
for ses in function_pages.values():
    func_ls.append(str(ses))
for funcs in func_ls:
    if funcs not in st.session_state:
        st.session_state[str(funcs)] = False

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


def nonread_file(bucket, path, file, col, lsit, pos=None):
    download(bucket, path, file)
    read = pd.read_csv(file)
    os.remove(file)
    if lsit:
        return list(read[str(col)])
    else:
        return float(read[col].iloc[pos])


def login_page():
    today = date.today()
    # st.subheader(today)
    col1, col2 = st.columns((3, 3))
    col2.image('background.jpg')
    col1.title("""电商智能管理平台 — KARQLIFE""")

    global basic_directory

    basic_directory = protempload(buckets[0])

    account = [str(i) for i in nonread_file(buckets[0], '用户/用户.csv', '用户.csv', '帐号', True)]
    account = list(filter(lambda x: len(x) > 1, account))
    pss = [str(i) for i in nonread_file(buckets[0], '用户/用户.csv', '用户.csv', '密码', True)]
    pss = list(filter(lambda x: len(x) > 1, pss))
    ls = dict(zip(account, pss))

    st.session_state.member = acc = col1.text_input('帐号',help = '还没有自己的工作帐号？请通知管理员开启你自己的工作帐号吧')
    pas = col1.text_input('密码',type='password',help = '忘记密码请联系管理员')
    enter = col1.button('登入')

    if enter:
        if acc not in ls.keys():
            col1.write('请输入正确的帐号和密码')

        else:
            if str(ls.get(acc)) == str(pas):
                st.session_state.login = False

            if str(ls.get(acc)) != str(pas):
                col1.write('请输入正确的帐号和密码')

    # hashed_passwords = stauth.hasher(pss).generate()
    #
    # authenticator = stauth.authenticate(account, account, hashed_passwords,
    #                                     'some_cookie_name', 'some_signature_key', cookie_expiry_days=1)
    #
    # name, authentication_status = authenticator.login('登陆', 'main')


# f

def mainpage():
    st.sidebar.image('logo.png')
    page = st.sidebar.radio('选择页面', tuple(function_pages.keys()))

    if not st.session_state.login:
        function_pages[page]()


# l
if 'login' not in st.session_state:
    st.session_state.login = True

if st.session_state.login:
    login_page()

if not st.session_state.login:
    mainpage()
