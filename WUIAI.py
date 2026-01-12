# # streamlit_app_naip_wui_mapclick.py
# # Run:
# #   pip install streamlit streamlit-folium folium geopandas rasterio pystac-client planetary-computer shapely pillow numpy openai matplotlib
# #   setx OPENAI_API_KEY "YOUR_KEY"   (PowerShell: $env:OPENAI_API_KEY="YOUR_KEY")
# #   streamlit run streamlit_app_naip_wui_mapclick.py

# import os
# import json
# import math
# import base64
# from io import BytesIO

# import numpy as np
# import streamlit as st
# from PIL import Image

# import folium
# from streamlit_folium import st_folium

# import rasterio
# from rasterio.mask import mask

# from shapely.geometry import Point, box, mapping, shape
# import geopandas as gpd

# import pystac_client
# import planetary_computer

# from openai import OpenAI
# import matplotlib.pyplot as plt


# # =========================
# # DEFAULTS
# # =========================
# DEFAULT_MODEL = "gpt-4o"
# DEFAULT_SAVE_DIR = r"C:\Users\magst\Desktop\openai\SNAGHAZARD"
# DEFAULT_SIDE_M = 500  # fixed crop side length (meters)
# DEFAULT_HALF_M = DEFAULT_SIDE_M / 2

# DEFAULT_SYSTEM = "You are a land cover photo-analyst. Use only what is visible."

# DEFAULT_QUESTION = r"""
# Analyze this NAIP RGB aerial image (~0.6–1 m resolution). Use only visible information in the image. Do not assume information not directly observable.

# Context:
# This image represents a fixed-area crop (~500 m × 500 m). The task is to characterize Wildland–Urban Interface (WUI) exposure and structural defensibility indicators based on visible housing patterns, vegetation proximity, and access.

# Tasks:

# 1. Housing Presence & Density
# - Identify all visible residential structures (single-family homes, cabins, outbuildings associated with residences).
# - Estimate the number of residential structures visible.
# - Classify housing density within the image as one of:
#   • Very Low (isolated structures, >40 acres per home equivalent)
#   • Low (scattered homes, rural residential)
#   • Medium (exurban/suburban edge)
#   • High (dense suburban/urban)
# - Briefly justify using spacing and clustering visible in the image.

# 2. Vegetation Proximity & Defensible Space
# - Assess vegetation immediately surrounding structures.
# - Note whether trees and shrubs are:
#   • In direct contact with structures
#   • Within ~0–10 m
#   • Within ~10–30 m
#   • Mostly cleared beyond ~30 m
# - Based on visible cues only, classify overall defensible space as:
#   • Poor
#   • Limited
#   • Moderate
#   • Good
# - Cite concrete visual indicators (e.g., canopy overhang, ladder fuels, cleared yards, mowed areas).

# 3. WUI Classification
# - Based on housing density and surrounding wildland vegetation, classify the scene as:
#   • Not WUI
#   • Intermix WUI
#   • Interface WUI
# - Briefly explain the classification using observable patterns.

# 4. Road Network & Access
# - Identify visible roads (paved vs unpaved if distinguishable).
# - Note apparent access characteristics:
#   • Multiple access routes vs single ingress/egress
#   • Road width (narrow vs standard two-lane)
#   • Connectivity (grid vs dead-end/driveways)
# - Comment on potential access constraints for fire response based only on visibility.

# 5. Overall WUI Risk Indicator
# - Rate overall wildfire exposure risk to structures as:
#   • Low
#   • Moderate
#   • High
#   • Very High
# - Base this rating strictly on housing density, vegetation proximity, and access—do not incorporate weather, slope, or fire history unless directly visible.

# Uncertainty:
# - Provide an uncertainty score from 0–1 reflecting confidence in your assessment given image resolution, shadows, and occlusions.

# Output strictly as JSON:
# {
#   "estimated_structure_count": <integer>,
#   "housing_density_class": "<Very Low|Low|Medium|High>",
#   "defensible_space_class": "<Poor|Limited|Moderate|Good>",
#   "wui_class": "<Not WUI|Intermix WUI|Interface WUI>",
#   "road_access_notes": "<concise description>",
#   "overall_wui_risk": "<Low|Moderate|High|Very High>",
#   "evidence": "<≤75 words citing visible features>",
#   "uncertainty": <float 0–1>
# }
# """.strip()


# # =========================
# # CACHED RESOURCES
# # =========================
# @st.cache_resource
# def get_catalog():
#     return pystac_client.Client.open(
#         "https://planetarycomputer.microsoft.com/api/stac/v1",
#         modifier=planetary_computer.sign_inplace,
#     )


# # =========================
# # HELPERS
# # =========================
# def pct_scale_to_u8(rgb_arr):
#     """Percentile scale each band to uint8 (0–255) for nice visualization."""
#     if rgb_arr.dtype == np.uint8:
#         return rgb_arr
#     out = []
#     for b in range(rgb_arr.shape[0]):
#         band = rgb_arr[b].astype(np.float32)
#         lo, hi = np.nanpercentile(band, [0.0, 99.5])
#         if not np.isfinite(lo): lo = 0.0
#         if not np.isfinite(hi) or hi <= lo: hi = lo + 1.0
#         band = (np.clip((band - lo) / (hi - lo), 0, 1) * 255.0).astype(np.uint8)
#         out.append(band)
#     return np.stack(out, axis=0)

# def find_best_naip_item(catalog, lon, lat, start="2018-01-01", end="2024-01-01", pad_deg=0.001):
#     """Search NAIP scenes around lon/lat and return the item that overlaps AOI the most."""
#     aoi = {
#         "type": "Polygon",
#         "coordinates": [[
#             [lon - pad_deg, lat - pad_deg],
#             [lon + pad_deg, lat - pad_deg],
#             [lon + pad_deg, lat + pad_deg],
#             [lon - pad_deg, lat + pad_deg],
#             [lon - pad_deg, lat - pad_deg],
#         ]]
#     }
#     items = catalog.search(
#         collections=["naip"],
#         intersects=aoi,
#         datetime=f"{start}/{end}",
#     ).item_collection()

#     if not items or len(items) == 0:
#         return None, aoi

#     aoi_shape = shape(aoi)
#     items_sorted = sorted(items, key=lambda it: shape(it.geometry).intersection(aoi_shape).area, reverse=True)
#     return items_sorted[0], aoi

# def item_to_href(item):
#     href = None
#     if "image" in item.assets:
#         href = item.assets["image"].href
#     else:
#         for a in item.assets.values():
#             if a.href.lower().endswith((".tif", ".tiff")):
#                 href = a.href
#                 break
#     return href

# def crop_naip_at_point(href, lon, lat, half_m=DEFAULT_HALF_M):
#     """Returns PIL image crop, and crop bounds in src CRS (for debug/overlay)."""
#     with rasterio.open(href) as src:
#         pt = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs=4326).to_crs(src.crs)
#         cx, cy = pt.geometry.iloc[0].x, pt.geometry.iloc[0].y
#         crop_box = box(cx - half_m, cy - half_m, cx + half_m, cy + half_m)
#         crop_geom = [mapping(crop_box)]
#         data, _ = mask(src, crop_geom, crop=True)

#         if data.shape[0] >= 3:
#             rgb = data[:3, :, :]
#         else:
#             rgb = np.repeat(data[0:1, :, :], 3, axis=0)

#         rgb_u8 = pct_scale_to_u8(rgb)
#         pil = Image.fromarray(np.transpose(rgb_u8, (1, 2, 0)))
#         return pil, crop_box, src.crs.to_string()

# def ask_image_question(client, pil_image, question, system_preamble, model, temperature=0.0):
#     buf = BytesIO()
#     pil_image.save(buf, format="PNG")
#     img_data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

#     resp = client.chat.completions.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": system_preamble},
#             {"role": "user", "content": [
#                 {"type": "text", "text": question},
#                 {"type": "image_url", "image_url": {"url": img_data_url}},
#             ]},
#         ],
#         temperature=float(temperature),
#     )
#     return resp.choices[0].message.content.strip()

# def try_parse_json(text):
#     try:
#         return json.loads(text)
#     except Exception:
#         t = text.strip()
#         if t.startswith("```"):
#             t = t.strip("`")
#             t = t.split("\n", 1)[-1]
#         try:
#             return json.loads(t)
#         except Exception:
#             return None

# def save_quicklook(pil_image, lon, lat, answer, naip_id, out_dir):
#     os.makedirs(out_dir, exist_ok=True)
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.imshow(pil_image)
#     ax.axis("off")
#     ax.set_title(f"NAIP @ {lat:.6f}, {lon:.6f}\n{naip_id}", fontsize=9)
#     fig.suptitle(f"Answer: {answer}", y=0.02, fontsize=9)
#     out_png = os.path.join(out_dir, f"naip_{lat:.6f}_{lon:.6f}.png".replace("-","m").replace(".","p"))
#     plt.tight_layout()
#     plt.savefig(out_png, dpi=150, bbox_inches="tight")
#     plt.close(fig)
#     return out_png


# # =========================
# # STREAMLIT UI
# # =========================
# st.set_page_config(page_title="NAIP WUI Map-Click Q&A", layout="wide")
# st.title("NAIP WUI Map-Click Q&A (click map → 500 m crop → run model)")

# api_key = os.getenv("OPENAI_API_KEY", "")
# if not api_key:
#     st.warning("OPENAI_API_KEY not found in environment. Set it before running.")

# # Session state for clicked point
# if "clicked_lat" not in st.session_state:
#     st.session_state.clicked_lat = 40.655527
# if "clicked_lon" not in st.session_state:
#     st.session_state.clicked_lon = -105.307652

# with st.sidebar:
#     st.header("NAIP Search")
#     start = st.text_input("Start date (YYYY-MM-DD)", value="2018-01-01")
#     end = st.text_input("End date (YYYY-MM-DD)", value="2024-01-01")
#     pad_deg = st.number_input("Search pad (degrees)", value=0.001, format="%.6f")

#     st.header("Crop")
#     side_m = st.selectbox("Crop size (meters)", options=[250, 500, 750, 1000], index=1)
#     half_m = float(side_m) / 2.0

#     st.header("Model")
#     model = st.text_input("OpenAI model", value=DEFAULT_MODEL)
#     temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

#     st.header("Output")
#     save_dir = st.text_input("Save directory", value=DEFAULT_SAVE_DIR)

# system_preamble = st.text_area("System preamble", value=DEFAULT_SYSTEM, height=90)
# question = st.text_area("Question prompt", value=DEFAULT_QUESTION, height=280)

# st.subheader("1) Click a location on the map")
# st.caption("Click anywhere; the app will use that lat/lon. Then click “Run analysis for clicked point”.")

# m = folium.Map(location=[st.session_state.clicked_lat, st.session_state.clicked_lon], zoom_start=14, control_scale=True)
# folium.Marker([st.session_state.clicked_lat, st.session_state.clicked_lon], tooltip="Current selected point").add_to(m)

# # Draw a rough 500 m box in degrees for user intuition (not used for the actual crop)
# # Approx conversion: 1 deg lat ~ 111,320 m; lon scaled by cos(lat)
# deg_lat = (half_m / 111320.0)
# deg_lon = (half_m / (111320.0 * max(0.2, math.cos(math.radians(st.session_state.clicked_lat)))))
# bounds = [
#     [st.session_state.clicked_lat - deg_lat, st.session_state.clicked_lon - deg_lon],
#     [st.session_state.clicked_lat + deg_lat, st.session_state.clicked_lon + deg_lon],
# ]
# folium.Rectangle(bounds=bounds, color="yellow", weight=2, fill=False).add_to(m)

# map_out = st_folium(m, height=520, width=None)

# # Update clicked point if user clicked
# if map_out and map_out.get("last_clicked"):
#     st.session_state.clicked_lat = float(map_out["last_clicked"]["lat"])
#     st.session_state.clicked_lon = float(map_out["last_clicked"]["lng"])

# st.write(f"Selected point: **lat={st.session_state.clicked_lat:.6f}, lon={st.session_state.clicked_lon:.6f}**")
# run = st.button("2) Run analysis for clicked point", type="primary")

# if run:
#     if not api_key:
#         st.error("Missing OPENAI_API_KEY in environment.")
#         st.stop()

#     lon = st.session_state.clicked_lon
#     lat = st.session_state.clicked_lat

#     catalog = get_catalog()

#     st.info("Searching NAIP item...")
#     try:
#         item, aoi = find_best_naip_item(catalog, lon, lat, start=start, end=end, pad_deg=float(pad_deg))
#         if item is None:
#             st.error("No NAIP scene found for that location/date window.")
#             st.stop()

#         href = item_to_href(item)
#         if href is None:
#             st.error("Could not find NAIP COG asset on the selected item.")
#             st.stop()

#         naip_id = item.id

#     except Exception as e:
#         st.exception(e)
#         st.stop()

#     st.info(f"Cropping NAIP to {int(side_m)} m × {int(side_m)} m...")
#     try:
#         pil, crop_box_srccrs, src_crs_str = crop_naip_at_point(href, lon, lat, half_m=half_m)
#     except Exception as e:
#         st.exception(e)
#         st.stop()

#     c1, c2 = st.columns([1, 1])

#     with c1:
#         st.subheader("NAIP crop")
#         #st.image(pil, caption=f"{naip_id} | crop={int(side_m)}m", use_container_width=True)
#         st.image(np.array(pil), caption=f"{naip_id} | crop={int(side_m)}m", width=650)
#         st.caption(f"COG href: {href}")

#     st.info("Calling OpenAI model...")
#     try:
#         client = OpenAI(api_key=api_key)
#         answer_text = ask_image_question(
#             client=client,
#             pil_image=pil,
#             question=question,
#             system_preamble=system_preamble,
#             model=model,
#             temperature=temperature,
#         )
#     except Exception as e:
#         st.exception(e)
#         st.stop()

#     parsed = try_parse_json(answer_text)

#     with c2:
#         st.subheader("Model answer")
#         if parsed is not None:
#             st.json(parsed)
#         else:
#             st.text_area("Raw answer (not valid JSON)", value=answer_text, height=320)

#         try:
#             out_png = save_quicklook(pil, lon, lat, answer_text, naip_id, out_dir=save_dir)
#             st.success(f"Saved preview: {out_png}")
#         except Exception as e:
#             st.warning(f"Could not save preview: {e}")

#     st.subheader("Run metadata")
#     st.code(
#         json.dumps(
#             {
#                 "lat": lat,
#                 "lon": lon,
#                 "crop_side_m": side_m,
#                 "start": start,
#                 "end": end,
#                 "pad_deg": float(pad_deg),
#                 "naip_id": naip_id,
#                 "naip_href": href,
#                 "model": model,
#                 "temperature": float(temperature),
#             },
#             indent=2,
#         ),
#         language="json",
#     )
















# streamlit_app_naip_wui_mapclick.py
# Run:
#   pip install streamlit streamlit-folium folium geopandas rasterio pystac-client planetary-computer shapely pillow numpy openai matplotlib
#   streamlit run streamlit_app_naip_wui_mapclick.py
#
# Streamlit Cloud:
#   - Put OPENAI_API_KEY in Secrets (Manage app → Secrets):
#       OPENAI_API_KEY = "sk-..."
#   - Add runtime.txt: python-3.11
#   - Add requirements.txt with the dependencies above

import os
import json
import math
import base64
from io import BytesIO

import numpy as np
import streamlit as st
from PIL import Image

import folium
from streamlit_folium import st_folium

import rasterio
from rasterio.mask import mask

from shapely.geometry import Point, box, mapping, shape
import geopandas as gpd

import pystac_client
import planetary_computer

from openai import OpenAI
import matplotlib.pyplot as plt


# =========================
# DEFAULTS
# =========================
DEFAULT_MODEL = "gpt-4o"
DEFAULT_SAVE_DIR = r"C:\Users\magst\Desktop\openai\SNAGHAZARD"

DEFAULT_SYSTEM = "You are a land cover photo-analyst. Use only what is visible."

DEFAULT_QUESTION = r"""
Analyze this NAIP RGB aerial image (~0.6–1 m resolution). Use only visible information in the image. Do not assume information not directly observable.

Context:
This image represents a fixed-area crop (~500 m × 500 m). The task is to characterize Wildland–Urban Interface (WUI) exposure and structural defensibility indicators based on visible housing patterns, vegetation proximity, and access.

Tasks:

1. Housing Presence & Density
- Identify all visible residential structures (single-family homes, cabins, outbuildings associated with residences).
- Estimate the number of residential structures visible.
- Classify housing density within the image as one of:
  • Very Low (isolated structures, >40 acres per home equivalent)
  • Low (scattered homes, rural residential)
  • Medium (exurban/suburban edge)
  • High (dense suburban/urban)
- Briefly justify using spacing and clustering visible in the image.

2. Vegetation Proximity & Defensible Space
- Assess vegetation immediately surrounding structures.
- Note whether trees and shrubs are:
  • In direct contact with structures
  • Within ~0–10 m
  • Within ~10–30 m
  • Mostly cleared beyond ~30 m
- Based on visible cues only, classify overall defensible space as:
  • Poor
  • Limited
  • Moderate
  • Good
- Cite concrete visual indicators (e.g., canopy overhang, ladder fuels, cleared yards, mowed areas).

3. WUI Classification
- Based on housing density and surrounding wildland vegetation, classify the scene as:
  • Not WUI
  • Intermix WUI
  • Interface WUI
- Briefly explain the classification using observable patterns.

4. Road Network & Access
- Identify visible roads (paved vs unpaved if distinguishable).
- Note apparent access characteristics:
  • Multiple access routes vs single ingress/egress
  • Road width (narrow vs standard two-lane)
  • Connectivity (grid vs dead-end/driveways)
- Comment on potential access constraints for fire response based only on visibility.

5. Overall WUI Risk Indicator
- Rate overall wildfire exposure risk to structures as:
  • Low
  • Moderate
  • High
  • Very High
- Base this rating strictly on housing density, vegetation proximity, and access—do not incorporate weather, slope, or fire history unless directly visible.

Uncertainty:
- Provide an uncertainty score from 0–1 reflecting confidence in your assessment given image resolution, shadows, and occlusions.

Output strictly as JSON:
{
  "estimated_structure_count": <integer>,
  "housing_density_class": "<Very Low|Low|Medium|High>",
  "defensible_space_class": "<Poor|Limited|Moderate|Good>",
  "wui_class": "<Not WUI|Intermix WUI|Interface WUI>",
  "road_access_notes": "<concise description>",
  "overall_wui_risk": "<Low|Moderate|High|Very High>",
  "evidence": "<≤75 words citing visible features>",
  "uncertainty": <float 0–1>
}
""".strip()


# =========================
# CONFIG (behind-the-scenes)
# =========================
# "Most recent NAIP" is found by searching a generous window and sorting by item datetime desc.
# This avoids requiring the user to set start/end dates.
NAIP_SEARCH_START = "2010-01-01"
NAIP_SEARCH_END = "2035-01-01"

# Search pad (degrees) – hidden from UI; used to build an intersects polygon around the click.
# 0.001 deg ~ 111 m latitude; sufficient to find NAIP tiles near the point.
HIDDEN_PAD_DEG = 0.0025  # slightly larger so clicks near edge still resolve

# Map behavior tuning
DEFAULT_ZOOM = 14
CLICK_ZOOM = 16  # zoom-in after click (optional)


# =========================
# CACHED RESOURCES
# =========================
@st.cache_resource
def get_catalog():
    return pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )


# =========================
# HELPERS
# =========================
def pct_scale_to_u8(rgb_arr):
    """Percentile scale each band to uint8 (0–255) for visualization."""
    if rgb_arr.dtype == np.uint8:
        return rgb_arr
    out = []
    for b in range(rgb_arr.shape[0]):
        band = rgb_arr[b].astype(np.float32)
        lo, hi = np.nanpercentile(band, [0.0, 99.5])
        if not np.isfinite(lo): lo = 0.0
        if not np.isfinite(hi) or hi <= lo: hi = lo + 1.0
        band = (np.clip((band - lo) / (hi - lo), 0, 1) * 255.0).astype(np.uint8)
        out.append(band)
    return np.stack(out, axis=0)

def _aoi_poly(lon, lat, pad_deg):
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon - pad_deg, lat - pad_deg],
            [lon + pad_deg, lat - pad_deg],
            [lon + pad_deg, lat + pad_deg],
            [lon - pad_deg, lat + pad_deg],
            [lon - pad_deg, lat - pad_deg],
        ]]
    }

def _item_datetime_str(it):
    # STAC item datetime handling: prefer item.datetime, fallback to properties["datetime"]
    dt = getattr(it, "datetime", None)
    if dt is not None:
        try:
            return dt.isoformat()
        except Exception:
            pass
    props = getattr(it, "properties", {}) or {}
    return props.get("datetime") or props.get("start_datetime") or ""

def find_most_recent_naip_item(catalog, lon, lat, pad_deg=HIDDEN_PAD_DEG):
    """
    Search NAIP around lon/lat and return the most recent item (by datetime).
    """
    aoi = _aoi_poly(lon, lat, pad_deg=pad_deg)

    items = catalog.search(
        collections=["naip"],
        intersects=aoi,
        datetime=f"{NAIP_SEARCH_START}/{NAIP_SEARCH_END}",
        max_items=200,
    ).item_collection()

    if not items or len(items) == 0:
        return None, aoi

    aoi_shape = shape(aoi)

    # Filter to those that actually intersect AOI (should already, but belt+suspenders)
    keep = []
    for it in items:
        try:
            if shape(it.geometry).intersects(aoi_shape):
                keep.append(it)
        except Exception:
            continue

    if len(keep) == 0:
        return None, aoi

    # Sort by datetime (desc), tie-breaker by intersection area (desc)
    def sort_key(it):
        dt = _item_datetime_str(it)
        try:
            area = shape(it.geometry).intersection(aoi_shape).area
        except Exception:
            area = 0.0
        return (dt, area)

    keep_sorted = sorted(keep, key=sort_key, reverse=True)
    return keep_sorted[0], aoi

def item_to_href(item):
    href = None
    if "image" in item.assets:
        href = item.assets["image"].href
    else:
        for a in item.assets.values():
            if a.href.lower().endswith((".tif", ".tiff")):
                href = a.href
                break
    return href

def crop_naip_at_point(href, lon, lat, half_m):
    with rasterio.open(href) as src:
        pt = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs=4326).to_crs(src.crs)
        cx, cy = pt.geometry.iloc[0].x, pt.geometry.iloc[0].y
        crop_box = box(cx - half_m, cy - half_m, cx + half_m, cy + half_m)
        crop_geom = [mapping(crop_box)]
        data, _ = mask(src, crop_geom, crop=True)

        if data.shape[0] >= 3:
            rgb = data[:3, :, :]
        else:
            rgb = np.repeat(data[0:1, :, :], 3, axis=0)

        rgb_u8 = pct_scale_to_u8(rgb)
        pil = Image.fromarray(np.transpose(rgb_u8, (1, 2, 0)))
        return pil, src.crs.to_string()

def ask_image_question(client, pil_image, question, system_preamble, model, temperature=0.0):
    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    img_data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_preamble},
            {"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": img_data_url}},
            ]},
        ],
        temperature=float(temperature),
    )
    return resp.choices[0].message.content.strip()

def try_parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        t = text.strip()
        if t.startswith("```"):
            t = t.strip("`")
            t = t.split("\n", 1)[-1]
        try:
            return json.loads(t)
        except Exception:
            return None

def save_quicklook(pil_image, lon, lat, answer, naip_id, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(pil_image)
    ax.axis("off")
    ax.set_title(f"NAIP @ {lat:.6f}, {lon:.6f}\n{naip_id}", fontsize=9)
    fig.suptitle(f"Answer: {answer}", y=0.02, fontsize=9)
    out_png = os.path.join(out_dir, f"naip_{lat:.6f}_{lon:.6f}.png".replace("-","m").replace(".","p"))
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_png


# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="NAIP WUI Map-Click Q&A", layout="wide")
st.title("NAIP WUI Map-Click Q&A (click map → crop → run model)")

api_key = os.getenv("OPENAI_API_KEY", "") or (st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else "")
if not api_key:
    st.warning("OPENAI_API_KEY not found. Add it in Streamlit → Manage app → Secrets.")
    st.stop()

# Session state for clicked point + map viewport persistence
if "clicked_lat" not in st.session_state:
    st.session_state.clicked_lat = 40.655527
if "clicked_lon" not in st.session_state:
    st.session_state.clicked_lon = -105.307652
if "map_center" not in st.session_state:
    st.session_state.map_center = [st.session_state.clicked_lat, st.session_state.clicked_lon]
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = DEFAULT_ZOOM

with st.sidebar:
    st.header("Crop")
    side_m = st.selectbox("Crop size (meters)", options=[250, 500, 750, 1000], index=1)
    half_m = float(side_m) / 2.0

    st.header("Model")
    model = st.text_input("OpenAI model", value=DEFAULT_MODEL)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

    st.header("Output")
    save_dir = st.text_input("Save directory", value=DEFAULT_SAVE_DIR)

system_preamble = st.text_area("System preamble", value=DEFAULT_SYSTEM, height=90)
question = st.text_area("Question prompt", value=DEFAULT_QUESTION, height=280)

st.subheader("1) Click a location on the map")
st.caption(
    "Tip: zoom/pan first, then click. The map center/zoom should persist, and the clicked point updates without resetting."
)

# Build map using persisted viewport
m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom, control_scale=True)

# Better click targeting: show a crosshair marker and a small circle around the click
folium.CircleMarker(
    location=[st.session_state.clicked_lat, st.session_state.clicked_lon],
    radius=8,
    weight=2,
    color="yellow",
    fill=True,
    fill_opacity=0.25,
    tooltip="Selected point",
).add_to(m)

# Draw crop box in degrees for intuition (still not used for the actual crop)
deg_lat = (half_m / 111320.0)
deg_lon = (half_m / (111320.0 * max(0.2, math.cos(math.radians(st.session_state.clicked_lat)))))
bounds = [
    [st.session_state.clicked_lat - deg_lat, st.session_state.clicked_lon - deg_lon],
    [st.session_state.clicked_lat + deg_lat, st.session_state.clicked_lon + deg_lon],
]
folium.Rectangle(bounds=bounds, color="yellow", weight=2, fill=False).add_to(m)

# Use key so the widget state is stable across reruns
map_out = st_folium(m, height=560, width=None, key="wui_map")

# Persist viewport to avoid "reset" feeling after interactions
if map_out:
    if map_out.get("center"):
        st.session_state.map_center = [float(map_out["center"]["lat"]), float(map_out["center"]["lng"])]
    if map_out.get("zoom") is not None:
        st.session_state.map_zoom = int(map_out["zoom"])

    # Update clicked point if user clicked
    if map_out.get("last_clicked"):
        st.session_state.clicked_lat = float(map_out["last_clicked"]["lat"])
        st.session_state.clicked_lon = float(map_out["last_clicked"]["lng"])
        # Optional: zoom in a bit after a click (comment out if you dislike)
        st.session_state.map_center = [st.session_state.clicked_lat, st.session_state.clicked_lon]
        st.session_state.map_zoom = max(st.session_state.map_zoom, CLICK_ZOOM)

st.write(f"Selected point: **lat={st.session_state.clicked_lat:.6f}, lon={st.session_state.clicked_lon:.6f}**")

# Run button outside map so the map isn't constantly re-rendered by typing
run = st.button("2) Run analysis for clicked point", type="primary")

if run:
    lon = st.session_state.clicked_lon
    lat = st.session_state.clicked_lat

    catalog = get_catalog()

    st.info("Finding most recent NAIP scene for that point...")
    try:
        item, _aoi = find_most_recent_naip_item(catalog, lon, lat, pad_deg=HIDDEN_PAD_DEG)
        if item is None:
            st.error("No NAIP scene found for that location.")
            st.stop()

        href = item_to_href(item)
        if href is None:
            st.error("Could not find NAIP COG asset on the selected item.")
            st.stop()

        naip_id = item.id
        naip_dt = _item_datetime_str(item)

    except Exception as e:
        st.exception(e)
        st.stop()

    st.info(f"Cropping NAIP to {int(side_m)} m × {int(side_m)} m...")
    try:
        pil, src_crs_str = crop_naip_at_point(href, lon, lat, half_m=half_m)
        if pil is None:
            st.error("Crop returned no image.")
            st.stop()
    except Exception as e:
        st.exception(e)
        st.stop()

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("NAIP crop")
        st.image(np.array(pil), caption=f"{naip_id} | {naip_dt} | crop={int(side_m)}m", width=650)
        st.caption(f"COG href: {href}")

    st.info("Calling OpenAI model...")
    try:
        client = OpenAI(api_key=api_key)
        answer_text = ask_image_question(
            client=client,
            pil_image=pil,
            question=question,
            system_preamble=system_preamble,
            model=model,
            temperature=temperature,
        )
    except Exception as e:
        st.exception(e)
        st.stop()

    parsed = try_parse_json(answer_text)

    with c2:
        st.subheader("Model answer")
        if parsed is not None:
            st.json(parsed)
        else:
            st.text_area("Raw answer (not valid JSON)", value=answer_text, height=320)

        try:
            out_png = save_quicklook(pil, lon, lat, answer_text, naip_id, out_dir=save_dir)
            st.success(f"Saved preview: {out_png}")
        except Exception as e:
            st.warning(f"Could not save preview: {e}")

    st.subheader("Run metadata")
    st.code(
        json.dumps(
            {
                "lat": lat,
                "lon": lon,
                "crop_side_m": int(side_m),
                "naip_id": naip_id,
                "naip_datetime": naip_dt,
                "naip_href": href,
                "model": model,
                "temperature": float(temperature),
                "hidden_search_pad_deg": HIDDEN_PAD_DEG,
            },
            indent=2,
        ),
        language="json",
    )

















