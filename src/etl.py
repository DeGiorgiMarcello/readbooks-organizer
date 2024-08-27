import pandas as pd
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
from os import environ
import logging

load_dotenv()

xlsx_file = pd.ExcelFile("../data/read.xlsx")

dfs = []

conv_dict = {
    "titolo": "title",
    "autore": "author",
    "mese": "month",
    "*": "rating",
    "categoria": "category",
    "pagine": "pages",
}

month_dict = {
    "gennaio":1,
    "febbraio":2,
    "marzo":3,
    "aprile":4,
    "maggio":5,
    "giugno":6,
    "luglio":7,
    "agosto":8,
    "settembre":9,
    "ottobre":10,
    "novembre":11,
    "dicembre":12,
}

for sheet in xlsx_file.sheet_names:
    logging.info("Reading sheet {}...".format(sheet))
    df = pd.read_excel(xlsx_file, sheet_name=sheet, header=2)
    df = df.drop(columns=["#"])
    df = df.rename(columns=conv_dict)
    df["month"] = df.month.map(month_dict)
    # rating wrongly converted to datetime
    df = df.dropna(how="all")
    susp_mask = df.rating.isin(["sosp","sospeso"])
    df["status"] = np.where(susp_mask,"suspended", "completed")
    df.loc[susp_mask,"rating"] = pd.NaT
    df["rating"] = df.rating.apply(lambda x: x.day)
    df = df.astype({"status":"category"})
    df["year"] = int(sheet)

    dfs.append(df)

logging.info("Concatenating all the sheets...")
all_books = pd.concat(dfs, axis=0)
all_books.reset_index(inplace=True, drop=True)

## To MongoDB
host = environ.get("BOOKS_MONGODB_HOST")
port = environ.get("BOOKS_MONGODB_PORT")

if not (host and port):
    raise KeyError("MongoDB host and port must both be passed")

logging.info("Connecting to MongoDB...")

client = MongoClient(host=host, port=int(port))
db = client.get_database("readbooks")

books_documents = [x for x in all_books.to_dict(orient="index").values()]

res = db.books.insert_many(books_documents)

if res.acknowledged:
    logging.info("Books pushed correctly to the database")
else:
    logging.error("An error occurred while pushing the data")

