import streamlit as st
import pandas as pd
import requests
from typing import Any
import json 

@st.cache_data
def get_books(query: dict[str,Any] | None = None) -> dict[str, Any]:
    url = URL
    if query:
        url = get_string_query(query, URL)
    return requests.get(url).json()

def get_string_query(query: dict[str,Any], url:str ) -> str:
        query_str = "".join([f"{k}={v}&" for k,v in query.items()])
        query_str = "?"+query_str[:-1]
        return url+query_str

def get_query():
    query =  {col: st.session_state[f"query_get_{col}"] for col in TEXT_COLS}
    query.update({col: st.session_state[f"query_get_{col}"] for col in NUM_COLS})
    return {k:v for k,v in query.items() if v}


def get_categories():
    return requests.get(URL+"/categories").json()

def draw_input_attributes(key:str | None = None):
    q_text_layout = st.columns(2)
    q_num_cols = st.columns(2)
    q_text_layout[0].text_input("title", key=f"{key}_title")
    q_text_layout[1].text_input("author", key=f"{key}_author")
    q_text_layout[0].selectbox("status",key=f"{key}_status", options=["completed","suspended"] )
    q_text_layout[1].selectbox("category", key=f"{key}_category",options=get_categories())

    q_num_cols[0].number_input("month",value = None, min_value=1,max_value=12,step=1, key=f"{key}_month")
    q_num_cols[1].number_input("year", value = None, min_value=1924,max_value=2100,step=1, key=f"{key}_year")
    q_num_cols[0].number_input("rating", value=None,min_value=1,max_value=5, key=f"{key}_rating")
    q_num_cols[1].number_input("pages", value = None,  min_value=0,step=1, key=f"{key}_pages")


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
        draw_input_attributes(key="query_get")

    btn_cols = st.columns([1,1,3])        
    all_books_btn = btn_cols[0].button("Get all books")
    delete_btn = btn_cols[1].button("Delete")
    security_check = btn_cols[2].checkbox("Are you sure?", help="Security check before the deletion")

    query = {}
    if all_books_btn:
        checked = {col: st.session_state[f"check_{col}"] for col in COLUMNS}
        to_show = [k for k,v in checked.items() if v]
        to_show = to_show if to_show else COLUMNS
        query = get_query()
        st.session_state.query = query
        all_books = get_books(query)
        if all_books:
            df = pd.DataFrame(all_books)[to_show]
            st.dataframe(df)
        else:
            st.write("No book found. Check the spelling and the case.")

    if delete_btn and security_check:
        res = requests.delete(URL, data = json.dumps(st.session_state["query"]))
        if res.status_code == 204:
            st.text("Entries deleted successfully")
        else:
            st.error("An error occurred while deleting the entries")



with tab3:
    st.title("Add a new read book")
    draw_input_attributes(key="add")

    st.text_input("New category", help="Use this field if the category is not available in the drop down menu", key="add_new_cat")
    add_btn = st.button("Add ")

    if add_btn:
        new_book = {col: st.session_state[f"add_{col}"] for col in COLUMNS}

        new_cat_state = st.session_state["add_new_cat"]
        if new_cat_state:
            if (cat_state:=st.session_state["add_category"]) != "None":
                st.warning(f"A new category has been added. The category chosen from the dropdown menù ({cat_state}) will be ignored.")
            new_book["category"] = new_cat_state

        new_book = {k.replace("\'",'\"'): v for k,v in new_book.items()}

        if not all([v for v in new_book.values()]):
            st.error("All the fields must be filled")
        else:
            requests.post(URL, json.dumps(new_book))
        
