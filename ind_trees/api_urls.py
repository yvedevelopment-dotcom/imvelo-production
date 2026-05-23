from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    TreeViewSet,
    CategoryViewSet,
    HeritageSiteViewSet,
    ConservationStatusViewSet,
    TreePlantingEventViewSet,
    TreeMonitoringRecordViewSet,
    PlotViewSet,
    PlotMonitoringRecordViewSet,
    TreesByCategoryList,
    TreesByHeritageSiteList,
    TreesByConservationStatusList,
)

router = DefaultRouter()
router.register(r'trees', TreeViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'heritage-sites', HeritageSiteViewSet)
router.register(r'conservation-statuses', ConservationStatusViewSet)
router.register(r'planting-events', TreePlantingEventViewSet)
router.register(r'monitoring-records', TreeMonitoringRecordViewSet)
router.register(r'plots', PlotViewSet)
router.register(r'plot-monitoring-records', PlotMonitoringRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Filtered extra endpoints
    path('categories/<int:pk>/trees/',
         TreesByCategoryList.as_view(),
         name='api-trees-by-category'),
    path('heritage-sites/<int:pk>/trees/',
         TreesByHeritageSiteList.as_view(),
         name='api-trees-by-heritage-site'),
    path('conservation-statuses/<int:pk>/trees/',
         TreesByConservationStatusList.as_view(),
         name='api-trees-by-conservation-status'),
]