import streamlit as st
import plotly.graph_objects as go
import datetime
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA  
import pandas as pd
import requests
import json
import hydralit_components as hc

#SETUP

st.set_page_config("Trade X",layout="wide")
ticker  = st.sidebar.text_input("Symbol","NVDA")

start = st.sidebar.text_input("Start Date",f"{datetime.date.today() - datetime.timedelta(183)}")
end = datetime.date.today()

average1 = st.sidebar.number_input("Moving Average 1", value=9)
average2 = st.sidebar.number_input("Moving Average 2", value = 20)

df = yf.download(ticker, start, end)

df["MA1"] = df.Close.rolling(average1).mean()
df["MA2"] = df.Close.rolling(average2).mean()

#ARIMA STARTS
pred_range = 5

train_df = df['Open']
model = ARIMA(train_df, order=(5,1,0))
model = model.fit()
open_pred = model.forecast(pred_range)

train_df = df['Close']
model = ARIMA(train_df, order=(5,1,0))
model = model.fit()
close_pred = model.forecast(pred_range)



i = []
last = datetime.date.today()

for _ in range(pred_range):
    i.append(str(last + datetime.timedelta(_+1)))

pred = pd.DataFrame({'open':open_pred.values, 'timestamp':i, 'close':close_pred.values})

#ARIMA ENDS

#PLOTTING 

fig = go.Figure(data=[
    go.Candlestick(x=pred['timestamp'], open=pred['open'], close=pred['close'], high=pred['open'],low=pred['close'], increasing_line_color='cyan', decreasing_line_color='orange', name='Prediction', yaxis='y2'),
    go.Candlestick(x=df.index, open = df.Open, close=df.Close, high=df.High, low=df.Low, name=ticker, yaxis="y2"),
    go.Bar(x = df.index, y = df['Volume'], yaxis="y3", name="Volume"),
    go.Scatter(x = df.index, y = df['MA1'], line = dict(color='orange'), name = 'MA1',yaxis="y2"),
    go.Scatter(x = df.index, y = df['MA2'], line = dict(color='cyan'), name = 'MA2',yaxis="y2"),
],

layout = go.Layout(
    yaxis=dict(
        domain=[0.2,1],
    ),
    yaxis2=dict(
        domain=[0.2,1]
    ),
    yaxis3=dict(
        domain=[0,0.2]
    )
))

fig.update_layout(autosize = True,height = 850, xaxis_rangeslider_visible=False)

st.plotly_chart(fig,use_container_width=True)


#NEWS
titles = []
links = []
summary = []

obj = requests.get("https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo")

obj = obj.json()

Max = len(obj["feed"])

for x in range(0,Max):
    titles.append((obj["feed"][x]["title"]))
    links.append((obj['feed'][x]["url"]))
    summary.append((obj['feed'][x]["summary"]))

# title, links, summary = news(option-1)
# res = card(
#     title= title[0:40]+"...",
#     url= links,
#     text= summary[0:100]+"...",
# )

hc.info_card(title=titles[0], content=summary[0], key='1')
hc.info_card(title=titles[1], content=summary[1], key='5')
hc.info_card(title=titles[2], content=summary[2], key='2')
