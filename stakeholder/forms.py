from django import forms
from ind_trees.models import (
    Tree, TreeImage, MedicalBenefitImage, CulturalSignificanceImage,
    ThreatsConservationImage, Plot, Species, Category,
    HeritageSite, ConservationStatus, EnvironmentalData
)
from django.forms import inlineformset_factory
class TreeForm(forms.ModelForm):
    class Meta:
        model = Tree
        exclude = ['qr_code', 'last_monitored']  # Keep related fields
        widgets = {
            'species': forms.Select(attrs={'class': 'select2'}),
            'plot': forms.Select(attrs={'class': 'select2'}),
            'categories': forms.SelectMultiple(attrs={'class': 'select2'}),
            'heritage_sites': forms.SelectMultiple(attrs={'class': 'select2'}),
            'conservation_status': forms.Select(attrs={'class': 'select2'}),

        }

# Formsets for images
TreeImageFormSet = inlineformset_factory(
    Tree,
    TreeImage,
    fields=['image', 'caption'],
    extra=5,
    can_delete=True,
    widgets={
        'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
        'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
    }
)

MedicalImageFormSet = inlineformset_factory(
    Tree,
    MedicalBenefitImage,
    fields=['image', 'caption'],
    extra=5,
    can_delete=True,
    widgets={
        'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
        'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
    }
)

CulturalImageFormSet = inlineformset_factory(
    Tree,
    CulturalSignificanceImage,
    fields=['image', 'caption'],
    extra=5,
    can_delete=True,
    widgets={
        'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
        'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
    }
)

# Related forms
class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = '__all__'

class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = '__all__'

class LandDataForm(forms.ModelForm):
    class Meta:
        model = EnvironmentalData
        exclude = ['plot'] 
        fields = '__all__'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class HeritageSiteForm(forms.ModelForm):
    class Meta:
        model = HeritageSite
        fields = '__all__'

class ConservationStatusForm(forms.ModelForm):
    class Meta:
        model = ConservationStatus
        fields = '__all__'

# Image formsets
TreeImageFormSet = inlineformset_factory(Tree, TreeImage, fields=('image', 'caption'), extra=2, can_delete=True)
MedicalImageFormSet = inlineformset_factory(Tree, MedicalBenefitImage, fields=('image', 'caption'), extra=2, can_delete=True)
CulturalImageFormSet = inlineformset_factory(Tree, CulturalSignificanceImage, fields=('image', 'caption'), extra=2, can_delete=True)
ThreatsImageFormSet = inlineformset_factory(Tree, ThreatsConservationImage, fields=('image', 'caption'), extra=2, can_delete=True)


from django import forms
from django.forms import inlineformset_factory
from ind_trees.models import TreePlantingEvent, TreePlantingDetail, TreePlantingEventImage

from django.core.exceptions import ValidationError

class TreePlantingEventForm(forms.ModelForm):
    class Meta:
        model = TreePlantingEvent
        fields = [
            'name', 'organizer', 'plot', 'location',
            'date_planted', 'number_of_trees_planted', 'notes'
        ]
        widgets = {
            'date_planted': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

from django import forms
from django.core.exceptions import ValidationError
from ind_trees.models import TreePlantingDetail

class TreePlantingDetailForm(forms.ModelForm):
    class Meta:
        model = TreePlantingDetail
        fields = ['tree', 'quantity_planted', 'latitude', 'longitude']
        widgets = {
            'tree': forms.Select(attrs={'class': 'select2'}),
            'quantity_planted': forms.NumberInput(attrs={
                'min': 1,
                'placeholder': 'Enter quantity'
            }),
            'latitude': forms.NumberInput(attrs={
                'step': 0.000001,
                'placeholder': 'Enter latitude',
            }),
            'longitude': forms.NumberInput(attrs={
                'step': 0.000001,
                'placeholder': 'Enter longitude',
            }),
        }

    def clean_quantity_planted(self):
        quantity = self.cleaned_data.get('quantity_planted')
        if quantity is None or quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        return quantity

    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is None:
            raise ValidationError("Latitude is required")
        if lat < -90 or lat > 90:
            raise ValidationError("Latitude must be between -90 and 90")
        return lat

    def clean_longitude(self):
        lon = self.cleaned_data.get('longitude')
        if lon is None:
            raise ValidationError("Longitude is required")
        if lon < -180 or lon > 180:
            raise ValidationError("Longitude must be between -180 and 180")
        return lon

    
TreeFormSet = inlineformset_factory(
    TreePlantingEvent,
    TreePlantingDetail,
    form=TreePlantingDetailForm,
    fields=('tree', 'quantity_planted', 'latitude', 'longitude'),
    extra=1,
    can_delete=True,
    can_delete_extra=True,
    min_num=1,
    validate_min=True,
    max_num=1000  # Set a high but reasonable limit
)

class TreePlantingEventImageForm(forms.ModelForm):
    class Meta:
        model = TreePlantingEventImage
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Optional caption'}),
        }

ImageFormSet = inlineformset_factory(
    TreePlantingEvent,
    TreePlantingEventImage,
    form=TreePlantingEventImageForm,
    fields=('image', 'caption'),
    extra=1,
    can_delete=True,
    can_delete_extra=True
)
##mon
# forms.py
from django import forms
from ind_trees.models import MonitoringSchedule

class MonitoringScheduleForm(forms.ModelForm):
    class Meta:
        model = MonitoringSchedule
        fields = '__all__'
        widgets = {
            'next_due': forms.DateInput(attrs={'type': 'date'}),
            'plot': forms.Select(attrs={'class': 'select2'}),
        }

## mon trees
# forms.py
from django import forms
from django.forms import inlineformset_factory
from ind_trees.models import (
    TreeMonitoringRecord,
    MonitoredTreeDetail,
    TreeMonitoringPhoto,
    TreePlantingDetail,
    TreePlantingEvent,
    Plot,
)

class EventChoiceForm(forms.Form):
    planting_event = forms.ModelChoiceField(
        queryset=TreePlantingEvent.objects.order_by('-date_planted'),
        label="Select Planting Event",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
class TreeMonitoringRecordForm(forms.ModelForm):
    class Meta:
        model = TreeMonitoringRecord
        fields = [
            'plot',
            'planting_event',
            'trees',
            'monitored_by',
            'alive_count',
            'dead_count',
            'health_status',
            'threats_observed',
            'conservation_actions',
            'notes',
            'intervention',
            'monitoring_schedule',
        ]
        widgets = {
            'plot': forms.Select(attrs={'class': 'form-control'}),
            'planting_event': forms.Select(attrs={'class': 'form-control'}),
            'trees': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'monitored_by': forms.TextInput(attrs={'class': 'form-control'}),
            'health_status': forms.TextInput(attrs={'class': 'form-control'}),
            'alive_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'dead_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conservation_actions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'threats_observed': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'intervention': forms.Select(attrs={'class': 'form-control'}),
            'monitoring_schedule': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, event_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter trees only if event ID is provided
        if event_id:
            planted_trees_qs = TreePlantingDetail.objects.filter(event_id=event_id).values_list('tree_id', flat=True)
            self.fields['trees'].queryset = self.fields['trees'].queryset.filter(id__in=planted_trees_qs)
            self.fields['trees'].initial = planted_trees_qs

MonitoredTreeDetailFormSet = inlineformset_factory(
    TreeMonitoringRecord,
    MonitoredTreeDetail,
    fields=['tree', 'alive_count', 'dead_count', 'notes'],
    extra=0,
    can_delete=False
)

TreeMonitoringPhotoFormSet = inlineformset_factory(
    TreeMonitoringRecord,
    TreeMonitoringPhoto,
    fields=['image', 'caption'],
    extra=6,
    can_delete=True
)


from django import forms
from ind_trees.models import Plot, PlotImage, EnvironmentalData

class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = '__all__'

class PlotImageForm(forms.ModelForm):
    class Meta:
        model = PlotImage
        fields = ['image', 'caption']

class EnvironmentalDataForm(forms.ModelForm):
    class Meta:
        model = EnvironmentalData
        fields = '__all__'

# forms.py
from django import forms
from ind_trees.models import PlotMonitoringRecord, PlotMonitoringPhoto

class PlotMonitoringRecordForm(forms.ModelForm):
    class Meta:
        model = PlotMonitoringRecord
        fields = [
            'plot',
            'monitored_by',
            'monitoring_schedule',
            'vegetation_cover',
            'invasive_species_present',
            'invasive_species_details',
            'signs_of_deforestation',
            'signs_of_fire',
            'illegal_activities_observed',
            'wildlife_presence',
            'soil_erosion_signs',
            'erosion_notes',
            'water_conditions',
            'human_activity_notes',
            'threats_identified',
            'recommended_actions',
            'intervention',
            'water_quality',
            'air_quality',
            'weather_conditions',
            'notes',
            'next_monitoring_due',
        ]
        widgets = {
            'next_monitoring_due': forms.DateInput(attrs={'type': 'date'}),
            'vegetation_cover': forms.Textarea(attrs={'rows': 2}),
            'illegal_activities_observed': forms.Textarea(attrs={'rows': 2}),
            'wildlife_presence': forms.Textarea(attrs={'rows': 2}),
            'recommended_actions': forms.Textarea(attrs={'rows': 2}),
            'threats_identified': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PlotMonitoringPhotoForm(forms.ModelForm):
    class Meta:
        model = PlotMonitoringPhoto
        fields = ['image', 'caption']

# Inline formset for multiple photos
PlotMonitoringPhotoFormSet = inlineformset_factory(
    PlotMonitoringRecord,
    PlotMonitoringPhoto,
    form=PlotMonitoringPhotoForm,
    extra=3,  # default number of photo fields shown
    can_delete=True
)