from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TreeReportCache

@admin.register(TreeReportCache)
class TreeReportCacheAdmin(admin.ModelAdmin):
    list_display = ('tree', 'last_generated', 'last_monitoring_at')
    search_fields = ('tree__name',)
    readonly_fields = ('last_generated',)

    def has_add_permission(self, request):
        # Prevent adding manually, since cache is auto-generated
        return False

from django.contrib import admin
from .models import GEEPlotAnalysis, GEEAnalysis, GEEAnalysisHistory

# -----------------------------
# 1️⃣ GEE Plot Snapshot Admin
# -----------------------------
@admin.register(GEEPlotAnalysis)
class GEEPlotAnalysisAdmin(admin.ModelAdmin):
    list_display = ('plot', 'created_at', 'summary')
    list_filter = ('created_at', 'plot')
    search_fields = ('plot__name',)
    readonly_fields = ('created_at', 'raw_gee_data')
    ordering = ('-created_at',)

    # Simple summary for display
    def summary(self, obj):
        if obj.raw_gee_data:
            ndvi = obj.raw_gee_data.get('ndvi_mean')
            tree_cover = obj.raw_gee_data.get('tree_cover_percent')
            return f"NDVI: {ndvi}, Tree Cover: {tree_cover}%"
        return "No data"


# -----------------------------
# 2️⃣ GEE Processed Analysis Admin
# -----------------------------
@admin.register(GEEAnalysis)
class GEEAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'plot', 'analyzed_at', 'ndvi_mean', 'evi_mean',
        'tree_cover_percent', 'forest_loss_hectares',
        'ndwi_mean', 'soil_moisture_index', 'rainfall_mm_recent',
        'temperature_c_recent', 'aerosol_optical_depth', 'shannon_diversity', 'simpson_diversity'
    )
    list_filter = ('analyzed_at', 'plot')
    search_fields = ('plot__name',)
    readonly_fields = ('analyzed_at', 'raw_gee_data')
    ordering = ('-analyzed_at',)

    fieldsets = (
        ('Plot Info', {'fields': ('plot', 'analyzed_at')}),
        ('Vegetation & Trees', {'fields': (
            'ndvi_mean', 'ndvi_min', 'ndvi_max', 'evi_mean',
            'tree_cover_percent', 'canopy_density',
            'forest_loss_hectares', 'forest_gain_hectares',
            'biomass_estimate', 'carbon_stock_estimate'
        )}),
        ('Fire Detection', {'fields': (
            'fire_hotspots', 'burned_area_hectares', 'fire_severity_index', 'post_fire_recovery'
        )}),
        ('Water & Flood', {'fields': (
            'ndwi_mean', 'water_presence_percent', 'flood_extent_hectares'
        )}),
        ('Soil & Terrain', {'fields': (
            'soil_moisture_index', 'bare_soil_index', 'erosion_risk',
            'elevation_mean', 'slope_mean'
        )}),
        ('Climate', {'fields': (
            'rainfall_mm_recent', 'temperature_c_recent', 'evapotranspiration', 'drought_index'
        )}),
        ('Land Cover & Encroachment', {'fields': (
            'landcover_summary', 'encroachment_detected', 'encroachment_details'
        )}),
        ('Biodiversity', {'fields': (
            'habitat_fragmentation_score', 'vegetation_diversity_index',
            'shannon_diversity', 'simpson_diversity'
        )}),
        ('Air Quality', {'fields': (
            'aerosol_optical_depth', 'smoke_presence_probability'
        )}),
        ('Raw GEE Data', {'fields': ('raw_gee_data', 'alerts')}),
    )


# -----------------------------
# 3️⃣ Historical Snapshots Admin
# -----------------------------
@admin.register(GEEAnalysisHistory)
class GEEAnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ('plot', 'snapshot', 'archived_at')
    list_filter = ('archived_at', 'plot')
    search_fields = ('plot__name',)
    readonly_fields = ('archived_at',)
    ordering = ('-archived_at',)

from django.contrib import admin
from .models import TreeReportHistory

@admin.register(TreeReportHistory)
class TreeReportHistoryAdmin(admin.ModelAdmin):
    list_display = ('tree', 'created_at', 'last_monitoring_at')
    list_filter = ('created_at',)
    search_fields = ('tree__name', 'ai_summary')
    readonly_fields = ('created_at',)

from django.contrib import admin
from .models import EventReportCache, EventReportHistory

@admin.register(EventReportCache)
class EventReportCacheAdmin(admin.ModelAdmin):
    list_display = ('event', 'last_generated', 'survival_rate')
    readonly_fields = ('last_generated',)

@admin.register(EventReportHistory)
class EventReportHistoryAdmin(admin.ModelAdmin):
    list_display = ('event', 'created_at', 'survival_rate')
    list_filter = ('created_at',)
    search_fields = ('event__name', 'ai_summary')