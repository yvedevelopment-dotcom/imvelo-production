from rest_framework import serializers
from .models import (
    Tree, TreeImage, Category, HeritageSite, HeritageSiteImage,
    ConservationStatus, TreePlantingEvent, TreeMonitoringRecord,
    Plot, PlotMonitoringRecord
)

# ---------- Small helpers ----------
class TreeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeImage
        fields = ['id', 'image', 'caption']

class HeritageSiteImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeritageSiteImage
        fields = ['id', 'image', 'caption']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class HeritageSiteSerializer(serializers.ModelSerializer):
    images = HeritageSiteImageSerializer(many=True, read_only=True, source='heritage_site_images')
    class Meta:
        model = HeritageSite
        fields = ['id', 'name', 'description', 'location', 'images']

class ConservationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConservationStatus
        fields = '__all__'
        
# ---------- Tree Serializers ----------
class TreeListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    species_name = serializers.SerializerMethodField()

    class Meta:
        model = Tree
        fields = [
            'id', 'name', 'species_name', 'tree_description',
            'categories',
        ]

    def get_species_name(self, obj):
        if hasattr(obj, 'species') and obj.species:
            return obj.species.common_name if hasattr(obj.species, 'common_name') else str(obj.species)
        return None

class TreeDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    images = TreeImageSerializer(many=True, read_only=True)
    heritage_sites = HeritageSiteSerializer(many=True, read_only=True)
    conservation_status = ConservationStatusSerializer(read_only=True)
    species_name = serializers.SerializerMethodField()

    class Meta:
        model = Tree
        fields = [
            'id', 'name', 'species_name', 'tree_description',
            'categories', 'images', 'heritage_sites',
            'conservation_status',
            'latitude', 'longitude',
            'created_at', 'updated_at'
        ]

    def get_species_name(self, obj):
        if hasattr(obj, 'species') and obj.species:
            return obj.species.common_name if hasattr(obj.species, 'common_name') else str(obj.species)
        return None

# ---------- Event & Monitoring ----------
class TreePlantingEventSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source='plot.name', read_only=True, allow_null=True)
    class Meta:
        model = TreePlantingEvent
        fields = [
            'id', 'name', 'date_planted', 'location',
            'organizer', 'number_of_trees_planted',
            'plot_name', 'notes'
        ]

class TreeMonitoringRecordSerializer(serializers.ModelSerializer):
    tree_names = serializers.SerializerMethodField()
    plot_name = serializers.CharField(source='plot.name', read_only=True, allow_null=True)
    class Meta:
        model = TreeMonitoringRecord
        fields = [
            'id', 'monitored_at', 'alive_count', 'dead_count',
            'health_status', 'threats_observed',
            'conservation_actions', 'tree_names', 'plot_name'
        ]
    def get_tree_names(self, obj):
        return [tree.name for tree in obj.trees.all()]

# ---------- Plot ----------
class PlotSerializer(serializers.ModelSerializer):
    soil_type = serializers.CharField(source='land_data.soil_type', read_only=True, allow_null=True)
    soil_pH = serializers.FloatField(source='land_data.soil_pH', read_only=True, allow_null=True)
    fertility_level = serializers.CharField(source='land_data.fertility_level', read_only=True, allow_null=True)
    rainfall_mm = serializers.FloatField(source='land_data.rainfall_mm', read_only=True, allow_null=True)
    temperature_c = serializers.FloatField(source='land_data.temperature_c', read_only=True, allow_null=True)

    class Meta:
        model = Plot
        fields = [
            'id', 'name', 'area_hectares', 'land_ownership',
            'zone_type', 'latitude', 'longitude',
            'soil_type', 'soil_pH', 'fertility_level',
            'rainfall_mm', 'temperature_c'
        ]

class PlotMonitoringRecordSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source='plot.name', read_only=True)
    class Meta:
        model = PlotMonitoringRecord
        fields = [
            'id', 'monitored_at', 'vegetation_cover',
            'invasive_species_present', 'signs_of_deforestation',
            'signs_of_fire', 'human_activity_notes',
            'plot_name'
        ]