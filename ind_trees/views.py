from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Tree, TreeImage, MedicalBenefitImage, CulturalSignificanceImage, ThreatsConservationImage, HeritageSiteImage
from .models import Tree, Category
from django.core.paginator import Paginator
from django.http import HttpResponse
import qrcode
from io import BytesIO
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile


class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')

class Monitor(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'monitor.html')


from django.views import View
from django.shortcuts import render
from django.db.models import Q
from .models import Tree  # Ensure your Tree model is imported

class Index(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')

        if search_query:
            latest_trees = Tree.objects.filter(
                Q(name__icontains=search_query) |
                Q(tree_description__icontains=search_query)
            ).order_by('-id')
        else:
            latest_trees = Tree.objects.all().order_by('-id')[:3]

        context = {
            'latest_trees': latest_trees,
            'search_query': search_query,
        }
        return render(request, 'index.html', context)


def generate_qr_code(request, pk, format="png"):
    tree = get_object_or_404(Tree, pk=pk)
    qr = qrcode.make(f"https://imvelo.yveeswatini.africa{tree.get_absolute_url()}")

    if format == "png":
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        return HttpResponse(buffer.getvalue(), content_type="image/png")

    elif format == "pdf":
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(200, 800, f"QR Code for {tree.name}")
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format="PNG")
        pdf.drawInlineImage(qr_buffer, 150, 600, width=300, height=300)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf")

    return HttpResponse(status=400)
# views.py
from django.views.generic import ListView
from .models import Tree
from django.db.models import Q


class TreeListView(ListView):
    model = Tree
    context_object_name = 'trees'
    paginate_by = 9   # Changed to 9 for a neat 3-column grid; feel free to adjust

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Tree.objects.filter(
                Q(name__icontains=query) |
                Q(tree_description__icontains=query) |
                Q(categories__name__icontains=query)
            ).distinct().order_by('-created_at')
        return Tree.objects.all().order_by('-created_at')

    def get_template_names(self):
        # Only change template for htmx requests
        if self.request.htmx:
            page = self.request.GET.get('page', '1')
            query = self.request.GET.get('q', '')
            # For search or first page, return the full grid (with cards + load-more button)
            if query or page == '1':
                return ['partials/tree_list_grid.html']
            else:
                # Load-more request: return only the new cards (plus OOB button swap)
                return ['partials/tree_list_more_items.html']
        # Default full page template
        return ['tree_list.html']

class TreeDetailView(DetailView):
    model = Tree
    template_name = 'tree_detail.html'
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

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Tree

# View for listing all categories
class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'  # Template to list all categories
    context_object_name = 'categories'
    queryset = Category.objects.order_by('name')  # Added default sorting by name

# View for listing trees in a specific category
class TreesByCategoryListView(ListView):
    model = Tree
    template_name = 'trees_by_category.html'  # Template to list trees in a category
    context_object_name = 'trees'
    paginate_by = getattr(settings, 'PAGINATE_BY', 20)  # Configurable pagination size

    def get_queryset(self):
        category_id = self.kwargs.get('pk')
        self.category = get_object_or_404(Category, pk=category_id)
        return Tree.objects.filter(categories=self.category).order_by('name')  # Ensuring consistent ordering by name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context




from django.urls import path
from django.views.generic import ListView, DetailView
from .models import HeritageSite, Tree

class HeritageSiteListView(ListView):
    model = HeritageSite
    template_name = 'heritage_site_list.html'
    context_object_name = 'heritage_sites'
    paginate_by = 10


class HeritageSiteDetailView(DetailView):
    model = HeritageSite
    template_name = 'heritage_site_detail.html'
    context_object_name = 'heritage_site'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trees'] = self.object.tree_set.all()
        return context


class TreesByHeritageSiteListView(ListView):
    template_name = 'trees_by_heritage_site.html'
    context_object_name = 'trees'
    paginate_by = 20

    def get_queryset(self):
        return Tree.objects.filter(heritage_sites__id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heritage_site'] = HeritageSite.objects.get(pk=self.kwargs['pk'])
        return context


class MedialBenefit(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'medical_benefits.html')


from .models import ConservationStatus, Tree

class ConservationStatusListView(ListView):
    model = ConservationStatus
    template_name = 'conservation_status_list.html'
    context_object_name = 'statuses'
    
    def get_queryset(self):
        # Fetch unique conservation statuses (in case any duplicates exist)
        return ConservationStatus.objects.distinct()

class TreeListByConservationStatusView(ListView):
    model = Tree
    template_name = 'tree_list_by_conservation_status.html'
    context_object_name = 'trees'
    
    def get_queryset(self):
        # Get the conservation status from the URL
        conservation_status = get_object_or_404(ConservationStatus, pk=self.kwargs['pk'])
        return Tree.objects.filter(conservation_status=conservation_status)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conservation_status'] = get_object_or_404(ConservationStatus, pk=self.kwargs['pk'])
        return context


from django.views.generic.edit import FormView
from django.contrib import messages
from .models import Subscriber
from .forms import SubscriberForm  # You need to create this form

from django.shortcuts import render, redirect
from .forms import SubscriberForm


def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'thank_you.html')
    else:
        form = SubscriberForm()

    return render(request, 'subscribe.html', {'form': form})


#cookies
from django.shortcuts import render
from django.http import JsonResponse

def accept_cookie_consent(request):
    if request.method == "POST":
        response = JsonResponse({"message": "Cookie consent accepted."})
        response.set_cookie("cookie_consent", "accepted", max_age=365 * 24 * 60 * 60)  # Expires in 1 year
        return response
    return JsonResponse({"error": "Invalid request method."}, status=400)


def cookie_policy(request):
    return render(request, 'cookie_policy.html')


#######3
from django.views.generic import ListView, DetailView
from .models import TreePlantingEvent

class TreePlantingEventListView(ListView):
    model = TreePlantingEvent
    template_name = 'treeplantingevent_list.html'
    context_object_name = 'events'
    ordering = ['-date_planted']


class TreePlantingEventDetailView(DetailView):
    model = TreePlantingEvent
    template_name = 'treeplantingevent_detail.html'
    context_object_name = 'event'


from django.views.generic import ListView, TemplateView
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Cast
from .models import TreeMonitoringRecord, TreePlantingEvent, Tree
from django.views.generic import ListView
from .models import Tree


class MonitoredTreeListView(ListView):
    model = Tree
    template_name = 'monitored_tree_list.html'
    context_object_name = 'trees'

    def get_queryset(self):
        return Tree.objects.filter(monitoring_records__isnull=False).distinct()
    
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import TreeMonitoringRecord

class TreeMonitoringRecordListView(ListView):
    model = TreeMonitoringRecord
    template_name = 'tree_monitoring_list.html'
    context_object_name = 'monitoring_records'
    paginate_by = 10  # Optional: paginates results

class TreeMonitoringRecordDetailView(DetailView):
    model = TreeMonitoringRecord
    template_name = 'tree_monitoring_detail.html'
    context_object_name = 'record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        context['tree_names'] = ", ".join([tree.name for tree in self.object.trees.all()])
        return context



# views.py
from django.views.generic import ListView
from .models import Plot

class PlotListView(ListView):
    model = Plot
    template_name = 'plot_list.html'  # your template location
    context_object_name = 'plots'
    queryset = Plot.objects.select_related('land_data').all()


class PlotDetailView(DetailView):
    model = Plot
    template_name = 'plot_detail.html'
    context_object_name = 'plot'
    queryset = Plot.objects.select_related('land_data').prefetch_related('images')

from django.views.generic import ListView
from .models import PlotMonitoringRecord

class PlotMonitoringRecordListView(ListView):
    model = PlotMonitoringRecord
    template_name = 'monitoring_land_list.html'  # Adjust as needed
    context_object_name = 'records'
    paginate_by = 10  # Optional pagination

    def get_queryset(self):
        return PlotMonitoringRecord.objects.prefetch_related('photos', 'plot')

from django.views.generic import DetailView
from .models import PlotMonitoringRecord

class PlotMonitoringRecordDetailView(DetailView):
    model = PlotMonitoringRecord
    template_name = 'monitoring_plot_detail.html'
    context_object_name = 'record'


from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Plot

class LandListView(ListView):
    model = Plot
    template_name = 'land_list.html' 
    context_object_name = 'plots'

class LandDetailView(DetailView):
    model = Plot
    template_name = 'land_detail.html' 
    context_object_name = 'plot'

