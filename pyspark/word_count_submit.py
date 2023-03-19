# At terminal or command line: spark-submit word_count_submit.py

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
 
spark = SparkSession.builder.appName(
    "Analyzing the vocabulary of Pride and Prejudice."
).getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
 
results = (
    spark.read.text("./data/gutenberg_books/1342-0.txt")
    .select(F.split(F.col("value"), " ").alias("line"))
    .select(F.explode(F.col("line")).alias("word"))
    .select(F.lower(F.col("word")).alias("word"))
    .select(F.regexp_extract(F.col("word"), "[a-z']*", 0).alias("word"))
    .where(F.col("word") != "")
    .groupby("word")
    .count()
)
 
results.coalesce(1).write.option("header", "true").csv("data/simple_count_single_partition.csv")
