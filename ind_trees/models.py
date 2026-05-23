from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse



class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class HeritageSite(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    featured_image = models.ImageField(
        upload_to='heri_imgs/', blank=True, help_text="A featured image for the heritage site."
    )

    def __str__(self):
        return self.name


class ConservationStatus(models.Model):
    STATUS_CHOICES = [
        ('LC', 'Least Concern'),
        ('NT', 'Near Threatened'),
        ('VU', 'Vulnerable'),
        ('EN', 'Endangered'),
        ('CR', 'Critically Endangered'),
        ('EW', 'Extinct in the Wild'),
        ('EX', 'Extinct'),
    ]

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
    #    default='LC',
        help_text="Select the conservation status of the species."
    )
    description = models.TextField(
        help_text="Provide a description explaining the selected conservation status."
    )

    def __str__(self):
        return self.get_status_display()


class Tree(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    name = models.CharField(max_length=200)
    species = models.ForeignKey('Species', on_delete=models.CASCADE, null=True, blank=True)
    plot = models.ForeignKey('Plot', on_delete=models.SET_NULL, null=True, blank=True)
    last_monitored = models.DateField(blank=True, null=True)
    categories = models.ManyToManyField(Category, help_text="Categories this tree belongs to.")
    tree_description = models.TextField(blank=True)
    origin = models.CharField(max_length=200, blank=True)
    pros = models.TextField(blank=True, help_text="Benefits of the tree.")
    cons = models.TextField(blank=True, help_text="Challenges associated with the tree.")
    medical_benefits = models.TextField(blank=True, help_text="Traditional medicinal uses.")
    general_use = models.TextField(blank=True, help_text="Applications such as timber, crafting, etc.")
    cultural_significance = models.TextField(blank=True, help_text="Symbolic or spiritual importance.")
    location = models.CharField(max_length=200, help_text="Geographical areas where found.")
    heritage_sites = models.ManyToManyField(
        HeritageSite, blank=True, help_text="Heritage sites associated with this tree."
    )
    conservation_status = models.ForeignKey(
        ConservationStatus, on_delete=models.CASCADE,
        help_text="Conservation status of the tree."
    )
    ecological_role = models.TextField(
        blank=True, help_text="Tree's role in biodiversity, soil health, ecosystem stability."
    )
    threats_and_conservation_efforts = models.TextField(
        blank=True, help_text="Threats and ongoing conservation efforts."
    )
    myths = models.TextField(blank=True, help_text="Traditional stories and folklore.")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('tree_detail', args=[str(self.id)])

    def generate_qr_code(self):
        """Generates and saves a QR code linking to the tree's detail page."""
        qr = qrcode.make(f"https://imvelo.yveeswatini.africa{self.get_absolute_url()}")
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"qr_{self.id}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Override save method to generate QR code every time the tree is saved."""
        super().save(*args, **kwargs)
        self.generate_qr_code()
        super().save(update_fields=['qr_code'])

class TreeImage(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='tree_imgs/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image.")

    def __str__(self):
        return f"Image for {self.tree.name}"


class HeritageSiteImage(models.Model):
    heritage_site = models.ForeignKey(
        HeritageSite,
        on_delete=models.CASCADE,
        related_name="heritage_site_images",  # Unique related_name
    )
    image = models.ImageField(upload_to='heri_imgs/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image.")

    def __str__(self):
        return f"Image for {self.heritage_site.name}"


class MedicalBenefitImage(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="medical_benefit_images")
    image = models.ImageField(upload_to='medical_benefit_imgs/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image.")

    def __str__(self):
        return f"Medical benefit image for {self.tree.name}"


class CulturalSignificanceImage(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="cultural_significance_images")
    image = models.ImageField(upload_to='cultural_significance_imgs/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image.")

    def __str__(self):
        return f"Cultural significance image for {self.tree.name}"


class ThreatsConservationImage(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="threats_conservation_images")
    image = models.ImageField(upload_to='threats_conservation_imgs/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image.")

    def __str__(self):
        return f"Threats and conservation image for {self.tree.name}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.email


########
class TreePlantingDetail(models.Model):
    tree = models.ForeignKey('Tree', on_delete=models.CASCADE)
    event = models.ForeignKey('TreePlantingEvent', on_delete=models.CASCADE)
    quantity_planted = models.PositiveIntegerField(default=1, help_text="Number of this tree species planted in the event")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        unique_together = ('tree', 'event')

    def __str__(self):
        coord_str = f" ({self.latitude}, {self.longitude})" if self.latitude and self.longitude else ""
        return f"{self.quantity_planted} of {self.tree.name} at {self.event.name}{coord_str}"


class TreePlantingEvent(models.Model):
    trees = models.ManyToManyField('Tree', through='TreePlantingDetail', related_name='planting_events', blank=True)
    name = models.CharField(max_length=255, help_text="Name of the planting event or project.")
    organizer = models.CharField(max_length=255, help_text="Organization or individual who organized the planting.")
    plot = models.ForeignKey('Plot', on_delete=models.CASCADE, related_name='environmental_data', null=True, blank=True)
    location = models.CharField(max_length=255, help_text="Where the event took place.")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    date_planted = models.DateField()
    number_of_trees_planted = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.date_planted})"
    
    def first_image(self):
        return self.images.first()
    
class TreePlantingEventImage(models.Model):
    event = models.ForeignKey(TreePlantingEvent, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='planting_event_imgs/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image.")

    def __str__(self):
        return f"Image for {self.event.name}"


from django.db import models

class TreeMonitoringRecord(models.Model):
    plot = models.ForeignKey('Plot', on_delete=models.CASCADE, blank=True, null=True)
    trees = models.ManyToManyField('Tree', related_name='monitoring_records')
    planting_event = models.ForeignKey(TreePlantingEvent, on_delete=models.SET_NULL, null=True, blank=True, help_text="Optional link to the planting event.")
    monitored_at = models.DateTimeField(auto_now_add=True)
    monitored_by = models.CharField(max_length=100, help_text="Name of the person or organization.")
    
    alive_count = models.PositiveIntegerField(help_text="Number of surviving trees (if group).", default=0)
    dead_count = models.PositiveIntegerField(default=0, help_text="How many trees have died (if any).")
    health_status = models.CharField(max_length=100, help_text="E.g., Healthy, Diseased, Pest-infested, Drying")
    
    threats_observed = models.TextField(blank=True)
    conservation_actions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    intervention = models.ForeignKey('TreeIntervention', on_delete=models.SET_NULL, null=True, blank=True, help_text="interventions done on trees")
    monitoring_schedule = models.ForeignKey('MonitoringSchedule', on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        ordering = ['-monitored_at']

    def __str__(self):
        tree_names = ", ".join(tree.name for tree in self.trees.all())
        planting_event_name = f" | Event: {self.planting_event.name}" if self.planting_event else ""
        return f"Monitoring [{tree_names}] on {self.monitored_at.date()}{planting_event_name}"

class MonitoredTreeDetail(models.Model):
    monitoring_record = models.ForeignKey(TreeMonitoringRecord, on_delete=models.CASCADE, related_name='monitored_trees')
    tree = models.ForeignKey('Tree', on_delete=models.CASCADE)
    alive_count = models.PositiveIntegerField(default=0)
    dead_count = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True, help_text="Optional notes about this tree species")

    class Meta:
        unique_together = ('monitoring_record', 'tree')

    def __str__(self):
        return f"{self.tree.name}: {self.alive_count} alive, {self.dead_count} dead"

class TreeMonitoringPhoto(models.Model):
    monitoring_record = models.ForeignKey(TreeMonitoringRecord, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='monitoring_photos/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Photo for monitoring on {self.monitoring_record.monitored_at.date()}"


class PlotMonitoringRecord(models.Model):
    plot = models.ForeignKey('Plot', on_delete=models.CASCADE, related_name='monitoring_records', null=True)
    monitored_at = models.DateTimeField(auto_now_add=True)
    monitored_by = models.CharField(max_length=255, help_text="Name of the ranger, researcher, or organization.")
    monitoring_schedule = models.ForeignKey('MonitoringSchedule', on_delete=models.SET_NULL, null=True, blank=True)
    
    vegetation_cover = models.TextField(help_text="General observation on vegetation cover, changes, or degradation.", blank=True)
    invasive_species_present = models.BooleanField(default=False)
    invasive_species_details = models.TextField(blank=True, help_text="Details of observed invasive species, if any.")
    signs_of_deforestation = models.BooleanField(default=False)
    signs_of_fire = models.BooleanField(default=False)
    illegal_activities_observed = models.TextField(blank=True, help_text="E.g., poaching, illegal logging, charcoal burning")
    wildlife_presence = models.TextField(blank=True, help_text="Observed wildlife species or evidence of wildlife")
    
    soil_erosion_signs = models.BooleanField(default=False)
    erosion_notes = models.TextField(blank=True)
    
    water_conditions = models.TextField(blank=True, help_text="Condition of nearby water sources, wetness, pollution signs, etc.")
    human_activity_notes = models.TextField(blank=True, help_text="Encroachment, grazing, settlements, road construction, etc.")
    
    threats_identified = models.TextField(blank=True)
    recommended_actions = models.TextField(blank=True)
    intervention = models.ForeignKey('TreeIntervention', on_delete=models.SET_NULL, null=True, blank=True, help_text="Intervention action taken on the plot level.")
    water_quality = models.CharField(max_length=100, blank=True, null=True)
    air_quality = models.CharField(max_length=100, blank=True, null=True)
  
    weather_conditions = models.CharField(max_length=255, blank=True, help_text="Weather during monitoring (e.g., sunny, rainy)")
    notes = models.TextField(blank=True)
    next_monitoring_due = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-monitored_at']

    def __str__(self):
        return f"Monitoring Report for {self.plot.name} on {self.monitored_at.date()}"

class PlotMonitoringPhoto(models.Model):
    monitoring_record = models.ForeignKey(PlotMonitoringRecord, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='plot_monitoring_photos/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Photo for {self.monitoring_record.plot.name} on {self.monitoring_record.monitored_at.date()}"



##########adons
from django.db import models
from django.contrib.gis.db import models as geomodels

# Choices examples
IUCN_CHOICES = [
    ('LC', 'Least Concern'),
    ('NT', 'Near Threatened'),
    ('VU', 'Vulnerable'),
    ('EN', 'Endangered'),
    ('CR', 'Critically Endangered'),
    ('EW', 'Extinct in the Wild'),
    ('EX', 'Extinct'),
]

LAND_TYPE_CHOICES = [
    ('protected', 'Protected Area'),
    ('private', 'Private Land'),
    ('communal', 'Communal Land'),
]

PROTECTION_CHOICES = [
    ('protected', 'Protected'),
    ('vulnerable', 'Vulnerable'),
    ('remediation', 'Remediation Zone'),
]

ZONE_CHOICES = [
    ('conservation', 'Conservation Forest'),
    ('communal', 'Communal Land'),
    ('municipal', 'Municipal Area'),
]

INTERVENTION_CHOICES = [
    ('planting', 'Planting'),
    ('pruning', 'Pruning'),
    ('disease_control', 'Disease Control'),
    ('fencing', 'Fencing'),
    ('other', 'Other'),
]

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('ranger', 'Ranger'),
    ('researcher', 'Researcher'),
    ('public', 'Public'),
]

# 1. Species Model (optional, to reuse species data)
class Species(models.Model):
    scientific_name = models.CharField(max_length=255, unique=True)
    common_name = models.CharField(max_length=255)
    family = models.CharField(max_length=255, blank=True, null=True)
    iucn_status = models.CharField(max_length=2, choices=IUCN_CHOICES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"
    
class TreeIntervention(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='interventions')
    action = models.CharField(max_length=50, choices=INTERVENTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    observer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.get_action_display()} on Tree {self.tree.id} at {self.date}"

# 2. Plot / Location Model
class Plot(models.Model):
    name = models.CharField(max_length=100)
    area_hectares = models.FloatField(blank=True)
    land_ownership = models.CharField(max_length=50, choices=LAND_TYPE_CHOICES)
    protection_status = models.CharField(max_length=50, choices=PROTECTION_CHOICES)
    zone_type = models.CharField(max_length=50, choices=ZONE_CHOICES)
    location = models.CharField(max_length=100, null=True, blank= True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    boundary_coordinates = models.JSONField(blank=True, null=True)
    land_data = models.ForeignKey('EnvironmentalData', on_delete=models.CASCADE, related_name='environmental_data', null=True, blank=True)

    def __str__(self):
        return self.name

class PlotImage(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='plot_imgs/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image.")

    def __str__(self):
        return f"Image for {self.plot.name}"
    

# 5. Environmental Data for Plots
class EnvironmentalData(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='land', null=True, blank=True)
    soil_type = models.CharField(max_length=100)
    soil_pH = models.FloatField()
    fertility_level = models.CharField(max_length=100)
    rainfall_mm = models.FloatField()
    temperature_c = models.FloatField()
    water_source_proximity = models.CharField(max_length=100)
    biodiversity_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        # You need to get the related plot from the reverse relation
        plot = self.environmental_data.first()
        plot_name = plot.name if plot else "Unknown Plot"
        return f"Environmental Data for {plot_name}"


# 6. Monitoring Schedule
class MonitoringSchedule(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    frequency_days = models.PositiveIntegerField(help_text="Days between monitoring")
    next_due = models.DateField()
    assigned_to = models.CharField(max_length=255)  # could link to User later

    def __str__(self):
        return f"Monitoring for {self.plot.name} every {self.frequency_days} days"

# 7. Stakeholders
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

# 8. Compliance and Permitting
class ComplianceRecord(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    permit_number = models.CharField(max_length=255)
    legal_status = models.CharField(max_length=255)
    valid_from = models.DateField()
    valid_until = models.DateField()
    notes = models.TextField(blank=True, null=True)

#    def __str__(self):
 #       return f"Permit {self.permit_number} for {self.plot.name}"

# 9. Public Engagement: Crowdsourced Photo Reporting
#class PublicReport(models.Model):
#    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='public_reports')
    #reporter_name = models.CharField(max_length=255)
   # reporter_contact = models.CharField(max_length=255, blank=True, null=True)
  #  photo = models.ImageField(upload_to='public_reports/photos/')
 #   description = models.TextField(blank=True, null=True)
#    date_reported = models.DateTimeField(auto_now_add=True)
#    verified = models.BooleanField(default=False)

#    def __str__(self):
#        return f"Report on Tree {self.tree.id} by {self.reporter_name}"

# 10. User Permissions / Roles (if you want custom users)
#from django.contrib.auth.models import AbstractUser

#class CustomUser(AbstractUser):
 #   role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='public')

# 11. Audit Logs for changes (basic example)
#class AuditLog(models.Model):
   # user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    #action = models.CharField(max_length=255)
   # model_name = models.CharField(max_length=255)
  #  object_id = models.PositiveIntegerField()
  #  timestamp = models.DateTimeField(auto_now_add=True)
 #   details = models.TextField(blank=True, null=True)

 #   def __str__(self):
#        return f"{self.action} on {self.model_name}({self.object_id}) by {self.user}"

