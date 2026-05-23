import ee
import datetime
import os

def get_tree_event_gee_report(event):
    """
    Generates a tree-level environmental report for a TreePlantingEvent.
    
    Parameters:
        event: TreePlantingEvent instance
    
    Returns:
        dict with event info and per-tree GEE metrics
    """
    # --- Prepare tree features ---
    tree_details = event.treeplantingdetail_set.all()
    features = []

    for detail in tree_details:
        # Skip trees without coordinates
        if detail.latitude is None or detail.longitude is None:
            continue

        point = ee.Geometry.Point([float(detail.longitude), float(detail.latitude)])
        buffer = point.buffer(5)  # 5m radius
        feature = ee.Feature(buffer, {
            "tree_id": detail.tree.id,
            "tree_name": detail.tree.name,
            "quantity": detail.quantity_planted
        })
        features.append(feature)

    if not features:
        return {"error": "No tree coordinates found for this event."}

    tree_fc = ee.FeatureCollection(features)

    # --- Date range ---
    start_date = event.date_planted.strftime('%Y-%m-%d')
    end_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')

    # --- Sentinel-2 imagery ---
    s2 = (ee.ImageCollection('COPERNICUS/S2_SR')
          .filterDate(start_date, end_date)
          .filterBounds(tree_fc)
          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
          )

    # --- Compute indices: NDVI, EVI, NDWI ---
    def add_indices(img):
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        evi = img.expression(
            '2.5 * ((B8 - B4)/(B8 + 6*B4 - 7.5*B2 + 1))',
            {'B8': img.select('B8'), 'B4': img.select('B4'), 'B2': img.select('B2')}
        ).rename('EVI')
        ndwi = img.normalizedDifference(['B3', 'B8']).rename('NDWI')
        return img.addBands([ndvi, evi, ndwi])

    s2 = s2.map(add_indices)

    # --- Sentinel-1 soil moisture proxy ---
    s1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
          .filterDate(start_date, end_date)
          .filterBounds(tree_fc)
          .filter(ee.Filter.eq('instrumentMode', 'IW'))
          .filter(ee.Filter.eq('resolution_meters', 10))
          .select('VH')
          )


# --- Tree Cover Proxy (public MODIS dataset, always accessible) ---
    vcf_collection = ee.ImageCollection("MODIS/006/MOD44B")

# Take the most recent image available
    vcf = vcf_collection.sort("system:time_start", False).first()

# Check if the band exists
    bands = vcf.bandNames().getInfo()
    if "Percent_Tree_Cover" not in bands:
        return {"error": "MOD44B image does not contain 'Percent_Tree_Cover' band."}

# Treat percent tree cover as biomass proxy
    biomass_img = vcf.select("Percent_Tree_Cover").rename("BIOMASS")

# Approximate carbon stock (not real carbon)
    carbon_img = biomass_img.multiply(0.47).rename("CARBON")




    # --- Merge all layers (median to reduce time series) ---
    s2_median = s2.median()
    s1_median = s1.median().rename('SOIL_MOISTURE')
    combined = s2_median.addBands([s1_median, biomass_img, carbon_img])


    # --- Reduce per tree buffer ---
    reducers = ee.Reducer.mean().combine(
        reducer2=ee.Reducer.minMax(),
        sharedInputs=True
    )

    tree_stats = combined.reduceRegions(
        collection=tree_fc,
        reducer=reducers,
        scale=10
    )

    # --- Fetch data safely ---
    try:
        tree_features = tree_stats.getInfo()['features']
    except Exception as e:
        return {"error": f"Failed to fetch GEE data: {str(e)}"}

    # --- Build per-tree reports ---
    tree_reports = []
    for f in tree_features:
        props = f['properties']

        # Alerts based on thresholds
        alerts = []
        ndvi = props.get('NDVI_mean')
        soil_m = props.get('SOIL_MOISTURE_mean')
        ndwi = props.get('NDWI_mean')

        if ndvi is not None and ndvi < 0.3:
            alerts.append("Low NDVI - possible stress")
        if soil_m is not None and soil_m < -20:
            alerts.append("Low soil moisture")
        if ndwi is not None and ndwi < 0:
            alerts.append("Low water content")

        tree_reports.append({
            "tree_id": props.get("tree_id"),
            "tree_name": props.get("tree_name"),
            "quantity": props.get("quantity"),
            "ndvi_mean": ndvi,
            "ndvi_min": props.get('NDVI_min'),
            "ndvi_max": props.get('NDVI_max'),
            "evi_mean": props.get('EVI_mean'),
            "ndwi_mean": ndwi,
            "soil_moisture_index": soil_m,
            "bare_soil_index": 1 - ndvi if ndvi else None,
            "biomass_estimate": props.get('BIOMASS_mean'),
            "carbon_stock_estimate": props.get('CARBON_mean'),
            "alerts": alerts
        })

    # --- Final event report ---
    report = {
        "event_id": event.id,
        "event_name": event.name,
        "plot_id": event.plot.id if event.plot else None,
        "date_planted": str(event.date_planted),
        "number_of_trees_planted": event.number_of_trees_planted,
        "location": {
            "latitude": float(event.latitude) if event.latitude else None,
            "longitude": float(event.longitude) if event.longitude else None,
        },
        "timestamp": str(datetime.datetime.utcnow()),
        "trees": tree_reports
    }

    return report 