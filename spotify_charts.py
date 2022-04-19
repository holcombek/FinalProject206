import sqlite3
import os
from bs4 import BeautifulSoup

#This file parses through html files saved from the Spotify Charts (older) website (https://spotifycharts.com/regional)
# and saves all data into a dictionary for each week, then uses those dictionaries to cross reference with Billboard
# Hot 100 database to get streaming info for each song on both lists

#Sets up connection with database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# gathers data from spotifycharts html file and put into dictionary
# html files cover the past four weeks (3-17, 3-24, 3-31, 4-07)
# each html page has the 200 songs most streamed in that week on Spotify
def get_data():
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
                stuff = top_song_dict.get(j)
                # adding each song to the top_songs dict
                top_song_dict[j] = (stuff, title, artist)
                j += 1
            all_lst.append(top_song_dict)
    return all_lst

# takes each week's dictionary to cross reference with billboard list for corresponding week and gather streaming data
def database(dictr, j, names, start, cur,conn):
    #cur.execute('DROP TABLE IF EXISTS ' + names)
    # billboard tables in database
    name_lst = ['Billboard_week_1', 'Billboard_week_2', 'Billboard_week_3', 'Billboard_week_4']
    cur.execute('CREATE TABLE IF NOT EXISTS ' + names + ' (song_id INTEGER PRIMARY KEY, streams INTEGER)')
    conn.commit()
    # getting all song titles only from billboard to cross reference
    cur.execute(f'SELECT song_title FROM ' + name_lst[j])
    billboard_songs = cur.fetchall()
    new_billboard = []
    current = []
    streaming = []
    for song in billboard_songs:
        # adds billboard song titles as a string to new list
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
            cur.execute(f'SELECT * FROM {name_lst[j]} WHERE song_title = \'{current[position]}\' ')
            song_data = cur.fetchall()
            # accounts for potential empty data
            if song_data == []:
                continue
            else:
                # gets id from Billboard chart, to cross reference later for song_title
                id = song_data[0][0]
                cur.execute(f'INSERT INTO {names} (song_id, streams) VALUES(?,?)', (id, streaming[position]))
                conn.commit()
    conn.commit()

#need to use JOIN on billboard and spotify table
def joining_tables():
    pass

def main():
    #Setting up connection to database
    cur,conn = setUpDatabase('final.db')

    #List of playlist data (each one has 200 songs)
    playlist_lst = get_data()

    #Set up names, start range
    name_lst = ['spotify_streams_week_1' , 'spotify_streams_week_2', 'spotify_streams_week_3', 'spotify_streams_week_4']
    start = 75

    #Run 4 times to go through all 100 songs of each playlist
    for i in range(4):
        database(playlist_lst[i], i, name_lst[i], start, cur, conn)



if __name__ == "__main__":
    main()