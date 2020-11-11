from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import os
import requests
import re
from urllib.request import urlopen
from urllib import request
import json
import shutil
import sys
from pandas.io.json import json_normalize
import pandas as pd, numpy as np


username= input('Input instagram username : ')
browser = webdriver.Chrome('E:/Downloads/chromedriver_win32/chromedriver')
browser.get('https://www.instagram.com/'+username+'/?hl=en')
# browser = requests.get('https://www.instagram.com/'+username+'/?hl=en')
Pagelength = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")


#Extract links from user profile page
links=[]
# source = browser.text
source = browser.page_source
data=bs(source, 'html.parser')
body = data.find('body')
script = str(body.find('script', text=lambda t: t.startswith('window._sharedData')))
page_json = script.split(' = ', 1)[1].rstrip(';</script>')
data = json.loads(page_json)

# Check account is exists
if 'HttpErrorPage' in data['entry_data'].keys():
    print('Instagram account not found')
    sys.exit()

account_private = data['entry_data']['ProfilePage'][0]['graphql']['user']['is_private']

if account_private == True:
    print("Make sure account isn't private")
    sys.exit()

# #try 'script.string' instead of script.text if you get error on index out of range
# for link in data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
#     links.append('https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/')
#try with ['display_url'] instead of ['shortcode'] if you don't get links 
#Extract links from hashtag page
links=[]
# source = browser.page_source
# data=bs(source, 'html.parser')
# body = data.find('body')
# script = str(body.find('script', text=lambda t: t.startswith('window._sharedData')))
# page_json = script.split(' = ', 1)[1].rstrip(';</script>')
# data_post = json.loads(page_json)
for link in data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
    links.append('https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/')


print(links)
print(len(links))
sys.exit()
# result=pd.DataFrame()
path = "S:/scraper-instagram/"
for i in range(2):
    try:
        page = requests.get(links[i]).text
        data=bs(page, 'html.parser')
        body = data.find('body')
        script = str(body.find('script'))
        raw = script.split(' = ', 1)[1].strip().replace('window._sharedData =', '').replace(';</script>', '')
        json_data=json.loads(raw)

        posts  = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        # posts= json.dumps(posts)
        # posts = json.loads(posts))

        # Making Folder of Feed
        folder_name = posts['shortcode']
        
        # print(os.path.isdir((path+folder_name)))
        # Check folder is exists?
        check_folder = os.path.isdir(path+folder_name)
        
        if check_folder == True:
            shutil.rmtree(path+folder_name)
            # os.rmdir(path+folder_name)
            os.mkdir(path+folder_name)
        else:
            os.mkdir(path+folder_name)

        # Insert Display Media to Folder Feed
        r = requests.get(posts['display_url'])
        with open(path+folder_name+"/"+posts['shortcode']+".jpg", 'wb') as f:
            f.write(r.content)             

        if 'edge_sidecar_to_children' in posts.keys():
            # Insert Pther Media to Folder Feed
            json_other_media = json.dumps(posts['edge_sidecar_to_children']['edges'])
            json_other_media = json.loads(json_other_media)

            # shutil.rmtree(path+folder_name)
            for other_media in json_other_media:
                detail = other_media['node']
                s = requests.get(detail['display_url'])
                with open(path+folder_name+"/"+detail['shortcode']+".jpg", 'wb') as f:
                    f.write(s.content)    

            if os.path.exists(path+folder_name+'/'+folder_name+'.jpg'):
                os.remove(path+folder_name+'/'+folder_name+'.jpg')
                   

        # Insert Caption Feed to Folder
        caption_media = json.dumps(posts['edge_media_to_caption']['edges'])
        caption_media = json.loads(caption_media)
        caption_media = caption_media[0]['node']['text']

        write_caption = open(path+folder_name+"/"+"caption.txt", 'w', encoding='utf-8')
        write_caption.write(str(caption_media))         
        
    except AssertionError as error:
        print(error)
        np.nan

# result = result.drop_duplicates(subset = 'shortcode')
# result.index = range(len(result.index))

# html = result.to_html()
# text_file = open("index1.html", "w")
# text_file.write(str(html.encode("utf-8")))
# text_file.close()