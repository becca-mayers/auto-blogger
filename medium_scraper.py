
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        NoSuchElementException, 
                                        WebDriverException,
                                        TimeoutException)
#from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from random import randint, choice
from selenium import webdriver
from time import sleep
import pandas as pd
import os
import re


def scroll_to_bottom(driver):
    return driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def scroll_100(driver):
    return driver.execute_script("window.scrollTo(0, window.scrollY + 100)")

def scroll_200(driver):
    return driver.execute_script("window.scrollTo(0, window.scrollY + 200)")

def scroll_300(driver):
    return driver.execute_script("window.scrollTo(0, window.scrollY + 300)")

def scroll_400(driver):
    return driver.execute_script("window.scrollTo(0, window.scrollY + 400)")


#%%
def get_titles_from_cards(cards):
    #PULLS TITLE DATA FROM EACH CARD IN CARDS, RETURNS A LIST OF TITLES
    def title_cleaner(title):
        #REMOVE MEDIUMS ENCODING SYMBOLS AND EMOJIS FROM TITLES
        title = title.replace('\xa0',' ')
        title = title.replace('\u200a','')
        title = title.replace('\ufe0f','')
        title = re.sub(r'[^\x00-\x7F]+','', title)
        return title

    titles = []
    for card in cards:
        #SEARCH FOR TITLE THERE ARE 3 DIFF CLASSES
        variant1 = card.find('h3', class_='graf graf--h3 graf-after--figure graf--title')
        variant2 = card.find('h3', class_='graf graf--h3 graf-after--figure graf--trailing graf--title')
        variant3 = card.find('h4', class_='graf graf--h4 graf--leading')
        variant4 = card.find('h3', class_='graf graf--h3 graf--leading graf--title')
        variant5 = card.find('p', class_='graf graf--p graf--leading')
        variant6 = card.find('h3', class_='graf graf--h3 graf--startsWithDoubleQuote graf--leading graf--title')
        variant7= card.find('h3', class_='graf graf--h3 graf--startsWithDoubleQuote graf-after--figure graf--trailing graf--title')
        #STYLING CODES
        variants = [variant1, variant2, variant3, variant4, variant5, variant6, variant7]
        saved = False
        #THE FIRST TITLE ENTRY WE MATCH, WE SAVE
        for variant in variants:
            if ((variant is not None) and (not saved)):
                title = variant.text
                title = title_cleaner(title)
                titles.append(title)
                saved = True
        if not saved:
            titles.append('NaN')
    return titles

#%%
def get_subtitles_from_cards(cards):

    def subtitle_cleaner(subtitle):
       
        subtitle = subtitle.replace('\xa0',' ')
        subtitle = subtitle.replace('\u200a','')
        subtitle = subtitle.replace('\ufe0f','')
        subtitle = re.sub(r'[^\x00-\x7F]+','', subtitle)
        return subtitle

    subtitles=[]
    for card in cards:
        variant1 = card.find('h4', class_='graf graf--h4 graf-after--h3 graf--subtitle')
        variant2 = card.find('h4', class_='graf graf--h4 graf-after--h3 graf--trailing graf--subtitle')
        variant3 = card.find('strong', class_='markup--strong markup--p-strong')
        variant4 = card.find('h4', class_='graf graf--p graf-after--h3 graf--trailing')
        variant5= card.find('p', class_='graf graf--p graf-after--h3 graf--trailing')
        variant6= card.find('blockquote', class_='graf graf--pullquote graf-after--figure graf--trailing')
        variant7 = card.find('p', class_='graf graf--p graf-after--figure')
        variant8 = card.find('blockquote', class_='graf graf--blockquote graf-after--h3 graf--trailing')
        variant9 = card.find('p', class_='graf graf--p graf-after--figure graf--trailing')
        variant10 = card.find('em', class_='markup--em markup--p-em')
        variant11=card.find('p', class_='graf graf--p graf-after--p graf--trailing')
        
        #Styling Codes
        variants = [variant1, variant2, variant3, variant4, variant5, variant6, variant7, variant8, variant9, variant10, variant11]
        saved = False
        for variant in variants:
            if ((variant is not None) and (not saved)):
                subtitle = variant.text
                subtitle = subtitle_cleaner(subtitle)
                subtitles.append(subtitle)
                saved = True
        if not saved:
            subtitles.append('NaN')
    return subtitles

#%%
def get_auth_and_pubs_from_cards(cards):

    authors = []
    pubs = []
    for card in cards:
        # get the author and publication
        author = card.find('a', class_='ds-link ds-link--styleSubtle link link--darken link--accent u-accentColor--textNormal u-accentColor--textDarken')
        pub = card.find('a', class_='ds-link ds-link--styleSubtle link--darken link--accent u-accentColor--textNormal')
        if author is not None:
            text = author.text
            text = re.sub('\s+[^A-Za-z]', '', text)
            text = re.sub(r'[^\x00-\x7F]+',' ', text)
            authors.append(text)
        else:
            authors.append('NaN')
        if pub is not None:
            text2 = pub.text
            text2 = re.sub('\s+[^A-Za-z]', '', text2)
            text2 = re.sub(r'[^\x00-\x7F]+',' ', text2)
            pubs.append(text2)
        else:
            pubs.append('NaN')
    return authors, pubs

#%%
def get_published_times(cards):

    pub_times = []
    for card in cards:
        written = card.find('p',
                             class_ = 'bm b bn bo cn')
        if written is not None:
            pub = written['span']
            pub_times.append(pub)
        else:
            pub_times.append('N/A')
    
    return pub_times

#%%
def get_readTime_from_cards(cards):

    reading_times = []
    for card in cards:
        time = card.find('span', class_ = 'readingTime')
        if time is not None:
            time = time['title']
            time = time.replace(' min read', '')
            reading_times.append(time)
        else:
            reading_times.append('0')
    return reading_times

#%%
def get_applause_from_cards(cards):

    applause = []
    for card in cards:
        claps=card.find('button', 
                        class_ = 'button button--chromeless u-baseColor--buttonNormal js-multirecommendCountButton u-disablePointerEvents')
        if claps is not None:
            applause.append(claps.text)
        else:
            applause.append('0')
    return applause

#%%
def get_comment_from_cards(cards):

    comments = []
    for card in cards:
        comment = card.find('div', 
                            class_ = 'u-fontSize14 u-marginTop10 u-marginBottom20 u-padding14 u-xs-padding12 u-borderRadius3 u-borderCardBackground u-borderLighterHover u-boxShadow1px4pxCardBorder')
        if comment is not None:
            comments.append(1)
        else:
            comments.append(0)
    return comments

#%%
def get_urls_from_cards(cards):

    urls = []
    for card in cards:
        url = card.find('a', class_ = '')
        if url is not None:
            urls.append(url['href'])
        else:
            raise Exception('couldn''t find a url')
    return urls

#%%
def get_auth_urls_from_cards(cards):
    
    auth_urls = []
    for card in cards:
        url = card.find('a', 
                        class_ = 'ds-link ds-link--styleSubtle link link--darken link--accent u-accentColor--textNormal u-accentColor--textDarken')
        if url is not None:
            auth_urls.append(url['href'])
        else:
            auth_urls.append('NaN')
    return auth_urls

#-----------------------------------------------------------------
#%% And, Begin!
def launch(tag, driver):   
   
    #Make base url
    url = 'https://medium.com/tag/' + tag

    driver.get(url)
    
    #Scroll as far down as possible wo getting flagged as a bot
    for w in range(20):
        choice([scroll_100(driver), 
                scroll_200(driver), 
                scroll_300(driver),
                scroll_400(driver)])
        
        sleep(randint(1,5))
        
    soup = bs(driver.page_source, 'lxml')

    cards = soup.find_all('div', class_='streamItem streamItem--postPreview js-streamItem')

    #Scrape deets
    titles = get_titles_from_cards(cards)
    subtitles = get_subtitles_from_cards(cards)
    authors, pubs = get_auth_and_pubs_from_cards(cards)
    published_times = get_published_times(cards)
    reading_times = get_readTime_from_cards(cards)
    applause = get_applause_from_cards(cards)
    urls = get_urls_from_cards(cards)
    auth_urls = get_auth_urls_from_cards(cards)
    comment = get_comment_from_cards(cards)

    #Build dict of scraped deets
    dict = {       'title': titles,
                'subtitle': subtitles,
                  'author': authors, 
             'publication': pubs, 
               'published': published_times, 
                     'tag': tag, 
            'reading_time': reading_times, 
                   'claps': applause,
                 'comment': comment, 
                     'url': urls, 
              'author_url': auth_urls}

    headers = ['title', 'subtitle', 'author', 'publication',
               'published', 'tag', 'reading_time', 'claps',
               'comment', 'url', 'author_url']
    
    # Make sure each col is the same length
    vals = list(dict.values())
    for col in vals:
        if len(col) == len(cards):
            continue
        else:
            raise Exception('Data length does not match number of stories on page.')

    #Create dataframe
    df = pd.DataFrame.from_dict(dict, headers = headers)

    print(df.head(2))
    
    #Export df
    csv_label = 'results/' + tag + '.csv'
    df.to_csv(csv_label, index = False)

    print(tag)
    
    sleep(randint(1,4))

#%% Tech
tech_tags = ['artificial-intelligence',
             'data-science',
             'programming',
             'software-development',
             'tech']

creativity_tags = ['creativity', 'design', 'ux',
                   #'storytelling','ux-design',
                   'writing']

marketing_tags = ['social-media-marketing',
                  'content-marketing',
                  'digital-marketing',
                  'marketing']

life_tags = ['self',
             'life',
             'life-lessons',
             'lifestyle',
             'mindfulness',
             'self-improvement',
             'psychology',
             'self-awareness']

business_tags = ['entrepreneurship', 'startup']

my_tags = [tech_tags, creativity_tags, life_tags, marketing_tags, business_tags]

#%% Launch browser

chrome_options = Options()
#chrome_options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

#launch medium home for 1-time manual login
#driver.get('https://www.medium.com')
#sleep(100)

for my_tag in my_tags:
    
    for tag in my_tag:
        
        print('Starting', tag, '.')
        launch(tag, driver)
        print('Done with', tag, '.')

driver.quit()
print('And, fini!')

