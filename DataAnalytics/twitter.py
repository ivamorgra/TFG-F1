import tweepy
from .models import Constructor
import datetime
import pyspark
from pyspark.sql import SparkSession

# Acceso a la sesión de PySpark
spark = SparkSession.builder.getOrCreate()

# Autenticación de la API de Twitter
CONSUMER_KEY = "AgR8SsVwEsHzYbE3A38I30RLj"
CONSUMER_SECRET = "kEDhWbtedLWlg4KyS6QsQkfQGN1QqNNxKUhj2IvFYss22XYShc"
ACCESS_TOKEN = "1618629118903336960-QcAA4pwqGvXyw4AkTQDcSeiGFSpKL1"
ACCESS_TOKEN_SECRET = "eMViPrQKXh9SD4QYezE8z5rxS483AMP2Ca6nvpEWhzsgx"


# Autenticación

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

SC_USERNAMES = ['MercedesAMGF1','AlpineF1Team','HaasF1Team','McLarenF1',
            'alfaromeoorlen', 'WilliamsRacing','redbullracing',
            'AstonMartinF1','ScuderiaFerrari','AlphaTauriF1']
# Listado de los nombres de usuario de las diferentes escuderías de Fórmula 1

def get_actual_followers():
    res = []
    for c in SC_USERNAMES:
        user = api.get_user(screen_name = c)

        res.append((c,user.followers_count))
    print (res)
    return res

def get_followers():
    res = []
    fecha_actual = datetime.datetime.now()
    for c in SC_USERNAMES:
        user = api.get_user(screen_name = c)
        res.append((fecha_actual,c,user.followers_count))
    df = spark.createDataFrame(res, schema=['fecha','escuderia','seguidores'])
    df.write.csv('./datasets/followers.csv', header=True)
    return res

# api.get_followers()



