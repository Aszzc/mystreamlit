import streamlit as st
import datetime
import requests
from parsel import Selector

def main():
    st.set_page_config(page_title='东方财富研报查询', page_icon=None, layout="wide")
    if 'selected_date' not in st.session_state:st.session_state['selected_date'] = datetime.date.today()
    st.sidebar.date_input('选择查询日期',key='selected_date',on_change = query(st.session_state.selected_date))


def processlink(link):
    resp = requests.get(link)
    sl = Selector(resp.text)
    pdf_url = sl.xpath('//a[@class = "pdf-link"]/@href').extract_first()
    return pdf_url



@st.cache_data(ttl=600)   
def query(selected_date):
    
    st.write(selected_date)
    c1,c2,c3 = st.columns(3, gap="small")
    
    qtype = [0,1,2,3,4]
    dbtype = {"0":"list","1":"list","2":"list","3":"jg","4":"jg",}
    
    for i in qtype:
        
        run_flag = True
        pageno = 1
        
        while run_flag:
            url = 'https://reportapi.eastmoney.com/report/{0}?pageSize=100&beginTime={1}&endTime={1}&pageNo={2}&qType={3}'.format(\
            dbtype[str(i)],str(selected_date),str(pageno),str(i))
            resp = requests.get(url).json()
            
            for j in resp['data']:
                title = j['title']
                orgSName = j['orgSName']
                publishDate = j['publishDate']
                industryName = j['industryName']
                try:
                    stockName = j['stockName']
                    infoCode = j['infoCode']
                    link = 'https://pdf.dfcfw.com/pdf/H3_{0}_1.pdf'.format(infoCode)
                except:
                    stockName = "None"
                    infoCode = j["encodeUrl"]
                    link = 'https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl={0}'.format(infoCode)
                    link = processlink(link)
                    
                if i == 0:
                    c1.write('{0} {1} {2} {3}'.format(stockName,industryName,title,link))
                elif i== 1:
                    c2.write('{0} {1} {2} {3}'.format(stockName,industryName,title,link))
                else:
                    c3.write('{0} {1} {2} {3}'.format(stockName,industryName,title,link))
                
            if resp['hits']/100 > pageno:
                pageno = pageno+1
            else:
                run_flag = False
                
main()
