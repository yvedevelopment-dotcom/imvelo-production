from django.urls import path
from .views import Dashboard, TreeListView, TreeCreateView
from .views import (
    TreeCreateView, SpeciesCreateView, PlotCreateView, MonitoringScheduleListView, MonitoringScheduleCreateView,
    CategoryCreateView, HeritageSiteCreateView, ConservationStatusCreateView, LandDataCreateView,
)

from .views import (
    TreePlantingEventListView,
    TreePlantingEventDetailView,
    TreePlantingEventCreateView,
    TreePlantingEventUpdateView,
    MonitoredTreeListView,
    TreeMonitoringWizard,
    TreeMonitoringRecordCreate,
    TreeMonitoringDetailView,
    LandMenu,
    PlotListView,
    PlotDetailView,
    PlotMonitoringRecordListView,
    PlotMonitoringRecordDetailView,
    TreeDetailView,
    ReportPage, 
    DataCreateView,
    LandCreateView,
    MonitoredEventListView,
    
    MonitoredEventListRView, 
    EventMonitoringDetailView,
    ReportTreeListView,
    TreeMonitoringReportView,
    TreeStatsView,
    TreeFullReportView,
    TreePlantingEventReportView,
    TreePlantingEventMonitoringReportView,
    TreeEventTrendAnalysisView,

)
from .views import clear_event_session_and_redirect
from .views import (
    PlotMonitoringRecordListView,
    PlotMonitoringRecordDetailView,
    PlotMonitoringRecordCreateView,
    EventReportDetailView,
    EventCachedReportView,
    EventReportsListView,

)
from .views import PlotMonitoringWizard, PlotEventSelectPlot, TreeMonitoringRecordPlotCreate, FinalizePlotRecord
from .views import CombinedTreeEventReportView, TreeReportsListView, TreeCachedReportView
from .views import PlotReportView, PlotDetailView, PlotAIReportTemplateView, OverallPlotAIAnalysisView, UnifiedPlotReportView


from .geeview import GEEPlotAnalysisView, TreeEventGEEReportView

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('tree-list/', TreeListView.as_view(), name='tree_list-m'),
    path('trees/<int:pk>/', TreeDetailView.as_view(), name='tree_detail-m'),
    path('trees/new/', TreeCreateView.as_view(), name='tree_create-m'),

    path('species/add/', SpeciesCreateView.as_view(), name='species_create'),
    path('plot/add/', PlotCreateView.as_view(), name='plot_create'),
    path('land/add/', LandDataCreateView.as_view(), name='land_data_create'),
    path('category/add/', CategoryCreateView.as_view(), name='category_create'),
    path('heritage/add/', HeritageSiteCreateView.as_view(), name='heritage_site_create'),
    path('conservation/add/', ConservationStatusCreateView.as_view(), name='conservation_status_create'),

    path('events/', TreePlantingEventListView.as_view(), name='treeplantingevent_list-m'),
    path('events/new/', TreePlantingEventCreateView.as_view(), name='treeplantingevent_create-m'),
    path('events/<int:pk>/', TreePlantingEventDetailView.as_view(), name='treeplantingevent_detail-m'),
    path('events/<int:pk>/edit/', TreePlantingEventUpdateView.as_view(), name='treeplantingevent_update-m'),

    path('monitoring/', MonitoringScheduleListView.as_view(), name='monitoring_schedule_list-m'),
    path('monitoring/create/', MonitoringScheduleCreateView.as_view(), name='monitoring_schedule_create-m'),

    path('monitored-trees/', MonitoredTreeListView.as_view(), name='monitored_tree_list-d'),
    path('monitoring/select-event/', TreeMonitoringWizard.as_view(), name='monitoring_wizard'),
    path('mon/create/', TreeMonitoringRecordCreate.as_view(), name='monitoring_fill'),
    path('monitored-trees/<int:pk>/', TreeMonitoringDetailView.as_view(), name='tree_monitoring_detail-d'),
    

    path('monitoring/events/', MonitoredEventListView.as_view(), name='monitored_event_list-d'),
    path('monitoring/event/<int:pk>/detail/', EventMonitoringDetailView.as_view(), name='event_monitoring_detail-d'),

    path('monitoring/back/', clear_event_session_and_redirect, name='monitoring_back_clear'),


    path('land-menu/', LandMenu.as_view(), name='land-menu'),
    path('plots/', PlotListView.as_view(), name='plot_list-m'),
    path('plots/<int:pk>/', PlotDetailView.as_view(), name='plot_detail-m'),
    path('plots/create/', LandCreateView.as_view(), name='land_create-m'),
    path('plots/data/create/', DataCreateView.as_view(), name='data-create-m'),




    path('monitoring-records/', PlotMonitoringRecordListView.as_view(), name='monitoring_record_list-m'),
    path('monitoring-record/<int:pk>/', PlotMonitoringRecordDetailView.as_view(), name='monitoring_record_detail-m'),
    path('create/', PlotMonitoringRecordCreateView.as_view(), name='monitoring-create'),
    path('wizard/', PlotMonitoringWizard.as_view(), name='monitoring_wizard'),
    path('wizard/<int:plot_id>/select-event/', PlotEventSelectPlot.as_view(), name='monitoring_event_select_plot'),
    path('wizard/tree-monitoring/', TreeMonitoringRecordPlotCreate.as_view(), name='monitoring_fill'),
    path('wizard/finalize/', FinalizePlotRecord.as_view(), name='monitoring_finalize'),

##################################  
    path('report-page/', ReportPage.as_view(), name='report_page'),

 #tree report
    path("tree/reports/<int:pk>/", TreeReportsListView.as_view(), name="tree_reports_list"),
    path("tree/cached-report/<int:pk>/", TreeCachedReportView.as_view(), name="tree_cached_report"),
    path("tree/full-report/<int:pk>/", TreeFullReportView.as_view(), name="tree_full_report"),
    path('report-trees/', ReportTreeListView.as_view(), name='report_tree_list-d'),
    path('events/<int:pk>/report/', TreePlantingEventReportView.as_view(), name='tree_event_report'),
    path('events/<int:pk>/monitoring-report/', TreePlantingEventMonitoringReportView.as_view(), name='tree_event_monitoring_report'),
    path('events/<int:pk>/trends/', TreeEventTrendAnalysisView.as_view(), name='tree-event-trends'),
#event
    path('event/full-report/<int:pk>/', CombinedTreeEventReportView.as_view(), name='event_full_report'),
    path('monitoring/event/', MonitoredEventListRView.as_view(), name='monitored_event_list-r'),

    path('event/reports/<int:pk>/', EventReportsListView.as_view(), name='event_reports_list'),
    path('event/cached-report/<int:pk>/', EventCachedReportView.as_view(), name='event_cached_report'),
    path('event/report-detail/<int:pk>/', EventReportDetailView.as_view(), name='event_report_detail'),


    path('plot/<int:pk>/report/', PlotReportView.as_view(), name='plot_report'),
    path('plot/<int:pk>/', PlotDetailView.as_view(), name='plot-detail'),
    path('plots/<int:plot_id>/ai-report/', PlotAIReportTemplateView.as_view(), name='plot_ai_report'),
    path(
        'plot/<int:plot_id>/overall/',
        OverallPlotAIAnalysisView.as_view(),
        name='overall_ai_report'
    ),
    path('plot/<int:plot_id>/unified-report/', UnifiedPlotReportView.as_view(), name='unified_plot_report'),




##########GEE
    path('gee/analyze/<int:plot_id>/', GEEPlotAnalysisView.as_view(), name='gee_analyze'),
    path('tree-event/<int:event_id>/gee-report/', TreeEventGEEReportView.as_view(), name='tree_event_gee_report'),


]