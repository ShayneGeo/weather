import streamlit as st
import requests
import pandas as pd
import s3fs
import numcodecs as ncd
import numpy as np
import datetime
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pytz
from timezonefinder import TimezoneFinder
from astral import LocationInfo
from astral.sun import sun

# ---------------------------
# PAGE CONFIG & TITLE
# ---------------------------
st.set_page_config(layout="centered")
st.title("NOAA Weather + HRRR Forecast (Local Time)")

# ----------------------------------
# Default Coordinates (automatically used)
# ----------------------------------
default_lat = 40.65
default_lon = -105.307

# --------------------------
# 1. NOAA Forecast Retrieval
# --------------------------
with st.spinner("Retrieving NOAA forecast..."):
    base_url = f"https://api.weather.gov/points/{default_lat},{default_lon}"
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
                hour = start_dt.hour

                # If forecast time is between 6:00 PM and 11:59 PM, mark as "Overnight"
                if 18 <= hour <= 23:
                    display_day = f"{day_of_week} Overnight"
                else:
                    display_day = day_of_week

                temperature = period.get('temperature')
                temperature_unit = period.get('temperatureUnit')
                wind_speed = period.get('windSpeed')
                wind_direction = period.get('windDirection')
                short_forecast = period.get('shortForecast')
                prob_precip = period.get('probabilityOfPrecipitation', {}).get('value')

                forecast_list.append({
                    "Day": display_day,
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

            for idx, row in forecast_df.iterrows():
                st.markdown(f"### {row['Day']} - {row['Date & Time']}")
                st.markdown(f"**Short Forecast:** {row['Short Forecast']}")
                with st.expander("More Details"):
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
# 2. HRRR Forecast Retrieval (Last 5 Cycles)
# --------------------------------------------------
with st.spinner("Retrieving last 5 HRRR forecast cycles (no analysis)..."):
    tz_finder = TimezoneFinder()
    local_tz_name = tz_finder.timezone_at(lng=default_lon, lat=default_lat)
    if local_tz_name is None:
        local_tz_name = "UTC"
    local_tz = pytz.timezone(local_tz_name)
    now_rounded_utc = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
    now_local = now_rounded_utc.astimezone(local_tz)
    hour_block = (now_rounded_utc.hour // 6) * 6
    current_cycle_time_utc = now_rounded_utc.replace(hour=hour_block)
    cycle_times_utc = [current_cycle_time_utc - datetime.timedelta(hours=6 * i) for i in range(5)]
    cycle_times_utc.reverse()

    level_surface = 'surface'
    var_gust = 'GUST'
    var_temp = 'TMP'
    level_rh = '2m_above_ground'
    var_rh = 'RH'

    fs = s3fs.S3FileSystem(anon=True)
    chunk_index = xr.open_zarr(s3fs.S3Map("s3://hrrrzarr/grid/HRRR_chunk_index.zarr", s3=fs))
    projection = ccrs.LambertConformal(
        central_longitude=262.5,
        central_latitude=38.5,
        standard_parallels=(38.5, 38.5),
        globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229)
    )
    x, y = projection.transform_point(default_lon, default_lat, ccrs.PlateCarree())
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

    # -----------------------------
    # Retrieve GUST
    # -----------------------------
    all_forecast_gust = []
    for init_time_utc in cycle_times_utc:
        run_date_str = init_time_utc.strftime("%Y%m%d")
        run_hr_str = init_time_utc.strftime("%H")
        fcst_url = (
            f"hrrrzarr/sfc/{run_date_str}/"
            f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level_surface}/{var_gust}/{level_surface}/{var_gust}/"
        )
        try:
            forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
        except Exception as e:
            print(f"Error retrieving GUST for {init_time_utc} -> {e}")
            continue
        num_fcst_hours = forecast_data.shape[0]
        valid_times_utc = [
            (init_time_utc + datetime.timedelta(hours=i)).replace(tzinfo=pytz.utc)
            for i in range(num_fcst_hours)
        ]
        valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]
        forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
        all_forecast_gust.append((init_time_utc, valid_times_local, forecast_values))

    # -----------------------------
    # Retrieve TMP
    # -----------------------------
    all_forecast_tmp = []
    for init_time_utc in cycle_times_utc:
        run_date_str = init_time_utc.strftime("%Y%m%d")
        run_hr_str = init_time_utc.strftime("%H")
        fcst_url = (
            f"hrrrzarr/sfc/{run_date_str}/"
            f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level_surface}/{var_temp}/{level_surface}/{var_temp}/"
        )
        try:
            forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
        except Exception as e:
            print(f"Error retrieving TMP for {init_time_utc} -> {e}")
            continue
        num_fcst_hours = forecast_data.shape[0]
        valid_times_utc = [
            (init_time_utc + datetime.timedelta(hours=i)).replace(tzinfo=pytz.utc)
            for i in range(num_fcst_hours)
        ]
        valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]
        forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
        all_forecast_tmp.append((init_time_utc, valid_times_local, forecast_values))

    # -----------------------------
    # Retrieve RH
    # -----------------------------
    all_forecast_rh = []
    for init_time_utc in cycle_times_utc:
        run_date_str = init_time_utc.strftime("%Y%m%d")
        run_hr_str = init_time_utc.strftime("%H")
        fcst_url = (
            f"hrrrzarr/sfc/{run_date_str}/"
            f"{run_date_str}_{run_hr_str}z_fcst.zarr/{level_rh}/{var_rh}/{level_rh}/{var_rh}/"
        )
        try:
            forecast_data = retrieve_data(fcst_url + fcst_chunk_id)
        except Exception as e:
            print(f"Error retrieving RH for {init_time_utc} -> {e}")
            continue
        num_fcst_hours = forecast_data.shape[0]
        valid_times_utc = [
            (init_time_utc + datetime.timedelta(hours=i)).replace(tzinfo=pytz.utc)
            for i in range(num_fcst_hours)
        ]
        valid_times_local = [vt.astimezone(local_tz) for vt in valid_times_utc]
        forecast_values = forecast_data[:, nearest_point.in_chunk_y, nearest_point.in_chunk_x]
        all_forecast_rh.append((init_time_utc, valid_times_local, forecast_values))

# -----------------------------
# FIRST PLOT: GUST
# -----------------------------
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_title(
    f'HRRR {var_gust} (mph) Forecasts [Local Time]\nLat={default_lat:.2f}, Lon={default_lon:.2f} | Last 5 Cycles'
)
ax.set_xlabel('Valid Time (Local)')
ax.set_ylabel(f'{var_gust} (mph)')
colors = [
    "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3",
    "#708090","#2E8B57","#8B0000","#FFD700","#556B2F","#DC143C",
    "#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
]
conv_factor_mps_to_mph = 2.23694
max_fcst_val_gust = 0
all_times = []
for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast_gust):
    fvalues_mph = fvalues * conv_factor_mps_to_mph
    if len(fvalues_mph) > 0:
        max_fcst_val_gust = max(max_fcst_val_gust, np.nanmax(fvalues_mph))
    color = colors[i % len(colors)]
    init_time_local_str = init_time_utc.astimezone(local_tz).strftime("%m-%d %H:%M %Z")
    ax.plot(
        vtimes_local, fvalues_mph,
        color=color, marker='x', linestyle='-',
        label=f'Init {init_time_local_str}'
    )
    all_times.extend(vtimes_local)
ax.axvline(x=now_local, color='black', linestyle=':', label='Now')
if all_times:
    earliest_time = min(all_times)
    latest_time = max(all_times)
    location = LocationInfo(
        name="HRRR Location",
        region="",
        timezone=local_tz_name,
        latitude=default_lat,
        longitude=default_lon
    )
    current_date = earliest_time.date()
    last_date = latest_time.date()
    label_used = False
    while current_date <= last_date:
        s = sun(location.observer, date=current_date, tzinfo=local_tz)
        next_date = current_date + datetime.timedelta(days=1)
        s_next = sun(location.observer, date=next_date, tzinfo=local_tz)
        today_sunset = s['sunset']
        tomorrow_sunrise = s_next['sunrise']
        shade_start = max(today_sunset, earliest_time)
        shade_end = min(tomorrow_sunrise, latest_time)
        if shade_start < shade_end:
            ax.axvspan(
                shade_start, shade_end,
                facecolor='lightgray', alpha=0.3,
                label='Nighttime' if not label_used else ""
            )
            label_used = True
        current_date = next_date
ax.set_ylim(0, max_fcst_val_gust + 5 if max_fcst_val_gust else 10)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.grid(True)
fig.autofmt_xdate(rotation=45)
st.pyplot(fig)
st.success("HRRR GUST forecasts (Local Time)!")

# -----------------------------
# SECOND PLOT: TMP (Fahrenheit)
# -----------------------------
with st.spinner("Plotting HRRR temperature..."):
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.set_title(
        f'HRRR {var_temp} (°F) Forecasts [Local Time]\nLat={default_lat:.2f}, Lon={default_lon:.2f} | Last 5 Cycles'
    )
    ax2.set_xlabel('Valid Time (Local)')
    ax2.set_ylabel(f'{var_temp} (°F)')
    colors_tmp = [
        "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3",
        "#708090","#2E8B57","#8B0000","#FFD700","#556B2F","#DC143C",
        "#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
    ]
    max_fcst_val_tmp = None
    min_fcst_val_tmp = None
    all_times_tmp = []
    for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast_tmp):
        temp_values_f = (fvalues - 273.15) * 9/5 + 32
        if len(temp_values_f) > 0:
            local_min = np.nanmin(temp_values_f)
            local_max = np.nanmax(temp_values_f)
            if min_fcst_val_tmp is None or local_min < min_fcst_val_tmp:
                min_fcst_val_tmp = local_min
            if max_fcst_val_tmp is None or local_max > max_fcst_val_tmp:
                max_fcst_val_tmp = local_max
        color = colors_tmp[i % len(colors_tmp)]
        init_time_local_str = init_time_utc.astimezone(local_tz).strftime("%m-%d %H:%M %Z")
        ax2.plot(
            vtimes_local, temp_values_f,
            color=color, marker='x', linestyle='-',
            label=f'Init {init_time_local_str}'
        )
        all_times_tmp.extend(vtimes_local)
    ax2.axvline(x=now_local, color='black', linestyle=':', label='Now')
    if all_times_tmp:
        earliest_time = min(all_times_tmp)
        latest_time = max(all_times_tmp)
        location = LocationInfo(
            name="HRRR Location",
            region="",
            timezone=local_tz_name,
            latitude=default_lat,
            longitude=default_lon
        )
        current_date = earliest_time.date()
        last_date = latest_time.date()
        label_used = False
        while current_date <= last_date:
            s = sun(location.observer, date=current_date, tzinfo=local_tz)
            next_date = current_date + datetime.timedelta(days=1)
            s_next = sun(location.observer, date=next_date, tzinfo=local_tz)
            today_sunset = s['sunset']
            tomorrow_sunrise = s_next['sunrise']
            shade_start = max(today_sunset, earliest_time)
            shade_end = min(tomorrow_sunrise, latest_time)
            if shade_start < shade_end:
                ax2.axvspan(
                    shade_start, shade_end,
                    facecolor='lightgray', alpha=0.3,
                    label='Nighttime' if not label_used else ""
                )
                label_used = True
            current_date = next_date
    if max_fcst_val_tmp is not None:
        ax2.set_ylim(min_fcst_val_tmp - 10, max_fcst_val_tmp + 10)
    else:
        ax2.set_ylim(0, 100)
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax2.grid(True)
    fig2.autofmt_xdate(rotation=45)
    st.pyplot(fig2)
    st.success("HRRR Temperature (F) forecasts (Local Time)!")

# -----------------------------
# THIRD PLOT: RH (%)
# -----------------------------
with st.spinner("Plotting HRRR Relative Humidity..."):
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.set_title(
        f'HRRR {var_rh} (%) Forecasts [Local Time]\nLat={default_lat:.2f}, Lon={default_lon:.2f} | Last 5 Cycles'
    )
    ax3.set_xlabel('Valid Time (Local)')
    ax3.set_ylabel(f'{var_rh} (%)')
    colors_rh = [
        "#7A0000","#D4A017","#001F3F","#6F4518","#FF4500","#9400D3",
        "#708090","#2E8B57","#8B0000","#FFD700","#556B2F","#DC143C",
        "#4682B4","#F4A460","#A9A9A9","#5F9EA0","#FF6347"
    ]
    max_fcst_val_rh = None
    all_times_rh = []
    for i, (init_time_utc, vtimes_local, fvalues) in enumerate(all_forecast_rh):
        rh_values = fvalues
        if len(rh_values) > 0:
            local_max = np.nanmax(rh_values)
            if max_fcst_val_rh is None or local_max > max_fcst_val_rh:
                max_fcst_val_rh = local_max
        color = colors_rh[i % len(colors_rh)]
        init_time_local_str = init_time_utc.astimezone(local_tz).strftime("%m-%d %H:%M %Z")
        ax3.plot(
            vtimes_local, rh_values,
            color=color, marker='x', linestyle='-',
            label=f'Init {init_time_local_str}'
        )
        all_times_rh.extend(vtimes_local)
    ax3.axvline(x=now_local, color='black', linestyle=':', label='Now')
    if all_times_rh:
        earliest_time = min(all_times_rh)
        latest_time = max(all_times_rh)
        location = LocationInfo(
            name="HRRR Location",
            region="",
            timezone=local_tz_name,
            latitude=default_lat,
            longitude=default_lon
        )
        current_date = earliest_time.date()
        last_date = latest_time.date()
        label_used = False
        while current_date <= last_date:
            s = sun(location.observer, date=current_date, tzinfo=local_tz)
            next_date = current_date + datetime.timedelta(days=1)
            s_next = sun(location.observer, date=next_date, tzinfo=local_tz)
            today_sunset = s['sunset']
            tomorrow_sunrise = s_next['sunrise']
            shade_start = max(today_sunset, earliest_time)
            shade_end = min(tomorrow_sunrise, latest_time)
            if shade_start < shade_end:
                ax3.axvspan(
                    shade_start, shade_end,
                    facecolor='lightgray', alpha=0.3,
                    label='Nighttime' if not label_used else ""
                )
                label_used = True
            current_date = next_date
    if max_fcst_val_rh is not None:
        ax3.set_ylim(0, min(max_fcst_val_rh + 10, 100))
    else:
        ax3.set_ylim(0, 100)
    ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax3.grid(True)
    fig3.autofmt_xdate(rotation=45)
    st.pyplot(fig3)
    st.success("HRRR Relative Humidity (%) forecasts (Local Time)!")



import streamlit as st
import s3fs
import xarray as xr
import matplotlib.pyplot as plt
import os
import gc
import io
from datetime import datetime, timedelta
import pytz
from PIL import Image
import base64

# -----------------------------
# SETUP
# -----------------------------
s3 = s3fs.S3FileSystem(anon=True)
def lookup(path):
    return s3fs.S3Map(path, s3=s3)

utc_tz = pytz.utc
mountain_tz = pytz.timezone("America/Los_Angeles")  # Change as needed

# Get current time in UTC
now_utc = datetime.now(utc_tz)
# HRRR analysis runs are available at 00, 06, 12, and 18 UTC.
# Calculate the most recent run hour (rounding down to the nearest multiple of 6)
most_recent_run_hour = (now_utc.hour // 6) * 6
# Create the most recent run time in UTC
most_recent_run_utc = now_utc.replace(hour=most_recent_run_hour, minute=0, second=0, microsecond=0)
# Set end_date to the most recent HRRR run time in Mountain Time
end_date = most_recent_run_utc.astimezone(mountain_tz)
# Process data for the day prior to the most recent run day as well
start_date = end_date - timedelta(days=0)

time_steps = ["00", "06", "12", "18"]
vmin, vmax = 0, 70

# -----------------------------
# BUTTON TO GENERATE AND DISPLAY GIF
# -----------------------------
if st.button("Generate HRRR Wind Gust GIF"):
    frames = []
    with st.spinner("Generating GIF..."):
        current_date_iter = start_date
        while current_date_iter <= end_date:
            date_str = current_date_iter.strftime("%Y%m%d")
            for time in time_steps:
                st.write(f"Processing: {date_str} {time}Z")
                path = f"hrrrzarr/sfc/{date_str}/{date_str}_{time}z_anl.zarr/surface/GUST"
                try:
                    ds = xr.open_zarr(lookup(path), consolidated=False)
                    if 'GUST' not in ds:
                        ds = xr.open_zarr(lookup(f"{path}/surface"), consolidated=False)
                    ds['GUST_mph'] = ds.GUST * 2.23694
                    utc_datetime = datetime.strptime(f"{date_str} {time}", "%Y%m%d %H")
                    utc_datetime = utc_tz.localize(utc_datetime)
                    mountain_datetime = utc_datetime.astimezone(mountain_tz)
                    mt_time_str = mountain_datetime.strftime("%Y-%m-%d %I:%M %p %Z")
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ds.GUST_mph.plot(ax=ax, vmin=vmin, vmax=vmax, cmap="inferno",
                                     cbar_kwargs={"orientation": "horizontal", "pad": 0.1})
                    ax.set_title(f"HRRR Wind Gust (MPH) - {date_str} {time}Z ({mt_time_str})", fontsize=12)
                    ax.set_xlabel("Longitude")
                    ax.set_ylabel("Latitude")
                    ax.grid(False)
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png", dpi=300)
                    buf.seek(0)
                    frame = Image.open(buf).convert("RGB")
                    frames.append(frame)
                    
                    plt.close(fig)
                    buf.close()
                    ds.close()
                    del ds
                    gc.collect()
                except Exception as e:
                    st.write(f"Skipping {date_str} {time}Z due to error: {e}")
            current_date_iter += timedelta(days=1)
        if frames:
            gif_buffer = io.BytesIO()
            frames[0].save(gif_buffer, format="GIF", append_images=frames[1:], save_all=True,
                           duration=500, loop=0)
            gif_buffer.seek(0)
            # Encode the GIF to base64 so it animates in the app
            gif_base64 = base64.b64encode(gif_buffer.getvalue()).decode("utf-8")
            gif_html = f'<img src="data:image/gif;base64,{gif_base64}" alt="HRRR Wind Gust GIF" style="width:100%;">'
            st.markdown(gif_html, unsafe_allow_html=True)
            st.success("GIF generated successfully!")
        else:
            st.error("No frames were generated. GIF not created.")


