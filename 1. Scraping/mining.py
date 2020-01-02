# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 22:00:10 2019

@author: arun_
"""

from bs4 import BeautifulSoup
import pandas as pd

files = ['script_1819', 'script_1718', 'script_1617', 'script_1516', 'script_1415']

data = []

for url_no in range(len(files)):
    
    file_name = files[url_no] + '.txt'
    f = open(file_name, "r")
    
    season = files[url_no][-4:-2] + '-' + files[url_no][-2:]
    page_content = f.read()
    
    soup = BeautifulSoup(page_content, 'html.parser')
    
    
    fixtures = soup.find_all('section', class_='fixtures')[0]
    
    fix_list = fixtures.find_all('span', class_='overview')
    
    for match in fix_list:
        [home, away] = match.find_all('span', class_='team')
        home_team = home.find(class_="shortname").get_text()
        away_team = away.find(class_="shortname").get_text()
        score = match.find_all('span', class_='score')[0].get_text()
        home_goals, away_goals = score.split('-')
        data.append([home_team, away_team, home_goals, away_goals, season])

    f.close()
    
df = pd.DataFrame(data, columns = ['Home Team', 'Away Team', 'Goals Scored', 'Goals Conceded', 'Season']) 

df.to_csv('FPL_Raw_Data.csv', index=False)
