# ===========================
# Import necessary libraries
# ===========================
    # For reading and manipulating shapefiles (geospatial data)
import geopandas as gpd
    # For reading/writing CSV files with coordinates
import csv
    # For making HTTP requests (download images from Google Maps API)
import requests
    # For handling folders and file paths
import os

# ===========================
# 1. FILE PATHS
# ===========================
    # Path to the shapefile (zipped) containing island boundaries
shapefile_path = r"E:\INTERNSHIP SOFIYA\Saint Vincent and The Grenadines\vct_admbnd_gadm_20240717_ab_shp.zip"

    # CSV file where extracted coordinates will be saved
csv_file_path = "StVincentandTheGrenadinesTrial.csv"

    # Directory where downloaded satellite images will be saved
image_directory = r"E:\INTERNSHIP SOFIYA\Saint Vincent and The Grenadines\Satellite Images From Coordinates_Trial"

# ===========================
# 2. READ SHAPEFILE
# ===========================
    # Load the shapefile using GeoPandas
gdf = gpd.read_file(shapefile_path)

    # Ensure coordinates are in WGS84 (EPSG:4326), required by Google Maps
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

# ===========================
# 3. EXTRACT COORDINATES
# ===========================
contour_coordinates = []    # List to store all polygon coordinates

for geom in gdf.geometry:
    if geom is None:        # Skip empty geometries
        continue
    if geom.geom_type == "Polygon":         # Single polygon
        contour_coordinates.append(list(geom.exterior.coords))
    elif geom.geom_type == "MultiPolygon":  # Multiple polygons (e.g., islands with small surrounding islets)
        for polygon in geom.geoms:
            contour_coordinates.append(list(polygon.exterior.coords))

# ===========================
# 4. SAVE COORDINATES TO CSV
# ===========================
    # Open CSV file for writing
with open(csv_file_path, mode='w', newline='') as csv_out:
    writer = csv.writer(csv_out)
    # Write header
    writer.writerow(["Latitude", "Longitude"])
    # Write coordinates to CSV (lat/lon order for Google Maps)
    for coords in contour_coordinates:
        for lon, lat in coords: # GeoPandas gives (lon, lat); swap for CSV
            writer.writerow([lat, lon])

# ===========================
# 5. GOOGLE MAPS API CONFIG
# ===========================
    # Replace with your valid API key
API_KEY = "put_your_actual_API_key_here"
    # Zoom level: higher = more detail
zoom = 19
    # Image size (max free size 640x640)
size = "640x640"
    # Satellite imagery
map_type = "satellite"

    # Create the output folder if it doesn't exist
os.makedirs(image_directory, exist_ok=True)

# ===========================
# 6. DOWNLOAD SATELLITE IMAGES
# ===========================
    # Open CSV with coordinates
with open(csv_file_path, mode='r') as csv_in:
    reader = csv.DictReader(csv_in)

    for index, row in enumerate(reader, start=1):
        latitude = row["Latitude"]
        longitude = row["Longitude"]

        # Only download every 5th point to reduce API calls
        if index % 5 == 0:
            # Construct Google Maps Static API URL
            url = (
                f"https://maps.googleapis.com/maps/api/staticmap?"
                f"center={latitude},{longitude}&"
                f"zoom={zoom}&"
                f"size={size}&"
                f"maptype={map_type}&"
                f"key={API_KEY}"
            )

            # Send HTTP request to download image
            response = requests.get(url)

            if response.status_code == 200:
                # Save image to output directory
                image_filename = os.path.join(image_directory, f"St_Vincent_sat_image_{index}.png")
                with open(image_filename, "wb") as img_out:
                    img_out.write(response.content)
                print(f"Image saved: {image_filename}")
            else:
                # Print error if download failed
                print(f"Error {response.status_code} downloading image at {latitude}, {longitude}")
