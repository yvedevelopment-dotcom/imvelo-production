from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from ind_trees.models import Tree, PlotImage
from django.db.models import Q

class Dashboard(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard.html')


class TreeListView(ListView):
    model = Tree
    template_name = 'trees.html'
    context_object_name = 'trees'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Tree.objects.filter(
                Q(name__icontains=query) |
                Q(tree_description__icontains=query) |
                Q(categories__name__icontains=query)
            ).distinct().order_by('-created_at')
        return Tree.objects.all().order_by('-created_at')


class TreeDetailView(DetailView):
    model = Tree
    template_name = 'tree_detail-m.html'
    context_object_name = 'tree'

    def get_context_data(self, **kwargs):
        # Get the default context data for the tree detail view
        context = super().get_context_data(**kwargs)
        
        # Add related images (for different categories like medical, cultural, etc.)
        tree = self.get_object()
        context['tree_images'] = tree.images.all()
        context['medical_images'] = tree.medical_benefit_images.all()
        context['cultural_images'] = tree.cultural_significance_images.all()
        context['threats_images'] = tree.threats_conservation_images.all()
        
        # Add heritage site images
        heritage_site_images = []
        for heritage_site in tree.heritage_sites.all():
            heritage_site_images.append({
                'heritage_site': heritage_site,
                'images': heritage_site.heritage_site_images.all()
            })
        context['heritage_site_images'] = heritage_site_images
        
        return context

    
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from ind_trees.models import Tree, TreeImage, MedicalBenefitImage, CulturalSignificanceImage, ThreatsConservationImage
from .forms import TreeForm


from django.shortcuts import render, redirect
from django.views import View
from ind_trees.models import Tree
from .forms import (
    TreeForm, SpeciesForm, PlotForm, CategoryForm, HeritageSiteForm, ConservationStatusForm,
    TreeImageFormSet, MedicalImageFormSet, CulturalImageFormSet, ThreatsImageFormSet
)

class TreeCreateView(View):
    template_name = 'tree_create.html'

    def get(self, request):
        context = {
            'form': TreeForm(),
            'species_form': SpeciesForm(),
            'plot_form': PlotForm(),
            'category_form': CategoryForm(),
            'heritage_form': HeritageSiteForm(),
            'status_form': ConservationStatusForm(),
            'tree_images': TreeImageFormSet(prefix='tree'),
            'medical_images': MedicalImageFormSet(prefix='medical'),
            'cultural_images': CulturalImageFormSet(prefix='cultural'),
            'threats_images': ThreatsImageFormSet(prefix='threats'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = TreeForm(request.POST, request.FILES)
        species_form = SpeciesForm(request.POST, prefix='species')
        plot_form = PlotForm(request.POST, prefix='plot')
        category_form = CategoryForm(request.POST, prefix='category')
        heritage_form = HeritageSiteForm(request.POST, prefix='heritage')
        status_form = ConservationStatusForm(request.POST, prefix='status')

        ti = TreeImageFormSet(request.POST, request.FILES, prefix='tree')
        mi = MedicalImageFormSet(request.POST, request.FILES, prefix='medical')
        ci = CulturalImageFormSet(request.POST, request.FILES, prefix='cultural')
        thi = ThreatsImageFormSet(request.POST, request.FILES, prefix='threats')

        if form.is_valid() and ti.is_valid() and mi.is_valid() and ci.is_valid() and thi.is_valid():
            tree = form.save(commit=False)

            if species_form.is_valid() and any(species_form.cleaned_data.values()):
                tree.species = species_form.save()
            else:
                tree.species = form.cleaned_data['species']

            if plot_form.is_valid() and any(plot_form.cleaned_data.values()):
                tree.plot = plot_form.save()
            else:
                tree.plot = form.cleaned_data['plot']

            if status_form.is_valid() and any(status_form.cleaned_data.values()):
                tree.conservation_status = status_form.save()
            else:
                tree.conservation_status = form.cleaned_data['conservation_status']

            tree.save()

            if category_form.is_valid() and any(category_form.cleaned_data.values()):
                new_category = category_form.save()
                tree.categories.add(new_category)
            else:
                for cat in form.cleaned_data['categories']:
                    tree.categories.add(cat)

            if heritage_form.is_valid() and any(heritage_form.cleaned_data.values()):
                new_heritage = heritage_form.save()
                tree.heritage_sites.add(new_heritage)
            else:
                for hs in form.cleaned_data['heritage_sites']:
                    tree.heritage_sites.add(hs)

            for fs in [ti, mi, ci, thi]:
                fs.instance = tree
                fs.save()

            return redirect('tree_list')

        return render(request, self.template_name, {
            'form': form,
            'species_form': species_form,
            'plot_form': plot_form,
            'category_form': category_form,
            'heritage_form': heritage_form,
            'status_form': status_form,
            'tree_images': ti,
            'medical_images': mi,
            'cultural_images': ci,
            'threats_images': thi,
        })



# views.py
from django.views.generic import CreateView
from django.urls import reverse,reverse_lazy
from ind_trees.models import Species, Plot, Category, HeritageSite, ConservationStatus, EnvironmentalData
from .forms import SpeciesForm, CategoryForm, HeritageSiteForm, ConservationStatusForm, LandDataForm

class SpeciesCreateView(CreateView):
    model = Species
    form_class = SpeciesForm
    template_name = 'tree/species_form.html'
    success_url = reverse_lazy('tree_create')  # Redirect back to tree form


class PlotCreateView(CreateView):
    model = Plot
    form_class = PlotForm
    template_name = 'tree/plot_form.html'
    success_url = reverse_lazy('tree_create')

    def get_initial(self):
        initial = super().get_initial()
        selected_land_id = self.request.GET.get('selected_land_id')
        if selected_land_id:
            try:
                initial['land_data'] = EnvironmentalData.objects.get(id=selected_land_id)
            except EnvironmentalData.DoesNotExist:
                pass
        return initial


class LandDataCreateView(CreateView):
    model = EnvironmentalData
    form_class = LandDataForm
    template_name = 'tree/land_form.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return f"{next_url}?selected_land_id={self.object.id}"
        return reverse('plot_create')


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'tree/category_form.html'
    success_url = reverse_lazy('tree_create')


class HeritageSiteCreateView(CreateView):
    model = HeritageSite
    form_class = HeritageSiteForm
    template_name = 'tree/heritage_form.html'
    success_url = reverse_lazy('tree_create')


class ConservationStatusCreateView(CreateView):
    model = ConservationStatus
    form_class = ConservationStatusForm
    template_name = 'tree/conservation_form.html'
    success_url = reverse_lazy('tree_create')

##event nav

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from ind_trees.models import TreePlantingEvent

class TreePlantingEventListView(ListView):
    model = TreePlantingEvent
    template_name = 'events/treeplantingevent_list.html'
    context_object_name = 'events'
    ordering = ['-date_planted']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(organizer__icontains=query) |
                Q(location__icontains=query)
            )
        return queryset


class TreePlantingEventDetailView(DetailView):
    model = TreePlantingEvent
    template_name = 'events/treeplantingevent_detail.html'
    context_object_name = 'event'

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from ind_trees.models import TreePlantingEvent

from django.shortcuts import render, redirect
from django.views import View
from .forms import TreePlantingEventForm, TreeFormSet, ImageFormSet
from django.views.generic import CreateView
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib import messages

class TreePlantingEventCreateView(CreateView):
    model = TreePlantingEvent
    form_class = TreePlantingEventForm
    template_name = 'events/treeplantingevent_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['trees'] = TreeFormSet(self.request.POST, prefix='trees')
            context['images'] = ImageFormSet(self.request.POST, self.request.FILES, prefix='images')
        else:
            context['trees'] = TreeFormSet(prefix='trees')
            context['images'] = ImageFormSet(prefix='images')
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        trees = context['trees']
        images = context['images']

        if trees.is_valid() and images.is_valid():
            self.object = form.save()

            # Save TreePlantingDetail forms (with coordinates)
            tree_details = trees.save(commit=False)

            # Check total quantity excluding deleted forms
            total_planted = sum(
                detail.cleaned_data['quantity_planted']
                for detail in trees.forms
                if detail not in trees.deleted_forms and detail.cleaned_data
            )

            if total_planted != self.object.number_of_trees_planted:
                form.add_error(
                    'number_of_trees_planted',
                    f"Total trees planted ({total_planted}) doesn't match the sum of individual species quantities"
                )
                return self.form_invalid(form)

            # Save tree details with event assignment
            for detail in tree_details:
                detail.event = self.object
                detail.save()

            # Delete removed tree forms if any
            for form_deleted in trees.deleted_forms:
                if form_deleted.instance.pk:
                    form_deleted.instance.delete()

            # Save images
            images.instance = self.object
            images.save()

            messages.success(self.request, 'Tree planting event created successfully!')
            return redirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(form=form))


    def get_success_url(self):
        return reverse('treeplantingevent_list-m')


class TreePlantingEventUpdateView(UpdateView):
    model = TreePlantingEvent
    form_class = TreePlantingEventForm
    template_name = 'events/treeplantingevent_form.html'
    success_url = reverse_lazy('treeplantingevent_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['images'] = TreePlantingEventImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['images'] = TreePlantingEventImageFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        images = context['images']
        self.object = form.save()
        if images.is_valid():
            images.instance = self.object
            images.save()
        return super().form_valid(form)



#mon
# views.py
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from ind_trees.models import MonitoringSchedule
from .forms import MonitoringScheduleForm
from django.db.models import Q

class MonitoringScheduleListView(ListView):
    model = MonitoringSchedule
    template_name = 'monitoring_schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = super().get_queryset().select_related('plot')
        if query:
            qs = qs.filter(
                Q(plot__name__icontains=query) |
                Q(assigned_to__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class MonitoringScheduleCreateView(CreateView):
    model = MonitoringSchedule
    form_class = MonitoringScheduleForm
    template_name = 'monitoring_schedule_form.html'
    success_url = reverse_lazy('monitoring_schedule_list-m')


from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from ind_trees.models import Tree, TreeMonitoringRecord
from django.views.generic import ListView
from django.db.models import Q

class MonitoredTreeListView(ListView):
    model = Tree
    template_name = 'monitoring/monitored_tree_list.html'
    context_object_name = 'trees'
    paginate_by = 20  # Optional: paginate results

    def get_queryset(self):
        queryset = Tree.objects.filter(monitoring_records__isnull=False).distinct()
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class TreeMonitoringDetailView(DetailView):
    model = Tree
    template_name = 'monitoring/tree_monitoring_detail.html'
    context_object_name = 'tree'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['monitoring_records'] = TreeMonitoringRecord.objects.filter(trees=self.object).prefetch_related('photos', 'trees')
        return context

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from .forms import (
    EventChoiceForm,
    TreeMonitoringRecordForm,
    MonitoredTreeDetailFormSet,
    TreeMonitoringPhotoFormSet
)
from ind_trees.models import TreeMonitoringRecord, TreePlantingDetail, MonitoredTreeDetail
from django.forms import inlineformset_factory


class TreeMonitoringWizard(View):
    template_name_event = 'monitoring/select_event.html'
    success_url = reverse_lazy('monitoring_fill')

    def get(self, request, *args, **kwargs):
        if 'event_id' in request.session:
            return redirect('monitoring_fill')
        return render(request, self.template_name_event, {'form': EventChoiceForm()})

    def post(self, request, *args, **kwargs):
        form = EventChoiceForm(request.POST)
        if form.is_valid():
            request.session['event_id'] = form.cleaned_data['planting_event'].id
            return redirect('monitoring_fill')
     

def clear_event_session_and_redirect(request):
    request.session.pop('event_id', None)  # Safely remove 'event_id' if it exists
    return redirect('monitoring_wizard')  # Send them back to the selection page

class TreeMonitoringRecordCreate(View):
    template_name = 'monitoring/monitor_record.html'
    success_url = reverse_lazy('monitored_tree_list-d')

    def get(self, request, *args, **kwargs):
        event_id = request.session.get('event_id')
        if not event_id:
            return redirect('monitoring_wizard')

        event_detail_qs = TreePlantingDetail.objects.filter(event_id=event_id)
        if not event_detail_qs.exists():
            return redirect('monitoring_wizard')

        event = event_detail_qs.first().event
        plot = getattr(event, 'plot', None)

        # Get tree instances from planting detail
        tree_ids = event_detail_qs.values_list('tree_id', flat=True)

        form = TreeMonitoringRecordForm(
            initial={
                'plot': plot,
                'planting_event': event,
                'trees': tree_ids
            },
            event_id=event_id
        )

        # Provide one MonitoredTreeDetail per tree
        MonitoredTreeDetailFormSetExtra = inlineformset_factory(
            TreeMonitoringRecord,
            MonitoredTreeDetail,
            fields=['tree', 'alive_count', 'dead_count', 'notes'],
            extra=len(tree_ids),
            can_delete=False
        )

        tree_formset = MonitoredTreeDetailFormSetExtra(
            prefix='trees',
            queryset=MonitoredTreeDetail.objects.none()
        )

        for form_i, tree_id in zip(tree_formset.forms, tree_ids):
            form_i.initial['tree'] = tree_id

        photo_formset = TreeMonitoringPhotoFormSet(prefix='photos')

        return render(request, self.template_name, {
            'form': form,
            'tree_formset': tree_formset,
            'photo_formset': photo_formset,
            'event': event
        })

    def post(self, request, *args, **kwargs):
        event_id = request.session.get('event_id')
        if not event_id:
            return redirect('monitoring_wizard')

        event_detail_qs = TreePlantingDetail.objects.filter(event_id=event_id)
        if not event_detail_qs.exists():
            return redirect('monitoring_wizard')

        event = event_detail_qs.first().event

        form = TreeMonitoringRecordForm(request.POST, event_id=event_id)
        tree_formset = MonitoredTreeDetailFormSet(request.POST, prefix='trees')
        photo_formset = TreeMonitoringPhotoFormSet(request.POST, request.FILES, prefix='photos')

        if form.is_valid() and tree_formset.is_valid() and photo_formset.is_valid():
            record = form.save(commit=False)
            record.planting_event = event
            record.save()
            form.save_m2m()

            tree_formset.instance = record
            tree_formset.save()

            photo_formset.instance = record
            photo_formset.save()

            del request.session['event_id']
            return redirect(self.success_url)

        return render(request, self.template_name, {
            'form': form,
            'tree_formset': tree_formset,
            'photo_formset': photo_formset,
            'event': event
        })



from django.views.generic import ListView
from django.db.models import Count, Q
from ind_trees.models import TreePlantingEvent, TreeMonitoringRecord

class MonitoredEventListView(ListView):
    model = TreePlantingEvent
    template_name = 'monitoring/monitored_event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = TreePlantingEvent.objects.annotate(
            monitoring_count=Count('treemonitoringrecord')
        ).filter(monitoring_count__gt=0)

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(plot__name__icontains=query) |
                Q(treemonitoringrecord__trees__name__icontains=query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

# views.py continued
from django.shortcuts import get_object_or_404
from ind_trees.models import TreeMonitoringRecord

class EventMonitoringDetailView(DetailView):
    model = TreePlantingEvent
    template_name = 'monitoring/event_monitoring_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object

        monitoring_records = TreeMonitoringRecord.objects.filter(
            planting_event=event
        ).prefetch_related(
            'trees',
            'monitored_trees__tree',
            'photos'
        ).order_by('-monitored_at')

        context['monitoring_records'] = monitoring_records
        return context


####
# views.py
class LandMenu(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'land_menu.html')

from django.views.generic import ListView, DetailView
from django.db.models import Q
from ind_trees.models import Plot

class PlotListView(ListView):
    model = Plot
    template_name = 'land/plot_list.html'
    context_object_name = 'plots'

    def get_queryset(self):
        queryset = Plot.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(location__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

import json

class PlotDetailView(DetailView):
    model = Plot
    template_name = 'land/plot_detail.html'
    context_object_name = 'plot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plot = context['plot']

        if plot.boundary_coordinates:
            # Flip from [lat, lon] to [lon, lat] for GeoJSON compliance
            formatted_coords = [[lon, lat] for lat, lon in plot.boundary_coordinates]
            context['boundary_coords'] = json.dumps(formatted_coords)
        else:
            context['boundary_coords'] = None

        return context


class LandCreateView(CreateView):
    model = Plot
    form_class = PlotForm
    template_name = 'land/land_form.html'
    success_url = reverse_lazy('plot_list-m')

    def get_initial(self):
        initial = super().get_initial()
        selected_land_id = self.request.GET.get('selected_land_id')
        if selected_land_id:
            try:
                initial['land_data'] = EnvironmentalData.objects.get(id=selected_land_id)
            except EnvironmentalData.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        images = self.request.FILES.getlist('images')
        for image in images:
            PlotImage.objects.create(plot=self.object, image=image)
        return response


class DataCreateView(CreateView):
    model = EnvironmentalData
    form_class = LandDataForm
    template_name = 'land/env_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        plot_id = self.request.GET.get('plot_id')
        if plot_id:
            try:
                plot = Plot.objects.get(id=plot_id)
                self.object.plot = plot
                self.object.save()
                # Set this environmental data as plot.land_data
                plot.land_data = self.object
                plot.save()
            except Plot.DoesNotExist:
                pass
        return response

    def get_success_url(self):
        plot_id = self.request.GET.get('plot_id')
        if plot_id:
            return reverse('plot_detail-m', kwargs={'pk': plot_id})
        return reverse('plot_list-m')


from django.views.generic import ListView
from ind_trees.models import PlotMonitoringRecord
from django.db.models import Q

class PlotMonitoringRecordListView(ListView):
    model = PlotMonitoringRecord
    template_name = 'monitoring/monitoring_land_list.html'
    context_object_name = 'records'
    paginate_by = 10

    def get_queryset(self):
        qs = PlotMonitoringRecord.objects.prefetch_related('photos', 'plot')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(plot__name__icontains=q))
        return qs

from django.views.generic import DetailView
from ind_trees.models import PlotMonitoringRecord

class PlotMonitoringRecordDetailView(DetailView):
    model = PlotMonitoringRecord
    template_name = 'monitoring/monitoring_plot_detail.html'
    context_object_name = 'record'

from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import redirect, render
from ind_trees.models import PlotMonitoringRecord
from .forms import PlotMonitoringRecordForm, PlotMonitoringPhotoFormSet

class PlotMonitoringRecordCreateView(CreateView):
    model = PlotMonitoringRecord
    form_class = PlotMonitoringRecordForm
    template_name = 'monitoring/monitoring_form.html'
    success_url = reverse_lazy('monitoring_record_list-m')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['photo_formset'] = PlotMonitoringPhotoFormSet(self.request.POST, self.request.FILES)
        else:
            context['photo_formset'] = PlotMonitoringPhotoFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        form.instance.monitored_by = form.cleaned_data.get('monitored_by', 'Unknown')
        self.object = form.save()
        if photo_formset.is_valid():
            photo_formset.instance = self.object
            photo_formset.save()
        return super().form_valid(form)

from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from .forms import PlotMonitoringRecordForm, PlotMonitoringPhotoFormSet
from ind_trees.models import PlotMonitoringRecord, TreePlantingEvent
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from .forms import PlotMonitoringRecordForm, PlotMonitoringPhotoFormSet
from ind_trees.models import TreePlantingEvent

from django.shortcuts import render, redirect
from django.views import View
from .forms import PlotMonitoringRecordForm, PlotMonitoringPhotoFormSet
import datetime

class PlotMonitoringWizard(View):
    template_name = 'monitoring/monitoring_wizard.html'

    def get(self, request, *args, **kwargs):
        """Display initial monitoring record and photos form."""
        form = PlotMonitoringRecordForm()
        photo_formset = PlotMonitoringPhotoFormSet()
        return render(request, self.template_name, {
            'form': form,
            'photo_formset': photo_formset
        })

    def post(self, request, *args, **kwargs):
        """Process and store form data temporarily in session."""
        form = PlotMonitoringRecordForm(request.POST, request.FILES)
        photo_formset = PlotMonitoringPhotoFormSet(request.POST, request.FILES)

        if form.is_valid() and photo_formset.is_valid():
            # Get cleaned form data
            plot_record_data = form.cleaned_data.copy()

            # Convert ForeignKeys to IDs
            fk_fields = ['plot', 'monitoring_schedule', 'intervention']
            for field in fk_fields:
                obj = plot_record_data.get(field)
                if obj:
                    plot_record_data[f"{field}_id"] = obj.id
                    del plot_record_data[field]

            # Convert date/datetime fields to strings
            for key, value in list(plot_record_data.items()):
                if isinstance(value, (datetime.date, datetime.datetime)):
                    plot_record_data[key] = value.isoformat()

            # Save cleaned, serializable data to session
            request.session['plot_record_data'] = plot_record_data

            # Save photo info (only serializable pieces)
            photo_data = []
            for photo_form in photo_formset.forms:
                if photo_form.cleaned_data.get('image'):
                    photo_data.append({
                        'image_name': photo_form.cleaned_data['image'].name,
                        'caption': photo_form.cleaned_data.get('caption', '')
                    })
            request.session['plot_photo_data'] = photo_data

            # Redirect to next step
            plot_id = plot_record_data.get('plot_id')
            if plot_id:
                return redirect('monitoring_event_select_plot', plot_id=plot_id)
            else:
                form.add_error('plot', 'Please select a plot before continuing.')

        # If invalid, render the same form with errors
        return render(request, self.template_name, {
            'form': form,
            'photo_formset': photo_formset
        })

    
    # Debugging info
        print("Form errors:", form.errors)
        print("Formset errors:", photo_formset.errors)

        return render(request, self.template_name, {'form': form, 'photo_formset': photo_formset})

class PlotEventSelectPlot(View):
    template_name = 'monitoring/select_event_plot.html'

    def get(self, request, plot_id, *args, **kwargs):
        events = TreePlantingEvent.objects.filter(plot_id=plot_id)
        return render(request, self.template_name, {'events': events, 'plot_id': plot_id})

    def post(self, request, plot_id, *args, **kwargs):
        selected_event = request.POST.get('event_id')
        if selected_event:
            request.session['event_id'] = selected_event
            return redirect('monitoring_fill')  # go to tree monitoring
        else:
            # Skip tree monitoring
            return redirect('monitoring_finalize')


class TreeMonitoringRecordPlotCreate(View):
    template_name = 'monitoring/monitor_record_plot.html'
    success_url = reverse_lazy('monitored_tree_list-d')

    def get(self, request, *args, **kwargs):
        event_id = request.session.get('event_id')
        if not event_id:
            return redirect('monitoring_wizard')

        event_detail_qs = TreePlantingDetail.objects.filter(event_id=event_id)
        if not event_detail_qs.exists():
            return redirect('monitoring_wizard')

        event = event_detail_qs.first().event
        plot = getattr(event, 'plot', None)

        # Get tree instances from planting detail
        tree_ids = event_detail_qs.values_list('tree_id', flat=True)

        form = TreeMonitoringRecordForm(
            initial={
                'plot': plot,
                'planting_event': event,
                'trees': tree_ids
            },
            event_id=event_id
        )

        # Provide one MonitoredTreeDetail per tree
        MonitoredTreeDetailFormSetExtra = inlineformset_factory(
            TreeMonitoringRecord,
            MonitoredTreeDetail,
            fields=['tree', 'alive_count', 'dead_count', 'notes'],
            extra=len(tree_ids),
            can_delete=False
        )

        tree_formset = MonitoredTreeDetailFormSetExtra(
            prefix='trees',
            queryset=MonitoredTreeDetail.objects.none()
        )

        for form_i, tree_id in zip(tree_formset.forms, tree_ids):
            form_i.initial['tree'] = tree_id

        photo_formset = TreeMonitoringPhotoFormSet(prefix='photos')

        return render(request, self.template_name, {
            'form': form,
            'tree_formset': tree_formset,
            'photo_formset': photo_formset,
            'event': event
        })

    def post(self, request, *args, **kwargs):
        event_id = request.session.get('event_id')
        if not event_id:
            return redirect('monitoring_wizard')

        event_detail_qs = TreePlantingDetail.objects.filter(event_id=event_id)
        if not event_detail_qs.exists():
            return redirect('monitoring_wizard')

        event = event_detail_qs.first().event

        form = TreeMonitoringRecordForm(request.POST, event_id=event_id)
        tree_formset = MonitoredTreeDetailFormSet(request.POST, prefix='trees')
        photo_formset = TreeMonitoringPhotoFormSet(request.POST, request.FILES, prefix='photos')

        if form.is_valid() and tree_formset.is_valid() and photo_formset.is_valid():
            record = form.save(commit=False)
            record.planting_event = event
            record.save()
            form.save_m2m()

            tree_formset.instance = record
            tree_formset.save()

            photo_formset.instance = record
            photo_formset.save()

            del request.session['event_id']
            return redirect(self.success_url)

        return render(request, self.template_name, {
            'form': form,
            'tree_formset': tree_formset,
            'photo_formset': photo_formset,
            'event': event
        })

class FinalizePlotRecord(View):
    success_url = reverse_lazy('monitoring-list')

    def get(self, request, *args, **kwargs):
        plot_record_data = request.session.get('plot_record_data')
        if not plot_record_data:
            return redirect('monitoring_wizard')

        form = PlotMonitoringRecordForm(plot_record_data)
        if form.is_valid():
            record = form.save()
            # Clear session cache
            del request.session['plot_record_data']
            return redirect(self.success_url)
        return redirect('monitoring_wizard')



###################################################################################report

class ReportPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'report/reportpage.html')

class ReportTreeListView(ListView):
    model = Tree
    template_name = 'report/report_tree_list.html'
    context_object_name = 'trees'
    paginate_by = 20  

    def get_queryset(self):
        queryset = Tree.objects.filter(monitoring_records__isnull=False).distinct()
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class TreeCachedReportView(DetailView):
    model = Tree
    template_name = "report/tree_cached_report.html"   # or reuse tree_stats.html
    context_object_name = "tree"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tree = self.object
        cached = get_object_or_404(TreeReportCache, tree=tree)

        # Rebuild the context the same way the full report template expects
        # We can simply pass the cached data
        context.update({
            "cached_html": cached.html_report,
            "ai_cleaned_lines": cached.ai_summary.splitlines(),
            "from_cache": True,
            # Add any additional fields your template needs (e.g., survival trend)
            "survival_trend_dates": cached.survival_trend_dates,
            "survival_trend_alive": cached.survival_trend_alive,
            "survival_trend_dead": cached.survival_trend_dead,
            # The template may also need other context like tree, etc.
        })
        return context

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from .models import TreeReportCache
from ind_trees.models import Tree
class TreeReportsListView(DetailView):
    model = Tree
    template_name = "report/tree_reports_list.html"
    context_object_name = "tree"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tree = self.object

        # Latest cached report (quick access, optional)
        try:
            cached = TreeReportCache.objects.get(tree=tree)
            context["cached_report"] = cached
        except TreeReportCache.DoesNotExist:
            context["cached_report"] = None

        # All historical reports (newest first)
        context["reports"] = tree.report_history.all()   # uses related_name='report_history'

        return context
# views.py
from django.views.generic import DetailView
from ind_trees.models import (
    Tree, TreeMonitoringRecord, MonitoredTreeDetail, TreePlantingDetail
)

class TreeMonitoringReportView(DetailView):
    model = Tree
    template_name = 'report/tree_monitoring_report.html'
    context_object_name = 'tree'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tree = self.get_object()

        # 1. Planting Details (all planting events for this tree)
        planting_details = TreePlantingDetail.objects.filter(tree=tree).select_related('event', 'event__plot')
        first_planting = planting_details.first()

        # 2. All Monitoring Records (for this tree)
        monitoring_records = tree.monitoring_records.select_related('planting_event', 'plot').order_by('monitored_at')
        total_monitorings = monitoring_records.count()
        first_monitoring = monitoring_records.first()
        latest_monitoring = monitoring_records.last()

        # 3. Monitoring Frequency (average interval)
        frequency_days = None
        if total_monitorings >= 2:
            duration = (latest_monitoring.monitored_at - first_monitoring.monitored_at).days
            frequency_days = duration // (total_monitorings - 1)

        # 4. Sum of alive/dead counts from last monitoring per planting event
        total_alive = 0
        total_dead = 0

        for planting_detail in planting_details:
            planting_event = planting_detail.event

            # Get the latest monitoring record for this event that includes this tree
            latest_event_monitoring = TreeMonitoringRecord.objects.filter(
                planting_event=planting_event,
                trees=tree
            ).order_by('-monitored_at').first()

            if latest_event_monitoring:
                # Fetch the corresponding MonitoredTreeDetail for this record and tree
                detail = MonitoredTreeDetail.objects.filter(
                    monitoring_record=latest_event_monitoring,
                    tree=tree
                ).first()

                if detail:
                    total_alive += detail.alive_count
                    total_dead += detail.dead_count

        context.update({
            "planting_details": planting_details,
            "first_planting": first_planting,
            "monitoring_records": monitoring_records,
            "total_monitorings": total_monitorings,
            "first_monitoring": first_monitoring,
            "latest_monitoring": latest_monitoring,
            "frequency_days": frequency_days,
            "total_alive": total_alive,
            "total_dead": total_dead
        })
        return context


from django.views.generic import DetailView
from django.db.models import Sum, Count
from collections import Counter
from ind_trees.models import Tree, TreeMonitoringRecord

class TreeStatsView(DetailView):
    model = Tree
    template_name = "report/tree_stats.html"
    context_object_name = "tree"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tree = self.object

        # Get all monitoring records for this tree
        records = TreeMonitoringRecord.objects.filter(trees=tree).order_by('monitored_at')

        # Initialize aggregates
        survival_trend = []  # list of dict {date, alive, dead}
        health_status_counter = Counter()
        threats_list = []
        conservation_actions_list = []
        total_alive = 0
        total_dead = 0

        for record in records:
            survival_trend.append({
                'date': record.monitored_at.date(),
                'alive': record.alive_count,
                'dead': record.dead_count,
            })
            total_alive += record.alive_count
            total_dead += record.dead_count

            # Count health statuses
            health_status_counter[record.health_status] += 1

            # Collect threats and actions (could be further processed)
            if record.threats_observed:
                threats_list.append(record.threats_observed)
            if record.conservation_actions:
                conservation_actions_list.append(record.conservation_actions)

        # Simple frequency counts of threats and conservation actions (could tokenize text)
        # For demo, just count total records with non-empty threats/actions
        threats_count = len(threats_list)
        actions_count = len(conservation_actions_list)

        # Add to context
        context.update({
            "survival_trend": survival_trend,
            "health_status_counts": dict(health_status_counter),
            "threats_count": threats_count,
            "conservation_actions_count": actions_count,
            "total_alive": total_alive,
            "total_dead": total_dead,
            "monitoring_records": records,
        })
        return context


##mix
from django.views.generic import DetailView
from django.utils.html import format_html
from django.template.loader import render_to_string
from django.db.models import Max
from collections import defaultdict, Counter
from django.utils.timezone import now
from .models import TreeReportCache
from ind_trees.models import (
    Tree, TreeMonitoringRecord, MonitoredTreeDetail, TreePlantingDetail,
    TreePlantingEvent, TreeMonitoringPhoto
)
from .ai_utils import get_tree_ai_insights, get_region_from_coordinates
import re
from django.views.generic import DetailView
from django.db.models import Max
from collections import defaultdict, Counter
from django.template.loader import render_to_string
from ind_trees.models import (
    Tree, TreeMonitoringRecord, MonitoredTreeDetail, TreePlantingDetail,
    TreePlantingEvent, TreeMonitoringPhoto
)
from .models import TreeReportCache, TreeReportHistory   # <-- IMPORT the new history model
from .ai_utils import get_tree_ai_insights, get_region_from_coordinates
import re
from django.views.generic import DetailView
from django.db.models import Max
from collections import defaultdict, Counter
from django.template.loader import render_to_string
from ind_trees.models import (
    Tree, TreeMonitoringRecord, MonitoredTreeDetail, TreePlantingDetail,
    TreePlantingEvent, TreeMonitoringPhoto
)
from .models import TreeReportCache, TreeReportHistory   # ensure this import exists
from .ai_utils import get_tree_ai_insights, get_region_from_coordinates
import re

class TreeFullReportView(DetailView):
    model = Tree
    template_name = "report/tree_stats.html"
    context_object_name = "tree"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tree = self.object

        # Check if user explicitly requested a new generation
        force_generate = self.request.GET.get('force') == 'true'

        # Latest monitoring date
        latest_monitoring_date = tree.monitoring_records.aggregate(latest=Max("monitored_at"))["latest"]

        # Cached report (fast lookup)
        cache = getattr(tree, "cached_report", None)

        # Serve from cache only if NOT forcing and the monitoring data hasn't changed
        if not force_generate and cache and cache.last_monitoring_at == latest_monitoring_date:
            context.update({
                "cached_html": cache.html_report,
                "ai_cleaned_lines": cache.ai_summary.splitlines(),
                "from_cache": True,
            })
            return context

        # ========== FULL REPORT GENERATION ==========

        # 1. Planting Details
        planting_details = TreePlantingDetail.objects.filter(tree=tree).select_related('event', 'event__plot')
        first_planting = planting_details.first()
        planting_events = [pd.event for pd in planting_details]
        planted_plots = list({pd.event.plot for pd in planting_details if pd.event.plot})

        # 2. Monitoring Records
        monitoring_records = tree.monitoring_records.select_related('planting_event').order_by('monitored_at')
        total_monitorings = monitoring_records.count()
        first_monitoring = monitoring_records.first()
        latest_monitoring = monitoring_records.last()

        # 3. Monitoring Frequency
        frequency_days = None
        if total_monitorings >= 2:
            duration = (latest_monitoring.monitored_at - first_monitoring.monitored_at).days
            frequency_days = duration // (total_monitorings - 1)

        # 4. Alive/Dead totals
        total_alive, total_dead = 0, 0
        for pd in planting_details:
            latest_event_monitoring = TreeMonitoringRecord.objects.filter(
                planting_event=pd.event, trees=tree
            ).order_by('-monitored_at').first()
            if latest_event_monitoring:
                detail = MonitoredTreeDetail.objects.filter(
                    monitoring_record=latest_event_monitoring, tree=tree
                ).first()
                if detail:
                    total_alive += detail.alive_count
                    total_dead += detail.dead_count

        # 5. Survival Trend
        survival_data = defaultdict(lambda: {'alive': 0, 'dead': 0})
        for detail in MonitoredTreeDetail.objects.filter(tree=tree).select_related('monitoring_record'):
            record_date = detail.monitoring_record.monitored_at.date().isoformat()
            survival_data[record_date]['alive'] += detail.alive_count
            survival_data[record_date]['dead'] += detail.dead_count
        survival_trend = [{'date': d, 'alive': v['alive'], 'dead': v['dead']} for d, v in sorted(survival_data.items())]

        # 6. Health & Threats
        health_status_counter = Counter()
        threats_count = 0
        conservation_actions_count = 0
        for record in monitoring_records:
            health_status_counter[record.health_status] += 1
            if record.threats_observed:
                threats_count += 1
            if record.conservation_actions:
                conservation_actions_count += 1

        # 7. AI Insights
        species = getattr(tree, 'species', None)
        plot = planting_events[0].plot if planting_events and planting_events[0].plot else None
        region_info = "Unknown"
        environmental_data = None
        plot_area = None
        if plot:
            plot_area = plot.area_hectares
            environmental_data = getattr(plot, 'land_data', None)
            if plot.latitude and plot.longitude:
                region_info = get_region_from_coordinates(float(plot.latitude), float(plot.longitude))

        # Build AI prompt summary
        summary_lines = [f"Tree Name: {tree.name}"]
        if species:
            summary_lines.append(f"Species: {species}")
        if plot:
            summary_lines.append(f"Planted at Plot: {plot.name} (Lat: {plot.latitude}, Lng: {plot.longitude})")
            summary_lines.append(f"Plot Size: {plot_area} hectares")
        summary_lines.append(f"Regional Location: {region_info}")
        if environmental_data:
            summary_lines.append(
                f"Environmental Data: Soil Type: {environmental_data.soil_type}, "
                f"Soil pH: {environmental_data.soil_pH}, Fertility: {environmental_data.fertility_level}, "
                f"Rainfall: {environmental_data.rainfall_mm} mm annually, Temp: {environmental_data.temperature_c} °C"
            )
        summary_lines.append("\nPlanting Events:")
        for event in planting_events:
            summary_lines.append(f"- {event.name} on {event.date_planted}, Organizer: {event.organizer}")
        summary_lines.append("\nMonitoring History:")
        for record in monitoring_records:
            summary_lines.append(
                f"- Date: {record.monitored_at.date()}, Alive: {record.alive_count}, Dead: {record.dead_count}, "
                f"Health: {record.health_status}, Threats: {record.threats_observed or 'None'}, "
                f"Actions: {record.conservation_actions or 'None'}, Notes: {record.notes or 'None'}"
            )

        # === Previous AI report for continuity ===
        previous_cache = TreeReportCache.objects.filter(tree=tree).first()
        if previous_cache and previous_cache.ai_summary:
            summary_lines.append("\n--- Previous AI Analysis (for continuity) ---")
            summary_lines.append(previous_cache.ai_summary)
            summary_lines.append(
                "--- End of Previous Analysis ---\n"
                "Now update the report with the latest data above, "
                "building upon the previous insights while adding new findings. "
                "Maintain a consistent professional tone and structure."
            )

        tree_summary = "\n".join(summary_lines)
        ai_raw = get_tree_ai_insights(tree_summary)

        # Clean AI output
        ai_cleaned_lines = []
        for paragraph in re.split(r"\n\s*\n", ai_raw):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            paragraph = re.sub(r"<.*?>", "", paragraph)
            paragraph = re.sub(r"[*#`]", "", paragraph)
            paragraph = re.sub(r"\s+", " ", paragraph)
            ai_cleaned_lines.append(paragraph)

        # 8. Latest Monitoring Photos
        latest_plot_images = []
        for plot in planted_plots:
            latest_record = TreeMonitoringRecord.objects.filter(plot=plot, trees=tree).order_by('-monitored_at').first()
            if latest_record:
                latest_photo = latest_record.photos.order_by('-id').first()
                if latest_photo:
                    latest_plot_images.append({
                        'plot': plot,
                        'photo': latest_photo,
                        'monitored_at': latest_record.monitored_at
                    })

        # Render HTML report
        html_report = render_to_string("report/_tree_report_body.html", {
            "tree": tree,
            "planting_details": planting_details,
            "first_planting": first_planting,
            "planting_events": planting_events,
            "planted_plots": planted_plots,
            "monitoring_records": monitoring_records,
            "total_monitorings": total_monitorings,
            "first_monitoring": first_monitoring,
            "latest_monitoring": latest_monitoring,
            "frequency_days": frequency_days,
            "total_alive": total_alive,
            "total_dead": total_dead,
            "survival_trend": survival_trend,
            "health_status_counts": dict(health_status_counter),
            "threats_count": threats_count,
            "conservation_actions_count": conservation_actions_count,
            "ai_cleaned_lines": ai_cleaned_lines,
            "ai_region_info": region_info,
            "latest_plot_images": latest_plot_images,
        })

        # ---- SAVE TO CACHE (latest snapshot) ----
        if cache:
            cache.html_report = html_report
            cache.ai_summary = "\n".join(ai_cleaned_lines)
            cache.last_monitoring_at = latest_monitoring_date
            cache.survival_trend_dates = [item['date'] for item in survival_trend]
            cache.survival_trend_alive = [item['alive'] for item in survival_trend]
            cache.survival_trend_dead = [item['dead'] for item in survival_trend]
            cache.save()
        else:
            TreeReportCache.objects.create(
                tree=tree,
                html_report=html_report,
                ai_summary="\n".join(ai_cleaned_lines),
                last_monitoring_at=latest_monitoring_date,
                survival_trend_dates=[item['date'] for item in survival_trend],
                survival_trend_alive=[item['alive'] for item in survival_trend],
                survival_trend_dead=[item['dead'] for item in survival_trend],
            )

        # ---- SAVE TO HISTORY (permanent archive) ----
        TreeReportHistory.objects.create(
            tree=tree,
            html_report=html_report,
            ai_summary="\n".join(ai_cleaned_lines),
            last_monitoring_at=latest_monitoring_date,
            survival_trend_dates=[item['date'] for item in survival_trend],
            survival_trend_alive=[item['alive'] for item in survival_trend],
            survival_trend_dead=[item['dead'] for item in survival_trend],
        )

        context.update({
            "cached_html": html_report,
            "ai_cleaned_lines": ai_cleaned_lines,
            "from_cache": False,
            "survival_trend_dates": [item['date'] for item in survival_trend],
            "survival_trend_alive": [item['alive'] for item in survival_trend],
            "survival_trend_dead": [item['dead'] for item in survival_trend],
        })
        return context





#events report
class MonitoredEventListRView(ListView):
    model = TreePlantingEvent
    template_name = 'monitoring/monitoring/monitored_event_list_r.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = TreePlantingEvent.objects.annotate(
            monitoring_count=Count('treemonitoringrecord')
        ).filter(monitoring_count__gt=0)

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(plot__name__icontains=query) |
                Q(treemonitoringrecord__trees__name__icontains=query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from ind_trees.models import TreePlantingEvent, TreePlantingDetail, TreeMonitoringRecord

class TreePlantingEventReportView(DetailView):
    model = TreePlantingEvent
    template_name = 'report/tree_event_report.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object

        # Planting Details
        planting_details = TreePlantingDetail.objects.filter(event=event).select_related('tree', 'tree__species')
        context['planting_details'] = planting_details

        # Total Species
        context['total_species'] = planting_details.count()

        # Monitoring Records for all trees in this event
        monitoring_records = TreeMonitoringRecord.objects.filter(planting_event=event).prefetch_related('trees', 'monitored_trees', 'photos')
        context['monitoring_records'] = monitoring_records

        # Event Images
        context['event_images'] = event.images.all()

        # Aggregated Alive / Dead Count
        alive_count = sum([record.alive_count for record in monitoring_records])
        dead_count = sum([record.dead_count for record in monitoring_records])
        context['alive_count'] = alive_count
        context['dead_count'] = dead_count

        # Most Recent Monitoring Date
        latest_monitoring = monitoring_records.order_by('-monitored_at').first()
        context['latest_monitoring_date'] = latest_monitoring.monitored_at if latest_monitoring else None

        # Environmental / Plot Data
        plot = event.plot
        context['plot'] = plot
        if plot:
            context['environmental_data'] = getattr(plot, 'land', None)

        return context

from django.views.generic import DetailView
from django.db.models import Sum, Count, Min, Max
from collections import Counter
from datetime import timedelta

from ind_trees.models import (
    TreePlantingEvent,
    TreePlantingDetail,
    TreeMonitoringRecord,
    MonitoredTreeDetail,
    TreeIntervention,
)

class TreePlantingEventMonitoringReportView(DetailView):
    model = TreePlantingEvent
    template_name = 'report/tree_event_monitoring_report.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object

        # 1️⃣ Planting details
        planting_details = TreePlantingDetail.objects.filter(event=event)
        context['planting_details'] = planting_details

        # 2️⃣ Linked monitoring records (all trees in the event)
        monitoring_records = TreeMonitoringRecord.objects.filter(
            trees__in=event.trees.all()
        ).distinct()
        context['monitoring_records'] = monitoring_records
        context['num_monitoring_records'] = monitoring_records.count()

        if monitoring_records.exists():
            # First and latest monitoring date
            context['first_monitoring_date'] = monitoring_records.order_by('monitored_at').first().monitored_at
            context['latest_monitoring_date'] = monitoring_records.order_by('-monitored_at').first().monitored_at

            # Average monitoring frequency in days
            dates = list(mr.monitored_at for mr in monitoring_records.order_by('monitored_at'))
            if len(dates) > 1:
                total_days = (dates[-1] - dates[0]).days
                avg_freq = total_days / (len(dates)-1)
            else:
                avg_freq = None
            context['avg_monitoring_frequency'] = avg_freq

            # Total alive and dead counts
            


# Get all trees planted in this event
            planted_trees = Tree.objects.filter(planting_events=event)

            total_alive = 0
            total_dead = 0

            for tree in planted_trees:
                # Get latest monitoring record for this tree
                latest_tree_monitoring = MonitoredTreeDetail.objects.filter(
                    tree=tree,
                    monitoring_record__in=monitoring_records
                ).order_by('-monitoring_record__monitored_at').first()

                if latest_tree_monitoring:
                    total_alive += latest_tree_monitoring.alive_count
                    total_dead += latest_tree_monitoring.dead_count

            context['total_alive'] = total_alive
            context['total_dead'] = total_dead


            # Most common health status
            health_list = list(mr.health_status for mr in monitoring_records if mr.health_status)
            context['most_common_health_status'] = Counter(health_list).most_common(1)[0][0] if health_list else None

            # Most frequent threats observed
            threats_list = []
            for mr in monitoring_records:
                if mr.threats_observed:
                    threats_list.extend([t.strip() for t in mr.threats_observed.split(',')])
            context['most_frequent_threats'] = Counter(threats_list).most_common(1)[0][0] if threats_list else None

            # Most common conservation actions
            actions_list = []
            for mr in monitoring_records:
                if mr.conservation_actions:
                    actions_list.extend([a.strip() for a in mr.conservation_actions.split(',')])
            context['most_common_conservation_actions'] = Counter(actions_list).most_common(1)[0][0] if actions_list else None
        else:
            # No monitoring records
            context.update({
                'first_monitoring_date': None,
                'latest_monitoring_date': None,
                'avg_monitoring_frequency': None,
                'total_alive': 0,
                'total_dead': 0,
                'most_common_health_status': None,
                'most_frequent_threats': None,
                'most_common_conservation_actions': None,
            })

        # 3️⃣ Per-species performance table
        species_performance = []
        for detail in planting_details:
            tree = detail.tree
            species_name = tree.species.common_name if tree.species else tree.name
            qty_planted = detail.quantity_planted

            # Latest monitoring for this tree
            latest_monitor = MonitoredTreeDetail.objects.filter(
                monitoring_record__in=monitoring_records,
                tree=tree
            ).order_by('-monitoring_record__monitored_at').first()

            alive_latest = latest_monitor.alive_count if latest_monitor else 0
            dead_latest = latest_monitor.dead_count if latest_monitor else 0
            survival_pct = round((alive_latest / qty_planted * 100), 2) if qty_planted else 0
            recent_health_status = latest_monitor.monitoring_record.health_status if latest_monitor else None

            # Interventions
            interventions = TreeIntervention.objects.filter(tree=tree, date__lte=context['latest_monitoring_date']).values_list('action', flat=True)
            interventions_taken = ", ".join([i for i in interventions]) if interventions else None

            species_performance.append({
                'species': species_name,
                'qty_planted': qty_planted,
                'alive_latest': alive_latest,
                'dead_latest': dead_latest,
                'survival_pct': survival_pct,
                'recent_health_status': recent_health_status,
                'interventions_taken': interventions_taken,
            })

        context['species_performance'] = species_performance

        return context




# views.py
from django.views.generic import TemplateView
from django.db.models import Sum
from ind_trees.models import (
    TreePlantingEvent, TreeMonitoringRecord, MonitoredTreeDetail,
    TreeIntervention
)
from django.utils.safestring import mark_safe
import json
from collections import defaultdict

class TreeEventTrendAnalysisView(TemplateView):
    template_name = "report/tree_event_trends.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('pk')
        event = TreePlantingEvent.objects.get(pk=event_id)
        context['event'] = event

        # All monitoring records linked to this event
        monitoring_records = TreeMonitoringRecord.objects.filter(
            planting_event=event
        ).order_by('monitored_at')
        context['monitoring_records'] = monitoring_records

        # --- 1️⃣ Survival Rate ---
        species_survival = defaultdict(list)
        total_planted = sum([d.quantity_planted for d in event.treeplantingdetail_set.all()])

        for record in monitoring_records:
            date = record.monitored_at.strftime('%Y-%m-%d')
            alive_sum = record.monitored_trees.aggregate(total_alive=Sum('alive_count'))['total_alive'] or 0
            survival_rate_total = (alive_sum / total_planted) * 100 if total_planted else 0
            species_survival['event_total'].append([date, survival_rate_total])

            for detail in record.monitored_trees.all():
                species_name = detail.tree.species.common_name if detail.tree.species else detail.tree.name
                qty_planted = detail.tree.planting_events.through.objects.get(tree=detail.tree, event=event).quantity_planted
                survival_rate = (detail.alive_count / qty_planted) * 100
                species_survival[species_name].append([date, survival_rate])

        context['species_survival_json'] = mark_safe(json.dumps(species_survival))

        # --- 2️⃣ Health Trends ---
        health_trends = defaultdict(list)
        for record in monitoring_records:
            date = record.monitored_at.strftime('%Y-%m-%d')
            for detail in record.monitored_trees.all():
                species_name = detail.tree.species.common_name if detail.tree.species else detail.tree.name
                health_trends[species_name].append([date, record.health_status])
        context['health_trends_json'] = mark_safe(json.dumps(health_trends))

        # --- 3️⃣ Threat Trends ---
        threat_trends = defaultdict(list)
        for record in monitoring_records:
            threats = record.threats_observed.split(',') if record.threats_observed else []
            for threat in threats:
                threat_trends[threat.strip()].append(1)
        context['threat_trends_json'] = mark_safe(json.dumps({k: len(v) for k, v in threat_trends.items()}))

        # --- 4️⃣ Intervention Effectiveness ---
        interventions = TreeIntervention.objects.filter(tree__planting_events=event)
        intervention_data = defaultdict(lambda: {'pre_alive': 0, 'post_alive': 0})
        for intervention in interventions:
            tree = intervention.tree
            pre_record = MonitoredTreeDetail.objects.filter(
                tree=tree,
                monitoring_record__monitored_at__lt=intervention.date
            ).order_by('-monitoring_record__monitored_at').first()
            post_record = MonitoredTreeDetail.objects.filter(
                tree=tree,
                monitoring_record__monitored_at__gte=intervention.date
            ).order_by('monitoring_record__monitored_at').first()
            if pre_record:
                intervention_data[intervention.action]['pre_alive'] += pre_record.alive_count
            if post_record:
                intervention_data[intervention.action]['post_alive'] += post_record.alive_count
        context['intervention_data_json'] = mark_safe(json.dumps(intervention_data))

        # --- 5️⃣ Mortality Trend ---
        mortality_trend = []
        planting_date = event.date_planted
        for record in monitoring_records:
            days = (record.monitored_at.date() - planting_date).days
            dead_count = record.monitored_trees.aggregate(total_dead=Sum('dead_count'))['total_dead'] or 0
            mortality_trend.append([days, dead_count])
        context['mortality_trend_json'] = mark_safe(json.dumps(mortality_trend))

        return context

from django.shortcuts import render
from django.test import RequestFactory
from django.http import Http404
from ind_trees.models import TreePlantingEvent, TreePlantingDetail, TreeMonitoringRecord, MonitoredTreeDetail
from collections import defaultdict
import re

# Import the 3 existing sub-views
from .views import (
    TreePlantingEventReportView,
    TreePlantingEventMonitoringReportView,
    TreeEventTrendAnalysisView
)

# Import AI helper for event insights
from .ai_utils_event import get_event_ai_insights
from .models import EventReportCache, EventReportHistory
from .ai_utils_event import get_event_ai_insights

from django.views.generic import DetailView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Max, Sum
from django.template.loader import render_to_string
from collections import defaultdict, Counter
import re
import json
# views.py

class EventReportsListView(DetailView):
    model = TreePlantingEvent
    template_name = "report/event_reports_list.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        try:
            cached = EventReportCache.objects.get(event=event)
            context['cached_report'] = cached
        except EventReportCache.DoesNotExist:
            context['cached_report'] = None
        context['reports'] = event.report_history.all()
        return context


class EventCachedReportView(DetailView):
    model = EventReportCache
    template_name = "report/event_cached_report.html"
    context_object_name = "cached_report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cache = self.object
        context['event'] = cache.event
        context['cached_html'] = cache.html_report
        context['ai_cleaned_lines'] = cache.ai_summary.splitlines() if cache.ai_summary else []
        return context


class EventReportDetailView(DetailView):
    model = EventReportHistory
    template_name = "report/event_cached_report.html"   # reuse same display template
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.object
        context['event'] = report.event
        context['cached_html'] = report.html_report
        context['ai_cleaned_lines'] = report.ai_summary.splitlines() if report.ai_summary else []
        return context



class CombinedTreeEventReportView(DetailView):
    model = TreePlantingEvent
    template_name = "report/event_full_report.html"   # uses the wrapper template
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        force_generate = self.request.GET.get('force') == 'true'

        # ---- latest monitoring date for this event ----
        latest_monitoring_date = TreeMonitoringRecord.objects.filter(
            planting_event=event
        ).aggregate(latest=Max('monitored_at'))['latest']

        # ---- check cache ----
        cache = getattr(event, 'cached_report', None)
        if not force_generate and cache and cache.last_monitoring_at == latest_monitoring_date:
            # Serve from cache
            context['ai_cleaned_lines'] = cache.ai_summary.splitlines() if cache.ai_summary else []
            context['from_cache'] = True
            # Still need planting_html etc.? We can store them in extra_data or just skip.
            # For full report view, we can just output the cached html directly.
            # But the template expects planting_html, monitoring_html, trend_html.
            # Since we're using the wrapper template that includes the partial, we could pass the cached_html and let the template render it.
            # Easiest: just re-render the partial using the cached content? No – we'll just pass the cached_html and adjust the template.
            # For now, we'll still generate the sub-views (lightweight) to keep template consistency.
            # We'll fall back to full generation but skip AI? Too wasteful.
            # Better to store the whole partial rendering (the inner content) as html_report, and then in the main template use {{ cached_html|safe }} instead of tabs.
            # So we'll modify the main template to accept cached_html.
            # We'll adjust both templates.
            return self._serve_from_cache(context, cache)

        # ============ FULL GENERATION ============
        # Child views
        from django.test import RequestFactory
        rf = RequestFactory()
        fake_request = rf.get("/")

        planting_view = TreePlantingEventReportView.as_view()
        monitoring_view = TreePlantingEventMonitoringReportView.as_view()
        trend_view = TreeEventTrendAnalysisView.as_view()

        planting_html = planting_view(fake_request, pk=event.pk).rendered_content
        monitoring_html = monitoring_view(fake_request, pk=event.pk).rendered_content
        trend_html = trend_view(fake_request, pk=event.pk).rendered_content

        # ---- Build AI summary text ----
        summary_lines = [
            f"Planting Event: {event.name}",
            f"Organizer: {event.organizer}",
            f"Location: {event.location}",
            f"Date: {event.date_planted}",
            f"Number of Trees Planted: {event.number_of_trees_planted}",
        ]
        if event.plot:
            summary_lines.append(f"Plot: {event.plot.name} (Lat: {event.latitude}, Lng: {event.longitude})")
        if event.notes:
            summary_lines.append(f"Notes: {event.notes}")

        planting_details = TreePlantingDetail.objects.filter(event=event).select_related('tree')
        summary_lines.append("\n=== Trees Planted ===")
        for detail in planting_details:
            summary_lines.append(f"- {detail.tree.name} | Quantity: {detail.quantity_planted}")

        monitoring_records = TreeMonitoringRecord.objects.filter(planting_event=event).prefetch_related('trees')
        tree_stats = defaultdict(lambda: {'alive': 0, 'dead': 0, 'records': 0})
        if monitoring_records.exists():
            for record in monitoring_records:
                details = MonitoredTreeDetail.objects.filter(monitoring_record=record)
                for d in details:
                    tree_stats[d.tree.name]['alive'] += d.alive_count
                    tree_stats[d.tree.name]['dead'] += d.dead_count
                    tree_stats[d.tree.name]['records'] += 1

            summary_lines.append("\n=== Monitoring Summary ===")
            for tree_name, stats in tree_stats.items():
                total = stats['alive'] + stats['dead']
                survival_rate = (stats['alive'] / total * 100) if total > 0 else 0
                summary_lines.append(
                    f"- {tree_name}: {stats['alive']} alive, {stats['dead']} dead "
                    f"({survival_rate:.1f}% survival across {stats['records']} records)"
                )
        else:
            summary_lines.append("No monitoring records available for this event yet.")

        summary_lines.append("\n=== Event Environmental Context ===")
        if event.plot and hasattr(event.plot, 'land_data'):
            land = event.plot.land_data
            summary_lines.append(
                f"Soil Type: {land.soil_type}, Soil pH: {land.soil_pH}, "
                f"Fertility: {land.fertility_level}, Rainfall: {land.rainfall_mm} mm/year, "
                f"Temperature: {land.temperature_c} °C"
            )
        else:
            summary_lines.append("No detailed environmental data recorded.")

        # Continuity: include previous AI summary from latest history record
        latest_history = event.report_history.first()
        if latest_history and latest_history.ai_summary:
            summary_lines.append("\n--- Previous AI Analysis (for continuity) ---")
            summary_lines.append(latest_history.ai_summary)
            summary_lines.append(
                "--- End of Previous Analysis ---\n"
                "Now update the report with the latest data above, "
                "building upon the previous insights while adding new findings. "
                "Maintain a consistent professional tone and structure."
            )

        event_summary_text = "\n".join(summary_lines)
        ai_raw = get_event_ai_insights(event_summary_text)

        # Clean AI output
        ai_cleaned_lines = []
        for paragraph in re.split(r"\n\s*\n", ai_raw):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            paragraph = re.sub(r"<.*?>", "", paragraph)
            paragraph = re.sub(r"[*#`]", "", paragraph)
            paragraph = re.sub(r"\s+", " ", paragraph)
            ai_cleaned_lines.append(paragraph)

        # ---- Render the inner content partial to a string ----
        inner_context = {
            'event': event,
            'planting_html': planting_html,
            'monitoring_html': monitoring_html,
            'trend_html': trend_html,
            'ai_cleaned_lines': ai_cleaned_lines,
        }
        rendered_inner_html = render_to_string("report/_event_report_content.html", inner_context)

        # ---- Save to cache and history ----
        total_alive = sum(stats['alive'] for stats in tree_stats.values()) if tree_stats else 0
        total_planted = event.number_of_trees_planted or sum(d.quantity_planted for d in planting_details)
        survival_rate = (total_alive / total_planted * 100) if total_planted else 0

        cache_data = {
            'html_report': rendered_inner_html,
            'ai_summary': "\n".join(ai_cleaned_lines),
            'last_monitoring_at': latest_monitoring_date,
            'total_trees_planted': total_planted,
            'survival_rate': survival_rate,
        }

        if cache:
            for field, value in cache_data.items():
                setattr(cache, field, value)
            cache.save()
        else:
            EventReportCache.objects.create(event=event, **cache_data)

        EventReportHistory.objects.create(
            event=event,
            html_report=rendered_inner_html,
            ai_summary=cache_data['ai_summary'],
            last_monitoring_at=latest_monitoring_date,
            total_trees_planted=total_planted,
            survival_rate=survival_rate,
        )

        # ---- Return context for the wrapper template ----
        context.update({
            'planting_html': planting_html,
            'monitoring_html': monitoring_html,
            'trend_html': trend_html,
            'ai_cleaned_lines': ai_cleaned_lines,
            'from_cache': False,
        })
        return context

    def _serve_from_cache(self, context, cache):
        """Populate context to display the cached report directly."""
        # Since the cached html is the full inner content, we'll pass it as cached_html
        # and let the wrapper template include it.
        context['cached_html'] = cache.html_report
        context['ai_cleaned_lines'] = cache.ai_summary.splitlines() if cache.ai_summary else []
        context['from_cache'] = True
        # We still need the event object (already in context)
        return context





# plots/views.py

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from ind_trees.models import Plot, TreePlantingEvent, TreeMonitoringRecord, Tree

class PlotReportView(DetailView):
    model = Plot
    template_name = "report/plot_report.html"
    context_object_name = "plot"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plot = self.get_object()
        
        # --- Plot Images ---
        plot_images = plot.images.all()
        context['plot_images'] = plot_images

        # --- Monitoring Records ---
        monitoring_records = plot.monitoring_records.all()
        context['monitoring_records'] = monitoring_records
        context['total_monitoring_records'] = monitoring_records.count()
        
        if monitoring_records.exists():
            context['last_monitored_by'] = monitoring_records.first().monitored_by
            context['last_monitored_at'] = monitoring_records.first().monitored_at
        else:
            context['last_monitored_by'] = None
            context['last_monitored_at'] = None

        # --- Tree Planting Events ---
        planting_events = TreePlantingEvent.objects.filter(plot=plot)
        context['planting_events'] = planting_events
        context['total_planting_events'] = planting_events.count()

        # --- Total Trees Planted ---
        tree_details = plot.environmental_data.values('trees__name').distinct()
        context['tree_species'] = [t['trees__name'] for t in tree_details if t['trees__name']]
        
        total_trees = sum([detail.quantity_planted for event in planting_events for detail in event.treeplantingdetail_set.all()])
        context['total_trees_planted'] = total_trees

        # --- Unique Species Count ---
        context['species_count'] = len(context['tree_species'])
        
        return context
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from ind_trees.models import Plot, EnvironmentalData, PlotMonitoringRecord

class PlotDetailView(DetailView):
    model = Plot
    template_name = 'report/plot_environmental_detail.html'
    context_object_name = 'plot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plot = self.object

        # Get environmental data
        environmental_data = plot.land.first()  # because related_name='land' is reverse FK
        context['environmental_data'] = environmental_data

        # Get latest monitoring record
        latest_monitoring = plot.monitoring_records.first()  # ordered by '-monitored_at' in model Meta
        context['latest_monitoring'] = latest_monitoring
        if latest_monitoring:
            context['latest_monitoring_photos'] = latest_monitoring.photos.all()
        else:
            context['latest_monitoring_photos'] = []

        return context
from django.views.generic import TemplateView
from ind_trees.models import Plot
from .gee import analyze_plot
from openai import OpenAI
from geopy.geocoders import Nominatim
from django.conf import settings
import json
import re

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_region_from_coordinates(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tree-ai-monitor")
        location = geolocator.reverse((lat, lon), language='en')
        return location.address if location else "Unknown region"
    except Exception:
        return "Unknown region"

def clean_ai_text(text: str) -> str:
    """
    Remove unwanted markdown symbols like '#', '*', '-', or numbering for a clean professional style.
    """
    text = re.sub(r'^[#*\-\d\.\s]+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', '\n\n', text)  # collapse multiple blank lines
    return text.strip()

from django.views.generic import TemplateView
from ind_trees.models import Plot
from .gee import analyze_plot
from openai import OpenAI
from geopy.geocoders import Nominatim
from django.conf import settings
import json

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_region_from_coordinates(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tree-ai-monitor")
        location = geolocator.reverse((lat, lon), language='en')
        return location.address if location else "Unknown region"
    except Exception:
        return "Unknown region"

def clean_ai_text(text: str) -> str:
    """
    Remove unwanted markdown symbols like #, *, bullets, etc.
    Keep plain readable paragraphs.
    """
    cleaned = text.replace("#", "").replace("*", "").replace("-", "").strip()
    return cleaned

class PlotAIReportTemplateView(TemplateView):
    template_name = "report/ai_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plot_id = self.kwargs.get("plot_id")
        plot = Plot.objects.get(id=plot_id)
        context["plot"] = plot

        # Only proceed if plot has boundary coordinates
        if not plot.boundary_coordinates:
            context["error"] = "Plot does not have boundary coordinates."
            return context

        # Convert coordinates to GeoJSON polygon
        geojson_polygon = {
            "type": "Polygon",
            "coordinates": [[[lng, lat] for lat, lng in plot.boundary_coordinates]]
        }

        # -----------------------------
        # Run GEE analysis
        # -----------------------------
        gee_data = analyze_plot(geojson_polygon)

        # -----------------------------
        # Determine region for context
        # -----------------------------
        first_coord = plot.boundary_coordinates[0]
        region = get_region_from_coordinates(first_coord[0], first_coord[1])

        # -----------------------------
        # Generate AI interpretation
        # -----------------------------
        system_prompt = (
            " on plot overview just put only notice that  data is analyzed from GEE Satellites and date(make a proffesional statement)"
            "You are Tree & Environmental Analyst AI. Interpret raw environmental from GEE and sattelite data "
            "and plot metrics into a brief explanation for each data for forestry experts in point form. "
            "Avoid markdown symbols like #, *, or bullets. Use readable paragraphs."
            "keep GEE data brief and heavy."
        )

        user_prompt = (
            f"Plot Name: {plot.name}\n"
            f"Region: {region}\n"
            f"GeoJSON Boundary: {json.dumps(geojson_polygon)}\n"
            f"Raw GEE Data:\n{json.dumps(gee_data, indent=2)}\n\n"
            "Generate a detailed, professional environmental & tree monitoring report, "
            "with clear sections and actionable advice, suitable for experts."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1800
            )
            ai_report_raw = response.choices[0].message.content.strip()
            ai_report = clean_ai_text(ai_report_raw)
        except Exception as e:
            ai_report = f"⚠️ Error generating AI report: {e}"

        # -----------------------------
        # Pass to template
        # -----------------------------
        context["gee_data"] = gee_data
        context["gee_data_json"] = json.dumps(gee_data, indent=2)  # <--- move here inside method
        context["ai_report"] = ai_report
        context["region"] = region
        return context


from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from ind_trees.models import (
    Plot, TreePlantingEvent, TreePlantingDetail,
    TreeMonitoringRecord, PlotMonitoringRecord
)
from openai import OpenAI
from django.conf import settings
import json

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def format_tree_data(plot: Plot):
    """
    Aggregate tree planting & monitoring data for the given plot.
    """
    tree_events = TreePlantingEvent.objects.filter(plot=plot)
    event_summaries = []
    for event in tree_events:
        trees_detail = TreePlantingDetail.objects.filter(event=event)
        tree_list = [f"{td.tree.name}: {td.quantity_planted}" for td in trees_detail]
        event_summaries.append({
            "event_name": event.name,
            "date": event.date_planted.isoformat(),
            "location": event.location,
            "trees_planted": tree_list,
            "notes": event.notes,
            "total_trees": sum(td.quantity_planted for td in trees_detail)
        })
    return event_summaries

def format_monitoring_data(plot: Plot):
    """
    Aggregate tree & plot monitoring data.
    """
    tree_records = TreeMonitoringRecord.objects.filter(plot=plot)
    plot_records = PlotMonitoringRecord.objects.filter(plot=plot)

    tree_monitoring_summary = []
    for record in tree_records:
        tree_monitoring_summary.append({
            "monitored_at": record.monitored_at.isoformat(),
            "alive_count": record.alive_count,
            "dead_count": record.dead_count,
            "health_status": record.health_status,
            "threats_observed": record.threats_observed,
            "actions_taken": record.conservation_actions
        })

    plot_monitoring_summary = []
    for record in plot_records:
        plot_monitoring_summary.append({
            "monitored_at": record.monitored_at.isoformat(),
            "vegetation_cover": record.vegetation_cover,
            "invasive_species": record.invasive_species_present,
            "signs_of_deforestation": record.signs_of_deforestation,
            "fire_signs": record.signs_of_fire,
            "human_activity": record.human_activity_notes,
            "threats_identified": record.threats_identified,
            "recommended_actions": record.recommended_actions,
            "water_quality": record.water_quality,
            "air_quality": record.air_quality,
            "weather_conditions": record.weather_conditions,
        })

    return {
        "tree_monitoring": tree_monitoring_summary,
        "plot_monitoring": plot_monitoring_summary
    }


def clean_ai_text(text: str) -> str:
    """
    Remove unwanted markdown symbols like #, *, bullets, etc.
    """
    cleaned = text.replace("#", "").replace("*", "").replace("-", "").strip()
    return cleaned


class OverallPlotAIAnalysisView(TemplateView):
    template_name = "report/overall_ai_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plot_id = self.kwargs.get("plot_id")
        plot = get_object_or_404(Plot, id=plot_id)
        context["plot"] = plot

        # Aggregate data
        tree_data = format_tree_data(plot)
        monitoring_data = format_monitoring_data(plot)
        environmental_data = {}
        if plot.land_data:
            env = plot.land_data
            environmental_data = {
                "soil_type": env.soil_type,
                "soil_pH": env.soil_pH,
                "fertility_level": env.fertility_level,
                "rainfall_mm": env.rainfall_mm,
                "temperature_c": env.temperature_c,
                "water_source_proximity": env.water_source_proximity,
                "biodiversity_notes": env.biodiversity_notes,
            }

        # Build the input summary for AI
        data_summary = {
            "tree_planting_events": tree_data,
            "monitoring_records": monitoring_data,
            "environmental_data": environmental_data,
            "plot_info": {
                "name": plot.name,
                "area_hectares": plot.area_hectares,
                "land_ownership": plot.land_ownership,
                "protection_status": plot.protection_status,
                "zone_type": plot.zone_type,
            }
        }

        user_prompt = (
            "You are a senior forestry and environmental analyst AI. "
            "Analyze the provided data and generate an overall professional report "
            "assessing the health, survival, and performance of trees, the plot condition, "
            "and event effectiveness. Provide actionable recommendations for improvements. "
            "Avoid markdown symbols, bullets, or headers; use clear readable paragraphs.\n\n"
            f"Data:\n{json.dumps(data_summary, indent=2)}"
        )

        system_prompt = (
            "You are an expert AI in forestry, tree planting monitoring, and environmental management. "
            "Generate a clear, structured, professional summary report suitable for stakeholders and researchers."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            ai_report_raw = response.choices[0].message.content.strip()
            ai_report = clean_ai_text(ai_report_raw)
        except Exception as e:
            ai_report = f"⚠️ Error generating AI report: {e}"

        # Pass all data to template
        context["ai_report"] = ai_report
        context["data_summary"] = data_summary
        return context


from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from ind_trees.models import Plot
from .gee import analyze_plot
from openai import OpenAI
from geopy.geocoders import Nominatim
from django.conf import settings
import json
import re

# OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def clean_ai_text(text: str) -> str:
    """Remove unwanted markdown symbols and keep text clean."""
    text = re.sub(r'^[#*\-\d\.\s]+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', '\n\n', text)  # collapse blank lines
    return text.strip()

def get_region_from_coordinates(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tree-ai-monitor")
        location = geolocator.reverse((lat, lon), language='en')
        return location.address if location else "Unknown region"
    except:
        return "Unknown region"


        
from ind_trees.models import Plot, TreePlantingEvent
from .views import format_tree_data, format_monitoring_data  # reuse your existing helpers
from .views import format_tree_data, format_monitoring_data

class UnifiedPlotReportView(TemplateView):
    template_name = "report/unified_plot_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plot_id = self.kwargs.get("plot_id")
        plot = get_object_or_404(Plot, id=plot_id)
        context["plot"] = plot

        # --- PlotReportView data ---
        plot_images = plot.images.all()
        # 🔧 FIX: use filter instead of undefined reverse relation
        planting_events = TreePlantingEvent.objects.filter(plot=plot)
        monitoring_records = plot.monitoring_records.all()
        total_trees = sum(
            detail.quantity_planted
            for event in planting_events
            for detail in event.treeplantingdetail_set.all()
        )
        # 🔧 Also fix the tree species list (if environmental_data might be None)
        tree_species = []
        if hasattr(plot, 'environmental_data') and plot.environmental_data.exists():
            tree_species = list(
                {t['trees__name'] for t in plot.environmental_data.values('trees__name') if t['trees__name']}
            )

        context.update({
            "plot_images": plot_images,
            "planting_events": planting_events,
            "monitoring_records": monitoring_records,
            "total_monitoring_records": monitoring_records.count(),
            "last_monitored_by": monitoring_records.first().monitored_by if monitoring_records.exists() else None,
            "last_monitored_at": monitoring_records.first().monitored_at if monitoring_records.exists() else None,
            "total_planting_events": planting_events.count(),
            "total_trees_planted": total_trees,
            "tree_species": tree_species,
            "species_count": len(tree_species),
        })

        # --- PlotDetailView data ---
        environmental_data = plot.land.first() if hasattr(plot, 'land') else None
        latest_monitoring = monitoring_records.first() if monitoring_records.exists() else None
        latest_monitoring_photos = latest_monitoring.photos.all() if latest_monitoring else []

        context.update({
            "environmental_data": environmental_data,
            "latest_monitoring": latest_monitoring,
            "latest_monitoring_photos": latest_monitoring_photos,
        })

        # --- PlotAIReportTemplateView data ---
        if plot.boundary_coordinates:
            geojson_polygon = {"type": "Polygon", "coordinates": [[[lng, lat] for lat, lng in plot.boundary_coordinates]]}
            gee_data = analyze_plot(geojson_polygon)
            region = get_region_from_coordinates(plot.boundary_coordinates[0][0], plot.boundary_coordinates[0][1])

            # Generate AI report (GEE)
            system_prompt = (
                "You are Tree & Environmental Analyst AI. Interpret raw environmental from GEE and satellite data "
                "into a professional summary suitable for forestry experts, avoiding markdown/bullets."
            )
            user_prompt = (
                f"Plot: {plot.name}\nRegion: {region}\nGeoJSON: {json.dumps(geojson_polygon)}\n"
                f"Raw GEE Data:\n{json.dumps(gee_data, indent=2)}"
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1800
                )
                ai_gee_report = clean_ai_text(response.choices[0].message.content.strip())
            except Exception as e:
                ai_gee_report = f"⚠️ Error generating GEE AI report: {e}"

            context.update({
                "gee_data": gee_data,
                "gee_data_json": json.dumps(gee_data, indent=2),
                "ai_gee_report": ai_gee_report,
                "region": region
            })
        else:
            context.update({
                "gee_data": None,
                "gee_data_json": None,
                "ai_gee_report": None,
                "region": "Unknown"
            })

        # --- OverallPlotAIAnalysisView data ---
        tree_data = format_tree_data(plot)
        monitoring_data = format_monitoring_data(plot)
        environmental_summary = {}
        if environmental_data:
            environmental_summary = {
                "soil_type": environmental_data.soil_type,
                "soil_pH": environmental_data.soil_pH,
                "fertility_level": environmental_data.fertility_level,
                "rainfall_mm": environmental_data.rainfall_mm,
                "temperature_c": environmental_data.temperature_c,
                "water_source_proximity": environmental_data.water_source_proximity,
                "biodiversity_notes": environmental_data.biodiversity_notes,
            }
        overall_summary_input = {
            "tree_planting_events": tree_data,
            "monitoring_records": monitoring_data,
            "environmental_data": environmental_summary,
            "plot_info": {
                "name": plot.name,
                "area_hectares": plot.area_hectares,
                "land_ownership": plot.land_ownership,
                "protection_status": plot.protection_status,
                "zone_type": plot.zone_type,
            }
        }

        try:
            system_prompt_overall = (
                "You are an expert AI in forestry, tree planting monitoring, and environmental management. "
                "Generate a professional summary suitable for stakeholders."
            )
            user_prompt_overall = (
                f"Analyze the following data and provide actionable recommendations:\n{json.dumps(overall_summary_input, indent=2)}"
            )
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt_overall},
                    {"role": "user", "content": user_prompt_overall}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            overall_ai_report = clean_ai_text(response.choices[0].message.content.strip())
        except Exception as e:
            overall_ai_report = f"⚠️ Error generating overall AI report: {e}"

        context["overall_ai_report"] = overall_ai_report
        context["overall_summary_input"] = overall_summary_input

        return context