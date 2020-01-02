# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 19:42:47 2019

@author: arun_
"""

import time

from selenium import webdriver

url_1819 = 'https://www.premierleague.com/results?co=1&se=210&cl=-1'
url_1718 = 'https://www.premierleague.com/results?co=1&se=79&cl=-1'
url_1617 = 'https://www.premierleague.com/results?co=1&se=54&cl=-1'
url_1516 = 'https://www.premierleague.com/results?co=1&se=42&cl=-1'
url_1415 = 'https://www.premierleague.com/results?co=1&se=27&cl=-1'

seasons = [url_1819, url_1718, url_1617, url_1516, url_1415]
files = ['script_1819', 'script_1718', 'script_1617', 'script_1516', 'script_1415']

for url_no in range(len(seasons)):
    url = seasons[url_no]
    driver = webdriver.Firefox(executable_path = 'C:/Users/arun_/Documents/Gecko Driver/geckodriver.exe')
    driver.get(url)    
    for i in range(20):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
    content = driver.page_source
    driver.quit()
    file_name = files[url_no] + '.txt'
    f = open(file_name, "w")
    f.write(content)
    f.close()
