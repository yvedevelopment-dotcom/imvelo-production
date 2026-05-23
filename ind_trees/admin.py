from django.contrib import admin
from .models import Category, HeritageSite, ConservationStatus, Tree, TreeImage, HeritageSiteImage, MedicalBenefitImage, CulturalSignificanceImage, ThreatsConservationImage, Subscriber

# Register models for the admin interface
admin.site.register(Category)
admin.site.register(HeritageSite)
admin.site.register(ConservationStatus)
admin.site.register(Tree)
admin.site.register(TreeImage)
admin.site.register(HeritageSiteImage)
admin.site.register(MedicalBenefitImage)
admin.site.register(CulturalSignificanceImage)
admin.site.register(ThreatsConservationImage)
admin.site.register(Subscriber)


from django.contrib import admin
from .models import TreeMonitoringRecord, PlotImage


from django.contrib import admin
from .models import TreePlantingDetail, TreePlantingEvent, TreePlantingEventImage

class TreePlantingDetailInline(admin.TabularInline):
    model = TreePlantingDetail
    extra = 1

class TreePlantingEventImageInline(admin.TabularInline):
    model = TreePlantingEventImage
    extra = 1

@admin.register(TreePlantingEvent)
class TreePlantingEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizer', 'location', 'date_planted', 'number_of_trees_planted')
    search_fields = ('name', 'organizer', 'location')
    list_filter = ('date_planted',)
    inlines = [TreePlantingDetailInline, TreePlantingEventImageInline]

@admin.register(TreePlantingDetail)
class TreePlantingDetailAdmin(admin.ModelAdmin):
    list_display = ('tree', 'event', 'quantity_planted', 'latitude', 'longitude')
    list_filter = ('event', 'tree')
    search_fields = ('tree__name', 'event__name')

@admin.register(TreePlantingEventImage)
class TreePlantingEventImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption')





class PlotImageInline(admin.TabularInline):
    model = PlotImage
    extra = 1
admin.site.register(PlotImage)


@admin.register(TreeMonitoringRecord)
class TreeMonitoringRecordAdmin(admin.ModelAdmin):
    list_display = ('plot', 'planting_event', 'monitored_by', 'monitored_at', 'alive_count', 'dead_count', 'health_status')
    search_fields = ('tree__name', 'monitored_by')
    list_filter = ('monitored_at', 'health_status')
    readonly_fields = ('monitored_at',)

from .models import TreeMonitoringRecord, TreeMonitoringPhoto

class TreeMonitoringPhotoInline(admin.TabularInline):
    model = TreeMonitoringPhoto
    extra = 1  # Number of empty forms to display
    fields = ['image', 'caption']
    readonly_fields = []

@admin.register(TreeMonitoringPhoto)
class TreeMonitoringPhotoAdmin(admin.ModelAdmin):
    list_display = ('monitoring_record', 'image', 'caption')
    search_fields = ['caption']





from django.contrib import admin
from .models import (
    Species,
    Plot,
    TreeIntervention,
    EnvironmentalData,
    MonitoringSchedule,
    Stakeholder,
    ComplianceRecord
)

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'family', 'iucn_status')
    search_fields = ('common_name', 'scientific_name')
    list_filter = ('iucn_status', 'family')

@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_hectares', 'land_ownership', 'protection_status', 'zone_type')
    search_fields = ('name',)
    list_filter = ('land_ownership', 'protection_status', 'zone_type')

@admin.register(TreeIntervention)
class TreeInterventionAdmin(admin.ModelAdmin):
    list_display = ('tree', 'action', 'date', 'observer')
    search_fields = ('tree__id', 'observer')
    list_filter = ('action', 'date')

@admin.register(EnvironmentalData)
class EnvironmentalDataAdmin(admin.ModelAdmin):
    list_display = ('soil_type', 'soil_pH', 'fertility_level', 'rainfall_mm', 'temperature_c')
    search_fields = ('soil_type',)
    list_filter = ('fertility_level',)

@admin.register(MonitoringSchedule)
class MonitoringScheduleAdmin(admin.ModelAdmin):
    list_display = ('plot', 'frequency_days', 'next_due', 'assigned_to')
    search_fields = ('plot__name', 'assigned_to')
    list_filter = ('next_due',)

@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'role', 'organization')
    search_fields = ('name', 'contact_person', 'organization')
    list_filter = ('role',)

@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ('plot', 'permit_number', 'legal_status', 'valid_from', 'valid_until')
    search_fields = ('permit_number', 'legal_status')
    list_filter = ('valid_from', 'valid_until')

from django.contrib import admin
from .models import PlotMonitoringRecord, PlotMonitoringPhoto

class PlotMonitoringPhotoInline(admin.TabularInline):
    model = PlotMonitoringPhoto
    extra = 1

@admin.register(PlotMonitoringRecord)
class PlotMonitoringRecordAdmin(admin.ModelAdmin):
    list_display = ('plot', 'monitored_at', 'monitored_by', 'invasive_species_present', 'signs_of_deforestation', 'signs_of_fire')
    list_filter = ('monitored_at', 'invasive_species_present', 'signs_of_deforestation', 'signs_of_fire')
    search_fields = ('plot__name', 'monitored_by', 'illegal_activities_observed', 'threats_identified', 'recommended_actions')
    inlines = [PlotMonitoringPhotoInline]
    readonly_fields = ('monitored_at',)

@admin.register(PlotMonitoringPhoto)
class PlotMonitoringPhotoAdmin(admin.ModelAdmin):
    list_display = ('monitoring_record', 'caption')
    search_fields = ('caption',)

