import sqlite3
import os
import requests
from bs4 import BeautifulSoup
import json

# This file gets the top 100 songs from Billboard Hot 100 and puts them into a database
# No visualisations done for this data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


# option to input which week(s) you want to look at?
#consider multiple weeks as well, could make list of urls and do for each url
def get_top_100_billboard():
    url = "https://www.billboard.com/charts/hot-100/"
    #Using BeautifulSoup to parse website for song title and artist name
    r = requests.get(url)
    if r.ok:
        top_100_song_lst = []
        soup = BeautifulSoup(r.content, 'html.parser')
        top = soup.find_all('ul', class_="lrv-a-unstyle-list lrv-u-flex lrv-u-height-100p lrv-u-flex-direction-column@mobile-max")
        i = 1
        for tag in top:
            curr_song = {}
            title = tag.find('h3', id='title-of-a-story').text.strip()
            artist = tag.find('span').text.strip()
            curr_song[i] = (title, artist)
            top_100_song_lst.append(curr_song)
            i += 1
    return top_100_song_lst

def top_100_into_database(lst, cur, conn):
    #Takes in top 100 list and creates table in database 25 items at a time
    cur.execute("CREATE TABLE IF NOT EXISTS Billboard (song_id INTEGER PRIMARY KEY, song_title TEXT, artist TEXT)")
    cur.execute("SELECT song_id FROM Billboard WHERE song_id = (SELECT MAX(song_id) FROM Billboard)")
    curr_spot = cur.fetchone()
    if curr_spot[0] == None:
        count = 1
    else:
        count = curr_spot[0] + 1
    for item in lst[count - 1:count + 24]:
        cur.execute("INSERT INTO Billboard (song_id, song_title, artist) VALUES (?, ?, ?)", (count, item[count][0], item[count][1]))
        count += 1
    conn.commit()


def main():
    cur, conn = setUpDatabase("final.db")
    song_list = get_top_100_billboard()
    #Puts 25 songs into database, run in total 4 times to get 100 songs
    top_100_into_database(song_list, cur, conn)


if __name__ == "__main__":
    main()