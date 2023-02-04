import tweepy
import datetime
import pyspark
from pyspark import SparkConf
from pyspark.sql import SparkSession
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
import re
import requests



#from tweepy.streaming import StreamListener
from tweepy import Stream
import numpy as np
from pyspark.sql.types import IntegerType

conf = SparkConf()
conf.set("spark.default.parallelism", 3)
conf.set("spark.network.timeout", "10000000")
# Acceso a la sesión de PySpark
spark = SparkSession.builder \
    .config("spark.some.config.option", conf).getOrCreate()
#spark = SparkSession.builder.getOrCreate()

# Claves de Autenticación de la API de Twitter
CONSUMER_KEY = "AgR8SsVwEsHzYbE3A38I30RLj"
CONSUMER_SECRET = "kEDhWbtedLWlg4KyS6QsQkfQGN1QqNNxKUhj2IvFYss22XYShc"
ACCESS_TOKEN = "1618629118903336960-QcAA4pwqGvXyw4AkTQDcSeiGFSpKL1"
ACCESS_TOKEN_SECRET = "eMViPrQKXh9SD4QYezE8z5rxS483AMP2Ca6nvpEWhzsgx"


# Listado de los nombres de usuario de las diferentes escuderías de Fórmula 1
SC_USERNAMES = ['MercedesAMGF1','AlpineF1Team','HaasF1Team','McLarenF1',
            'alfaromeof1', 'WilliamsRacing','redbullracing',
            'AstonMartinF1','ScuderiaFerrari','AlphaTauriF1']

# Autenticación
class TwitterAuth():
    def authenticate_twitter_app(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        return auth

# Extracción de datos
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuth().authenticate_twitter_app()
        self.twitter_client = tweepy.API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in tweepy.Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in tweepy.Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in tweepy.Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


class UserClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuth().authenticate_twitter_app()
        self.twitter_client = tweepy.API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
    
    def get_num_followers(self):
        res = []
        for c in SC_USERNAMES:
            user = self.twitter_client.get_user(screen_name = c)
            num_tweets = 100
            total_likes = 0
            total_rts = 0
            for tweet in tweepy.Cursor(self.twitter_client.user_timeline, screen_name=c, include_rts=False).items(num_tweets):
            #Se obtiene el número de likes y rts de los tweets
                total_likes += tweet.favorite_count
                total_rts += tweet.retweet_count
            res.append((c,user.followers_count,user.statuses_count,total_likes,total_rts))
        return res

class ProcessData():

    # Elimina emoji de los textos de los tweets
    def remove_emojis(self, text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)










'''
def call_api():
    res = []
    fecha_actual = datetime.datetime.now()
    for c in SC_USERNAMES:
        user = api.get_user(screen_name = c)
        res.append((fecha_actual,c,user.followers_count))
    df = spark.createDataFrame(res, schema=['fecha','escuderia','seguidores'])
    df.write.csv('./datasets/followers.csv', header=True)
    return res
'''


