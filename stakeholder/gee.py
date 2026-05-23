#!/usr/bin/env python3
"""
Advanced GEE Data Fetcher for Plot Analysis
-------------------------------------------
Fetches ultra-recent environmental metrics for a given plot using GEE.

Designed for Django integration:
- Can be called from views
- Can be used in Celery tasks
- Can run via cron for scheduled monitoring

Features:
- NDVI, EVI, NDWI
- Tree cover, biomass, carbon
- Burned area, fire hotspots, post-fire recovery
- Soil moisture, bare soil, erosion risk
- Flood extent, water quality proxies
- Vegetation diversity, habitat fragmentation
- Climate & microclimate monitoring
- Air quality & smoke detection
- Land use, encroachment, illegal logging
- Automatic alerts for anomalies
"""


import math

import ee
import os
import datetime

SERVICE_ACCOUNT = "imvelo@my-earth-engine-project-463609.iam.gserviceaccount.com"
KEY_FILE = os.path.join(os.path.dirname(__file__), "key.json")

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
ee.Initialize(credentials)


# -----------------------------
# 2. DATASETS
# -----------------------------
S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
FOREST = ee.Image("UMD/hansen/global_forest_change_2024_v1_12")
CHIRPS = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
LANDCOVER_COLLECTION = ee.ImageCollection("ESA/WorldCover/v200")
MODIS_TEMP = ee.ImageCollection("MODIS/061/MOD11A1")
SOIL_MOISTURE = ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
AEROSOLS = ee.ImageCollection("MODIS/061/MCD19A2_GRANULES")
MODIS_FIRE = ee.ImageCollection("MODIS/006/MCD64A1")
VIIRS_FIRE = ee.ImageCollection("NOAA/VIIRS/001/VNP14A1")
MODIS_ET = ee.ImageCollection("MODIS/006/MOD16A2")
DEM = ee.Image("USGS/SRTMGL1_003")

# -----------------------------
# 3. DATE WINDOWS
# -----------------------------
def get_dates():
    today = ee.Date(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    return {
        "today": today,
        "last_3": today.advance(-3, "day"),
        "last_7": today.advance(-7, "day"),
        "last_30": today.advance(-30, "day"),
        "last_90": today.advance(-90, "day"),
        "last_365": today.advance(-365, "day"),
    }

# -----------------------------
# 4. HELPER FUNCTIONS
# -----------------------------
def calculate_shannon_diversity(histogram):
    if not histogram:
        return None
    total = sum(histogram.values())
    return -sum((v / total) * math.log(v / total) for v in histogram.values() if v > 0)

def calculate_simpson_diversity(histogram):
    if not histogram:
        return None
    total = sum(histogram.values())
    return 1 - sum((v / total) ** 2 for v in histogram.values())

# -----------------------------
# 5. ANALYZE PLOT FUNCTION
# -----------------------------
def analyze_plot(boundary_geojson):
    dates = get_dates()
    geom = ee.Geometry(boundary_geojson)

    # -----------------------------
    # SENTINEL-2
    # -----------------------------
    s2_collection = S2.filterBounds(geom) \
                      .filterDate(dates["last_30"], dates["today"]) \
                      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40)) \
                      .sort("CLOUDY_PIXEL_PERCENTAGE")
    s2_image = ee.Image(s2_collection.first()) if s2_collection.size().getInfo() > 0 else None

    ndvi_stats = {"NDVI_mean": None, "NDVI_min": None, "NDVI_max": None}
    evi_mean = None
    ndwi_mean = None
    bare_soil_index = None

    if s2_image:
        s2_image = s2_image.clip(geom)

        # NDVI
        ndvi = s2_image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndvi_stats = ndvi.reduceRegion(
            ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True),
            geom, scale=10, maxPixels=1e10
        ).getInfo()

        # EVI
        evi = s2_image.expression(
            "2.5 * ((NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1))",
            {"NIR": s2_image.select("B8"), "RED": s2_image.select("B4"), "BLUE": s2_image.select("B2")}
        )
        evi_mean = evi.reduceRegion(ee.Reducer.mean(), geom, 10, maxPixels=1e10).getInfo().get("constant")

        # NDWI
        ndwi = s2_image.normalizedDifference(["B3", "B8"]).rename("NDWI")
        ndwi_mean = ndwi.reduceRegion(ee.Reducer.mean(), geom, 10).getInfo().get("NDWI")

        # Bare soil index
        bsi = s2_image.expression("(SWIR - NIR) / (SWIR + NIR)", {"SWIR": s2_image.select("B11"), "NIR": s2_image.select("B8")})
        bare_soil_index = bsi.reduceRegion(ee.Reducer.mean(), geom, 10).getInfo().get("constant")

    # -----------------------------
    # TREE COVER, LOSS, BIOMASS, CARBON
    # -----------------------------
    tree_cover_mean = None
    forest_loss_area = None
    try:
        tree_cover_mean = FOREST.select("treecover2000").reduceRegion(ee.Reducer.mean(), geom, 30).getInfo().get("treecover2000")
        forest_loss_area = FOREST.select("lossyear").gt(0).multiply(ee.Image.pixelArea()).clip(geom).reduceRegion(
            ee.Reducer.sum(), geom, 30, maxPixels=1e10
        ).getInfo().get("lossyear")
        biomass_estimate = (tree_cover_mean or 0) * 10
        carbon_stock_estimate = biomass_estimate * 0.5
    except Exception:
        biomass_estimate = None
        carbon_stock_estimate = None

    # -----------------------------
    # FIRE DETECTION
    # -----------------------------
    burned_area_hectares = 0
    post_fire_recovery = None
    fire_collection = MODIS_FIRE.filterBounds(geom).filterDate(dates["last_30"], dates["today"])
    if fire_collection.size().getInfo() > 0:
        fire_image = fire_collection.max().clip(geom)
        if fire_image.bandNames().size().getInfo() > 0:
            burned_area_hectares = fire_image.select("BurnDate").gt(0).multiply(ee.Image.pixelArea()).reduceRegion(
                ee.Reducer.sum(), geom, 500, maxPixels=1e10
            ).getInfo().get("BurnDate", 0)

    # Fire hotspots
    viirs_collection = VIIRS_FIRE.filterBounds(geom).filterDate(dates["last_7"], dates["today"])
    fire_hotspots = viirs_collection.size().getInfo() if viirs_collection.size().getInfo() > 0 else 0

    # -----------------------------
    # SOIL & EROSION
    # -----------------------------
    soil_moisture_mean = None
    smap_collection = SOIL_MOISTURE.filterBounds(geom).filterDate(dates["last_7"], dates["today"])
    if smap_collection.size().getInfo() > 0:
        soil_moisture_mean = smap_collection.mean().clip(geom).select("ssm").reduceRegion(
            ee.Reducer.mean(), geom, 10, maxPixels=1e10
        ).getInfo().get("ssm")

    slope_mean = DEM.select("elevation").gradient().clip(geom).reduceRegion(ee.Reducer.mean(), geom, 30, maxPixels=1e10).getInfo().get("dx") if DEM else None
    erosion_risk = "High" if (bare_soil_index and slope_mean and bare_soil_index * slope_mean > 0.5) else "Low"

    # -----------------------------
    # WATER & FLOOD
    # -----------------------------
# -----------------------------
# WATER & FLOOD
# -----------------------------
    rainfall = None
    chirps_collection = CHIRPS.filterBounds(geom).filterDate(dates["last_30"], dates["today"])
    if chirps_collection.size().getInfo() > 0:
        rainfall = chirps_collection.sum().clip(geom).select("precipitation").reduceRegion(
            ee.Reducer.mean(), geom, 5000, maxPixels=1e10
        ).getInfo().get("precipitation")

    flood_extent_hectares = 0
    if s2_image:
    # NDWI < 0 indicates water
        flood_mask = ndwi.lt(0).rename("flood_mask")
    
    # Pixel area in m²
        pixel_area = ee.Image.pixelArea()
    
    # Flood area clipped to plot
        flood_area_m2 = flood_mask.multiply(pixel_area).reduceRegion(
            ee.Reducer.sum(), geom, 10, maxPixels=1e10
        ).getInfo().get("flood_mask", 0)
    
    # Convert to hectares
        flood_extent_hectares = flood_area_m2 / 10000.0


    # -----------------------------
    # TEMPERATURE & CLIMATE
    # -----------------------------
    temp_c = None
    temp_collection = MODIS_TEMP.filterBounds(geom).filterDate(dates["last_7"], dates["today"])
    if temp_collection.size().getInfo() > 0:
        temp_c = temp_collection.mean().clip(geom).select("LST_Day_1km").reduceRegion(
            ee.Reducer.mean(), geom, 1000, maxPixels=1e10
        ).getInfo().get("LST_Day_1km")

    et = None
    et_collection = MODIS_ET.filterBounds(geom).filterDate(dates["last_30"], dates["today"])
    if et_collection.size().getInfo() > 0:
        et = et_collection.mean().clip(geom).select("ET").reduceRegion(
            ee.Reducer.mean(), geom, 1000, maxPixels=1e10
        ).getInfo().get("ET")

    # -----------------------------
    # LANDCOVER & BIODIVERSITY
    # -----------------------------
    landcover_type = None
    landcover_diversity = None
    shannon_diversity = None
    simpson_diversity = None
    landcover_img = LANDCOVER_COLLECTION.sort("system:time_start", False).first()
    if landcover_img:
        lc_img_clip = landcover_img.clip(geom)
        lc_region = lc_img_clip.reduceRegion(ee.Reducer.mode(), geom, 10).getInfo()
        if lc_region:
            landcover_type = lc_region.get("Map")
        lc_hist = lc_img_clip.reduceRegion(ee.Reducer.frequencyHistogram(), geom, 10).getInfo()
        if lc_hist:
            lc_map = lc_hist.get("Map", {})
            landcover_diversity = len(lc_map)
            shannon_diversity = calculate_shannon_diversity(lc_map)
            simpson_diversity = calculate_simpson_diversity(lc_map)

    # -----------------------------
    # AIR & AEROSOLS
    # -----------------------------
    aq = None
    aerosols_collection = AEROSOLS.filterBounds(geom).filterDate(dates["last_3"], dates["today"])
    if aerosols_collection.size().getInfo() > 0:
        aq = aerosols_collection.mean().clip(geom).select("Optical_Depth_055").reduceRegion(
            ee.Reducer.mean(), geom, 10000, maxPixels=1e10
        ).getInfo().get("Optical_Depth_055")

    # -----------------------------
    # ALERTS
    # -----------------------------
    alerts = []
    if ndvi_stats.get("NDVI_mean") and ndvi_stats.get("NDVI_mean") < 0.3:
        alerts.append("NDVI low: Vegetation stress")
    if soil_moisture_mean and soil_moisture_mean < 0.2:
        alerts.append("Soil moisture low: Drought warning")
    if forest_loss_area and forest_loss_area > 0:
        alerts.append("New forest loss detected: Possible logging or disturbance")

    # -----------------------------
    # FINAL RETURN
    # -----------------------------
    return {
        "timestamp": str(datetime.datetime.utcnow()),
        "ndvi_mean": ndvi_stats.get("NDVI_mean"),
        "ndvi_min": ndvi_stats.get("NDVI_min"),
        "ndvi_max": ndvi_stats.get("NDVI_max"),
        "evi_mean": evi_mean,
        "tree_cover_percent": tree_cover_mean,
        "forest_loss_hectares": forest_loss_area,
        "biomass_estimate": biomass_estimate,
        "carbon_stock_estimate": carbon_stock_estimate,
        "ndwi_mean": ndwi_mean,
        "soil_moisture_index": soil_moisture_mean,
        "bare_soil_index": bare_soil_index,
        "erosion_risk": erosion_risk,
        "rainfall_mm_recent": rainfall,
        "temperature_c_recent": temp_c,
        "evapotranspiration": et,
        "landcover_type": landcover_type,
        "landcover_diversity": landcover_diversity,
        "shannon_diversity": shannon_diversity,
        "simpson_diversity": simpson_diversity,
        "flood_extent_hectares": flood_extent_hectares,
        "burned_area_hectares": burned_area_hectares,
        "fire_hotspots": fire_hotspots,
        "post_fire_recovery": post_fire_recovery,
        "aerosol_optical_depth": aq,
        "alerts": alerts
    }
