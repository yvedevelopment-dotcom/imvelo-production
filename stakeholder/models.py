from django.db import models

# Create your models here.
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('ranger', 'Ranger'),
    ('researcher', 'Researcher'),
    ('public', 'Public'),
]

class Stakeholder(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    organization = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



##reports
# models.py
from django.db import models
from django.utils import timezone
from ind_trees.models import Tree

class TreeReportCache(models.Model):
    tree = models.OneToOneField(Tree, on_delete=models.CASCADE, related_name='cached_report')
    html_report = models.TextField()
    ai_summary = models.TextField()
    last_generated = models.DateTimeField(auto_now=True)
    last_monitoring_at = models.DateTimeField(null=True, blank=True)
    survival_trend_json = models.JSONField(default=list, blank=True)
    map_lat = models.FloatField(null=True, blank=True)
    map_lng = models.FloatField(null=True, blank=True)
    monitoring_points = models.JSONField(null=True, blank=True)
    survival_trend_dates = models.JSONField(default=list, blank=True)
    survival_trend_alive = models.JSONField(default=list, blank=True)
    survival_trend_dead = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Cached report for {self.tree.name}"

# models.py
class TreeReportHistory(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='report_history')
    html_report = models.TextField()
    ai_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_generated = models.DateTimeField(auto_now=True)
    last_monitoring_at = models.DateTimeField(null=True, blank=True)
    survival_trend_dates = models.JSONField(default=list, blank=True)
    survival_trend_alive = models.JSONField(default=list, blank=True)
    survival_trend_dead = models.JSONField(default=list, blank=True)
    map_lat = models.FloatField(null=True, blank=True)
    map_lng = models.FloatField(null=True, blank=True)
    monitoring_points = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']



# models.py (in your reports or events app)
from django.db import models
from ind_trees.models import TreePlantingEvent

class EventReportCache(models.Model):
    """
    One‑to‑one link to the latest generated report for quick access.
    """
    event = models.OneToOneField(
        TreePlantingEvent,
        on_delete=models.CASCADE,
        related_name='cached_report'
    )
    html_report = models.TextField(blank=True, null=True)   # full rendered content (partial)
    ai_summary = models.TextField(blank=True, null=True)
    last_generated = models.DateTimeField(auto_now=True)
    last_monitoring_at = models.DateTimeField(null=True, blank=True)
    total_trees_planted = models.IntegerField(default=0)
    survival_rate = models.FloatField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Cached report for event '{self.event.name}'"


class EventReportHistory(models.Model):
    """
    Permanent archive – every generated report is stored here.
    """
    event = models.ForeignKey(
        TreePlantingEvent,
        on_delete=models.CASCADE,
        related_name='report_history'
    )
    html_report = models.TextField(blank=True, null=True)
    ai_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_monitoring_at = models.DateTimeField(null=True, blank=True)
    total_trees_planted = models.IntegerField(default=0)
    survival_rate = models.FloatField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report for event '{self.event.name}' on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
##from django.db import modelsfrom django.db import models
from django.utils import timezone
from ind_trees.models import Plot

# ---------------------------------------------------
# 1. Raw GEE snapshot
# ---------------------------------------------------
class GEEPlotAnalysis(models.Model):
    """
    Stores automated GEE-based environmental analysis snapshot.
    One record = one analysis run (e.g., daily or on-demand)
    """
    plot = models.ForeignKey(
        Plot,
        on_delete=models.CASCADE,
        related_name='gee_snapshots',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    raw_gee_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.plot:
            return f"GEE Snapshot for {self.plot.name} ({self.created_at.date()})"
        return f"GEE Snapshot ({self.created_at.date()})"


# ---------------------------------------------------
# 2. Processed GEE metrics per plot
# ---------------------------------------------------
class GEEAnalysis(models.Model):
    """
    Stores processed GEE metrics for a specific Plot.
    """
    plot = models.ForeignKey(
        Plot,
        on_delete=models.CASCADE,
        related_name='gee_analysis'
    )
    analyzed_at = models.DateTimeField(default=timezone.now)

    # -----------------------------
    # Vegetation & Tree Health
    # -----------------------------
    ndvi_mean = models.FloatField(null=True, blank=True)
    ndvi_min = models.FloatField(null=True, blank=True)
    ndvi_max = models.FloatField(null=True, blank=True)
    evi_mean = models.FloatField(null=True, blank=True)
    tree_cover_percent = models.FloatField(null=True, blank=True)
    canopy_density = models.FloatField(null=True, blank=True)
    forest_loss_hectares = models.FloatField(null=True, blank=True)
    forest_gain_hectares = models.FloatField(null=True, blank=True)
    biomass_estimate = models.FloatField(null=True, blank=True)
    carbon_stock_estimate = models.FloatField(null=True, blank=True)

    # -----------------------------
    # Fire Detection
    # -----------------------------
    fire_hotspots = models.IntegerField(null=True, blank=True)
    burned_area_hectares = models.FloatField(null=True, blank=True)
    fire_severity_index = models.FloatField(null=True, blank=True)
    post_fire_recovery = models.FloatField(null=True, blank=True)

    # -----------------------------
    # Water & Flood Monitoring
    # -----------------------------
    ndwi_mean = models.FloatField(null=True, blank=True)
    water_presence_percent = models.FloatField(null=True, blank=True)
    flood_extent_hectares = models.FloatField(null=True, blank=True)

    # -----------------------------
    # Soil & Terrain
    # -----------------------------
    soil_moisture_index = models.FloatField(null=True, blank=True)
    bare_soil_index = models.FloatField(null=True, blank=True)
    erosion_risk = models.CharField(max_length=50, blank=True, null=True)
    elevation_mean = models.FloatField(null=True, blank=True)
    slope_mean = models.FloatField(null=True, blank=True)

    # -----------------------------
    # Climate Conditions
    # -----------------------------
    rainfall_mm_recent = models.FloatField(null=True, blank=True)
    temperature_c_recent = models.FloatField(null=True, blank=True)
    evapotranspiration = models.FloatField(null=True, blank=True)
    drought_index = models.FloatField(null=True, blank=True)

    # -----------------------------
    # Land Cover & Encroachment
    # -----------------------------
    landcover_summary = models.JSONField(null=True, blank=True)
    encroachment_detected = models.BooleanField(default=False)
    encroachment_details = models.TextField(blank=True, null=True)

    # -----------------------------
    # Biodiversity (Indirect)
    # -----------------------------
    habitat_fragmentation_score = models.FloatField(null=True, blank=True)
    vegetation_diversity_index = models.FloatField(null=True, blank=True)
    shannon_diversity = models.FloatField(null=True, blank=True)
    simpson_diversity = models.FloatField(null=True, blank=True)

    # -----------------------------
    # Air Quality
    # -----------------------------
    aerosol_optical_depth = models.FloatField(null=True, blank=True)
    smoke_presence_probability = models.FloatField(null=True, blank=True)

    # -----------------------------
    # Raw GEE outputs (optional)
    # -----------------------------
    raw_gee_data = models.JSONField(null=True, blank=True)
    alerts = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"GEE Analysis for {self.plot.name} at {self.analyzed_at.date()}"


# ---------------------------------------------------
# 3. Historical snapshots of GEE analyses
# ---------------------------------------------------
class GEEAnalysisHistory(models.Model):
    """
    Historical snapshots of GEE analyses per plot.
    """
    plot = models.ForeignKey(
        Plot,
        on_delete=models.CASCADE,
        related_name='gee_history'
    )
    snapshot = models.ForeignKey(
        GEEPlotAnalysis,
        on_delete=models.CASCADE,
        related_name='history_records'
    )
    archived_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-archived_at']

    def __str__(self):
        return f"Historical Snapshot for {self.plot.name} on {self.archived_at.date()}"
