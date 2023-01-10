import csv 
from .models import Circuito, Piloto, Constructor
from pyspark import SparkContext
from pyspark.sql import SparkSession

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

def driver_basic_stats(driver_id):
    races = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    races_driver = races.filter(races.driverId == driver_id)
    num_races = races_driver.count()
    num_wins = races.filter( (races.driverId == driver_id) & (races.position == 1)).count()
    sraces =  spark.read.csv("./datasets/sprint_results.csv", header=True,sep=",")
    num_sraces = sraces.filter(sraces.driverId == driver_id).count()
    num_swins = sraces.filter( (sraces.driverId == driver_id) & (sraces.position == 1)).count()
    
    stats = [num_races,num_wins,num_sraces,num_swins]
    return stats

def constructor_basic_stats(constructor_id):
    races = spark.read.csv("./datasets/constructor_standings.csv", header=True,sep=",")
    races_constructor = races.filter(races.constructorId == constructor_id)
    num_races = races_constructor.dropDuplicates(['raceId']).count()
    num_wins = races.filter( (races.constructorId == constructor_id) & (races.position == 1)).count()
    sraces =  spark.read.csv("./datasets/sprint_results.csv", header=True,sep=",")
    num_sraces = sraces.filter(sraces.constructorId == constructor_id).dropDuplicates(['raceId']).count()
    num_swins = sraces.filter( (sraces.constructorId == constructor_id) & (sraces.position == 1)).count()
    
    stats = [num_races,num_wins,num_sraces,num_swins]
    return stats
