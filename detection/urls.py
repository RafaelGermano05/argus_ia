from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('generate-dataset/', views.GenerateDatasetView.as_view(), name='generate_dataset'),
    path('analyze-dataset/', views.AnalyzeDatasetView.as_view(), name='analyze_dataset'),
    path('results/<uuid:analysis_id>/', views.AnalysisResultsView.as_view(), name='analysis_results'),
    path('export/<uuid:analysis_id>/', views.ExportDataView.as_view(), name='export_data'),
]