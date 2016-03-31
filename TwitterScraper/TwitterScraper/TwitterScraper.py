'''
Created on Mar 31, 2016

@author: Andrew
'''

from TwitterConstants import *
from pymongo.mongo_client import MongoClient
from selenium import webdriver
from urllib import quote_plus
from time import sleep
import datetime
from selenium.common.exceptions import NoSuchElementException

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
    
    
    def scrapePage(self, url, startDate=None, endDate=None, count=0, maxCount=10000):
        """
        Method for scraping all tweets from the page specified by url
        
        @param url: the URL to be scraped
        @type url: str
        @param startDate: Beginning of the date range, UTC. Value is inclusive
        @type startDate: datetime.datetime
        @param endDate: End of date range, UTC. Value is exclusive
        @type endDate: datetime.datetime
        @param count: the number of tweets already scraped. Used for querying one day at a time
        @type count: int
        @param maxCount: the maximum number of tweets we wish to scrape
        @type maxCount: int
        
        @return the number of tweets inserted into the database
        @rtype int
        """
        
        #Load the URL in a firefox browser
        #TODO: user-specified browser
        driver = webdriver.Firefox()
        driver.get(url)
        
        sleep(3) #let the page load
        
        #load all tweets
        self.scrollToBottom(driver)
        
        return self.scrapeTweets(driver)
    
    def scrapeQuery(self, queryStr, startDate=None, endDate=None, maxCount=10000):
        """
        Method for scraping all tweets that match a specific query, optionally within a specific date range
        
        @param queryStr: the string to be queried for
        @type queryStr: str
        @param startDate: Beginning of the date range, UTC. Value is inclusive
        @type startDate: datetime.datetime
        @param endDate: End of date range, UTC. Value is exclusive
        @type endDate: datetime.datetime
        @param maxCount: the maximum number of tweets we wish to scrape
        @type maxCount: int
        
        @return the number of tweets inserted into the database
        @rtype int
        """
        
        #Scraping tweets in one day increments is more robust and avoids slowdowns when loading large numbers of tweets
        oneDay = datetime.timedelta(days=1)
        searchDateEnd = endDate
        if searchDateEnd == None:
            #No end date specified
            #Set endDate to tomorrow's date (since endDate is exclusive)
            searchDateEnd = datetime.datetime.today() + oneDay
        searchDateStart = searchDateEnd - oneDay
        
        count = 0 #this will count the number of tweets we've submitted to the database. Start at 0
        
        while(((startDate == None) or (startDate and (startDate <= searchDateStart)))
              and (count <= maxCount)):
            #If there's a startDate, we don't want to search before it
            #We also don't want to keep searching if we've hit max count
            
            #TODO: this will cause errors if maxCount is None
            #TODO: if there's no startDate AND no maxCount this will look forever
            
            #Scrape tweets for the specified day
            dayCount = self.scrapeQueryByDateRange(queryStr, searchDateStart, searchDateEnd, count, maxCount)
            count += dayCount #update count
            #move the search window back one day
            searchDateEnd = searchDateStart
            searchDateStart = searchDateStart - oneDay
        
        return count
        
        
        
    
    def scrapeQueryByDateRange(self, queryStr, startDate, endDate, count=0, maxCount=10000):
        """
        Method for scraping all tweets on a specific day
        
        @param queryStr: the string to be queried for
        @type queryStr: str
        @param startDate: Beginning of the date range, UTC. Value is inclusive
        @type startDate: datetime.datetime
        @param endDate: End of date range, UTC. Value is exclusive
        @type endDate: datetime.datetime
        @param count: the number of tweets already scraped. Used for querying one day at a time
        @type count: int
        @param maxCount: the maximum nuber of tweets we wish to scrape. Used for recursively querying one day at a time
        @type maxCount: int
        
        @return the number of tweets inserted into the database
        @rtype int
        """
        
        #Twitter web search requires a gap of at least 1 day
        sinceStr = startDate.strftime("%Y-%m-%d")
        untilStr = endDate.strftime("%Y-%m-%d")
        queryStr = "q={}%20since:{}%20until:{}".format(quote_plus(queryStr), sinceStr, untilStr)
        url = "&".join([TWITTER_SEARCH, queryStr])
        
        return self.scrapePage(url, startDate, endDate, count, maxCount)
    
    def findTweets(self, driver):
        return driver.find_elements_by_class_name(CLASS_JS_STREAM_ITEM)
    
    def scrapeTweet(self,tweetDriver):
        tweet = {}
        tweet[TWEET_TEXT] = tweetDriver.find_element_by_class_name(CLASS_JS_TWEET_TEXT).text
        tweet[TWEET_DATE] = datetime.datetime.strptime(tweetDriver.find_element_by_class_name(CLASS_TWEET_TIMESTAMP).get_attribute(ATTR_TITLE), TWITTER_DATE_FORMAT)
        tweet[TWEET_ID] = tweetDriver.get_attribute[ATTR_ITEM_ID]
        
        return tweet

    def scrapeTweets(self, driver, startDate=None, endDate=None, count=0, maxTweets=None):
        """
        Method for scraping tweets from HTML
        
        @param driver: webdriver of the page containing tweets
        @type url: selenium.webdriver
        @param startDate: Beginning of the date range, UTC. Value is inclusive
        @type startDate: datetime.datetime
        @param endDate: End of date range, UTC. Value is exclusive
        @type endDate: datetime.datetime
        @param count: the number of tweets already scraped. Used for querying one day at a time
        @type count: int
        @param maxCount: the maximum number of tweets we wish to scrape
        @type maxCount: int
        
        @return the number of tweets inserted into the database
        @rtype int
        """
        #TODO: Insert into DB
        #TODO: Return count

        tweetDrivers = self.findTweets(driver)
        
        for tweetDriver in tweetDrivers:
            tweet = self.scrapeTweet(tweetDriver)
            
            if ((startDate and (tweet[TWEET_DATE] < startDate)) #If the tweet is before the start date
                or (endDate and (tweet[TWEET_DATE] >= endDate))):#or if the tweet is after the endDate
                continue #don't process this tweet. Move to the next tweet
            
            #place the tweet in the DB
            tweets.append(tweet)
            count +=1 #update count
            
            if (maxTweets and (count > maxTweets)): #if we've hit the maximum tweet number
                break #don't process this tweet. Exit the loop

    def scrollToBottom(self, driver):
        """
        Method for scrolling webpage to bottom to load all tweets. Note that this method can take a very long time if there are a lot of query results
        
        @param driver: A driver for the webpage to be scrolled
        @type driver: selenium.webdriver
        """
        while True:
            #Scroll down to load more tweets
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1) #let tweets load
            
            #check for error
            tryAgain = driver.find_element_by_class_name(CLASS_TRY_AGAIN)
            if tryAgain.is_visible():
                #TODO: Should we deal with cases where TryAgain is deactivated between checking visibility and clicking it?
                #The try again button is visible
                tryAgain.click() #click it
                sleep(5) #let page load
            
            #check to see if there are more tweets to load
            try:
                driver.find_element_by_class_name(CLASS_HAS_MORE_ITEMS)
            except NoSuchElementException:
                #"Has More Items" not found
                #This may mean we've loaded all tweets or it could be a mistake
                #spam "scroll down"
                for x in xrange(10):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    sleep(0.5)
                   
                sleep(5) #let page finish loading
                #check again 
                try:
                    driver.find_element_by_class_name(CLASS_HAS_MORE_ITEMS)
                except NoSuchElementException:
                    #Still can't find "Has More Items". Probably legitimate
                    break #exit the loop
                
if __name__ == "__main__":
    print "test"
    scraper = TwitterScraper(collection="Understatement")
    
    today = datetime.datetime.today()
    
    scraper.scrapeByDay("#understatement", today)
    