import streamlit as st
import pandas as pd
import requests
from typing import Any
from datetime import datetime

@st.cache_data
def get_books(query: str | None = None) -> dict[str, Any]:
    url = URL
    if query:
        query_str = "".join([f"{k}={v}&" for k,v in query.items()])
        query_str = "?"+query_str[:-1]
        url = URL+query_str
    return requests.get(url).json()

def get_query():
    query =  {col: st.session_state[f"text_{col}"] for col in TEXT_COLS}
    query.update({col: st.session_state[f"num_{col}"] for col in NUM_COLS})
    return {k:v for k,v in query.items() if v}
    

URL = "http://127.0.0.1:8080/book"

COLUMNS = ["title","author","month","year","pages", "rating", "status", "category"]
TEXT_COLS = ["title","author", "status", "category"]
NUM_COLS = ["month","year","pages", "rating"]
st.title("Read books manager")

tab1, tab2, tab3 = st.tabs(tabs=["Show","Update", "Add"])

with tab1:
    st.write("Select the columns to be displayed")
    cols_layout = st.columns(round(len(COLUMNS)/3))



    for e, col in enumerate(COLUMNS):
        cols_layout[e % 3].checkbox(col, key=f"check_{col}")

    with st.expander("Search"):
        q_text_layout = st.columns(2)
        q_num_cols = st.columns(2)
        q_text_layout[0].text_input("title", key="text_title")
        q_text_layout[1].text_input("author", key="text_author")
        q_text_layout[0].selectbox("status",key="text_status", options=["completed","suspended"] )
        q_text_layout[1].selectbox("category", key="text_category",options=[None, "classici cinesi"]  )

        q_num_cols[0].number_input("month",value = None, min_value=1,max_value=12,step=1, key="num_month")
        q_num_cols[1].number_input("year", value = None, min_value=1924,max_value=2100,step=1, key="num_year")
        q_num_cols[0].number_input("rating", value=None,min_value=1,max_value=5, key="num_rating")
        q_num_cols[1].number_input("pages", value = None,  min_value=0,step=1, key="num_pages")

            
    all_books_btn = st.button("Get all books")


    if all_books_btn:
        checked = {col: st.session_state[f"check_{col}"] for col in COLUMNS}
        to_show = [k for k,v in checked.items() if v]
        to_show = to_show if to_show else COLUMNS
        all_books = get_books(get_query())
        if all_books:
            df = pd.DataFrame(all_books)[to_show]
            st.dataframe(df)
        else:
            st.write("No book found. Check the spelling and the case.")

    