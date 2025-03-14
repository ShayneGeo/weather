# # # import streamlit as st
# # # import folium
# # # import rasterio
# # # import numpy as np
# # # from rasterio.plot import reshape_as_image
# # # from streamlit_folium import st_folium
# # # import matplotlib.pyplot as plt
# # # import tempfile
# # # import os

# # # tif_path = "pcltile_70000-40000.tif"

# # # def load_tif(tif_path):
# # #     with rasterio.open(tif_path) as src:
# # #         image = src.read(1)  # Read the first band (grayscale)
# # #         bounds = src.bounds
# # #     return image, bounds

# # # st.title("TIFF Overlay Map")

# # # # Load TIFF bounds for centering the map
# # # with rasterio.open(tif_path) as src:
# # #     bounds = src.bounds
# # # lat_center = (bounds.top + bounds.bottom) / 2
# # # lon_center = (bounds.left + bounds.right) / 2

# # # # Create a folium map centered on the TIFF's bounds
# # # m = folium.Map(location=[lat_center, lon_center], zoom_start=12)

# # # # Toggle to show or hide the TIFF overlay
# # # show_tiff = st.checkbox("Show TIFF overlay", value=True)

# # # if show_tiff:
# # #     image, _ = load_tif(tif_path)

# # #     # Normalize image to 0-255 range
# # #     image = (255 * (image - np.min(image)) / (np.max(image) - np.min(image))).astype(np.uint8)

# # #     # Save the image temporarily
# # #     with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
# # #         plt.imsave(temp_img.name, image, cmap='viridis')  # Save as grayscale PNG
# # #         temp_img_path = temp_img.name

# # #     # Add the overlay to folium
# # #     folium.raster_layers.ImageOverlay(
# # #         name="TIFF Overlay",
# # #         image=temp_img_path,
# # #         bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
# # #         opacity=1.0
# # #     ).add_to(m)
    
# # #     folium.LayerControl().add_to(m)

# # # st_folium(m, width=700, height=500)

# # # # Clean up temporary file
# # # if os.path.exists(temp_img_path):
# # #     os.remove(temp_img_path)



# # import streamlit as st
# # import folium
# # import rasterio
# # import numpy as np
# # from rasterio.plot import reshape_as_image
# # from streamlit_folium import st_folium
# # import matplotlib.pyplot as plt
# # import tempfile
# # import os

# # tif_path = "pcltile_70000-40000.tif"

# # def load_tif(tif_path, num_quantiles=5):
# #     with rasterio.open(tif_path) as src:
# #         image = src.read(1)  # Read the first band (grayscale)
# #         bounds = src.bounds

# #     # Flatten image and compute quantile thresholds
# #     valid_pixels = image[image > 0]  # Ignore zero or NoData values
# #     quantiles = np.percentile(valid_pixels, np.linspace(0, 100, num_quantiles + 1))

# #     # Assign each pixel to a quantile bin
# #     quantized_image = np.digitize(image, bins=quantiles, right=True) - 1  # Convert to bin index

# #     # Normalize the quantized bins to 0-255 range
# #     quantized_image = (255 * (quantized_image / (num_quantiles - 1))).astype(np.uint8)

# #     return quantized_image, bounds

# # st.title("Quantile-Scaled TIFF Overlay (Viridis)")

# # # Load TIFF bounds for centering the map
# # with rasterio.open(tif_path) as src:
# #     bounds = src.bounds
# # lat_center = (bounds.top + bounds.bottom) / 2
# # lon_center = (bounds.left + bounds.right) / 2

# # # Create a folium map centered on the TIFF's bounds
# # m = folium.Map(location=[lat_center, lon_center], zoom_start=12)

# # # Toggle to show or hide the TIFF overlay
# # show_tiff = st.checkbox("Show TIFF overlay", value=True)

# # if show_tiff:
# #     # Apply quantile binning
# #     image, _ = load_tif(tif_path, num_quantiles=5)  # Change num_quantiles as needed

# #     # Save the image temporarily with Viridis colormap
# #     with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
# #         plt.imsave(temp_img.name, image, cmap="viridis")  # Apply Viridis colormap to quantized data
# #         temp_img_path = temp_img.name

# #     # Add the overlay to folium with full opacity
# #     folium.raster_layers.ImageOverlay(
# #         name="TIFF Overlay (Quantile)",
# #         image=temp_img_path,
# #         bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
# #         opacity=1.0  # No transparency
# #     ).add_to(m)
    
# #     folium.LayerControl().add_to(m)

# # st_folium(m, width=700, height=500)

# # # Clean up temporary file
# # if os.path.exists(temp_img_path):
# #     os.remove(temp_img_path)


# import streamlit as st
# import folium
# import rasterio
# import numpy as np
# from rasterio.plot import reshape_as_image
# from rasterio.warp import transform_bounds
# from streamlit_folium import st_folium
# import matplotlib.pyplot as plt
# import tempfile
# import os

# tif_path = "pcltile_70000-40000.tif"

# def get_bounds_in_wgs84(tif_path):
#     """ Reproject raster bounds to EPSG:4326 """
#     with rasterio.open(tif_path) as src:
#         bounds = src.bounds
#         crs = src.crs

#         # Reproject bounds to WGS 84 (Lat/Lon)
#         wgs84_bounds = transform_bounds(crs, "EPSG:4326", 
#                                         bounds.left, bounds.bottom, 
#                                         bounds.right, bounds.top)
#     return wgs84_bounds

# def load_tif(tif_path, num_quantiles=5):
#     """ Load and quantile TIFF data """
#     with rasterio.open(tif_path) as src:
#         image = src.read(1)  # Read first band (grayscale)
#     # Compute quantile bins
#     valid_pixels = image[image > 0]  
#     quantiles = np.percentile(valid_pixels, np.linspace(0, 100, num_quantiles + 1))
#     quantized_image = np.digitize(image, bins=quantiles, right=True) - 1
#     quantized_image = (255 * (quantized_image / (num_quantiles - 1))).astype(np.uint8)
#     return quantized_image

# st.title("Corrected TIFF Overlay (Viridis)")

# # Get corrected bounds
# bounds = get_bounds_in_wgs84(tif_path)
# lat_center = (bounds[1] + bounds[3]) / 2
# lon_center = (bounds[0] + bounds[2]) / 2

# # Create Folium map
# m = folium.Map(location=[lat_center, lon_center], zoom_start=12)

# # Toggle overlay
# show_tiff = st.checkbox("Show TIFF overlay", value=True)

# if show_tiff:
#     image = load_tif(tif_path, num_quantiles=5)

#     # Save as Viridis PNG
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
#         plt.imsave(temp_img.name, image, cmap="viridis")
#         temp_img_path = temp_img.name

#     # Overlay with corrected bounds
#     folium.raster_layers.ImageOverlay(
#         name="TIFF Overlay",
#         image=temp_img_path,
#         bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],  # Corrected WGS84 bounds
#         opacity=1.0
#     ).add_to(m)
    
#     folium.LayerControl().add_to(m)

# st_folium(m, width=700, height=500)

# # Clean up temp file
# if os.path.exists(temp_img_path):
#     os.remove(temp_img_path)

import streamlit as st
import folium
import rasterio
import numpy as np
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import tempfile
import os

tif_path = "pcltile_70000-40000.tif"

def load_tif(tif_path, num_quantiles=5):
    """
    Load a single-band (grayscale) TIFF in EPSG:4326, 
    apply quantile binning, and return the quantized image array and native bounds.
    """
    with rasterio.open(tif_path) as src:
        # Confirm that the CRS is EPSG:4326
        print("Raster CRS:", src.crs)
        image = src.read(1)  # Single band
        bounds = src.bounds  # Already in Lat/Lon if EPSG:4326

    # Compute quantiles (ignore zero if it's NoData)
    valid_pixels = image[image > 0]
    quantiles = np.percentile(valid_pixels, np.linspace(0, 100, num_quantiles + 1))
    # Bin the pixel values according to these quantiles
    quantized_image = np.digitize(image, bins=quantiles, right=True) - 1
    # Scale to 0-255 for display
    quantized_image = (255 * (quantized_image / (num_quantiles - 1))).astype(np.uint8)

    return quantized_image, bounds

st.title("TIFF Overlay (EPSG:4326)")

# Checkbox to show/hide the TIFF overlay
show_tiff = st.checkbox("Show TIFF overlay", value=True)
if show_tiff:
    # Load the TIFF (already in EPSG:4326) and get its bounds
    image, bounds = load_tif(tif_path, num_quantiles=5)

    # Calculate the center of the raster in lat/lon
    lat_center = (bounds.top + bounds.bottom) / 2
    lon_center = (bounds.left + bounds.right) / 2

    # Create a Folium map specifying EPSG:4326 so it won't internally project to Web Mercator
    m = folium.Map(location=[lat_center, lon_center],
                   zoom_start=12,
                   crs="EPSG4326",        # Keep everything in WGS84
                   tiles="OpenStreetMap")  # You can change or remove this if you like

    # Write the quantized array to a temporary PNG using Viridis
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
        plt.imsave(temp_img.name, image, cmap="viridis")
        temp_img_path = temp_img.name

    # Use the original bounds (already in lat-lon) for the overlay
    folium.raster_layers.ImageOverlay(
        name="TIFF Overlay",
        image=temp_img_path,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=1.0
    ).add_to(m)

    folium.LayerControl().add_to(m)

    # Show the map in Streamlit
    st_folium(m, width=700, height=500)

    # Clean up temp file
    os.remove(temp_img_path)


