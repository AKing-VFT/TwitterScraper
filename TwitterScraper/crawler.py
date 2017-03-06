'''
Created on 2013-08-18

@author: Andrew
'''
import tweepy
from twitterCredentials import consumer_key, consumer_secret, access_key,\
    access_secret
from pymongo.mongo_client import MongoClient
from TwitterWebScraper.TwitterConstants import TWEET_TEXT, TWEET_DATE,\
    TWEET_FAVORITE_COUNT, TWEET_ID, TWEET_MENTIONS, TWEET_NAME,\
    TWEET_RETWEET_COUNT, TWEET_SCREEN_NAME, TWEET_USER_ID

class TwitterConnection():
    def __init__(self):
        self.auth=None
        self.api=None
    
    def getAPI(self):
        if not self.api:
            self.authenticateTwitter()
        return self.api
    
    def authenticateTwitter(self): 
        self.auth = tweepy.OAuthHandler(
            consumer_key,
            consumer_secret)
        self.auth.set_access_token(
            access_key,
            access_secret)
        self.api = tweepy.API(self.auth)
    
    def isReferential(self,tweet):
        try:
            tweet.retweeted_status
            return True
        except AttributeError:        
            pass
        
        try:
            tweet.quote_status_id_str
            return True
        except AttributeError:        
            pass
    
        return False
    
    #TODO: return tweepy.tweet objects?
    def searchTwitter(self, query, limit=30000):
        tweetCount=0
#         tweets = []
        
        for result in tweepy.Cursor(self.getAPI().search,
                                   q=query,
                                   count=100,
                                   lang="en").items():
            
            if self.isReferential(result):
                continue
            tweetCount += 1
#             tweets.append(tweet)
            tweet = {}
            tweet[TWEET_TEXT] = unicode(result.text)
            tweet[TWEET_DATE] = result.created_at
            tweet[TWEET_FAVORITE_COUNT] = result.favorite_count
            tweet[TWEET_ID] = result.id_str
            tweet[TWEET_RETWEET_COUNT] = result.retweet_count
            
            user = result.user
            tweet[TWEET_NAME] = user.name
            tweet[TWEET_SCREEN_NAME] = user.screen_name
            tweet[TWEET_USER_ID] = user.id_str
            
            tweet[TWEET_MENTIONS] = None
            entities = result.entities
            mentions = entities.get("user_mentions", None)
            if mentions:
                user_mentions = []
                for mention in mentions:
                    user_mentions.append(mention["screen_name"])
                tweet[TWEET_MENTIONS] = " ".join(user_mentions)
            
#             print tweet["text"]
            client.tweets.BasketballMovies.insert_one(tweet)
            
            #we only really want the first 2000
            if tweetCount >=limit:
                break
        
        print "{} tweets found for query \"{}\"".format(tweetCount, query)
#         return tweets

if __name__ == "__main__":
#    queriesTags = [("#understatement", "understatement"), ("#hyperbole OR #exaggeration OR #exaggerating", "hyperbole"), ("#rhetorical", "rhetorical"), ("#sarcasm OR #sarcastic", "sarcasm")]
    client = MongoClient()
    twitConn = TwitterConnection()
    
    results = twitConn.searchTwitter("#BasketballMovies")
#     for result in results:
#         tweet = {}
#         tweet[TWEET_TEXT] = tweet.text
#         tweet[TWEET_DATE] = tweet.created_at
#         tweet[TWEET_FAVORITE_COUNT] = tweet.favorite_count
#         tweet[TWEET_ID] = tweet.id_str
#         tweet[TWEET_RETWEET_COUNT] = tweet.retweet_count
#         
#         contributors = tweet.contributors
#         tweet[TWEET_NAME] = contributors.name
#         tweet[TWEET_SCREEN_NAME] = contributors.screen_name
#         tweet[TWEET_USER_ID] = contributors.id_str
#         
#         entities = tweet.entities
#         mentions = entities.user_mentions
#         user_mentions = []
#         for mention in mentions:
#             user_mentions.append(mention.name)
#         tweet[TWEET_MENTIONS] = " ".join(user_mentions)
#         
#         client.tweets.GentlerSongs.insert_one(tweet)
#         
#             tweets.append((tweet.id, unicode(tweet.text), tag))
    
#     corpusLoc = "data/tweets.sqlite"
#     corpus = SQLiteDB(corpusLoc)
#     corpus.insertTweetList(tweets)