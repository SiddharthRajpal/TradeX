import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
from statsmodels.tsa import arima_model

invested = 0
profit = 0

def buy(shares):
    pass

def sell(shares):
    pass

st.set_page_config("Trade X",layout="wide")
st.sidebar.header("Select Ticker and Date")

today = datetime.date.today()

ticker  = st.sidebar.text_input("Ticker","NVDA")


start_date = st.sidebar.text_input("Start Date","2023-5-28")
end_date = st.sidebar.text_input("End Date",'2024-1-1')
average1 = st.sidebar.number_input("Moving Average ",value=9)
average2 = st.sidebar.number_input("Moving Average 2", value = 20)
b_price = st.sidebar.number_input("Shares", value = 1)
buy = st.sidebar.button("Buy", on_click=buy(b_price))
sell = st.sidebar.button("Sell",on_click=sell(b_price))


start = pd.to_datetime(start_date)
end = pd.to_datetime(end_date)
data = yf.download(ticker,start,end)

df = pd.DataFrame(data)
df["MA1"] = df.Close.rolling(average1).mean()
df["MA2"] = df.Close.rolling(average2).mean()


fig = go.Figure(data=[
    go.Candlestick(x=df.index, open = df.Open, close=df.Close, high=df.High, low=df.Low),
    go.Scatter(x = df.index, y = df['MA1'], line = dict(color='orange'), name = 'MA1'),
    go.Scatter(x = df.index, y = df['MA2'], line = dict(color='yellow'), name = 'MA2'),
])

fig2 = go.Figure(data=[
    go.Bar(x = df.index, y = df['Volume']),
])

fig.update_layout(autosize = True,height = 700,xaxis_rangeslider_visible=False)

st.plotly_chart(fig,use_container_width=True)

fig2.update_layout(autosize = True,height = 300)

st.plotly_chart(fig2,use_container_width=True)