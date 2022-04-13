import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import os
import re
import pprint
import seaborn as sns
import matplotlib.pyplot as plt

# This file gets data from the Spotify API 
# get top 50, viral 50 from api
# made other two databses
# overlap songs (25?)

#To set up client credentials for spotipy
os.environ['SPOTIPY_CLIENT_ID'] = '473bcf2d2cc74da7a4affadb888cc338'
os.environ['SPOTIPY_CLIENT_SECRET'] = '07558f45c4a2444ab3344ab5a3104903'

def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_spotipy():
	client_credentials_manager = SpotifyClientCredentials()
	sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
	return sp

def search_for_playlists(sp):
    top_usa = "spotify top 50 usa"
    top_usa_id = sp.search(q=top_usa, type='playlist', limit=1)
    top_global = "spotify top songs global"
    top_global_id = sp.search(q=top_global, type='playlist', limit=1)
    ids = {}
    ids['usa_id'] = top_usa_id['playlists']['items'][0]['uri']
    ids['global_id'] = top_global_id['playlists']['items'][0]['uri']
    return ids

def get_usa_info(id_dict, sp, cur, conn):
    #getting 49 songs
    #cur.execute('DROP TABLE IF EXISTS usa_top_50')
    cur.execute('CREATE TABLE IF NOT EXISTS usa_top_50 (song_id INTEGER PRIMARY KEY, song_title TEXT, artist TEXT)')
    cur.execute("SELECT song_id FROM usa_top_50 WHERE song_id = (SELECT MAX(song_id) FROM usa_top_50)")
    curr_spot = cur.fetchone()
    if curr_spot == None:
        count = 0
    else:
        count = curr_spot[0]
    response1 = sp.playlist(id_dict['usa_id'])
    response = sp.playlist_items(id_dict['usa_id'],offset=count,limit=25,additional_types=['track'])
    for i in range(25):
        artist = response['items'][i]['track']['artists'][0]['name']
        title = response['items'][i]['track']['name']
        cur.execute("INSERT OR IGNORE INTO usa_top_50 VALUES (?,?,?)", (count, title, artist))
        conn.commit()
        count+=1
    conn.commit()
    


def get_global_info(id_dict, sp, cur, conn):
    #getting 48 songs
    #cur.execute('DROP TABLE IF EXISTS global_top_50')
    cur.execute('CREATE TABLE IF NOT EXISTS global_top_50 (song_id INTEGER PRIMARY KEY, song_title TEXT, artist TEXT)')
    cur.execute("SELECT song_id FROM global_top_50 WHERE song_id = (SELECT MAX(song_id) FROM global_top_50)")
    curr_spot = cur.fetchone()
    if curr_spot == None:
        count = 0
    else:
        count = curr_spot[0]
    response = sp.playlist_items(id_dict['global_id'],offset=count,limit=25,additional_types=['track'])
    for i in range(25):
        artist = response['items'][i]['track']['artists'][0]['name']
        title = response['items'][i]['track']['name']
        cur.execute("INSERT OR IGNORE INTO global_top_50 VALUES (?,?,?)", (count, title, artist))
        count+=1
    conn.commit()

def combined_top(cur,conn):
    #cur.execute('DROP TABLE IF EXISTS result')
    cur.execute('CREATE TABLE result AS SELECT usa_top_50.song_id, usa_top_50.song_title, usa_top_50.artist FROM usa_top_50 JOIN global_top_50 ON usa_top_50.song_title = global_top_50.song_title')
    conn.commit()
    
# visualisations of chosen data 
#def make_visualisations(lst,cur,conn):

def main():
    cur, conn = set_up_database("final.db")
    sp = set_up_spotipy()
    id_dict = search_for_playlists(sp)
    #get_usa_info(id_dict, sp, cur, conn)
    #get_global_info(id_dict, sp, cur, conn)
    combined_top(cur,conn)


if __name__ == "__main__":
    main()