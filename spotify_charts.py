import sqlite3
import os
import requests
from bs4 import BeautifulSoup
# 200 songs from website, make list all songs, search for songs in lst, get streaming data and put into table

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_data():
    file_lst = ['wk3.17spotify.html', 'wk3.24spotify.html', 'wk3.31spotify.html', 'wk4.7spotify.html']
    base_path = os.path.abspath(os.path.dirname(__file__))
    all_lst =[]
    for i in range(4):
        full_path = os.path.join(base_path, file_lst[i])
        with open(full_path, "r", encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            song_lst = {}
            i = 1
            song_data = soup.find('table', class_='chart-table')
            streams = song_data.find_all('td', class_='chart-table-streams')
            for stream in streams:
                stream_number = stream.text.strip(',')
                song_lst[i] = stream_number
                i+=1
            song_info = song_data.find_all('td', class_='chart-table-track')
            j=1
            for song in song_info:
                title = song.find('strong').text.strip()
                artist = song.find('span').text.strip()
                stuff = song_lst.get(j)#.append(title, artist)
                song_lst[j] = (stuff, title, artist)
                j+=1
            #print(title, artist, stream_number)
            all_lst.append(song_lst)
    return all_lst

   
# bar graph of top 5 songs and number of total streams
# line graph top song and number of streams over month
def database(lst, j, names, cur,conn):
    #takes in song dict
    name_lst = ['Billboard_week_4', 'Billboard_week_3', 'Billboard_week_2', 'Billboard_week_1']
    cur.execute('CREATE TABLE IF NOT EXISTS ' + names + ' (song_id INTEGER PRIMARY KEY, streams TEXT)')
    conn.commit()
    #FIX TO INSERT 25 AT A TIME
    for i in range(len(lst)):
        cur_title = lst[i+1][1]
        cur_streams = lst[i+1][0]
        #names different, need to clean data
        cur.execute(F'SELECT song_id FROM {name_lst[j]} WHERE song_title = \'{cur_title}\' ')
        id = cur.fetchone()[0]
        cur.execute(f'INSERT OR IGNORE INTO {names} (song_id, streams) VALUES(?,?)', (id, cur_streams))
        print('working')
    conn.commit()
    #get song_id, match put into database w streams (total 8 tables in database)

def main():
    cur,conn = setUpDatabase('final.db')
    lst = get_data()
    #database(lst)
    #NEED TO ACCOUNT FOR ALL 4 WEEKS
    for i in range(4):
        database(lst[i], i, f'spotify_streams_week_{i+1} ', cur, conn)



if __name__ == "__main__":
    main()