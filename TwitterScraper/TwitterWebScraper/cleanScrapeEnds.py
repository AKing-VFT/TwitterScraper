'''
Created on Apr 14, 2016

@author: Andrew
'''
from TwitterWebScraper.TwitterScraper import TwitterScraper
import datetime
from TwitterWebScraper.TwitterConstants import TWEET_DATE


#to purpose of this script is to get the tweets we failed to load due to maxTweets

scraper = TwitterScraper(collection="understatement")
    
maxDate = scraper.collection.find_one(sort=[(TWEET_DATE, 1)])[TWEET_DATE]
oneDay = datetime.timedelta(days=1)
startDate = maxDate+oneDay
endDate = maxDate+oneDay+oneDay

print scraper.scrapeQuery("#understatement", startDate=startDate, endDate=endDate, rangeDays=1)