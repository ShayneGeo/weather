# import streamlit as st
# import requests
# import pandas as pd
# import numpy as np
# import geopandas as gpd
# import folium
# import re
# from folium.plugins import MarkerCluster
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from functools import lru_cache
# from streamlit_folium import st_folium

# # 0. SESSION
# session = requests.Session()
# session.headers.update({"User-Agent": "fire-weather-scraper"})

# # 1. SAFE GET
# def safe_get(url, params=None, timeout=60, retries=3, sleep_time=2):
#     for i in range(retries):
#         try:
#             return session.get(url, params=params, timeout=timeout)
#         except requests.exceptions.RequestException:
#             time.sleep(sleep_time)
#     raise

# # 2. FETCH WFIGS
# @st.cache_data(show_spinner=True)
# def fetch_active_fires():
#     url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations_Current/FeatureServer/0/query"
#     geojson = safe_get(url, params={"where": "1=1", "outFields": "*", "f": "geojson"}).json()
#     gdf = gpd.GeoDataFrame.from_features(geojson["features"], crs="epsg:4326")
#     return gdf[gdf["POOState"].isin(['US-CA','US-OR','US-WA','US-ID','US-NV','US-UT','US-AZ','US-NM','US-CO','US-MT','US-WY'])]

# # 3. WEATHER FUNCTIONS
# @lru_cache(maxsize=128)
# def get_fwf_product_id(office_id):
#     resp = safe_get(f"https://api.weather.gov/products", params={"type": "FWF", "location": office_id, "limit": 1}).json().get("@graph", [])
#     return resp[0]["id"] if resp else None

# def point_forecast(lat, lon, max_periods=14):
#     props = safe_get(f"https://api.weather.gov/points/{lat},{lon}").json()["properties"]
#     fc_url = props["forecast"]
#     periods = safe_get(fc_url).json()["properties"]["periods"][:max_periods]
#     rec = {"latitude": lat, "longitude": lon, "forecastURL": fc_url}
#     for idx, p in enumerate(periods):
#         for key in ["temperature", "windSpeed", "windDirection", "shortForecast", "detailedForecast", "temperatureTrend", "startTime", "endTime"]:
#             rec[f"{key}_{idx}"] = p.get(key)
#         for key in ["probabilityOfPrecipitation", "relativeHumidity", "dewpoint"]:
#             value = (p.get(key) or {}).get("value")
#             if key == "probabilityOfPrecipitation" and value is None:
#                 value = 0
#             rec[f"{key}_{idx}"] = value
#     return rec

# def fwf_forecast(lat, lon):
#     props = safe_get(f"https://api.weather.gov/points/{lat},{lon}").json()["properties"]
#     office = props["forecastOffice"].split("/")[-1]
#     zone = props["fireWeatherZone"].split("/")[-1]
#     pid = get_fwf_product_id(office)
#     if not pid:
#         return {}
#     text = safe_get(f"https://api.weather.gov/products/{pid}").json().get("productText", "")
#     disc_match = re.search(r"\.DISCUSSION\.\.\.\s*(.*?)\n\n", text, re.DOTALL)
#     discussion = disc_match.group(1).strip() if disc_match else ""
#     block_match = re.search(rf"\n{zone}-\d{{6}}-\n(.*?)(?=\n[A-Z]{{3}}\d{{3}}-\d{{6}}-|\Z)", text, re.DOTALL)
#     full_forecast_block = block_match.group(1).strip() if block_match else ""
#     return {"discussion": discussion, "full_forecast_block": full_forecast_block}

# def process_fire(row):
#     lat, lon = row.geometry.y, row.geometry.x
#     with ThreadPoolExecutor(max_workers=2) as subexecutor:
#         future_pf = subexecutor.submit(point_forecast, lat, lon)
#         future_fw = subexecutor.submit(fwf_forecast, lat, lon)
#         pf = future_pf.result(timeout=30)
#         fw = future_fw.result(timeout=30)
#     return {**pf, **fw, **row._asdict()}

# # MAIN APP
# st.set_page_config(page_title="Wildfire Active Incidents", layout="wide")
# st.title("🔥 Active Wildfires in the Western U.S. (With Forecasts)")

# # Load and process data
# gdf_wgs = fetch_active_fires()

# # Button to trigger processing
# if st.button("Fetch Forecasts"):
#     with st.spinner("Fetching forecasts and building map..."):
#         records = []
#         with ThreadPoolExecutor(max_workers=32) as executor:
#             futures = {executor.submit(process_fire, row): row for row in gdf_wgs.itertuples()}
#             for future in tqdm(as_completed(futures), total=len(futures)):
#                 try:
#                     records.append(future.result())
#                 except Exception as e:
#                     st.error(f"Failed {futures[future].IncidentName}: {e}")

#         forecast_df = pd.DataFrame(records)
#         forecast_df["size_scaled"] = np.log1p(forecast_df["IncidentSize"].fillna(1)) * 2

#         gdf_map = gpd.GeoDataFrame(forecast_df, geometry="geometry", crs="epsg:4326")
#         center = [gdf_map.geometry.y.mean(), gdf_map.geometry.x.mean()]
#         m = folium.Map(location=center, zoom_start=5, tiles="CartoDB Positron", control_scale=False, zoom_control=False)

#         for _, row in gdf_map.iterrows():
#             lat, lon = row.geometry.y, row.geometry.x
#             irwin = row.get('IrwinID', row.get('IRWINID', 'N/A')).strip('{}')
#             detail = row.get('detailedForecast_0', 'No forecast available').replace('\n', '<br>')
#             html = f"""
#             <div style="font-size: 16px; line-height: 1.4;">
#                 <b>IrwinID:</b> {irwin}<br><br>
#                 {detail}
#             </div>
#             """
#             popup = folium.Popup(folium.IFrame(html=html, width=300, height=200))
#             folium.CircleMarker(
#                 location=(lat, lon),
#                 radius=row.get('size_scaled', 0.75),
#                 color='red',
#                 fill=True,
#                 fill_opacity=0.7,
#                 popup=popup
#             ).add_to(m)

#         st_folium(m, width=1400, height=800)
# 🚀 Always-Running Streamlit Wildfire Forecast Map

import asyncio
import httpx
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
import streamlit as st
from streamlit_folium import st_folium
from functools import lru_cache
import re

# ------------------ SETUP ------------------
HEADERS = {"User-Agent": "fire-weather-scraper"}
SEM = asyncio.Semaphore(100)

# ------------------ ASYNC HTTP REQUEST ------------------
async def safe_get(client, url, params=None, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            async with SEM:
                response = await client.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                return response
        except Exception:
            if attempt == retries - 1:
                return None
            await asyncio.sleep(1)

# ------------------ FETCH ACTIVE FIRES ------------------
async def fetch_active_fires(client):
    url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations_Current/FeatureServer/0/query"
    resp = await safe_get(client, url, params={"where": "1=1", "outFields": "*", "f": "geojson"})
    if resp is None:
        raise RuntimeError("Failed to fetch active fires.")
    geojson = resp.json()
    gdf = gpd.GeoDataFrame.from_features(geojson["features"], crs="epsg:4326")
    return gdf[gdf["POOState"].isin(['US-CA', 'US-OR', 'US-WA', 'US-ID', 'US-NV', 'US-UT', 'US-AZ', 'US-NM', 'US-CO', 'US-MT', 'US-WY'])]

# ------------------ WEATHER FUNCTIONS ------------------
@lru_cache(maxsize=512)
async def get_fwf_product_id(client, office_id):
    url = "https://api.weather.gov/products"
    resp = await safe_get(client, url, params={"type": "FWF", "location": office_id, "limit": 1})
    if resp is None:
        return None
    products = resp.json().get("@graph", [])
    return products[0]["id"] if products else None

async def point_forecast(client, lat, lon, max_periods=14):
    point_resp = await safe_get(client, f"https://api.weather.gov/points/{lat},{lon}")
    if point_resp is None:
        return {}

    point = point_resp.json()["properties"]
    forecast_url = point["forecast"]

    forecast_resp = await safe_get(client, forecast_url)
    if forecast_resp is None:
        return {}

    periods = forecast_resp.json()["properties"]["periods"][:max_periods]
    rec = {"latitude": lat, "longitude": lon, "forecastURL": forecast_url}
    for idx, p in enumerate(periods):
        for key in ["temperature", "windSpeed", "windDirection", "shortForecast", "detailedForecast", "temperatureTrend", "startTime", "endTime"]:
            rec[f"{key}_{idx}"] = p.get(key)
        for key in ["probabilityOfPrecipitation", "relativeHumidity", "dewpoint"]:
            value = (p.get(key) or {}).get("value")
            if key == "probabilityOfPrecipitation" and value is None:
                value = 0
            rec[f"{key}_{idx}"] = value
    return rec

async def fwf_forecast(client, lat, lon):
    point_resp = await safe_get(client, f"https://api.weather.gov/points/{lat},{lon}")
    if point_resp is None:
        return {}

    point = point_resp.json()["properties"]
    office_id = point["forecastOffice"].split("/")[-1]
    zone_id = point["fireWeatherZone"].split("/")[-1]

    pid = await get_fwf_product_id(client, office_id)
    if not pid:
        return {}

    text_resp = await safe_get(client, f"https://api.weather.gov/products/{pid}")
    if text_resp is None:
        return {}

    text = text_resp.json().get("productText", "")

    discussion_match = re.search(r"\.DISCUSSION\.\.\.\s*(.*?)\n\n", text, re.DOTALL)
    discussion = discussion_match.group(1).strip() if discussion_match else ""

    block_match = re.search(rf"\n{zone_id}-\d{{6}}-\n(.*?)(?=\n[A-Z]{{3}}\d{{3}}-\d{{6}}-|\Z)", text, re.DOTALL)
    full_forecast_block = block_match.group(1).strip() if block_match else ""

    return {"discussion": discussion, "full_forecast_block": full_forecast_block}

async def process_fire(client, row):
    lat, lon = row.geometry.y, row.geometry.x
    pf, fw = await asyncio.gather(
        point_forecast(client, lat, lon),
        fwf_forecast(client, lat, lon)
    )
    return {**pf, **fw, **row._asdict()}

# ------------------ MAIN FETCH ------------------
async def get_forecast_map():
    async with httpx.AsyncClient(headers=HEADERS) as client:
        gdf_wgs = await fetch_active_fires(client)
        tasks = [process_fire(client, row) for row in gdf_wgs.itertuples()]
        records = await asyncio.gather(*tasks, return_exceptions=False)

    forecast_df = pd.DataFrame(records)
    forecast_df["size_scaled"] = np.log1p(forecast_df["IncidentSize"].fillna(1)) * 2

    gdf_map = gpd.GeoDataFrame(forecast_df, geometry="geometry", crs="epsg:4326")
    center = [gdf_map.geometry.y.mean(), gdf_map.geometry.x.mean()]

    m = folium.Map(location=center, zoom_start=5, tiles="CartoDB Positron", control_scale=False, zoom_control=False)

    for _, row in gdf_map.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        irwin = row.get('IrwinID', row.get('IRWINID', 'N/A')).strip('{}')
        detail = row.get('detailedForecast_0', 'No forecast available').replace('\n', '<br>')
        html = f"""
        <div style="font-size: 16px; line-height: 1.4;">
            <b>IrwinID:</b> {irwin}<br><br>
            {detail}
        </div>
        """
        popup = folium.Popup(folium.IFrame(html=html, width=300, height=200))
        folium.CircleMarker(
            location=(lat, lon),
            radius=row.get('size_scaled', 0.75),
            color='red',
            fill=True,
            fill_opacity=0.7,
            popup=popup
        ).add_to(m)

    return m

# ------------------ STREAMLIT APP ------------------
st.set_page_config(page_title="🔥 Wildfire Forecasts", layout="wide")
st.title("🔥 Active Wildfires in the Western U.S. (With Forecasts)")

with st.spinner("Loading wildfires and forecasts..."):
    final_map = asyncio.run(get_forecast_map())
    st_data = st_folium(final_map, width=1400, height=800)


