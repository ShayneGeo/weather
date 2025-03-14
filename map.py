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
import matplotlib.pyplot as plt
import tempfile
import os

from rasterio.warp import transform_bounds, calculate_default_transform, reproject, Resampling
from streamlit_folium import st_folium

# ---------------------------------------------------------------------------
# 1) FORCE REPROJECT THE TIFF TO EPSG:4326 (Lat/Lon) EVEN IF IT CLAIMS TO BE WGS84
#    This helps fix bounding-box issues when the file is actually in a projected system.
# ---------------------------------------------------------------------------
def reproject_to_wgs84(input_path, output_path="reprojected.tif"):
    with rasterio.open(input_path) as src:
        # If it's really EPSG:4326, this won't harm anything
        dst_crs = "EPSG:4326"

        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update({
            "crs": dst_crs,
            "transform": transform,
            "width": width,
            "height": height
        })

        with rasterio.open(output_path, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear
                )
    return output_path

# ---------------------------------------------------------------------------
# 2) LOAD SINGLE-BAND, QUANTILE IT, RETURN ARRAY AND BOUNDS
# ---------------------------------------------------------------------------
def load_tif_quantile(tif_path, num_quantiles=5):
    """
    Load a single-band TIFF now guaranteed to be in EPSG:4326,
    apply quantile binning, and return (quantized_image, bounds).
    """
    with rasterio.open(tif_path) as src:
        # Confirm final CRS is EPSG:4326
        st.write("Reprojected/Checked CRS:", src.crs)
        image = src.read(1)  # Single band
        # The bounds below are in lat/lon if src.crs == EPSG:4326
        bounds = src.bounds

    # Quantile binning (ignore <= 0 if that's NoData)
    valid_pixels = image[image > 0]
    if len(valid_pixels) == 0:
        # Edge case: if entire raster is zero or negative
        # Just return as-is
        quantized_image = image.astype(np.uint8)
    else:
        quantiles = np.percentile(valid_pixels, np.linspace(0, 100, num_quantiles + 1))
        quantized_image = np.digitize(image, bins=quantiles, right=True) - 1
        # Normalize to 0-255
        quantized_image = (255 * (quantized_image / (num_quantiles - 1))).astype(np.uint8)

    return quantized_image, bounds

# ---------------------------------------------------------------------------
# MAIN STREAMLIT APP
# ---------------------------------------------------------------------------
st.title("TIFF Overlay (Force-Reprojected to EPSG:4326)")

# Input TIFF (replace with your file if needed)
original_tif_path = "pcltile_70000-40000.tif"

# 1) Force reproject the data to EPSG:4326 in case it's not truly lat/lon
reprojected_tif = reproject_to_wgs84(original_tif_path)

# 2) Load and quantize
image, bounds = load_tif_quantile(reprojected_tif, num_quantiles=5)

# 3) Compute center
lat_center = (bounds.top + bounds.bottom) / 2
lon_center = (bounds.left + bounds.right) / 2

# 4) Create Folium map (using default Web Mercator tiles)
m = folium.Map(location=[lat_center, lon_center], zoom_start=12)

# Toggle overlay
show_tiff = st.checkbox("Show TIFF overlay", value=True)
if show_tiff:
    # Save our quantized array to a temp PNG with Viridis
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
        plt.imsave(temp_img.name, image, cmap="viridis")
        temp_img_path = temp_img.name

    # 5) Add raster overlay to Folium
    #    The bounding box is in lat/lon because we reprojected above.
    folium.raster_layers.ImageOverlay(
        name="TIFF Overlay",
        image=temp_img_path,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=1.0
    ).add_to(m)

    folium.LayerControl().add_to(m)

# 6) Show it in Streamlit
st_folium(m, width=700, height=500)

# 7) Clean up temporary image
if os.path.exists(temp_img_path):
    os.remove(temp_img_path)

# 8) Clean up reprojected TIFF if desired
if os.path.exists(reprojected_tif):
    os.remove(reprojected_tif)


