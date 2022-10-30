import streamlit as st
import plotly
import ujson
import pandas as pd
import plotly.express as px
import glob
import time
from datetime import datetime as dt
import itertools
import collections
import os

st.set_page_config(layout="wide")

@st.cache
def load_jsons(ids):
    point_dfs = []
    club_data = []
    for id in ids:
        with open(id, "r") as f:
            json_loaded = ujson.load(f)
            point_dfs.append(json_loaded["point"])
            club_data.append(list(json_loaded["stay"].values()))
    
    point_dataframe = pd.DataFrame(data=dict(id=[i[27:].replace(".json","") for i in ids], point=point_dfs))
    club_data = collections.Counter(itertools.chain.from_iterable(club_data))
    club_data = pd.DataFrame(data=dict(name=list(club_data.keys()), counts=list(club_data.values())))
    club_data.drop(0,inplace=True)
    return point_dataframe, club_data



@st.cache
def load_data(id_selected):
    with open(id_selected, "r") as f:
        df = ujson.load(f)
    df_history = pd.DataFrame(df)
    df_history["point"] = df_history["log"].cumsum()
    df_history["time"] = df_history["time"].apply(lambda x: dt.strptime("2021/"+x, r"%Y/%m/%d %H:%M:%S"))
    return df_history

id_list = glob.glob(r"/app/gpoint-2021-site/2021/*.json")
id_list_names = [i[27:].replace(".json","") for i in id_list]

st.sidebar.write("### ID")
id_selected = st.sidebar.selectbox(' ', id_list_names)

st.sidebar.write("### point ranking")
point_dataframe, club_data = load_jsons(id_list)
st.sidebar.dataframe(point_dataframe.sort_values("point", ascending=False).reset_index(drop=True))

st.header("G-Point 履歴 2021\n")
tab1, tab2 = st.tabs(["user", "club"])

with tab1:
    df_history = load_data("/app/gpoint-2021-site/2021/"+id_selected+".json")
    st.subheader("ポイントの推移")
    fig = px.line(df_history, x='time', y='point', hover_name='stay', markers=True)
    st.write(fig)
    left_column, right_column = st.columns(2)
    left_column.subheader('ログ')
    right_column.subheader('景品の引き換え')
    with left_column:
        st.dataframe(df_history,height=150)
    with right_column:
        st.dataframe(pd.DataFrame(data=dict(prize=["item1","item2"],bool=["交換済み","交換済み"])))
        #st.write("item1: "+"True")
        #st.write("item2: "+"True")

with tab2:
    st.subheader("サークルに訪れた人数")
    fig = px.bar(club_data, x="name", y="counts")
    st.write(fig)
    st.subheader("合計ポイント: "+str(sum(point_dataframe["point"])))
