import streamlit as st
import folium
import rasterio
import numpy as np
from rasterio.plot import reshape_as_image
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import tempfile
import os

tif_path = "pcltile_70000-40000.tif"

def load_tif(tif_path):
    with rasterio.open(tif_path) as src:
        image = src.read(1)  # Read the first band (grayscale)
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

    # Normalize image to 0-255 range
    image = (255 * (image - np.min(image)) / (np.max(image) - np.min(image))).astype(np.uint8)

    # Save the image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
        plt.imsave(temp_img.name, image, cmap='gray')  # Save as grayscale PNG
        temp_img_path = temp_img.name

    # Add the overlay to folium
    folium.raster_layers.ImageOverlay(
        name="TIFF Overlay",
        image=temp_img_path,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=0.6
    ).add_to(m)
    
    folium.LayerControl().add_to(m)

st_folium(m, width=700, height=500)

# Clean up temporary file
if os.path.exists(temp_img_path):
    os.remove(temp_img_path)
