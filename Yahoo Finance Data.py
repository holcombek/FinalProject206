import os
import sqlite3
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf



#api = 'https://yfapi.net/v8/finance/chart/SPOT?range=1mo&region=US&interval=1d&lang=en&events=div%2Csplit'

#api2 = 'https://yfapi.net/v6/finance/quote/SPOT'

#api_key = 'jr6crJlIJh1uTSmQ0tHsM7DJWCjfsPsu5xCVCBbo'

#Get Yahoo Finance Spotify Data from API
def get_Spotify_Price():
    price_List = []
    spot = yf.Ticker('SPOT')
    resp = spot.history(period = '1mo', interval = '1d')
    #resp = requests.get(api, headers = 'X-API-KEY : jr6crJlIJh1uTSmQ0tHsM7DJWCjfsPsu5xCVCBbo', params = {'range' : '1mo', 'region' : 'US', 'interval' : '1d', 'language' : 'en', 'ticker' : 'SPOT'})
    for i in resp['Close']:
        price_List.append(i)

    return price_List

#Get Trading Volume of Spotify from API
def get_Spotify_Volume():
    volume_list = []
    #response = requests.get(api2, params = {'region' : 'US', 'lang' : 'en', 'symbols' : 'SPOT'})
    spot = yf.Ticker('SPOT')
    response = spot.history(period = '1mo', interval = '1d')
    print(response)
    for i in response['Volume']:
        volume_list.append(i)
   
    return volume_list

#Calculate Day-to-day Variance
def get_Variance():
    price_list = get_Spotify_Price()
    variance_list = []
    for index, value in enumerate(price_list[1:]):
        day_variance = value - price_list[index]
        answer = float(day_variance)
        variance_list.append(answer)

    return variance_list

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def retrieve_Streams(cur, conn):
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    #connection = setUpDatabase('final.db')
    #conn = sqlite3.connect('final.db')
    #cursor = connection.cursor()
    cur.execute('''SELECT streams FROM spotify_streams_week_1''')
    result1 = cur.fetchall()
    cur.execute('''SELECT streams FROM spotify_streams_week_2''')
    result2 = cur.fetchall()
    cur.execute('''SELECT streams FROM spotify_streams_week_3''')
    result3 = cur.fetchall()
    cur.execute('''SELECT streams FROM spotify_streams_week_4''')
    result4 = cur.fetchall()


    for i in result1:
        streams = i[0]
        list1.append(streams)

    for i in result2:
        streams = i[0]
        list2.append(streams)
    
    for i in result3:
        streams = i[0]
        list3.append(streams)
    
    for i in result4:
        streams = i[0]
        list4.append(streams)


    sum1 = sum(list1)
    sum2 = sum(list2)
    sum3 = sum(list3)
    sum4 = sum(list4)

    total_Streams = [sum1, sum2, sum3, sum4]

    return total_Streams


#Visualize Variance
def visualize_Variance():
    variance = get_Variance()
    df = pd.DataFrame(variance, columns = ['Variance'])
    print(df)
    sns.set_style('darkgrid')
    variance_graph = plt.figure(figsize=(14, 5))
    variance_graph = plt.xticks([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    variance_graph = sns.lineplot(data = df, x = df.index, y = 'Variance', color = 'red', linewidth = 2.5)
    variance_graph.set(xlabel = 'Day', ylabel = 'Variance', title = 'Day-to-Day Variance of Spotify Stock Price Over 4 Weeks')

   # plt.title('Spotify Daily Stock Price Variance over 4 Weeks')
    plt.show()
    
    return variance_graph

#Visualize Volume
def visualize_Volume():
    spot = yf.Ticker('SPOT')
    response = spot.history(period = '1mo', interval = '1d')
    volume_graph = plt.figure(figsize=(14, 5))
    sns.set_style('darkgrid')
    volume_graph = sns.lineplot(data = response, x = 'Date', y = 'Volume', color = 'gold', linewidth = 2.5)
    volume_graph.set(xlabel = 'Day', ylabel = 'Volume', title = "Spotify Trading Volume")

    #plt.title('Price-to-Earnings Ratio over 4 Weeks')
    plt.show()

    return volume_graph

def visualize_correlation(cur, conn):
    spot = yf.Ticker('SPOT')
    data1 = retrieve_Streams(cur, conn)
    price_List = []
    resp = spot.history(period = '1mo', interval = '1wk')
    for i in resp['Close']:
        price_List.append(i)
    data2 = price_List
    df1 = pd.DataFrame(data1, columns = ['Weekly Total Spotify Streams'])
    df2 = pd.DataFrame(data2, columns = ['Weekly Spotify Stock Price'])
    final_df = df1.join(df2)
    #print(final_df)

    plt.figure(figsize=(10,16))
    visualizeCorrelation = sns.regplot(data = final_df, color = 'purple',
     x = 'Weekly Total Spotify Streams', 
     y = 'Weekly Spotify Stock Price')

    plt.show()

    return visualizeCorrelation

def main():
    cur, conn = setUpDatabase('final.db')
    get_Spotify_Price()
    get_Spotify_Volume()
    get_Variance()
    visualize_Variance()
    visualize_Volume()
    retrieve_Streams(cur, conn)
    visualize_correlation(cur, conn)

main()
