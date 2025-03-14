import streamlit as st
import folium
import rasterio
from rasterio.plot import reshape_as_image
from streamlit_folium import st_folium

# Note: For small TIFF files, you can include them in your Git repository (e.g., in a "data" folder).
# For larger files, consider using Git LFS or hosting them externally.
tif_path = "data/your_file.tif"

def load_tif(tif_path):
    with rasterio.open(tif_path) as src:
        image = reshape_as_image(src.read())
        bounds = src.bounds
    return image, bounds

st.title("TIFF Overlay Map")

# Load TIFF bounds for centering the map
with rasterio.open(tif_path) as src:
    bounds = src.bounds
lat_center = (bounds.top + bounds.bottom) / 2
lon_center = (bounds.left + bounds.right) / 2

# Create a folium map centered on the TIFF's bounds
m = folium.Map(location=[lat_center, lon_center], zoom_start=12)

# Toggle to show or hide the TIFF overlay
show_tiff = st.checkbox("Show TIFF overlay", value=True)

if show_tiff:
    image, _ = load_tif(tif_path)
    folium.raster_layers.ImageOverlay(
        image=image,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=0.6,
        name="TIFF Overlay"
    ).add_to(m)
    folium.LayerControl().add_to(m)

st_folium(m, width=700, height=500)
