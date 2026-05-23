from django.urls import path
from . import views
from .views import CategoryListView, TreesByCategoryListView, HeritageSiteListView, HeritageSiteDetailView, TreesByHeritageSiteListView, MedialBenefit
from .views import About, generate_qr_code, TreeMonitoringRecordDetailView, PlotListView, PlotDetailView, PlotMonitoringRecordListView
from .views import ConservationStatusListView, TreeListByConservationStatusView, TreeDetailView, TreeMonitoringRecordListView
from .views import TreePlantingEventListView, TreePlantingEventDetailView, TreeMonitoringRecordListView, MonitoredTreeListView, PlotMonitoringRecordDetailView, Monitor
#from .views import PlotDetailView, PlotListView

urlpatterns = [

    path('about/', About.as_view(), name='about'),
    path('monitoring-menu/', Monitor.as_view(), name='monitoring_menu'),
    path('plots/', PlotListView.as_view(), name='plot_list'),
    path('plots/<int:pk>/', PlotDetailView.as_view(), name='plot_detail'),


    
    path('trees/', views.TreeListView.as_view(), name='tree_list'),
    path('trees/<int:pk>/', views.TreeDetailView.as_view(), name='tree_detail'),
    path('tree/<int:pk>/qr/', generate_qr_code, name='tree_qr'),
    path('tree/<int:pk>/qr/download/', generate_qr_code, name='tree_qr_download'),


    path('categories/', CategoryListView.as_view(), name='category'),
    path('categories/<int:pk>/', TreesByCategoryListView.as_view(), name='trees-by-category'),

    path('heritage-sites/', HeritageSiteListView.as_view(), name='heritage_site_list'),
    path('heritage-sites/<int:pk>/', HeritageSiteDetailView.as_view(), name='heritage_site_detail'),
    path('heritage-sites/<int:pk>/trees/', TreesByHeritageSiteListView.as_view(), name='trees_by_heritage_site'),

    path('medical-benefits/', MedialBenefit.as_view(), name='medical_benefit'),

    path('conservation-status/', ConservationStatusListView.as_view(), name='conservation_status_list'),
    path('conservation-status/<int:pk>/trees/', TreeListByConservationStatusView.as_view(), name='trees_by_conservation_status'),
    
    path('subscribe', views.subscribe, name='subscribe'),

    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('accept-cookie-consent/', views.accept_cookie_consent, name='cookie_consent_accept'),

    path('monitored-trees/', MonitoredTreeListView.as_view(), name='monitored_tree_list'),
    path('monitoring/<int:pk>/', TreeMonitoringRecordDetailView.as_view(), name='tree_monitoring_detail'),
    path('monitoring/tree/<int:tree_id>/', TreeMonitoringRecordListView.as_view(), name='tree_monitoring_list'),

    path('monitoring/<int:pk>/', TreeMonitoringRecordDetailView.as_view(), name='tree_monitoring_detail'),

    path('monitoring-records/', PlotMonitoringRecordListView.as_view(), name='monitoring_record_list'),
    path('monitoring-record/<int:pk>/', PlotMonitoringRecordDetailView.as_view(), name='monitoring_record_detail'),


    path('planting-events/', TreePlantingEventListView.as_view(), name='treeplantingevent_list'),
    path('planting-events/<int:pk>/', TreePlantingEventDetailView.as_view(), name='treeplantingevent_detail'),
    path('plots/', PlotListView.as_view(), name='plot-list'),
    path('plot_detail/<int:pk>/', PlotDetailView.as_view(), name='plot_detail'),


  #  path('monitoring-records/', TreeMonitoringRecordListView.as_view(), name='monitoring_record_list'),
   #@ path('monitoring-summary/', TreeMonitoringSummaryView.as_view(), name='monitoring_summary'),
]
