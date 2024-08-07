import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection


import numpy as np
import pandas as pd
import plotly

# Print version information for debugging
#st.write("NumPy version:", np.__version__)
#st.write("Pandas version:", pd.__version__)
#st.write("Streamlit version:", st.__version__)
s#t.write("Plotly version:", plotly.__version__)



# Function to fetch data with caching
@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_data(connection_name, url):
    conn = st.connection(connection_name, type=GSheetsConnection)
    data = conn.read(spreadsheet=url)
    return data

# Google Spreadsheet URL and connection name
url = "https://docs.google.com/spreadsheets/d/1Z4GDst-_he_Et8iUt2LNTbB9VWKCXmB4cblRfk4UdZE/edit?gid=0#gid=0"
connection_name = "my_gsheets_connection"

# Fetch data
data = fetch_data(connection_name, url)
st.dataframe(data)

st.subheader("Stores")
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
    
    temperature = pd.to_numeric(latest_data['Temperature(°C)'].values[0], errors='coerce')
    humidity = pd.to_numeric(latest_data['Humidity(%)'].values[0], errors='coerce')
    
    #st.write(f"Debug: Current Temperature: {temperature}")
    #st.write(f"Debug: Current Humidity: {humidity}")
    
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

    # Ensure the columns are numeric
    store_data['Temperature(°C)'] = pd.to_numeric(store_data['Temperature(°C)'], errors='coerce')
    store_data['Humidity(%)'] = pd.to_numeric(store_data['Humidity(%)'], errors='coerce')

    #st.write("Debug: Temperature data type -", store_data['Temperature(°C)'].dtype)
    #st.write("Debug: Humidity data type -", store_data['Humidity(%)'].dtype)
    
    fig_temp = px.line(store_data, x='Time', y='Temperature(°C)', title=f'Temperature Over Time - {store_name}')
    fig_temp.add_hline(y=18, line_dash="dash", line_color="red", annotation_text="Low Threshold (18°C)")
    fig_temp.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="High Threshold (25°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    fig_hum = px.line(store_data, x='Time', y='Humidity(%)', title=f'Humidity Over Time - {store_name}')
    fig_hum.add_hline(y=55, line_dash="dash", line_color="blue", annotation_text="Low Threshold (55%)")
    fig_hum.add_hline(y=75, line_dash="dash", line_color="blue", annotation_text="High Threshold (75%)")
    st.plotly_chart(fig_hum, use_container_width=True)

with left_column:
    st.write("Store 1")
    store1_latest = get_latest_data(data, 'Store 1')
    display_live_data(store1_latest)
    store1_data = data[data['Store'] == 'Store 1']
    create_graphs(store1_data, 'Store 1')

with right_column:
    st.write("Store 2")
    store2_latest = get_latest_data(data, 'Store 2')
    display_live_data(store2_latest)
    store2_data = data[data['Store'] == 'Store 2']
    create_graphs(store2_data, 'Store 2')

with left_column:
    st.write("Store 3")
    store1_latest = get_latest_data(data, 'Store 3')
    display_live_data(store1_latest)
    store1_data = data[data['Store'] == 'Store 3']
    create_graphs(store1_data, 'Store 3')

with right_column:
    st.write("Store 4")
    store2_latest = get_latest_data(data, 'Store 4')
    display_live_data(store2_latest)
    store2_data = data[data['Store'] == 'Store 4']
    create_graphs(store2_data, 'Store 4')

# Button to clear cache and refresh data
if st.button('Refresh Data'):
    fetch_data.clear()
    st.rerun()
