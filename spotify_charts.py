import sqlite3
import os
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt

#This file parses through html files saved from the Spotify Charts 
# (older) website (https://spotifycharts.com/regional)
# and saves all data into a dictionary for each week, then uses those dictionaries 
# to cross reference with Billboard Hot 100 database 
# to get streaming info for each song on both lists

def setUpDatabase(db_name):
    '''
    Takes in database name; returns cursor and connection objects.
    Used in main to set up database.
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_charts_data():
    '''
    Takes in nothing; returns list of dictionaries with song rank
     as key and song title, artist, and number of streams as values
     for each week of Spotify top 200 streamed songs.
    Scrapes SpotifyCharts HTML files of given weeks below for
     song data using BeautifulSoup objects.
    '''
    # list of last 4 weeks of Spotify Charts data, with date as beginning of week
    file_lst = ['wk3.17spotify.html', 'wk3.24spotify.html', 'wk3.31spotify.html', 'wk4.7spotify.html']
    base_path = os.path.abspath(os.path.dirname(__file__))
    #all_lst holds all four dictionaries (one for each week)
    all_lst =[]
    for i in range(4):
        full_path = os.path.join(base_path, file_lst[i])
        with open(full_path, "r", encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            top_song_dict = {}
            # j and i are position variables
            i = 1
            j = 1
            # finding song data
            song_data = soup.find('table', class_='chart-table')
            # using song_data to find stream number
            streams = song_data.find_all('td', class_='chart-table-streams')
            for stream in streams:
                # getting stream number and stripping excess characters, so it can be used as an integer
                stream_number = stream.text.replace(',', "")
                top_song_dict[i] = stream_number
                i += 1
            # using song_data to find title and artist
            song_info = song_data.find_all('td', class_='chart-table-track')
            for song in song_info:
                # getting title and artist and stripping any excess characters
                title = song.find('strong').text.strip()
                artist = song.find('span').text.strip()
                curr_stuff = top_song_dict.get(j)
                # adding each song to the top_songs dict
                top_song_dict[j] = (curr_stuff, title, artist)
                j += 1
            all_lst.append(top_song_dict)
    return all_lst

def database(dictr, week, name, start, cur, conn):
    '''
    Takes in given weeks dictionary of Spotify Charts data, week variable, 
     name of table to be created, start variable, cursor, connection; returns nothing.
    Creates Spotify Streams table for given week
     with Billboard rank (song_id) and number of streams
     by looping through Spotify Charts dict 25 items at a time.
    '''
    # comment out if need to reset data collection
    #cur.execute('DROP TABLE IF EXISTS ' + names)
    # week 1 is earliest week, week 4 most recent
    name_lst = ['Billboard_week_1', 'Billboard_week_2', 'Billboard_week_3', 'Billboard_week_4']
    cur.execute('CREATE TABLE IF NOT EXISTS ' + name + ' (song_id INTEGER PRIMARY KEY, streams INTEGER)')
    conn.commit()
    # getting song titles ONLY from billboard to cross reference
    cur.execute(f'SELECT song_title FROM ' + name_lst[week])
    billboard_songs = cur.fetchall()
    new_billboard = []
    current = []
    streaming = []
    # adds billboard song titles as a string to new list
    for song in billboard_songs:
        new_billboard.append(song[0])
    for item in range(len(dictr)):
        # adds current spotify charts song to list as a stripped down string
        cur_title = dictr[item+1][1]
        cur_title = cur_title.lower().strip().replace("(", "").replace("'","").replace("-","").replace(")", "").replace(" ", "")
        current.append(cur_title)
        # adds number of streams to list of corresponding streams
        streams = dictr[item+1][0]
        streaming.append(streams)
    for i in range(start, start+25):
        # song to cross reference from Billboard to Spotify Charts
        to_cross = new_billboard[i]
        # looking for billboard song in list of spotify charts songs
        if to_cross in current:
            # gets index to reference for streams
            position = current.index(new_billboard[i])
            cur.execute(f'SELECT * FROM {name_lst[week]} WHERE song_title = \'{current[position]}\' ')
            song_data = cur.fetchall()
            # accounts for potential empty data
            if song_data == []:
                continue
            else:
                # gets song_id from Billboard chart, to cross reference laterin file for song title and artist
                id = song_data[0][0]
                cur.execute(f'INSERT INTO {name} (song_id, streams) VALUES(?,?)', (id, streaming[position]))
                conn.commit()
    conn.commit()

def joining_billboard_spotify_tables(week, cur, conn):
    ''' 
    Takes in week variable, cursor, connection; returns nothing.
    Uses SQL query with JOIN on song_ids to create a new, combined table of
     song info from Billboard table and Spotify table for given week 
     (with billboard rank, song title, artist, and spotify streams).
    '''
    # comment out unless needed to reset data in tables
    #cur.execute(f'DROP TABLE IF EXISTS billboardXspotify_wk{week}')
    cur.execute(f'''CREATE TABLE billboardXspotify_wk{week} AS 
                    SELECT Billboard_week_{week}.song_id AS 'billboard_rank_id',
                    Billboard_week_{week}.song_title, Billboard_week_{week}.artist, spotify_streams_week_{week}.streams 
                    FROM Billboard_week_{week} JOIN spotify_streams_week_{week} 
                    ON Billboard_week_{week}.song_id = spotify_streams_week_{week}.song_id
                    ORDER BY spotify_streams_week_{week}.streams DESC''')
    conn.commit()

def streams_visualisation(cur, conn):
    '''
    Takes in cursor, connection; returns nothing.
    Finds MAX numbers of streams using SQL query from
     joined BillboardxSpotify table for each week
     and creates a scatter graph using Seaborn showing the 
     change over last four weeks.
    '''
    max_streams = []
    for i in range(1,5):
        # finds MAX streams for given week
        cur.execute(f'SELECT MAX(streams) FROM billboardXspotify_wk{i}')
        conn.commit()
        info = cur.fetchall()
        max_streams.append(info[0][0])
    sns.set_style('darkgrid')
    # creates plot and labels with Seaborn
    print(max_streams)
    streamplot = sns.relplot(data=max_streams, color = 'magenta')
    streamplot.set(xlabel = 'Weeks', ylabel = 'Number of Streams (in tens of millions)', title = 'Billboard Top Song Number of Streams Over Past 4 Weeks')
    plt.show()

def main():
    '''
    Main function of file.
    Sets up database and sets up list of dictionaries with song info.
    Adds song information for each week to corresponding table
     25 items at a time (for each of the four weeks) with changing start value.
    Joins tables in database to create new tables with 
     billboard rank and number of spotify streams.
    Shows visualization.
    '''
    cur,conn = setUpDatabase('final.db')

    # list of playlist dictionaries (each one has 200 songs)
    playlist_lst = get_charts_data()

    # set up names of tables, start range
    name_lst = ['spotify_streams_week_1' , 'spotify_streams_week_2', 'spotify_streams_week_3', 'spotify_streams_week_4']
    
    #start values are 0, 25, 50, 75; change start value each time you run file
    # to next start value (four times in total) beginning with 0
    start = 0

    # comment out if already created
    # run 4 times to go through all 100 songs of each playlist
    #for i in range(4):
        #database(playlist_lst[i], i, name_lst[i], start, cur, conn)
    
    # comment out if already created
    #for i in range(1,5):
        #joining_billboard_spotify_tables(i, cur, conn)
    
    # comment out if don't want to see visualization
    # streams_visualisation(cur, conn)



if __name__ == "__main__":
    main()