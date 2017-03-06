'''
Created on Mar 31, 2016

@author: Andrew
'''

from TwitterWebScraper.TwitterConstants import *
from pymongo.mongo_client import MongoClient
from selenium import webdriver
from urllib import quote_plus
from time import sleep, time
import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

TWITTER_LAUNCH_DATE = datetime.datetime(2006, 3, 20)
    
class TwitterScraper():
    '''
    Class for scraping Tweets off of Twitter website
    '''
    


    def __init__(self, host="localhost", port=27017, db=TWEET_DB, collection=TWEET_COLLECTION):
        '''
        Constructor
        '''
        self.client = MongoClient(host, port)
        self.db = self.client[db]
        self.collection = self.db[collection]
    
    
    def scrapePage(self, url, startDate=None, endDate=None, count=0, maxCount=10000, timeout=None):
        """
        Method for scraping all tweets from the page specified by url
        
        @param url: the URL to be scraped
        @type url: str
        @param startDate: Beginning of the date range, UTC. Value is inclusive
        @type startDate: datetime.date
        @param endDate: End of date range, UTC. Value is exclusive
        @type endDate: datetime.date
        @param count: the number of tweets already scraped. Used for querying one day at a time
        @type count: int
        @param maxCount: the maximum number of tweets we wish to scrape
        @type maxCount: int
        @param timeout: the number of seconds until scrolling should timeout. None means no timeout
        @type timeout: int
        
        @return the number of tweets inserted into the database
        @rtype int
        """
        
        driver = None
        try:
            #Load the URL in a firefox browser
            #TODO: user-specified browser
#             driver = webdriver.Firefox()
            driver = webdriver.Chrome("C:/chromedriver.exe")
            driver.get(url)
            
            sleep(3) #let the page load
            
            #load all tweets
            self.scrollToBottom(driver, timeout)
            print "scrolling finished"
            
            return self.scrapeTweets(driver, startDate, endDate, count, maxCount)
        finally:
            if driver:
                driver.quit()
                sleep(1) #TODO: to avoid threading issues, maybe?
    
    def scrapeQuery(self, queryStr, startDate=None, endDate=None, maxCount=10000, lang="en", rangeDays=5, timeout=None):
        """
        Method for scraping all tweets that match a specific query, optionally within a specific date range
        
        @param queryStr: the string to be queried for
        @type queryStr: str
        @param startDate: Beginning of the date range, UTC. Value is inclusive
        @type startDate: datetime.date
        @param endDate: End of date range, UTC. Value is exclusive
        @type endDate: datetime.date
        @param maxCount: the maximum number of tweets we wish to scrape
        @type maxCount: int
        @param lang: Used to filter by tweet language
        @type lang: str
        @param rangeDays: The number of days of tweets to load at one time. Used for tuning loading efficiency.
        @type rangeDays: int
        @param timeout: the number of seconds until scrolling should timeout. None means no timeout
        @type timeout: int
        
        @return the number of tweets inserted into the database
        @rtype int
        """
        
        #Scraping tweets in one day increments is more robust and avoids slowdowns when loading large numbers of tweets
        rangeDelta = datetime.timedelta(days=rangeDays)
        searchDateEnd = endDate
        if searchDateEnd == None:
            #No end date specified
            #Set endDate to tomorrow's date (since endDate is exclusive)
            searchDateEnd = datetime.datetime.today() + datetime.timedelta(days=1)
        searchDateStart = searchDateEnd - rangeDelta
        
        if startDate == None:
            #if user doesn't specify a startDate, set it to the launch of twitter to avoid infinite loops
            startDate = TWITTER_LAUNCH_DATE
        
        count = 0 #this will count the number of tweets we've submitted to the database. Start at 0
        
        while((startDate <= searchDateStart) and ((maxCount == None) or count < maxCount)):
            #If there's a startDate, we don't want to search before it
            #We also don't want to keep searching if we've hit max count
            
            #Scrape tweets for the specified day and update the count
            count = self.scrapeQueryByDateRange(queryStr, searchDateStart, searchDateEnd, count, maxCount, lang, timeout)
            #move the search window back one day
            searchDateEnd = searchDateStart
            searchDateStart = searchDateStart - rangeDelta
        
        return count
        
        
        
    
    def scrapeQueryByDateRange(self, queryStr, startDate, endDate, count=0, maxCount=10000, lang="en", timeout=None):
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
        @param lang: Used to filter by tweet language
        @type lang: str
        @param timeout: the number of seconds until scrolling should timeout. None means no timeout
        @type timeout: int
        
        @return the number of tweets inserted into the database
        @rtype int
        """
        
        #TODO: start and endDate are UTC, scraped timestamp is local time
        
        #Twitter web search requires a gap of at least 1 day
        sinceStr = startDate.strftime("%Y-%m-%d")
        untilStr = endDate.strftime("%Y-%m-%d")
        #TODO: maybe do a list implementation so you only call join once?
        queryStr = "q={}%20since:{}%20until:{}".format(quote_plus(queryStr), sinceStr, untilStr)
        if lang:
            queryStr = "%20".join([queryStr, "lang%3A{}".format(lang)])
        url = "&".join([TWITTER_SEARCH, queryStr])
        
        #TODO: remove
        print "Scraping Tweets for {}".format(sinceStr)
        
        #TODO: readd date ranges to scrapepage once we decide how ot deal with the UTC vs local time issue
#         return self.scrapePage(url, startDate, endDate, count, maxCount)
        return self.scrapePage(url, count=count, maxCount=maxCount, timeout=timeout)
    
    def findTweets(self, driver):
        """
        Method for finding all tweets on the page specified by driver
        
        @param driver: webdriver of the page to be searched for tweets
        @type driver: selenium.webdriver
        
        @return list of drivers pointing to all tweets on the specified page
        @rtype [selenium.webdriver]
        """
        return driver.find_elements_by_class_name(CLASS_JS_ORIGINAL_TWEET)
    
    def scrapeTweet(self,tweetDriver):
        tweet = {}
        tweet[TWEET_TEXT] = tweetDriver.find_element_by_class_name(CLASS_JS_TWEET_TEXT).text
        tweet[TWEET_DATE] = datetime.datetime.strptime(tweetDriver.find_element_by_class_name(CLASS_TWEET_TIMESTAMP).get_attribute(ATTR_TITLE), TWITTER_DATE_FORMAT)
        tweet[TWEET_ID] = tweetDriver.get_attribute(ATTR_ITEM_ID)
        tweet[TWEET_USER_ID] = tweetDriver.get_attribute(ATTR_USER_ID)
        tweet[TWEET_SCREEN_NAME] = tweetDriver.get_attribute(ATTR_SCREEN_NAME)
        tweet[TWEET_NAME] = tweetDriver.get_attribute(ATTR_NAME)
        tweet[TWEET_MENTIONS] = tweetDriver.get_attribute(ATTR_MENTIONS)
        tweet[TWEET_RETWEET_COUNT] = self.getActionCount(tweetDriver.find_element_by_class_name(CLASS_RETWEET))
        tweet[TWEET_FAVORITE_COUNT] = self.getActionCount(tweetDriver.find_element_by_class_name(CLASS_FAVORITE))
        
        return tweet

    def scrapeTweets(self, driver, startDate=None, endDate=None, count=0, maxCount=None):
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
        
        for tweetDriver in self.findTweets(driver):            
            #TODO: more nuanced handling of special tweets
            if (self.isLink(tweetDriver) or self.isMultimedia(tweetDriver) or self.isPeriscope(tweetDriver)
                or self.isRetweet(tweetDriver) or self.isReply(tweetDriver) or self.isQuote(tweetDriver)):
                #These tweets are not self contained. Easiest to just filter them out
                continue
            
            tweet = self.scrapeTweet(tweetDriver)
            
            #TODO: search API is in UTC. Scraped timestamp is local time
            if ((startDate and (tweet[TWEET_DATE] < startDate)) #If the tweet is before the start date
                or (endDate and (tweet[TWEET_DATE] >= endDate))):#or if the tweet is after the endDate
                continue #don't process this tweet. Move to the next tweet
            
            #place the tweet in the DB
            self.collection.insert_one(tweet)
            count +=1 #update count
            
            if (maxCount and (count > maxCount)): #if we've hit the maximum tweet number
                break #don't process this tweet. Exit the loop
        
        #TODO: remove
        print "{} tweets scraped".format(count)
        
        return count

    def scrollToBottom(self, driver, timeout=None):
        """
        Method for scrolling webpage to bottom to load all tweets. Note that this method can take a very long time if there are a lot of query results
        
        @param driver: A driver for the webpage to be scrolled
        @type driver: selenium.webdriver
        @param timeout: the number of seconds until scrolling should timeout. None means no timeout
        @type timeout: int
        """
        
        if timeout:
            startTime = time()
        
        ac = ActionChains(driver)
        ac = ac.send_keys(Keys.PAGE_DOWN)
        
        scrollPosition = 0 #hold the Y value of the scroll bar
        while True:
            ac.perform() #press PageDown
            sleep(1) #wait for page to load
             
#             newScrollPosition = driver.execute_script("return window.scrollY;");
#              
#             if newScrollPosition == scrollPosition: #If there was no change in scroll bar position
#                 #If the scroll bar didn't move it might mean we've loaded all the tweets or it could mean something went wrong
#                 
#                 sleep(3) #give extra time to load
#                 
#                 #Try scrolling down more to see if it loads more tweets
#                 for _ in xrange(5): #press PageDown 5 more times
#                     ac.perform() #press PageDown
#                     sleep(1) #wait for page to load
#                     
#                 #check for error message
#                 try:
#                     tryAgain = driver.find_element_by_class_name(CLASS_TRY_AGAIN)
#                     if tryAgain.is_displayed():
#                         #TODO: Should we deal with cases where TryAgain is deactivated between checking visibility and clicking it?
#                         #The try again button is visible
#                         tryAgain.click() #click it
#                         sleep(5) #let page load
#                 except NoSuchElementException:
#                     #for some reason "Try again" hasn't loaded.
#                     pass
#                 
#                 #one last hail mary scroll
#                 ac.perform()
#                  
#                 #update srroll position
#                 newScrollPosition = driver.execute_script("return window.scrollY;");
#                  
#                 if scrollPosition == newScrollPosition:
#                     #If the scroll position still has't changed then we're probably at the end of the page
#                     break #exit the loop
#                    
# #             #TODO: Remove old page end verification
# #             #check to see if there are more tweets to load
# #             try:
# #                 driver.find_element_by_class_name(CLASS_HAS_MORE_ITEMS)
# #             except NoSuchElementException:
# #                 #"Has More Items" not found
# #                 #This may mean we've loaded all tweets or it could be a mistake
# #                 #spam "scroll down"
# #                 for x in xrange(5):
# #                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# #                     sleep(0.5)
# #                     
# #                 sleep(5) #let page finish loading
# #                 #check again 
# #                 try:
# #                     driver.find_element_by_class_name(CLASS_HAS_MORE_ITEMS)
# #                 except NoSuchElementException:
# #                     #Still can't find "Has More Items". Probably legitimate
# #                     break #exit the loop
#  
#             #update the value of scrollPosition
#             scrollPosition = newScrollPosition
            
            #check for timeout
            if timeout:
                if ((time() - startTime) > timeout):
                    #we've exceeded the timeout
                    break
        
    def isQuote(self,tweetDriver):
        """
        Method for determining if a tweet contains a quoted tweet
        
        @param tweetDriver: webdriver for the tweet to be checked
        @type tweetDriver: selenium.webdriver
        
        @return boolean representing whether the tweet contains a quoted tweet
        @rtype bool
        """
        try:
            tweetDriver.find_element_by_class_name(CLASS_QUOTE_TWEET)
            #Quote container found
            return True
        except NoSuchElementException:
            #No quote container found
            return False
    
    def isLink(self,tweetDriver):
        """
        Method for determining if a tweet contains a URL
        
        @param tweetDriver: webdriver for the tweet to be checked
        @type tweetDriver: selenium.webdriver
        
        @return boolean representing whether the tweet contains a URL
        @rtype bool
        """
        try:
            tweetDriver.find_element_by_class_name(CLASS_TIMELINE_LINK)
            #link found
            return True
        except NoSuchElementException:
            #No link found
            return False
    
    def isRetweet(self,tweetDriver):
        """
        Method for determining if a tweet is a retweet
        
        @param tweetDriver: webdriver for the tweet to be checked
        @type tweetDriver: selenium.webdriver
        
        @return boolean representing whether the tweet is a retweet
        @rtype bool
        """
        retweeterID = tweetDriver.get_attribute(ATTR_RETWEETER)
        #if such attribute exists, tweet is a retweet
        return retweeterID != None
    
    def isReply(self,tweetDriver):
        """
        Method for determining if a tweet is a reply
        
        @param tweetDriver: webdriver for the tweet to be checked
        @type tweetDriver: selenium.webdriver
        
        @return boolean representing whether the tweet is a reply
        @rtype bool
        """
        reply = tweetDriver.get_attribute(ATTR_IS_REPLY_TO)
        #if such attribute exists, tweet is a reply
        return reply != None
    
    def isMultimedia(self,tweetDriver):
        """
        Method for determining if a tweet contains a photo or video
        
        @param tweetDriver: webdriver for the tweet to be checked
        @type tweetDriver: selenium.webdriver
        
        @return boolean representing whether the tweet contains a photo or video
        @rtype bool
        """
        try:
            tweetDriver.find_element_by_class_name(CLASS_ADAPTIVE_MEDIA)
            #Quote container found
            return True
        except NoSuchElementException:
            #No quote container found
            return False
    
    def isPeriscope(self,tweetDriver):
        """
        Method for determining if a tweet contains a periscope video
        
        @param tweetDriver: webdriver for the tweet to be checked
        @type tweetDriver: selenium.webdriver
        
        @return boolean representing whether the tweet contains a periscope video
        @rtype bool
        """
        try:
            tweetDriver.find_element_by_class_name(CLASS_MEDIA_CONTAINER)
            #Quote container found
            return True
        except NoSuchElementException:
            #No quote container found
            return False
    
    def getActionCount(self, driver):
        """
        Method for getting the retweet/favorite count contained in driver
        
        @param driver: webdriver to be checked. Should be either CLASS_RETWEET or CLASS_FAVORITE
        @type driver: selenium.webdriver
        
        @return The count as an integer
        @rtype int
        """
        countStr = driver.find_element_by_class_name(CLASS_ACTION_COUNT).get_attribute(ATTR_STAT_COUNT)
        
        if not countStr: #if the string is empty
            countStr = "0"
        
        return int(countStr)
    
if __name__ == "__main__":
    scraper = TwitterScraper(collection="OlympicSongs")
    
#     minDates = []
#     minDates.append(scraper.db.sarcasm.find_one(sort=[(TWEET_DATE, 1)])[TWEET_DATE])
#     minDates.append(scraper.db.hyperbole.find_one(sort=[(TWEET_DATE, 1)])[TWEET_DATE])
#     minDates.append(scraper.db.understatement.find_one(sort=[(TWEET_DATE, 1)])[TWEET_DATE])
#     minDate = min(minDates)
     
#     maxDate = scraper.collection.find_one(sort=[(TWEET_DATE, 1)])[TWEET_DATE]
#     minDate = scraper.collection.find_one(sort=[(TWEET_DATE, DESCENDING)])[TWEET_DATE]
#     oneDay = datetime.timedelta(days=1)
#     startDate = minDate
#     startDate = None
#     endDate = maxDate+oneDay
#     endDate = None
    startDate = datetime.datetime(2016, 8, 9)
    endDate = datetime.datetime(2016, 8, 10)
    
    print scraper.scrapeQuery("#olympicsongs", startDate=startDate, endDate=endDate, rangeDays=1, maxCount=None, timeout=14400)
    