import pandas as pd
import streamlit as st
import datetime
import plotly.express as px 


# Hides Burger Menu From Users and adding credits in footer
hide_menu = """
<style>
    #MainMenu {
        visibility:hidden; 
    }
    
    footer {
        visibility:visible; 
    }
    footer:after {
        content: "Created by: Saeed Salman, Jessica Bridgland and Adis Zukic"; 
        display: block; 
        position: relative;
        color: black; 
        padding: 5px; 
        top: 3px; 
        font-size: 20px; 
    }
</style>
"""
st.set_page_config(
        page_title="Victorian Accidents Data Visualiser",
        layout="wide"
)
st.markdown(hide_menu, unsafe_allow_html=True)

fileName = "Crash_Statistics_Victoria.csv"
# Reads data from csv file 
df = pd.read_csv(fileName)

if df.empty:
    print("Did not read file")

# Add 'HOUR' column to dataframe
df["HOUR"] = pd.to_datetime(df["ACCIDENT_TIME"], format="%H.%M.%S").dt.hour

# Add 'DAY' column to dataframe to convert day of week to number
df["DAY"] = pd.to_datetime(df["ACCIDENT_DATE"]).dt.dayofweek

# covert date to pd format
df['ACCIDENT_DATE'] = pd.to_datetime(df['ACCIDENT_DATE']).dt.date
min_date = datetime.datetime.strptime('2013-01-07', '%Y-%m-%d')
max_date = datetime.datetime.strptime('2019-12-03', '%Y-%m-%d')

# SIDEBAR
st.sidebar.header("Please filter here")

# start and end date selection
start_date_input = st.sidebar.date_input("Select start date", (datetime.date(2013,1,7)), help="The start date begins: 2013/01/07")
end_date_input = st.sidebar.date_input("Select end date", (datetime.date(2019,12,4)), help="The end date finishes: 2019/12/03, but is exclusive")

if start_date_input < min_date.date() and end_date_input < min_date.date() or start_date_input > max_date.date() and end_date_input > max_date.date():
    st.error("There is no data in between these dates")
if start_date_input <= end_date_input:
    pass
else:
    st.error("The start date must come before the end date")


accidentType = st.sidebar.multiselect(
    "Select the Accident Type:",
    options = df["ACCIDENT_TYPE"].unique() 
)

#Light Condition Selector 
lightCondition = st.sidebar.multiselect(
    "Select Light Coniditon of Accident:",
    options = df["LIGHT_CONDITION"].unique(),       
)
container = st.sidebar.container()                  
all = st.sidebar.checkbox("Select all")             #Checkbox for select all 
if all:                                             #Checks to see if user clicks select all
    lightCondition = st.sidebar.multiselect(
    "Select Light Coniditon of Accident:",
    options = df["LIGHT_CONDITION"].unique(),  
    default = df["LIGHT_CONDITION"].unique(),       
)

#Alcohol trend
alcohol = st.sidebar.checkbox("Include Alcohol Trends")    

# Retrieves data based on which query the user has selected
if not lightCondition and not accidentType:
    df_selection = df.query(
    " (ACCIDENT_TYPE == @accidentType) and (ACCIDENT_DATE >= @start_date_input) and (ACCIDENT_DATE < @end_date_input)"
)
    
elif not accidentType:
    df_selection = df.query(
    " (LIGHT_CONDITION == @lightCondition) and (ACCIDENT_DATE >= @start_date_input) and (ACCIDENT_DATE < @end_date_input)"
)
    
elif not lightCondition:
    df_selection = df.query(
    "(ACCIDENT_DATE >= @start_date_input) and (ACCIDENT_DATE < @end_date_input)"
)   
else:
    df_selection = df.query(
        "(LIGHT_CONDITION == @lightCondition) and (ACCIDENT_TYPE == @accidentType) and (ACCIDENT_DATE >= @start_date_input) and (ACCIDENT_DATE < @end_date_input)"
)



# Main Page 
st.title(":bar_chart: Victorian Accidents Data Visualiser")
st.markdown("##")
total_accidents = int(df_selection["OBJECTID"].count())

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader(f" Total Accidents: {total_accidents:,}") # changed this to be inline

st.markdown("---")
st.dataframe(df_selection) 

# LIGHT CONDITION CHART
light_condition_chart = (
        df_selection.groupby(by=["LIGHT_CONDITION"]).sum()[["TOTAL_PERSONS"]].sort_values(by="TOTAL_PERSONS")
)

fig_light_condition = px.bar(
        light_condition_chart,
        x = "TOTAL_PERSONS",
        y = light_condition_chart.index,
        orientation="h",
        title="<b>Light Condition Chart</b>",
        template="plotly_white",
)

# ACCIDENT TYPE CHART
accident_type_chart = (
        df_selection.groupby(by=["ACCIDENT_TYPE"]).sum()[["TOTAL_PERSONS"]].sort_values(by="TOTAL_PERSONS")
)

fig_accident_type = px.bar(
        accident_type_chart,
        x = "TOTAL_PERSONS",
        y = accident_type_chart.index,
        orientation="h",
        title="<b>Accident Type Chart</b>",
        template="plotly_white",
)


## accidents per hour average [BAR CHART]
accident_by_hour = (
    df_selection.groupby("HOUR") # 0-23 : 0=midnight
    .mean()
    .round(0) # rounds to display int
    .reset_index()
    .rename(columns={"DAY": "Average"})
)

fig_accident_hourly = px.bar(
   accident_by_hour,
    x="HOUR",
    y="Average",
    labels={"HOUR": "Hour of Day (Midnight = 0)",
            "Average": "Average Number of Accidents"},
    title="<b>Accidents per Hour</b>",
    text="Average",
)

#alcohol trend chart
alcohol_trend_chart = (
    df_selection.groupby(by=["ALCOHOL_RELATED"]).sum()[["TOTAL_PERSONS"]].sort_values(by="TOTAL_PERSONS")
)

fig_alcohol_trend = px.bar(
    alcohol_trend_chart,
    x = "TOTAL_PERSONS",
    y = alcohol_trend_chart.index,
    orientation="h",
    title="<b>Alcohol Involved in Accident</b>",
    template="plotly_white",
)

if lightCondition:   
    st.plotly_chart(fig_light_condition, use_container_width=True)
    
    if accidentType:
        st.plotly_chart(fig_accident_type, use_container_width=True)
        st.plotly_chart(fig_accident_hourly, use_container_width=True)
    
    if alcohol:
        st.plotly_chart(fig_alcohol_trend, use_container_width=True)
        
elif accidentType:
    st.plotly_chart(fig_accident_type, use_container_width=True)
    st.plotly_chart(fig_accident_hourly, use_container_width=True)

    
    if alcohol:
        st.plotly_chart(fig_alcohol_trend, use_container_width=True)



# button download csv file
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.sidebar.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='Crash_Statistics_Victoria.csv',
    mime='text/csv',
)