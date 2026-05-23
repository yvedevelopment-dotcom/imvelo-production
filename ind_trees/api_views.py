from rest_framework import viewsets, generics, filters
from .models import (
    Tree, Category, HeritageSite, ConservationStatus,
    TreePlantingEvent, TreeMonitoringRecord,
    Plot, PlotMonitoringRecord
)
from .serializers import (
    TreeListSerializer, TreeDetailSerializer,
    CategorySerializer, HeritageSiteSerializer,
    ConservationStatusSerializer,
    TreePlantingEventSerializer,
    TreeMonitoringRecordSerializer,
    PlotSerializer, PlotMonitoringRecordSerializer
)

class TreeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tree.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'tree_description']

    def get_serializer_class(self):
        if self.action == 'list':
            return TreeListSerializer
        return TreeDetailSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

class HeritageSiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeritageSite.objects.all().prefetch_related('heritage_site_images')
    serializer_class = HeritageSiteSerializer

class ConservationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConservationStatus.objects.all()
    serializer_class = ConservationStatusSerializer

class TreePlantingEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TreePlantingEvent.objects.all().order_by('-date_planted')
    serializer_class = TreePlantingEventSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location', 'organizer']

class TreeMonitoringRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TreeMonitoringRecord.objects.all().order_by('-monitored_at')
    serializer_class = TreeMonitoringRecordSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['health_status', 'threats_observed']

class PlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plot.objects.select_related('land_data').all()
    serializer_class = PlotSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'land_ownership', 'zone_type']

class PlotMonitoringRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlotMonitoringRecord.objects.all().order_by('-monitored_at')
    serializer_class = PlotMonitoringRecordSerializer

# Filtered endpoints
class TreesByCategoryList(generics.ListAPIView):
    serializer_class = TreeListSerializer
    def get_queryset(self):
        return Tree.objects.filter(categories__id=self.kwargs['pk']).order_by('name')

class TreesByHeritageSiteList(generics.ListAPIView):
    serializer_class = TreeListSerializer
    def get_queryset(self):
        return Tree.objects.filter(heritage_sites__id=self.kwargs['pk']).order_by('name')

class TreesByConservationStatusList(generics.ListAPIView):
    serializer_class = TreeListSerializer
    def get_queryset(self):
        return Tree.objects.filter(conservation_status__id=self.kwargs['pk']).order_by('name')