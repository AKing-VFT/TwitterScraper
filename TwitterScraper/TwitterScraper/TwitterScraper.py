'''
Created on Mar 31, 2016

@author: Andrew
'''

from TwitterConstants import *
from pymongo.mongo_client import MongoClient
from selenium import webdriver
from urllib import quote_plus
from time import strftime
import datetime

class TwitterScraper():
    '''
    Class for scraping Tweets off of Twitter website
    '''


    def __init__(self, host="localhost", port=27017, db=TWEET_DB, collection=TWEET_COLLECTION):
        '''
        Constructor
        '''
        self.driver = webdriver.Firefox()
        self.client = MongoClient(host, port)
        self.db = self.client[db]
        self.collection = self.db[collection]
    
    def scrapeByDay(self, query, qDate, endDate=None, count=0, maxCount=10000):
        if endDate and qDate < endDate:
            #We have reached our max date
            return None
        
        dateStr = strftime("%Y-%m-%d")
        queryStr = "q={}%20since:{}%20until:{}".format(quote_plus(query), dateStr, dateStr)
        url = "&".join([TWITTER_SEARCH, queryStr])
        
        self.driver.get(url)
    
    def findTweets(self, soup):
        tweetsSoup = soup.find_elements_by_class_name(CLASS_JS_STREAM_ITEM)
    
    def scrapeTweet(self,tweetDriver):
        tweet = {}
        tweet[TWEET_TEXT] = tweetDriver.find_element_by_class_name(CLASS_JS_TWEET_TEXT).text
        tweet[TWEET_DATE] = datetime.datetime.strptime(tweetDriver.find_element_by_class_name(CLASS_TWEET_TIMESTAMP).get_attribute(ATTR_TITLE), TWITTER_DATE_FORMAT)
        tweet[TWEET_ID] = tweetDriver.get_attribute[ATTR_ITEM_ID]
        
        return tweet

    def scrapeTweets(self, soup, maxTweets=None, startDate=None, endDate=None ):
        tweets = []
        count = 0
        tweetsSoup = self.findTweets(soup)
        
        for tweetSoup in tweetsSoup:
            tweet = self.scrapeTweet(tweetSoup)
            
            if ((startDate and (tweet["date"] < startDate)) #If the tweet is before the start date
                or (endDate and (tweet["date"] > endDate))):#or if the tweet is after the endDate
                continue #don't process this tweet. Move to the next tweet
            
            if (maxTweets and (count > maxTweets)): #if we've hit the maximum tweet number
                break #don't process this tweet. Exit the loop
            
            tweets.append(tweet)

if __name__ == "__main__":
    print "test"
    scraper = TwitterScraper(collection="Understatement")
    
    today = datetime.datetime.today()
    
    scraper.scrapeByDay("#understatement", today)
    