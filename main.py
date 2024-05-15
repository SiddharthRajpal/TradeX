import streamlit as st
import plotly.graph_objects as go
import datetime
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA  
import pandas as pd
import requests
import json
import streamlit.components.v1 as components

#SETUP

st.set_page_config("Trade X",layout="wide")

st.markdown(

    """
    <style>
        .top-container{
            width: 100%;
            height: 3.5rem;
            background-color: #474955;
            position: fixed;
            top: 0px;
            left: 0px;
            z-index: 1000001;
            padding: 1px;
        }
        .top-title{
            margin-left:1%;
            padding:0px;
        }

    </style>

    <nav class="top-container">
        <h1 class="top-title">Trade X</h1>
    </nav>
    """
, unsafe_allow_html=True
)

ticker  = st.sidebar.text_input("Symbol","NVDA")

start = st.sidebar.text_input("Start Date",f"{datetime.date.today() - datetime.timedelta(183)}")
end = datetime.date.today()

average1 = st.sidebar.slider("Moving Average 1", 0,50, value=20)
average2 = st.sidebar.slider("Moving Average 2", 0,50, value=10)

df = yf.download(ticker, start, end)

df["MA1"] = df.Close.rolling(average1).mean()
df["MA2"] = df.Close.rolling(average2).mean()

#ARIMA STARTS
pred_range = 5

train_df = df['Open']
model = ARIMA(train_df, order=(9,3,1))
model = model.fit()
open_pred = model.forecast(pred_range)

train_df = df['Close']
model = ARIMA(train_df, order=(9,3,1))
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
    go.Candlestick(x=df.index, open = df.Open, close=df.Close, high=df.High, low=df.Low, name=ticker, yaxis="y2", decreasing_line_color='#f23645', increasing_line_color='#089981'),
    go.Bar(x = df.index, y = df['Volume'], yaxis="y3", name="Volume", marker={'color': "#089981"}),
    go.Scatter(x = df.index, y = df['MA1'], line = dict(color='#4c3b75'), name = 'MA1',yaxis="y2", visible= True if average1!=0 else False),
    go.Scatter(x = df.index, y = df['MA2'], line = dict(color='#d3c43a'), name = 'MA2',yaxis="y2", visible= True if average2!=0 else False),
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
sentiment = []

obj = requests.get("https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo")

obj = obj.json()

Max = len(obj["feed"])

for x in range(0,Max):
    titles.append((obj["feed"][x]["title"]))
    links.append((obj['feed'][x]["url"]))
    summary.append((obj['feed'][x]["summary"]))
    sentiment.append((obj['feed'][x]["overall_sentiment_score"]))


def card(title, summary, link, sentiment):
    color = ""

    if -0.25 < sentiment < 0.25:
        color = "white"
    elif sentiment < -0.25:
        color = "rgb(242,54,69)"
    else:
        color = "rgb(8,153,129)"

    return components.html(
            """
            <style>
                #trade-x{
                    padding: 0px;
                }
                .card-wrapper{
                    font-family: "Source Sans Pro", sans-serif;
                    font-weight: 400;
                    color: white;
                    background-color: rgb(38,39,48);
                    width: auto;
                    height: fit-content;
                    margin: 5px;
                    border-radius: 7px;
                    padding: 10px;
                    cursor: pointer;
                }
                .card-header{
                    color: white;
                    font-size: 25px;
                    font-weight: 600;
                    margin: 0px;
                }
                .card-summary{
                    color: white;
                    font-size: 17px;
                    font-weight: 200;
                    margin-top: 5px;
                }
            </style>
            
            <div class="card-wrapper" onclick="window.open('"""+link+"""','mywindow');">
                <h1 class="card-header" style="color: """+color+""";">"""+title+"""</h1>
                <p class="card-summary">"""+summary+"""</p>
            </div>

            """
        , height=200)

cols = 4

cc = st.columns(cols)

for i in range(cols):
    with cc[i]:
        card(titles[i][0:40]+"...", (summary[i][0:100]+"..."), links[i], sentiment[i])

cols = 4

cc = st.columns(cols)

for i in range(cols):
    with cc[i]:
        card(titles[i+4][0:40]+"...", (summary[i+4][0:100]+"..."), links[i+4], sentiment[i+4])




