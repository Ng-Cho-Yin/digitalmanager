import streamlit as st
import pandas as pd
import numpy as np

def data_clean(x):
    if "." and "," in x:
        x = x.replace(".","")
        x = x.replace(",",".")
        return x
    else:
        return x.replace(",",".")

def finance():
    

    class Create_objs:

        def __init__(self, name, datafile=None):
            self.df = pd.read_csv(datafile)
            self.name = name
            if self.name in ['other','total']:
                self.df[self.name] = self.df[self.name].str.replace(",", "").astype(float)
            self.sum = self.df[self.name].sum()

    instanceNames = ['product sales', 'product sales tax', 'shipping credits', 'shipping credits tax',
                     'gift wrap credits', 'giftwrap credits tax', 'promotional rebates',
                     'promotional rebates tax', 'marketplace withheld tax', 'selling fees', 'fba fees',
                     'other transaction fees', 'other', 'total']

    instanceNames_Chi = ['产品销售', '产品销售税', '订单的运费(买家支付)', '订单的运费税', '礼品包装费(买家支付)', '礼品包装费税', '促销回扣',
                         '促销回扣税', '市场预扣税', '销售费用', 'FBA费用', '其他交易费用', '其他', '利润']
    
    cat = ['date/time','settlement' 'id','type','order id','sku','description','quantity','marketplace','account type','fulfillment','order city',
                   'order state','order postal','tax collection model','product sales','product sales tax','shipping credits','shipping credits tax',
                   'gift wrap credits','giftwrap credits tax','promotional rebates','promotional rebates tax','marketplace withheld tax','selling fees','fba fees',
                   'other transaction fees','other','total']
    
    uploaded_file = st.file_uploader('交易记录上传口')
            if uploaded_file is not None:
                uploaded_file = pd.read_csv(uploaded_file, skiprows=7, encoding = "ISO-8859-1")

                if 'account type' in uploaded_file:
                    st.write(1)
                    uploaded_file = uploaded_file.drop('account type', 1)
                uploaded_file.columns = cat
                try:

                    uploaded_file['product sales'] = uploaded_file['product sales'].apply(data_clean)
                    uploaded_file['product sales tax'] = uploaded_file['product sales tax'].apply(data_clean)
                    uploaded_file['shipping credits'] = uploaded_file['shipping credits'].apply(data_clean)
                    uploaded_file['shipping credits tax'] = uploaded_file['product sales'].apply(data_clean)
                    uploaded_file['gift wrap credits'] = uploaded_file['gift wrap credits'].apply(data_clean)
                    uploaded_file['giftwrap credits tax'] = uploaded_file['giftwrap credits tax'].apply(data_clean)
                    uploaded_file['promotional rebates'] = uploaded_file['promotional rebates'].apply(data_clean)
                    uploaded_file['promotional rebates tax'] = uploaded_file['promotional rebates tax'].apply(data_clean)
                    uploaded_file['marketplace withheld tax'] = uploaded_file['marketplace withheld tax'].apply(data_clean)
                    uploaded_file['selling fees'] = uploaded_file['selling fees'].apply(data_clean)
                    uploaded_file['fba fees'] = uploaded_file['fba fees'].apply(data_clean)
                    uploaded_file['other transaction fees'] = uploaded_file['other transaction fees'].apply(data_clean)
                    uploaded_file['other'] = uploaded_file['other'].apply(data_clean)
                    uploaded_file['total'] = uploaded_file['total'].apply(data_clean)


                except:
                    pass

                uploaded_file.to_csv('logs2.csv')
                res = {instanceNames[i]: instanceNames_Chi[i] for i in range(len(instanceNames))}
                holder = {name: Create_objs(name=name, datafile='logs2.csv') for name in instanceNames}
                st.write(' ## 销售额:$', float(round(holder['product sales'].sum)))
                platfrom_fees = holder['marketplace withheld tax'].sum + holder['selling fees'].sum + holder[
                    'fba fees'].sum + holder['other transaction fees'].sum + holder['other'].sum
                st.write(' ## 平台费用:$', round(platfrom_fees))
                st.write(' ## 利润:$', float(round(holder['total'].sum)))
                col1, col2, col3, col4, col5 = st.columns((1, 1, 1, 1, 1))
                h = 1
                for k in instanceNames:
                    if h == 1:
                        col1.metric(label=res[k], value=float(round(holder[k].sum)))
                        h += 1
                    elif h == 2:
                        col2.metric(label=res[k], value=float(round(holder[k].sum)))
                        h += 1
                    elif h == 3:
                        col3.metric(label=res[k], value=float(round(holder[k].sum)))
                        h += 1
                    elif h == 4:
                        col4.metric(label=res[k], value=float(round(holder[k].sum)))
                        h += 1
                    elif h == 5:
                        col5.metric(label=res[k], value=float(round(holder[k].sum)))
                        h = 1
