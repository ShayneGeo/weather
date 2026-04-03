# import streamlit as st
# st.set_page_config(layout="wide")

# import requests
# import pandas as pd
# import s3fs
# import numcodecs as ncd
# import numpy as np
# import xarray as xr
# import cartopy.crs as ccrs
# import matplotlib.pyplot as plt
# import pytz
# from timezonefinder import TimezoneFinder
# from astral import LocationInfo
# from astral.sun import sun
# from datetime import timedelta, datetime

# # ---------------------------
# # Default Location Settings
# # ---------------------------
# default_lat = 40.65
# default_lon = -105.307

# st.title("NOAA Weather + HRRR Forecast (Local Time)")

# # ---------------------------
# # NOAA Forecast Retrieval ONLY
# # ---------------------------
# forecast_df = None
# forecast_error = None

# with st.spinner("Retrieving NOAA forecast..."):
#     try:
#         base_url = f"https://api.weather.gov/points/{default_lat},{default_lon}"
#         response = requests.get(base_url, timeout=30)
#         if response.status_code == 200:
#             noaa_data = response.json()
#             forecast_url = noaa_data["properties"]["forecast"]
#             forecast_response = requests.get(forecast_url, timeout=30)

#             if forecast_response.status_code == 200:
#                 forecast_data = forecast_response.json()
#                 forecast_list = []

#                 for period in forecast_data["properties"]["periods"]:
#                     start_time = period.get("startTime")
#                     if not start_time:
#                         continue

#                     start_dt = datetime.fromisoformat(start_time)
#                     day_name = start_dt.strftime("%A")

#                     is_daytime = bool(period.get("isDaytime", False))
#                     daypart = "Daytime" if is_daytime else "Nighttime"

#                     temperature = period.get("temperature")
#                     temperature_unit = period.get("temperatureUnit")
#                     wind_speed = period.get("windSpeed")
#                     wind_direction = period.get("windDirection")
#                     short_forecast = period.get("shortForecast", "N/A")
#                     detailed_forecast = period.get("detailedForecast", "N/A")
#                     prob_precip = period.get("probabilityOfPrecipitation", {}).get("value")

#                     forecast_list.append({
#                         "Day": day_name,
#                         "DayPart": daypart,
#                         "StartDT": start_dt,
#                         "DateLabel": start_dt.strftime("%B %d, %Y"),
#                         "TimeLabel": start_dt.strftime("%I:%M %p"),
#                         "Short Forecast": short_forecast,
#                         "Detailed Forecast": detailed_forecast,
#                         "Temperature": f"{temperature} {temperature_unit}" if temperature is not None and temperature_unit else "N/A",
#                         "Wind Speed": wind_speed if wind_speed else "N/A",
#                         "Wind Direction": wind_direction if wind_direction else "N/A",
#                         "Precipitation Chance (%)": prob_precip if prob_precip is not None else "N/A"
#                     })

#                 if forecast_list:
#                     forecast_df = pd.DataFrame(forecast_list).sort_values("StartDT").reset_index(drop=True)
#                 else:
#                     forecast_error = "NOAA forecast returned no periods."
#             else:
#                 forecast_error = f"Failed to retrieve NOAA forecast. Status {forecast_response.status_code}"
#         else:
#             forecast_error = f"Failed to retrieve location data from NOAA. Status {response.status_code}"
#     except Exception as e:
#         forecast_error = f"Error retrieving NOAA forecast: {e}"

# # ---------------------------
# # HRRR Forecast Retrieval (Last 5 Cycles)
# # ---------------------------
# with st.spinner("Retrieving last 5 HRRR forecast cycles..."):
#     tz_finder = TimezoneFinder()
#     local_tz_name = tz_finder.timezone_at(lng=default_lon, lat=default_lat)
#     if local_tz_name is None:
#         local_tz_name = "UTC"
#     local_tz = pytz.timezone(local_tz_name)

#     now_rounded_utc = datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
#     hour_block = (now_rounded_utc.hour // 6) * 6
#     current_cycle_time_utc = now_rounded_utc.replace(hour=hour_block)
#     cycle_times_utc = [current_cycle_time_utc - timedelta(hours=6 * i) for i in range(5)]
#     cycle_times_utc.reverse()

#     level_gust = "surface"
#     level_temp = "2m_above_ground"
#     level_rh = "2m_above_ground"

#     var_gust = "GUST"
#     var_temp = "TMP"
#     var_rh = "RH"

#     fs = s3fs.S3FileSystem(anon=True)
#     chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))

#     projection = ccrs.LambertConformal(
#         central_longitude=262.5,
#         central_latitude=38.5,
#         standard_parallels=(38.5, 38.5),
#         globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
#     )

#     x, y = projection.transform_point(default_lon, default_lat, ccrs.PlateCarree())
#     nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
#     fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

#     def retrieve_data(s3_url):
#         with fs.open(s3_url, "rb") as compressed_data:
#             buffer = ncd.blosc.decompress(compressed_data.read())
#         dtype = "<f4"
#         chunk = np.frombuffer(buffer, dtype=dtype)
#         entry_size = 150 * 150
#         num_entries = len(chunk) // entry_size
#         if num_entries == 1:
#             return np.reshape(chunk, (150, 150))
#         return np.reshape(chunk, (num_entries, 150, 150))

#     all_forecast_gust = []
#     for init_time_utc in cycle_times_utc:
#         run_date_str = init_time_utc.strftime("%Y%m%d")
#         run_hr_str = init_time_utc.strftime("%H")
#         fcst_url = (
#             f"hrrrzarr/sfc/{run_date_str}/"
#             f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level_gust}/{var_gust}/{level_gust}/{var_gust}/"
#         )
#         try:
#             forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#             num_fcst_hours = forecast_data.shape[0]
#             valid_times_utc = [
#                 (init_time_utc + timedelta(hours=i)).replace(tzinfo=pytz.utc)
#                 for i in range(num_fcst_hours)
#             ]
#             valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]
#             forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             all_forecast_gust.append((init_time_utc, valid_times_local, forecast_values))
#         except Exception as e:
#             print(f"Error retrieving GUST for {init_time_utc} -> {e}")

#     all_forecast_tmp = []
#     for init_time_utc in cycle_times_utc:
#         run_date_str = init_time_utc.strftime("%Y%m%d")
#         run_hr_str = init_time_utc.strftime("%H")
#         fcst_url = (
#             f"hrrrzarr/sfc/{run_date_str}/"
#             f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level_temp}/{var_temp}/{level_temp}/{var_temp}/"
#         )
#         try:
#             forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#             num_fcst_hours = forecast_data.shape[0]
#             valid_times_utc = [
#                 (init_time_utc + timedelta(hours=i)).replace(tzinfo=pytz.utc)
#                 for i in range(num_fcst_hours)
#             ]
#             valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]
#             forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             all_forecast_tmp.append((init_time_utc, valid_times_local, forecast_values))
#         except Exception as e:
#             print(f"Error retrieving TMP for {init_time_utc} -> {e}")

#     all_forecast_rh = []
#     for init_time_utc in cycle_times_utc:
#         run_date_str = init_time_utc.strftime("%Y%m%d")
#         run_hr_str = init_time_utc.strftime("%H")
#         fcst_url = (
#             f"hrrrzarr/sfc/{run_date_str}/"
#             f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level_rh}/{var_rh}/{level_rh}/{var_rh}/"
#         )
#         try:
#             forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
#             num_fcst_hours = forecast_data.shape[0]
#             valid_times_utc = [
#                 (init_time_utc + timedelta(hours=i)).replace(tzinfo=pytz.utc)
#                 for i in range(num_fcst_hours)
#             ]
#             valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]
#             forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
#             all_forecast_rh.append((init_time_utc, valid_times_local, forecast_values))
#         except Exception as e:
#             print(f"Error retrieving RH for {init_time_utc} -> {e}")

# # ---------------------------
# # Shared plotting vars
# # ---------------------------
# colors = [
#     "#7A0000", "#D4A017", "#001F3F", "#6F4518", "#FF4500", "#9400D3",
#     "#708090", "#2E8B57", "#8B0000", "#FFD700", "#556B2F", "#DC143C",
#     "#4682B4", "#F4A460", "#A9A9A9", "#5F9EA0", "#FF6347"
# ]

# now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
# now_local2 = now_utc.astimezone(local_tz)

# def add_night_shading(ax, all_times, local_tz_name, local_tz, default_lat, default_lon):
#     if not all_times:
#         return

#     earliest_time = min(all_times)
#     latest_time = max(all_times)

#     location = LocationInfo(
#         name="HRRR Location",
#         region="",
#         timezone=local_tz_name,
#         latitude=default_lat,
#         longitude=default_lon
#     )

#     current_date = earliest_time.date()
#     last_date = latest_time.date()
#     label_used = False

#     while current_date <= last_date:
#         s = sun(location.observer, date=current_date, tzinfo=local_tz)
#         next_date = current_date + timedelta(days=1)
#         s_next = sun(location.observer, date=next_date, tzinfo=local_tz)

#         today_sunset = s["sunset"]
#         tomorrow_sunrise = s_next["sunrise"]

#         shade_start = max(today_sunset, earliest_time)
#         shade_end = min(tomorrow_sunrise, latest_time)

#         if shade_start < shade_end:
#             ax.axvspan(
#                 shade_start,
#                 shade_end,
#                 facecolor="lightgray",
#                 alpha=0.3,
#                 label="Nighttime" if not label_used else ""
#             )
#             label_used = True

#         current_date = next_date

# # ---------------------------
# # GUST / TEMP / RH ON TOP
# # ---------------------------
# st.header("HRRR Forecast Plots")

# fig, ax = plt.subplots(figsize=(10, 5))
# ax.set_title(f"HRRR GUST (mph) Forecasts [Local Time]\nLat={default_lat:.2f}, Lon={default_lon:.2f} | Last 5 Cycles")
# ax.set_xlabel("Valid Time (Local)")
# ax.set_ylabel("GUST (mph)")

# conv_factor_mps_to_mph = 2.23694
# max_fcst_val_gust = 0
# all_times_gust = []

# for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast_gust):
#     fvalues_mph = fvalues * conv_factor_mps_to_mph
#     if len(fvalues_mph) > 0:
#         max_fcst_val_gust = max(max_fcst_val_gust, np.nanmax(fvalues_mph))
#     color = colors[i % len(colors)]
#     init_label = init_time_utc.strftime("%m-%d %H:%M UTC")
#     ax.plot(vtimes_local, fvalues_mph, color=color, marker="x", linestyle="-", label=f"Init {init_label}")
#     all_times_gust.extend(vtimes_local)

# ax.axvline(x=now_local2, color="black", linestyle=":", label="Now")
# add_night_shading(ax, all_times_gust, local_tz_name, local_tz, default_lat, default_lon)
# ax.set_ylim(0, max_fcst_val_gust + 5 if max_fcst_val_gust else 10)
# ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
# ax.grid(True)
# fig.autofmt_xdate(rotation=45)
# st.pyplot(fig)

# fig2, ax2 = plt.subplots(figsize=(10, 5))
# ax2.set_title(f"HRRR TMP (°F) Forecasts [Local Time]\nLat={default_lat:.2f}, Lon={default_lon:.2f} | Last 5 Cycles")
# ax2.set_xlabel("Valid Time (Local)")
# ax2.set_ylabel("TMP (°F)")

# max_fcst_val_tmp = None
# min_fcst_val_tmp = None
# all_times_tmp = []

# for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast_tmp):
#     temp_values_f = (fvalues - 273.15) * 9 / 5 + 32
#     if len(temp_values_f) > 0:
#         local_min = np.nanmin(temp_values_f)
#         local_max = np.nanmax(temp_values_f)
#         if min_fcst_val_tmp is None or local_min < min_fcst_val_tmp:
#             min_fcst_val_tmp = local_min
#         if max_fcst_val_tmp is None or local_max > max_fcst_val_tmp:
#             max_fcst_val_tmp = local_max
#     color = colors[i % len(colors)]
#     init_label = init_time_utc.strftime("%m-%d %H:%M UTC")
#     ax2.plot(vtimes_local, temp_values_f, color=color, marker="x", linestyle="-", label=f"Init {init_label}")
#     all_times_tmp.extend(vtimes_local)

# ax2.axvline(x=now_local2, color="black", linestyle=":", label="Now")
# add_night_shading(ax2, all_times_tmp, local_tz_name, local_tz, default_lat, default_lon)
# if max_fcst_val_tmp is not None:
#     ax2.set_ylim(min_fcst_val_tmp - 10, max_fcst_val_tmp + 10)
# else:
#     ax2.set_ylim(0, 100)
# ax2.legend(loc="center left", bbox_to_anchor=(1, 0.5))
# ax2.grid(True)
# fig2.autofmt_xdate(rotation=45)
# st.pyplot(fig2)

# fig3, ax3 = plt.subplots(figsize=(10, 5))
# ax3.set_title(f"HRRR RH (%) Forecasts [Local Time]\nLat={default_lat:.2f}, Lon={default_lon:.2f} | Last 5 Cycles")
# ax3.set_xlabel("Valid Time (Local)")
# ax3.set_ylabel("RH (%)")

# max_fcst_val_rh = None
# all_times_rh = []

# for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast_rh):
#     rh_values = fvalues
#     if len(rh_values) > 0:
#         local_max = np.nanmax(rh_values)
#         if max_fcst_val_rh is None or local_max > max_fcst_val_rh:
#             max_fcst_val_rh = local_max
#     color = colors[i % len(colors)]
#     init_label = init_time_utc.strftime("%m-%d %H:%M UTC")
#     ax3.plot(vtimes_local, rh_values, color=color, marker="x", linestyle="-", label=f"Init {init_label}")
#     all_times_rh.extend(vtimes_local)

# ax3.axvline(x=now_local2, color="black", linestyle=":", label="Now")
# add_night_shading(ax3, all_times_rh, local_tz_name, local_tz, default_lat, default_lon)
# if max_fcst_val_rh is not None:
#     ax3.set_ylim(0, min(max_fcst_val_rh + 10, 100))
# else:
#     ax3.set_ylim(0, 100)
# ax3.legend(loc="center left", bbox_to_anchor=(1, 0.5))
# ax3.grid(True)
# fig3.autofmt_xdate(rotation=45)
# st.pyplot(fig3)

# # ---------------------------
# # NOAA DAILY DROPDOWNS BELOW PLOTS
# # ---------------------------
# st.header("NOAA Daily Forecast")

# if forecast_df is not None and not forecast_df.empty:
#     st.success("NOAA forecast retrieved successfully!")

#     day_order = []
#     for day in forecast_df["Day"].tolist():
#         if day not in day_order:
#             day_order.append(day)

#     for day in day_order:
#         day_rows = forecast_df[forecast_df["Day"] == day].copy()
#         header_date = day_rows.iloc[0]["DateLabel"] if len(day_rows) > 0 else ""

#         with st.expander(f"{day} — {header_date}", expanded=False):
#             daypart_order = ["Daytime", "Nighttime"]

#             for part in daypart_order:
#                 part_rows = day_rows[day_rows["DayPart"] == part].sort_values("StartDT")
#                 if len(part_rows) == 0:
#                     continue

#                 for _, row in part_rows.iterrows():
#                     st.markdown(f"### {row['DayPart']}")
#                     st.markdown(f"**Start Time:** {row['TimeLabel']}")
#                     st.markdown(f"**Short Forecast:** {row['Short Forecast']}")
#                     st.markdown(f"**Detailed Forecast:** {row['Detailed Forecast']}")
#                     st.markdown(f"**Temperature:** {row['Temperature']}")
#                     st.markdown(f"**Wind Speed:** {row['Wind Speed']}")
#                     st.markdown(f"**Wind Direction:** {row['Wind Direction']}")
#                     st.markdown(f"**Precipitation Chance (%):** {row['Precipitation Chance (%)']}")
#                     st.markdown("---")
# elif forecast_error:
#     st.error(forecast_error)
# else:
#     st.warning("NOAA forecast data is not available.")

# # ---------------------------
# # TIDE SECTION AT BOTTOM
# # ---------------------------
# st.header("NOAA Tide Information")

# st.caption("Your weather location is inland, so tides use a selectable NOAA coastal station.")

# tide_station_options = {
#     "San Francisco, CA (9414290)": "9414290",
#     "Monterey, CA (9413450)": "9413450",
#     "La Jolla, CA (9410230)": "9410230",
#     "Seattle, WA (9447130)": "9447130",
#     "Boston, MA (8443970)": "8443970",
#     "Key West, FL (8724580)": "8724580",
#     "Charleston, SC (8665530)": "8665530",
#     "Honolulu, HI (1612340)": "1612340"
# }

# col1, col2 = st.columns([2, 1])
# with col1:
#     tide_station_label = st.selectbox("NOAA Tide Station", list(tide_station_options.keys()), index=0)
# with col2:
#     tide_days = st.selectbox("Days of tide forecast", [2, 3, 5], index=0)

# tide_station_id = tide_station_options[tide_station_label]

# def fetch_noaa_tide_predictions(station_id, begin_date_str, end_date_str, interval_value):
#     url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
#     params = {
#         "product": "predictions",
#         "application": "streamlit_weather_hrrr_tides",
#         "begin_date": begin_date_str,
#         "end_date": end_date_str,
#         "datum": "MLLW",
#         "station": station_id,
#         "time_zone": "lst_ldt",
#         "units": "english",
#         "interval": interval_value,
#         "format": "json"
#     }
#     response = requests.get(url, params=params, timeout=30)
#     response.raise_for_status()
#     data = response.json()
#     if "predictions" not in data:
#         raise ValueError(f"Unexpected tide response: {data}")
#     return pd.DataFrame(data["predictions"])

# with st.spinner("Retrieving NOAA tide predictions..."):
#     try:
#         today_local = datetime.now().date()
#         begin_date = today_local.strftime("%Y%m%d")
#         end_date = (today_local + timedelta(days=int(tide_days))).strftime("%Y%m%d")

#         tide_hourly_df = fetch_noaa_tide_predictions(tide_station_id, begin_date, end_date, "h")
#         tide_hilo_df = fetch_noaa_tide_predictions(tide_station_id, begin_date, end_date, "hilo")

#         if not tide_hourly_df.empty:
#             tide_hourly_df["t"] = pd.to_datetime(tide_hourly_df["t"])
#             tide_hourly_df["v"] = pd.to_numeric(tide_hourly_df["v"], errors="coerce")
#             tide_hourly_df = tide_hourly_df.sort_values("t").reset_index(drop=True)

#             fig4, ax4 = plt.subplots(figsize=(11, 5))
#             ax4.plot(tide_hourly_df["t"], tide_hourly_df["v"], linewidth=2)
#             ax4.set_title(f"Tide Predictions (ft) — {tide_station_label}")
#             ax4.set_xlabel("Local Time")
#             ax4.set_ylabel("Water Level (ft, MLLW)")
#             ax4.grid(True, alpha=0.3)
#             fig4.autofmt_xdate(rotation=45)
#             st.pyplot(fig4)

#             metric_col1, metric_col2, metric_col3 = st.columns(3)
#             with metric_col1:
#                 st.metric("Max Tide", f"{tide_hourly_df['v'].max():.2f} ft")
#             with metric_col2:
#                 st.metric("Min Tide", f"{tide_hourly_df['v'].min():.2f} ft")
#             with metric_col3:
#                 st.metric("Tide Range", f"{(tide_hourly_df['v'].max() - tide_hourly_df['v'].min()):.2f} ft")

#         if not tide_hilo_df.empty:
#             tide_hilo_df["t"] = pd.to_datetime(tide_hilo_df["t"])
#             tide_hilo_df["v"] = pd.to_numeric(tide_hilo_df["v"], errors="coerce")
#             tide_hilo_df["Type"] = tide_hilo_df["type"].map({"H": "High", "L": "Low"}).fillna(tide_hilo_df["type"])
#             tide_hilo_df["Date"] = tide_hilo_df["t"].dt.strftime("%Y-%m-%d")
#             tide_hilo_df["Time"] = tide_hilo_df["t"].dt.strftime("%I:%M %p")

#             st.subheader("High / Low Tides")
#             st.dataframe(
#                 tide_hilo_df[["Date", "Time", "Type", "v"]].rename(columns={"v": "Height (ft)"}),
#                 use_container_width=True,
#                 hide_index=True
#             )

#     except Exception as e:
#         st.error(f"Could not retrieve tide information for station {tide_station_id}: {e}")



import streamlit as st
st.set_page_config(layout="wide")

import requests
import pandas as pd
import s3fs
import numcodecs as ncd
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pytz
from astral import LocationInfo
from astral.sun import sun
from datetime import timedelta, datetime

# Based on your current app structure, but hardcoded for Panama City Beach so
# timezonefinder/cffi is removed entirely. :contentReference[oaicite:0]{index=0}

# ---------------------------
# HARD-CODED PCB SETTINGS
# ---------------------------
LOCATION_NAME = "Margaritaville Beach Cottage Resort, Panama City Beach"
DEFAULT_LAT = 30.1766
DEFAULT_LON = -85.8055
LOCAL_TZ_NAME = "America/Chicago"

st.title(f"{LOCATION_NAME} Weather App")
st.caption(f"Panama City Beach, FL • Lat {DEFAULT_LAT:.4f}, Lon {DEFAULT_LON:.4f} • Time Zone: {LOCAL_TZ_NAME}")

# ---------------------------
# CACHED HELPERS
# ---------------------------
@st.cache_resource
def get_s3_fs():
    return s3fs.S3FileSystem(anon=True)

@st.cache_resource
def get_chunk_index():
    fs = get_s3_fs()
    return xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))

@st.cache_data(ttl=1800)
def fetch_noaa_forecast(lat, lon):
    base_url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(base_url, timeout=30)
    response.raise_for_status()

    noaa_data = response.json()
    forecast_url = noaa_data["properties"]["forecast"]

    forecast_response = requests.get(forecast_url, timeout=30)
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()

    forecast_list = []
    for period in forecast_data["properties"]["periods"]:
        start_time = period.get("startTime")
        if not start_time:
            continue

        start_dt = datetime.fromisoformat(start_time)
        day_name = start_dt.strftime("%A")
        is_daytime = bool(period.get("isDaytime", False))
        daypart = "Daytime" if is_daytime else "Nighttime"

        temperature = period.get("temperature")
        temperature_unit = period.get("temperatureUnit")
        wind_speed = period.get("windSpeed")
        wind_direction = period.get("windDirection")
        short_forecast = period.get("shortForecast", "N/A")
        detailed_forecast = period.get("detailedForecast", "N/A")
        prob_precip = period.get("probabilityOfPrecipitation", {}).get("value")

        forecast_list.append({
            "Day": day_name,
            "DayPart": daypart,
            "StartDT": start_dt,
            "DateLabel": start_dt.strftime("%B %d, %Y"),
            "TimeLabel": start_dt.strftime("%I:%M %p"),
            "Short Forecast": short_forecast,
            "Detailed Forecast": detailed_forecast,
            "Temperature": f"{temperature} {temperature_unit}" if temperature is not None and temperature_unit else "N/A",
            "Wind Speed": wind_speed if wind_speed else "N/A",
            "Wind Direction": wind_direction if wind_direction else "N/A",
            "Precipitation Chance (%)": prob_precip if prob_precip is not None else "N/A"
        })

    if not forecast_list:
        return pd.DataFrame()

    return pd.DataFrame(forecast_list).sort_values("StartDT").reset_index(drop=True)

@st.cache_data(ttl=1800)
def fetch_noaa_tide_predictions(station_id, begin_date_str, end_date_str, interval_value):
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": "predictions",
        "application": "streamlit_weather_hrrr_tides",
        "begin_date": begin_date_str,
        "end_date": end_date_str,
        "datum": "MLLW",
        "station": station_id,
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": interval_value,
        "format": "json"
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "predictions" not in data:
        raise ValueError(f"Unexpected tide response: {data}")
    return pd.DataFrame(data["predictions"])

def add_night_shading(ax, all_times, local_tz_name, local_tz, lat, lon):
    if not all_times:
        return

    earliest_time = min(all_times)
    latest_time = max(all_times)

    location = LocationInfo(
        name="Forecast Location",
        region="",
        timezone=local_tz_name,
        latitude=lat,
        longitude=lon
    )

    current_date = earliest_time.date()
    last_date = latest_time.date()
    label_used = False

    while current_date <= last_date:
        s = sun(location.observer, date=current_date, tzinfo=local_tz)
        next_date = current_date + timedelta(days=1)
        s_next = sun(location.observer, date=next_date, tzinfo=local_tz)

        today_sunset = s["sunset"]
        tomorrow_sunrise = s_next["sunrise"]

        shade_start = max(today_sunset, earliest_time)
        shade_end = min(tomorrow_sunrise, latest_time)

        if shade_start < shade_end:
            ax.axvspan(
                shade_start,
                shade_end,
                facecolor="lightgray",
                alpha=0.3,
                label="Nighttime" if not label_used else ""
            )
            label_used = True

        current_date = next_date

def retrieve_hrrr_chunk_data(fs, s3_url):
    with fs.open(s3_url, "rb") as compressed_data:
        buffer = ncd.blosc.decompress(compressed_data.read())
    dtype = "<f4"
    chunk = np.frombuffer(buffer, dtype=dtype)
    entry_size = 150 * 150
    num_entries = len(chunk) // entry_size
    if num_entries == 1:
        return np.reshape(chunk, (150, 150))
    return np.reshape(chunk, (num_entries, 150, 150))

@st.cache_data(ttl=1800, show_spinner=False)
def load_hrrr_forecasts(lat, lon, n_cycles=3):
    local_tz_name = LOCAL_TZ_NAME
    local_tz = pytz.timezone(local_tz_name)

    now_rounded_utc = datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
    hour_block = (now_rounded_utc.hour // 6) * 6
    current_cycle_time_utc = now_rounded_utc.replace(hour=hour_block)
    cycle_times_utc = [current_cycle_time_utc - timedelta(hours=6 * i) for i in range(n_cycles)]
    cycle_times_utc.reverse()

    fs = get_s3_fs()
    chunk_index = get_chunk_index()

    projection = ccrs.LambertConformal(
        central_longitude=262.5,
        central_latitude=38.5,
        standard_parallels=(38.5, 38.5),
        globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
    )

    x, y = projection.transform_point(lon, lat, ccrs.PlateCarree())
    nearest_point = chunk_index.sel(x=x, y=y, method="nearest")
    fcst_chunk_id = f"0.{nearest_point.chunk_id.values}"

    vars_info = {
        "gust": ("surface", "GUST"),
        "tmp": ("2m_above_ground", "TMP"),
        "rh": ("2m_above_ground", "RH"),
    }

    results = {"gust": [], "tmp": [], "rh": []}

    for key, (level, varname) in vars_info.items():
        for init_time_utc in cycle_times_utc:
            run_date_str = init_time_utc.strftime("%Y%m%d")
            run_hr_str = init_time_utc.strftime("%H")
            fcst_url = (
                f"hrrrzarr/sfc/{run_date_str}/"
                f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level}/{varname}/{level}/{varname}/"
            )
            try:
                forecast_data = retrieve_hrrr_chunk_data(fs, fcst_url + fcst_chunk_id)
                num_fcst_hours = forecast_data.shape[0]
                valid_times_utc = [
                    (init_time_utc + timedelta(hours=i)).replace(tzinfo=pytz.utc)
                    for i in range(num_fcst_hours)
                ]
                valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]
                forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
                results[key].append((init_time_utc, valid_times_local, forecast_values))
            except Exception:
                continue

    return results, local_tz_name

# ---------------------------
# SIDEBAR CONTROLS
# ---------------------------
st.sidebar.header("Settings")
st.sidebar.markdown("Hardcoded for Panama City Beach.")
st.sidebar.write(f"Latitude: {DEFAULT_LAT}")
st.sidebar.write(f"Longitude: {DEFAULT_LON}")
st.sidebar.write(f"Timezone: {LOCAL_TZ_NAME}")
n_cycles = st.sidebar.selectbox("HRRR cycles", [2, 3, 4, 5], index=1)
load_hrrr = st.sidebar.button("Load HRRR plots")

# ---------------------------
# NOAA FORECAST
# ---------------------------
st.header("NOAA Daily Forecast")

try:
    forecast_df = fetch_noaa_forecast(DEFAULT_LAT, DEFAULT_LON)

    if forecast_df is not None and not forecast_df.empty:
        st.success("NOAA forecast retrieved successfully!")

        day_order = []
        for day in forecast_df["Day"].tolist():
            if day not in day_order:
                day_order.append(day)

        for day in day_order:
            day_rows = forecast_df[forecast_df["Day"] == day].copy()
            header_date = day_rows.iloc[0]["DateLabel"] if len(day_rows) > 0 else ""

            with st.expander(f"{day} — {header_date}", expanded=False):
                for part in ["Daytime", "Nighttime"]:
                    part_rows = day_rows[day_rows["DayPart"] == part].sort_values("StartDT")
                    if len(part_rows) == 0:
                        continue

                    for _, row in part_rows.iterrows():
                        st.markdown(f"### {row['DayPart']}")
                        st.markdown(f"**Start Time:** {row['TimeLabel']}")
                        st.markdown(f"**Short Forecast:** {row['Short Forecast']}")
                        st.markdown(f"**Detailed Forecast:** {row['Detailed Forecast']}")
                        st.markdown(f"**Temperature:** {row['Temperature']}")
                        st.markdown(f"**Wind Speed:** {row['Wind Speed']}")
                        st.markdown(f"**Wind Direction:** {row['Wind Direction']}")
                        st.markdown(f"**Precipitation Chance (%):** {row['Precipitation Chance (%)']}")
                        st.markdown("---")
    else:
        st.warning("NOAA forecast data is not available.")
except Exception as e:
    st.error(f"NOAA forecast failed: {e}")

# ---------------------------
# HRRR PLOTS
# ---------------------------
st.header("HRRR Forecast Plots")

if load_hrrr:
    with st.spinner("Loading HRRR forecasts..."):
        try:
            results, local_tz_name = load_hrrr_forecasts(DEFAULT_LAT, DEFAULT_LON, n_cycles=n_cycles)
            local_tz = pytz.timezone(local_tz_name)
            now_local = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)

            colors = [
                "#7A0000", "#D4A017", "#001F3F", "#6F4518", "#FF4500", "#9400D3",
                "#708090", "#2E8B57", "#8B0000", "#FFD700", "#556B2F", "#DC143C",
                "#4682B4", "#F4A460", "#A9A9A9", "#5F9EA0", "#FF6347"
            ]

            # GUST
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.set_title(f"HRRR GUST (mph)\nLat={DEFAULT_LAT:.2f}, Lon={DEFAULT_LON:.2f}")
            ax.set_xlabel("Valid Time (Local)")
            ax.set_ylabel("GUST (mph)")
            all_times = []
            max_val = 0

            for i, (init_time_utc, vtimes_local, fvalues) in enumerate(results["gust"]):
                vals = fvalues * 2.23694
                if len(vals) > 0:
                    max_val = max(max_val, np.nanmax(vals))
                ax.plot(
                    vtimes_local,
                    vals,
                    color=colors[i % len(colors)],
                    marker="x",
                    linestyle="-",
                    label=f"Init {init_time_utc.strftime('%m-%d %H:%M UTC')}"
                )
                all_times.extend(vtimes_local)

            ax.axvline(x=now_local, color="black", linestyle=":", label="Now")
            add_night_shading(ax, all_times, local_tz_name, local_tz, DEFAULT_LAT, DEFAULT_LON)
            ax.set_ylim(0, max_val + 5 if max_val else 10)
            ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            ax.grid(True)
            fig.autofmt_xdate(rotation=45)
            st.pyplot(fig)

            # TEMP
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.set_title(f"HRRR TMP (°F)\nLat={DEFAULT_LAT:.2f}, Lon={DEFAULT_LON:.2f}")
            ax2.set_xlabel("Valid Time (Local)")
            ax2.set_ylabel("TMP (°F)")
            all_times = []
            min_val = None
            max_val = None

            for i, (init_time_utc, vtimes_local, fvalues) in enumerate(results["tmp"]):
                vals = (fvalues - 273.15) * 9 / 5 + 32
                if len(vals) > 0:
                    local_min = np.nanmin(vals)
                    local_max = np.nanmax(vals)
                    min_val = local_min if min_val is None else min(min_val, local_min)
                    max_val = local_max if max_val is None else max(max_val, local_max)
                ax2.plot(
                    vtimes_local,
                    vals,
                    color=colors[i % len(colors)],
                    marker="x",
                    linestyle="-",
                    label=f"Init {init_time_utc.strftime('%m-%d %H:%M UTC')}"
                )
                all_times.extend(vtimes_local)

            ax2.axvline(x=now_local, color="black", linestyle=":", label="Now")
            add_night_shading(ax2, all_times, local_tz_name, local_tz, DEFAULT_LAT, DEFAULT_LON)
            if min_val is not None and max_val is not None:
                ax2.set_ylim(min_val - 10, max_val + 10)
            ax2.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            ax2.grid(True)
            fig2.autofmt_xdate(rotation=45)
            st.pyplot(fig2)

            # RH
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            ax3.set_title(f"HRRR RH (%)\nLat={DEFAULT_LAT:.2f}, Lon={DEFAULT_LON:.2f}")
            ax3.set_xlabel("Valid Time (Local)")
            ax3.set_ylabel("RH (%)")
            all_times = []
            max_val = None

            for i, (init_time_utc, vtimes_local, fvalues) in enumerate(results["rh"]):
                vals = fvalues
                if len(vals) > 0:
                    local_max = np.nanmax(vals)
                    max_val = local_max if max_val is None else max(max_val, local_max)
                ax3.plot(
                    vtimes_local,
                    vals,
                    color=colors[i % len(colors)],
                    marker="x",
                    linestyle="-",
                    label=f"Init {init_time_utc.strftime('%m-%d %H:%M UTC')}"
                )
                all_times.extend(vtimes_local)

            ax3.axvline(x=now_local, color="black", linestyle=":", label="Now")
            add_night_shading(ax3, all_times, local_tz_name, local_tz, DEFAULT_LAT, DEFAULT_LON)
            ax3.set_ylim(0, min(max_val + 10, 100) if max_val is not None else 100)
            ax3.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            ax3.grid(True)
            fig3.autofmt_xdate(rotation=45)
            st.pyplot(fig3)

        except Exception as e:
            st.error(f"HRRR load failed: {e}")
else:
    st.info("Click 'Load HRRR plots' in the sidebar to avoid heavy loading on every rerun.")

# ---------------------------
# TIDES
# ---------------------------
st.header("NOAA Tide Information")

tide_station_options = {
    "Panama City, FL (8729108)": "8729108",
    "Key West, FL (8724580)": "8724580",
    "Charleston, SC (8665530)": "8665530",
    "Boston, MA (8443970)": "8443970",
}

col1, col2 = st.columns([2, 1])
with col1:
    tide_station_label = st.selectbox("NOAA Tide Station", list(tide_station_options.keys()), index=0)
with col2:
    tide_days = st.selectbox("Days of tide forecast", [2, 3, 5], index=0)

try:
    tide_station_id = tide_station_options[tide_station_label]
    today_local = datetime.now(pytz.timezone(LOCAL_TZ_NAME)).date()
    begin_date = today_local.strftime("%Y%m%d")
    end_date = (today_local + timedelta(days=int(tide_days))).strftime("%Y%m%d")

    tide_hourly_df = fetch_noaa_tide_predictions(tide_station_id, begin_date, end_date, "h")
    tide_hilo_df = fetch_noaa_tide_predictions(tide_station_id, begin_date, end_date, "hilo")

    if not tide_hourly_df.empty:
        tide_hourly_df["t"] = pd.to_datetime(tide_hourly_df["t"])
        tide_hourly_df["v"] = pd.to_numeric(tide_hourly_df["v"], errors="coerce")
        tide_hourly_df = tide_hourly_df.sort_values("t").reset_index(drop=True)

        fig4, ax4 = plt.subplots(figsize=(11, 5))
        ax4.plot(tide_hourly_df["t"], tide_hourly_df["v"], linewidth=2)
        ax4.set_title(f"Tide Predictions (ft) — {tide_station_label}")
        ax4.set_xlabel("Local Time")
        ax4.set_ylabel("Water Level (ft, MLLW)")
        ax4.grid(True, alpha=0.3)
        fig4.autofmt_xdate(rotation=45)
        st.pyplot(fig4)

    if not tide_hilo_df.empty:
        tide_hilo_df["t"] = pd.to_datetime(tide_hilo_df["t"])
        tide_hilo_df["v"] = pd.to_numeric(tide_hilo_df["v"], errors="coerce")
        tide_hilo_df["Type"] = tide_hilo_df["type"].map({"H": "High", "L": "Low"}).fillna(tide_hilo_df["type"])
        tide_hilo_df["Date"] = tide_hilo_df["t"].dt.strftime("%Y-%m-%d")
        tide_hilo_df["Time"] = tide_hilo_df["t"].dt.strftime("%I:%M %p")

        st.dataframe(
            tide_hilo_df[["Date", "Time", "Type", "v"]].rename(columns={"v": "Height (ft)"}),
            use_container_width=True,
            hide_index=True
        )
except Exception as e:
    st.error(f"Tide load failed: {e}")

