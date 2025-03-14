# THIS WORKS FOR lat long
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

#         # Send request for location information
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

#                     # Extract additional details
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     probability_of_precipitation = period.get('probabilityOfPrecipitation', {}).get('value')

#                     # Append to list, now including the detailed forecast
#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Short Forecast": short_forecast,
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Detailed Forecast": detailedForecast,
#                         "Precipitation Chance (%)": probability_of_precipitation if probability_of_precipitation is not None else "N/A"
#                     })

#                 # Convert to DataFrame and reorder columns so that "Short Forecast" is the 3rd column
#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day", 
#                     "Date & Time", 
#                     "Short Forecast", 
#                     "Detailed Forecast", 
#                     "Temperature", 
#                     "Wind Speed", 
#                     "Wind Direction", 
#                     "Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]

#                 # Display the weather data
#                 st.success("Weather forecast retrieved successfully!")
#                 st.dataframe(forecast_df)

#             else:
#                 st.error(f"Failed to retrieve forecast. Status code: {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data. Status code: {response.status_code}")

# # THIS HAS A MAP selector too
# import streamlit as st
# import requests
# import pandas as pd
# import folium
# from datetime import datetime
# from streamlit_folium import st_folium

# # App title
# st.title("🌦️ NOAA Weather Forecast App")

# # Default coordinates
# default_lat = 40.72
# default_lon = -105.33

# # User inputs for latitude and longitude (initially set to default values)
# lat_input = st.number_input("Enter Latitude", value=default_lat, format="%.6f")
# lon_input = st.number_input("Enter Longitude", value=default_lon, format="%.6f")

# # Create an interactive map with a marker at the current coordinates
# st.subheader("Click on the map to update the location")
# m = folium.Map(location=[lat_input, lon_input], zoom_start=10)
# folium.Marker([lat_input, lon_input], popup="Selected Location").add_to(m)
# map_data = st_folium(m, width=700, height=450)

# # If the user clicks on the map, update the coordinates
# if map_data and map_data.get("last_clicked"):
#     clicked_coords = map_data["last_clicked"]
#     lat_input = clicked_coords["lat"]
#     lon_input = clicked_coords["lng"]
#     st.write(f"Updated coordinates from map click: {lat_input:.6f}, {lon_input:.6f}")

# # Button to fetch weather forecast using the updated coordinates
# if st.button("Get Weather Forecast"):
#     with st.spinner("Fetching weather data..."):
#         # NOAA API URL for the given point
#         base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
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
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailedForecast,
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Precipitation Chance (%)": probability_of_precipitation if probability_of_precipitation is not None else "N/A"
#                     })

#                 # Convert to DataFrame and reorder columns
#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day", 
#                     "Date & Time", 
#                     "Short Forecast", 
#                     "Detailed Forecast", 
#                     "Temperature", 
#                     "Wind Speed", 
#                     "Wind Direction", 
#                     "Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]

#                 # Display the weather data
#                 st.success("Weather forecast retrieved successfully!")
#                 st.dataframe(forecast_df)
#             else:
#                 st.error(f"Failed to retrieve forecast. Status code: {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data. Status code: {response.status_code}")

# THIS WORKS WITH HRRR
# import streamlit as st
# import requests
# import pandas as pd
# import folium
# import s3fs
# import numcodecs as ncd
# import numpy as np
# import datetime
# import xarray as xr
# import cartopy.crs as ccrs
# import matplotlib.pyplot as plt
# from streamlit_folium import st_folium

# st.set_page_config(layout="wide")
# st.title("🌦️ Weather + HRRR GUST Data App")

# # ----------------------------------
# # Default Coordinates
# # ----------------------------------
# default_lat = 40.72
# default_lon = -105.33
# lat_input = default_lat
# lon_input = default_lon

# # ----------------------------------
# # Map Section
# # ----------------------------------
# st.markdown("#### Select Location on Map")
# m = folium.Map(location=[default_lat, default_lon], zoom_start=10)
# folium.Marker([default_lat, default_lon], popup="Default Location").add_to(m)
# map_data = st_folium(m, width=700, height=450)

# # Check if user clicked on the map
# if map_data and map_data.get("last_clicked"):
#     lat_input = map_data["last_clicked"]["lat"]
#     lon_input = map_data["last_clicked"]["lng"]

# st.write(f"**Latitude:** {lat_input:.6f}")
# st.write(f"**Longitude:** {lon_input:.6f}")

# # ----------------------------------
# # Single Button to Get All Data
# # ----------------------------------
# if st.button("Get Weather Data"):
#     # --------------------------
#     # NOAA Forecast Retrieval
#     # --------------------------
#     with st.spinner("Retrieving NOAA forecast..."):
#         base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
#         response = requests.get(base_url)
#         if response.status_code == 200:
#             noaa_data = response.json()
#             forecast_url = noaa_data["properties"]["forecast"]
#             forecast_response = requests.get(forecast_url)
#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []
#                 for period in forecast_data["properties"]["periods"]:
#                     startTime = period["startTime"]
#                     detailedForecast = period["detailedForecast"]
#                     start_dt = datetime.datetime.fromisoformat(startTime[:-6])
#                     day_of_week = start_dt.strftime("%A")
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')
#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailedForecast,
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Precipitation Chance (%)": prob_precip if prob_precip is not None else "N/A"
#                     })
#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day","Date & Time","Short Forecast","Detailed Forecast","Temperature",
#                     "Wind Speed","Wind Direction","Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]
#                 st.success("NOAA forecast retrieved successfully!")
#                 st.dataframe(forecast_df)
#             else:
#                 st.error(f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data from NOAA. Status {response.status_code}")

#     # --------------------------
#     # HRRR GUST Retrieval & Plot
#     # --------------------------
#     with st.spinner("Retrieving HRRR GUST data..."):
#         now_rounded = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
#         start_datetime = now_rounded
#         valid_end = start_datetime + datetime.timedelta(days=3)
#         level = 'surface'
#         var = 'GUST'
#         init_hours = [0, 6, 12, 18]
#         fs = s3fs.S3FileSystem(anon=True)

#         # Chunk index
#         chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
#         projection = ccrs.LambertConformal(
#             central_longitude=262.5, 
#             central_latitude=38.5, 
#             standard_parallels=(38.5, 38.5),
#             globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
#         )
#         x, y = projection.transform_point(lon_input, lat_input, ccrs.PlateCarree())
#         nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
#         fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"
#         anl_chunk_id = nearest_point.chunk_id.values

#         def retrieve_data(s3_url):
#             with fs.open(s3_url, 'rb') as compressed_data:
#                 buffer = ncd.blosc.decompress(compressed_data.read())
#             dtype = "<f4"
#             chunk = np.frombuffer(buffer, dtype=dtype)
#             entry_size = 150 * 150
#             num_entries = len(chunk) // entry_size
#             if num_entries == 1:
#                 data_array = np.reshape(chunk, (150, 150))
#             else:
#                 data_array = np.reshape(chunk, (num_entries, 150, 150))
#             return data_array

#         # Forecast data
#         forecast_results = []
#         current_date = start_datetime.date()
#         end_date = valid_end.date()
#         while current_date <= end_date:
#             for hr in init_hours:
#                 init_time = datetime.datetime.combine(current_date, datetime.time(hour=hr))
#                 if init_time < start_datetime or init_time > valid_end:
#                     continue
#                 run_date_str = init_time.strftime("%Y%m%d")
#                 run_hr_str = init_time.strftime("%H")
#                 fcst_url = (
#                     f"hrrrzarr/sfc/{run_date_str}/"
#                     f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{var}/{level}/{var}/"
#                 )
#                 try:
#                     forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#                 except Exception as e:
#                     print(f"Error retrieving forecast for {init_time}: {e}")
#                     continue
#                 num_fcst_hours = forecast_data.shape[0]
#                 valid_times = [init_time + datetime.timedelta(hours=i) for i in range(num_fcst_hours)]
#                 valid_indices = [i for i, vt in enumerate(valid_times) if start_datetime <= vt <= valid_end]
#                 if not valid_indices:
#                     continue
#                 filtered_valid_times = [valid_times[i] for i in valid_indices]
#                 forecast_values = forecast_data[valid_indices, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#                 forecast_results.append((filtered_valid_times, forecast_values, init_time))
#             current_date += datetime.timedelta(days=1)

#         # Analysis data
#         analysis_times = []
#         gridpoint_analysis = []
#         analysis_valid_end = min(valid_end, datetime.datetime.now())
#         total_hours = int((analysis_valid_end - start_datetime).total_seconds() // 3600) + 1
#         for h in range(total_hours):
#             analysis_time = start_datetime + datetime.timedelta(hours=h)
#             if analysis_time > analysis_valid_end:
#                 break
#             analysis_url = analysis_time.strftime(
#                 f"hrrrzarr/sfc/%Y%m%d/%Y%m%d_%Hz_anl.zarr/{level}/{var}/{level}/{var}/{anl_chunk_id}"
#             )
#             try:
#                 anl_data = retrieve_data(analysis_url)
#                 value = anl_data[nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             except Exception as e:
#                 print(f"Error retrieving analysis for {analysis_time}: {e}")
#                 value = np.nan
#             analysis_times.append(analysis_time)
#             gridpoint_analysis.append(value)

#         analysis_times = np.array(analysis_times)
#         gridpoint_analysis = np.array(gridpoint_analysis)
#         conv_factor = 2.23694
#         analysis_mph = gridpoint_analysis * conv_factor

#         # Plot
#         fig, ax = plt.subplots(figsize=(10, 5))
#         ax.set_title(f'HRRR {var} (mph) vs. Analysis\nLat={lat_input:.2f}, Lon={lon_input:.2f}')
#         ax.set_xlabel('Valid Time (UTC)')
#         ax.set_ylabel(f'{var} (mph)')
#         ax.plot(analysis_times, analysis_mph, color='black', linestyle='--', marker='o', label='Analysis')

#         colors = [
#             "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3","#708090","#2E8B57",
#             "#8B0000","#FFD700","#556B2F","#DC143C","#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
#         ]
#         all_forecast_mph = []
#         for i, (vtimes, fvalues, init_time) in enumerate(forecast_results):
#             fvalues_mph = fvalues * conv_factor
#             all_forecast_mph.append(fvalues_mph)
#             color = colors[i % len(colors)]
#             ax.plot(vtimes, fvalues_mph, color=color, marker='x', linestyle='-',
#                     label=f'Init {init_time.strftime("%m-%d %H:%M UTC")}')

#         max_analysis = np.nanmax(analysis_mph) if len(analysis_mph) else 0
#         max_fcst = max([np.nanmax(f) for f in all_forecast_mph]) if all_forecast_mph else 0
#         overall_max = max(max_analysis, max_fcst)
#         ax.set_ylim(0, overall_max + 7)
#         ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#         ax.grid(True)
#         fig.autofmt_xdate(rotation=45)

#         st.pyplot(fig)
#         st.success("HRRR GUST data plotted successfully!")



# # GOOD FORCAST ONLY
# import streamlit as st
# import requests
# import pandas as pd
# import folium
# import s3fs
# import numcodecs as ncd
# import numpy as np
# import datetime
# import xarray as xr
# import cartopy.crs as ccrs
# import matplotlib.pyplot as plt
# from streamlit_folium import st_folium

# st.set_page_config(layout="wide")
# st.title("🌦️ Weather + HRRR GUST Data (Forecast-Only)")

# # ----------------------------------
# # Default Coordinates
# # ----------------------------------
# default_lat = 40.72
# default_lon = -105.33
# lat_input = default_lat
# lon_input = default_lon

# # ----------------------------------
# # Map Section
# # ----------------------------------
# st.markdown("#### Select Location on Map")
# m = folium.Map(location=[default_lat, default_lon], zoom_start=10)
# folium.Marker([default_lat, default_lon], popup="Default Location").add_to(m)
# map_data = st_folium(m, width=700, height=450)

# # Check if user clicked on the map
# if map_data and map_data.get("last_clicked"):
#     lat_input = map_data["last_clicked"]["lat"]
#     lon_input = map_data["last_clicked"]["lng"]

# st.write(f"**Latitude:** {lat_input:.6f}")
# st.write(f"**Longitude:** {lon_input:.6f}")

# # ----------------------------------
# # Single Button to Get All Data
# # ----------------------------------
# if st.button("Get Weather Data"):
#     # --------------------------
#     # NOAA Forecast Retrieval
#     # --------------------------
#     with st.spinner("Retrieving NOAA forecast..."):
#         base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
#         response = requests.get(base_url)
#         if response.status_code == 200:
#             noaa_data = response.json()
#             forecast_url = noaa_data["properties"]["forecast"]
#             forecast_response = requests.get(forecast_url)
#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []
#                 for period in forecast_data["properties"]["periods"]:
#                     startTime = period["startTime"]
#                     detailedForecast = period["detailedForecast"]
#                     start_dt = datetime.datetime.fromisoformat(startTime[:-6])
#                     day_of_week = start_dt.strftime("%A")
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')
#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailedForecast,
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Precipitation Chance (%)": prob_precip if prob_precip is not None else "N/A"
#                     })
#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day","Date & Time","Short Forecast","Detailed Forecast","Temperature",
#                     "Wind Speed","Wind Direction","Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]
#                 st.success("NOAA forecast retrieved successfully!")
#                 st.dataframe(forecast_df)
#             else:
#                 st.error(f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data from NOAA. Status {response.status_code}")

#     # --------------------------
#     # HRRR GUST Forecast Retrieval & Plot (no analysis)
#     # --------------------------
#     with st.spinner("Retrieving HRRR GUST forecast data..."):
#         now_rounded = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
#         start_datetime = now_rounded
#         valid_end = start_datetime + datetime.timedelta(days=3)
#         level = 'surface'
#         var = 'GUST'
#         init_hours = [0, 6, 12, 18]
#         fs = s3fs.S3FileSystem(anon=True)

#         # Chunk index
#         chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
#         projection = ccrs.LambertConformal(
#             central_longitude=262.5, 
#             central_latitude=38.5, 
#             standard_parallels=(38.5, 38.5),
#             globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
#         )
#         x, y = projection.transform_point(lon_input, lat_input, ccrs.PlateCarree())
#         nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
#         fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

#         def retrieve_data(s3_url):
#             with fs.open(s3_url, 'rb') as compressed_data:
#                 buffer = ncd.blosc.decompress(compressed_data.read())
#             dtype = "<f4"
#             chunk = np.frombuffer(buffer, dtype=dtype)
#             entry_size = 150 * 150
#             num_entries = len(chunk) // entry_size
#             if num_entries == 1:
#                 data_array = np.reshape(chunk, (150, 150))
#             else:
#                 data_array = np.reshape(chunk, (num_entries, 150, 150))
#             return data_array

#         # Collect forecasts from multiple init times
#         forecast_results = []
#         current_date = start_datetime.date()
#         end_date = valid_end.date()
#         while current_date <= end_date:
#             for hr in init_hours:
#                 init_time = datetime.datetime.combine(current_date, datetime.time(hour=hr))
#                 if init_time < start_datetime or init_time > valid_end:
#                     continue
#                 run_date_str = init_time.strftime("%Y%m%d")
#                 run_hr_str = init_time.strftime("%H")
#                 fcst_url = (
#                     f"hrrrzarr/sfc/{run_date_str}/"
#                     f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{var}/{level}/{var}/"
#                 )
#                 try:
#                     forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#                 except Exception as e:
#                     print(f"Error retrieving forecast for {init_time}: {e}")
#                     continue
#                 num_fcst_hours = forecast_data.shape[0]
#                 valid_times = [init_time + datetime.timedelta(hours=i) for i in range(num_fcst_hours)]
#                 valid_indices = [i for i, vt in enumerate(valid_times) if start_datetime <= vt <= valid_end]
#                 if not valid_indices:
#                     continue
#                 filtered_valid_times = [valid_times[i] for i in valid_indices]
#                 forecast_values = forecast_data[valid_indices, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#                 forecast_results.append((filtered_valid_times, forecast_values, init_time))
#             current_date += datetime.timedelta(days=1)

#         # Convert to mph and plot
#         conv_factor = 2.23694
#         fig, ax = plt.subplots(figsize=(10, 5))
#         ax.set_title(f'HRRR {var} (mph) Forecasts\nLat={lat_input:.2f}, Lon={lon_input:.2f}')
#         ax.set_xlabel('Valid Time (UTC)')
#         ax.set_ylabel(f'{var} (mph)')

#         colors = [
#             "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3","#708090","#2E8B57",
#             "#8B0000","#FFD700","#556B2F","#DC143C","#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
#         ]

#         # We'll track the maximum forecast value so we can set plot bounds nicely
#         max_fcst_val = 0
#         for i, (vtimes, fvalues, init_time) in enumerate(forecast_results):
#             fvalues_mph = fvalues * conv_factor
#             max_fcst_val = max(max_fcst_val, np.nanmax(fvalues_mph))
#             color = colors[i % len(colors)]
#             ax.plot(
#                 vtimes,
#                 fvalues_mph,
#                 color=color, marker='x', linestyle='-',
#                 label=f'Init {init_time.strftime("%m-%d %H:%M UTC")}'
#             )

#         ax.set_ylim(0, max_fcst_val + 5)
#         ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#         ax.grid(True)
#         fig.autofmt_xdate(rotation=45)

#         st.pyplot(fig)
#         st.success("HRRR GUST forecasts plotted successfully!")


# # WORKS UTC
# import streamlit as st
# import requests
# import pandas as pd
# import folium
# import s3fs
# import numcodecs as ncd
# import numpy as np
# import datetime
# import xarray as xr
# import cartopy.crs as ccrs
# import matplotlib.pyplot as plt
# from streamlit_folium import st_folium

# st.set_page_config(layout="centered")
# st.title("🌦️ Weather + HRRR GUST Forecast-Only (Last 5 Cycles)")

# # ----------------------------------
# # Default Coordinates
# # ----------------------------------
# default_lat = 40.72
# default_lon = -105.33
# lat_input = default_lat
# lon_input = default_lon

# # ----------------------------------
# # Map Section
# # ----------------------------------
# st.markdown("#### Select Location on Map")
# m = folium.Map(location=[default_lat, default_lon], zoom_start=10)
# folium.Marker([default_lat, default_lon], popup="Default Location").add_to(m)
# map_data = st_folium(m, width=700, height=450)

# # Check if user clicked on the map
# if map_data and map_data.get("last_clicked"):
#     lat_input = map_data["last_clicked"]["lat"]
#     lon_input = map_data["last_clicked"]["lng"]

# st.write(f"**Latitude:** {lat_input:.6f}")
# st.write(f"**Longitude:** {lon_input:.6f}")

# # ----------------------------------
# # Single Button to Get NOAA + HRRR
# # ----------------------------------
# if st.button("Get Weather Data"):
#     # --------------------------
#     # 1. NOAA Forecast Retrieval
#     # --------------------------
#     with st.spinner("Retrieving NOAA forecast..."):
#         base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
#         response = requests.get(base_url)
#         if response.status_code == 200:
#             noaa_data = response.json()
#             forecast_url = noaa_data["properties"]["forecast"]
#             forecast_response = requests.get(forecast_url)
#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []
#                 for period in forecast_data["properties"]["periods"]:
#                     startTime = period["startTime"]
#                     detailedForecast = period["detailedForecast"]
#                     start_dt = datetime.datetime.fromisoformat(startTime[:-6])
#                     day_of_week = start_dt.strftime("%A")
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')

#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailedForecast,
#                         "Temperature": (
#                             f"{temperature} {temperature_unit}" 
#                             if temperature and temperature_unit 
#                             else "N/A"
#                         ),
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Precipitation Chance (%)": (
#                             prob_precip if prob_precip is not None else "N/A"
#                         )
#                     })

#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day", "Date & Time", "Short Forecast", "Detailed Forecast",
#                     "Temperature", "Wind Speed", "Wind Direction", "Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]
#                 st.success("NOAA forecast retrieved successfully!")
#                 st.dataframe(forecast_df)
#             else:
#                 st.error(f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data from NOAA. Status {response.status_code}")

#     # --------------------------------------------------
#     # 2. HRRR GUST Forecast Retrieval (Last 5 Cycles)
#     # --------------------------------------------------
#     with st.spinner("Retrieving last 5 HRRR forecast cycles (no analysis)..."):
#         # Round current time to the previous whole hour
#         now_rounded = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)

#         # Determine which HRRR cycle is current (0,6,12,18)
#         # e.g. if hour=13, cycle=12
#         hour_block = (now_rounded.hour // 6) * 6
#         current_cycle_time = now_rounded.replace(hour=hour_block)

#         # Build a list of the last 5 cycles (including current)
#         # Step backward by 6 hours each time
#         cycle_times = [current_cycle_time - datetime.timedelta(hours=6 * i) for i in range(5)]
#         cycle_times.reverse()  # oldest to newest

#         level = 'surface'
#         var = 'GUST'
#         fs = s3fs.S3FileSystem(anon=True)

#         # Load HRRR grid index
#         chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
#         projection = ccrs.LambertConformal(
#             central_longitude=262.5, 
#             central_latitude=38.5, 
#             standard_parallels=(38.5, 38.5),
#             globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
#         )

#         # Find nearest model gridpoint
#         x, y = projection.transform_point(lon_input, lat_input, ccrs.PlateCarree())
#         nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
#         fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

#         def retrieve_data(s3_url):
#             with fs.open(s3_url, 'rb') as compressed_data:
#                 buffer = ncd.blosc.decompress(compressed_data.read())
#             dtype = "<f4"
#             chunk = np.frombuffer(buffer, dtype=dtype)
#             entry_size = 150 * 150
#             num_entries = len(chunk) // entry_size
#             if num_entries == 1:
#                 data_array = np.reshape(chunk, (150, 150))
#             else:
#                 data_array = np.reshape(chunk, (num_entries, 150, 150))
#             return data_array

#         # For each cycle, retrieve forecast data
#         all_forecast = []
#         for init_time in cycle_times:
#             run_date_str = init_time.strftime("%Y%m%d")
#             run_hr_str = init_time.strftime("%H")

#             fcst_url = (
#                 f"hrrrzarr/sfc/{run_date_str}/"
#                 f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{var}/{level}/{var}/"
#             )
#             try:
#                 forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#             except Exception as e:
#                 print(f"Error retrieving forecast for {init_time} -> {e}")
#                 continue

#             # The number of forecast hours in this model run
#             num_fcst_hours = forecast_data.shape[0]
#             # Build valid times from init_time
#             valid_times = [init_time + datetime.timedelta(hours=i) for i in range(num_fcst_hours)]
#             # Extract the forecast values for the nearest gridpoint
#             forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             all_forecast.append((init_time, valid_times, forecast_values))

#         # Plot each cycle's forecast
#         fig, ax = plt.subplots(figsize=(10, 5))
#         ax.set_title(
#             f'HRRR {var} (mph) Forecasts\n'
#             f'Lat={lat_input:.2f}, Lon={lon_input:.2f} | Last 5 Cycles'
#         )
#         ax.set_xlabel('Valid Time (UTC)')
#         ax.set_ylabel(f'{var} (mph)')

#         # Colors for each cycle line
#         colors = [
#             "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3","#708090","#2E8B57",
#             "#8B0000","#FFD700","#556B2F","#DC143C","#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
#         ]

#         conv_factor = 2.23694
#         max_fcst_val = 0

#         for i, (init_time, vtimes, fvalues) in enumerate(all_forecast):
#             fvalues_mph = fvalues * conv_factor
#             max_fcst_val = max(max_fcst_val, np.nanmax(fvalues_mph))
#             color = colors[i % len(colors)]
#             ax.plot(
#                 vtimes, fvalues_mph,
#                 color=color, marker='x', linestyle='-',
#                 label=f'Init {init_time.strftime("%m-%d %H:%M UTC")}'
#             )

#         # Add vertical line for "now"
#         ax.axvline(x=now_rounded, color='black', linestyle=':', label='Now')

#         ax.set_ylim(0, max_fcst_val + 5)
#         ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#         ax.grid(True)
#         fig.autofmt_xdate(rotation=45)

#         st.pyplot(fig)
#         st.success("HRRR GUST forecasts (last 5 cycles) plotted successfully!")
# WORKS !!

# # WORKS WITH LOCAL TIME
# import streamlit as st
# import requests
# import pandas as pd
# import folium
# import s3fs
# import numcodecs as ncd
# import numpy as np
# import datetime
# import xarray as xr
# import cartopy.crs as ccrs
# import matplotlib.pyplot as plt
# from streamlit_folium import st_folium

# # *** NEW IMPORTS FOR LOCAL TIME ***
# import pytz
# from timezonefinder import TimezoneFinder

# st.set_page_config(layout="centered")
# st.title("🌦️ Weather + HRRR GUST Forecast-Only (Last 5 Cycles, Local Time)")

# # ----------------------------------
# # Default Coordinates
# # ----------------------------------
# default_lat = 40.72
# default_lon = -105.33
# lat_input = default_lat
# lon_input = default_lon

# # ----------------------------------
# # Map Section
# # ----------------------------------
# st.markdown("#### Select Location on Map")
# m = folium.Map(location=[default_lat, default_lon], zoom_start=10)
# folium.Marker([default_lat, default_lon], popup="Default Location").add_to(m)
# map_data = st_folium(m, width=700, height=450)

# # Check if user clicked on the map
# if map_data and map_data.get("last_clicked"):
#     lat_input = map_data["last_clicked"]["lat"]
#     lon_input = map_data["last_clicked"]["lng"]

# st.write(f"**Latitude:** {lat_input:.6f}")
# st.write(f"**Longitude:** {lon_input:.6f}")

# # ----------------------------------
# # Single Button to Get NOAA + HRRR
# # ----------------------------------
# if st.button("Get Weather Data"):
#     # --------------------------
#     # 1. NOAA Forecast Retrieval
#     # --------------------------
#     with st.spinner("Retrieving NOAA forecast..."):
#         base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
#         response = requests.get(base_url)
#         if response.status_code == 200:
#             noaa_data = response.json()
#             forecast_url = noaa_data["properties"]["forecast"]
#             forecast_response = requests.get(forecast_url)
#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []
#                 for period in forecast_data["properties"]["periods"]:
#                     startTime = period["startTime"]
#                     detailedForecast = period["detailedForecast"]
                    
#                     # Convert the startTime to a Python datetime
#                     start_dt = datetime.datetime.fromisoformat(startTime[:-6])
#                     day_of_week = start_dt.strftime("%A")
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')

#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailedForecast,
#                         "Temperature": (
#                             f"{temperature} {temperature_unit}" 
#                             if temperature and temperature_unit 
#                             else "N/A"
#                         ),
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Precipitation Chance (%)": (
#                             prob_precip if prob_precip is not None else "N/A"
#                         )
#                     })

#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day", "Date & Time", "Short Forecast", "Detailed Forecast",
#                     "Temperature", "Wind Speed", "Wind Direction", "Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]
#                 st.success("NOAA forecast retrieved successfully!")
#                 st.dataframe(forecast_df)
#             else:
#                 st.error(f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data from NOAA. Status {response.status_code}")

#     # --------------------------------------------------
#     # 2. HRRR GUST Forecast Retrieval (Last 5 Cycles)
#     #    *** NOW SHIFTED TO LOCAL TIME LABELING ***
#     # --------------------------------------------------
#     with st.spinner("Retrieving last 5 HRRR forecast cycles (no analysis)..."):
#         # --- Get local time zone from lat/lon ---
#         tz_finder = TimezoneFinder()
#         local_tz_name = tz_finder.timezone_at(lng=lon_input, lat=lat_input)
#         if local_tz_name is None:
#             local_tz_name = "UTC"
#         local_tz = pytz.timezone(local_tz_name)

#         # Round current time (UTC) to the previous whole hour
#         now_rounded_utc = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
#         # Also get local "now" for plotting the vertical line
#         now_rounded_utc = now_rounded_utc.replace(tzinfo=pytz.utc)
#         now_local = now_rounded_utc.astimezone(local_tz)

#         # Determine which HRRR cycle is current (0,6,12,18)
#         hour_block = (now_rounded_utc.hour // 6) * 6
#         current_cycle_time_utc = now_rounded_utc.replace(hour=hour_block)

#         # Build a list of the last 5 cycles (including current), step backward by 6 hours
#         cycle_times_utc = [current_cycle_time_utc - datetime.timedelta(hours=6 * i) for i in range(5)]
#         cycle_times_utc.reverse()  # oldest to newest

#         level = 'surface'
#         var = 'GUST'
#         fs = s3fs.S3FileSystem(anon=True)
#         chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
#         projection = ccrs.LambertConformal(
#             central_longitude=262.5, 
#             central_latitude=38.5, 
#             standard_parallels=(38.5, 38.5),
#             globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
#         )

#         x, y = projection.transform_point(lon_input, lat_input, ccrs.PlateCarree())
#         nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
#         fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

#         def retrieve_data(s3_url):
#             with fs.open(s3_url, 'rb') as compressed_data:
#                 buffer = ncd.blosc.decompress(compressed_data.read())
#             dtype = "<f4"
#             chunk = np.frombuffer(buffer, dtype=dtype)
#             entry_size = 150 * 150
#             num_entries = len(chunk) // entry_size
#             if num_entries == 1:
#                 data_array = np.reshape(chunk, (150, 150))
#             else:
#                 data_array = np.reshape(chunk, (num_entries, 150, 150))
#             return data_array

#         all_forecast = []
#         for init_time_utc in cycle_times_utc:
#             run_date_str = init_time_utc.strftime("%Y%m%d")
#             run_hr_str = init_time_utc.strftime("%H")

#             fcst_url = (
#                 f"hrrrzarr/sfc/{run_date_str}/"
#                 f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{var}/{level}/{var}/"
#             )
#             try:
#                 forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#             except Exception as e:
#                 print(f"Error retrieving forecast for {init_time_utc} -> {e}")
#                 continue

#             num_fcst_hours = forecast_data.shape[0]
#             # valid times in UTC (naive), then attach UTC tz
#             valid_times_utc = [
#                 (init_time_utc + datetime.timedelta(hours=i)).replace(tzinfo=pytz.utc) 
#                 for i in range(num_fcst_hours)
#             ]
#             # convert each to local
#             valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]

#             forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             all_forecast.append((init_time_utc, valid_times_local, forecast_values))

#         # --- Plot each cycle's forecast in local time ---
#         fig, ax = plt.subplots(figsize=(10, 5))
#         ax.set_title(
#             f'HRRR {var} (mph) Forecasts [Local Time]\n'
#             f'Lat={lat_input:.2f}, Lon={lon_input:.2f} | Last 5 Cycles'
#         )
#         ax.set_xlabel('Valid Time (Local)')
#         ax.set_ylabel(f'{var} (mph)')

#         colors = [
#             "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3","#708090","#2E8B57",
#             "#8B0000","#FFD700","#556B2F","#DC143C","#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
#         ]

#         conv_factor = 2.23694
#         max_fcst_val = 0

#         for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast):
#             fvalues_mph = fvalues * conv_factor
#             max_fcst_val = max(max_fcst_val, np.nanmax(fvalues_mph))
#             color = colors[i % len(colors)]
#             # Also label init_time in local
#             init_time_local_str = init_time_utc.astimezone(local_tz).strftime("%m-%d %H:%M %Z")
#             ax.plot(
#                 vtimes_local, fvalues_mph,
#                 color=color, marker='x', linestyle='-',
#                 label=f'Init {init_time_local_str}'
#             )

#         # Add vertical line for "Now" (Local)
#         ax.axvline(x=now_local, color='black', linestyle=':', label='Now')
#         ax.set_ylim(0, max_fcst_val + 5)
#         ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#         ax.grid(True)
#         fig.autofmt_xdate(rotation=45)

#         st.pyplot(fig)
#         st.success("HRRR GUST forecasts (last 5 cycles) plotted successfully (Local Time)!")
# # WORKS FOR LOCAL 


# # WORKS WITH CLENA LAYOUT
# import streamlit as st
# import requests
# import pandas as pd
# import folium
# import s3fs
# import numcodecs as ncd
# import numpy as np
# import datetime
# import xarray as xr
# import cartopy.crs as ccrs
# import matplotlib.pyplot as plt
# from streamlit_folium import st_folium

# # *** NEW IMPORTS FOR LOCAL TIME ***
# import pytz
# from timezonefinder import TimezoneFinder

# st.set_page_config(layout="centered")
# st.title("🌦️ Weather + HRRR GUST Forecast-Only (Last 5 Cycles, Local Time)")

# # ----------------------------------
# # Default Coordinates
# # ----------------------------------
# default_lat = 40.72
# default_lon = -105.33
# lat_input = default_lat
# lon_input = default_lon

# # ----------------------------------
# # Map Section
# # ----------------------------------
# st.markdown("#### Select Location on Map")
# m = folium.Map(location=[default_lat, default_lon], zoom_start=10)
# folium.Marker([default_lat, default_lon], popup="Default Location").add_to(m)
# map_data = st_folium(m, width=700, height=450)

# if map_data and map_data.get("last_clicked"):
#     lat_input = map_data["last_clicked"]["lat"]
#     lon_input = map_data["last_clicked"]["lng"]

# st.write(f"**Latitude:** {lat_input:.6f}")
# st.write(f"**Longitude:** {lon_input:.6f}")

# if st.button("Get Weather Data"):
#     # --------------------------
#     # 1. NOAA Forecast Retrieval
#     # --------------------------
#     with st.spinner("Retrieving NOAA forecast..."):
#         base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
#         response = requests.get(base_url)
#         if response.status_code == 200:
#             noaa_data = response.json()
#             forecast_url = noaa_data["properties"]["forecast"]
#             forecast_response = requests.get(forecast_url)
#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []

#                 for period in forecast_data["properties"]["periods"]:
#                     startTime = period["startTime"]
#                     detailedForecast = period["detailedForecast"]
                    
#                     start_dt = datetime.datetime.fromisoformat(startTime[:-6])
#                     day_of_week = start_dt.strftime("%A")
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')

#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailedForecast,
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Precipitation Chance (%)": prob_precip if prob_precip is not None else "N/A"
#                     })

#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day", "Date & Time", "Short Forecast", "Detailed Forecast",
#                     "Temperature", "Wind Speed", "Wind Direction", "Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]
                
#                 # --- COOL DISPLAY APPROACH ---
#                 # Instead of st.dataframe(forecast_df), let's display each row in a neat "card-like" format.
#                 st.success("NOAA forecast retrieved successfully!")
#                 for idx, row in forecast_df.iterrows():
#                     st.markdown("---")
#                     st.markdown(f"**{row['Day']} - {row['Date & Time']}**")
#                     st.markdown(f"- **Short Forecast:** {row['Short Forecast']}")
#                     st.markdown(f"- **Detailed Forecast:** {row['Detailed Forecast']}")
#                     st.markdown(f"- **Temperature:** {row['Temperature']}")
#                     st.markdown(f"- **Wind Speed:** {row['Wind Speed']}")
#                     st.markdown(f"- **Wind Direction:** {row['Wind Direction']}")
#                     st.markdown(f"- **Precipitation Chance (%):** {row['Precipitation Chance (%)']}")
                
#             else:
#                 st.error(f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data from NOAA. Status {response.status_code}")

#     # --------------------------------------------------
#     # 2. HRRR GUST Forecast Retrieval (Last 5 Cycles)
#     # --------------------------------------------------
#     with st.spinner("Retrieving last 5 HRRR forecast cycles (no analysis)..."):
#         # Timezone
#         tz_finder = TimezoneFinder()
#         local_tz_name = tz_finder.timezone_at(lng=lon_input, lat=lat_input)
#         if local_tz_name is None:
#             local_tz_name = "UTC"
#         local_tz = pytz.timezone(local_tz_name)

#         now_rounded_utc = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
#         now_local = now_rounded_utc.astimezone(local_tz)

#         hour_block = (now_rounded_utc.hour // 6) * 6
#         current_cycle_time_utc = now_rounded_utc.replace(hour=hour_block)

#         cycle_times_utc = [current_cycle_time_utc - datetime.timedelta(hours=6 * i) for i in range(5)]
#         cycle_times_utc.reverse()

#         level = 'surface'
#         var = 'GUST'
#         fs = s3fs.S3FileSystem(anon=True)
#         chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
#         projection = ccrs.LambertConformal(
#             central_longitude=262.5, 
#             central_latitude=38.5, 
#             standard_parallels=(38.5, 38.5),
#             globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
#         )
#         x, y = projection.transform_point(lon_input, lat_input, ccrs.PlateCarree())
#         nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
#         fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

#         def retrieve_data(s3_url):
#             with fs.open(s3_url, 'rb') as compressed_data:
#                 buffer = ncd.blosc.decompress(compressed_data.read())
#             dtype = "<f4"
#             chunk = np.frombuffer(buffer, dtype=dtype)
#             entry_size = 150 * 150
#             num_entries = len(chunk) // entry_size
#             if num_entries == 1:
#                 data_array = np.reshape(chunk, (150, 150))
#             else:
#                 data_array = np.reshape(chunk, (num_entries, 150, 150))
#             return data_array

#         all_forecast = []
#         for init_time_utc in cycle_times_utc:
#             run_date_str = init_time_utc.strftime("%Y%m%d")
#             run_hr_str = init_time_utc.strftime("%H")

#             fcst_url = (
#                 f"hrrrzarr/sfc/{run_date_str}/"
#                 f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{var}/{level}/{var}/"
#             )
#             try:
#                 forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#             except Exception as e:
#                 print(f"Error retrieving forecast for {init_time_utc} -> {e}")
#                 continue

#             num_fcst_hours = forecast_data.shape[0]
#             valid_times_utc = [(init_time_utc + datetime.timedelta(hours=i)).replace(tzinfo=pytz.utc) for i in range(num_fcst_hours)]
#             valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]

#             forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             all_forecast.append((init_time_utc, valid_times_local, forecast_values))

#         fig, ax = plt.subplots(figsize=(10, 5))
#         ax.set_title(
#             f'HRRR {var} (mph) Forecasts [Local Time]\n'
#             f'Lat={lat_input:.2f}, Lon={lon_input:.2f} | Last 5 Cycles'
#         )
#         ax.set_xlabel('Valid Time (Local)')
#         ax.set_ylabel(f'{var} (mph)')

#         colors = [
#             "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3","#708090","#2E8B57",
#             "#8B0000","#FFD700","#556B2F","#DC143C","#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
#         ]

#         conv_factor = 2.23694
#         max_fcst_val = 0

#         for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast):
#             fvalues_mph = fvalues * conv_factor
#             max_fcst_val = max(max_fcst_val, np.nanmax(fvalues_mph))
#             color = colors[i % len(colors)]
#             init_time_local_str = init_time_utc.astimezone(local_tz).strftime("%m-%d %H:%M %Z")
#             ax.plot(
#                 vtimes_local, fvalues_mph,
#                 color=color, marker='x', linestyle='-',
#                 label=f'Init {init_time_local_str}'
#             )

#         ax.axvline(x=now_local, color='black', linestyle=':', label='Now')
#         ax.set_ylim(0, max_fcst_val + 5)
#         ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#         ax.grid(True)
#         fig.autofmt_xdate(rotation=45)

#         st.pyplot(fig)
#         st.success("HRRR GUST forecasts (last 5 cycles) plotted successfully (Local Time)!")


# import streamlit as st
# import requests
# import pandas as pd
# import folium
# import s3fs
# import numcodecs as ncd
# import numpy as np
# import datetime
# import xarray as xr
# import cartopy.crs as ccrs
# import matplotlib.pyplot as plt
# from streamlit_folium import st_folium

# # *** NEW IMPORTS FOR LOCAL TIME ***
# import pytz
# from timezonefinder import TimezoneFinder

# st.set_page_config(layout="centered")
# st.title("🌦️ Weather + HRRR GUST Forecast-Only (Last 5 Cycles, Local Time)")

# # ----------------------------------
# # Default Coordinates
# # ----------------------------------
# default_lat = 40.72
# default_lon = -105.33
# lat_input = default_lat
# lon_input = default_lon

# # ----------------------------------
# # Map Section
# # ----------------------------------
# st.markdown("#### Select Location on Map")
# m = folium.Map(location=[default_lat, default_lon], zoom_start=10)
# folium.Marker([default_lat, default_lon], popup="Default Location").add_to(m)
# map_data = st_folium(m, width=700, height=450)

# if map_data and map_data.get("last_clicked"):
#     lat_input = map_data["last_clicked"]["lat"]
#     lon_input = map_data["last_clicked"]["lng"]

# st.write(f"**Latitude:** {lat_input:.6f}")
# st.write(f"**Longitude:** {lon_input:.6f}")

# if st.button("Get Weather Data"):
#     # --------------------------
#     # 1. NOAA Forecast Retrieval
#     # --------------------------
#     with st.spinner("Retrieving NOAA forecast..."):
#         base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
#         response = requests.get(base_url)
#         if response.status_code == 200:
#             noaa_data = response.json()
#             forecast_url = noaa_data["properties"]["forecast"]
#             forecast_response = requests.get(forecast_url)
#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []

#                 for period in forecast_data["properties"]["periods"]:
#                     startTime = period["startTime"]
#                     detailedForecast = period["detailedForecast"]
                    
#                     start_dt = datetime.datetime.fromisoformat(startTime[:-6])
#                     day_of_week = start_dt.strftime("%A")
#                     temperature = period.get('temperature')
#                     temperature_unit = period.get('temperatureUnit')
#                     wind_speed = period.get('windSpeed')
#                     wind_direction = period.get('windDirection')
#                     short_forecast = period.get('shortForecast')
#                     prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')

#                     forecast_list.append({
#                         "Day": day_of_week,
#                         "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailedForecast,
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed,
#                         "Wind Direction": wind_direction,
#                         "Precipitation Chance (%)": prob_precip if prob_precip is not None else "N/A"
#                     })

#                 forecast_df = pd.DataFrame(forecast_list)
#                 columns_order = [
#                     "Day", "Date & Time", "Short Forecast", "Detailed Forecast",
#                     "Temperature", "Wind Speed", "Wind Direction", "Precipitation Chance (%)"
#                 ]
#                 forecast_df = forecast_df[columns_order]
                
#                 st.success("NOAA forecast retrieved successfully!")

#                 # --- Display each row in an expander ("accordion") so the user can click to open/close ---
#                 for idx, row in forecast_df.iterrows():
#                     title = f"{row['Day']} - {row['Date & Time']}"
#                     with st.expander(title):
#                         st.markdown(f"**Short Forecast:** {row['Short Forecast']}")
#                         st.markdown(f"**Detailed Forecast:** {row['Detailed Forecast']}")
#                         st.markdown(f"**Temperature:** {row['Temperature']}")
#                         st.markdown(f"**Wind Speed:** {row['Wind Speed']}")
#                         st.markdown(f"**Wind Direction:** {row['Wind Direction']}")
#                         st.markdown(f"**Precipitation Chance (%):** {row['Precipitation Chance (%)']}")

#             else:
#                 st.error(f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}")
#         else:
#             st.error(f"Failed to retrieve location data from NOAA. Status {response.status_code}")

#     # --------------------------------------------------
#     # 2. HRRR GUST Forecast Retrieval (Last 5 Cycles)
#     # --------------------------------------------------
#     with st.spinner("Retrieving last 5 HRRR forecast cycles (no analysis)..."):
#         # Timezone
#         tz_finder = TimezoneFinder()
#         local_tz_name = tz_finder.timezone_at(lng=lon_input, lat=lat_input)
#         if local_tz_name is None:
#             local_tz_name = "UTC"
#         local_tz = pytz.timezone(local_tz_name)

#         now_rounded_utc = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
#         now_local = now_rounded_utc.astimezone(local_tz)

#         hour_block = (now_rounded_utc.hour // 6) * 6
#         current_cycle_time_utc = now_rounded_utc.replace(hour=hour_block)

#         cycle_times_utc = [current_cycle_time_utc - datetime.timedelta(hours=6 * i) for i in range(5)]
#         cycle_times_utc.reverse()

#         level = 'surface'
#         var = 'GUST'
#         fs = s3fs.S3FileSystem(anon=True)
#         chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
#         projection = ccrs.LambertConformal(
#             central_longitude=262.5, 
#             central_latitude=38.5, 
#             standard_parallels=(38.5, 38.5),
#             globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
#         )
#         x, y = projection.transform_point(lon_input, lat_input, ccrs.PlateCarree())
#         nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
#         fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

#         def retrieve_data(s3_url):
#             with fs.open(s3_url, 'rb') as compressed_data:
#                 buffer = ncd.blosc.decompress(compressed_data.read())
#             dtype = "<f4"
#             chunk = np.frombuffer(buffer, dtype=dtype)
#             entry_size = 150 * 150
#             num_entries = len(chunk) // entry_size
#             if num_entries == 1:
#                 data_array = np.reshape(chunk, (150, 150))
#             else:
#                 data_array = np.reshape(chunk, (num_entries, 150, 150))
#             return data_array

#         all_forecast = []
#         for init_time_utc in cycle_times_utc:
#             run_date_str = init_time_utc.strftime("%Y%m%d")
#             run_hr_str = init_time_utc.strftime("%H")

#             fcst_url = (
#                 f"hrrrzarr/sfc/{run_date_str}/"
#                 f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{var}/{level}/{var}/"
#             )
#             try:
#                 forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#             except Exception as e:
#                 print(f"Error retrieving forecast for {init_time_utc} -> {e}")
#                 continue

#             num_fcst_hours = forecast_data.shape[0]
#             valid_times_utc = [(init_time_utc + datetime.timedelta(hours=i)).replace(tzinfo=pytz.utc) for i in range(num_fcst_hours)]
#             valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]

#             forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             all_forecast.append((init_time_utc, valid_times_local, forecast_values))

#         fig, ax = plt.subplots(figsize=(10, 5))
#         ax.set_title(
#             f'HRRR {var} (mph) Forecasts [Local Time]\n'
#             f'Lat={lat_input:.2f}, Lon={lon_input:.2f} | Last 5 Cycles'
#         )
#         ax.set_xlabel('Valid Time (Local)')
#         ax.set_ylabel(f'{var} (mph)')

#         colors = [
#             "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3","#708090","#2E8B57",
#             "#8B0000","#FFD700","#556B2F","#DC143C","#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
#         ]

#         conv_factor = 2.23694
#         max_fcst_val = 0

#         for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast):
#             fvalues_mph = fvalues * conv_factor
#             max_fcst_val = max(max_fcst_val, np.nanmax(fvalues_mph))
#             color = colors[i % len(colors)]
#             init_time_local_str = init_time_utc.astimezone(local_tz).strftime("%m-%d %H:%M %Z")
#             ax.plot(
#                 vtimes_local, fvalues_mph,
#                 color=color, marker='x', linestyle='-',
#                 label=f'Init {init_time_local_str}'
#             )

#         ax.axvline(x=now_local, color='black', linestyle=':', label='Now')
#         ax.set_ylim(0, max_fcst_val + 5)
#         ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#         ax.grid(True)
#         fig.autofmt_xdate(rotation=45)

#         st.pyplot(fig)
#         st.success("HRRR GUST forecasts (last 5 cycles) plotted successfully (Local Time)!")

import streamlit as st
import requests
import pandas as pd
import folium
import s3fs
import numcodecs as ncd
import numpy as np
import datetime
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from streamlit_folium import st_folium

# For local time
import pytz
from timezonefinder import TimezoneFinder

# For sunrise/sunset calculation
# pip install astral
from astral import LocationInfo
from astral.sun import sun

st.set_page_config(layout="centered")
st.title("🌦️ Weather + HRRR GUST Forecast-Only (Last 5 Cycles, Local Time)")

# ----------------------------------
# Default Coordinates
# ----------------------------------
default_lat = 40.72
default_lon = -105.33
lat_input = default_lat
lon_input = default_lon

# ----------------------------------
# Map Section
# ----------------------------------
st.markdown("#### Select Location on Map")

m = folium.Map(location=[default_lat, default_lon], zoom_start=10)
folium.Marker([default_lat, default_lon], popup="Default Location").add_to(m)
map_data = st_folium(m, width=700, height=450)

if map_data and map_data.get("last_clicked"):
    lat_input = map_data["last_clicked"]["lat"]
    lon_input = map_data["last_clicked"]["lng"]

st.write(f"**Latitude:** {lat_input:.6f}")
st.write(f"**Longitude:** {lon_input:.6f}")

if st.button("Get Weather Data"):
    # --------------------------
    # 1. NOAA Forecast Retrieval
    # --------------------------
    with st.spinner("Retrieving NOAA forecast..."):
        base_url = f"https://api.weather.gov/points/{lat_input},{lon_input}"
        response = requests.get(base_url)
        if response.status_code == 200:
            noaa_data = response.json()
            forecast_url = noaa_data["properties"]["forecast"]
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                forecast_list = []

                for period in forecast_data["properties"]["periods"]:
                    startTime = period["startTime"]
                    detailedForecast = period["detailedForecast"]

                    start_dt = datetime.datetime.fromisoformat(startTime[:-6])
                    day_of_week = start_dt.strftime("%A")
                    temperature = period.get('temperature')
                    temperature_unit = period.get('temperatureUnit')
                    wind_speed = period.get('windSpeed')
                    wind_direction = period.get('windDirection')
                    short_forecast = period.get('shortForecast')
                    prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')

                    forecast_list.append({
                        "Day": day_of_week,
                        "Date & Time": start_dt.strftime('%B %d, %Y %I:%M %p'),
                        "Short Forecast": short_forecast,
                        "Detailed Forecast": detailedForecast,
                        "Temperature": f"{temperature} {temperature_unit}" if temperature and temperature_unit else "N/A",
                        "Wind Speed": wind_speed,
                        "Wind Direction": wind_direction,
                        "Precipitation Chance (%)": prob_precip if prob_precip is not None else "N/A"
                    })

                forecast_df = pd.DataFrame(forecast_list)
                columns_order = [
                    "Day", "Date & Time", "Short Forecast", "Detailed Forecast",
                    "Temperature", "Wind Speed", "Wind Direction", "Precipitation Chance (%)"
                ]
                forecast_df = forecast_df[columns_order]
                
                st.success("NOAA forecast retrieved successfully!")

                # Display each row in an expander to let the user toggle details
                for idx, row in forecast_df.iterrows():
                    title = f"{row['Day']} - {row['Date & Time']}"
                    with st.expander(title):
                        st.markdown(f"**Short Forecast:** {row['Short Forecast']}")
                        st.markdown(f"**Detailed Forecast:** {row['Detailed Forecast']}")
                        st.markdown(f"**Temperature:** {row['Temperature']}")
                        st.markdown(f"**Wind Speed:** {row['Wind Speed']}")
                        st.markdown(f"**Wind Direction:** {row['Wind Direction']}")
                        st.markdown(f"**Precipitation Chance (%):** {row['Precipitation Chance (%)']}")
            else:
                st.error(f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}")
        else:
            st.error(f"Failed to retrieve location data from NOAA. Status {response.status_code}")

    # --------------------------------------------------
    # 2. HRRR GUST Forecast Retrieval (Last 5 Cycles)
    #    + Nighttime Shading
    # --------------------------------------------------
    with st.spinner("Retrieving last 5 HRRR forecast cycles (no analysis)..."):
        tz_finder = TimezoneFinder()
        local_tz_name = tz_finder.timezone_at(lng=lon_input, lat=lat_input)
        if local_tz_name is None:
            local_tz_name = "UTC"
        local_tz = pytz.timezone(local_tz_name)

        now_rounded_utc = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
        now_local = now_rounded_utc.astimezone(local_tz)

        hour_block = (now_rounded_utc.hour // 6) * 6
        current_cycle_time_utc = now_rounded_utc.replace(hour=hour_block)

        cycle_times_utc = [current_cycle_time_utc - datetime.timedelta(hours=6 * i) for i in range(5)]
        cycle_times_utc.reverse()

        level = 'surface'
        var = 'GUST'
        fs = s3fs.S3FileSystem(anon=True)
        chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
        projection = ccrs.LambertConformal(
            central_longitude=262.5, 
            central_latitude=38.5, 
            standard_parallels=(38.5, 38.5),
            globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
        )
        x, y = projection.transform_point(lon_input, lat_input, ccrs.PlateCarree())
        nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
        fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

        def retrieve_data(s3_url):
            with fs.open(s3_url, 'rb') as compressed_data:
                buffer = ncd.blosc.decompress(compressed_data.read())
            dtype = "<f4"
            chunk = np.frombuffer(buffer, dtype=dtype)
            entry_size = 150 * 150
            num_entries = len(chunk) // entry_size
            if num_entries == 1:
                data_array = np.reshape(chunk, (150, 150))
            else:
                data_array = np.reshape(chunk, (num_entries, 150, 150))
            return data_array

        all_forecast = []
        for init_time_utc in cycle_times_utc:
            run_date_str = init_time_utc.strftime("%Y%m%d")
            run_hr_str = init_time_utc.strftime("%H")

            fcst_url = (
                f"hrrrzarr/sfc/{run_date_str}/"
                f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{var}/{level}/{var}/"
            )
            try:
                forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
            except Exception as e:
                print(f"Error retrieving forecast for {init_time_utc} -> {e}")
                continue

            num_fcst_hours = forecast_data.shape[0]
            valid_times_utc = [(init_time_utc + datetime.timedelta(hours=i)).replace(tzinfo=pytz.utc)
                               for i in range(num_fcst_hours)]
            # convert each to local
            valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]

            forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
            all_forecast.append((init_time_utc, valid_times_local, forecast_values))

        # -----------------------------
        # Plot each cycle's forecast
        # -----------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_title(
            f'HRRR {var} (mph) Forecasts [Local Time]\n'
            f'Lat={lat_input:.2f}, Lon={lon_input:.2f} | Last 5 Cycles'
        )
        ax.set_xlabel('Valid Time (Local)')
        ax.set_ylabel(f'{var} (mph)')

        colors = [
            "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3","#708090","#2E8B57",
            "#8B0000","#FFD700","#556B2F","#DC143C","#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
        ]

        conv_factor = 2.23694
        max_fcst_val = 0
        for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast):
            fvalues_mph = fvalues * conv_factor
            max_fcst_val = max(max_fcst_val, np.nanmax(fvalues_mph))
            color = colors[i % len(colors)]
            init_time_local_str = init_time_utc.astimezone(local_tz).strftime("%m-%d %H:%M %Z")
            ax.plot(
                vtimes_local, fvalues_mph,
                color=color, marker='x', linestyle='-',
                label=f'Init {init_time_local_str}'
            )

        # Add vertical line for "Now" (Local)
        ax.axvline(x=now_local, color='black', linestyle=':', label='Now')

        # ----------------------------------
        # Shade nighttime intervals in light grey
        # ----------------------------------
        # 1. Determine earliest and latest valid times
        all_times = []
        for _, vtimes, _ in all_forecast:
            all_times.extend(vtimes)
        if not all_times:
            # if for some reason we have no times, skip shading
            pass
        else:
            earliest_time = min(all_times)
            latest_time = max(all_times)

            # 2. Set up an Astral Location for sunrise/sunset
            #    astral requires lat, lon, and timezone
            location = LocationInfo(
                name="HRRR Location",
                region="",
                timezone=local_tz_name,
                latitude=lat_input,
                longitude=lon_input
            )

            # 3. Iterate over each day from earliest to latest and shade from sunset to sunrise
            current_date = earliest_time.date()
            last_date = latest_time.date()

            # We only want to label 'Nighttime' once in the legend
            label_used = False

            while current_date <= last_date:
                # Get sunrise/sunset times for this 'current_date'
                s = sun(location.observer, date=current_date, tzinfo=local_tz)
                # s['sunrise'], s['sunset'] etc. are local times
                # Next day's sunrise for bounding
                next_date = current_date + datetime.timedelta(days=1)
                s_next = sun(location.observer, date=next_date, tzinfo=local_tz)

                # If the times are within the plot range, we can clamp them
                today_sunset = s['sunset']
                tomorrow_sunrise = s_next['sunrise']

                # We want to shade from today's sunset to tomorrow's sunrise
                shade_start = max(today_sunset, earliest_time)  # clamp to earliest
                shade_end = min(tomorrow_sunrise, latest_time)  # clamp to latest

                if shade_start < shade_end:
                    ax.axvspan(
                        shade_start, shade_end,
                        facecolor='lightgray', alpha=0.3,
                        label='Nighttime' if not label_used else ""
                    )
                    label_used = True

                current_date = next_date

        ax.set_ylim(0, max_fcst_val + 5)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        fig.autofmt_xdate(rotation=45)

        st.pyplot(fig)
        st.success("HRRR GUST forecasts (Local Time)!")
#WORSK AND day and night

