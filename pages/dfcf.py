import requests
import streamlit as st
import datetime
import json
import sqlite3

@st.cache_data(ttl=600)
def query(date):
    data = []
    qtype = [0, 1, 2, 3]
    dbtype = {"0": "list", "1": "list", "2": "list", "3": "jg", }
    for i in qtype:
        pageno = 1
        run_flag = True
        while run_flag:
            url = 'https://reportapi.eastmoney.com/report/{0}?pageSize=100&beginTime={1}&endTime={1}&pageNo={2}&qType={3}'.format( \
                dbtype[str(i)], str(date), str(pageno), str(i))
            resp = requests.get(url).json()

            for j in resp['data']:
                title = j['title']
                orgSName = j['orgSName']
                industryName = j['industryName']
                try:
                    stockName = j['stockName']
                    infoCode = j['infoCode']
                    link = 'https://pdf.dfcfw.com/pdf/H3_{0}_1.pdf'.format(infoCode)
                except:
                    stockName = "None"
                    infoCode = j["encodeUrl"]
                    link = 'https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl={0}'.format(infoCode)

                data.append({"type": i,"data": "{0} {1} {2} {3} {4}".format(stockName, industryName, title, orgSName, link)})
            if (resp['hits']==0/ 100 > pageno):pageno = pageno + 1
            else:run_flag = False
    return data

def func_date_change(date):
    data = query(date)
    c1,c2,c3 = st.columns(3)

    for i in data:
        if i['type'] == 0:
            c1.write(i['data'])
        elif i['type'] == 1:
            c2.write(i['data'])
        else:
            c3.write(i['data'])

def download():
    data = query(st.session_state['selected_time'])
    data = json.dumps(data,ensure_ascii=False,indent=2)
    return data

def writr2sql():
    data = query(st.session_state['selected_time'])
    conn = sqlite3.connect('dfcf.db')
    c = conn.cursor()
    #
    try:
        sql = 'CREATE TABLE dfcf (type ANY,date ANY,data ANY);'
        c.execute(sql)
    except:
        print('table exsits')
    #
    for i in data:
        sql = 'INSERT INTO dfcf (type,date,data) VALUES ("{0}","{1}","{2}")'.format(i['type'],st.session_state['selected_time'],i['data'])
        c.execute(sql)

    conn.commit()
    conn.close()


st.set_page_config(page_title='????????????????????????', page_icon=None, layout="wide")

if 'selected_time' not in st.session_state:
    st.session_state['selected_time'] = datetime.date.today()

st.sidebar.date_input('??????????????????',key='selected_time',on_change = func_date_change(st.session_state['selected_time']))
st.sidebar.download_button('????????????????????????',data=download(),file_name='{0}.txt'.format(st.session_state['selected_time']))
st.sidebar.button('??????????????????',on_click=writr2sql())
