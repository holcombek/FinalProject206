import sqlite3
import os
import requests
from bs4 import BeautifulSoup

# This file gets the top 100 songs from Billboard Hot 100 and puts them into a database
# No visualisations done for this data

def setUpDatabase(db_name):
    '''
    Takes in database name; returns cursor and connection objects.
    Used in main to set up database.
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_top_100_billboard():
    '''
    Takes in nothing; returns list of dictionaries with song rank
     as key and song title, artist as values
     for each week of Billboard Hot 100 songs.
    Scrapes Billboard Hot 100 websites of last four weeks
     for song data using Beautiful Soup objects.
    '''
    # end dates of each week we are looking at
    week_lst = ['2022-03-26', '2022-04-02', '2022-04-09', '2022-04-16']
    last_4_wk_top_100 = []
    for w in range(4):
        url = "https://www.billboard.com/charts/hot-100/" + week_lst[w] + '/'
    # using BeautifulSoup object to parse website for song title and artist name
        r = requests.get(url)
        if r.ok:
            top_100_song_lst = []
            soup = BeautifulSoup(r.content, 'html.parser')
            top = soup.find_all('ul', class_="lrv-a-unstyle-list lrv-u-flex lrv-u-height-100p lrv-u-flex-direction-column@mobile-max")
            i = 1
            # looping through found tags to get song title and artist
            for tag in top:
                curr_song = {}
                title = tag.find('h3', id='title-of-a-story').text.strip()
                artist = tag.find('span').text.strip()
                curr_song[i] = (title, artist)
                top_100_song_lst.append(curr_song)
                i += 1
        last_4_wk_top_100.append(top_100_song_lst)
    return last_4_wk_top_100

def top_100_into_database(billboard_lst, table_name, cur, conn):
    '''
    Takes in list returned from get_top_100_billboard(), table name, 
     cursor, and connection; returns nothing.
    Creates table in database for given week of Billboard data and
     adds song information 25 items at a time.
    '''
    cur.execute("CREATE TABLE IF NOT EXISTS "+ table_name + "(song_id INTEGER PRIMARY KEY, song_title TEXT, artist TEXT)")
    cur.execute("SELECT song_id FROM " + table_name + "WHERE song_id = (SELECT MAX(song_id) FROM " + table_name + ")")
    # getting current spot in table on database
    curr_spot = cur.fetchone()
    if curr_spot == None:
        count = 1
    else:
        count = curr_spot[0] + 1
    for item in billboard_lst[count - 1:count + 24]:
        cur.execute("INSERT INTO " + table_name + "(song_id, song_title, artist) VALUES (?, ?, ?)", (count, item[count][0].lower().strip().replace("(", "").replace("'","").replace('-', "").replace(")", "").replace(" ", ""), item[count][1]))
        count += 1
    conn.commit()


def main():
    '''
    Main function of file.
    Sets up database and sets up list of dictionaries with song info.
    Adds song information for each week to corresponding table
     25 items at a time (for each of the four weeks).
    '''
    cur, conn = setUpDatabase("final.db")
    # holds last 4 weeks (1 being most recent)
    weeks_100_list = get_top_100_billboard()
    # puts 25 songs into database for each week, run in total 4 times to get 100 songs
    for i in range(4):
        top_100_into_database(weeks_100_list[i], f'Billboard_week_{i+1} ', cur, conn)


if __name__ == "__main__":
    main()