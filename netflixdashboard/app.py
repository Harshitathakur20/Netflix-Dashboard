import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Netflix Data Dashboard",
    layout="wide"
)

st.title("🎬 Netflix Data Analysis Dashboard")

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")

    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["year_added"] = df["date_added"].dt.year

    return df


df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Dashboard Filters")

type_filter = st.sidebar.multiselect(
    "Select Content Type",
    options=sorted(df["type"].dropna().unique()),
    default=sorted(df["type"].dropna().unique())
)

country_filter = st.sidebar.multiselect(
    "Select Country",
    options=sorted(
        df["country"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .unique()
    )
)

rating_filter = st.sidebar.multiselect(
    "Select Rating",
    options=sorted(df["rating"].dropna().unique())
)

year_filter = st.sidebar.slider(
    "Select Release Year",
    int(df.release_year.min()),
    int(df.release_year.max()),
    (
        int(df.release_year.min()),
        int(df.release_year.max())
    )
)

# -----------------------------
# Apply Filters
# -----------------------------
filtered_df = df[df["type"].isin(type_filter)]

if country_filter:
    filtered_df = filtered_df[
        filtered_df["country"].fillna("").apply(
            lambda x: any(c in x for c in country_filter)
        )
    ]

if rating_filter:
    filtered_df = filtered_df[
        filtered_df["rating"].isin(rating_filter)
    ]

filtered_df = filtered_df[
    (filtered_df["release_year"] >= year_filter[0]) &
    (filtered_df["release_year"] <= year_filter[1])
]

# -----------------------------
# Metrics
# -----------------------------
st.subheader("📊 Key Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Titles", len(filtered_df))
c2.metric("Movies", len(filtered_df[filtered_df["type"] == "Movie"]))
c3.metric("TV Shows", len(filtered_df[filtered_df["type"] == "TV Show"]))
c4.metric("Countries", filtered_df["country"].nunique())

st.divider()

# -----------------------------
# Pie Chart
# -----------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("Movies vs TV Shows")

    # type_count = filtered_df["type"].value_counts()
    #
    # fig = px.pie(
    #     values=type_count.values,
    #     names=type_count.index,
    #     color_discrete_sequence=px.colors.sequential.Reds
    # )
    type_count = filtered_df["type"].value_counts().reset_index()
    type_count.columns = ["Type", "Count"]

    fig = px.pie(
        type_count,
        values="Count",
        names="Type",
        color_discrete_sequence=px.colors.sequential.Reds
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Line Chart
# -----------------------------
with col2:

    st.subheader("Content Added Over Time")

    yearly = (
        filtered_df["year_added"]
        .dropna()
        .value_counts()
        .sort_index()
        .reset_index()
    )

    yearly.columns = ["Year", "Titles"]

    fig = px.line(
        yearly,
        x="Year",
        y="Titles",
        markers=True
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Titles Added"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# Top Countries
# -----------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("Top Countries")

    countries = (
        filtered_df["country"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
    )

    # top = countries.value_counts().head(10)
    #
    # fig = px.bar(
    #     x=top.values,
    #     y=top.index,
    #     orientation="h",
    #     color=top.values,
    #     color_continuous_scale="Reds"
    # )
    top = countries.value_counts().head(10).reset_index()
    top.columns = ["Country", "Titles"]

    fig = px.bar(
        top,
        x="Titles",
        y="Country",
        orientation="h",
        color="Titles",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        xaxis_title="Titles",
        yaxis_title="Country"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Ratings
# -----------------------------
with col2:

    st.subheader("Ratings Distribution")

    # rating = filtered_df["rating"].value_counts()
    #
    # fig = px.bar(
    #     x=rating.index,
    #     y=rating.values,
    #     color=rating.values,
    #     color_continuous_scale="Reds"
    # )
    rating = filtered_df["rating"].value_counts().reset_index()
    rating.columns = ["Rating", "Count"]

    fig = px.bar(
        rating,
        x="Rating",
        y="Count",
        color="Count",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        xaxis_title="Rating",
        yaxis_title="Count"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# Genres
# -----------------------------
st.subheader("Top Genres")

genres = (
    filtered_df["listed_in"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
)

# genre = genres.value_counts().head(10)
#
# fig = px.bar(
#     x=genre.index,
#     y=genre.values,
#     color=genre.values,
#     color_continuous_scale="Reds"
# )
genre = genres.value_counts().head(10).reset_index()
genre.columns = ["Genre", "Titles"]

fig = px.bar(
    genre,
    x="Genre",
    y="Titles",
    color="Titles",
    color_continuous_scale="Reds"
)

fig.update_layout(
    xaxis_title="Genre",
    yaxis_title="Titles"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# World Map
# -----------------------------
st.subheader("Global Distribution")

country_counts = (
    filtered_df["country"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
    .value_counts()
    .reset_index()
)

country_counts.columns = ["country", "count"]

fig = px.choropleth(
    country_counts,
    locations="country",
    locationmode="country names",
    color="count",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# Search
# -----------------------------
st.subheader("Dataset Preview")

search = st.text_input("Search Title")

if search:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.markdown(
    "<center><h4>Netflix Data Dashboard</h4></center>",
    unsafe_allow_html=True
)
