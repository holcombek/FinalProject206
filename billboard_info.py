import sqlite3
import os
import requests
from bs4 import BeautifulSoup

# This file gets the top 100 songs from Billboard Hot 100 and puts them into a database
# No visualisations done for this data (could look at one song and its placement over weeks)

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_top_100_billboard():
    #Looking at last 4 weeks of Billboard Top 100
    week_lst = ['2022-03-26', '2022-04-02', '2022-04-09', '2022-04-16']
    last_4_wk_top_100 = []
    for w in range(4):
        url = "https://www.billboard.com/charts/hot-100/" + week_lst[w] + '/'
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
        last_4_wk_top_100.append(top_100_song_lst)
    return last_4_wk_top_100

def top_100_into_database(lst, name, cur, conn):
    #Takes in last 4 weeks top 100 list and creates table in database 25 items at a time (for each lst)
    #rename billboard tables to match spotify
    #cur.execute('DROP TABLE IF EXISTS ' + name)
    cur.execute("CREATE TABLE IF NOT EXISTS "+ name + "(song_id INTEGER PRIMARY KEY, song_title TEXT, artist TEXT)")
    cur.execute("SELECT song_id FROM " + name + "WHERE song_id = (SELECT MAX(song_id) FROM " + name + ")")
    curr_spot = cur.fetchone()
    if curr_spot == None:
        count = 1
    else:
        count = curr_spot[0] + 1
    for item in lst[count - 1:count + 24]:
        cur.execute("INSERT INTO " + name + "(song_id, song_title, artist) VALUES (?, ?, ?)", (count, item[count][0].lower().strip().replace("(", "").replace("'","").replace('-', "").replace(")", "").replace(" ", ""), item[count][1]))
        count += 1
    conn.commit()


def main():
    cur, conn = setUpDatabase("final.db")
    #Holds last 4 weeks (1 being most recent)
    song_list = get_top_100_billboard()
    #Puts 25 songs into database for each week, run in total 4 times to get 100 songs
    for i in range(4):
        top_100_into_database(song_list[i], f'Billboard_week_{i+1} ', cur, conn)


if __name__ == "__main__":
    main()