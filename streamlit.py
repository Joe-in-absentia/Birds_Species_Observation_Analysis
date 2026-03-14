import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine


# Page title and layout width.

st.set_page_config(page_title="Bird Species Analysis", layout="wide")

st.title("🦅 Bird Species Analysis Dashboard")     # Main title.
st.markdown("---")

# Database connection.

engine = create_engine("postgresql://postgres:12345678@localhost:5432/birds_monitoring")

# Import the data from the database.

@st.cache_data
def load_data():

    forest = pd.read_sql("SELECT * FROM bird_forest_data", engine)
    grassland = pd.read_sql("SELECT * FROM bird_grassland_data", engine)

    forest["habitat"] = "Forest"
    grassland["habitat"] = "Grassland"    # Create a habitat column in data.

    df = pd.concat([forest, grassland], ignore_index=True)  # Convert into dataframe.

    df.columns = df.columns.str.lower()          # Convert column names to lowercase.
    
    df["date"] = pd.to_datetime(df["date"])
                                                 # Convert the date and month from string.
    df["month"] = df["date"].dt.month_name() 

    return df

df = load_data()


st.sidebar.header("⚙️Dashboard Controls")      # Sidebar layout.
st.sidebar.markdown("---")

analysis = st.sidebar.radio("Choose Analysis",["Seasonal Trends","Species Distribution" ,
           "Observer Trends","Environmental Impact","Distance & Behavior"])

# Sidebar filters.

st.sidebar.subheader("Filters")

months = st.sidebar.multiselect("Select Months",sorted(df["month"].unique()),
         default=sorted(df["month"].unique()))

intervals = st.sidebar.multiselect("Select Time Interval",sorted(df["interval_length"].unique()),
            default=sorted(df["interval_length"].unique()))

filtered_df = df[(df["month"].isin(months)) &(df["interval_length"].isin(intervals))]



def seasonal_trends():                         # For seasonal chart.

    st.header("📅Seasonal Bird Sightings")

    data = filtered_df.groupby(["date", "habitat"])["common_name"].count().reset_index()

    fig = px.line(data,
          x="date",
          y="common_name",
          color="habitat",
          markers=True,
          title="Bird Sightings Over Time")

    st.plotly_chart(fig,width='stretch')



def species_distribution():                    # For species distribution barchart

    st.header("🦢Species Distribution")

    species = filtered_df.groupby(["common_name", "habitat"]).size().reset_index(name="birds count")

    fig = px.bar(species,
          x="common_name",
          y="birds count",
          color="habitat",
          title="Bird Species Distribution")
    st.plotly_chart(fig,width='stretch')
    



def observer_trends():                          # For observer barchart.

    st.header("👀 Observer Contributions")

    observers = filtered_df.groupby(["observer", "habitat"]).size().reset_index(name="observed count")

    fig = px.bar(
          observers,
          x="observer",
          y="observed count",
          color="habitat",
          title="Observer Activity")

    st.plotly_chart(fig,width='stretch')



def environmental_impact():                     # For environment scatterchart.

    st.header("🌍Environmental Impact Analysis")

    fig1 = px.scatter(filtered_df,
          x="temperature",
          y="common_name",
          color="habitat",                      # For temperature.
          hover_name="common_name",
          title="🌡️ Temperature Impact",
          hover_data=["common_name","observer","distance"])
    st.plotly_chart(fig1,width='stretch')

    fig2 = px.scatter(filtered_df,
          x="humidity",
          y="common_name",                      # For humidity.
          color="habitat",
          hover_name="common_name",
          title="💧 Humidity Impact",
          hover_data=["common_name","observer","distance"])
    st.plotly_chart(fig2,width='stretch')


def distance_behavior():                        # Distance & behavior charts.

    st.header("📏Distance Analysis")

    distance = filtered_df.groupby(["distance", "habitat"]).size().reset_index(name="observed count")

    fig1 = px.bar(distance,
           x="distance",
           y="observed count",
           color="habitat",
        title="Bird Sightings by Distance")

    st.plotly_chart(fig1,width='stretch')

    st.header("🕊️Flyover Observations")

    fly = filtered_df.groupby(["flyover_observed", "habitat"]).size().reset_index(name="observed count")

    fig2 = px.pie(fly,
           names="flyover_observed",
           values="observed count",
           title="Flyover Observed")

    st.plotly_chart(fig2,width='stretch')


if analysis == "Seasonal Trends":
    seasonal_trends()
elif analysis == "Species Distribution":
    species_distribution()
elif analysis == "Observer Trends":
    observer_trends()
elif analysis == "Environmental Impact":
    environmental_impact()
else:
    distance_behavior()

