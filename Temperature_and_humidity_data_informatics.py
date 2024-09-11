#python3 -m streamlit run tst.py
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta




# Function to fetch data with caching
@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_data(connection_name, url):
    conn = st.connection(connection_name, type=GSheetsConnection)
    data = conn.read(spreadsheet=url)
    return data


hide_st_style =  """
                    <style>
                    #MainMenu {visibility : hidden}
                    footer {visibility : hidden}
                    header {visibility : hidden}
                    </style>
            """

st.markdown (hide_st_style, unsafe_allow_html=True)


# Google Spreadsheet URL and connection name
#url = st.secrets["sensor_data"]
url = "https://docs.google.com/spreadsheets/d/1Z4GDst-_he_Et8iUt2LNTbB9VWKCXmB4cblRfk4UdZE/edit?gid=0#gid=0"
connection_name = "my_gsheets_connection"

# Fetch data
data = fetch_data(connection_name, url)

# Convert 'Date' column to datetime and extract only the date part
data['Date'] = pd.to_datetime(data['Date'], errors='coerce').dt.date

data['Datetime'] = pd.to_datetime(data['Date'].astype(str) + ' ' + data['Time'], errors='coerce')

# Filter for the last 24 hours
last_24_hours = data[data['Datetime'] >= (datetime.now() - timedelta(hours=24))]


# Remove rows where 'Date' is missing or invalid
data = data.dropna(subset=['Date'])

# Convert 'Temperature(°C)' and 'Humidity(%)' to numeric
data['Temperature(°C)'] = pd.to_numeric(data['Temperature(°C)'], errors='coerce')
data['Humidity(%)'] = pd.to_numeric(data['Humidity(%)'], errors='coerce')

st.title("Temperature and Humidity Monitoring for Sri Lankan Airlines Engineering Stores")

left_column, right_column = st.columns(2)

# Function to get the latest data for a store by finding the largest row number
def get_latest_data(data, store):
    store_data = data[data['Store'] == store]
    if store_data.empty:
        return None
    latest_data = store_data.tail(1)
    return latest_data

# Function to display live data with warnings
def display_live_data(latest_data):
    if latest_data is None or latest_data.empty:
        st.warning("No data available.")
        return
    
    temperature = latest_data['Temperature(°C)'].values[0]
    humidity = latest_data['Humidity(%)'].values[0]
    
    if pd.isna(temperature) or pd.isna(humidity):
        st.error("Error: Invalid data encountered.")
        return
    
    st.metric(label="Temperature (°C)", value=f"{temperature:.2f}")
    st.metric(label="Humidity (%)", value=f"{humidity:.2f}")
    
    if temperature > 25 or temperature < 18:
        st.warning(f"Temperature is out of range! Current Temperature: {temperature:.2f}°C")
    elif abs(temperature - 25) < 2 or abs(temperature - 18) < 2:
        st.warning(f"Temperature is near threshold! Current Temperature: {temperature:.2f}°C")
    
    if humidity > 75 or humidity < 55:
        st.warning(f"Humidity is out of range! Current Humidity: {humidity:.2f}%")
    elif abs(humidity - 75) < 5 or abs(humidity - 55) < 5:
        st.warning(f"Humidity is near threshold! Current Humidity: {humidity:.2f}%")

# Function to create temperature and humidity graphs with thresholds
def create_graphs(store_data, store_name):
    if store_data.empty:
        st.warning(f"No data available for {store_name}.")
        return

    fig_temp = px.line(store_data, x='Time', y='Temperature(°C)', title=f'Temperature Over Time - {store_name}', labels={'Temperature(°C)': 'Temperature (°C)'})
    fig_temp.add_hline(y=18, line_dash="dash", line_color="red", annotation_text="Low Threshold (18°C)")
    fig_temp.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="High Threshold (25°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    fig_hum = px.line(store_data, x='Time', y='Humidity(%)', title=f'Humidity Over Time - {store_name}', labels={'Humidity(%)': 'Humidity (%)'})
    fig_hum.add_hline(y=55, line_dash="dash", line_color="blue", annotation_text="Low Threshold (55%)")
    fig_hum.add_hline(y=75, line_dash="dash", line_color="blue", annotation_text="High Threshold (75%)")
    st.plotly_chart(fig_hum, use_container_width=True)


def create_graphs(store_data, store_name):
    if store_data.empty:
        st.warning(f"No data available for {store_name}.")
        return
    
    # Filter the store data for the last 24 hours
    store_last_24_hours = store_data[store_data['Datetime'] >= (datetime.now() - timedelta(hours=24))]
    
    if store_last_24_hours.empty:
        st.warning(f"No data available for the last 24 hours for {store_name}.")
        return
    
    # Plot temperature
    fig_temp = px.line(store_last_24_hours, x='Datetime', y='Temperature(°C)', title=f'Temperature Over Time - {store_name}', labels={'Temperature(°C)': 'Temperature (°C)'})
    fig_temp.add_hline(y=18, line_dash="dash", line_color="red", annotation_text="Low Threshold (18°C)")
    fig_temp.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="High Threshold (25°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    # Plot humidity
    fig_hum = px.line(store_last_24_hours, x='Datetime', y='Humidity(%)', title=f'Humidity Over Time - {store_name}', labels={'Humidity(%)': 'Humidity (%)'})
    fig_hum.add_hline(y=55, line_dash="dash", line_color="blue", annotation_text="Low Threshold (55%)")
    fig_hum.add_hline(y=75, line_dash="dash", line_color="blue", annotation_text="High Threshold (75%)")
    st.plotly_chart(fig_hum, use_container_width=True)




with left_column:
    st.subheader("Store 1")
    store1_latest = get_latest_data(data, 'Store 1')
    display_live_data(store1_latest)
    
    with st.expander("Show Graphs"):
        store2_data = data[data['Store'] == 'Store 1']
        create_graphs(store2_data, 'Store 1')
    



with right_column:
    st.subheader("Store 2")
    store2_latest = get_latest_data(data, 'Store 2')
    display_live_data(store2_latest)
    
    with st.expander("Show Graphs"):
        store2_data = data[data['Store'] == 'Store 2']
        create_graphs(store2_data, 'Store 2')

st.write("##")

with left_column:
    st.subheader("Store 3")
    store3_latest = get_latest_data(data, 'Store 3')
    display_live_data(store3_latest)
    
    with st.expander("Show Graphs"):
        store3_data = data[data['Store'] == 'Store 3']
        create_graphs(store3_data, 'Store 3')

with right_column:
    st.subheader("Store 4")
    store4_latest = get_latest_data(data, 'Store 4')
    display_live_data(store4_latest)
    
    with st.expander("Show Graphs"):
        store4_data = data[data['Store'] == 'Store 4']
        create_graphs(store4_data, 'Store 4')

st.write("##")

with left_column:
    st.subheader("Store 5")
    store5_latest = get_latest_data(data, 'Store 5')
    display_live_data(store5_latest)
    
    with st.expander("Show Graphs"):
        store5_data = data[data['Store'] == 'Store 5']
        create_graphs(store5_data, 'Store 5')

with right_column:
    st.subheader("Store 6")
    store6_latest = get_latest_data(data, 'Store 6')
    display_live_data(store6_latest)
    
    with st.expander("Show Graphs"):
        store6_data = data[data['Store'] == 'Store 6']
        create_graphs(store6_data, 'Store 6')
st.write("##")



with left_column:
    st.subheader("Store 7")
    store5_latest = get_latest_data(data, 'Store 7')
    display_live_data(store5_latest)
    
    with st.expander("Show Graphs"):
        store5_data = data[data['Store'] == 'Store 7']
        create_graphs(store5_data, 'Store 7')

with right_column:
    st.subheader("Store 8")
    store6_latest = get_latest_data(data, 'Store 8')
    display_live_data(store6_latest)
    
    with st.expander("Show Graphs"):
        store6_data = data[data['Store'] == 'Store 8']
        create_graphs(store6_data, 'Store 8')


# Search and download functionality
st.subheader("Search and Download Data")

# Multiselect for stores
stores = data['Store'].unique().tolist()
selected_stores = st.multiselect("Select store(s)", stores, default=stores)

# Ensure min_date and max_date are valid datetime.date objects
min_date = data['Date'].min()
max_date = data['Date'].max()

# Date range input for date range
start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter data based on selected stores and date range
filtered_data = data[(data['Store'].isin(selected_stores)) & (data['Date'] >= start_date) & (data['Date'] <= end_date)]
st.dataframe(filtered_data)

if st.button('Download Searched Data as CSV'):
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv, file_name='searched_data.csv', mime='text/csv')


def reload_page():
    js = "window.location.reload();"
    st.write(f'<script>{js}</script>', unsafe_allow_html=True)

# Example button to trigger the reload
#if st.button('Reload Page'):
    
    
    # Button to clear cache and refresh data
if st.button('Refresh Data'):
    fetch_data.clear()
    st.cache_data.clear()
    st.cache_resource.clear()
    reload_page()
    st.rerun()
