from forex_python.converter import CurrencyRates
import streamlit as st
import pandas as pd

def finance():
    c = CurrencyRates()
    usd = round(c.get_rate('USD', 'CNY'), 2)
    eur = round(c.get_rate('EUR', 'CNY'), 2)
    gbp = round(c.get_rate('GBP', 'CNY'), 2)
    cad = round(c.get_rate('CAD', 'CNY'), 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="USD/CNY", value=usd)
    col2.metric(label="EUR/CNY", value=eur)
    col3.metric(label="GBP/CNY", value=gbp)
    col4.metric(label="CAD/CNY", value=cad)


    class Create_objs:

        def __init__(self, name, datafile=None):
            self.df = pd.read_csv(datafile)
            self.name = name
            self.sum = self.df[self.name].sum()
    instanceNames = ['product sales', 'product sales tax', 'shipping credits', 'shipping credits tax',
                     'gift wrap credits', 'giftwrap credits tax', 'promotional rebates',
                     'promotional rebates tax', 'marketplace withheld tax', 'selling fees', 'fba fees',
                     'other transaction fees', 'other', 'total']

    instanceNames_Chi = ['产品销售', '产品销售税', '订单的运费(买家支付)', '订单的运费税', '礼品包装费(买家支付)', '礼品包装费税', '促销回扣',
                         '促销回扣税', '市场预扣税', '销售费用', 'FBA费用', '其他交易费用', '其他', '利润']
    uploaded_file = st.file_uploader('交易记录上传口')
    if uploaded_file is not None:
        uploaded_file = pd.read_csv(uploaded_file)
        uploaded_file = uploaded_file.iloc[6:, :]
        uploaded_file.to_csv('logs2.csv', header=False, index=False)
        res = {instanceNames[i]: instanceNames_Chi[i] for i in range(len(instanceNames))}
        holder = {name: Create_objs(name=name, datafile='logs2.csv') for name in instanceNames}

        st.write(' ## 销售额:$', float(round(holder['product sales'].sum)))
        platfrom_fees = holder['marketplace withheld tax'].sum + holder['selling fees'].sum + holder['fba fees'].sum + holder['other transaction fees'].sum + holder['other'].sum
        st.write(' ## 平台费用:$', platfrom_fees)
        st.write(' ## 利润:$', float(round(holder['total'].sum)))
        with st.expander('详细数据', expanded=True):
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