# import streamlit as st
# import requests
# import pandas as pd
# from datetime import datetime

# # App title
# st.title("🌦️ NOAA Weather Forecast App")

# # User inputs for latitude and longitude
# latitude = st.number_input("Enter Latitude", value=40.72, format="%.6f")
# longitude = st.number_input("Enter Longitude", value=-105.33, format="%.6f")

# # Button to fetch weather
# if st.button("Get Weather Forecast"):
#     with st.spinner("Fetching weather data..."):
#         # NOAA API URL
#         base_url = f"https://api.weather.gov/points/{latitude},{longitude}"

#         # Send request
#         response = requests.get(base_url)

#         if response.status_code == 200:
#             data = response.json()
#             forecast_url = data["properties"]["forecast"]

#             # Fetch forecast data
#             forecast_response = requests.get(forecast_url)

#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []

#                 # Loop through forecast periods
#                 for period in forecast_data["properties"]["periods"]:
#                     startTime = period["startTime"]
#                     detailedForecast = period["detailedForecast"]
                    
#                     # Convert startTime to a readable format
#                     start_dt = datetime.fromisoformat(startTime[:-6])
#                     day_of_week = start_dt.strftime("%A")
#                     date_numeric = start_dt.strftime('%Y%m%d')

#                     # Extract additional details
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     probability_of_precipitation = period.get('probabilityOfPrecipitation', {}).get('value')

#                     # Append to list
#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Short Forecast": short_forecast,
#                         "Precipitation Chance (%)": probability_of_precipitation if probability_of_precipitation is not None else "N/A"
#                     })

#                 # Convert to DataFrame
#                 forecast_df = pd.DataFrame(forecast_list)

#                 # Display the weather data
#                 st.success("Weather forecast retrieved successfully!")
#                 st.dataframe(forecast_df)

#             else:
#                 st.error(f"Failed to retrieve forecast. Status code: {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data. Status code: {response.status_code}")




import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# App title
st.title("🌦️ NOAA Weather Forecast App")

# User inputs for latitude and longitude
latitude = st.number_input("Enter Latitude", value=40.72, format="%.6f")
longitude = st.number_input("Enter Longitude", value=-105.33, format="%.6f")

# Button to fetch weather
if st.button("Get Weather Forecast"):
    with st.spinner("Fetching weather data..."):
        # NOAA API URL
        base_url = f"https://api.weather.gov/points/{latitude},{longitude}"

        # Send request for location information
        response = requests.get(base_url)

        if response.status_code == 200:
            data = response.json()
            forecast_url = data["properties"]["forecast"]

            # Fetch forecast data
            forecast_response = requests.get(forecast_url)

            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                forecast_list = []

                # Loop through forecast periods
                for period in forecast_data["properties"]["periods"]:
                    startTime = period["startTime"]
                    detailedForecast = period["detailedForecast"]
                    
                    # Convert startTime to a readable format
                    start_dt = datetime.fromisoformat(startTime[:-6])
                    day_of_week = start_dt.strftime("%A")
                    date_numeric = start_dt.strftime('%Y%m%d')

                    # Extract additional details
                    temperature = period.get('temperature')
                    temperature_unit = period.get('temperatureUnit')
                    wind_speed = period.get('windSpeed')
                    wind_direction = period.get('windDirection')
                    short_forecast = period.get('shortForecast')
                    probability_of_precipitation = period.get('probabilityOfPrecipitation', {}).get('value')

                    # Append to list, now including the detailed forecast
                    forecast_list.append({
                        "Day": day_of_week,
                        "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
                        "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
                        "Wind Speed": wind_speed,
                        "Wind Direction": wind_direction,
                        "Short Forecast": short_forecast,
                        "Detailed Forecast": detailedForecast,
                        "Precipitation Chance (%)": probability_of_precipitation if probability_of_precipitation is not None else "N/A"
                    })

                # Convert to DataFrame
                forecast_df = pd.DataFrame(forecast_list)

                # Display the weather data
                st.success("Weather forecast retrieved successfully!")
                st.dataframe(forecast_df)

            else:
                st.error(f"Failed to retrieve forecast. Status code: {forecast_response.status_code}")
        else:
            st.error(f"Failed to retrieve location data. Status code: {response.status_code}")



