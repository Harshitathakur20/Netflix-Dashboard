import pandas as pd
import streamlit as st
import plotly.express as px
st.set_page_config(page_title="Netflix Dashboard",layout="wide")
st.header("Netflix Dashboard")

@st.cache_data
def load_data():
    df=pd.read_csv("netflix_titles.csv")
    df["date_added"]=pd.to_datetime(df["date_added"],errors="coerce")
    df["year_added"]=df["date_added"].dt.year
    return df

df=load_data()
st.sidebar.header("Dashboard Filters")

type_filter=st.sidebar.multiselect("Select Content Type",
            options=df["type"].dropna().unique(),
            default=df["type"].dropna().unique())
country_filter=st.sidebar.multiselect("Select Country",
            options=df["country"].dropna().unique())
rating_filter=st.sidebar.multiselect("Select Rating",
            options=df["rating"].dropna().unique())
year_filter=st.sidebar.slider("Select Release Year",
                              int(df["release_year"].min()),
                              int(df["release_year"].max()),
                              (2000,2020))
fil_df=df[df["type"].isin(type_filter)]
if country_filter:
    fil_df=fil_df[fil_df["country"].isin(country_filter)]
if rating_filter:
    fil_df = fil_df[fil_df["rating"].isin(rating_filter)]
if year_filter:
    fil_df=fil_df[(fil_df["release_year"]>=year_filter[0]) &
                  (fil_df["release_year"]<=year_filter[1])]

st.subheader("Key Metrics")
col1,col2,col3,col4=st.columns(4)
total=len(fil_df)
movies=len(fil_df[fil_df["type"]=="Movie"])
tvshows=len(fil_df[fil_df["type"]=="TV Show"])
cnts=fil_df["country"].nunique()
col1.metric("Total Titles",total)
col2.metric("Movies",movies)
col3.metric("TV Shows",tvshows)
col4.metric("Countries",cnts)

st.divider()
col1,col2=st.columns(2)
with col1:
    st.subheader("Movies vs TV Shows")
    type_count=fil_df["type"].value_counts()
    fig=px.pie(values=type_count.values,names=type_count.index,
               color_discrete_sequence=px.colors.sequential.Reds)
    st.plotly_chart(fig,width="stretch")

with col2:
    st.subheader("Content Added Over Time")
    yearly_count=fil_df["release_year"].value_counts().sort_index()
    fig=px.line(x=yearly_count.index,y=yearly_count.values,markers=True)
    fig.update_layout( xaxis_title="Year",
        yaxis_title="Titles Added")
    st.plotly_chart(fig,width="stretch")

st.divider()
col1,col2=st.columns(2)
with col1:
    st.subheader("Top Countries Producing Content")
    cnt_values=fil_df["country"].value_counts().head(10)
    fig=px.bar(x=cnt_values.values,y=cnt_values.index,
               orientation="h",
               color=cnt_values.values,
               color_continuous_scale="Reds"
               )
    fig.update_layout(yaxis_title="Country",
                      xaxis_title="Titles Added")
    st.plotly_chart(fig,width="stretch")

with col2:
    st.subheader("Ratings Distribution")
    rating_counts = fil_df['rating'].value_counts()

    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        color=rating_counts.values,
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        xaxis_title="Rating",
        yaxis_title="Count"
    )

    st.plotly_chart(fig,width="stretch")

st.divider()
st.subheader("Top Genres")
genres=fil_df["listed_in"].str.split(",").explode()
genre_counts=genres.value_counts().head(10)
fig = px.bar(
    x=genre_counts.index,
    y=genre_counts.values,
    color=genre_counts.values,
    color_continuous_scale="Reds"
)

fig.update_layout(
    xaxis_title="Genre",
    yaxis_title="Number of Titles"
)

st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("Global Distribution of Netflix Content")
country_counts = fil_df['country'].value_counts().reset_index()
country_counts.columns = ['country','count']

fig = px.choropleth(
    country_counts,
    locations="country",
    locationmode="country names",
    color="count",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig,width="stretch")


st.divider()
st.subheader("Dataset Preview")
search = st.text_input("Search Title")

if search:
    fil_df = fil_df[
        fil_df['title'].str.contains(search, case=False)
    ]

st.dataframe(fil_df.head(100))