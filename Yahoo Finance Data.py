import os
import sqlite3
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf
from zipfile import ZipFile


#Get Yahoo Finance Spotify Data from APIs
def get_Spotify_Price():
    '''
    Takes in nothing and returns price_list
    Uses Yahoo Finance API to get day to day closing price for the Spotify Stock
    Appends each day's price into a list
    '''
    price_List = []
    spot = yf.Ticker('SPOT')
    resp = spot.history(period = '1mo', interval = '1d')
    for i in resp['Close']:
        price_List.append(i)

    return price_List

#Get Trading Volume of Spotify from API
def get_Spotify_Volume():
    '''
    Takes in nothing and returns volume_list
    Uses Yahoo Finance API to get day to day trading volume for the Spotify Stock
    Appends each day's volume into a list
    '''
    volume_list = []
    spot = yf.Ticker('SPOT')
    response = spot.history(period = '1mo', interval = '1d')
    print(response)
    for i in response['Volume']:
        volume_list.append(i)
   
    return volume_list

#Calculate Day-to-day Variance
def get_Variance():
    '''
    Takes in nothing and returns variance_list
    Uses Yahoo Finance API to get day to day price for the Spotify Stock
    Then, calculates the variance by subtracting each day's price from the day prior
    Beginning with the second day as the first day has no prior day to compare to
    Appends each day's variance into a list
    '''
    price_list = get_Spotify_Price()
    variance_list = []
    for index, value in enumerate(price_list[1:]):
        day_variance = value - price_list[index]
        answer = float(day_variance)
        variance_list.append(answer)

    return variance_list

#Connect to Database for Data Retrieval
def setUpDatabase(db_name):
    '''
    Takes in db_name and returns cur, conn
    Connects to database (in this case final.db)
    Establishes cur and conn variables for later use with the database
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#Retrieve Number of Streams from the Database
def retrieve_Streams(cur, conn):
    '''
    Takes in cur and conn and returns total_streams
    Uses database connection and SELECT SQL command to retrieve the streams for each week
    Sums each weeks streams
    Adds the sum for each week into a list of total streams for each week
    '''
    list1 = []
    list2 = []
    list3 = []
    list4 = []
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
    '''
    Takes in nothing and returns variance_Graph
    Uses get_Variance function from above to get list of day-to-day variance of Spotify's stock price
    Uses a pandas dataframe in order to properly label and set the data
    Uses seaborn and matplotlib to visualize variance_graph
    '''
    variance = get_Variance()
    df = pd.DataFrame(variance, columns = ['Variance'])
    print(df)
    sns.set_style('darkgrid')
    variance_graph = plt.figure(figsize=(14, 5))
    variance_graph = plt.xticks([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    variance_graph = sns.lineplot(data = df, x = df.index, y = 'Variance', color = 'red', linewidth = 2.5)
    variance_graph.set(xlabel = 'Day', ylabel = 'Variance', title = 'Day-to-Day Variance of Spotify Stock Price Over 4 Weeks')
    plt.show()
    
    return variance_graph

#Visualize Volume
def visualize_Volume():
    '''
    Takes in nothing and returns volume_graph
    Uses the code from get_Volume to retrieve data for volume
    Uses seaborn and matplotlib to visualize volume_graph
    '''
    spot = yf.Ticker('SPOT')
    response = spot.history(period = '1mo', interval = '1d')
    volume_graph = plt.figure(figsize=(14, 5))
    sns.set_style('darkgrid')
    volume_graph = sns.lineplot(data = response, x = 'Date', y = 'Volume', color = 'gold', linewidth = 2.5)
    volume_graph.set(xlabel = 'Day', ylabel = 'Volume', title = "Spotify Trading Volume")
    plt.show()

    return volume_graph

#Visualize a linear regression plot for the two variables of Streams and Stock Price
def visualize_correlation(cur, conn):
    '''
    Takes in cur and conn and returns visualizeCorrelation
    Creates the linear regression plot for the variables of Spotify Streams and Spotify Stock Price
    Uses retrieved streaming data from retrieve_Streams
    Uses pandas dataframes to combine the data for use
    matplotlib and seaborn are used to visualize visualizeCorrelation
    '''
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
     y = 'Weekly Spotify Stock Price',
     )
    visualizeCorrelation.set(title = "Linear Regression of Total Top Song Streams and Weekly Stock Price")

    plt.show()

    return visualizeCorrelation

#Write Calculations to Text File which can then be zipped
def write_to_text(calculation1, calculation2, calculation3, calculation4):
    '''
    Takes in the four calculations from above and returns None
    Writes calculations into a text file in directory
    '''
    file_name = 'calculations.txt'
   #full_path = os.path.join(save_path, file_name)
    with open(file_name, 'w') as f:
     f.writelines(' Spotify Price: ' + str(calculation1) + '\n')
     f.writelines(' Spotify Trading Volume: ' + str(calculation2) + '\n')
     f.writelines(' Spotify Stock Price Variance: ' + str(calculation3) + '\n')
     f.writelines(' Stream Data from Database: ' + str((calculation4)) + '\n')
   
    f.close()

    return None


#Main function of the file to call the code
def main():
    '''
    Takes in nothing and returns None
    Used to set up and run all the code above
    Utilizes cur, conn, and calculations 1-4 variables as well as final.db string
    To make sure each function has the necessary variables to run properly
    '''
    cur, conn = setUpDatabase('final.db')
    calculation1 = get_Spotify_Price()
    calculation2 = get_Spotify_Volume()
    calculation3 = get_Variance()
    visualize_Variance()
    visualize_Volume()
    calculation4 =  retrieve_Streams(cur, conn)
    visualize_correlation(cur, conn)
    write_to_text(calculation1, calculation2, calculation3, calculation4)

    return None

main()
