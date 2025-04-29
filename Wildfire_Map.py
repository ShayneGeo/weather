# THIS IS ABSOLUTLY THE ONE
import requests
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import re
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
# ------------------ SETUP ------------------
HEADERS = {"User-Agent": "fire-weather-scraper"}
session = requests.Session()
session.headers.update(HEADERS)

# ------------------ HTTP REQUEST ------------------
def safe_get(url, params=None, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1)

# ------------------ FETCH ACTIVE FIRES ------------------
def fetch_active_fires():
    url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations_Current/FeatureServer/0/query"
    resp = safe_get(url, params={"where": "1=1", "outFields": "*", "f": "geojson"})
    geojson = resp.json()
    gdf = gpd.GeoDataFrame.from_features(geojson["features"], crs="epsg:4326")
    return gdf[gdf["POOState"].isin(['US-CA', 'US-OR', 'US-WA', 'US-ID', 'US-NV', 'US-UT', 'US-AZ', 'US-NM', 'US-CO', 'US-MT', 'US-WY'])]

# ------------------ WEATHER FUNCTIONS ------------------
@lru_cache(maxsize=512)
def get_fwf_product_id(office_id):
    url = "https://api.weather.gov/products"
    resp = safe_get(url, params={"type": "FWF", "location": office_id, "limit": 1})
    products = resp.json().get("@graph", [])
    return products[0]["id"] if products else None

def point_forecast(lat, lon, max_periods=14):
    point = safe_get(f"https://api.weather.gov/points/{lat},{lon}").json()["properties"]
    forecast_url = point["forecast"]
    periods = safe_get(forecast_url).json()["properties"]["periods"][:max_periods]
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

def fwf_forecast(lat, lon):
    point = safe_get(f"https://api.weather.gov/points/{lat},{lon}").json()["properties"]
    office_id = point["forecastOffice"].split("/")[-1]
    zone_id = point["fireWeatherZone"].split("/")[-1]

    pid = get_fwf_product_id(office_id)
    if not pid:
        return {}

    text = safe_get(f"https://api.weather.gov/products/{pid}").json().get("productText", "")
    discussion_match = re.search(r"\.DISCUSSION\.\.\.\s*(.*?)\n\n", text, re.DOTALL)
    discussion = discussion_match.group(1).strip() if discussion_match else ""

    block_match = re.search(rf"\n{zone_id}-\d{{6}}-\n(.*?)(?=\n[A-Z]{{3}}\d{{3}}-\d{{6}}-|\Z)", text, re.DOTALL)
    full_forecast_block = block_match.group(1).strip() if block_match else ""

    return {"discussion": discussion, "full_forecast_block": full_forecast_block}

def process_fire(row):
    lat, lon = row.geometry.y, row.geometry.x
    pf = point_forecast(lat, lon)
    fw = fwf_forecast(lat, lon)
    return {**pf, **fw, **row._asdict()}

# ------------------ MAIN ------------------
from datetime import datetime

# ------------------ MAIN ------------------
def main():
    gdf_wgs = fetch_active_fires()

    records = []
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(process_fire, row): row for row in gdf_wgs.itertuples()}
        for future in as_completed(futures):
            try:
                records.append(future.result())
            except Exception as e:
                print(f"Failed {futures[future].IncidentName}: {e}")

    forecast_df = pd.DataFrame(records)
    forecast_df["size_scaled"] = np.log1p(forecast_df["IncidentSize"].fillna(1)) * 2

    gdf_map = gpd.GeoDataFrame(forecast_df, geometry="geometry", crs="epsg:4326")

    # ⏳ Save CSV with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    #forecast_df.to_csv(r"C:\Users\magst\OneDrive\Pictures\Desktop\NIFC_WEATHER_OUTPUTS\wildfire_forecast_2025-04-29_17-33.csv", index=False)
    # Base directory
    base_dir = r"C:\Users\magst\OneDrive\Pictures\Desktop\NIFC_WEATHER_OUTPUTS"
    
    # Save outputs with dynamic filenames
    forecast_df.to_csv(fr"{base_dir}\wildfire_forecast_{timestamp}.csv", index=False)

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
            radius=row.get('size_scaled', 0.075),
            color='red',
            fill=True,
            fill_opacity=0.3,
            popup=popup
        ).add_to(m)

    return m

if __name__ == "__main__":
    m = main()  # assign returned map
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    m.save(fr"{base_dir}\wildfire_map_{timestamp}.html")



# THIS IS ABSOLUTLY THE ONE
m
