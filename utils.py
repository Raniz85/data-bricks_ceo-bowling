from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType
from itertools import tee
from functools import reduce
import re

# Define a helper to load the input for a series
def load_input(part: int) -> [str]:
    """Loads the input for a part of the kata from the volume"""
    input_path = f"./series{part:02d}.txt"
    with open(input_path) as f:
        return f.readlines()

players_schema = StructType([
    StructField("PlayerID", IntegerType(), False),
    StructField("Name", StringType(), False),
])
frames_schema = StructType([
    StructField("PlayerID", IntegerType(), False),
    StructField("Game", IntegerType(), False),
    StructField("Frame", IntegerType(), False),
    StructField("Throw1", IntegerType(), False),
    StructField("Throw2", IntegerType(), True),
])

def split_row(row: str) -> (str, [int]):
    first_digit = re.search(r"\d", row).start()
    return (row[0:first_digit].strip(), [int(n) for n in row[first_digit:].strip().split()])

def load_input_into_dataframes(spark: SparkSession, game: int) -> (DataFrame, DataFrame):
    input = load_input(game)
    players = [ (i, split_row(row)[0]) for i, row in enumerate(input) ]
    frames = []
    for player_id, row in enumerate(input):
        _, throws = split_row(row)
        throw_iterator = iter(throws)
        pairs = [ (it, next(throw_iterator) if it < 10 else None) for it in throw_iterator]
        frames.extend([ (player_id, game, i, first, second) for i, (first, second) in enumerate(pairs)])

    players = spark.createDataFrame(players, players_schema)
    frames = spark.createDataFrame(frames, frames_schema)
    return (players, frames)

def load_all_input_into_dataframes(spark: SparkSession):
    data_frames = [ load_input_into_dataframes(spark, i) for i in range(1, 5)]
    player_frames = [x[0] for x in data_frames]
    frame_frames = [x[1] for x in data_frames]
    players_frame = reduce(lambda x, y: x.union(y), player_frames).distinct()
    frames_frame = reduce(lambda x, y: x.union(y), frame_frames)
    return (players_frame, frames_frame)