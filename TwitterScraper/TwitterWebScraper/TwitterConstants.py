'''
Created on Mar 1, 2016

@author: Andrew
'''

'''
Constants for Scraping Twitter.com
'''
TWITTER_SEARCH = "http://twitter.com/search?f=tweets&vertical=default&src=typd"
CLASS_HAS_MORE_ITEMS = "has-more-items"
CLASS_JS_TWEET_TEXT = "js-tweet-text"
CLASS_TWEET_TIMESTAMP = "tweet-timestamp"
CLASS_TRY_AGAIN = "try-again-after-whale"
CLASS_JS_ORIGINAL_TWEET = "js-original-tweet"
CLASS_QUOTE_TWEET = "QuoteTweet-innerContainer"
CLASS_ADAPTIVE_MEDIA = "AdaptiveMedia"
CLASS_MEDIA_CONTAINER = "js-media-container"
CLASS_TIMELINE_LINK = "twitter-timeline-link"
CLASS_RETWEET = "js-actionRetweet"
CLASS_FAVORITE = "js-actionFavorite"
CLASS_COUNT = "ProfileTweet-actionCountForPresentation"
ATTR_ITEM_ID = 'data-item-id'
ATTR_TITLE = "title"
ATTR_SCREEN_NAME = "data-screen-name"
ATTR_USER_ID = "data-user-id"
ATTR_NAME = "data-name"
ATTR_IS_REPLY_TO = "data-is-reply-to"
ATTR_RETWEETER = "data-retweeter"
ATTR_MENTIONS = "data-mentions"
TWITTER_DATE_FORMAT = '%I:%M %p - %d %b %Y'

'''
Tweet DB Constants
'''
TWEET_DB = "tweets"
TWEET_COLLECTION = "Unsorted Tweets"
TWEET_TEXT = "text"
TWEET_DATE = "date"
TWEET_ID = "tweet id"
TWEET_NAME = "name"
TWEET_SCREEN_NAME = "username"
TWEET_USER_ID = "user id"
TWEET_MENTIONS = "mentions"
TWEET_FAVORITE_COUNT = "favorites"
TWEET_RETWEET_COUNT = "retweets"