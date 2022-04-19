#from calendar import day_abbr
import sqlite3
import requests
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

#Calculate Correlation
#def get_Correlation():
    
    #return correlation


#Visualize Variance
def visualize_Variance():
    variance = get_Variance()
    #plt.figure(figsize=(14, 5))
    sns.set_style('darkgrid')
    variance_graph = sns.lineplot(data = variance, color = 'red', linewidth = 2.5) #,
    #col = 'Day-to-Day Variance over 4 Weeks')
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
    volume_graph.set(xlabel = 'day', ylabel = 'Volume', title = "Spotify Trading Volume")

    #plt.title('Price-to-Earnings Ratio over 4 Weeks')
    plt.show()

    return volume_graph

def visualize_correlation():
    plt.figure(figsize=(14,5))
    visualizeCorrelation = sns.regplot(data = total_streams,
     x = 'Total Streams', 
     y = 'Stock Price')

    return visualizeCorrelation


#get_Spotify_Price()
#get_Spotify_Volume()
#get_Variance()
visualize_Variance()
visualize_Volume()