from django.shortcuts import render
from pyspark import SparkContext, SparkConf, SQLContext
import findspark
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("F1Analytics").getOrCreate()
print(spark)
# Create your views here.
