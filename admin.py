import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import firebase_admin
import random
from firebase_admin import credentials, db


# Initialize Firebase Admin SDK only if it hasn't been initialized yet
if not firebase_admin._apps:
    cred = credentials.Certificate("springjal-66c38-firebase-adminsdk-fwr7z-c69d8e48bd.json")  # Replace with your credentials file
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://springjal-66c38-default-rtdb.firebaseio.com/'
    })


# Function to generate random device statistics with "Springs without IoT Devices" less than 30%
def generate_random_device_stats(num_devices, num_springs):
    active_devices = random.sample(range(1, num_devices + 1), random.randint(1, num_devices))
    max_springs_without_iot = int(num_springs * 0.3)  # Set a maximum limit for "Springs without IoT Devices"
    num_springs_without_iot = random.randint(1, max_springs_without_iot)
    springs_without_iot = random.sample(range(1, num_springs + 1), num_springs_without_iot)
    return active_devices, springs_without_iot

# Function to fetch sensor data for a specific device
def fetch_sensor_data(device_id):
    ref = db.reference(f'/springshediotdata/{device_id}')
    return ref.get()


# List of Indian states and union territories
indian_states = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 
    'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli', 
    'Daman and Diu', 'Delhi', 'Lakshadweep', 'Puducherry'
]


# Function to generate realistic random data for a given year
def generate_data(year):
    np.random.seed(year)
    dates = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='D')
    rainfall = np.random.normal(loc=5, scale=2, size=len(dates))
    rainfall[rainfall < 0] = 0
    heavy_rain_days = np.random.choice(len(dates), size=20, replace=False)
    rainfall[heavy_rain_days] *= np.random.uniform(2, 5, size=len(heavy_rain_days))
    spring_discharge = rainfall * np.random.uniform(1.5, 2.5) + np.random.normal(50, 15, len(dates))
    spring_discharge[spring_discharge < 0] = 0
    return pd.DataFrame({'Date': dates, 'Rainfall': rainfall, 'SpringDischarge': spring_discharge})


# Function to generate mock springshed data with state and district information
def generate_springshed_data():
    # Mock data with state and district - replace with actual data
    data = pd.DataFrame({
        'State': np.random.choice(indian_states, 50),
        'District': np.random.choice(['DistrictA', 'DistrictB', 'DistrictC'], 50),
        'Latitude': np.random.uniform(20, 30, 50),
        'Longitude': np.random.uniform(70, 80, 50),
        'Springsheds': np.random.randint(1, 10, 50)
    })
    return data


# Function to generate mock springshed data at different mountain ranges in India
def generate_springshed_data_indian_mountains():
    # Approximate coordinates for some Indian mountain ranges
    mountain_ranges = {
        'Himalayas': {'lat': np.random.uniform(30.0, 35.0, 15), 'lon': np.random.uniform(77.0, 80.0, 15)},
        'Western Ghats': {'lat': np.random.uniform(10.0, 15.0, 15), 'lon': np.random.uniform(76.0, 77.0, 15)},
        'Eastern Ghats': {'lat': np.random.uniform(13.0, 20.0, 15), 'lon': np.random.uniform(80.0, 83.0, 15)}  # Adjusted longitude range
    }

    data_frames = []
    for range_name, coords in mountain_ranges.items():
        df = pd.DataFrame({
            'Latitude': coords['lat'],
            'Longitude': coords['lon'],
            'Springsheds': np.random.randint(1, 10, len(coords['lat'])),
            'Range': [range_name] * len(coords['lat'])
        })
        data_frames.append(df)

    return pd.concat(data_frames, ignore_index=True)


# Set up Streamlit sidebar for feature selection
st.sidebar.title("Admin Panel")
feature_selection = st.sidebar.radio("Select a Feature", ["Rainfall vs Spring Discharge", "Springshed Availability", "Sensor Data Visualization", "Device Statistics"])


# Display content based on feature selection
if feature_selection == "Rainfall vs Spring Discharge":
    st.title('Realistic Simulation of Rainfall vs Spring Discharge')
    st.write("Select a year to visualize the rainfall and spring discharge data.")
  
    # Dropdown for year selection
    selected_year = st.sidebar.selectbox("Select Year", range(2020, 2024))

    # Generate and plot data for the selected year
    data = generate_data(selected_year)

    # Create a combo chart
    fig = go.Figure()

    # Add Bar chart for rainfall
    fig.add_trace(go.Bar(x=data['Date'], y=data['Rainfall'], name='Rainfall'))

    # Add Line chart for spring discharge
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SpringDischarge'], mode='lines', name='Spring Discharge'))

    # Update layout
    fig.update_layout(title=f'Rainfall and Spring Discharge in {selected_year}',
                      xaxis_title='Date',
                      yaxis_title='Measurement',
                      legend_title='Parameter')

    st.plotly_chart(fig)

elif feature_selection == "Springshed Availability":

    st.title('Springshed Availability in India')
    st.write("Select a state and district to visualize the availability of springsheds, or view all springsheds in Indian mountain ranges.")

    # Generate springshed data with state and district
    springshed_data = generate_springshed_data()

    # State and District selection
    selected_state = st.sidebar.selectbox("Select State", springshed_data['State'].unique())
    state_filtered_data = springshed_data[springshed_data['State'] == selected_state]
    selected_district = st.sidebar.selectbox("Select District", state_filtered_data['District'].unique())
    district_filtered_data = state_filtered_data[state_filtered_data['District'] == selected_district]

    # Button to show all springsheds
    show_all = st.button('Show All Springsheds in Indian Mountain Ranges')

    # Determine which data to display
    if show_all:
        # If button is clicked, show all springsheds in Indian mountain ranges
        data_to_display = generate_springshed_data_indian_mountains()
        map_title = "Springsheds Availability in Indian Mountain Ranges"
    else:
        # Otherwise, show filtered data
        data_to_display = district_filtered_data
        map_title = f"Springsheds Availability in {selected_district}, {selected_state}"

    # Plotting springshed availability
    fig = px.scatter_geo(data_to_display, lat='Latitude', lon='Longitude',
                         size='Springsheds',
                         hover_name='Range' if show_all else 'Springsheds',
                         projection='natural earth',
                         title=map_title,
                         scope='asia',
                         center={'lat': data_to_display['Latitude'].mean(), 'lon': data_to_display['Longitude'].mean()})
    fig.update_geos(lataxis_range=[20, 30], lonaxis_range=[70, 80])

    st.plotly_chart(fig)

elif feature_selection == "Sensor Data Visualization":
    
    st.title('IoT Sensor Data Visualization')
    st.write("Select an IoT device ID to fetch and visualize the sensor data.")

    # Dropdown for device ID
    device_ids = ["spr8561714", "spr8561714"]
    selected_device_id = st.selectbox("Select Device ID", device_ids)

    # Button to fetch data
    if st.button('Fetch Sensor Data'):
        # Fetching sensor data
        sensor_data = fetch_sensor_data(selected_device_id)
        if sensor_data:
            sensor_df = pd.DataFrame([sensor_data])
            st.write(sensor_df)  # Displaying the data in a table

            # Creating a bar chart for sensor data
            fig = px.bar(sensor_df.T, labels={'value': 'Measurement', 'index': 'Sensor'}, orientation='h')
            st.plotly_chart(fig)
        else:
            st.error("No data found for the selected device ID.")
elif feature_selection == "Device Statistics":
    st.title('Device Statistics')
    # Generate random device statistics (you can specify the number of devices and springs)
    num_devices = 50
    num_springs = 100
    active_devices, springs_without_iot = generate_random_device_stats(num_devices, num_springs)
    # Create a DataFrame for the pie chart
    device_stats_df = pd.DataFrame({
        'Category': ['Active Springsheds with IoT Devices', 'Springs without IoT Devices'],
        'Count': [len(active_devices), len(springs_without_iot)]
    })
    # Create a pie chart
    fig = px.pie(device_stats_df, values='Count', names='Category', title='Device Statistics')
    # Display the pie chart
    st.plotly_chart(fig)