import streamlit as st
import pandas as pd
import numpy as np

def mainpage():
    st.subheader('你好! {}'.format(st.session_state.member))

    st.write('## 打卡！')
    if st.checkbox('确认'):
        st.success('打卡记录成功')



    