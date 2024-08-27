from pathlib import Path
import pandas as pd
import numpy as np
import logging
from utils import connect_to_mongo

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    data_folder_path = Path(__file__).parents[1] / "data"
    xlsx_file = pd.ExcelFile(data_folder_path / "read.xlsx")

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

    books_documents = [x for x in all_books.to_dict(orient="index").values()]
    logging.info("Connecting to MongoDB...")

    with connect_to_mongo() as client:
        db = client.get_database("readbooks")
        res = db.books.insert_many(books_documents)
        if res.acknowledged:
            logging.info("Books pushed correctly to the database")
        else:
            logging.error("An error occurred while pushing the data")

