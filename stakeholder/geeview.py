from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import GEEPlotAnalysis, GEEAnalysis
from ind_trees.models import Plot
from .gee import analyze_plot
import json

class GEEPlotAnalysisView(View):
    """
    API endpoint or admin-triggered view to run GEE analysis on a single Plot.
    GET request triggers analysis and saves result.
    """

    def get(self, request, plot_id):
        plot = get_object_or_404(Plot, id=plot_id)

        if not plot.boundary_coordinates:
            return JsonResponse({
                "status": "error",
                "message": "Plot does not have boundary coordinates."
            }, status=400)

        try:
            # Convert [lat, lng] to [lng, lat] GeoJSON polygon
            coords_latlng = plot.boundary_coordinates
            geojson_polygon = {
                "type": "Polygon",
                "coordinates": [[ [lng, lat] for lat, lng in coords_latlng ]]
            }

            # Run GEE analysis
            gee_data = analyze_plot(geojson_polygon)

            # -----------------------------
            # 1️⃣ Save raw snapshot
            # -----------------------------
            snapshot = GEEPlotAnalysis.objects.create(
                raw_gee_data=gee_data
            )

            # -----------------------------
            # 2️⃣ Save processed metrics
            # -----------------------------
            landcover_summary = {
                "main_type": gee_data.get("landcover_type"),
                "diversity": gee_data.get("landcover_diversity"),
                "shannon_diversity": gee_data.get("shannon_diversity"),
                "simpson_diversity": gee_data.get("simpson_diversity")
            }

            analysis = GEEAnalysis.objects.create(
                plot=plot,
                ndvi_mean=gee_data.get("ndvi_mean"),
                ndvi_min=gee_data.get("ndvi_min"),
                ndvi_max=gee_data.get("ndvi_max"),
                evi_mean=gee_data.get("evi_mean"),
                tree_cover_percent=gee_data.get("tree_cover_percent"),
                forest_loss_hectares=gee_data.get("forest_loss_hectares"),
                ndwi_mean=gee_data.get("ndwi_mean"),
                soil_moisture_index=gee_data.get("soil_moisture_index"),
                rainfall_mm_recent=gee_data.get("rainfall_mm_recent"),
                temperature_c_recent=gee_data.get("temperature_c_recent"),
                evapotranspiration=gee_data.get("evapotranspiration"),
                bare_soil_index=gee_data.get("bare_soil_index"),
                burned_area_hectares=gee_data.get("burned_area_hectares"),
                post_fire_recovery=gee_data.get("post_fire_recovery"),
                aerosol_optical_depth=gee_data.get("aerosol_optical_depth"),
                erosion_risk=gee_data.get("erosion_risk"),
                flood_extent_hectares=gee_data.get("flood_extent_hectares"),  # ✅ fixed
                alerts=json.dumps(gee_data.get("alerts", [])),
                landcover_summary=json.dumps(landcover_summary),
                raw_gee_data=json.dumps(gee_data)
            )

            return JsonResponse({
                "status": "success",
                "message": f"GEE analysis completed for plot {plot.name}",
                "data": gee_data
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)


# views.py
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ind_trees.models import TreePlantingEvent
from .gee_event import get_tree_event_gee_report  # import your function

class TreeEventGEEReportView(View):
    """
    Initiates a GEE report for a TreePlantingEvent.
    Returns JSON containing per-tree metrics and alerts.
    """

    def get(self, request, event_id, *args, **kwargs):
        # Fetch the event or return 404
        event = get_object_or_404(TreePlantingEvent, id=event_id)

        # Run GEE script (the function you already have)
        report = get_tree_event_gee_report(event)

        # Return JSON
        return JsonResponse(report, safe=False)
