import streamlit as st
import pandas as pd
import requests
from typing import Any

@st.cache_data
def get_all_books() -> dict[str, Any]:
    return requests.get(url).json()

def parse_query(text:str):
    fields = text.split(";")
    

url = "http://127.0.0.1:8080/book"

columns = ["title","author","month","year","pages", "rating", "status", "category"]

st.title("Read books manager")

tab1, tab2, tab3 = st.tabs(tabs=["Show","Update", "Add"])

with tab1:
    st.write("Select the columns to be displayed")
    cols_layout = st.columns(round(len(columns)/3))
    for e, col in enumerate(columns):
        cols_layout[e % 3].checkbox(col, key=f"check_{col}")
            
    all_books_btn = st.button("Get all books")

    if all_books_btn:
        checked = {col: st.session_state[f"check_{col}"] for col in columns}
        to_show = [k for k,v in checked.items() if v]
        all_books = get_all_books()
        df = pd.DataFrame(all_books)[to_show]
        st.dataframe(df)