from calendar import day_abbr
import requests
import seaborn as sns
import matplotlib as plt


api = 'https://yfapi.net/v8/finance/chart/SPOT'

api2 = 'https://yfapi.net/v6/finance/quote/SPOT'

#Get Yahoo Finance Spotify Data from API
def get_Spotify_Price(api, params = {'range' : '1mo', 'region' : 'US', 'interval' : '1d', 'language' : 'en', 'ticker' : 'SPOT'}):
    price_List = []
    resp = requests.get(api)
    for i in resp:
        price_List.append(i['chart']['result']['meta']['regularMarketPrice'])

    return price_List

#Get Trailing P/E Ratio from API
def get_Spotify_PE(api2, params = {'region' : 'US', 'lang' : 'en', 'symbols' : 'SPOT'}):
    PE_list = []
    response = requests.get(api2)
    for i in response:
        PE_list.append(i['quoteResponse']['result']['trailingPE'])

#Calculate Variance
def get_Variance(price_list):
    variance_list = []
    for i in price_list[1:]:
        day_variance = i - i[i-1]
        variance_list.append(day_variance)

    variance = sum(variance_list)/len(price_list)


    return variance

#Calculate Correlation
def get_Correlation():

    return None


#Visualize Variance
def visualize_Variance(variance):
    plt.figure(figsize=(14, 5))
    variance_graph = sns.lineplot(data = variance,
    x = 'day',
    y = 'variance')

    plt.title('Spotify Daily Stock Price Variance over 4 Weeks')
    plt.show()
    
    return None

def visualize_PE(PE):
    plt.figure(figsize=(14, 5))
    visualize_PE = sns.lineplot(data = PE, 
    x = 'day'
    y = 'Price-to-Earnings Ratio')

    plt.title('Price-to-Earnings Ratio over 4 Weeks')
    plt.show()

    return None


get_Spotify_Price(api)
